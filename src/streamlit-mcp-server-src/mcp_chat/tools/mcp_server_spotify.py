# Spotify APIを使用して楽曲を検索するMCPサーバー
from mcp.server.fastmcp import FastMCP
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

# 環境変数の読み込み
# .envファイルからSPOTIFY_USER_IDとSPOTIFY_TOKENを読み込みます
load_dotenv()

# MCPサーバーの初期化
# このサーバーは"Spotify"という名前で識別されます
mcp = FastMCP(name="Spotify")

# Spotify APIクライアントの初期化
# 環境変数から認証情報を取得してSpotify APIに接続します
CLIENT_ID = os.getenv("SPOTIFY_USER_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_TOKEN")
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

@mcp.tool()
async def search_track(track_name: str) -> str:
    """指定された楽曲名でSpotifyを検索します。
    
    Args:
        track_name: 検索する楽曲名
    
    Returns:
        str: 検索結果の文字列。以下の形式で返されます：
        - 楽曲名
        - アーティスト名
        - アルバム名
        - SpotifyのURL
    """
    try:
        # Spotify APIを使用して楽曲を検索
        # type='track'で楽曲のみを検索
        # limit=3で最大3件の結果を取得
        results = sp.search(q=track_name, type='track', limit=3)
        tracks = results.get('tracks', {}).get('items', [])
        
        if not tracks:
            return "該当する楽曲が見つかりませんでした。"
        
        # 検索結果を整形
        output = []
        for i, track in enumerate(tracks, 1):
            # 各楽曲の情報を整形
            track_info = [
                f"{i}. {track['name']}",  # 楽曲名
                f"   アーティスト: {', '.join(artist['name'] for artist in track['artists'])}",  # アーティスト名（複数の場合は全て表示）
                f"   アルバム: {track['album']['name']}",  # アルバム名
                f"   URL: {track['external_urls']['spotify']}"  # SpotifyのURL
            ]
            output.append("\n".join(track_info))
        
        return "\n\n".join(output)
    except Exception as e:
        return f"検索中にエラーが発生しました: {str(e)}"

if __name__ == "__main__":
    # MCPサーバーを起動
    # transport="stdio"で標準入出力を使用
    mcp.run(transport="stdio")
    # mcp.run(transport="streamable_http", port=8000)
    
    # 以下のようにHTTPサーバーとしても起動可能
    # mcp.run(transport="http", host="127.0.0.1", port=8001) 