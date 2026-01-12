"""
The Sentinel: Universal Entropy Firewall

Watches the '_inbox' directory.
When a file lands, it attempts to route it through the Coherence Engine.

- If it fits the schema -> It finds its home.
- If it doesn't -> It goes to quarantine.

The filesystem becomes an active circuit.
No ETL pipelines. No ingestion scripts. Just a folder that thinks.
"""

import os
import sys
import time
import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Set, Optional

from coherence import Coherence


# =============================================================================
# CONFIGURABLE SCHEMAS
# =============================================================================
# The Sentinel can use different schemas for different purposes.

# Schema for general data routing
DATA_SCHEMA = {
    "type": {
        "sensor": {
            "sensor_id": {
                "*": {
                    "quality": {
                        "high": "{timestamp}_{sensor_id}_high.json",
                        "medium": "{timestamp}_{sensor_id}_med.json",
                        "low": "{timestamp}_{sensor_id}_low.json",
                    }
                }
            }
        },
        "log": {
            "level": {
                "error": "logs/error/{timestamp}_{source}.json",
                "warning": "logs/warning/{timestamp}_{source}.json",
                "info": "logs/info/{timestamp}_{source}.json",
                "debug": "logs/debug/{timestamp}_{source}.json",
            }
        },
        "metric": {
            "domain": {
                "performance": "metrics/perf/{timestamp}.json",
                "business": "metrics/business/{timestamp}.json",
                "system": "metrics/system/{timestamp}.json",
            }
        },
        "memory": {
            "outcome": {
                "success": "memories/success/{tool}/{timestamp}.json",
                "failure": "memories/failure/{tool}/{timestamp}.json",
                "learning": "memories/learning/{timestamp}.json",
            }
        },
    }
}


