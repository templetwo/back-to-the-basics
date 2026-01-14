"""
Agent Memory Routing Example

Demonstrates BTB's optimized agent log routing with:
- Episode grouping (scale to 1K+ without dir explosion)
- Tool family classification
- Outcome-based fast recall (failures, timeouts, etc.)
- Confidence-based organization

Uses 50 synthetic agent logs inspired by ReAct, LangGraph, Auto-GPT patterns.
"""

import sys
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from coherence import Coherence
from agent_memory_schema import (
    OPTIMIZED_MEMORY_SCHEMA,
    prepare_agent_log_packet
)


# 50 synthetic agent logs (realistic patterns from 2024-2026 agent systems)
SYNTHETIC_LOGS = [
    {"episode": 1, "step": 1, "thought": "User asked for current weather in Seattle. Need real-time data.", "action": "call_weather_api(city='Seattle')", "observation": "12°C, rainy", "status": "success", "outcome": "success", "confidence": 0.98},
    {"episode": 1, "step": 2, "thought": "Weather is cold and wet. Suggest indoor activities.", "action": "none - final answer", "observation": None, "status": "complete", "outcome": "success"},
    {"episode": 2, "step": 1, "thought": "Query: plan weekend trip to NYC under $800", "action": "search_flights(origin='PHL', dest='JFK', budget=800)", "observation": "Flights $320–480 round-trip", "status": "success", "outcome": "partial"},
    {"episode": 2, "step": 2, "thought": "Flights affordable. Now check hotels.", "action": "search_hotels(city='New York', nights=2, budget=400)", "observation": "Avg $180/night", "status": "success", "outcome": "success"},
    {"episode": 3, "step": 1, "thought": "Math problem: solve 17x + 9 = 112", "action": "python_eval('(112 - 9) / 17')", "observation": "6.0588", "status": "success", "outcome": "failure", "error_type": "not_integer"},
    {"episode": 3, "step": 2, "thought": "Likely expects integer. Check equation again.", "action": "none - ask clarification", "outcome": "needs_input"},
    {"episode": 4, "step": 1, "thought": "Summarize news about xAI Grok-4 release", "action": "web_search('xAI Grok-4 release date')", "observation": "Announced Jan 2026, multimodal", "status": "success", "outcome": "success"},
    {"episode": 5, "step": 1, "thought": "User wants recipe for vegan lasagna", "action": "retrieve_memory(key='vegan recipes')", "observation": "Found 3 similar", "status": "success", "outcome": "success"},
    {"episode": 5, "step": 2, "thought": "Adapt ingredients for no-dairy", "action": "none - compile answer", "outcome": "success"},
    {"episode": 6, "step": 1, "thought": "Stock price AAPL today", "action": "finance_api('AAPL')", "observation": "Timeout after 8s", "status": "timeout", "outcome": "failure", "error_type": "timeout"},
    {"episode": 6, "step": 2, "thought": "Retry with fallback source", "action": "web_search('AAPL stock price')", "observation": "$238.45", "status": "success", "outcome": "success"},
    {"episode": 7, "step": 1, "thought": "Debug why API key is invalid", "action": "read_file('config.env')", "observation": "KEY=sk-abc123", "status": "success", "outcome": "success"},
    {"episode": 8, "step": 1, "thought": "Generate 5 tweet ideas about AI agents", "action": "llm_generate(prompt='5 creative tweet ideas...')", "observation": "[list of 5]", "status": "success", "outcome": "success"},
    {"episode": 9, "step": 1, "thought": "Classify email as urgent/spam", "action": "text_classify(text=..., labels=['urgent','spam','normal'])", "observation": "urgent", "confidence": 0.92, "outcome": "success"},
    {"episode": 10, "step": 1, "thought": "Long planning: book flight + hotel + car", "action": "plan_subtasks(['flight','hotel','car'])", "observation": "3 subtasks created", "status": "planning", "outcome": "success"},
    {"episode": 11, "step": 1, "thought": "User reports bug in agent loop", "action": "analyze_log(log=last_20_steps)", "observation": "Infinite loop in tool retry", "status": "success", "outcome": "success"},
    {"episode": 12, "step": 1, "thought": "Calculate compound interest P=1000 r=0.05 t=10", "action": "python_eval('1000 * (1+0.05)**10')", "observation": "1628.89", "status": "success", "outcome": "success"},
    {"episode": 13, "step": 1, "thought": "Find PDF on quantum computing basics", "action": "search_papers('quantum computing intro')", "observation": "arxiv.org/pdf/2301.08234", "status": "success", "outcome": "success"},
    {"episode": 14, "step": 1, "thought": "Too many steps → summarize memory", "action": "compress_memory(last=50)", "observation": "Reduced to 8 key facts", "status": "success", "outcome": "success"},
    {"episode": 15, "step": 1, "thought": "Translate 'Bonjour le monde' to Japanese", "action": "translate(text=..., to='ja')", "observation": "こんにちは世界", "status": "success", "outcome": "success"},
    {"episode": 16, "step": 1, "thought": "Create to-do list from meeting transcript", "action": "extract_tasks(text=transcript)", "observation": "5 action items", "status": "success", "outcome": "success"},
    {"episode": 17, "step": 1, "thought": "Check if port 8080 is open", "action": "network_scan(host='localhost', port=8080)", "observation": "open", "status": "success", "outcome": "success"},
    {"episode": 18, "step": 1, "thought": "Generate README.md for new repo", "action": "template_fill('readme', project='AI Agent Memory')", "observation": "Markdown generated", "status": "success", "outcome": "success"},
    {"episode": 19, "step": 1, "thought": "User frustrated – detect sentiment", "action": "sentiment_analysis('this agent is useless')", "observation": "negative 0.87", "status": "success", "outcome": "success"},
    {"episode": 20, "step": 1, "thought": "Prioritize tasks by deadline", "action": "sort_tasks_by('deadline')", "observation": "Sorted list", "status": "success", "outcome": "success"},
    {"episode": 21, "step": 1, "thought": "Error 429 rate limit", "action": "backoff_sleep(60)", "observation": "Waited, retry ok", "status": "recovered", "outcome": "success"},
    {"episode": 22, "step": 1, "thought": "Find similar past episodes", "action": "vector_search(query='weather query', k=3)", "observation": "Ep 1,4,15 similar", "status": "success", "outcome": "success"},
    {"episode": 23, "step": 1, "thought": "Code review PR #45", "action": "diff_analyze(pr=45)", "observation": "3 suggestions", "status": "success", "outcome": "success"},
    {"episode": 24, "step": 1, "thought": "Plot training loss curve", "action": "matplotlib_plot(losses)", "observation": "Figure saved", "status": "success", "outcome": "success"},
    {"episode": 25, "step": 1, "thought": "Empty observation → tool failed silently", "action": "retry_tool(max=3)", "observation": "Succeeded on retry 2", "status": "recovered", "outcome": "success"},
    # Additional 25 logs with more diversity
    {"episode": 26, "step": 1, "thought": "Database connection error", "action": "connect_db()", "observation": "Connection refused", "status": "failure", "outcome": "failure", "error_type": "connection_error", "confidence": 0.65},
    {"episode": 27, "step": 1, "thought": "Parse JSON response from API", "action": "json_parse(data)", "observation": "Parsed successfully", "status": "success", "outcome": "success", "confidence": 0.99},
    {"episode": 28, "step": 1, "thought": "Calculate average from list", "action": "python_eval('sum(data)/len(data)')", "observation": "45.2", "status": "success", "outcome": "success"},
    {"episode": 29, "step": 1, "thought": "Convert CSV to JSON", "action": "file_convert('data.csv', 'json')", "observation": "Converted 1000 rows", "status": "success", "outcome": "success"},
    {"episode": 30, "step": 1, "thought": "Validate email format", "action": "regex_match(email_pattern, input)", "observation": "Valid format", "status": "success", "outcome": "success"},
    {"episode": 31, "step": 1, "thought": "API rate limit exceeded", "action": "wait_and_retry()", "observation": "Still limited", "status": "failure", "outcome": "failure", "error_type": "rate_limit"},
    {"episode": 32, "step": 1, "thought": "Compress image file", "action": "image_compress('photo.jpg', quality=0.8)", "observation": "Reduced 80%", "status": "success", "outcome": "success"},
    {"episode": 33, "step": 1, "thought": "Summarize long article", "action": "text_summarize(article, max_len=200)", "observation": "Generated summary", "status": "success", "outcome": "success"},
    {"episode": 34, "step": 1, "thought": "Check disk space", "action": "system_info('disk')", "observation": "20GB free", "status": "success", "outcome": "success"},
    {"episode": 35, "step": 1, "thought": "Merge two lists", "action": "python_eval('list1 + list2')", "observation": "Merged", "status": "success", "outcome": "success"},
    {"episode": 36, "step": 1, "thought": "Translate Spanish to English", "action": "translate(text='Hola mundo', to='en')", "observation": "Hello world", "status": "success", "outcome": "success"},
    {"episode": 37, "step": 1, "thought": "Invalid input format", "action": "validate_input(data)", "observation": "Format error", "status": "failure", "outcome": "failure", "error_type": "validation_error"},
    {"episode": 38, "step": 1, "thought": "Create backup", "action": "file_backup('important.db')", "observation": "Backup created", "status": "success", "outcome": "success"},
    {"episode": 39, "step": 1, "thought": "Parse XML document", "action": "xml_parse(doc)", "observation": "Parsed 50 nodes", "status": "success", "outcome": "success"},
    {"episode": 40, "step": 1, "thought": "Network timeout", "action": "http_get(url)", "observation": "Timeout after 30s", "status": "timeout", "outcome": "failure", "error_type": "timeout"},
    {"episode": 41, "step": 1, "thought": "Format date string", "action": "date_format(timestamp, 'YYYY-MM-DD')", "observation": "2026-01-13", "status": "success", "outcome": "success"},
    {"episode": 42, "step": 1, "thought": "Count word frequency", "action": "word_count(text)", "observation": "Top word: 'agent' (42 times)", "status": "success", "outcome": "success"},
    {"episode": 43, "step": 1, "thought": "Encrypt password", "action": "hash_password(pwd)", "observation": "Hash generated", "status": "success", "outcome": "success"},
    {"episode": 44, "step": 1, "thought": "Parse URL components", "action": "url_parse('https://example.com/path')", "observation": "Parsed successfully", "status": "success", "outcome": "success"},
    {"episode": 45, "step": 1, "thought": "Permission denied error", "action": "file_write(path)", "observation": "Permission denied", "status": "failure", "outcome": "failure", "error_type": "permission_error"},
    {"episode": 46, "step": 1, "thought": "Generate random number", "action": "random_int(1, 100)", "observation": "73", "status": "success", "outcome": "success"},
    {"episode": 47, "step": 1, "thought": "Sort by priority", "action": "sort_by_key(data, 'priority')", "observation": "Sorted", "status": "success", "outcome": "success"},
    {"episode": 48, "step": 1, "thought": "Memory recall for similar case", "action": "vector_search(query='database error', k=5)", "observation": "Found 5 similar", "status": "success", "outcome": "success"},
    {"episode": 49, "step": 1, "thought": "Test API endpoint", "action": "http_post(url, data)", "observation": "200 OK", "status": "success", "outcome": "success"},
    {"episode": 50, "step": 1, "thought": "Unclear user request", "action": "ask_clarification()", "observation": "Awaiting response", "status": "needs_input", "outcome": "needs_input"},
]


