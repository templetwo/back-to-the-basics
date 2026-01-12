#!/usr/bin/env python3
"""
Back to the Basics - CLI

The filesystem is not storage. It is a circuit.

Commands:
  derive  - Discover structure from existing paths
  route   - Route a packet through a schema
  receive - Generate glob pattern from intent
  watch   - Start Sentinel daemon to watch inbox
  map     - Visualize directory topology
  demo    - Run demonstrations
"""

import argparse
import json
import sys
from pathlib import Path

from coherence import Coherence


def cmd_derive(args):
    """Discover structure from existing paths."""
    paths = []

    if args.paths:
        paths = args.paths
    elif args.glob:
        from glob import glob
        paths = glob(args.glob, recursive=True)
    elif not sys.stdin.isatty():
        paths = [line.strip() for line in sys.stdin if line.strip()]

    if not paths:
        print("No paths provided. Use --paths, --glob, or pipe paths via stdin.", file=sys.stderr)
        sys.exit(1)

    result = Coherence.derive(paths, min_frequency=args.min_freq)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Analyzed {result.get('_path_count', 0)} paths\n")
        print("Discovered structure:")
        for key, info in result.get('_structure', {}).items():
            values = info.get('values', [])
            preview = values[:5]
            more = f" (+{len(values)-5} more)" if len(values) > 5 else ""
            print(f"  {key}: {preview}{more}")


def cmd_route(args):
    """Route a packet through a schema."""
    schema_path = Path(args.schema)
    if not schema_path.exists():
        print(f"Schema file not found: {args.schema}", file=sys.stderr)
        sys.exit(1)

    with open(schema_path) as f:
        schema = json.load(f)

    engine = Coherence(schema, root=args.root)

    # Parse packet
    packet = {}
    for kv in args.packet:
        if '=' in kv:
            k, v = kv.split('=', 1)
            try:
                v = float(v) if '.' in v else int(v)
            except ValueError:
                pass
            packet[k] = v

    path = engine.transmit(packet, dry_run=not args.write)
    print(path)

    if args.write:
        print(f"(directories created)", file=sys.stderr)


def cmd_receive(args):
    """Generate glob pattern from intent."""
    schema_path = Path(args.schema)
    if not schema_path.exists():
        print(f"Schema file not found: {args.schema}", file=sys.stderr)
        sys.exit(1)

    with open(schema_path) as f:
        schema = json.load(f)

    engine = Coherence(schema, root=args.root)

    # Parse intent
    intent = {}
    for kv in args.intent:
        if '=' in kv:
            k, v = kv.split('=', 1)
            try:
                v = float(v) if '.' in v else int(v)
            except ValueError:
                pass
            intent[k] = v

    pattern = engine.receive(**intent)
    print(pattern)


def cmd_watch(args):
    """Start the Sentinel to watch an inbox."""
    from sentinel import Sentinel, DATA_SCHEMA

    schema = DATA_SCHEMA
    if args.schema:
        with open(args.schema) as f:
            schema = json.load(f)

    s = Sentinel(inbox=args.inbox, root=args.root, schema=schema)
    s.start(interval=args.interval)


def cmd_map(args):
    """Visualize the directory topology."""
    from visualizer import Visualizer

    v = Visualizer(root=args.root)
    v.map(max_depth=args.depth, min_percent=args.min_percent)

    if args.hotspots:
        print("\n[HOTSPOTS] Directories exceeding threshold:")
        for path, percent in v.hotspots(threshold=args.hotspots / 100):
            print(f"  {path}: {percent*100:.1f}%")


def cmd_demo(_args):
    """Run the demonstration."""
    print("=" * 60)
    print("BACK TO THE BASICS")
    print("Path is Model. Storage is Inference. Glob is Query.")
    print("=" * 60)
    print()
    print("The filesystem is not storage. It is a circuit.")
    print()
    print("Run the modules directly:")
    print("  python coherence.py   # Core engine demo")
    print("  python ai_lab.py      # AI Model Factory demo")
    print("  python memory.py      # Agentic Memory demo")
    print("  python sentinel.py    # Entropy Firewall demo")
    print("  python visualizer.py  # Topology Map demo")
    print()
    print("Or use the CLI:")
    print("  btb derive --glob 'data/**/*'    # Discover structure")
    print("  btb watch --inbox _inbox         # Watch for files")
    print("  btb map --root data              # Visualize topology")
    print()
    print("Core Concepts:")
    print("  - Path is Model (directory structure = decision tree)")
    print("  - Storage is Inference (saving = classifying)")
    print("  - Glob is Query (pattern matching = database query)")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog='btb',
        description='Back to the Basics: The filesystem is not storage. It is a circuit.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Discover structure from existing paths
  btb derive --glob "data/**/*.json"

  # Route a packet through a schema
  btb route --schema schema.json type=log level=error

  # Generate glob pattern from intent
  btb receive --schema schema.json type=log

  # Watch an inbox for incoming files
  btb watch --inbox _inbox --root data

  # Visualize directory topology
  btb map --root data

  # Find hotspots (directories with >30% of files)
  btb map --root data --hotspots 30
"""
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # derive
    p_derive = subparsers.add_parser('derive', help='Discover structure from existing paths')
    p_derive.add_argument('--paths', nargs='+', help='Paths to analyze')
    p_derive.add_argument('--glob', help='Glob pattern to find paths')
    p_derive.add_argument('--min-freq', type=float, default=0.1, help='Minimum frequency threshold')
    p_derive.add_argument('--json', action='store_true', help='Output as JSON')
    p_derive.set_defaults(func=cmd_derive)

    # route
    p_route = subparsers.add_parser('route', help='Route a packet through a schema')
    p_route.add_argument('--schema', required=True, help='Path to schema JSON file')
    p_route.add_argument('--root', default='data', help='Root directory')
    p_route.add_argument('--write', action='store_true', help='Create directories')
    p_route.add_argument('packet', nargs='+', help='Key=value pairs')
    p_route.set_defaults(func=cmd_route)

    # receive
    p_receive = subparsers.add_parser('receive', help='Generate glob pattern from intent')
    p_receive.add_argument('--schema', required=True, help='Path to schema JSON file')
    p_receive.add_argument('--root', default='data', help='Root directory')
    p_receive.add_argument('intent', nargs='*', help='Key=value pairs')
    p_receive.set_defaults(func=cmd_receive)

    # watch
    p_watch = subparsers.add_parser('watch', help='Start Sentinel daemon')
    p_watch.add_argument('--inbox', default='_inbox', help='Inbox directory to watch')
    p_watch.add_argument('--root', default='data', help='Root data directory')
    p_watch.add_argument('--schema', help='Path to custom schema JSON')
    p_watch.add_argument('--interval', type=float, default=1.0, help='Polling interval in seconds')
    p_watch.set_defaults(func=cmd_watch)

    # map
    p_map = subparsers.add_parser('map', help='Visualize directory topology')
    p_map.add_argument('--root', default='data', help='Root directory to map')
    p_map.add_argument('--depth', type=int, default=10, help='Maximum depth to display')
    p_map.add_argument('--min-percent', type=float, default=1.0, help='Minimum percentage to show')
    p_map.add_argument('--hotspots', type=float, help='Show hotspots exceeding N percent')
    p_map.set_defaults(func=cmd_map)

    # demo
    p_demo = subparsers.add_parser('demo', help='Show usage examples')
    p_demo.set_defaults(func=cmd_demo)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == '__main__':
    main()
