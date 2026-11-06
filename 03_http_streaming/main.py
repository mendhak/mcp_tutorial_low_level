import asyncio
from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from contextlib import asynccontextmanager
from fastapi import FastAPI


mcp = MCPServer("learn")


# Serve it over HTTP
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():
        yield

app = FastAPI(lifespan=lifespan)
app.mount("/", mcp.streamable_http_app())

# A slow tool with progress, for streaming HTTP. 
@mcp.tool()
async def slow_count(n: int, ctx: Context) -> str:
    """Count to n, reporting progress each second"""
    for i in range(1, n + 1):
        await asyncio.sleep(1)
        await ctx.report_progress(i, n, f"Counted {i}")
    return f"Done! Counted to {n}"