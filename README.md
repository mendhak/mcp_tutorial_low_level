# Learn how MCP works with low level commands

## Setup 

Start by creating a folder for the tutorial, then a virtual environment with some dependencies that will be needed:  

```bash
mkdir -p tutorial_mcp_low_level
cd tutorial_mcp_low_level
uv init
uv sync
uv add fastapi mcp[cli] uvicorn[standard]
```

## First MCP - basic STDIO tool

Now right away start by creating a main.py with a minimal MCP server setup:

< 01_stdio_basic/main.py >

This is simply a single method that returns the sum of two numbers, and the @mcp.tool registers it as a tool within the MCP server. 

Right now it's only visible over stdio. For now just run it. Nothing will happen but it's listening through stdio. 

```bash
uv run mcp run main.py

```

You can try sending it a discover command, which will list what the server is capable of. The discover JSON is like this:

```json

{
  "jsonrpc": "2.0",
  "id": "discover-1",
  "method": "server/discover",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientInfo": {
        "name": "ExampleClient",
        "version": "1.0.0"
      },
      "io.modelcontextprotocol/clientCapabilities": {}
    }
  }
}

```

The payload contains some information about the client itself, and the important bit is the method, which in this case is `server/discover`. The client is asking the server to provide a list of its capabilities. 

However, the server in this case needs the input in a single line, rather than pretty printed. So try sending it like this:


```bash
$ uv run mcp run main.py
{  "jsonrpc": "2.0", "id": "discover-1","method": "server/discover","params": {"_meta": {"io.modelcontextprotocol/protocolVersion": "2026-07-28", "io.modelcontextprotocol/clientInfo": { "name": "ExampleClient", "version": "1.0.0" },"io.modelcontextprotocol/clientCapabilities":{}}}}

{"jsonrpc":"2.0","id":"discover-1","result":{"cacheScope":"private","capabilities":{"prompts":{"listChanged":true},"resources":{"listChanged":true,"subscribe":true},"tools":{"listChanged":true}},"resultType":"complete","supportedVersions":["2026-07-28"],"ttlMs":0,"_meta":{"io.modelcontextprotocol/serverInfo":{"name":"learn","version":""}}}}

```

This is an awkward way of interacting with the tool, but essentially this is what your real MCP clients are doing when they use a local MCP server over stdio. Press Ctrl+C a few times to get out of this mode. 

Let's do the discover call again, pipe the input to the server. This will make our input and output a bit more readable. We can use `jq` to help us pass the payload as a single line, and also to read the response nicely. But we also need to add a little delay, otherwise the listener will treat the EOF as a shutdown signal. 


```bash
 $ (echo '{
  "jsonrpc": "2.0",
  "id": "discover-1",
  "method": "server/discover",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientInfo": {
        "name": "ExampleClient",
        "version": "1.0.0"
      },
      "io.modelcontextprotocol/clientCapabilities": {}
    }
  }
}' | jq -c; sleep 1) | uv run mcp run main.py  | jq

{
  "jsonrpc": "2.0",
  "id": "discover-1",
  "result": {
    "cacheScope": "private",
    "capabilities": {
      "prompts": {
        "listChanged": true
      },
      "resources": {
        "listChanged": true,
        "subscribe": true
      },
      "tools": {
        "listChanged": true
      }
    },
    "resultType": "complete",
    "supportedVersions": [
      "2026-07-28"
    ],
    "ttlMs": 0,
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "learn",
        "version": ""
      }
    }
  }
}
```


You can see in the response, the capabilities mentions tools, so we can ask for the list of tools as our next step. The payload is similar, the method is `tools/list`. 

```bash
$ (echo '{
  "jsonrpc": "2.0",
  "id": "tools-1",
  "method": "tools/list",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientCapabilities": {}
    }
  }
}' | jq -c; sleep 1) |  uv run mcp run main.py  | jq
{
  "jsonrpc": "2.0",
  "id": "tools-1",
  "result": {
    "cacheScope": "private",
    "resultType": "complete",
    "tools": [
      {
        "description": "Add two integers together!",
        "inputSchema": {
          "type": "object",
          "properties": {
            "a": {
              "title": "A",
              "type": "integer"
            },
            "b": {
              "title": "B",
              "type": "integer"
            }
          },
          "required": [
            "a",
            "b"
          ],
          "title": "addArguments"
        },
        "name": "add",
        "outputSchema": {
          "properties": {
            "result": {
              "title": "Result",
              "type": "integer"
            }
          },
          "required": [
            "result"
          ],
          "title": "addOutput",
          "type": "object"
        }
      }
    ],
    "ttlMs": 0,
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "learn",
        "version": ""
      }
    }
  }
}
```


