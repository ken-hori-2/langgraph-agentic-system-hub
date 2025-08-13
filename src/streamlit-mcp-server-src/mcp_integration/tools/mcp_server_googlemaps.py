from mcp.server.fastmcp import FastMCP
import os
import requests
from urllib.parse import quote
from dotenv import load_dotenv
import json

# 環境変数の読み込み
load_dotenv()

# MCPサーバーの初期化
mcp = FastMCP("GoogleMapsSearch")

@mcp.tool()
async def search_restaurants(location: str, cuisine: str = "", radius: int = 1000, count: int = 20) -> str:
    """Google Mapsでレストランを検索します。
    
    Args:
        location: エリア名（例: 渋谷, 新宿, 大崎）
        cuisine: ジャンル（例: イタリアン, 中華, 居酒屋）
        radius: 検索半径（メートル、デフォルト: 1000）
        count: 取得するレストラン数（デフォルト: 20）
    """
    try:
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not api_key:
            return "エラー: Google Maps API key not configured. Please set GOOGLE_MAPS_API_KEY in your .env file."
        
        # Build search query
        query = f"restaurants in {location}"
        if cuisine:
            query += f" {cuisine}"
        
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            'query': query,
            'key': api_key,
            'radius': radius,
            'type': 'restaurant',
            'maxwidth': count
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            return "エラー: Failed to search Google Maps API"
        
        data = response.json()
        places = data.get('results', [])
        
        restaurants = []
        for place in places:
            restaurant_info = {
                'name': place['name'],
                'address': place.get('formatted_address', '住所不明'),
                'rating': place.get('rating', '評価なし'),
                'price_level': place.get('price_level', '価格不明'),
                'google_maps_url': f"https://www.google.com/maps/place/?q=place_id:{place['place_id']}",
                'place_id': place['place_id'],
                'types': place.get('types', []),
                'user_ratings_total': place.get('user_ratings_total', 0)
            }
            restaurants.append(restaurant_info)
        
        return json.dumps({
            "message": f"{len(restaurants)}件のレストランが見つかりました",
            "restaurants": restaurants
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return f"エラー: Google Maps search error: {str(e)}"

@mcp.tool()
async def get_place_details(place_id: str) -> str:
    """Google Mapsで場所の詳細情報を取得します。
    
    Args:
        place_id: 場所のID
    """
    try:
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not api_key:
            return "エラー: Google Maps API key not configured."
        
        url = f"https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            'place_id': place_id,
            'key': api_key,
            'fields': 'name,formatted_address,formatted_phone_number,opening_hours,rating,user_ratings_total,price_level,website,url,reviews'
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            return "エラー: Failed to get place details from Google Maps API"
        
        data = response.json()
        place = data.get('result', {})
        
        place_details = {
            'name': place.get('name', ''),
            'address': place.get('formatted_address', ''),
            'phone': place.get('formatted_phone_number', ''),
            'rating': place.get('rating', '評価なし'),
            'user_ratings_total': place.get('user_ratings_total', 0),
            'price_level': place.get('price_level', '価格不明'),
            'website': place.get('website', ''),
            'google_maps_url': place.get('url', ''),
            'opening_hours': place.get('opening_hours', {}).get('weekday_text', []),
            'reviews': place.get('reviews', [])[:3]  # 最新3件のレビュー
        }
        
        return json.dumps({
            "message": "場所の詳細情報を取得しました",
            "place_details": place_details
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return f"エラー: Google Maps place details error: {str(e)}"

@mcp.tool()
async def search_nearby_places(location: str, place_type: str = "restaurant", radius: int = 1000) -> str:
    """指定した場所の近くの場所を検索します。
    
    Args:
        location: 場所（住所または座標）
        place_type: 場所の種類（例: restaurant, cafe, bar）
        radius: 検索半径（メートル、デフォルト: 1000）
    """
    try:
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not api_key:
            return "エラー: Google Maps API key not configured."
        
        # まず場所の座標を取得
        geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        geocode_params = {
            'address': location,
            'key': api_key
        }
        
        geocode_response = requests.get(geocode_url, params=geocode_params)
        
        if geocode_response.status_code != 200:
            return "エラー: Failed to geocode location"
        
        geocode_data = geocode_response.json()
        if not geocode_data.get('results'):
            return "エラー: Location not found"
        
        location_coords = geocode_data['results'][0]['geometry']['location']
        lat = location_coords['lat']
        lng = location_coords['lng']
        
        # 近くの場所を検索
        nearby_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        nearby_params = {
            'location': f"{lat},{lng}",
            'radius': radius,
            'type': place_type,
            'key': api_key
        }
        
        nearby_response = requests.get(nearby_url, params=nearby_params)
        
        if nearby_response.status_code != 200:
            return "エラー: Failed to search nearby places"
        
        nearby_data = nearby_response.json()
        places = nearby_data.get('results', [])
        
        results = []
        for place in places:
            place_info = {
                'name': place['name'],
                'address': place.get('vicinity', '住所不明'),
                'rating': place.get('rating', '評価なし'),
                'price_level': place.get('price_level', '価格不明'),
                'google_maps_url': f"https://www.google.com/maps/place/?q=place_id:{place['place_id']}",
                'place_id': place['place_id'],
                'types': place.get('types', [])
            }
            results.append(place_info)
        
        return json.dumps({
            "message": f"{len(results)}件の{place_type}が見つかりました",
            "places": results
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return f"エラー: Google Maps nearby search error: {str(e)}"

@mcp.tool()
async def get_directions(origin: str, destination: str, mode: str = "driving") -> str:
    """2つの場所間の経路を取得します。
    
    Args:
        origin: 出発地
        destination: 目的地
        mode: 移動手段（driving, walking, bicycling, transit）
    """
    try:
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not api_key:
            return "エラー: Google Maps API key not configured."
        
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            'origin': origin,
            'destination': destination,
            'mode': mode,
            'key': api_key
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            return "エラー: Failed to get directions from Google Maps API"
        
        data = response.json()
        
        if not data.get('routes'):
            return "エラー: No route found"
        
        route = data['routes'][0]
        leg = route['legs'][0]
        
        directions_info = {
            'origin': leg['start_address'],
            'destination': leg['end_address'],
            'distance': leg['distance']['text'],
            'duration': leg['duration']['text'],
            'steps': [step['html_instructions'] for step in leg['steps'][:5]],  # 最初の5ステップ
            'google_maps_url': f"https://www.google.com/maps/dir/?api=1&origin={quote(origin)}&destination={quote(destination)}&travelmode={mode}"
        }
        
        return json.dumps({
            "message": "経路情報を取得しました",
            "directions": directions_info
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return f"エラー: Google Maps directions error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio") 