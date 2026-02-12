#!/usr/bin/env python3
"""
MCP Client — Call tools on MCP servers via Streamable HTTP transport.

Supports the Cloudflare Workers MCP protocol:
1. POST /mcp with initialize → get session ID
2. POST /mcp with tools/list or tools/call → use session ID
3. Parse SSE (text/event-stream) responses

Usage:
    python3 mcp_call.py --list-servers
    python3 mcp_call.py --server keothom --list-tools
    python3 mcp_call.py --server keothom --tool platform_overview
    python3 mcp_call.py --server keothom --tool search_user --params '{"query": "demo"}'
"""

import os
import sys
import json
import argparse
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

SCRIPT_DIR = Path(__file__).resolve().parent
SERVERS_FILE = SCRIPT_DIR.parent / "servers.json"
DEFAULT_TIMEOUT = 30
MCP_PROTOCOL_VERSION = "2024-11-05"


def load_servers() -> dict:
    if not SERVERS_FILE.exists():
        print(f"ERROR: Server config not found: {SERVERS_FILE}")
        sys.exit(1)
    with open(SERVERS_FILE) as f:
        return json.load(f)


def get_auth_header(server_config: dict) -> dict:
    auth_env = server_config.get("auth_env", "")
    if not auth_env:
        return {}
    token = os.environ.get(auth_env, "")
    if not token:
        print(f"WARNING: '{auth_env}' not set.")
        return {}
    auth_type = server_config.get("auth_type", "bearer")
    if auth_type == "bearer":
        return {"Authorization": f"Bearer {token}"}
    elif auth_type == "header":
        return {server_config.get("auth_header_name", "X-API-Key"): token}
    return {"Authorization": f"Bearer {token}"}


def parse_sse(body: str) -> dict:
    """Parse SSE text/event-stream body → extract JSON-RPC result."""
    for line in body.split("\n"):
        line = line.strip()
        if line.startswith("data:"):
            data_str = line[5:].strip()
            if data_str:
                try:
                    parsed = json.loads(data_str)
                    if isinstance(parsed, dict):
                        if "error" in parsed:
                            err = parsed["error"]
                            code = err.get("code", "?")
                            msg = err.get("message", str(err))
                            print(f"MCP error {code}: {msg}", file=sys.stderr)
                            sys.exit(1)
                        if "result" in parsed:
                            return parsed["result"]
                        return parsed
                except json.JSONDecodeError:
                    pass
    return {"raw": body}


def mcp_post(url: str, payload: dict, headers: dict, timeout: int) -> tuple:
    """POST to MCP endpoint. Returns (result_dict, response_headers_dict)."""
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers=headers, method="POST")

    try:
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            resp_headers = {k.lower(): v for k, v in resp.headers.items()}
            content_type = resp_headers.get("content-type", "")

            if "text/event-stream" in content_type:
                result = parse_sse(body)
            else:
                result = json.loads(body)
                if isinstance(result, dict) and "result" in result:
                    result = result["result"]

            return result, resp_headers
    except HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")[:500]
        print(f"ERROR: HTTP {e.code}: {error_body}")
        sys.exit(1)
    except URLError as e:
        print(f"ERROR: Connection failed: {e}")
        sys.exit(1)


def mcp_initialize(server_config: dict, timeout: int = DEFAULT_TIMEOUT) -> str:
    """Initialize MCP session. Returns session ID."""
    url = server_config["url"].rstrip("/") + "/mcp"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "User-Agent": "OpenClaw-MCP-Client/1.0",
        **get_auth_header(server_config),
    }
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "openclaw-mcp-client", "version": "1.0"},
        },
    }

    result, resp_headers = mcp_post(url, payload, headers, timeout)
    session_id = resp_headers.get("mcp-session-id", "")

    if not session_id:
        print("WARNING: No mcp-session-id in response. Some features may not work.")

    return session_id


