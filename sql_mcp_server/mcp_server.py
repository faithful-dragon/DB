import logging
import inspect
import asyncio
from mcp.server.fastmcp import FastMCP

from agent_main import agent
from Nodes.FetchSchemaNode import fetch_schema_node
from Nodes.RefineUserQueryNode import refine_user_query_node
from Nodes.IntentNode import intent_node
from Nodes.GenerateSQLQueryNode import generate_sql_node
from Nodes.VerifySQLQueryNode import verify_sql_node
from Nodes.HumanApprovalNode import approval_node
from Nodes.ExecuteSQLQueryNode import execute_node
from Nodes.ParseResultNode import parse_result_node


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP("sql_mcp_server")


# -------------------------
# Node functions as MCP tools
# -------------------------
@mcp.tool()
async def fetch_schema(params: dict):
    return fetch_schema_node(params)


@mcp.tool()
async def refine_query(params: dict):
    return refine_user_query_node(params)


@mcp.tool()
async def intent(params: dict):
    return intent_node(params)


@mcp.tool()
async def generate_sql(params: dict):
    return generate_sql_node(params)


@mcp.tool()
async def verify_sql(params: dict):
    return verify_sql_node(params)

@mcp.tool()
async def approval(params: dict):
    return approval_node(params)

@mcp.tool()
async def execute(params: dict):
    return execute_node(params)

@mcp.tool()
async def parse_result(params: dict):
    return parse_result_node(params)



# ... rest of your tools decorators (unchanged) ...


# -------------------------
# Full agent pipeline as a tool
# -------------------------
@mcp.tool()
async def full_agent(params: dict):
    persistent_state = params.get("persistent_state", {
        "schema": None,
        "schema_update_required": False,
        "retries": 0,
        "retry_logs": [],
        "max_retries": 2,
    })
    user_input = params.get("user_input", "")
    persistent_state["user_input"] = user_input

    # Run LangGraph agent
    result_state = agent.invoke(persistent_state)
    persistent_state.update(result_state)

    return {
        "result": result_state.get("result"),
        "state": persistent_state
    }


# -------------------------
# Helper: log registered tools in a few ways (robust)
# -------------------------
def log_registered_tools(mcp_instance):
    # 1) Try an exposed list_tools() API (may be coroutine or sync)
    try:
        if hasattr(mcp_instance, "list_tools") and callable(getattr(mcp_instance, "list_tools")):
            try:
                tools_obj = mcp_instance.list_tools()
                if inspect.iscoroutine(tools_obj):
                    # run it synchronously here (startup time)
                    tools_obj = asyncio.get_event_loop().run_until_complete(tools_obj)
                # normalize
                if isinstance(tools_obj, (list, tuple)):
                    names = [getattr(t, "name", str(t)) for t in tools_obj]
                elif hasattr(tools_obj, "tools"):
                    names = [t.name for t in tools_obj.tools]
                else:
                    names = [str(tools_obj)]
                logger.info("Registered tools (via list_tools): %s", names)
                return
            except Exception as e:
                logger.debug("mcp.list_tools() call failed: %s", e)
    except Exception:
        # continue to fallbacks
        pass

    # 2) Look for common container attributes like tools, _tools, _registered_tools
    for attr in ("tools", "_tools", "_registered_tools", "_tool_registry"):
        if hasattr(mcp_instance, attr):
            try:
                container = getattr(mcp_instance, attr)
                if isinstance(container, dict):
                    names = list(container.keys())
                elif isinstance(container, (list, tuple)):
                    names = [getattr(t, "name", getattr(t, "__name__", str(t))) for t in container]
                else:
                    # try to extract .name attributes
                    try:
                        names = [getattr(container, "name")]
                    except Exception:
                        names = [str(container)]
                logger.info("Registered tools (via attribute %s): %s", attr, names)
                return
            except Exception as e:
                logger.debug("inspecting %s failed: %s", attr, e)

    # 3) Search for callables on the mcp object that look like tool wrappers
    detected = []
    for name in dir(mcp_instance):
        try:
            obj = getattr(mcp_instance, name)
            if callable(obj):
                # common decorator flags used by different implementations
                for flag in ("__mcp_tool__", "mcp_tool", "is_tool", "tool_name"):
                    if getattr(obj, flag, False):
                        detected.append(getattr(obj, "__name__", name))
                        break
        except Exception:
            continue
    if detected:
        logger.info("Registered tools (detected by decorator flags): %s", detected)
        return

    # 4) Last resort: inspect module-level functions defined above that were decorated
    #    (this looks at this module's globals for functions that have decorator flags)
    fallback = []
    current_globals = globals()
    for name, obj in current_globals.items():
        if callable(obj):
            for flag in ("__mcp_tool__", "mcp_tool", "is_tool", "tool_name"):
                if getattr(obj, flag, False):
                    fallback.append(name)
                    break
    if fallback:
        logger.info("Registered tools (module globals with decorator flags): %s", fallback)
        return

    # If nothing found
    logger.info("Could not automatically detect registered MCP tools via introspection. "
                "Call mcp.list_tools() at runtime or inspect mcp internals.")


# -------------------------
# Run the MCP server (log the tools before starting)
# -------------------------
if __name__ == "__main__":
    logger.info("🚀 Starting FastMCP server (stdio)...")
    # log registered tool names (best-effort, handles a few SDK variations)
    log_registered_tools(mcp)
    mcp.run()
