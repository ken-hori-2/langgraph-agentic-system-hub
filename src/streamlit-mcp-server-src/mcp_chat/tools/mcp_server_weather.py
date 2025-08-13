#!/usr/bin/env python3
"""
MCP Server for Weather Information
"""

import asyncio
import json
import os
import requests
from typing import Any, Dict, List
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    ListToolsRequest,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# OpenWeatherMap API設定
WEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
WEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

server = Server("weather-mcp")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """利用可能なツールのリストを返す"""
    return [
        Tool(
            name="get_weather",
            description="指定された都市の現在の天気情報を取得します",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "天気を取得したい都市名（例: Tokyo, New York, London）"
                    },
                    "country_code": {
                        "type": "string",
                        "description": "国コード（例: JP, US, GB）。オプションです。",
                        "default": ""
                    }
                },
                "required": ["city"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """ツールを実行する"""
    if name == "get_weather":
        return await get_weather_info(arguments)
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def get_weather_info(arguments: Dict[str, Any]) -> List[TextContent]:
    """天気情報を取得する"""
    try:
        city = arguments.get("city", "")
        country_code = arguments.get("country_code", "")
        
        if not city:
            return [TextContent(type="text", text="都市名が指定されていません。")]
        
        # APIキーが設定されていない場合の処理
        if not WEATHER_API_KEY:
            return [TextContent(
                type="text", 
                text=f"申し訳ございませんが、現在天気情報を取得できません。{city}の天気情報を取得するには、OpenWeatherMap APIキーが必要です。"
            )]
        
        # 都市名と国コードを組み合わせ
        location = city
        if country_code:
            location = f"{city},{country_code}"
        
        # OpenWeatherMap APIにリクエスト
        params = {
            "q": location,
            "appid": WEATHER_API_KEY,
            "units": "metric",  # 摂氏温度
            "lang": "ja"  # 日本語
        }
        
        response = requests.get(WEATHER_BASE_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            weather_data = response.json()
            
            # 天気情報を整形
            weather_info = format_weather_data(weather_data)
            return [TextContent(type="text", text=weather_info)]
        else:
            error_msg = f"天気情報の取得に失敗しました。ステータスコード: {response.status_code}"
            if response.status_code == 404:
                error_msg = f"都市 '{city}' が見つかりませんでした。正しい都市名を指定してください。"
            return [TextContent(type="text", text=error_msg)]
            
    except requests.exceptions.Timeout:
        return [TextContent(type="text", text="天気情報の取得がタイムアウトしました。しばらく時間をおいて再試行してください。")]
    except requests.exceptions.RequestException as e:
        return [TextContent(type="text", text=f"天気情報の取得中にエラーが発生しました: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"予期しないエラーが発生しました: {str(e)}")]

def format_weather_data(weather_data: Dict[str, Any]) -> str:
    """天気データを読みやすい形式に整形する"""
    try:
        city_name = weather_data.get("name", "不明")
        country = weather_data.get("sys", {}).get("country", "")
        temp = weather_data.get("main", {}).get("temp")
        feels_like = weather_data.get("main", {}).get("feels_like")
        humidity = weather_data.get("main", {}).get("humidity")
        pressure = weather_data.get("main", {}).get("pressure")
        description = weather_data.get("weather", [{}])[0].get("description", "不明")
        wind_speed = weather_data.get("wind", {}).get("speed")
        
        location = f"{city_name}"
        if country:
            location += f", {country}"
        
        weather_text = f"🌤️ {location}の現在の天気\n\n"
        weather_text += f"天気: {description}\n"
        if temp is not None:
            weather_text += f"気温: {temp}°C\n"
        if feels_like is not None:
            weather_text += f"体感温度: {feels_like}°C\n"
        if humidity is not None:
            weather_text += f"湿度: {humidity}%\n"
        if pressure is not None:
            weather_text += f"気圧: {pressure}hPa\n"
        if wind_speed is not None:
            weather_text += f"風速: {wind_speed}m/s\n"
        
        return weather_text
        
    except Exception as e:
        return f"天気データの整形中にエラーが発生しました: {str(e)}"

async def main():
    """メイン関数"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="weather-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main()) 