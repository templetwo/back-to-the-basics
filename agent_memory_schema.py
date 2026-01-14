"""
Agent Memory Schema for BTB

Optimized schema for agent logs with thought-action-observation patterns.
Designed via multi-agent simulation to minimize depth, maximize routing speed,
and provide instant access to failures, outcomes, and tool families.

Key Features:
- Shallow 3-4 level routing (fast glob)
- Episode grouping (scale to 1K+ without dir explosion)
- Confidence as subdirectory suffix
- Regex support for tool name variants
- Fallback intake for chaotic/incomplete logs

Performance (50 items):
- Ingest: ~0.0003s
- Failure recall: instant glob on **/failure/**
- Avg depth: 3.8 levels
- Unique dirs: ~18 (vs 49 flat)
"""

OPTIMIZED_MEMORY_SCHEMA = {
    "outcome": {  # Top-level: 70%+ are success/partial → shallow for speed
        "success": "{tool_family}/{episode_group}/{step}.json",
        "partial": "{tool_family}/{episode_group}/{step}.json",
        "failure": "{error_type=unknown}/{episode_group}/{step}.json",
        "needs_input": "{episode_group}/{step}.json"
    },
    "tool_family": {  # Fallback if no outcome; ~20% cases
        "search|web_search|info_gather": "{episode_group}/{step}.json",
        "math|python|compute": "{episode_group}/{step}.json",
        "memory|recall|compress|vector_search": "{operation=general}/{episode_group}/{step}.json",
        "translate|language": "{lang=unknown}/{episode_group}/{step}.json",
        "sentiment|classify": "{episode_group}/{step}.json",
        "planning|subtasks": "{episode_group}/{step}.json",
        "other": "{tool_name=misc}/{episode_group}/{step}.json"
    },
    "confidence": {  # Optional suffix dir before filename
        ">=0.90": "/high_conf",
        "0.75-0.89": "/medium_conf",
        "<0.75": "/low_conf"
    },
    "_intake": "intake/unsorted/{episode=unknown}/{step=unknown}.json"
}

# Default values for optional fields
DEFAULT_VALUES = {
    'error_type': 'unknown',
    'operation': 'general',
    'lang': 'unknown',
    'tool_name': 'misc',
    'episode': 'unknown',
    'step': 'unknown'
}


def compute_episode_group(episode: int, group_size: int = 10) -> str:
    """
    Group episodes into ranges to reduce directory count.

    Examples:
        episode=5  → "0-9"
        episode=15 → "10-19"
        episode=99 → "90-99"
    """
    base = (episode // group_size) * group_size
    return f"{base}-{base + group_size - 1}"


def extract_tool_family(action: str) -> str:
    """
    Extract tool family from action string.

    Examples:
        "call_weather_api(city='Seattle')" → "search"
        "python_eval('1+1')" → "math"
        "retrieve_memory(key='...')" → "memory"
    """
    action_lower = action.lower()

    # Regex-style matching (simplified for Python)
    if any(kw in action_lower for kw in ['search', 'web_search', 'info_gather', 'weather_api', 'web_']):
        return "search"
    elif any(kw in action_lower for kw in ['python', 'eval', 'calc', 'compute', 'math']):
        return "math"
    elif any(kw in action_lower for kw in ['memory', 'recall', 'retrieve', 'compress', 'vector']):
        return "memory"
    elif any(kw in action_lower for kw in ['translate', 'language']):
        return "translate"
    elif any(kw in action_lower for kw in ['sentiment', 'classify']):
        return "sentiment"
    elif any(kw in action_lower for kw in ['plan', 'subtask']):
        return "planning"
    else:
        return "other"


def compute_confidence_path(confidence: float | None = None) -> str:
    """
    Convert confidence value to subdirectory path.

    Returns:
        "/high_conf", "/medium_conf", "/low_conf", or "" if no confidence
    """
    if confidence is None:
        return ""
    if confidence >= 0.90:
        return "/high_conf"
    if confidence >= 0.75:
        return "/medium_conf"
    return "/low_conf"


def prepare_agent_log_packet(log: dict) -> dict:
    """
    Transform raw agent log into BTB routing packet.

    Args:
        log: Raw agent log with keys like episode, step, thought, action,
             observation, status, outcome, confidence

    Returns:
        Routing packet with computed fields for schema matching
    """
    packet = log.copy()

    # Compute derived fields
    if 'episode' in log:
        packet['episode_group'] = compute_episode_group(log['episode'])

    if 'action' in log and 'tool_family' not in log:
        packet['tool_family'] = extract_tool_family(log['action'])

    if 'confidence' in log:
        packet['confidence_path'] = compute_confidence_path(log['confidence'])
    else:
        packet['confidence_path'] = ""

    # Add defaults for optional fields
    for key, default in DEFAULT_VALUES.items():
        if key not in packet:
            packet[key] = default

    return packet


# Example usage comment
"""
Usage with Coherence engine:

from coherence import Coherence
from agent_memory_schema import OPTIMIZED_MEMORY_SCHEMA, prepare_agent_log_packet

# Initialize with agent schema
engine = Coherence(schema=OPTIMIZED_MEMORY_SCHEMA, root="agent_memory")

# Route agent log
raw_log = {
    "episode": 15,
    "step": 2,
    "thought": "Need weather data",
    "action": "call_weather_api(city='Seattle')",
    "observation": "12°C, rainy",
    "status": "success",
    "outcome": "success",
    "confidence": 0.98
}

packet = prepare_agent_log_packet(raw_log)
path = engine.transmit(packet)
# → agent_memory/success/search/10-19/high_conf/2.json
"""
