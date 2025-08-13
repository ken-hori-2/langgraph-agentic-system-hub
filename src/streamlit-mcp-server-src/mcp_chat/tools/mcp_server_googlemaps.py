from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv
import requests
from typing import Optional, Dict, Any
import json

# 環境変数の読み込み
load_dotenv()

# MCPサーバーの初期化
mcp = FastMCP(
    "GoogleMapsService",
    instructions="You are a Google Maps assistant that can provide route directions, place search, and geocoding services.",
    host="0.0.0.0",
    port=8006
)

# Google Maps APIキーの取得
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Google Maps API エンドポイント
GEOCODING_API_URL = "https://maps.googleapis.com/maps/api/geocode/json"
DIRECTIONS_API_URL = "https://maps.googleapis.com/maps/api/directions/json"
PLACES_API_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"

@mcp.tool()
async def get_route_directions(
    origin: str,
    destination: str,
    mode: str = "driving",
    avoid: Optional[str] = None
) -> str:
    """
    出発地から目的地までのルート検索を実行します。
    
    Args:
        origin: 出発地（住所または場所名）
        destination: 目的地（住所または場所名）
        mode: 移動手段（"driving", "walking", "bicycling", "transit"）
        avoid: 回避したい要素（"tolls", "highways", "ferries"）
    
    Returns:
        str: ルート情報を含む文字列
    """
    if not GOOGLE_MAPS_API_KEY:
        return "エラー: Google Maps APIキーが設定されていません。"
    
    try:
        params = {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "key": GOOGLE_MAPS_API_KEY
        }
        
        if avoid:
            params["avoid"] = avoid
        
        response = requests.get(DIRECTIONS_API_URL, params=params)
        data = response.json()
        
        if data["status"] != "OK":
            return f"ルート検索エラー: {data['status']}"
        
        route = data["routes"][0]
        leg = route["legs"][0]
        
        # ルート情報を整形
        result = []
        result.append(f"🚗 {origin} から {destination} へのルート")
        result.append(f"移動手段: {mode}")
        result.append(f"総距離: {leg['distance']['text']}")
        result.append(f"予想時間: {leg['duration']['text']}")
        
        result.append("\n📋 経路:")
        for i, step in enumerate(leg["steps"], 1):
            result.append(f"{i}. {step['html_instructions'].replace('<b>', '').replace('</b>', '')}")
            if step.get('distance'):
                result.append(f"   ({step['distance']['text']})")
        
        return "\n".join(result)
        
    except Exception as e:
        return f"ルート検索中にエラーが発生しました: {str(e)}"

@mcp.tool()
async def search_places(
    query: str,
    location: Optional[str] = None,
    radius: int = 5000
) -> str:
    """
    場所検索を実行します。
    
    Args:
        query: 検索クエリ（例: "レストラン", "ガソリンスタンド"）
        location: 検索の中心となる場所（住所または座標）
        radius: 検索半径（メートル）
    
    Returns:
        str: 検索結果を含む文字列
    """
    if not GOOGLE_MAPS_API_KEY:
        return "エラー: Google Maps APIキーが設定されていません。"
    
    try:
        params = {
            "query": query,
            "key": GOOGLE_MAPS_API_KEY
        }
        
        if location:
            # 場所が指定されている場合、ジオコーディングで座標を取得
            geocode_params = {
                "address": location,
                "key": GOOGLE_MAPS_API_KEY
            }
            geocode_response = requests.get(GEOCODING_API_URL, params=geocode_params)
            geocode_data = geocode_response.json()
            
            if geocode_data["status"] == "OK":
                location_coords = geocode_data["results"][0]["geometry"]["location"]
                params["location"] = f"{location_coords['lat']},{location_coords['lng']}"
                params["radius"] = radius
        
        response = requests.get(PLACES_API_URL, params=params)
        data = response.json()
        
        if data["status"] != "OK":
            return f"場所検索エラー: {data['status']}"
        
        # 検索結果を整形
        result = []
        result.append(f"🔍 '{query}' の検索結果")
        if location:
            result.append(f"検索場所: {location} (半径{radius}m)")
        
        for i, place in enumerate(data["results"][:10], 1):  # 上位10件を表示
            result.append(f"\n{i}. {place['name']}")
            result.append(f"   住所: {place.get('formatted_address', 'N/A')}")
            result.append(f"   評価: {place.get('rating', 'N/A')}⭐")
            if place.get('opening_hours'):
                result.append(f"   営業状況: {'営業中' if place['opening_hours']['open_now'] else '営業時間外'}")
        
        return "\n".join(result)
        
    except Exception as e:
        return f"場所検索中にエラーが発生しました: {str(e)}"

@mcp.tool()
async def geocode_address(address: str) -> str:
    """
    住所を座標に変換します（ジオコーディング）。
    
    Args:
        address: 住所
    
    Returns:
        str: 座標情報を含む文字列
    """
    if not GOOGLE_MAPS_API_KEY:
        return "エラー: Google Maps APIキーが設定されていません。"
    
    try:
        params = {
            "address": address,
            "key": GOOGLE_MAPS_API_KEY
        }
        
        response = requests.get(GEOCODING_API_URL, params=params)
        data = response.json()
        
        if data["status"] != "OK":
            return f"ジオコーディングエラー: {data['status']}"
        
        result = data["results"][0]
        location = result["geometry"]["location"]
        
        # 結果を整形
        output = []
        output.append(f"📍 住所: {address}")
        output.append(f"座標: {location['lat']}, {location['lng']}")
        output.append(f"フォーマット済み住所: {result['formatted_address']}")
        
        # 住所コンポーネントの詳細情報
        if result.get("address_components"):
            output.append("\n住所詳細:")
            for component in result["address_components"]:
                types = ", ".join(component["types"])
                output.append(f"  {component['long_name']} ({types})")
        
        return "\n".join(output)
        
    except Exception as e:
        return f"ジオコーディング中にエラーが発生しました: {str(e)}"

@mcp.tool()
async def reverse_geocode(lat: float, lng: float) -> str:
    """
    座標を住所に変換します（逆ジオコーディング）。
    
    Args:
        lat: 緯度
        lng: 経度
    
    Returns:
        str: 住所情報を含む文字列
    """
    if not GOOGLE_MAPS_API_KEY:
        return "エラー: Google Maps APIキーが設定されていません。"
    
    try:
        params = {
            "latlng": f"{lat},{lng}",
            "key": GOOGLE_MAPS_API_KEY
        }
        
        response = requests.get(GEOCODING_API_URL, params=params)
        data = response.json()
        
        if data["status"] != "OK":
            return f"逆ジオコーディングエラー: {data['status']}"
        
        result = data["results"][0]
        
        # 結果を整形
        output = []
        output.append(f"📍 座標: {lat}, {lng}")
        output.append(f"住所: {result['formatted_address']}")
        
        # 住所コンポーネントの詳細情報
        if result.get("address_components"):
            output.append("\n住所詳細:")
            for component in result["address_components"]:
                types = ", ".join(component["types"])
                output.append(f"  {component['long_name']} ({types})")
        
        return "\n".join(output)
        
    except Exception as e:
        return f"逆ジオコーディング中にエラーが発生しました: {str(e)}"

if __name__ == "__main__":
    # stdio transportでMCPサーバーを起動
    mcp.run(transport="stdio") 