Interesting! The tool listed has a description which comes from the method's comment. It has an input schema, which is the two integers in the method signature. The name of the tool is the method name. With this information we have enough to know how to call the tool directly. 

Let's call the `add` tool and add 5 and 3, which we pass in the params as arguments.  

```bash
$ (echo '{
  "jsonrpc": "2.0",
  "id": "call-add-1",
  "method": "tools/call",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientCapabilities": {}
    },
    "name": "add",
    "arguments": {
      "a": 5,
      "b": 3
    }
  }
}' | jq -c; sleep 1) | uv run mcp run main.py  | jq
{
  "jsonrpc": "2.0",
  "id": "call-add-1",
  "result": {
    "content": [
      {
        "text": "8",
        "type": "text"
      }
    ],
    "isError": false,
    "resultType": "complete",
    "structuredContent": {
      "result": 8
    },
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "learn",
        "version": ""
      }
    }
  }
}
```

## What were the other two - resources and prompts

MCP is well known for tools, but it has many other features. It can do resources - pieces of data or assets - and prompts - which allow natural language input for other LLM. 

Let's add a resource, and test it. 

< code snippet >


List it

```bash
$ (echo '{
  "jsonrpc": "2.0",
  "id": "resource-1",
  "method": "resources/list",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientCapabilities": {}
    }
  }
}' | jq -c; sleep 1) |  uv run mcp run main.py  | jq

{
  "jsonrpc": "2.0",
  "id": "resource-1",
  "result": {
    "cacheScope": "private",
    "resources": [
      {
        "description": "Return a table of the users",
        "mimeType": "text/plain",
        "name": "users_table",
        "uri": "database://users"
      }
    ],
    "resultType": "complete",
    "ttlMs": 0,
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "learn",
        "version": ""
      }
    }
  }
}
```

And then call it to get the contents of the `users_table` resource.

```bash
$ (echo '{
  "jsonrpc": "2.0",
  "id": "get-users-table-1",
  "method": "resources/read",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientCapabilities": {}
    },
    "uri": "database://users"
  }
}' | jq -c; sleep 1) | uv run mcp run main.py  | jq


{
  "jsonrpc": "2.0",
  "id": "get-users-table-1",
  "result": {
    "cacheScope": "private",
    "contents": [
      {
        "mimeType": "text/plain",
        "text": "[\n  {\n    \"id\": 1,\n    \"name\": \"Alice\"\n  },\n  {\n    \"id\": 2,\n    \"name\": \"Bob\"\n  }\n]",
        "uri": "database://users"
      }
    ],
    "resultType": "complete",
    "ttlMs": 0,
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "learn",
        "version": ""
      }
    }
  }
}
```

And just for completeness, add a prompt

< snippet >


```bash
$ (echo '{
  "jsonrpc": "2.0",
  "id": "prompt-1",
  "method": "prompts/list",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientCapabilities": {}
    }
  }
}' | jq -c; sleep 1) |  uv run mcp run main.py  | jq

{
  "jsonrpc": "2.0",
  "id": "prompt-1",
  "result": {
    "cacheScope": "private",
    "prompts": [
      {
        "arguments": [
          {
            "name": "question",
            "required": true
          }
        ],
        "description": "Ask a question and get an answer",
        "name": "ask_question"
      }
    ],
    "resultType": "complete",
    "ttlMs": 0,
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "learn",
        "version": ""
      }
    }
  }
}
```

Now let's call that prompt. 


```bash
$ (echo '{
  "jsonrpc": "2.0",
  "id": "get-prompt-1",
  "method": "prompts/get",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientCapabilities": {}
    },
    "name": "ask_question",
    "arguments": {
      "question": "What is MCP?"
    }
  }
}' | jq -c; sleep 1) | uv run mcp run main.py | jq

{
  "jsonrpc": "2.0",
  "id": "get-prompt-1",
  "result": {
    "description": "Ask a question and get an answer",
    "messages": [
      {
        "content": {
          "text": "You asked: What is MCP? but there is no answer.",
          "type": "text"
        },
        "role": "user"
      }
    ],
    "resultType": "complete",
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "learn",
        "version": ""
      }
    }
  }
}
```


## MCP over HTTP

To serve the same MCP server over HTTP, we add FastAPI integration. 

<code snippet>

Then run it with 

```bash
uv run uvicorn main:app --port 8000
```

Now, let's call the same methods as before, but using curl commands. 

First, discover. Same payload as before, but we also need to add HTTP headers to indicate the protocol version and method being called. 

