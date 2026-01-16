"""
Schema Discovery via Ward Linkage Clustering

This module implements the derive() capability for BTB:
discovering optimal filesystem routing schemas from chaotic data patterns.

Based on DERIVE_IMPLEMENTATION_GUIDE.md
"""

from typing import List, Dict
from collections import defaultdict
import re

# Optional dependencies for clustering
try:
    import numpy as np
    from sklearn.cluster import AgglomerativeClustering
    CLUSTERING_AVAILABLE = True
except ImportError:
    np = None  # type: ignore
    AgglomerativeClustering = None  # type: ignore
    CLUSTERING_AVAILABLE = False


def derive_schema(file_paths: List[str], max_clusters: int = 5) -> Dict:
    """
    Discover optimal routing schema from file paths.

    Analyzes path patterns to extract key=value segments and generates
    a hierarchical schema for filesystem routing.

    Args:
        file_paths: List of file paths (relative or absolute)
        max_clusters: Maximum number of natural groupings to discover

    Returns:
        Dict with '_derived': True and '_structure': schema_dict

    Example:
        >>> paths = [
        ...     "data/region=us-east/sensor=lidar/date=2026-01-01/0.parquet",
        ...     "data/region=us-west/sensor=thermal/date=2026-01-02/1.parquet"
        ... ]
        >>> schema = derive_schema(paths)
        >>> schema['_structure']['region']['us-east']
        {'sensor': {...}}
    """
    if not file_paths:
        return {"_derived": True, "_structure": {}, "_stats": {"path_count": 0}}

    # Extract features from paths
    features = extract_path_features(file_paths)

    # Cluster paths by similarity
    if CLUSTERING_AVAILABLE and len(file_paths) >= 2:
        clusters = cluster_paths_ward(file_paths, features, max_clusters)
    else:
        clusters = cluster_paths_simple(file_paths, features)

    # Generate schema for each cluster
    cluster_schemas = {}
    for cluster_id, paths_in_cluster in clusters.items():
        schema = generate_schema_from_paths(paths_in_cluster)
        cluster_schemas[cluster_id] = {
            "schema": schema,
            "path_count": len(paths_in_cluster),
            "sample_paths": paths_in_cluster[:3]
        }

    # Merge cluster schemas into unified structure
    merged_schema = merge_cluster_schemas(cluster_schemas)

    return {
        "_derived": True,
        "_structure": merged_schema,
        "_stats": {
            "path_count": len(file_paths),
            "clusters": len(clusters),
            "unique_keys": len(features["keys"])
        }
    }


def extract_path_features(paths: List[str]) -> Dict:
    """
    Extract routing features from file paths.

    Analyzes paths for:
    - key=value patterns (e.g., region=us-east)
    - Common directory segments
    - Numerical patterns
    - File extensions

    Returns:
        Dict with keys, values, patterns
    """
    features = {
        "keys": set(),
        "key_values": defaultdict(set),
        "segments": defaultdict(int),
        "depths": []
    }

    for path in paths:
        # Normalize path separators
        path = path.replace('\\', '/')
        segments = path.split('/')
        features["depths"].append(len(segments))

        for segment in segments:
            features["segments"][segment] += 1

            # Extract key=value patterns
            if '=' in segment:
                parts = segment.split('=', 1)
                if len(parts) == 2:
                    key, value = parts
                    features["keys"].add(key)
                    features["key_values"][key].add(value)

    return features


def cluster_paths_ward(paths: List[str], features: Dict, max_clusters: int) -> Dict[int, List[str]]:
    """
    Cluster paths using Ward linkage hierarchical clustering.

    Vectorizes paths based on:
    - Presence of key=value patterns
    - Directory depth
    - Segment overlap

    Returns:
        Dict mapping cluster_id → list of paths
    """
    # Ensure numpy and sklearn are available
    if not CLUSTERING_AVAILABLE or np is None or AgglomerativeClustering is None:
        return cluster_paths_simple(paths, features)

    # Vectorize paths
    all_keys = sorted(features["keys"])
    all_segments = sorted([s for s, count in features["segments"].items() if count > 1])

    vectors = []
    for path in paths:
        vec = []

        # Key presence features
        for key in all_keys:
            vec.append(1 if f"{key}=" in path else 0)

        # Common segment features
        for seg in all_segments[:10]:  # Limit to top 10
            vec.append(1 if seg in path else 0)

        # Depth feature (normalized)
        depth = len(path.split('/'))
        vec.append(depth / 10.0)  # Normalize to ~0-1 range

        vectors.append(vec)

    X = np.array(vectors)

    # Determine optimal cluster count
    n_clusters = min(max_clusters, len(paths))
    if n_clusters < 2:
        return {0: paths}

    # Apply Ward linkage
    clustering = AgglomerativeClustering(
        n_clusters=n_clusters,
        linkage='ward'
    )
    labels = clustering.fit_predict(X)

    # Group paths by cluster
    clusters = defaultdict(list)
    for i, path in enumerate(paths):
        clusters[int(labels[i])].append(path)

    return clusters


