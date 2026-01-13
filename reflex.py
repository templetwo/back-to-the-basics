"""
The Reflex Engine: Reactive Filesystem Triggers

Binds actions to paths. When data lands in a matching location,
the reflex fires automatically.

Input → Routing → Storage → Action

The knee-jerk reaction. Bypassing the brain for immediate response.
"""

import json
import time
import fnmatch
import threading
from pathlib import Path
from datetime import datetime
from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict
import traceback


@dataclass
class ReflexBinding:
    """A single reflex: pattern → action."""
    pattern: str
    action: Callable[[Path, Dict], Any]
    name: str = ""
    priority: int = 0  # Higher = fires first
    enabled: bool = True
    fire_count: int = 0
    last_fired: Optional[datetime] = None
    cooldown_ms: int = 0  # Minimum ms between fires
    _last_fire_time: float = 0


@dataclass
class ReflexEvent:
    """Record of a reflex firing."""
    timestamp: datetime
    pattern: str
    path: str
    action_name: str
    success: bool
    duration_ms: float
    result: Any = None
    error: Optional[str] = None


class Reflex:
    """
    The Reflex Engine.

    Binds glob patterns to callback functions.
    When a file matches a pattern, the associated action fires.

    This is the nervous system - automatic reactions to stimuli.
    """

    def __init__(self, root: str = "data"):
        self.root = Path(root)
        self.bindings: List[ReflexBinding] = []
        self.event_log: List[ReflexEvent] = []
        self.stats = defaultdict(int)
        self._lock = threading.Lock()

    def bind(self,
             pattern: str,
             action: Callable[[Path, Dict], Any],
             name: Optional[str] = None,
             priority: int = 0,
             cooldown_ms: int = 0) -> ReflexBinding:
        """
        Bind an action to a glob pattern.

        Args:
            pattern: Glob pattern to match (e.g., "**/level=error/**")
            action: Function(path, content) -> Any
            name: Human-readable name for this reflex
            priority: Higher priority fires first
            cooldown_ms: Minimum time between fires for this pattern

        Returns:
            The ReflexBinding object (can be used to disable later)
        """
        binding = ReflexBinding(
            pattern=pattern,
            action=action,
            name=name or f"reflex_{len(self.bindings)}",
            priority=priority,
            cooldown_ms=cooldown_ms
        )

        with self._lock:
            self.bindings.append(binding)
            # Keep sorted by priority (highest first)
            self.bindings.sort(key=lambda b: -b.priority)

        return binding

    def unbind(self, binding: ReflexBinding) -> bool:
        """Remove a reflex binding."""
        with self._lock:
            if binding in self.bindings:
                self.bindings.remove(binding)
                return True
        return False

    def check(self, path: Path, content: Optional[Dict] = None) -> List[ReflexEvent]:
        """
        Check if a path triggers any reflexes and fire them.

        Args:
            path: Path to check against patterns
            content: Optional file content (will be loaded if not provided)

        Returns:
            List of ReflexEvents for reflexes that fired
        """
        events = []
        path = Path(path)

        # Normalize path for matching
        if path.is_absolute():
            try:
                rel_path = path.relative_to(Path.cwd())
            except ValueError:
                rel_path = path
        else:
            rel_path = path
        path_str = str(rel_path)

        # Load content if needed
        if content is None and path.exists() and path.suffix == '.json':
            try:
                with open(path) as f:
                    content = json.load(f)
            except (json.JSONDecodeError, IOError):
                content = {}
        content = content or {}

        # Check each binding
        current_time = time.time() * 1000  # ms

        with self._lock:
            bindings_snapshot = list(self.bindings)

        for binding in bindings_snapshot:
            if not binding.enabled:
                continue

            # Check cooldown
            if binding.cooldown_ms > 0:
                elapsed = current_time - binding._last_fire_time
                if elapsed < binding.cooldown_ms:
                    continue

            # Check pattern match
            if self._matches(path_str, binding.pattern):
                event = self._fire(binding, path, content)
                events.append(event)

        return events

    def _matches(self, path: str, pattern: str) -> bool:
        """Check if path matches glob pattern."""
        # Handle ** for recursive matching
        if '**' in pattern:
            # Convert to fnmatch-compatible pattern
            # **/ matches any number of directories
            parts = pattern.split('**')
            if len(parts) == 2:
                prefix, suffix = parts
                prefix = prefix.rstrip('/')
                suffix = suffix.lstrip('/')

                # Check if path contains the pattern structure
                if prefix and not path.startswith(prefix.replace('*', '')):
                    # Check with fnmatch for wildcards in prefix
                    if not fnmatch.fnmatch(path, pattern.replace('**', '*')):
                        return False

                if suffix:
                    # The suffix pattern should appear somewhere in the path
                    return fnmatch.fnmatch(path, f"*{suffix}") or \
                           fnmatch.fnmatch(path, pattern.replace('**/', '*/'))

                return fnmatch.fnmatch(path, pattern.replace('**', '*'))

        return fnmatch.fnmatch(path, pattern)

    def _fire(self, binding: ReflexBinding, path: Path, content: Dict) -> ReflexEvent:
        """Fire a reflex and record the event."""
        start = time.time()
        result = None
        error = None
        success = True

        try:
            result = binding.action(path, content)
        except Exception as e:
            success = False
            error = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"

        duration = (time.time() - start) * 1000  # ms

        # Update binding stats
        binding.fire_count += 1
        binding.last_fired = datetime.now()
        binding._last_fire_time = time.time() * 1000

        # Update global stats
        self.stats['total_fires'] += 1
        if success:
            self.stats['successful'] += 1
        else:
            self.stats['failed'] += 1

        # Create event record
        event = ReflexEvent(
            timestamp=datetime.now(),
            pattern=binding.pattern,
            path=str(path),
            action_name=binding.name,
            success=success,
            duration_ms=duration,
            result=result,
            error=error
        )

        self.event_log.append(event)

        # Keep log bounded
        if len(self.event_log) > 10000:
            self.event_log = self.event_log[-5000:]

        return event

    def scan(self, path: Optional[Path] = None) -> List[ReflexEvent]:
        """
        Scan a directory and fire reflexes for all matching files.

        Args:
            path: Directory to scan (defaults to root)

        Returns:
            List of all events that fired
        """
        path = Path(path) if path else self.root
        all_events = []

        for file_path in path.rglob("*.json"):
            events = self.check(file_path)
            all_events.extend(events)

        return all_events

    def watch(self, interval: float = 1.0, callback: Optional[Callable] = None):
        """
        Watch for new files and fire reflexes.

        Args:
            interval: Polling interval in seconds
            callback: Optional function to call with events
        """
        seen = set()

        # Initialize with existing files
        for f in self.root.rglob("*.json"):
            seen.add(str(f))

        print(f"[REFLEX] Watching {self.root}/ for triggers...")
        print(f"[REFLEX] {len(self.bindings)} reflexes bound")
        print("[REFLEX] Press Ctrl+C to stop\n")

        try:
            while True:
                # Find new files
                current = set(str(f) for f in self.root.rglob("*.json"))
                new_files = current - seen

                for file_path in new_files:
                    path = Path(file_path)
                    events = self.check(path)

                    for event in events:
                        status = "OK" if event.success else "FAIL"
                        print(f"  [{status}] {event.action_name}: {path.name} ({event.duration_ms:.1f}ms)")

                        if callback:
                            callback(event)

                    seen.add(file_path)

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n[REFLEX] Stopping...")

    def report(self) -> Dict:
        """Generate a report of reflex activity."""
        return {
            "total_bindings": len(self.bindings),
            "total_fires": self.stats['total_fires'],
            "successful": self.stats['successful'],
            "failed": self.stats['failed'],
            "bindings": [
                {
                    "name": b.name,
                    "pattern": b.pattern,
                    "fire_count": b.fire_count,
                    "last_fired": b.last_fired.isoformat() if b.last_fired else None,
                    "enabled": b.enabled
                }
                for b in self.bindings
            ],
            "recent_events": [
                {
                    "timestamp": e.timestamp.isoformat(),
                    "action": e.action_name,
                    "path": e.path,
                    "success": e.success,
                    "duration_ms": e.duration_ms
                }
                for e in self.event_log[-10:]
            ]
        }