```bash
$ curl -s -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -H "MCP-Protocol-Version: 2026-07-28" -H "Mcp-Method: server/discover" -d '{     
  "jsonrpc": "2.0",
  "id": "discover-1",
  "method": "server/discover",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientInfo": {
        "name": "ExampleClient",
        "version": "1.0.0"
      },
      "io.modelcontextprotocol/clientCapabilities": {}
    }
  }
}' | jq

{
  "jsonrpc": "2.0",
  "id": "discover-1",
  "result": {
    "cacheScope": "private",
    "capabilities": {
      "prompts": {
        "listChanged": true
      },
      "resources": {
        "listChanged": true,
        "subscribe": true
      },
      "tools": {
        "listChanged": true
      }
    },
    "resultType": "complete",
    "supportedVersions": [
      "2026-07-28"
    ],
    "ttlMs": 0,
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "learn",
        "version": ""
      }
    }
  }
}
```

Next, we list the tools

```bash
$ curl -s -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -H "MCP-Proto
col-Version: 2026-07-28" -H "Mcp-Method: tools/list" -d '{     
  "jsonrpc": "2.0",
  "id": "tools-1",
  "method": "tools/list",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientCapabilities": {}
    }
  }
}' | jq


{
  "jsonrpc": "2.0",
  "id": "tools-1",
  "result": {
    "cacheScope": "private",
    "resultType": "complete",
    "tools": [
      {
        "description": "Add two integers together!",
        "inputSchema": {
          "type": "object",
          "properties": {
            "a": {
              "title": "A",
              "type": "integer"
            },
            "b": {
              "title": "B",
              "type": "integer"
            }
          },
          "required": [
            "a",
            "b"
          ],
          "title": "addArguments"
        },
        "name": "add",
        "outputSchema": {
          "properties": {
            "result": {
              "title": "Result",
              "type": "integer"
            }
          },
          "required": [
            "result"
          ],
          "title": "addOutput",
          "type": "object"
        }
      }
    ],
    "ttlMs": 0,
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "learn",
        "version": ""
      }
    }
  }
}
```

And now to call the tool, once again notice the headers being passed - protocol version, method, and method name.  


```bash
$ curl -s -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -H "MCP-Proto
col-Version: 2026-07-28" -H "Mcp-Method: tools/call" -H "Mcp-Name: add" -d '{
  "jsonrpc": "2.0",
  "id": "call-add-1",
  "method": "tools/call",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientCapabilities": {}
    },
    "name": "add",
    "arguments": {
      "a": 5,
      "b": 3
    }
  }
}' | jq

{
  "jsonrpc": "2.0",
  "id": "call-add-1",
  "result": {
    "content": [
      {
        "text": "8",
        "type": "text"
      }
    ],
    "isError": false,
    "resultType": "complete",
    "structuredContent": {
      "result": 8
    },
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "learn",
        "version": ""
      }
    }
  }
}
```

Just for completeness I'll also call a resource. 

```bash
 curl -s -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -H "MCP-Protocol-Version: 2026-07-28" -H "Mcp-Method: resources/read" -H "Mcp-Name: database://users"  -d '{
  "jsonrpc": "2.0",
  "id": "get-users-table-1",
  "method": "resources/read",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientCapabilities": {}
    },
    "uri": "database://users"
  }
}' | jq
{
  "jsonrpc": "2.0",
  "id": "get-users-table-1",
  "result": {
    "cacheScope": "private",
    "contents": [
      {
        "mimeType": "text/plain",
        "text": "[\n  {\n    \"id\": 1,\n    \"name\": \"Alice\"\n  },\n  {\n    \"id\": 2,\n    \"name\": \"Bob\"\n  }\n]",
        "uri": "database://users"
      }
    ],
    "resultType": "complete",
    "ttlMs": 0,
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "learn",
        "version": ""
      }
    }
  }
}
```

And a prompt

```bash
curl -s -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -H "MCP-Proto
col-Version: 2026-07-28" -H "Mcp-Method: prompts/get" -H "Mcp-Name: ask_question"  -d '{     
  "jsonrpc": "2.0",
  "id": "get-prompt-1",
  "method": "prompts/get",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientCapabilities": {}
    },
    "name": "ask_question",
    "arguments": {
      "question": "What is MCP?"
    }
  }
}' | jq
{
  "jsonrpc": "2.0",
  "id": "get-prompt-1",
  "result": {
    "description": "Ask a question and get an answer",
    "messages": [
      {
        "content": {
          "text": "You asked: What is MCP? but there is no answer.",
          "type": "text"
        },
        "role": "user"
      }
    ],
    "resultType": "complete",
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "learn",
        "version": ""
      }
    }
  }
}
```


## HTTP Streaming 

