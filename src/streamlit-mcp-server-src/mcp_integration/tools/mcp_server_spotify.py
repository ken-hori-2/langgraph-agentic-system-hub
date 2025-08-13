from mcp.server.fastmcp import FastMCP
import os
import requests
from urllib.parse import quote
from dotenv import load_dotenv
import json

# 環境変数の読み込み
load_dotenv()

# MCPサーバーの初期化
mcp = FastMCP("SpotifySearch")

@mcp.tool()
async def search_tracks(query: str, limit: int = 10) -> str:
    """Spotifyで楽曲を検索します。
    
    Args:
        query: 検索クエリ（楽曲名またはアーティスト名）
        limit: 取得する楽曲数（デフォルト: 10）
    """
    try:
        client_id = os.getenv("SPOTIFY_USER_ID")
        client_secret = os.getenv("SPOTIFY_TOKEN")
        
        if not client_id or not client_secret:
            return "エラー: Spotify API credentials not configured. Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your .env file."
        
        # Get access token
        auth_response = requests.post('https://accounts.spotify.com/api/token', {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
        })
        
        if auth_response.status_code != 200:
            return "エラー: Failed to authenticate with Spotify API"
        
        access_token = auth_response.json()['access_token']
        
        # Search for tracks
        headers = {'Authorization': f'Bearer {access_token}'}
        search_response = requests.get(
            f'https://api.spotify.com/v1/search?q={quote(query)}&type=track&limit={limit}',
            headers=headers
        )
        
        if search_response.status_code != 200:
            return "エラー: Failed to search Spotify API"
        
        tracks_data = search_response.json()['tracks']['items']
        results = []
        
        for i, track in enumerate(tracks_data, 1):
            track_info = {
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'album': track['album']['name'],
                'release_date': track['album']['release_date'],
                'spotify_url': track['external_urls']['spotify'],
                'album_art': track['album']['images'][0]['url'] if track['album']['images'] else None
            }
            results.append(track_info)
        
        # 結果をJSON形式で返す
        return json.dumps({
            "message": f"{len(results)}件の楽曲が見つかりました",
            "results": results
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return f"エラー: Spotify search error: {str(e)}"

@mcp.tool()
async def search_artists(artist_name: str, limit: int = 5) -> str:
    """Spotifyでアーティストを検索します。
    
    Args:
        artist_name: アーティスト名
        limit: 取得するアーティスト数（デフォルト: 5）
    """
    try:
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            return "エラー: Spotify API credentials not configured."
        
        # Get access token
        auth_response = requests.post('https://accounts.spotify.com/api/token', {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
        })
        
        if auth_response.status_code != 200:
            return "エラー: Failed to authenticate with Spotify API"
        
        access_token = auth_response.json()['access_token']
        
        # Search for artists
        headers = {'Authorization': f'Bearer {access_token}'}
        search_response = requests.get(
            f'https://api.spotify.com/v1/search?q={quote(artist_name)}&type=artist&limit={limit}',
            headers=headers
        )
        
        if search_response.status_code != 200:
            return "エラー: Failed to search Spotify API"
        
        artists_data = search_response.json()['artists']['items']
        results = []
        
        for artist in artists_data:
            artist_info = {
                'name': artist['name'],
                'spotify_url': artist['external_urls']['spotify'],
                'followers': artist['followers']['total'],
                'genres': artist['genres'],
                'image': artist['images'][0]['url'] if artist['images'] else None
            }
            results.append(artist_info)
        
        return json.dumps({
            "message": f"{len(results)}件のアーティストが見つかりました",
            "results": results
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return f"エラー: Spotify artist search error: {str(e)}"

@mcp.tool()
async def get_playlist(playlist_id: str) -> str:
    """Spotifyプレイリストの情報を取得します。
    
    Args:
        playlist_id: プレイリストID
    """
    try:
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            return "エラー: Spotify API credentials not configured."
        
        # Get access token
        auth_response = requests.post('https://accounts.spotify.com/api/token', {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
        })
        
        if auth_response.status_code != 200:
            return "エラー: Failed to authenticate with Spotify API"
        
        access_token = auth_response.json()['access_token']
        
        # Get playlist
        headers = {'Authorization': f'Bearer {access_token}'}
        playlist_response = requests.get(
            f'https://api.spotify.com/v1/playlists/{playlist_id}',
            headers=headers
        )
        
        if playlist_response.status_code != 200:
            return "エラー: Failed to get playlist from Spotify API"
        
        playlist_data = playlist_response.json()
        
        playlist_info = {
            'name': playlist_data['name'],
            'description': playlist_data.get('description', ''),
            'spotify_url': playlist_data['external_urls']['spotify'],
            'image': playlist_data['images'][0]['url'] if playlist_data['images'] else None,
            'tracks_count': playlist_data['tracks']['total'],
            'owner': playlist_data['owner']['display_name']
        }
        
        return json.dumps({
            "message": "プレイリスト情報を取得しました",
            "playlist": playlist_info
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return f"エラー: Spotify playlist error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio") 