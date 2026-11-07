# Learn how MCP works with low level commands

## Setup 

Start by creating a folder for the tutorial, then a virtual environment with some dependencies that will be needed:  

```bash
mkdir -p tutorial_mcp_low_level
cd tutorial_mcp_low_level
uv init
uv sync
uv add fastmcp
```

## First MCP - basic STDIO tool

Now right away start by creating a server.py with a minimal MCP server setup:

< 01_stdio_basic/server.py >

This is simply a single method that returns the sum of two numbers, and the @mcp.tool registers it as a tool within the MCP server. 

Right now it's only visible over stdio. For now just run it. Nothing will happen but it's listening through stdio. 

```bash
fastmcp run server.py:mcp --transport stdio

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
$ fastmcp run server.py:mcp --transport stdio
{  "jsonrpc": "2.0", "id": "discover-1","method": "server/discover","params": {"_meta": {"io.modelcontextprotocol/protocolVersion": "2026-07-28", "io.modelcontextprotocol/clientInfo": { "name": "ExampleClient", "version": "1.0.0" },"io.modelcontextprotocol/clientCapabilities":{}}}}

{"jsonrpc":"2.0","id":"discover-1","result":{"cacheScope":"private","capabilities":{"prompts":{"listChanged":true},"resources":{"listChanged":true,"subscribe":true},"tools":{"listChanged":true}},"resultType":"complete","supportedVersions":["2026-07-28"],"ttlMs":0,"_meta":{"io.modelcontextprotocol/serverInfo":{"name":"learn","version":""}}}}

```

This is an awkward way of interacting with the tool, but essentially this is what your real MCP clients are doing when they use a local MCP server over stdio. Press Ctrl+C a few times to get out of this mode. 

Let's do the discover call again, pipe the input to the server. This will make our input and output a bit more readable. We can use `jq` to help us pass the payload as a single line, and also to read the response nicely. But we also need to add a little delay, otherwise the listener will treat the EOF as a shutdown signal. 


```bash
 $ echo '{
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
}' | jq -c | fastmcp run server.py:mcp --transport stdio | jq

{
  "jsonrpc": "2.0",
  "id": "discover-1",
  "result": {
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "learn",
        "version": "4.1.6"
      }
    },
    "ttlMs": 0,
    "cacheScope": "private",
    "supportedVersions": [
      "2026-07-28"
    ],
    "capabilities": {
      "logging": {},
      "prompts": {
        "listChanged": false
      },
      "resources": {
        "subscribe": false,
        "listChanged": false
      },
      "tools": {
        "listChanged": false
      },
      "extensions": {
        "io.modelcontextprotocol/ui": {}
      }
    },
    "resultType": "complete"
  }
}
```


You can see in the response, the capabilities mentions tools, so we can ask for the list of tools as our next step. The payload is similar, the method is `tools/list`. 

```bash
$ echo '{
  "jsonrpc": "2.0",
  "id": "tools-1",
  "method": "tools/list",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientCapabilities": {}
    }
  }
}' | jq -c | fastmcp run server.py:mcp --transport stdio | jq

{
  "jsonrpc": "2.0",
  "id": "tools-1",
  "result": {
    "cacheScope": "private",
    "resultType": "complete",
    "tools": [
      {
        "_meta": {
          "fastmcp": {
            "tags": []
          }
        },
        "description": "Add two integers together!",
        "inputSchema": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "a": {
              "type": "integer"
            },
            "b": {
              "type": "integer"
            }
          },
          "required": [
            "a",
            "b"
          ]
        },
        "name": "add",
        "outputSchema": {
          "properties": {
            "result": {
              "type": "integer"
            }
          },
          "required": [
            "result"
          ],
          "type": "object",
          "x-fastmcp-wrap-result": true
        },
        "title": "Add"
      }
    ],
    "ttlMs": 0,
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "learn",
        "version": "4.1.6"
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
}' | jq -c ; sleep 1) | fastmcp run server.py:mcp --transport stdio | jq

{
  "jsonrpc": "2.0",
  "id": "call-add-1",
  "result": {
    "_meta": {
      "fastmcp": {
        "wrap_result": true
      },
      "io.modelcontextprotocol/serverInfo": {
        "name": "learn",
        "version": "4.1.6"
      }
    },
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
    }
  }
}
```