# =============================================================================
# COMMON REFLEX ACTIONS
# =============================================================================

def log_to_console(path: Path, content: Dict) -> str:
    """Simple logging action."""
    print(f"    [LOG] {path}: {content.get('message', content.get('summary', '...'))[:50]}")
    return "logged"


def append_to_file(log_path: str):
    """Create an action that appends to a log file."""
    def action(path: Path, content: Dict) -> str:
        with open(log_path, "a") as f:
            f.write(f"{datetime.now().isoformat()} | {path} | {json.dumps(content)}\n")
        return "appended"
    return action


def call_webhook(url: str, method: str = "POST"):
    """Create an action that calls a webhook."""
    def action(path: Path, content: Dict) -> str:
        import urllib.request
        import urllib.error

        data = json.dumps({
            "path": str(path),
            "content": content,
            "timestamp": datetime.now().isoformat()
        }).encode('utf-8')

        req = urllib.request.Request(url, data=data, method=method)
        req.add_header('Content-Type', 'application/json')

        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return f"webhook_response_{resp.status}"
        except urllib.error.URLError as e:
            return f"webhook_error_{e.reason}"

    return action


def execute_command(cmd_template: str):
    """Create an action that executes a shell command."""
    def action(path: Path, content: Dict) -> str:
        import subprocess
        cmd = cmd_template.format(path=path, **content)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return f"exit_{result.returncode}"
    return action


def aggregate_counter(counter_path: str, key_field: str = "type"):
    """Create an action that maintains a counter file."""
    def action(_path: Path, content: Dict) -> str:
        # Load or create counter
        counter_file = Path(counter_path)
        if counter_file.exists():
            with open(counter_file) as f:
                counters = json.load(f)
        else:
            counters = {}

        # Increment counter
        key = content.get(key_field, "unknown")
        counters[key] = counters.get(key, 0) + 1
        counters["_total"] = counters.get("_total", 0) + 1
        counters["_last_updated"] = datetime.now().isoformat()

        # Save
        counter_file.parent.mkdir(parents=True, exist_ok=True)
        with open(counter_file, "w") as f:
            json.dump(counters, f, indent=2)

        return f"count_{key}_{counters[key]}"

    return action


