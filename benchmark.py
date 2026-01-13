"""
The Gauntlet: Back to the Basics vs. The World

A rigorous benchmark measuring 'Time-to-Meaning'.
Compares the Filesystem Circuit against Relational and Vector approaches.

Metrics:
1. Ingestion Rate (items/sec)
2. Recall Latency (seconds)
3. Disk Footprint (bytes)
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

# Import our engine
from coherence import Coherence

# =========================================================================
# CONFIGURATION
# =========================================================================
ITEM_COUNT = 1000  # Number of items to process in the race
EMBEDDING_LATENCY_MS = 20  # Conservative estimate for CPU embedding (e.g., all-MiniLM-L6-v2)
ROOT_DIR = "benchmark_arena"

# Schema for BTB - leaf is just the filename, path is the decision tree
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


# Generators
def generate_dataset(count):
    data = []
    for i in range(count):
        item_type = random.choice(["log", "memory"])
        if item_type == "log":
            item = {
                "id": f"log_{i}",
                "type": "log",
                "level": random.choice(["info", "error"]),
                "message": f"System event {i} occurred at {time.time()}",
                "timestamp": int(time.time())
            }
        else:
            item = {
                "id": f"mem_{i}",
                "type": "memory",
                "outcome": random.choice(["success", "failure"]),
                "content": f"Agent thought process {i} analysis",
                "timestamp": int(time.time())
            }
        data.append(item)
    return data


# =========================================================================
# CONTENDER 1: Back to the Basics (BTB)
# =========================================================================
class BTBRunner:
    def __init__(self, root):
        self.root = Path(root) / "btb"
        if self.root.exists():
            shutil.rmtree(self.root)
        self.engine = Coherence(BENCHMARK_SCHEMA, root=str(self.root))

    def ingest(self, dataset):
        start = time.time()
        for item in dataset:
            path = self.engine.transmit(item, dry_run=False)
            # Coherence.transmit creates dirs but not files - write content
            with open(path, "w") as f:
                json.dump(item, f)
        return time.time() - start

    def recall_failure(self):
        start = time.time()
        # "Find all failures" -> glob (path encodes the query)
        pattern = str(self.root / "type=memory/outcome=failure/*.json")
        results = glob(pattern)
        # Actually load them to be fair (SQL does read + parse)
        loaded = []
        for p in results:
            with open(p) as f:
                loaded.append(json.load(f))
        return time.time() - start, len(loaded)

    def size(self):
        total_size = 0
        for dirpath, _, filenames in os.walk(self.root):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size


# =========================================================================
# CONTENDER 2: SQLite (Relational Standard)
# =========================================================================
class SQLiteRunner:
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
            # Flatten for SQL
            subtype = item.get("level") or item.get("outcome")
            self.cursor.execute(
                "INSERT INTO items VALUES (?, ?, ?, ?)",
                (item["id"], item["type"], subtype, json.dumps(item))
            )
        self.conn.commit()
        return time.time() - start

    def recall_failure(self):
        start = time.time()
        self.cursor.execute("SELECT data FROM items WHERE subtype='failure'")
        rows = self.cursor.fetchall()
        loaded = [json.loads(r[0]) for r in rows]
        return time.time() - start, len(loaded)

    def size(self):
        return os.path.getsize(self.db_path)


# =========================================================================
# CONTENDER 3: Vector DB (Simulated Hype)
# =========================================================================
class VectorSimRunner:
    def __init__(self, root):
        self.root = Path(root) / "vector"
        if self.root.exists():
            shutil.rmtree(self.root)
        self.root.mkdir(parents=True)
        # We simulate a vector store as a flat file + an in-memory index
        self.storage = []

    def _simulate_embedding(self):
        # Simulating the CPU cost of calculating an embedding
        # This is the "Time-to-Meaning" tax
        time.sleep(EMBEDDING_LATENCY_MS / 1000.0)

    def ingest(self, dataset):
        start = time.time()
        for item in dataset:
            # 1. Embed (Simulated)
            self._simulate_embedding()
            # 2. Store
            self.storage.append(item)

        # Serialize to disk to simulate persistence cost
        with open(self.root / "vector_store.json", "w") as f:
            json.dump(self.storage, f)

        return time.time() - start

    def recall_failure(self):
        start = time.time()
        # Vector recall involves: Embed Query -> Cosine Sim.
        self._simulate_embedding()  # Embed the query "show me failures"

        # Naive linear scan to simulate ANN search overhead/filtering
        results = [x for x in self.storage if x.get("outcome") == "failure"]
        return time.time() - start, len(results)

    def size(self):
        return os.path.getsize(self.root / "vector_store.json")


# =========================================================================
# THE ARENA
# =========================================================================
def run_benchmark():
    print("=" * 60)
    print("THE GAUNTLET: Benchmark Suite")
    print(f"Items: {ITEM_COUNT} | Embedding Simulation: {EMBEDDING_LATENCY_MS}ms")
    print("=" * 60)

    dataset = generate_dataset(ITEM_COUNT)

    # --- BTB ---
    print("\n[1] Back to the Basics (Filesystem)...")
    btb = BTBRunner(ROOT_DIR)
    btb_time = btb.ingest(dataset)
    btb_recall, btb_count = btb.recall_failure()
    btb_size = btb.size()
    print(f"    Ingest: {btb_time:.4f}s | Recall: {btb_recall:.4f}s | Size: {btb_size/1024:.1f}KB")

    # --- SQLite ---
    print("\n[2] SQLite (Relational)...")
    sql = SQLiteRunner(ROOT_DIR)
    sql_time = sql.ingest(dataset)
    sql_recall, sql_count = sql.recall_failure()
    sql_size = sql.size()
    print(f"    Ingest: {sql_time:.4f}s | Recall: {sql_recall:.4f}s | Size: {sql_size/1024:.1f}KB")

    # --- Vector ---
    print("\n[3] Vector DB (Simulated)...")
    vec = VectorSimRunner(ROOT_DIR)
    vec_time = vec.ingest(dataset)
    vec_recall, vec_count = vec.recall_failure()
    vec_size = vec.size()
    print(f"    Ingest: {vec_time:.4f}s | Recall: {vec_recall:.4f}s | Size: {vec_size/1024:.1f}KB")

    # --- REPORT ---
    print("\n")
    print("=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print("| Metric | BTB (Filesystem) | SQLite | Vector (Sim) | BTB Speedup |")
    print("| :--- | :--- | :--- | :--- | :--- |")

    # Speedup calculations
    ingest_speedup = vec_time / btb_time if btb_time > 0 else float('inf')
    recall_speedup = vec_recall / btb_recall if btb_recall > 0 else float('inf')

    print(f"| Ingest Time | **{btb_time:.3f}s** | {sql_time:.3f}s | {vec_time:.3f}s | **{ingest_speedup:.0f}x** vs Vector |")
    print(f"| Recall Time | **{btb_recall:.4f}s** | {sql_recall:.4f}s | {vec_recall:.4f}s | **{recall_speedup:.0f}x** vs Vector |")
    print(f"| Disk Size   | {btb_size/1024:.1f}KB | {sql_size/1024:.1f}KB | {vec_size/1024:.1f}KB | - |")
    print(f"| Items Found | {btb_count} | {sql_count} | {vec_count} | - |")

    print("\n*Note: Vector latency simulates a local CPU embedding model (20ms/item).")
    print(" This is the 'Time-to-Meaning' tax of semantic search.*")
    print("\nThe filesystem wins when you KNOW what you're looking for.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The Gauntlet: BTB vs The World")
    parser.add_argument("--count", type=int, default=1000, help="Number of items")
    parser.add_argument("--latency", type=int, default=20, help="Simulated embedding latency (ms)")
    args = parser.parse_args()

    ITEM_COUNT = args.count
    EMBEDDING_LATENCY_MS = args.latency

    run_benchmark()