def mcp_call(server_config: dict, method: str, params: dict = None,
             session_id: str = None, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """Call an MCP method with session."""
    url = server_config["url"].rstrip("/") + "/mcp"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "User-Agent": "OpenClaw-MCP-Client/1.0",
        **get_auth_header(server_config),
    }
    if session_id:
        headers["mcp-session-id"] = session_id

    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": method,
    }
    if params:
        payload["params"] = params

    result, _ = mcp_post(url, payload, headers, timeout)
    return result


# ── Commands ──

def cmd_list_servers(servers: dict):
    print("📡 Available MCP Servers:\n")
    for key, srv in servers.items():
        auth_env = srv.get("auth_env", "N/A")
        auth_set = "✅" if os.environ.get(auth_env) else "❌ not set"
        print(f"  {key}")
        print(f"    Name: {srv['name']}")
        print(f"    URL:  {srv['url']}")
        print(f"    Auth: {auth_env} ({auth_set})")
        print(f"    Desc: {srv.get('description', '')}")
        print()


def cmd_list_tools(server_config: dict, timeout: int):
    session_id = mcp_initialize(server_config, timeout)
    result = mcp_call(server_config, "tools/list", session_id=session_id, timeout=timeout)

    tools = result.get("tools", result) if isinstance(result, dict) else result
    if isinstance(tools, list):
        print(f"🔧 Available tools ({len(tools)}):\n")
        for tool in tools:
            name = tool.get("name", "?")
            desc = tool.get("description", "")
            schema = tool.get("inputSchema", {})
            params = schema.get("properties", {})
            required = schema.get("required", [])
            print(f"  {name}")
            if desc:
                # Truncate long descriptions
                short = desc[:100] + "..." if len(desc) > 100 else desc
                print(f"    {short}")
            if params:
                param_strs = []
                for p, info in params.items():
                    req = "*" if p in required else ""
                    ptype = info.get("type", "")
                    param_strs.append(f"{p}{req}({ptype})")
                print(f"    Params: {', '.join(param_strs)}")
            print()
    else:
        print(json.dumps(tools, indent=2, ensure_ascii=False))


def cmd_call_tool(server_config: dict, tool_name: str, params: dict = None, timeout: int = DEFAULT_TIMEOUT):
    session_id = mcp_initialize(server_config, timeout)

    call_params = {"name": tool_name, "arguments": params or {}}

    result = mcp_call(server_config, "tools/call", call_params, session_id=session_id, timeout=timeout)

    # Format output
    if isinstance(result, dict):
        content = result.get("content", result)
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text = item["text"]
                    try:
                        parsed = json.loads(text)
                        print(json.dumps(parsed, indent=2, ensure_ascii=False))
                    except (json.JSONDecodeError, TypeError):
                        print(text)
                else:
                    print(json.dumps(item, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(content, indent=2, ensure_ascii=False))
    elif isinstance(result, str):
        print(result)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="MCP Client — Call tools on MCP servers")
    parser.add_argument("--server", "-s", help="Server key from servers.json")
    parser.add_argument("--tool", "-t", help="Tool name to call")
    parser.add_argument("--params", "-p", help="Tool parameters as JSON string")
    parser.add_argument("--list-servers", action="store_true", help="List configured servers")
    parser.add_argument("--list-tools", action="store_true", help="List tools on a server")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Timeout (seconds)")
    args = parser.parse_args()

    servers = load_servers()

    if args.list_servers:
        cmd_list_servers(servers)
        return

    if not args.server:
        print("ERROR: --server required. Use --list-servers to see options.")
        sys.exit(1)

    if args.server not in servers:
        print(f"ERROR: Unknown server '{args.server}'. Available: {', '.join(servers.keys())}")
        sys.exit(1)

    srv = servers[args.server]

    if args.list_tools:
        cmd_list_tools(srv, args.timeout)
        return

    if not args.tool:
        print("ERROR: --tool required. Use --list-tools to see options.")
        sys.exit(1)

    params = None
    if args.params:
        try:
            params = json.loads(args.params)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON: {e}")
            sys.exit(1)

    cmd_call_tool(srv, args.tool, params, timeout=args.timeout)


if __name__ == "__main__":
    main()
