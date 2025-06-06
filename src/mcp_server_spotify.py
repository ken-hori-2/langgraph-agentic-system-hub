from mcp.server.fastmcp import FastMCP
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
load_dotenv()

mcp = FastMCP(name="Spotify")
CLIENT_ID = os.getenv("SPOTIFY_USER_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_TOKEN")
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

@mcp.tool()
async def search_track(track_name: str) -> str:
    """指定された楽曲名でSpotifyを検索します。"""
    results = sp.search(q=track_name, type='track', limit=3)
    tracks = results.get('tracks', {}).get('items', [])
    output = "\n".join([f"{track['name']} by {track['artists'][0]['name']}" for track in tracks])
    return output

if __name__ == "__main__":
    mcp.run(transport="stdio")
    # mcp.run(transport="streamable_http") # , port=8006)
    # mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)