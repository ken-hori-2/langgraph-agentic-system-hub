#!/usr/bin/env python3
"""
MCP Server for getting current time
"""

import asyncio
import json
import sys
from datetime import datetime
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
)

# Create server instance
server = Server("time-server")

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available tools."""
    return ListToolsResult(
        tools=[
            Tool(
                name="get_current_time",
                description="Get the current date and time",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            )
        ]
    )

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> CallToolResult:
    """Handle tool calls."""
    if name == "get_current_time":
        current_time = datetime.now()
        return CallToolResult(
            content=[
                {
                    "type": "text",
                    "text": json.dumps({
                        "current_time": current_time.isoformat(),
                        "formatted_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "timezone": "JST"
                    }, ensure_ascii=False)
                }
            ]
        )
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Main function."""
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="time-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main()) 