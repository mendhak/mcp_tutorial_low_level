from mcp.server import MCPServer
from contextlib import asynccontextmanager
from fastapi import FastAPI


mcp = MCPServer("learn")

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



# Serve it over HTTP
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():
        yield

app = FastAPI(lifespan=lifespan)
app.mount("/", mcp.streamable_http_app())