MCPs support HTTP streaming, which allows tools to report progress over time. This is often used during chat interactions as portions of the response are generated and sent to the client.  

Add a slow_count tool to the server

<code snippet>

Now when calling it, notice how the response comes back in blocks as report prgoresses. 

```bash

curl -N http://localhost:8000/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Mcp-Protocol-Version: 2026-07-28' \
  -H 'Mcp-Method: tools/call' \
  -H 'Mcp-Name: slow_count' \
  -d '{
    "jsonrpc": "2.0",
    "id": "slow-1",
    "method": "tools/call",
    "params": {
      "_meta": {
        "io.modelcontextprotocol/protocolVersion": "2026-07-28",
        "io.modelcontextprotocol/clientCapabilities": {},
        "progressToken": "p1"
      },
      "name": "slow_count",
      "arguments": {"n": 5}
    }
  }'

event: message
data: {"jsonrpc":"2.0","method":"notifications/progress","params":{"progressToken":"p1","progress":1,"total":5,"message":"Counted 1"}}

event: message
data: {"jsonrpc":"2.0","method":"notifications/progress","params":{"progressToken":"p1","progress":2,"total":5,"message":"Counted 2"}}

event: message
data: {"jsonrpc":"2.0","method":"notifications/progress","params":{"progressToken":"p1","progress":3,"total":5,"message":"Counted 3"}}

event: message
data: {"jsonrpc":"2.0","method":"notifications/progress","params":{"progressToken":"p1","progress":4,"total":5,"message":"Counted 4"}}

event: message
data: {"jsonrpc":"2.0","method":"notifications/progress","params":{"progressToken":"p1","progress":5,"total":5,"message":"Counted 5"}}

event: message
data: {"jsonrpc":"2.0","id":"slow-1","result":{"content":[{"text":"Counted to 5","type":"text"}],"isError":false,"resultType":"complete","structuredContent":{"result":"Counted to 5"},"_meta":{"io.modelcontextprotocol/serverInfo":{"name":"learn","version":""}}}}

```

## HTTP with Authentication

Now on to everyone's favourite topic - security. 

So far we've had unauthenticated HTTP requests. We can add authentication. 

To do this we'll need a few moving parts and a bit of a primer. We'll need an identity server, for this we'll use Keycloak. Don't worry I've preconfigured it. 
We'll also need to configure the MCP server to require an access token, issued by that identity server, for incoming requests. 
But it isn't enough to just let any MCP client connect, the 2026-07-28 protocol requires that clients be preconfigured and have an online presence registered with the server. This is known as Client Identification Metadata Document (CIMD).  

For example, the CIMD URL for Visual Studio Code is: https://vscode.dev/oauth/client-metadata.json  have a look at its contents

It contains:

```json
{
  "client_name": "Visual Studio Code",
  "logo_uri": "https://code.visualstudio.com/assets/branding/code-stable.png",
  "grant_types": [
    "authorization_code",
    "refresh_token",
    "urn:ietf:params:oauth:grant-type:device_code"
  ],
  "response_types": [
    "code"
  ],
  "token_endpoint_auth_method": "none",
  "application_type": "native",
  "client_id": "https://vscode.dev/oauth/client-metadata.json",
  "client_uri": "https://vscode.dev/product",
  "redirect_uris": [
    "http://127.0.0.1:33418/",
    "https://vscode.dev/redirect"
  ]
}
```

We need to register those details in KeyCloak, so that it knows about the client, in this case VSCode, which in turn gives Keycloak information on the name, logo, and where to redirect after authentication. 

### Keycloak Configuration

Run the docker compose up shown here <link TBD>. It requires the realms.json <link TBD>

Run 

```bash
docker compose up
```

And have a browse at http://localhost:8080 to access the Keycloak admin console, use the credentials admin/admin. You will find a [client profile](http://localhost:8080/admin/master/console/#/mcp/realm-settings/client-policies/cimd-profile/edit-profile) and a [client policy](http://localhost:8080/admin/master/console/#/mcp/realm-settings/client-policies/cimd-policy/edit-policy/client-id-uri/edit-condition) configured for VSCode's metadata. 


### MCP Server Oauth configuration

Modify the MCP server configuration to include the Keycloak identity provider. 


```python

ISSUER = "http://localhost:8080/realms/mcp"
MCP_URL = "http://localhost:8000/mcp"
AUDIENCE = MCP_URL  # must match an `aud` claim you configure in Keycloak

mcp = MCPServer( 
    "learn",
    token_verifier=KeycloakVerifier(),
    auth=AuthSettings(
        issuer_url=ISSUER,
        resource_server_url=MCP_URL,
        required_scopes=["openid"],
        validate_token_resource=True,
    ),
)

```