# =============================================================================
# DEMONSTRATION
# =============================================================================

if __name__ == "__main__":
    import shutil

    print("=" * 70)
    print("THE REFLEX ENGINE: Reactive Filesystem Triggers")
    print("Input → Routing → Storage → Action")
    print("=" * 70)

    # Clean up
    test_root = Path("reflex_test")
    if test_root.exists():
        shutil.rmtree(test_root)
    test_root.mkdir()

    # Create reflex engine
    reflex = Reflex(root=str(test_root))

    # --- Bind reflexes ---
    print("\n[BINDING REFLEXES]")

    # Reflex 1: Log all errors
    reflex.bind(
        "**/level=error/**",
        log_to_console,
        name="error_logger",
        priority=10
    )
    print("  Bound: error_logger (**/level=error/**)")

    # Reflex 2: Count by outcome
    reflex.bind(
        "**/outcome=*/**",
        aggregate_counter("reflex_test/_stats/outcomes.json", "outcome"),
        name="outcome_counter",
        priority=5
    )
    print("  Bound: outcome_counter (**/outcome=*/**)")

    # Reflex 3: Alert on critical
    critical_alerts = []
    def alert_critical(path, _content):
        critical_alerts.append({"path": str(path), "time": datetime.now()})
        return f"ALERT: {path}"

    reflex.bind(
        "**/severity=critical/**",
        alert_critical,
        name="critical_alerter",
        priority=100  # Highest priority
    )
    print("  Bound: critical_alerter (**/severity=critical/**)")

    # Reflex 4: Archive successes
    def archive_success(path, _content):
        archive_dir = test_root / "_archive" / "successes"
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive_path = archive_dir / path.name
        shutil.copy(path, archive_path)
        return f"archived to {archive_path}"

    reflex.bind(
        "**/outcome=success/**",
        archive_success,
        name="success_archiver",
        priority=1
    )
    print("  Bound: success_archiver (**/outcome=success/**)")

    # --- Create test files ---
    print("\n[CREATING TEST FILES]")

    test_files = [
        ("logs/level=error/severity=critical/alert1.json",
         {"level": "error", "severity": "critical", "message": "Database connection lost"}),

        ("logs/level=error/severity=high/error1.json",
         {"level": "error", "severity": "high", "message": "API timeout"}),

        ("logs/level=warning/warn1.json",
         {"level": "warning", "message": "Disk usage at 80%"}),

        ("memories/outcome=success/task=deploy/deploy1.json",
         {"outcome": "success", "task": "deploy", "duration": 45}),

        ("memories/outcome=failure/task=test/test1.json",
         {"outcome": "failure", "task": "test", "error": "assertion failed"}),

        ("memories/outcome=success/task=build/build1.json",
         {"outcome": "success", "task": "build", "duration": 120}),

        ("metrics/severity=critical/metric1.json",
         {"severity": "critical", "cpu": 99, "memory": 95}),
    ]

    for rel_path, content in test_files:
        full_path = test_root / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w") as f:
            json.dump(content, f, indent=2)
        print(f"  Created: {rel_path}")

    # --- Trigger reflexes ---
    print("\n[TRIGGERING REFLEXES]")

    for rel_path, content in test_files:
        full_path = test_root / rel_path
        print(f"\n  Checking: {rel_path}")
        events = reflex.check(full_path, content)

        for event in events:
            status = "OK" if event.success else "FAIL"
            print(f"    [{status}] {event.action_name} → {event.result} ({event.duration_ms:.1f}ms)")

    # --- Report ---
    print("\n" + "=" * 70)
    print("[REFLEX REPORT]")
    print("=" * 70)

    report = reflex.report()
    print(f"\n  Total bindings: {report['total_bindings']}")
    print(f"  Total fires: {report['total_fires']}")
    print(f"  Successful: {report['successful']}")
    print(f"  Failed: {report['failed']}")

    print("\n  Binding stats:")
    for b in report['bindings']:
        print(f"    {b['name']}: {b['fire_count']} fires")

    print(f"\n  Critical alerts triggered: {len(critical_alerts)}")
    for alert in critical_alerts:
        print(f"    - {alert['path']}")

    # Check counter file
    counter_file = test_root / "_stats" / "outcomes.json"
    if counter_file.exists():
        with open(counter_file) as f:
            counters = json.load(f)
        print(f"\n  Outcome counters:")
        for k, v in counters.items():
            if not k.startswith("_"):
                print(f"    {k}: {v}")

    # Check archive
    archive_dir = test_root / "_archive" / "successes"
    if archive_dir.exists():
        archived = list(archive_dir.glob("*.json"))
        print(f"\n  Archived successes: {len(archived)}")
        for a in archived:
            print(f"    - {a.name}")

    print("\n" + "=" * 70)
    print("The system flinches. Input → Route → Store → React.")
    print("=" * 70)
