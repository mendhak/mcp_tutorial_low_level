from fastmcp import FastMCP, Context
import asyncio

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

@mcp.tool()
async def slow_count(n: int, ctx: Context) -> str:
    """Count to n, reporting progress each second"""
    for i in range(1, n + 1):
        await asyncio.sleep(1)
        await ctx.report_progress(i, n, f"Counted {i}")
    return f"Done! Counted to {n}"