class Sentinel:
    """
    The Entropy Firewall.

    Watches an inbox directory and routes incoming files through
    a Coherence schema. Valid packets find their semantic home.
    Invalid packets go to quarantine.

    The membrane of the cell.
    """

    def __init__(self,
                 inbox: str = "_inbox",
                 root: str = "data",
                 quarantine: str = "_quarantine",
                 schema: Dict = None):
        """
        Initialize the Sentinel.

        Args:
            inbox: Directory to watch for incoming files
            root: Root directory for routed files
            quarantine: Directory for rejected files
            schema: Routing schema (uses DATA_SCHEMA if None)
        """
        self.inbox = Path(inbox)
        self.root = root
        self.quarantine = Path(quarantine)
        self.schema = schema or DATA_SCHEMA
        self.engine = Coherence(self.schema, root=root)

        # Track processed files to avoid reprocessing
        self.processed: Set[str] = set()

        # Statistics
        self.stats = {
            "admitted": 0,
            "rejected": 0,
            "errors": 0,
            "started": datetime.now().isoformat()
        }

        # Ensure directories exist
        os.makedirs(self.inbox, exist_ok=True)
        os.makedirs(self.quarantine, exist_ok=True)
        os.makedirs(self.root, exist_ok=True)

    def start(self, interval: float = 1.0, once: bool = False):
        """
        Start the sentinel loop.

        Args:
            interval: Polling interval in seconds
            once: If True, scan once and exit (for testing)
        """
        self._print_banner()

        if once:
            self._scan()
            self._print_stats()
            return

        try:
            while True:
                self._scan()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[SENTINEL] Shutting down...")
            self._print_stats()

    def _print_banner(self):
        """Print startup banner."""
        print("=" * 60)
        print("THE SENTINEL: Entropy Firewall")
        print("=" * 60)
        print(f"  Inbox:      {self.inbox}/")
        print(f"  Routes to:  {self.root}/")
        print(f"  Rejects to: {self.quarantine}/")
        print("=" * 60)
        print()

    def _print_stats(self):
        """Print statistics."""
        print()
        print("-" * 40)
        print(f"Admitted:  {self.stats['admitted']}")
        print(f"Rejected:  {self.stats['rejected']}")
        print(f"Errors:    {self.stats['errors']}")
        print("-" * 40)

    def _scan(self):
        """Scan inbox for new files."""
        for item in self.inbox.iterdir():
            if item.is_file() and not item.name.startswith("."):
                # Generate file hash to track processing
                file_hash = self._hash_file(item)

                if file_hash not in self.processed:
                    self._process(item)
                    self.processed.add(file_hash)

    def _hash_file(self, path: Path) -> str:
        """Generate hash for file tracking."""
        stat = path.stat()
        return hashlib.md5(f"{path.name}:{stat.st_size}:{stat.st_mtime}".encode()).hexdigest()

    def _process(self, filepath: Path):
        """Process a single file."""
        print(f"[INCOMING] {filepath.name}")

        # 1. PARSE - Extract the packet (the electron)
        packet = self._parse(filepath)
        if packet is None:
            return

        # 2. ROUTE - Find the destination
        try:
            destination = self.engine.transmit(packet, dry_run=True)

            # Check for intake/reject paths (Coherence sends unknowns there)
            if "_intake" in destination or "reject" in destination.lower():
                self._reject(filepath, "no_matching_route", packet)
                return

            # 3. ADMIT - Move to canonical location
            self._admit(filepath, destination, packet)

        except Exception as e:
            self._reject(filepath, f"routing_error", packet, error=str(e))

    def _parse(self, filepath: Path) -> Optional[Dict]:
        """
        Parse file into a packet.

        Supports:
        - JSON files (.json)
        - Files with JSON content
        - Simple key=value text files
        """
        try:
            content = filepath.read_text()

            # Try JSON first
            if filepath.suffix == ".json" or content.strip().startswith("{"):
                packet = json.loads(content)

                # Ensure timestamp
                if "timestamp" not in packet:
                    packet["timestamp"] = datetime.now().strftime("%Y%m%d_%H%M%S")

                return packet

            # Try key=value parsing
            packet = self._parse_keyvalue(content)
            if packet:
                packet["timestamp"] = datetime.now().strftime("%Y%m%d_%H%M%S")
                packet["_original_file"] = filepath.name
                return packet

            # Can't parse - reject
            self._reject(filepath, "unparseable_format")
            return None

        except json.JSONDecodeError:
            self._reject(filepath, "malformed_json")
            return None
        except Exception as e:
            self._reject(filepath, "parse_error", error=str(e))
            return None

    def _parse_keyvalue(self, content: str) -> Optional[Dict]:
        """Parse simple key=value format."""
        lines = content.strip().split("\n")
        packet = {}

        for line in lines:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Try to parse value as number
                try:
                    value = float(value) if "." in value else int(value)
                except ValueError:
                    pass

                packet[key] = value

        return packet if packet else None

    def _admit(self, source: Path, destination: str, packet: Dict):
        """Admit file to its canonical location."""
        dest_path = Path(destination)

        # If destination doesn't end with extension, append filename
        if not any(destination.endswith(ext) for ext in [".json", ".txt", ".log"]):
            name = f"{packet.get('timestamp', 'unknown')}_{source.stem}.json"
            dest_path = dest_path / name

        # Create directory
        os.makedirs(dest_path.parent, exist_ok=True)

        # Write packet (enriched) to destination
        with open(dest_path, "w") as f:
            packet["_source"] = source.name
            packet["_admitted_at"] = datetime.now().isoformat()
            json.dump(packet, f, indent=2, default=str)

        # Remove original
        source.unlink()

        print(f"  [ADMIT]  → {dest_path}")
        self.stats["admitted"] += 1

    def _reject(self, source: Path, reason: str, packet: Dict = None, error: str = None):
        """Reject file to quarantine."""
        # Create rejection record
        reject_dir = self.quarantine / reason
        os.makedirs(reject_dir, exist_ok=True)

        # Move original file
        dest = reject_dir / source.name
        shutil.move(str(source), str(dest))

        # Write rejection metadata
        meta = {
            "original_file": source.name,
            "reason": reason,
            "rejected_at": datetime.now().isoformat(),
            "packet": packet,
            "error": error
        }
        meta_path = reject_dir / f"{source.stem}_rejection.json"
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2, default=str)

        print(f"  [REJECT] → {reject_dir}/ ({reason})")
        self.stats["rejected"] += 1


