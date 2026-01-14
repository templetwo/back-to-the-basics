# BTB Examples

Example code demonstrating BTB (Back to the Basics) usage patterns.

## Quick Start

### 1. Basic Usage (`basic_usage.py`)

Demonstrates fundamental operations:
- Storing memories with `remember()`
- Querying with `recall()` and glob patterns
- Analyzing patterns with `reflect()`

```bash
python examples/basic_usage.py
```

**Output**: Creates `example_brain/` directory with organized memory files.

---

### 2. Debugging Workflow (`debugging_workflow.py`)

Shows how BTB memory guides systematic debugging:
- Building a knowledge base from past fixes
- Querying relevant experiences when bugs appear
- Ranking techniques by relevance
- Storing new successes with metadata

```bash
python examples/debugging_workflow.py
```

⚠️ **Transparency**: This is an ILLUSTRATIVE example showing methodology, not measured experimental results.

---

## MCP Server Configuration

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "btb-memory": {
      "command": "python",
      "args": [
        "/absolute/path/to/btb_mcp_server.py",
        "--root",
        "agent_brain"
      ]
    }
  }
}
```

See `claude_desktop_config.json` for complete example.

### Generic MCP Client

See `mcp_client_config.json` for configuration template.

---

## Directory Structure After Running Examples

```
.
├── example_brain/              # From basic_usage.py
│   ├── outcome=success/
│   │   └── tool=code_interpreter/
│   │       ├── task_type=write/
│   │       └── task_type=debug/
│   ├── outcome=failure/
│   └── outcome=learning/
│
└── debugging_brain/            # From debugging_workflow.py
    └── outcome=success/
        └── tool=code_interpreter/
            └── task_type=debug/
```

---

## MCP Tools Available

Once configured as an MCP server, these tools become available:

### `btb_remember`
Store a new memory with automatic routing.

### `btb_recall`
Query memories by pattern or intent.

### `btb_reflect`
Analyze memory topology and patterns.

### `btb_map`
Visualize the memory structure as ASCII tree.

### `btb_hotspots`
Find areas of high data concentration.

---

## Creating Your Own Examples

```python
from memory import MemoryEngine

# Initialize
memory = MemoryEngine(root="my_brain")

# Store
path = memory.remember(
    content="What you learned or did",
    outcome="success",  # or "failure", "learning", "interaction"
    tool="code_interpreter",
    task_type="debug",  # Required for code_interpreter success
    summary="descriptive_name"
)

# Recall
memories = memory.recall(pattern="my_brain/outcome=success/**/*.json")

# Reflect
analysis = memory.reflect()
print(f"Total memories: {analysis['total_memories']}")
```

---

## Next Steps

1. Run the examples
2. Explore the generated `*_brain/` directories
3. Use `tree` command to visualize topology
4. Configure as MCP server for your agent
5. Build your own domain-specific schemas

---

*For full documentation, see the main README.md*
