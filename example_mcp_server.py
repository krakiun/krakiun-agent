#!/usr/bin/env python3
"""
Example MCP Server for Krakiun Agent
===============================
A simple MCP server that provides utility tools via stdio transport.

Usage in Krakiun Agent Settings > MCP Tools > Custom MCP Servers:
  - Transport: Local (stdio)
  - Command: python3
  - Args: /path/to/example_mcp_server.py

Requirements:
  pip install nothing (zero dependencies - uses only stdlib!)

Tools provided:
  - get_datetime: Get current date and time
  - calculator: Evaluate math expressions
  - generate_uuid: Generate a UUID
  - system_info: Get system information
  - list_files: List files in a directory with details
"""

import json
import sys
import os
import uuid
import math
import platform
import datetime


def send_response(response):
    """Send a JSON-RPC response to stdout."""
    line = json.dumps(response) + "\n"
    sys.stdout.write(line)
    sys.stdout.flush()


def handle_initialize(msg_id, params):
    """Handle the initialize request."""
    send_response({
        "jsonrpc": "2.0",
        "id": msg_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "Krakiun Agent Example MCP Server",
                "version": "1.0.0"
            }
        }
    })


def handle_tools_list(msg_id):
    """Handle tools/list request."""
    send_response({
        "jsonrpc": "2.0",
        "id": msg_id,
        "result": {
            "tools": [
                {
                    "name": "get_datetime",
                    "description": "Get current date and time in various formats",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "format": {
                                "type": "string",
                                "description": "Output format: 'iso', 'human', 'unix', or a custom strftime format (default: 'human')"
                            },
                            "timezone_offset": {
                                "type": "number",
                                "description": "UTC offset in hours (e.g. 2 for UTC+2, -5 for UTC-5). Default: local time"
                            }
                        }
                    }
                },
                {
                    "name": "calculator",
                    "description": "Evaluate a mathematical expression safely. Supports: +, -, *, /, **, sqrt, sin, cos, tan, log, pi, e",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "Math expression to evaluate (e.g. '2 + 2', 'sqrt(16)', 'sin(pi/2)')"
                            }
                        },
                        "required": ["expression"]
                    }
                },
                {
                    "name": "generate_uuid",
                    "description": "Generate one or more UUIDs (v4)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "count": {
                                "type": "number",
                                "description": "Number of UUIDs to generate (default: 1, max: 20)"
                            }
                        }
                    }
                },
                {
                    "name": "system_info",
                    "description": "Get information about the current system (OS, Python version, CPU, etc.)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "list_files",
                    "description": "List files and directories in a given path with size and modification date",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Directory path to list (default: current directory)"
                            },
                            "show_hidden": {
                                "type": "boolean",
                                "description": "Include hidden files (starting with dot). Default: false"
                            }
                        }
                    }
                }
            ]
        }
    })


def tool_get_datetime(args):
    fmt = args.get("format", "human")
    offset = args.get("timezone_offset")

    now = datetime.datetime.now()
    if offset is not None:
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=offset)

    if fmt == "iso":
        return now.isoformat()
    elif fmt == "unix":
        return str(int(now.timestamp()))
    elif fmt == "human":
        return now.strftime("%A, %B %d, %Y at %H:%M:%S")
    else:
        return now.strftime(fmt)


def tool_calculator(args):
    expression = args.get("expression", "")
    if not expression:
        return "Error: No expression provided"

    # Safe math environment
    safe_env = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log2": math.log2,
        "log10": math.log10,
        "abs": abs,
        "round": round,
        "pi": math.pi,
        "e": math.e,
        "inf": math.inf,
        "pow": pow,
        "min": min,
        "max": max,
    }

    try:
        result = eval(expression, {"__builtins__": {}}, safe_env)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error evaluating '{expression}': {e}"


def tool_generate_uuid(args):
    count = min(int(args.get("count", 1)), 20)
    uuids = [str(uuid.uuid4()) for _ in range(count)]
    return "\n".join(uuids)


def tool_system_info(args):
    info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "hostname": platform.node(),
        "user": os.environ.get("USER", os.environ.get("USERNAME", "unknown")),
        "cwd": os.getcwd(),
        "home": os.path.expanduser("~"),
    }
    return "\n".join(f"{k}: {v}" for k, v in info.items())


def tool_list_files(args):
    path = args.get("path", ".")
    show_hidden = args.get("show_hidden", False)

    if not os.path.isdir(path):
        return f"Error: '{path}' is not a directory"

    entries = []
    try:
        for name in sorted(os.listdir(path)):
            if not show_hidden and name.startswith("."):
                continue
            full_path = os.path.join(path, name)
            try:
                stat = os.stat(full_path)
                is_dir = os.path.isdir(full_path)
                size = stat.st_size
                modified = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")

                if is_dir:
                    entries.append(f"  [DIR]  {name}/  ({modified})")
                else:
                    size_str = format_size(size)
                    entries.append(f"  [FILE] {name}  ({size_str}, {modified})")
            except OSError:
                entries.append(f"  [?]    {name}  (permission denied)")
    except PermissionError:
        return f"Error: Permission denied for '{path}'"

    header = f"Contents of {os.path.abspath(path)} ({len(entries)} items):"
    return header + "\n" + "\n".join(entries) if entries else header + "\n  (empty)"


def format_size(size):
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}" if unit != "B" else f"{size} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def handle_tools_call(msg_id, params):
    """Handle tools/call request."""
    tool_name = params.get("name", "")
    arguments = params.get("arguments", {})

    tool_handlers = {
        "get_datetime": tool_get_datetime,
        "calculator": tool_calculator,
        "generate_uuid": tool_generate_uuid,
        "system_info": tool_system_info,
        "list_files": tool_list_files,
    }

    handler = tool_handlers.get(tool_name)
    if handler:
        try:
            result = handler(arguments)
            send_response({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": str(result)}]
                }
            })
        except Exception as e:
            send_response({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": f"Error: {e}"}],
                    "isError": True
                }
            })
    else:
        send_response({
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": -32601,
                "message": f"Unknown tool: {tool_name}"
            }
        })


def main():
    """Main loop: read JSON-RPC from stdin, dispatch, respond on stdout."""
    # Log to stderr (not stdout, which is for protocol)
    sys.stderr.write("[MCP Server] Starting Krakiun Agent Example MCP Server...\n")
    sys.stderr.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            msg = json.loads(line)
        except json.JSONDecodeError as e:
            sys.stderr.write(f"[MCP Server] Invalid JSON: {e}\n")
            sys.stderr.flush()
            continue

        method = msg.get("method", "")
        msg_id = msg.get("id")
        params = msg.get("params", {})

        if method == "initialize":
            handle_initialize(msg_id, params)
        elif method == "notifications/initialized":
            # Notification, no response needed
            sys.stderr.write("[MCP Server] Initialized successfully\n")
            sys.stderr.flush()
        elif method == "tools/list":
            handle_tools_list(msg_id)
        elif method == "tools/call":
            handle_tools_call(msg_id, params)
        elif method == "ping":
            send_response({"jsonrpc": "2.0", "id": msg_id, "result": {}})
        else:
            if msg_id is not None:
                send_response({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                })


if __name__ == "__main__":
    main()
