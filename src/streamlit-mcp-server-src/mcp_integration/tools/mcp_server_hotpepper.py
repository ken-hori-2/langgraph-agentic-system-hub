from mcp.server.fastmcp import FastMCP
import os
import requests
from dotenv import load_dotenv
import json

# 環境変数の読み込み
load_dotenv()

# MCPサーバーの初期化
mcp = FastMCP("HotPepperSearch")

@mcp.tool()
async def search_restaurants(location: str, cuisine: str = "", budget: str = "", count: int = 20) -> str:
    """HotPepperでレストランを検索します。
    
    Args:
        location: エリア名（例: 渋谷, 新宿, 大崎）
        cuisine: ジャンル（例: 居酒屋, イタリアン, 中華）
        budget: 予算（例: 3000円以下）
        count: 取得するレストラン数（デフォルト: 20）
    """
    try:
        api_key = os.getenv("HOTPEPPER_API_KEY")
        if not api_key:
            return "エラー: HotPepper API key not configured. Please set HOTPEPPER_API_KEY in your .env file."
        
        # Build search parameters
        params = {
            'key': api_key,
            'format': 'json',
            'count': count
        }
        
        if location:
            params['address'] = location
        if cuisine:
            params['genre'] = cuisine
        if budget:
            params['budget'] = budget
        
        response = requests.get('https://webservice.recruit.co.jp/hotpepper/gourmet/v1/', params=params)
        
        if response.status_code != 200:
            return "エラー: Failed to search HotPepper API"
        
        data = response.json()
        shops = data.get('results', {}).get('shop', [])
        
        restaurants = []
        for shop in shops:
            restaurant_info = {
                'name': shop['name'],
                'address': shop['address'],
                'cuisine': shop['genre']['name'],
                'budget': shop['budget']['name'],
                'rating': shop.get('rating', '評価なし'),
                'url': shop['urls']['pc'],
                'phone': shop.get('tel', '電話番号なし'),
                'hours': shop.get('open', '営業時間不明'),
                'access': shop.get('access', 'アクセス情報なし')
            }
            restaurants.append(restaurant_info)
        
        return json.dumps({
            "message": f"{len(restaurants)}件のレストランが見つかりました",
            "restaurants": restaurants
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return f"エラー: HotPepper search error: {str(e)}"

@mcp.tool()
async def search_by_name(restaurant_name: str, count: int = 10) -> str:
    """レストラン名で検索します。
    
    Args:
        restaurant_name: レストラン名
        count: 取得するレストラン数（デフォルト: 10）
    """
    try:
        api_key = os.getenv("HOTPEPPER_API_KEY")
        if not api_key:
            return "エラー: HotPepper API key not configured."
        
        # Build search parameters
        params = {
            'key': api_key,
            'format': 'json',
            'count': count,
            'name': restaurant_name
        }
        
        response = requests.get('https://webservice.recruit.co.jp/hotpepper/gourmet/v1/', params=params)
        
        if response.status_code != 200:
            return "エラー: Failed to search HotPepper API"
        
        data = response.json()
        shops = data.get('results', {}).get('shop', [])
        
        restaurants = []
        for shop in shops:
            restaurant_info = {
                'name': shop['name'],
                'address': shop['address'],
                'cuisine': shop['genre']['name'],
                'budget': shop['budget']['name'],
                'rating': shop.get('rating', '評価なし'),
                'url': shop['urls']['pc'],
                'phone': shop.get('tel', '電話番号なし'),
                'hours': shop.get('open', '営業時間不明'),
                'access': shop.get('access', 'アクセス情報なし')
            }
            restaurants.append(restaurant_info)
        
        return json.dumps({
            "message": f"{len(restaurants)}件のレストランが見つかりました",
            "restaurants": restaurants
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return f"エラー: HotPepper name search error: {str(e)}"

@mcp.tool()
async def get_master_data(master_type: str = "genre") -> str:
    """HotPepperのマスターデータを取得します。
    
    Args:
        master_type: マスターデータの種類（"genre", "large_area", "middle_area", "budget"）
    """
    try:
        api_key = os.getenv("HOTPEPPER_API_KEY")
        if not api_key:
            return "エラー: HotPepper API key not configured."
        
        # Build search parameters
        params = {
            'key': api_key,
            'format': 'json'
        }
        
        if master_type == "genre":
            url = 'https://webservice.recruit.co.jp/hotpepper/genre/v1/'
        elif master_type == "large_area":
            url = 'https://webservice.recruit.co.jp/hotpepper/large_area/v1/'
        elif master_type == "middle_area":
            url = 'https://webservice.recruit.co.jp/hotpepper/middle_area/v1/'
        elif master_type == "budget":
            url = 'https://webservice.recruit.co.jp/hotpepper/budget/v1/'
        else:
            return "エラー: Invalid master_type. Use 'genre', 'large_area', 'middle_area', or 'budget'."
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            return "エラー: Failed to get master data from HotPepper API"
        
        data = response.json()
        
        # マスターデータの種類に応じて結果を整形
        if master_type == "genre":
            items = data.get('results', {}).get('genre', [])
            result_data = [{'code': item['code'], 'name': item['name']} for item in items]
        elif master_type == "large_area":
            items = data.get('results', {}).get('large_area', [])
            result_data = [{'code': item['code'], 'name': item['name']} for item in items]
        elif master_type == "middle_area":
            items = data.get('results', {}).get('middle_area', [])
            result_data = [{'code': item['code'], 'name': item['name'], 'large_area': item['large_area']} for item in items]
        elif master_type == "budget":
            items = data.get('results', {}).get('budget', [])
            result_data = [{'code': item['code'], 'name': item['name']} for item in items]
        
        return json.dumps({
            "message": f"{master_type}マスターデータを取得しました",
            "data": result_data
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return f"エラー: HotPepper master data error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio") 