import asyncio
from fastmcp import Context, FastMCP
from fastmcp.server.auth import RemoteAuthProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier
from pydantic import AnyHttpUrl


ISSUER = "http://localhost:8080/realms/mcp"
AUDIENCE = "http://localhost:8000/mcp"  # must match an `aud` claim configured in Keycloak

auth = RemoteAuthProvider(
    token_verifier=JWTVerifier(
        jwks_uri=f"{ISSUER}/protocol/openid-connect/certs",
        issuer=ISSUER,
        audience=AUDIENCE,
        algorithm="RS256",
    ),
    authorization_servers=[AnyHttpUrl(ISSUER)],
    base_url="http://localhost:8000",
)

# Unauthenticated: use this one.
mcp = FastMCP("learn")

# Authenticated: use this one instead 
# mcp = FastMCP("learn", auth=auth)


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers together!"""
    return a + b


@mcp.resource("database://users")
def users_table() -> list[dict]:
    """Return a table of the users"""
    return [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
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
