"""
Tests for derive.py schema discovery functionality.

Tests Ward linkage clustering, pattern extraction, and schema generation.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from derive import (
    derive_schema,
    extract_path_features,
    cluster_paths_simple,
    generate_schema_from_paths,
    merge_cluster_schemas,
    compute_episode_group,
    extract_tool_family
)


class TestDeriveSchema:
    """Tests for main derive_schema() function."""

    def test_empty_paths(self):
        """Test derive with no paths returns empty schema."""
        result = derive_schema([])
        assert result["_derived"] is True
        assert result["_structure"] == {}
        assert result["_stats"]["path_count"] == 0

    def test_single_key_value_pattern(self):
        """Test deriving schema from single key=value pattern."""
        paths = [
            "data/region=us-east/file1.json",
            "data/region=us-west/file2.json",
            "data/region=eu-central/file3.json"
        ]
        result = derive_schema(paths)

        assert result["_derived"] is True
        assert "region" in result["_structure"]
        assert result["_stats"]["path_count"] == 3

    def test_nested_key_value_patterns(self):
        """Test deriving schema from nested key=value patterns."""
        paths = [
            "data/region=us-east/sensor=lidar/date=2026-01-01/0.parquet",
            "data/region=us-east/sensor=thermal/date=2026-01-02/1.parquet",
            "data/region=us-west/sensor=lidar/date=2026-01-01/2.parquet"
        ]
        result = derive_schema(paths)

        assert result["_derived"] is True
        assert "region" in result["_structure"]
        assert "sensor" in result["_structure"]

    def test_max_clusters_parameter(self):
        """Test that max_clusters limits discovered groups."""
        paths = [f"data/type={i}/file.json" for i in range(20)]
        result = derive_schema(paths, max_clusters=3)

        # Should discover <= 3 clusters
        assert result["_stats"]["clusters"] <= 3


class TestExtractPathFeatures:
    """Tests for path feature extraction."""

    def test_extract_keys_from_paths(self):
        """Test extracting key names from key=value patterns."""
        paths = [
            "data/region=us-east/sensor=lidar/file.json",
            "data/region=us-west/sensor=thermal/file.json"
        ]
        features = extract_path_features(paths)

        assert "region" in features["keys"]
        assert "sensor" in features["keys"]
        assert len(features["keys"]) == 2

    def test_extract_values_for_keys(self):
        """Test extracting unique values for each key."""
        paths = [
            "data/outcome=success/tool=code/file1.json",
            "data/outcome=failure/tool=search/file2.json",
            "data/outcome=success/tool=memory/file3.json"
        ]
        features = extract_path_features(paths)

        assert "success" in features["key_values"]["outcome"]
        assert "failure" in features["key_values"]["outcome"]
        assert len(features["key_values"]["outcome"]) == 2
        assert len(features["key_values"]["tool"]) == 3

    def test_extract_depth_statistics(self):
        """Test extracting directory depth information."""
        paths = [
            "shallow/file.json",
            "deeper/level2/file.json",
            "deepest/level2/level3/file.json"
        ]
        features = extract_path_features(paths)

        assert len(features["depths"]) == 3
        assert min(features["depths"]) == 2
        assert max(features["depths"]) == 4

    def test_windows_path_normalization(self):
        """Test that Windows backslashes are handled."""
        paths = ["data\\region=us\\file.json"]
        features = extract_path_features(paths)

        # Should normalize to forward slashes
        assert "region" in features["keys"]


class TestClusterPathsSimple:
    """Tests for simple (fallback) clustering."""

    def test_cluster_by_most_common_key(self):
        """Test grouping paths by most common key's values."""
        paths = [
            "data/region=us-east/file1.json",
            "data/region=us-east/file2.json",
            "data/region=us-west/file3.json"
        ]
        features = extract_path_features(paths)
        clusters = cluster_paths_simple(paths, features)

        # Should group by region values
        assert len(clusters) >= 2

    def test_fallback_to_depth_clustering(self):
        """Test clustering by depth when no key=value patterns."""
        paths = [
            "shallow/file1.json",
            "deep/level2/file2.json",
            "deeper/level2/level3/file3.json"
        ]
        features = extract_path_features(paths)
        clusters = cluster_paths_simple(paths, features)

        # Should group by directory depth
        assert len(clusters) >= 2


