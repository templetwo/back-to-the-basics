"""
The Gauntlet: BTB vs The World

Rigorous benchmark comparing BTB filesystem approach against:
- SQLite (indexed relational DB)
- Vector DB (simulated with embedding latency)
- FAISS (production-grade ANN index)

Validates the core thesis: BTB wins on structured queries, loses on fuzzy semantic search.

Usage:
    python benchmark.py --count 1000 --latency 20
    python benchmark.py --count 100000 --latency 0  # No sleep for faster testing
"""

import os
import time
import json
import sqlite3
import shutil
import random
import argparse
from pathlib import Path
from glob import glob
import numpy as np
import faiss
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from coherence import Coherence

# Reproducible embeddings
np.random.seed(42)
d = 384
failure_vec = np.random.randn(d)
success_vec = np.random.randn(d)
error_vec = np.random.randn(d)
info_vec = np.random.randn(d)

# Defaults (overridden by CLI args)
ITEM_COUNT = 1000
EMBEDDING_LATENCY_MS = 20
ROOT_DIR = "benchmark_arena"

BENCHMARK_SCHEMA = {
    "type": {
        "log": {
            "level": {
                "error": "{id}.json",
                "info": "{id}.json",
            }
        },
        "memory": {
            "outcome": {
                "success": "{id}.json",
                "failure": "{id}.json",
            }
        }
    }
}

def generate_dataset(count):
    """Generate synthetic dataset with embeddings."""
    data = []
    for i in range(count):
        item_type = random.choice(["log", "memory"])
        if item_type == "log":
            level = random.choice(["error", "info"])
            base_vec = error_vec if level == "error" else info_vec
            item = {
                "id": f"log_{i}",
                "type": "log",
                "level": level,
                "message": f"System event {i} occurred at {time.time()}",
                "timestamp": int(time.time())
            }
        else:
            outcome = random.choice(["success", "failure"])
            base_vec = failure_vec if outcome == "failure" else success_vec
            item = {
                "id": f"mem_{i}",
                "type": "memory",
                "outcome": outcome,
                "content": f"Agent thought process {i} analysis",
                "timestamp": int(time.time())
            }
        emb = base_vec + 0.1 * np.random.randn(d)
        item["embedding"] = emb.tolist()
        data.append(item)
    return data


class BTBRunner:
    """BTB filesystem approach."""

    def __init__(self, root):
        self.root = Path(root) / "btb"
        if self.root.exists():
            shutil.rmtree(self.root)
        self.engine = Coherence(BENCHMARK_SCHEMA, root=str(self.root))

    def ingest(self, dataset):
        start = time.time()
        for item in dataset:
            path = self.engine.transmit(item, dry_run=False)
            with open(path, "w") as f:
                json.dump(item, f)
        return time.time() - start

    def recall_structured(self):
        """Exact match: outcome=failure"""
        start = time.time()
        pattern = str(self.root / "type=memory/outcome=failure/*.json")
        results = glob(pattern)
        loaded = []
        for p in results:
            with open(p) as f:
                loaded.append(json.load(f))
        return time.time() - start, len(loaded)

    def recall_fuzzy(self, query_emb, k):
        """Semantic similarity: top-k nearest to query embedding"""
        start = time.time()
        pattern = str(self.root / "**/*.json")
        results = glob(pattern, recursive=True)
        loaded = []
        for p in results:
            with open(p) as f:
                item = json.load(f)
            emb = np.array(item["embedding"])
            dist = np.linalg.norm(emb - query_emb)
            loaded.append((dist, item))
        loaded.sort(key=lambda x: x[0])
        top = loaded[:k]
        return time.time() - start, len(top)

    def size(self):
        total_size = 0
        for dirpath, _, filenames in os.walk(self.root):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size


