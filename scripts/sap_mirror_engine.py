import json, os, sqlite3, time
from pathlib import Path
import pytds

BASE=Path('/opt/foxbrain-core'); ENV=BASE/'sync/mirror-source.env'; STATE=BASE/'sync/mirror-state.db'; LOG=BASE/'logs/sap-mirror.jsonl'
TABLES=['OWHS','OSLP','OHEM','OCRD','OITM','OINV','INV1','ORIN','RIN1','OPOR','POR1','OPCH','PCH1','OITW']
def env():
 d={}
 for line in ENV.read_text().splitlines():
  if '=' in line:
   k,v=line.split('=',1); d[k]=v
 return d
def log(**x):
 x['time']=int(time.time()); LOG.parent.mkdir(parents=True,exist_ok=True)
 with LOG.open('a',encoding='utf-8') as f:f.write(json.dumps(x,ensure_ascii=False,default=str)+'\n')
def q(n): return '['+str(n).replace(']',']]')+']'
def ddl_type(r):
 t=r[1].lower(); size=int(r[2] or 0); p=int(r[3] or 0); s=int(r[4] or 0)
 if t in ('varchar','char','varbinary','binary'): return f'{t}({"max" if size==-1 else size})'
 if t in ('nvarchar','nchar'): return f'{t}({"max" if size==-1 else max(1,size//2)})'
 if t in ('decimal','numeric'): return f'{t}({p},{s})'
 if t in ('timestamp','rowversion'): return 'binary(8)'
 return t
def main():
 e=env(); src=pytds.connect(server=e['SOURCE_HOST'],port=int(e['SOURCE_PORT']),database=e['SOURCE_DB'],user=e['SOURCE_USER'],password=e['SOURCE_PASSWORD'],autocommit=True,timeout=60)
 dst=pytds.connect(server='127.0.0.1',port=11433,database='master',user='sa',password=e['TARGET_SA_PASSWORD'],autocommit=True,timeout=60)
 dc=dst.cursor(); dc.execute("if db_id('SAP_MIRROR') is null create database SAP_MIRROR")
 dst.close(); dst=pytds.connect(server='127.0.0.1',port=11433,database='SAP_MIRROR',user='sa',password=e['TARGET_SA_PASSWORD'],autocommit=True,timeout=60); dc=dst.cursor(); sc=src.cursor()
 state=sqlite3.connect(STATE); state.execute('create table if not exists progress(table_name text primary key,status text,source_rows integer default 0,target_rows integer default 0,copied_rows integer default 0,updated_at integer,error text)'); state.commit()
 for table in TABLES:
  try:
   row=state.execute('select status,copied_rows from progress where table_name=?',(table,)).fetchone()
   if row and row[0]=='completed': continue
   sc.execute("select c.name,t.name,c.max_length,c.precision,c.scale,c.is_nullable,c.is_computed from sys.columns c join sys.types t on c.user_type_id=t.user_type_id where c.object_id=object_id(%s) order by c.column_id",('dbo.'+table,)); cols=[r for r in sc.fetchall() if not r[6]]
   if not cols: raise RuntimeError('table metadata missing')
   sc.execute('select count(*) from '+q(table)); source_rows=int(sc.fetchone()[0]); copied=int(row[1] or 0) if row else 0
   if copied==0:
    dc.execute("if object_id(%s,'U') is not null drop table "+q(table),('dbo.'+table,)); dc.execute('create table '+q(table)+'('+','.join(q(r[0])+' '+ddl_type(r)+(' null' if r[5] else ' not null') for r in cols)+')')
   names=[r[0] for r in cols]; projection=','.join(q(x) for x in names); select='select '+projection+' from (select '+projection+',row_number() over(order by '+q(names[0])+') as [__fox_row] from '+q(table)+') [fox_page] where [__fox_row]>%d and [__fox_row]<=%d order by [__fox_row]'
   insert='insert into '+q(table)+'('+','.join(q(x) for x in names)+') values('+','.join(['%s']*len(names))+')'
   while copied<source_rows:
    sc.execute(select%(copied,copied+1000)); rows=sc.fetchall()
    if not rows: break
    dc.executemany(insert,rows); copied+=len(rows); state.execute('insert or replace into progress values(?,?,?,?,?,?,?)',(table,'running',source_rows,0,copied,int(time.time()),'')); state.commit()
   dc.execute('select count(*) from '+q(table)); target_rows=int(dc.fetchone()[0]); status='completed' if target_rows==source_rows else 'failed'
   state.execute('insert or replace into progress values(?,?,?,?,?,?,?)',(table,status,source_rows,target_rows,copied,int(time.time()),'' if status=='completed' else 'row_count_mismatch')); state.commit(); log(table=table,status=status,source_rows=source_rows,target_rows=target_rows)
  except Exception as ex:
   previous=state.execute('select source_rows,copied_rows from progress where table_name=?',(table,)).fetchone() or (0,0); state.execute('insert or replace into progress values(?,?,?,?,?,?,?)',(table,'failed',previous[0],0,previous[1],int(time.time()),str(ex)[:1000])); state.commit(); log(table=table,status='failed',error=str(ex));
 state.close(); src.close(); dst.close()
if __name__=='__main__': main()