def cluster_paths_simple(paths: List[str], features: Dict) -> Dict[int, List[str]]:
    """
    Fallback clustering when sklearn unavailable.

    Groups paths by:
    1. Most common key=value pattern
    2. Directory depth
    """
    clusters = defaultdict(list)

    # Find most common key
    most_common_key = None
    if features["keys"]:
        most_common_key = max(
            features["keys"],
            key=lambda k: len(features["key_values"][k])
        )

    if most_common_key:
        # Group by values of most common key
        for path in paths:
            match = re.search(rf"{most_common_key}=([^/]+)", path)
            if match:
                value = match.group(1)
                # Use hash of value as cluster ID for stability
                cluster_id = hash(value) % 10
                clusters[cluster_id].append(path)
            else:
                clusters[999].append(path)  # Uncategorized
    else:
        # No key=value patterns, group by depth
        for path in paths:
            depth = len(path.split('/'))
            clusters[depth].append(path)

    return clusters


def generate_schema_from_paths(paths: List[str]) -> Dict:
    """
    Generate hierarchical schema from a cluster of similar paths.

    Analyzes path structure to create nested routing schema.

    Args:
        paths: List of similar file paths

    Returns:
        Nested schema dict
    """
    if not paths:
        return {}

    # Extract all key=value pairs at each depth level
    level_patterns = defaultdict(lambda: defaultdict(set))

    for path in paths:
        segments = path.replace('\\', '/').split('/')
        for depth, segment in enumerate(segments):
            if '=' in segment:
                key, value = segment.split('=', 1)
                level_patterns[depth][key].add(value)

    # Build nested schema from patterns
    schema = {}

    # Sort levels for consistent nesting
    sorted_levels = sorted(level_patterns.keys())

    for level in sorted_levels:
        patterns_at_level = level_patterns[level]

        for key, values in patterns_at_level.items():
            if key not in schema:
                schema[key] = {}

            # Create branches for each value
            for value in sorted(values):
                if len(sorted_levels) > level + 1:
                    # More levels exist, nest deeper
                    next_level = sorted_levels[level + 1]
                    next_patterns = level_patterns[next_level]

                    if next_patterns:
                        # Create nested structure
                        next_key = list(next_patterns.keys())[0]
                        schema[key][value] = {next_key: {}}
                    else:
                        # Leaf node
                        schema[key][value] = "{filename}.json"
                else:
                    # Leaf level
                    schema[key][value] = "{filename}.json"

    return schema


def merge_cluster_schemas(cluster_schemas: Dict) -> Dict:
    """
    Merge schemas from multiple clusters into unified schema.

    Strategy:
    - Use schema from largest cluster as base
    - Add unique branches from other clusters
    - Preserve all routing dimensions discovered
    """
    if not cluster_schemas:
        return {}

    # Find largest cluster
    largest_cluster_id = max(
        cluster_schemas.keys(),
        key=lambda cid: cluster_schemas[cid]["path_count"]
    )

    merged = cluster_schemas[largest_cluster_id]["schema"].copy()

    # Add unique keys from other clusters
    for cluster_id, cluster_data in cluster_schemas.items():
        if cluster_id == largest_cluster_id:
            continue

        schema = cluster_data["schema"]
        for key, branches in schema.items():
            if key not in merged:
                merged[key] = branches
            else:
                # Merge branches
                for branch_value, branch_schema in branches.items():
                    if branch_value not in merged[key]:
                        merged[key][branch_value] = branch_schema

    return merged


def compute_episode_group(episode: int, group_size: int = 10) -> str:
    """
    Compute logarithmic episode grouping.

    Groups episodes into buckets: 0-9, 10-99, 100-999, etc.
    Prevents O(n) directory explosion.

    Args:
        episode: Episode number
        group_size: Size of initial group (default 10)

    Returns:
        Group string like "0-9", "10-99", "100-999"
    """
    if episode < 0:
        episode = 0

    if episode < group_size:
        return f"0-{group_size - 1}"

    # Determine magnitude
    magnitude = len(str(episode)) - 1
    lower = 10 ** magnitude
    upper = (10 ** (magnitude + 1)) - 1

    return f"{lower}-{upper}"


def extract_tool_family(tool_or_action: str) -> str:
    """
    Extract tool family from action string.

    Maps specific tools to broader categories:
    - search, web_search, info_gather → "search"
    - python_repl, code_interpreter → "compute"
    - translate_en, translate_es → "translate"

    Args:
        tool_or_action: Tool name or action string

    Returns:
        Tool family category
    """
    # Define tool families (pipe-delimited patterns)
    families = {
        "search": r"search|web_search|info_gather|query",
        "compute": r"python|code|math|calculate|interpreter",
        "memory": r"memory|recall|remember|store",
        "translate": r"translate|trans_",
        "sentiment": r"sentiment|emotion|analyze_tone",
        "planning": r"plan|schedule|organize|strategy"
    }

    tool_lower = tool_or_action.lower()

    for family, pattern in families.items():
        if re.search(pattern, tool_lower):
            return family

    return "general"


def generate_explanation(schema: Dict, stats: Dict) -> str:
    """
    Generate human-readable explanation of discovered schema.

    Args:
        schema: The derived schema structure
        stats: Statistics about derivation

    Returns:
        Formatted explanation string
    """
    lines = [
        f"Derived schema from {stats.get('path_count', 0)} paths",
        f"Discovered {stats.get('clusters', 0)} natural groupings",
        f"Found {stats.get('unique_keys', 0)} routing dimensions",
        "",
        "Schema structure:"
    ]

    for key, branches in schema.items():
        lines.append(f"  {key}:")
        if isinstance(branches, dict):
            branch_count = len(branches)
            sample_branches = list(branches.keys())[:5]
            lines.append(f"    {branch_count} branches: {', '.join(sample_branches)}")
            if branch_count > 5:
                lines.append(f"    ... and {branch_count - 5} more")

    return "\n".join(lines)
