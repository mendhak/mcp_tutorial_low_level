from fastmcp import FastMCP

mcp = FastMCP("learn")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers together!"""
    return a+b

@mcp.resource("database://users")
def users_table() -> list[dict]:
    """Return a table of the users"""
    return [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]

@mcp.prompt()
def ask_question(question: str) -> str:
    """Ask a question and get an answer"""
    return f"You asked: {question} but there is no answer."