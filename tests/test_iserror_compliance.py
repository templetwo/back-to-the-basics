"""Regression test for isError-compliance in back-to-the-basics MCP server.

12 `@mcp.tool()` handlers in `btb_mcp_server.py` caught `except Exception`
and returned `_format_error(e)` which is a formatted string. FastMCP wraps
the return value as success content with `isError=false`, so MCP clients
treat the failure as data and the LLM often proceeds as if the call had
succeeded.

The fix replaces each swallowed-error return with bare `raise` so the
original exception propagates and FastMCP sets `isError=true` on the wire.

Reference: https://composio.dev/blog/mcp-security-vulnerabilities (Dayna
Blackwell MCP security audit, June 2026).
"""
import pytest

try:
    from fastmcp.exceptions import ToolError
except ImportError:
    ToolError = None  # type: ignore

pytestmark = pytest.mark.skipif(
    ToolError is None, reason="fastmcp not installed; skip when unavailable"
)


def test_btb_remember_failure_raises_tool_error(monkeypatch, tmp_path):
    """A failing btb_remember call must surface as ToolError → isError=true."""
    from btb_mcp_server import mcp
    import btb_mcp_server as btb

    # Force the underlying memory storage to raise
    def _raise(*args, **kwargs):
        raise PermissionError("write denied")

    # Patch whatever the tool calls into (depends on internal API).
    # Fall back gracefully if the API surface has changed.
    patched = False
    for module_name in ("memory", "btb_mcp_server"):
        try:
            mod = __import__(module_name)
        except ImportError:
            continue
        for attr in dir(mod):
            obj = getattr(mod, attr, None)
            if callable(obj) and getattr(obj, "__module__", "") == module_name:
                try:
                    monkeypatch.setattr(f"{module_name}.{attr}", _raise)
                    patched = True
                    break
                except (AttributeError, TypeError):
                    continue
        if patched:
            break

    if not patched:
        pytest.skip("no hookable callable found in btb_mcp_server; surface may have changed")

    import asyncio

    with pytest.raises(ToolError):
        asyncio.run(mcp.call_tool("btb_remember", {"content": "x", "path": str(tmp_path)}))
