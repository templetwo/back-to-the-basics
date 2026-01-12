"""
The Visualizer: fMRI for the Filesystem

Renders the topology of the directory structure as a statistical map.
It helps answer: "Where is the signal accumulating?"

The filesystem is a decision tree. This shows you where the mass is.
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple


class Visualizer:
    """
    fMRI for the filesystem.

    Scans the directory topology and renders a statistical map
    showing where data is accumulating. Reveals the "bias" of
    the model encoded in your folder structure.
    """

    def __init__(self, root: str = "data"):
        self.root = Path(root)

    def map(self, max_depth: int = 10, min_percent: float = 1.0) -> None:
        """
        Generate a text-based frequency map of the directory tree.

        Args:
            max_depth: Maximum depth to display
            min_percent: Minimum percentage to display (filters noise)
        """
        if not self.root.exists():
            print(f"Root '{self.root}' does not exist.")
            return

        # 1. Walk and Count
        tree_stats = self._scan_tree(self.root)

        # 2. Render Header
        print()
        print("=" * 70)
        print(f"TOPOLOGY MAP: {self.root}/")
        print("=" * 70)
        print(f"Total Files: {tree_stats['files']}")
        print(f"Total Size:  {self._format_size(tree_stats['size'])}")
        print("-" * 70)

        # 3. Render Tree
        self._render_node(tree_stats, prefix="", depth=0, max_depth=max_depth, min_percent=min_percent)

        # 4. Render Insights
        print("-" * 70)
        insights = self._generate_insights(tree_stats)
        if insights:
            print("\nINSIGHTS:")
            for insight in insights:
                print(f"  * {insight}")
        print()

    def summary(self) -> Dict:
        """
        Generate a summary dict of the topology.

        Returns:
            Dict with counts, sizes, and top directories
        """
        if not self.root.exists():
            return {"error": f"Root '{self.root}' does not exist"}

        tree_stats = self._scan_tree(self.root)

        # Flatten to get all directories with their stats
        all_dirs = []
        self._flatten_tree(tree_stats, "", all_dirs)

        # Sort by file count
        by_files = sorted(all_dirs, key=lambda x: x[1]['files'], reverse=True)

        # Sort by size
        by_size = sorted(all_dirs, key=lambda x: x[1]['size'], reverse=True)

        return {
            "root": str(self.root),
            "total_files": tree_stats['files'],
            "total_size": tree_stats['size'],
            "total_size_human": self._format_size(tree_stats['size']),
            "top_by_files": [(p, s['files']) for p, s in by_files[:10]],
            "top_by_size": [(p, self._format_size(s['size'])) for p, s in by_size[:10]],
        }

    def hotspots(self, threshold: float = 0.5) -> List[Tuple[str, float]]:
        """
        Find directories that contain disproportionate amounts of data.

        Args:
            threshold: Percentage threshold (0.5 = 50%)

        Returns:
            List of (path, percentage) tuples for hotspots
        """
        if not self.root.exists():
            return []

        tree_stats = self._scan_tree(self.root)
        hotspots = []

        self._find_hotspots(tree_stats, "", tree_stats['files'], threshold, hotspots)

        return sorted(hotspots, key=lambda x: -x[1])

    def _scan_tree(self, path: Path) -> Dict:
        """Recursively scan tree and aggregate stats."""
        stats = {
            "name": path.name,
            "files": 0,
            "size": 0,
            "children": {}
        }

        try:
            for item in path.iterdir():
                if item.name.startswith("."):
                    continue

                if item.is_dir():
                    child_stats = self._scan_tree(item)
                    if child_stats["files"] > 0:  # Only include non-empty branches
                        stats["children"][item.name] = child_stats
                        stats["files"] += child_stats["files"]
                        stats["size"] += child_stats["size"]
                elif item.is_file():
                    stats["files"] += 1
                    try:
                        stats["size"] += item.stat().st_size
                    except (OSError, IOError):
                        pass
        except PermissionError:
            pass

        return stats

    def _render_node(self, node: Dict, prefix: str, depth: int,
                     max_depth: int, min_percent: float) -> None:
        """Render a single node line with ASCII bars."""
        if depth > max_depth:
            return

        # Sort children by file count (descending) - Pareto view
        sorted_children = sorted(
            node["children"].items(),
            key=lambda x: x[1]["files"],
            reverse=True
        )

        total_siblings = len(sorted_children)
        parent_files = node["files"]

        for i, (name, child) in enumerate(sorted_children):
            is_last = (i == total_siblings - 1)
            connector = "└── " if is_last else "├── "

            # Calculate percentage of parent
            percent = (child["files"] / parent_files) * 100 if parent_files > 0 else 0

            # Skip if below threshold
            if percent < min_percent and depth > 0:
                continue

            # Render bar (20 chars = 100%)
            bar_len = int(percent / 5)
            bar = "█" * bar_len + "░" * (20 - bar_len)

            # Format name (highlight key=value segments)
            display_name = name
            if "=" in name:
                key, val = name.split("=", 1)
                display_name = f"{key}={val}"

            # Size info
            size_str = self._format_size(child["size"])

            print(f"{prefix}{connector}{display_name:<28} {bar} {child['files']:>5} ({percent:>5.1f}%) {size_str:>10}")

            # Recurse
            extension = "    " if is_last else "│   "
            self._render_node(child, prefix + extension, depth + 1, max_depth, min_percent)

    def _flatten_tree(self, node: Dict, path: str, result: List) -> None:
        """Flatten tree into list of (path, stats) tuples."""
        for name, child in node["children"].items():
            child_path = f"{path}/{name}" if path else name
            result.append((child_path, child))
            self._flatten_tree(child, child_path, result)

    def _find_hotspots(self, node: Dict, path: str, total_files: int,
                       threshold: float, result: List) -> None:
        """Find directories exceeding threshold percentage."""
        for name, child in node["children"].items():
            child_path = f"{path}/{name}" if path else name
            percent = child["files"] / total_files if total_files > 0 else 0

            if percent >= threshold:
                result.append((child_path, percent))

            self._find_hotspots(child, child_path, total_files, threshold, result)

    def _generate_insights(self, tree_stats: Dict) -> List[str]:
        """Generate insights from the topology."""
        insights = []

        if tree_stats["files"] == 0:
            return ["No files found in this directory."]

        # Find imbalances
        all_dirs = []
        self._flatten_tree(tree_stats, "", all_dirs)

        if not all_dirs:
            return insights

        # Top directory by files
        top_by_files = max(all_dirs, key=lambda x: x[1]['files'])
        top_percent = (top_by_files[1]['files'] / tree_stats['files']) * 100
        if top_percent > 50:
            insights.append(f"'{top_by_files[0]}' contains {top_percent:.1f}% of all files (potential imbalance)")

        # Check for "failure" patterns
        failure_count = sum(s['files'] for p, s in all_dirs if 'failure' in p.lower())
        success_count = sum(s['files'] for p, s in all_dirs if 'success' in p.lower())

        if failure_count > 0 and success_count > 0:
            ratio = failure_count / success_count
            if ratio > 1:
                insights.append(f"Failure-to-success ratio: {ratio:.1f}x (more failures than successes)")
            elif ratio < 0.5:
                insights.append(f"Success-to-failure ratio: {1/ratio:.1f}x (healthy success rate)")

        # Check for "error" accumulation
        error_count = sum(s['files'] for p, s in all_dirs if 'error' in p.lower())
        if error_count > tree_stats['files'] * 0.3:
            insights.append(f"High error rate: {error_count} errors ({error_count/tree_stats['files']*100:.1f}% of total)")

        # Empty vs full
        leaf_dirs = [d for d in all_dirs if not d[1]['children']]
        if leaf_dirs:
            avg_files = sum(d[1]['files'] for d in leaf_dirs) / len(leaf_dirs)
            max_files = max(d[1]['files'] for d in leaf_dirs)
            if max_files > avg_files * 5:
                insights.append(f"Uneven distribution: max leaf has {max_files} files vs avg {avg_files:.1f}")

        return insights

    def _format_size(self, size: int) -> str:
        """Format size in human-readable form."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}PB"


# =============================================================================
# DEMONSTRATION
# =============================================================================

if __name__ == "__main__":
    import sys

    root = sys.argv[1] if len(sys.argv) > 1 else "data"

    viz = Visualizer(root)
    viz.map()

    print("\n[HOTSPOTS] Directories with >20% of total files:")
    for path, percent in viz.hotspots(threshold=0.2):
        print(f"  {path}: {percent*100:.1f}%")