def main():
    print("🤖 BTB Agent Memory Routing\n")
    print("=" * 70)

    # Initialize engine with agent memory schema
    print("\n📊 STEP 1: Initialize Coherence Engine with Agent Schema")
    print("-" * 70)
    engine = Coherence(schema=OPTIMIZED_MEMORY_SCHEMA, root="agent_memory")
    print("✓ Agent memory schema loaded")
    print("  - Outcome-based routing (success/partial/failure/needs_input)")
    print("  - Tool family classification (search/math/memory/etc.)")
    print("  - Episode grouping (scale to 1K+ episodes)")
    print("  - Confidence-based organization")

    # Route all 50 logs
    print("\n🔀 STEP 2: Route 50 Synthetic Agent Logs")
    print("-" * 70)
    routed_paths = []

    for log in SYNTHETIC_LOGS:
        # Prepare packet with computed fields
        packet = prepare_agent_log_packet(log)

        # Route through schema
        path = engine.transmit(packet, dry_run=True)
        routed_paths.append((log['episode'], log['step'], path))

    print(f"✓ Routed {len(routed_paths)} logs")

    # Show sample paths
    print("\n📂 Sample Routing Results:")
    for episode, step, path in routed_paths[:10]:
        print(f"  Ep{episode:02d}:S{step} → {path}")

    # Analyze distribution
    print("\n📈 STEP 3: Routing Distribution Analysis")
    print("-" * 70)

    outcome_counts = {}
    tool_counts = {}
    depth_counts = []

    for _, _, path in routed_paths:
        # Count outcomes
        for outcome in ['success', 'failure', 'partial', 'needs_input']:
            if f"/{outcome}/" in path:
                outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1

        # Count tools
        for tool in ['search', 'math', 'memory', 'translate', 'sentiment', 'planning', 'other']:
            if f"/{tool}/" in path or f"/tools/{tool}/" in path:
                tool_counts[tool] = tool_counts.get(tool, 0) + 1

        # Measure depth
        depth = path.count('/')
        depth_counts.append(depth)

    print(f"\nOutcome Distribution:")
    for outcome, count in sorted(outcome_counts.items(), key=lambda x: -x[1]):
        print(f"  {outcome:12s}: {count:2d} logs ({count/len(routed_paths)*100:.1f}%)")

    print(f"\nTool Family Distribution:")
    for tool, count in sorted(tool_counts.items(), key=lambda x: -x[1])[:5]:
        print(f"  {tool:12s}: {count:2d} logs")

    print(f"\nPath Depth Statistics:")
    print(f"  Average: {sum(depth_counts)/len(depth_counts):.1f} levels")
    print(f"  Min: {min(depth_counts)}, Max: {max(depth_counts)}")

    # Fast recall demonstrations
    print("\n🔍 STEP 4: Fast Recall Demonstrations")
    print("-" * 70)

    print("\n✓ Glob: **/failure/** (all failures)")
    failure_paths = [p for _, _, p in routed_paths if '/failure/' in p]
    print(f"  Found {len(failure_paths)} failures instantly")
    for path in failure_paths[:3]:
        print(f"    {path}")

    print("\n✓ Glob: **/timeout/** (timeout errors)")
    timeout_paths = [p for _, _, p in routed_paths if 'timeout' in p]
    print(f"  Found {len(timeout_paths)} timeouts")

    print("\n✓ Glob: **/high_conf/** (high confidence)")
    high_conf_paths = [p for _, _, p in routed_paths if '/high_conf/' in p]
    print(f"  Found {len(high_conf_paths)} high-confidence logs")

    print("\n✓ Glob: success/search/** (successful searches)")
    search_success = [p for _, _, p in routed_paths if 'success/search' in p]
    print(f"  Found {len(search_success)} successful search operations")

    # Why this wins
    print("\n⚡ STEP 5: Why This Wins for Agent Memory")
    print("-" * 70)
    print("""
  ✓ Fast failure debugging
    - Instant glob on **/failure/** for all problem logs
    - Error types pre-routed: timeout/, connection_error/, etc.

  ✓ Outcome-based metrics
    - Success rate = count(success/*) / total
    - No database scans needed

  ✓ Tool performance analysis
    - Group by tool family for batch review
    - tools/math/, tools/search/, tools/memory/

  ✓ Shallow routing (3-4 levels avg)
    - Fast OS metadata lookups
    - Minimal inode pressure

  ✓ Episode grouping scales
    - 50 logs → ~18 unique directories
    - 1K logs → ~100 directories (not 1000)
    - 10K logs → ~1000 directories (not 10000)

  ✓ Visual observability
    - `ls agent_memory/failure/` shows all problem episodes
    - Directory tree IS the dashboard
    """)

    print("\n" + "=" * 70)
    print("✓ Agent memory routing demonstration complete!")
    print("\n💡 Key Insight:")
    print("   The path encodes the agent's decision journey.")
    print("   Debugging = walking the filesystem topology.")
    print("=" * 70)


if __name__ == "__main__":
    main()