class TestGenerateSchemaFromPaths:
    """Tests for schema generation from path clusters."""

    def test_generate_single_level_schema(self):
        """Test generating schema from single-level patterns."""
        paths = [
            "data/outcome=success/file1.json",
            "data/outcome=failure/file2.json"
        ]
        schema = generate_schema_from_paths(paths)

        assert "outcome" in schema
        assert "success" in schema["outcome"]
        assert "failure" in schema["outcome"]

    def test_generate_nested_schema(self):
        """Test generating nested schema from multi-level patterns."""
        paths = [
            "data/outcome=success/tool=code/file1.json",
            "data/outcome=failure/tool=search/file2.json"
        ]
        schema = generate_schema_from_paths(paths)

        assert "outcome" in schema
        # Should have nesting for tool
        # (exact structure depends on implementation)

    def test_empty_paths_returns_empty_schema(self):
        """Test that empty path list returns empty schema."""
        schema = generate_schema_from_paths([])
        assert schema == {}


class TestMergeClusterSchemas:
    """Tests for merging schemas from multiple clusters."""

    def test_merge_uses_largest_cluster(self):
        """Test that largest cluster's schema is used as base."""
        cluster_schemas = {
            0: {
                "schema": {"outcome": {"success": "{file}.json"}},
                "path_count": 10
            },
            1: {
                "schema": {"tool": {"code": "{file}.json"}},
                "path_count": 5
            }
        }
        merged = merge_cluster_schemas(cluster_schemas)

        # Should have outcome (from largest cluster)
        assert "outcome" in merged

    def test_merge_adds_unique_keys(self):
        """Test that unique keys from smaller clusters are added."""
        cluster_schemas = {
            0: {
                "schema": {"outcome": {"success": "{file}.json"}},
                "path_count": 10
            },
            1: {
                "schema": {"tool": {"code": "{file}.json"}},
                "path_count": 5
            }
        }
        merged = merge_cluster_schemas(cluster_schemas)

        # Should have both keys
        assert "outcome" in merged
        assert "tool" in merged

    def test_merge_empty_schemas(self):
        """Test merging when no schemas provided."""
        merged = merge_cluster_schemas({})
        assert merged == {}


class TestComputeEpisodeGroup:
    """Tests for logarithmic episode grouping."""

    def test_small_episodes_group_0_9(self):
        """Test that episodes 0-9 group to '0-9'."""
        assert compute_episode_group(0) == "0-9"
        assert compute_episode_group(5) == "0-9"
        assert compute_episode_group(9) == "0-9"

    def test_medium_episodes_group_10_99(self):
        """Test that episodes 10-99 group to '10-99'."""
        assert compute_episode_group(10) == "10-99"
        assert compute_episode_group(50) == "10-99"
        assert compute_episode_group(99) == "10-99"

    def test_large_episodes_group_100_999(self):
        """Test that episodes 100-999 group to '100-999'."""
        assert compute_episode_group(100) == "100-999"
        assert compute_episode_group(500) == "100-999"
        assert compute_episode_group(999) == "100-999"

    def test_very_large_episodes(self):
        """Test that very large episodes use correct magnitude."""
        assert compute_episode_group(1000) == "1000-9999"
        assert compute_episode_group(10000) == "10000-99999"

    def test_negative_episodes_treated_as_zero(self):
        """Test that negative episodes are treated as 0."""
        assert compute_episode_group(-5) == "0-9"


class TestExtractToolFamily:
    """Tests for tool family extraction."""

    def test_search_family(self):
        """Test extracting search tool family."""
        assert extract_tool_family("web_search") == "search"
        assert extract_tool_family("info_gather") == "search"
        assert extract_tool_family("query_db") == "search"

    def test_compute_family(self):
        """Test extracting compute tool family."""
        assert extract_tool_family("python_repl") == "compute"
        assert extract_tool_family("code_interpreter") == "compute"
        assert extract_tool_family("math_solver") == "compute"

    def test_memory_family(self):
        """Test extracting memory tool family."""
        assert extract_tool_family("memory_store") == "memory"
        assert extract_tool_family("recall_facts") == "memory"
        assert extract_tool_family("remember") == "memory"

    def test_translate_family(self):
        """Test extracting translate tool family."""
        assert extract_tool_family("translate_en") == "translate"
        assert extract_tool_family("trans_es") == "translate"

    def test_planning_family(self):
        """Test extracting planning tool family."""
        assert extract_tool_family("plan_strategy") == "planning"
        assert extract_tool_family("organize_tasks") == "planning"

    def test_unknown_tool_returns_general(self):
        """Test that unknown tools return 'general'."""
        assert extract_tool_family("unknown_tool") == "general"
        assert extract_tool_family("xyz_123") == "general"

    def test_case_insensitive_matching(self):
        """Test that tool family matching is case-insensitive."""
        assert extract_tool_family("WEB_SEARCH") == "search"
        assert extract_tool_family("Python_REPL") == "compute"
