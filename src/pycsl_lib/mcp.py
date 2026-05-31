"""PyCSL mock for mcp (Model Context Protocol).

Provides trusted stubs for the MCP server framework.
"""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def FastMCP(name: int) -> int:
    """Mock: create a FastMCP server instance."""
    return 0

#@ \trusted
#@ ensures \result == 0
def FastMCP_run(self: int) -> int:
    """Mock: start the MCP server."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def FastMCP_tool(self: int, fn: int) -> int:
    """Mock: register a tool handler."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def FastMCP_resource(self: int, uri: int) -> int:
    """Mock: register a resource handler."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def FastMCP_prompt(self: int, fn: int) -> int:
    """Mock: register a prompt handler."""
    return 0