## Other types - resources and prompts

MCP is well known for tools, but it has many other features. It can do resources - pieces of data or assets - and prompts - which allow natural language input for other LLM. 

Let's add a resource, and test it. 

< code snippet >


List it

```bash
$ echo '{
  "jsonrpc": "2.0",
  "id": "resource-1",
  "method": "resources/list",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientCapabilities": {}
    }
  }
}' | jq -c | fastmcp run server.py:mcp --transport stdio  | jq

{
  "jsonrpc": "2.0",
  "id": "resource-1",
  "result": {
    "cacheScope": "private",
    "resources": [
      {
        "_meta": {
          "fastmcp": {
            "tags": []
          }
        },
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
        "version": "4.1.6"
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
      "io.modelcontextprotocol/cliewe are essentially impersonatingntCapabilities": {}
    },
    "uri": "database://users"
  }
}' | jq -c ; sleep 1) | fastmcp run server.py:mcp --transport stdio  | jq


{
  "jsonrpc": "2.0",
  "id": "get-users-table-1",
  "result": {
    "cacheScope": "private",
    "contents": [
      {
        "mimeType": "text/plain",
        "text": "[{\"id\": 1, \"name\": \"Alice\"}, {\"id\": 2, \"name\": \"Bob\"}]",
        "uri": "database://users"
      }
    ],
    "resultType": "complete",
    "ttlMs": 0,
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "learn",
        "version": "4.1.6"
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
}' | jq -c; sleep 1) | fastmcp run server.py:mcp --transport stdio  | jq

{
  "jsonrpc": "2.0",
  "id": "prompt-1",
  "result": {
    "cacheScope": "private",
    "prompts": [
      {
        "_meta": {
          "fastmcp": {
            "tags": []
          }
        },
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
        "version": "4.1.6"
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
}' | jq -c ; sleep 1) | fastmcp run server.py:mcp --transport stdio  | jq

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
        "version": "4.1.6"
      }
    }
  }
}
```


## MCP over HTTP

To serve the same MCP server over HTTP, we add FastAPI integration. 

< code snippet >

Then run it with 

```bash
fastmcp run server.py:mcp --transport http --port 8000
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
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "learn",
        "version": "4.1.6"
      }
    },
    "ttlMs": 0,
    "cacheScope": "private",
    "supportedVersions": [
      "2026-07-28"
    ],
    "capabilities": {
      "logging": {},
      "prompts": {
        "listChanged": false
      },
      "resources": {
        "subscribe": false,
        "listChanged": false
      },
      "tools": {
        "listChanged": false
      },
      "extensions": {
        "io.modelcontextprotocol/ui": {}
      }
    },
    "resultType": "complete"
  }
}
```

Next, we list the tools

```bash
$ curl -s -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -H "MCP-Protocol-Version: 2026-07-28" -H "Mcp-Method: tools/list" -d '{     
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
        "_meta": {
          "fastmcp": {
            "tags": []
          }
        },
        "description": "Add two integers together!",
        "inputSchema": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "a": {
              "type": "integer"
            },
            "b": {
              "type": "integer"
            }
          },
          "required": [
            "a",
            "b"
          ]
        },
        "name": "add",
        "outputSchema": {
          "properties": {
            "result": {
              "type": "integer"
            }
          },
          "required": [
            "result"
          ],
          "type": "object",
          "x-fastmcp-wrap-result": true
        },
        "title": "Add"
      }
    ],
    "ttlMs": 0,
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "learn",
        "version": "4.1.6"
      }
    }
  }
}
```

And now to call the tool, once again notice the headers being passed - protocol version, method, and method name.  


