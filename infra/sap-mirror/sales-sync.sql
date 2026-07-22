/* Canonical, read-only SAP B1 sales projection consumed by Core Sales Domain.
   The sync worker is the only writer.  Core API has SELECT-only access. */
create table dbo.sap_sales_orders (
    order_id bigint not null primary key,
    store nvarchar(100) not null,
    order_date date not null,
    is_cancelled bit not null default 0,
    source_updated_at datetime2 null,
    synced_at datetime2 not null default sysutcdatetime()
);

create table dbo.sap_sales_order_lines (
    order_id bigint not null,
    line_number int not null,
    sku nvarchar(100) not null,
    quantity decimal(19,4) not null,
    amount decimal(19,4) not null,
    margin decimal(19,4) not null,
    primary key (order_id, line_number),
    constraint fk_sap_sales_order_lines_order foreign key (order_id)
        references dbo.sap_sales_orders(order_id)
);

create index ix_sap_sales_orders_date on dbo.sap_sales_orders(order_date desc, order_id desc);
create index ix_sap_sales_order_lines_sku on dbo.sap_sales_order_lines(sku);
