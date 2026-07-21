from services.memory.phase1b.indexing import InMemoryIndexJobs, IndexWorker, extract_text

class Memory:
    def content(self, _): return ({"type": "text/plain", "name": "guide.txt", "tags": ["safe"], "source": "handbook", "owner_id": "acme", "organization_id": "org-1", "department_id": "ops", "role_scope": "private", "visibility": "private"}, b"one two three four")
class Embeddings:
    def embed_batch(self, rows): return [[0.1, 0.2] for _ in rows]
class Qdrant:
    def __init__(self): self.batches = []
    def upsert(self, points): self.batches.append(points)

def test_job_is_idempotent_and_worker_indexes_deterministic_chunks():
    jobs = InMemoryIndexJobs(); job, created = jobs.create("m1", "acme", "p1", "chunk-v1", "1")
    same, created_again = jobs.create("m1", "acme", "p1", "chunk-v1", "1")
    qdrant = Qdrant(); completed = IndexWorker(Memory(), jobs, Embeddings(), qdrant, "p1", chunk_size=2, overlap=1).run(job.id)
    assert created and not created_again and same.id == job.id
    assert completed.status == "completed" and completed.chunk_count == 3
    assert qdrant.batches and qdrant.batches[0][0]["payload"]["owner"] == "acme"

def test_extraction_contract_rejects_unsupported():
    try: extract_text(b"x", "application/vnd.ms-excel", "sheet.xlsx")
    except RuntimeError as error: assert str(error) == "unsupported_file_type"
    else: assert False
