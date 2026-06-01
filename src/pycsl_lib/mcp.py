"""PyCSL mock for mcp (Model Context Protocol).

Provides trusted stubs for the MCP server framework.
"""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/server/fastmcp/server.py
#@ requires True
#@ ensures True
def FastMCP(name: int) -> int:
    """Mock: create a FastMCP server instance."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/jlowin/fastmcp/blob/main/src/fastmcp/server/server.py
#@ requires True
#@ ensures True
def FastMCP_run(self: int) -> int:
    """Mock: start the MCP server."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/server/fastmcp/server.py
#@ requires True
#@ ensures True
def FastMCP_tool(self: int, fn: int) -> int:
    """Mock: register a tool handler."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/jlowin/fastmcp/blob/main/src/fastmcp/server/server.py
#@ requires True
#@ ensures True
def FastMCP_resource(self: int, uri: int) -> int:
    """Mock: register a resource handler."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/jlowin/fastmcp/blob/main/src/fastmcp/server/server.py
#@ requires True
#@ ensures True
def FastMCP_prompt(self: int, fn: int) -> int:
    """Mock: register a prompt handler."""
    return 0
