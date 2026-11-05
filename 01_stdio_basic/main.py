from mcp.server import MCPServer

mcp = MCPServer("learn")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers together!"""
    return a+b