class SQLiteRunner:
    """SQLite with indexes."""

    def __init__(self, root):
        self.root = Path(root) / "sql"
        if self.root.exists():
            shutil.rmtree(self.root)
        self.root.mkdir(parents=True)
        self.db_path = self.root / "db.sqlite"
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE items (
                id TEXT PRIMARY KEY,
                type TEXT,
                subtype TEXT,
                data TEXT
            )
        ''')
        self.cursor.execute('CREATE INDEX idx_subtype ON items(subtype)')

    def ingest(self, dataset):
        start = time.time()
        for item in dataset:
            subtype = item.get("level") or item.get("outcome")
            self.cursor.execute(
                "INSERT INTO items VALUES (?, ?, ?, ?)",
                (item["id"], item["type"], subtype, json.dumps(item))
            )
        self.conn.commit()
        return time.time() - start

    def recall_structured(self):
        start = time.time()
        self.cursor.execute("SELECT data FROM items WHERE subtype='failure'")
        rows = self.cursor.fetchall()
        loaded = [json.loads(r[0]) for r in rows]
        return time.time() - start, len(loaded)

    def recall_fuzzy(self, query_emb, k):
        start = time.time()
        self.cursor.execute("SELECT data FROM items")
        rows = self.cursor.fetchall()
        loaded = []
        for r in rows:
            item = json.loads(r[0])
            emb = np.array(item["embedding"])
            dist = np.linalg.norm(emb - query_emb)
            loaded.append((dist, item))
        loaded.sort(key=lambda x: x[0])
        top = loaded[:k]
        return time.time() - start, len(top)

    def size(self):
        return os.path.getsize(self.db_path)


class VectorSimRunner:
    """Vector DB with simulated embedding latency."""

    def __init__(self, root):
        self.root = Path(root) / "vector"
        if self.root.exists():
            shutil.rmtree(self.root)
        self.root.mkdir(parents=True)
        self.storage = []

    def _simulate_embedding(self):
        if EMBEDDING_LATENCY_MS > 0:
            time.sleep(EMBEDDING_LATENCY_MS / 1000.0)

    def ingest(self, dataset):
        start = time.time()
        for item in dataset:
            self._simulate_embedding()
            self.storage.append(item)
        with open(self.root / "vector_store.json", "w") as f:
            json.dump(self.storage, f)
        return time.time() - start

    def recall_structured(self):
        start = time.time()
        results = [x for x in self.storage if x.get("outcome") == "failure"]
        return time.time() - start, len(results)

    def recall_fuzzy(self, query_emb, k):
        start = time.time()
        self._simulate_embedding()
        loaded = []
        for x in self.storage:
            emb = np.array(x["embedding"])
            dist = np.linalg.norm(emb - query_emb)
            loaded.append((dist, x))
        loaded.sort(key=lambda x: x[0])
        top = loaded[:k]
        return time.time() - start, len(top)

    def size(self):
        return os.path.getsize(self.root / "vector_store.json")


class FAISSRunner:
    """FAISS production-grade ANN index."""

    def __init__(self, root):
        self.root = Path(root) / "faiss"
        if self.root.exists():
            shutil.rmtree(self.root)
        self.root.mkdir(parents=True)
        self.d = d
        quantizer = faiss.IndexFlatL2(self.d)
        self.index = faiss.IndexIVFFlat(quantizer, self.d, 100)
        self.index.nprobe = 10
        self.items = None

    def _simulate_embedding(self):
        if EMBEDDING_LATENCY_MS > 0:
            time.sleep(EMBEDDING_LATENCY_MS / 1000.0)

    def ingest(self, dataset):
        start = time.time()
        self.items = dataset
        embeddings = np.zeros((len(dataset), self.d), dtype='float32')
        for i, item in enumerate(dataset):
            self._simulate_embedding()
            embeddings[i] = np.array(item["embedding"])
        self.index.train(embeddings)
        self.index.add(embeddings)
        faiss.write_index(self.index, str(self.root / "index.faiss"))
        with open(self.root / "items.json", "w") as f:
            json.dump(dataset, f)
        return time.time() - start

    def recall_structured(self):
        start = time.time()
        results = [x for x in self.items if x.get("outcome") == "failure"]
        return time.time() - start, len(results)

    def recall_fuzzy(self, query_emb, k):
        start = time.time()
        self._simulate_embedding()
        query = query_emb.reshape(1, -1).astype('float32')
        D, I = self.index.search(query, k)
        loaded = [self.items[int(i)] for i in I[0] if i >= 0]
        return time.time() - start, len(loaded)

    def size(self):
        index_path = self.root / "index.faiss"
        items_path = self.root / "items.json"
        return os.path.getsize(index_path) + os.path.getsize(items_path)


def run_benchmark():
    """Execute the full benchmark suite."""
    print("=" * 70)
    print("THE GAUNTLET: Benchmark Suite")
    print(f"Items: {ITEM_COUNT} | Embedding Simulation: {EMBEDDING_LATENCY_MS}ms")
    print("=" * 70)

    dataset = generate_dataset(ITEM_COUNT)
    query_emb = failure_vec
    k = 100

    # BTB
    print("\n[1] Back to the Basics (Filesystem)...")
    btb = BTBRunner(ROOT_DIR)
    btb_time = btb.ingest(dataset)
    btb_str_time, btb_str_count = btb.recall_structured()
    btb_fuz_time, btb_fuz_count = btb.recall_fuzzy(query_emb, k)
    btb_size = btb.size()
    print(f"    Ingest: {btb_time:.4f}s | Structured: {btb_str_time:.4f}s | Fuzzy: {btb_fuz_time:.4f}s | Size: {btb_size/1024:.1f}KB")

    # SQLite
    print("\n[2] SQLite (Relational)...")
    sql = SQLiteRunner(ROOT_DIR)
    sql_time = sql.ingest(dataset)
    sql_str_time, sql_str_count = sql.recall_structured()
    sql_fuz_time, sql_fuz_count = sql.recall_fuzzy(query_emb, k)
    sql_size = sql.size()
    print(f"    Ingest: {sql_time:.4f}s | Structured: {sql_str_time:.4f}s | Fuzzy: {sql_fuz_time:.4f}s | Size: {sql_size/1024:.1f}KB")

    # Vector Sim
    print("\n[3] Vector DB (Simulated)...")
    vec = VectorSimRunner(ROOT_DIR)
    vec_time = vec.ingest(dataset)
    vec_str_time, vec_str_count = vec.recall_structured()
    vec_fuz_time, vec_fuz_count = vec.recall_fuzzy(query_emb, k)
    vec_size = vec.size()
    print(f"    Ingest: {vec_time:.4f}s | Structured: {vec_str_time:.4f}s | Fuzzy: {vec_fuz_time:.4f}s | Size: {vec_size/1024:.1f}KB")

    # FAISS
    print("\n[4] FAISS (Vector Baseline)...")
    fai = FAISSRunner(ROOT_DIR)
    fai_time = fai.ingest(dataset)
    fai_str_time, fai_str_count = fai.recall_structured()
    fai_fuz_time, fai_fuz_count = fai.recall_fuzzy(query_emb, k)
    fai_size = fai.size()
    print(f"    Ingest: {fai_time:.4f}s | Structured: {fai_str_time:.4f}s | Fuzzy: {fai_fuz_time:.4f}s | Size: {fai_size/1024:.1f}KB")

    # REPORT
    print("\n")
    print("=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print("| Metric | BTB | SQLite | Vector Sim | FAISS |")
    print("| --- | --- | --- | --- | --- |")
    print(f"| Ingest Time | {btb_time:.3f}s | {sql_time:.3f}s | {vec_time:.3f}s | {fai_time:.3f}s |")
    print(f"| Structured Recall Time | {btb_str_time:.4f}s | {sql_str_time:.4f}s | {vec_str_time:.4f}s | {fai_str_time:.4f}s |")
    print(f"| Fuzzy Recall Time (top {k}) | {btb_fuz_time:.4f}s | {sql_fuz_time:.4f}s | {vec_fuz_time:.4f}s | {fai_fuz_time:.4f}s |")
    print(f"| Disk Size (KB) | {btb_size/1024:.1f} | {sql_size/1024:.1f} | {vec_size/1024:.1f} | {fai_size/1024:.1f} |")
    print(f"| Items Found Structured | {btb_str_count} | {sql_str_count} | {vec_str_count} | {fai_str_count} |")
    print(f"| Items Found Fuzzy | {btb_fuz_count} | {sql_fuz_count} | {vec_fuz_count} | {fai_fuz_count} |")
    print("\n*Note: Fuzzy recall finds top 100 items similar to 'failure' vector.")
    print(" Structured is exact match on 'failure'.")
    print(f" Embedding latency: {EMBEDDING_LATENCY_MS}ms (simulated for Vector/FAISS).")

    # Cleanup
    if Path(ROOT_DIR).exists():
        shutil.rmtree(ROOT_DIR)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The Gauntlet: BTB vs The World")
    parser.add_argument("--count", type=int, default=1000, help="Number of items")
    parser.add_argument("--latency", type=int, default=20, help="Simulated embedding latency (ms)")
    args = parser.parse_args()
    ITEM_COUNT = args.count
    EMBEDDING_LATENCY_MS = args.latency
    run_benchmark()
