# call_server.py
"""
Usage:
    python3 call_server.py <path_to_mcp_server_script>

Example:
    python3 call_server.py ./mcp_server.py
"""
import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.shared.exceptions import McpError


def pretty_print_content(content_item):
    """
    Helper to print a single content item returned by call_tool.
    Handles text and json content shapes commonly used by MCP tool results.
    """
    ctype = getattr(content_item, "type", None)
    if ctype == "text":
        print(getattr(content_item, "text", "<no-text>"))
    elif ctype == "json":
        # some SDKs expose `.json` as a Python object, others as text
        j = getattr(content_item, "json", None)
        if j is None:
            print("json (raw):", getattr(content_item, "text", "<no-json>"))
        else:
            import json
            print(json.dumps(j, indent=2))
    else:
        # fallback: print the object
        print(repr(content_item))


async def run(server_script_path: str):
    script = Path(server_script_path)
    if not script.exists():
        print("ERROR: server script not found:", script.resolve())
        return

    # Use the same Python interpreter to spawn the server (avoids env mismatch)
    python_exe = sys.executable
    server_params = StdioServerParameters(command=python_exe, args=[str(script.resolve())])

    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                # Handshake
                print("→ initializing session (handshake)...")
                await session.initialize()
                print("✓ session initialized")

                # Discovery: list available tools
                tools_resp = await session.list_tools()
                tools = [t.name for t in tools_resp.tools]
                print("Available tools:", tools)

                # -------------------------
                # Call fetch_schema (no parameters)
                # -------------------------
                print("\nCalling fetch_schema() ...")
                # IMPORTANT: server expects arguments wrapped under "params"
                fetch_params = {"params": {}}  # empty params object
                fetch_result = await session.call_tool("fetch_schema", fetch_params)
                if getattr(fetch_result, "content", None):
                    for idx, content in enumerate(fetch_result.content, start=1):
                        print(f"-- fetch_schema content #{idx}:")
                        pretty_print_content(content)
                else:
                    print("fetch_schema returned no content; raw result:", fetch_result)

                # -------------------------
                # Call full_agent (example parameters)
                # -------------------------
                print("\nCalling full_agent(...) ...")
                agent_params = {
                    "params": {
                        "persistent_state": {
                            "schema": None,
                            "schema_update_required": False,
                            "retries": 0,
                            "retry_logs": [],
                            "max_retries": 2
                        },
                        "user_input": "List all tables and their column counts"
                    }
                }
                agent_result = await session.call_tool("full_agent", agent_params)
                if getattr(agent_result, "content", None):
                    for idx, content in enumerate(agent_result.content, start=1):
                        print(f"-- full_agent content #{idx}:")
                        pretty_print_content(content)
                else:
                    print("full_agent returned no content; raw result:", agent_result)

    except FileNotFoundError as e:
        print("FileNotFoundError:", e)
        print("Make sure the server script path is correct and accessible.")
    except McpError as e:
        print("MCP error (connection/protocol):", e)
    except Exception as e:
        print("Unexpected error:", type(e).__name__, e)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 call_server.py <path_to_mcp_server_script>")
        sys.exit(1)
    asyncio.run(run(sys.argv[1]))