# =============================================================================
# DEMONSTRATION
# =============================================================================

def demo():
    """Run the Sentinel demonstration."""

    # Clean up from previous runs
    for d in ["_inbox", "_quarantine", "data"]:
        if os.path.exists(d):
            shutil.rmtree(d)

    # Initialize Sentinel
    sentinel = Sentinel(inbox="_inbox", root="data", schema=DATA_SCHEMA)

    # ─────────────────────────────────────────────────────────────────────────
    # Drop test packets into inbox
    # ─────────────────────────────────────────────────────────────────────────

    print("[SIMULATION] Dropping packets into inbox...\n")

    # Packet 1: Valid sensor data (high quality)
    with open("_inbox/sensor_reading.json", "w") as f:
        json.dump({
            "type": "sensor",
            "sensor_id": "temp_001",
            "quality": "high",
            "value": 23.5,
            "unit": "celsius"
        }, f)

    # Packet 2: Valid log entry (error level)
    with open("_inbox/app_error.json", "w") as f:
        json.dump({
            "type": "log",
            "level": "error",
            "source": "auth_service",
            "message": "Failed login attempt",
            "user_id": "user_123"
        }, f)

    # Packet 3: Valid metric (performance)
    with open("_inbox/perf_metric.json", "w") as f:
        json.dump({
            "type": "metric",
            "domain": "performance",
            "latency_ms": 45,
            "endpoint": "/api/users"
        }, f)

    # Packet 4: Valid memory (success)
    with open("_inbox/agent_memory.json", "w") as f:
        json.dump({
            "type": "memory",
            "outcome": "success",
            "tool": "code_interpreter",
            "content": "Successfully debugged the auth module"
        }, f)

    # Packet 5: Invalid - unknown type
    with open("_inbox/mystery_data.json", "w") as f:
        json.dump({
            "type": "quantum_fluctuation",  # Schema doesn't know this
            "data": "???"
        }, f)

    # Packet 6: Malformed JSON
    with open("_inbox/broken.json", "w") as f:
        f.write("{this is not: valid json")

    # Packet 7: Key-value format (alternative input)
    with open("_inbox/simple_log.txt", "w") as f:
        f.write("type=log\nlevel=warning\nsource=backup_service\nmessage=disk_space_low")

    # ─────────────────────────────────────────────────────────────────────────
    # Run Sentinel once
    # ─────────────────────────────────────────────────────────────────────────

    print()
    sentinel.start(once=True)

    # ─────────────────────────────────────────────────────────────────────────
    # Show resulting structure
    # ─────────────────────────────────────────────────────────────────────────

    print("\n" + "=" * 60)
    print("RESULTING STRUCTURE")
    print("=" * 60 + "\n")

    print("[ROUTED DATA]")
    for root, dirs, files in os.walk("data"):
        level = root.replace("data", "").count(os.sep)
        indent = "  " * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = "  " * (level + 1)
        for f in files:
            print(f"{subindent}{f}")

    print("\n[QUARANTINE]")
    for root, dirs, files in os.walk("_quarantine"):
        level = root.replace("_quarantine", "").count(os.sep)
        indent = "  " * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = "  " * (level + 1)
        for f in files:
            print(f"{subindent}{f}")

    print("\n" + "=" * 60)
    print("The inbox is now empty. The entropy has been sorted.")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "watch":
        # Run in watch mode
        sentinel = Sentinel()
        sentinel.start(interval=1.0)
    else:
        # Run demo
        demo()