```bash
$ curl -s -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -H "MCP-Protocol-Version: 2026-07-28" -H "Mcp-Method: tools/call" -H "Mcp-Name: add" -d '{
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
    "_meta": {
      "fastmcp": {
        "wrap_result": true
      },
      "io.modelcontextprotocol/serverInfo": {
        "name": "learn",
        "version": "4.1.6"
      }
    },
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
        "text": "[{\"id\": 1, \"name\": \"Alice\"}, {\"id\": 2, \"name\": \"Bob\"}]",
        "uri": "database://users"
      }
    ],
    "resultType": "complete",
    "ttlMs": 0,
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "learn",
        "version": "4.1.6"
      }
    }
  }
}
```

And a prompt

```bash
curl -s -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -H "MCP-Protocol-Version: 2026-07-28" -H "Mcp-Method: prompts/get" -H "Mcp-Name: ask_question"  -d '{     
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
        "version": "4.1.6"
      }
    }
  }
}
```


## HTTP Streaming 

MCPs support HTTP streaming, which allows tools to report progress over time. This is often used during chat interactions as portions of the response are generated and sent to the client.  

Add a slow_count tool to the server

< code snippet >

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
data: {"jsonrpc":"2.0","method":"notifications/progress","params":{"progressToken":"p1","progress":1.0,"total":5.0,"message":"Counted 1"}}

event: message
data: {"jsonrpc":"2.0","method":"notifications/progress","params":{"progressToken":"p1","progress":2.0,"total":5.0,"message":"Counted 2"}}

event: message
data: {"jsonrpc":"2.0","method":"notifications/progress","params":{"progressToken":"p1","progress":3.0,"total":5.0,"message":"Counted 3"}}

event: message
data: {"jsonrpc":"2.0","method":"notifications/progress","params":{"progressToken":"p1","progress":4.0,"total":5.0,"message":"Counted 4"}}

event: message
data: {"jsonrpc":"2.0","method":"notifications/progress","params":{"progressToken":"p1","progress":5.0,"total":5.0,"message":"Counted 5"}}

event: message
data: {"jsonrpc":"2.0","id":"slow-1","result":{"_meta":{"fastmcp":{"wrap_result":true},"io.modelcontextprotocol/serverInfo":{"name":"learn","version":"4.1.6"}},"content":[{"text":"Done! Counted to 5","type":"text"}],"isError":false,"resultType":"complete","structuredContent":{"result":"Done! Counted to 5"}}}

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

< code snippet >


Now run the web server again

```bash
fastmcp run server.py:mcp --transport http --port 8000
```

And try the discover endpoint once more to get an HTTP 401 response. 


```bash
 curl -s -i -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -H "MCP-Protocol-Ve
rsion: 2026-07-28" -H "Mcp-Method: server/discover" -d '{     
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
}' 
HTTP/1.1 401 Unauthorized
date: Fri, 06 Nov 2026 16:51:00 GMT
server: uvicorn
content-length: 0
www-authenticate: Bearer resource_metadata="http://localhost:8000/.well-known/oauth-protected-resource/mcp"
```
Notice in the response header, the `www-authenticate` field indicates that the resource is protected by OAuth and provides the URL to the resource metadata. This tells the client that it needs to obtain a valid access token from the identity provider (Keycloak) to access the MCP server.

Let's query that URL

```bash
curl -s http://localhost:8000/.well-known/oauth-protected-resource/mcp | jq

{
  "resource": "http://localhost:8000/mcp",
  "authorization_servers": [
    "http://localhost:8080/realms/mcp"
  ],
  "scopes_supported": [],
  "bearer_methods_supported": [
    "header"
  ]
}
```

The authorization_servers points at `http://localhost:8080/realms/mcp` which is the Keycloak realm that was configured earlier. 

We then call its well known openid-configuration

```bash
$ curl -s http://localhost:8080/realms/mcp/.well-known/openid-configuration | jq
{
  "issuer": "http://localhost:8080/realms/mcp",
  "authorization_endpoint": "http://localhost:8080/realms/mcp/protocol/openid-connect/auth",
  ...
  ...
  "client_id_metadata_document_supported": true
}
```
The `client_id_metadata_document_supported` indicates support for CIMD (Client ID Metadata Documents), so the client then knows how to proceed by generating a login URL for the user to authenticate, and obtain an access token. 

Let's actually do this, let's generate a login URL. There's a bit of bash required to construct it:

```bash
CODE_VERIFIER=$(openssl rand -base64 32 | tr '+/' '-_' | tr -d '=')
echo "CODE_VERIFIER=$CODE_VERIFIER"
CODE_CHALLENGE=$(printf '%s' "$CODE_VERIFIER" | openssl dgst -sha256 -binary | openssl base64 -A | tr '+/' '-_' | tr -d '=')

URL="http://localhost:8080/realms/mcp/protocol/openid-connect/auth?client_id=https://vscode.dev/oauth/client-metadata.json&response_type=code&code_challenge=${CODE_CHALLENGE}&code_challenge_method=S256&scope=openid+offline_access&resource=http://localhost:8000/mcp&redirect_uri=http://127.0.0.1:33418/&state=$(openssl rand -base64 16 | tr '+/' '-_' | tr -d '=')"
echo "$URL"
echo "$CODE_VERIFIER"
```

Take a moment to study the URL, notice that the client ID is set to VSCode's CIMD URL.   
Copy that URL into a browser and begin the login process, use test/test for the credentials. 

You will then see a consent screen, "Grant Access to Visual Studio Code" 

< screenshots here >

After granting access, the browser will try to redirect to the `redirect_uri` from earlier, but nothing's listening there. That's expected, we can still carry on. 

So, taking the URL, such as

```
http://127.0.0.1:33418/?state=47_CseCkvgkokQIgEfNoUQ&session_state=Yp0-PXbPKPnHKTxyEXjTIwPP&iss=http%3A%2F%2Flocalhost%3A8080%2Frealms%2Fmcp&code=cfb09146-a79d-5644-d49c-c634d9303329.Yp0-PXbPKPnHKTxyEXjTIwPP.2d6c0e01-527a-4f6f-aa0b-673fdee407b6
```

We get the `code` value from the URL, and then using the code_verifier from our URL generation step, we request an access token. 

```
curl -s -X POST http://localhost:8080/realms/mcp/protocol/openid-connect/token \
  -d grant_type=authorization_code \
  -d code=cfb09146-a79d-5644-d49c-c634d9303329.Yp0-PXbPKPnHKTxyEXjTIwPP.2d6c0e01-527a-4f6f-aa0b-673fdee407b6 \
  -d redirect_uri=http://127.0.0.1:33418/ \
  -d code_verifier=$CODE_VERIFIER \
  -d client_id=https://vscode.dev/oauth/client-metadata.json

```


Which gives an access token in the response

```
{"access_token":"eyJh.....
```

We can inspect that access token in a JWT decoder such as https://jwt.ms

<screenshot here>

And finally now that we have an access token we can call the discover endpoint, making sure to pass the Authorization: Bearer header. 

```bash

curl -s -i -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -H "MCP-Protocol-Version: 2026-07-28" -H "Mcp-Method: server/discover" -H "Authorization: Bearer eyJ.... \
  -d '{     
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
}' 


After that, all the subsequent calls are the same as before, just making sure to include the Authorization: Bearer header with the access token.

In case you haven't spotted the security hole here, the MCP CIMD mechanism allows us to impersonate any 'well known' MCP client by obtaining an access token for it, such as VSCode, Claude Code, etc. From the authorization server's perspective, they are none the wiser, they think we are the legitimate client. However, the Client ID being a URL immediately introduces the risk of SSRF, as an attacker could potentially make the server perform requests to arbitrary URLs. As can be seen, MCP's security model continues to be an afterthought, and it should not be a surprise if this goes through a number of further revisions in the future. 



## Finishing notes

The idea here was to understand MCP by implementing the calls that an MCP client would perform, but using normal tools found in Linux. This approach allows us to see the underlying mechanisms and potential security implications without relying on a specific client implementation.

That said, this set up _can_ be used with an MCP client too. With the above MCP server and Keycloak still running, it's possible to add the MCP URL to VSCode as an MCP endpoint and interact with it using the client. 

This could be as simple as an `.mcp.json` file with:

```
{
 "mcpServers": {
		"my_mcp_test": {
		"url": "http://localhost:8000/mcp",
		"type": "http"
	}
 }
}
```