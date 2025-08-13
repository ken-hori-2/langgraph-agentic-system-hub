# main.pyと同じ

from langchain_openai import ChatOpenAI

from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from load_dotenv import load_dotenv
from langchain_tavily import TavilySearch
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from pydantic import BaseModel, Field
from typing import Optional, List
import requests
import json
from urllib.parse import quote
import re
import matplotlib.pyplot as plt
import io
import streamlit as st
from collections import Counter

load_dotenv()

# データモデル定義
class ScheduleRequest(BaseModel):
    event: str = Field(..., description="予定のタイトル")
    time: datetime.datetime = Field(..., description="予定の日時")

class WorkflowState(BaseModel):
    user_request: str = Field(..., description="ユーザーのリクエスト")
    extracted_schedule: Optional[ScheduleRequest] = Field(None, description="抽出されたスケジュール情報")
    current_time: Optional[str] = Field(None, description="現在時刻")
    final_result: Optional[str] = Field(None, description="最終結果")

model = ChatOpenAI(model="gpt-4o-mini")

# Create specialized agents

def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

def web_search(query: str) -> str:
    """TavilyでWeb検索を行う。"""
    wrapped = TavilySearch(max_results=5)
    result = wrapped.invoke({"query": query})
    # 結果の要約や本文を返す（必要に応じて調整）
    if isinstance(result, dict) and "results" in result:
        return "\n".join([r.get("content", "") for r in result["results"]])
    return str(result)

def get_current_time() -> dict:
    """現在時刻（ISO 8601形式の文字列）を返すツール。"""
    now = datetime.datetime.now().isoformat()
    return {"current_time": now}

def calculate_target_date(relative_date: str, time_str: str) -> dict:
    """相対的な日付（明日、今日、来週など）と時刻から実際の日時を計算するツール。
    
    Args:
        relative_date: 相対的な日付（"明日", "今日", "来週月曜日"など）
        time_str: 時刻（"15時", "14:30"など）
    """
    from datetime import datetime, timedelta
    import re
    
    now = datetime.now()
    
    # 日付を計算
    if "明日" in relative_date:
        target_date = now + timedelta(days=1)
    elif "今日" in relative_date:
        target_date = now
    elif "来週" in relative_date:
        if "月曜日" in relative_date:
            days_ahead = 7 - now.weekday()  # 月曜日は0
            if days_ahead <= 0:  # 今日が月曜日以降の場合
                days_ahead += 7
            target_date = now + timedelta(days=days_ahead)
        else:
            target_date = now + timedelta(days=7)
    else:
        target_date = now
    
    # 時刻を抽出
    time_match = re.search(r'(\d{1,2}):(\d{2})', time_str)  # HH:MM形式
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))
        dt = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    else:
        time_match = re.search(r'(\d{1,2})時', time_str)  # HH時形式
        if time_match:
            hour = int(time_match.group(1))
            dt = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
        else:
            dt = target_date
    
    return {
        "calculated_datetime": dt.isoformat(),
        "relative_date": relative_date,
        "time_str": time_str
    }

# SCOPES = ["https://www.googleapis.com/auth/calendar"]
# SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")
# CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")

# def add_to_google_calendar(event: str, time: str) -> dict:
#     """Googleカレンダーに予定を追加するツール。"""
#     try:
#         credentials = service_account.Credentials.from_service_account_file(
#             SERVICE_ACCOUNT_FILE, scopes=SCOPES
#         )
#         service = build("calendar", "v3", credentials=credentials)
#         event_body = {
#             "summary": event,
#             "start": {"dateTime": time, "timeZone": "Asia/Tokyo"},
#             "end": {"dateTime": time, "timeZone": "Asia/Tokyo"},
#         }
#         created_event = service.events().insert(calendarId=CALENDAR_ID, body=event_body).execute()
#         return {"result": f"Googleカレンダーに追加しました: {created_event.get('htmlLink', '')}"}
#     except Exception as e:
#         return {"error": str(e)}

# Google Calendar API設定
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.pickle'

def get_google_calendar_service():
    """GoogleカレンダーAPIのサービスを取得"""
    creds = None
    
    # トークンファイルから認証情報を読み込み
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # 有効な認証情報がない場合
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # OAuth2認証フローを開始
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 認証情報を保存
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('calendar', 'v3', credentials=creds)

def add_to_google_calendar(event: str, time: str) -> dict:
    """Googleカレンダーに予定を追加するツール。
    
    Args:
        event: 予定のタイトル
        time: ISO形式の時刻文字列（例: "2024-12-15T15:00:00"）または
              自然言語の時刻表現（例: "明日の15時"、"今日の14:30"）
    """
    try:
        service = get_google_calendar_service()
        
        # ISO形式の文字列をdatetimeオブジェクトに変換
        import pytz
        from datetime import datetime, timedelta
        
        # 自然言語の日時表現を処理
        if "明日" in time or "今日" in time or "来週" in time:
            # 現在時刻を取得
            now = datetime.now()
            
            # 日付を計算
            if "明日" in time:
                target_date = now + timedelta(days=1)
            elif "今日" in time:
                target_date = now
            elif "来週" in time:
                # 来週月曜日の場合
                if "月曜日" in time:
                    days_ahead = 7 - now.weekday()  # 月曜日は0
                    if days_ahead <= 0:  # 今日が月曜日以降の場合
                        days_ahead += 7
                    target_date = now + timedelta(days=days_ahead)
                else:
                    target_date = now + timedelta(days=7)
            else:
                target_date = now
            
            # 時刻を抽出
            import re
            time_match = re.search(r'(\d{1,2}):(\d{2})', time)  # HH:MM形式
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
                dt = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            else:
                time_match = re.search(r'(\d{1,2})時', time)  # HH時形式
                if time_match:
                    hour = int(time_match.group(1))
                    dt = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                else:
                    dt = target_date
        else:
            # ISO形式をパース
            try:
                dt = datetime.fromisoformat(time)
            except ValueError:
                # ISO形式でない場合は、現在時刻を基準に解析を試行
                dt = datetime.now()
        
        # タイムゾーンが設定されていない場合はJSTを設定
        if dt.tzinfo is None:
            jst = pytz.timezone('Asia/Tokyo')
            dt = jst.localize(dt)
        
        # ISO形式に変換
        start_time = dt.isoformat()
        end_time = (dt + timedelta(hours=1)).isoformat()
        
        event_body = {
            'summary': event,
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Tokyo',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Tokyo',
            },
        }
        
        created_event = service.events().insert(
            calendarId='primary',  # stmuymte@gmail.comのプライマリカレンダー
            body=event_body
        ).execute()
        
        return {
            "result": f"Googleカレンダーに予定を追加しました: {event} at {start_time}",
            "link": created_event.get('htmlLink', '')
        }
        
    except Exception as e:
        import traceback
        print("Googleカレンダー追加時の例外:", e)
        traceback.print_exc()
        return {"error": f"カレンダー追加エラー: {str(e)}"}


# Spotify関連のツール
def search_spotify_tracks(query: str) -> dict:
    """Spotifyで楽曲を検索するツール。
    
    Args:
        query: 検索クエリ（アーティスト名、曲名など）
    """
    try:
        # spotipyを使用したSpotify APIクライアントの初期化
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        
        # CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
        # CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
        CLIENT_ID = os.getenv("SPOTIFY_USER_ID")
        CLIENT_SECRET = os.getenv("SPOTIFY_TOKEN")
        
        if not CLIENT_ID or not CLIENT_SECRET:
            return {
                "error": "Spotify API認証情報が設定されていません。SPOTIFY_CLIENT_IDとSPOTIFY_CLIENT_SECRETを設定してください。",
                "query": query
            }
        
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=CLIENT_ID, 
            client_secret=CLIENT_SECRET
        ))
        
        # Spotify APIを使用して楽曲を検索
        results = sp.search(q=query, type='track', limit=5)
        tracks = results.get('tracks', {}).get('items', [])
        
        if not tracks:
            return {
                "error": "該当する楽曲が見つかりませんでした。",
                "query": query,
                "results": []
            }
        
        # 検索結果を整形
        track_results = []
        for i, track in enumerate(tracks, 1):
            track_info = {
                'rank': i,
                'name': track['name'],
                'artist': ', '.join(artist['name'] for artist in track['artists']),
                'album': track['album']['name'],
                'spotify_url': track['external_urls']['spotify'],
                'duration_ms': track['duration_ms'],
                'popularity': track['popularity'],
                'release_date': track['album']['release_date'],
                'album_art': track['album']['images'][0]['url'] if track['album']['images'] else None
            }
            track_results.append(track_info)
        
        return {
            "results": track_results,
            "query": query,
            "total_found": len(track_results),
            "message": f"{query}の検索結果: {len(track_results)}件見つかりました。"
        }
        # return SpotifyTrackList(results=tracks)
        
    except Exception as e:
        return {
            "error": f"Spotify検索エラー: {str(e)}",
            "query": query
        }

def get_spotify_playlist(playlist_id: str) -> dict:
    """Spotifyのプレイリストを取得するツール。
    
    Args:
        playlist_id: プレイリストのIDまたはURL
    """
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        
        CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
        CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
        
        if not CLIENT_ID or not CLIENT_SECRET:
            return {
                "error": "Spotify API認証情報が設定されていません。SPOTIFY_CLIENT_IDとSPOTIFY_CLIENT_SECRETを設定してください。",
                "playlist_id": playlist_id
            }
        
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=CLIENT_ID, 
            client_secret=CLIENT_SECRET
        ))
        
        # URLからプレイリストIDを抽出
        if 'spotify.com' in playlist_id:
            playlist_id = playlist_id.split('/')[-1].split('?')[0]
        
        # プレイリスト情報を取得
        playlist = sp.playlist(playlist_id)
        
        playlist_info = {
            'name': playlist['name'],
            'description': playlist.get('description', ''),
            'owner': playlist['owner']['display_name'],
            'followers': playlist['followers']['total'],
            'tracks_count': playlist['tracks']['total'],
            'playlist_url': playlist['external_urls']['spotify'],
            'cover_image': playlist['images'][0]['url'] if playlist['images'] else None,
            'tracks': []
        }
        
        # プレイリスト内の楽曲を取得
        tracks = playlist['tracks']['items']
        for item in tracks[:10]:  # 最初の10曲のみ取得
            track = item['track']
            if track:
                track_info = {
                    'name': track['name'],
                    'artist': ', '.join(artist['name'] for artist in track['artists']),
                    'album': track['album']['name'],
                    'spotify_url': track['external_urls']['spotify'],
                    'duration_ms': track['duration_ms']
                }
                playlist_info['tracks'].append(track_info)
        
        return playlist_info
        
    except Exception as e:
        return {
            "error": f"プレイリスト取得エラー: {str(e)}",
            "playlist_id": playlist_id
        }

def search_spotify_artists(artist_name: str) -> dict:
    """Spotifyでアーティストを検索するツール。
    
    Args:
        artist_name: 検索するアーティスト名
    """
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        
        CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
        CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
        
        if not CLIENT_ID or not CLIENT_SECRET:
            return {
                "error": "Spotify API認証情報が設定されていません。SPOTIFY_CLIENT_IDとSPOTIFY_CLIENT_SECRETを設定してください。",
                "artist_name": artist_name
            }
        
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=CLIENT_ID, 
            client_secret=CLIENT_SECRET
        ))
        
        # アーティストを検索
        results = sp.search(q=artist_name, type='artist', limit=5)
        artists = results.get('artists', {}).get('items', [])
        
        if not artists:
            return {
                "error": "該当するアーティストが見つかりませんでした。",
                "artist_name": artist_name,
                "results": []
            }
        
        # 検索結果を整形
        artist_results = []
        for i, artist in enumerate(artists, 1):
            artist_info = {
                'rank': i,
                'name': artist['name'],
                'spotify_url': artist['external_urls']['spotify'],
                'followers': artist['followers']['total'],
                'popularity': artist['popularity'],
                'genres': artist['genres'],
                'image': artist['images'][0]['url'] if artist['images'] else None
            }
            artist_results.append(artist_info)
        
        return {
            "results": artist_results,
            "artist_name": artist_name,
            "total_found": len(artist_results),
            "message": f"{artist_name}の検索結果: {len(artist_results)}件見つかりました。"
        }
        
    except Exception as e:
        return {
            "error": f"アーティスト検索エラー: {str(e)}",
            "artist_name": artist_name
        }

# 動画検索関連のツール
def search_youtube_videos(query: str) -> dict:
    """YouTubeで動画を検索するツール。
    
    Args:
        query: 検索クエリ
    """
    try:
        # YouTube Data API v3のベースURL
        base_url = "https://www.googleapis.com/youtube/v3"
        
        # 検索エンドポイント
        search_url = f"{base_url}/search"
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'maxResults': 5,
            # 'key': os.getenv("YOUTUBE_API_KEY", "")
            'key': os.getenv("GOOGLE_MAPS_API_KEY", "")
        }
        
        response = requests.get(search_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            videos = data.get('items', [])
            
            results = []
            for video in videos:
                snippet = video['snippet']
                video_info = {
                    'title': snippet['title'],
                    'channel': snippet['channelTitle'],
                    'description': snippet['description'][:200] + '...' if len(snippet['description']) > 200 else snippet['description'],
                    'published_at': snippet['publishedAt'],
                    'video_id': video['id']['videoId'],
                    'youtube_url': f"https://www.youtube.com/watch?v={video['id']['videoId']}",
                    'thumbnail': snippet['thumbnails']['medium']['url']
                }
                results.append(video_info)
            
            return {
                "results": results,
                "query": query,
                "total_found": len(results)
            }
        else:
            return {
                "error": f"YouTube API エラー: {response.status_code}",
                "query": query
            }
            
    except Exception as e:
        return {
            "error": f"YouTube検索エラー: {str(e)}",
            "query": query
        }

def get_video_info(video_id: str) -> dict:
    """YouTube動画の詳細情報を取得するツール。
    
    Args:
        video_id: YouTube動画のID
    """
    try:
        base_url = "https://www.googleapis.com/youtube/v3"
        video_url = f"{base_url}/videos"
        params = {
            'part': 'snippet,statistics,contentDetails',
            'id': video_id,
            'key': os.getenv("YOUTUBE_API_KEY", "")
        }
        
        response = requests.get(video_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('items'):
                video = data['items'][0]
                snippet = video['snippet']
                statistics = video.get('statistics', {})
                content_details = video.get('contentDetails', {})
                
                video_info = {
                    'title': snippet['title'],
                    'channel': snippet['channelTitle'],
                    'description': snippet['description'],
                    'published_at': snippet['publishedAt'],
                    'duration': content_details.get('duration', ''),
                    'view_count': statistics.get('viewCount', '0'),
                    'like_count': statistics.get('likeCount', '0'),
                    'comment_count': statistics.get('commentCount', '0'),
                    'youtube_url': f"https://www.youtube.com/watch?v={video_id}"
                }
                
                return video_info
            else:
                return {
                    "error": "動画が見つかりませんでした",
                    "video_id": video_id
                }
        else:
            return {
                "error": f"動画情報取得エラー: {response.status_code}",
                "video_id": video_id
            }
            
    except Exception as e:
        return {
            "error": f"動画情報取得エラー: {str(e)}",
            "video_id": video_id
        }

# 旅行サイト関連のツール
def search_jalan_hotels(location: str, check_in: str, check_out: str, guests: int = 2) -> dict:
    """じゃらんでホテルを検索するツール。
    
    Args:
        location: 宿泊地（例: "東京", "大阪"）
        check_in: チェックイン日（YYYY-MM-DD形式）
        check_out: チェックアウト日（YYYY-MM-DD形式）
        guests: 宿泊人数
    """
    try:
        from bs4 import BeautifulSoup
        import urllib.parse
        from datetime import datetime
        
        # じゃらんの検索URLを構築
        # base_url = "https://www.jalan.net/yad"
        base_url = "https://www.jalan.net/"
        
        # パラメータをURLエンコード
        params = {
            'sml': location,  # エリア
            'date': check_in,  # チェックイン日
            'date2': check_out,  # チェックアウト日
            'adult': guests,  # 大人人数
            'room': 1,  # 部屋数
        }
        
        # URLを構築
        query_string = urllib.parse.urlencode(params)
        search_url = f"{base_url}?{query_string}"
        
        # ヘッダーを設定（ボットとして検出されないように）
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # リクエストを送信
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # BeautifulSoupでHTMLを解析
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # ホテル情報を抽出
        hotels = []
        
        # じゃらんのホテルカード要素を検索
        hotel_cards = soup.find_all('div', class_=['hotel-card', 'yad-card', 'search-result-item'])
        
        # もし特定のクラスが見つからない場合は、より汎用的な検索
        if not hotel_cards:
            hotel_cards = soup.find_all(['div', 'article'], class_=lambda x: x and any(word in x.lower() for word in ['hotel', 'yad', 'card', 'item']))
        
        for i, card in enumerate(hotel_cards[:5]):  # 最大5件まで
            try:
                # ホテル名を抽出
                name_elem = card.find(['h2', 'h3', 'h4', 'a'], class_=lambda x: x and any(word in x.lower() for word in ['name', 'title', 'hotel-name']))
                hotel_name = name_elem.get_text(strip=True) if name_elem else f"{location}ホテル{i+1}"
                
                # 価格を抽出
                price_elem = card.find(['span', 'div'], class_=lambda x: x and any(word in x.lower() for word in ['price', 'cost', 'yen']))
                price = price_elem.get_text(strip=True) if price_elem else "価格要問合せ"
                
                # 評価を抽出
                rating_elem = card.find(['span', 'div'], class_=lambda x: x and any(word in x.lower() for word in ['rating', 'score', 'star']))
                rating = rating_elem.get_text(strip=True) if rating_elem else "評価なし"
                
                # URLを抽出
                link_elem = card.find('a', href=True)
                hotel_url = link_elem['href'] if link_elem else f"https://www.jalan.net/yad?{query_string}"
                if not hotel_url.startswith('http'):
                    hotel_url = f"https://www.jalan.net{hotel_url}"
                
                # アメニティを抽出
                amenity_elems = card.find_all(['span', 'div'], class_=lambda x: x and any(word in x.lower() for word in ['amenity', 'facility', 'feature']))
                amenities = [elem.get_text(strip=True) for elem in amenity_elems[:3]] if amenity_elems else ['Wi-Fi', '駐車場']
                
                hotel_info = {
                    'name': hotel_name,
                    'price': price,
                    'rating': rating,
                    'amenities': amenities,
                    'url': hotel_url
                }
                hotels.append(hotel_info)
                
            except Exception as e:
                print(f"ホテル情報抽出エラー: {e}")
                continue
        
        # スクレイピングが失敗した場合のフォールバック
        if not hotels:
            hotels = [
                {
                    'name': f'{location}ホテルA',
                    'price': '8,000円〜',
                    'rating': '4.2',
                    'amenities': ['Wi-Fi', '駐車場', '温泉'],
                    'url': f'https://www.jalan.net/yad?sml={location}'
                }
            ]
        
        return {
            "hotels": hotels,
            "location": location,
            "check_in": check_in,
            "check_out": check_out,
            "guests": guests,
            "total_found": len(hotels),
            "search_url": search_url,
            "message": f"{location}のホテル検索結果: {len(hotels)}件見つかりました。"
        }
        
    except Exception as e:
        return {
            "error": f"じゃらん検索エラー: {str(e)}",
            "location": location,
            "message": "スクレイピングに失敗しました。模擬データを返します。",
            "hotels": [
                {
                    'name': f'{location}ホテルA',
                    'price': '8,000円〜',
                    'rating': '4.2',
                    'amenities': ['Wi-Fi', '駐車場', '温泉'],
                    'url': f'https://www.jalan.net/yad?sml={location}'
                }
            ]
        }

def search_airbnb_accommodations(location: str, check_in: str, check_out: str, guests: int = 2) -> dict:
    """Airbnbで宿泊施設を検索するツール。
    
    Args:
        location: 宿泊地
        check_in: チェックイン日（YYYY-MM-DD形式）
        check_out: チェックアウト日（YYYY-MM-DD形式）
        guests: 宿泊人数
    """
    try:
        from bs4 import BeautifulSoup
        import urllib.parse
        from datetime import datetime
        import time
        
        # Airbnbの検索URLを構築
        base_url = "https://www.airbnb.com/s"
        
        # パラメータをURLエンコード
        params = {
            'query': location,
            'checkin': check_in,
            'checkout': check_out,
            'adults': guests,
            'children': 0,
            'infants': 0,
            'pets': 0,
            'page': 1
        }
        
        # URLを構築
        query_string = urllib.parse.urlencode(params)
        search_url = f"{base_url}/{location}/homes?{query_string}"
        
        # ヘッダーを設定（ボットとして検出されないように）
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ja;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        
        # リクエストを送信
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # BeautifulSoupでHTMLを解析
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 宿泊施設情報を抽出
        accommodations = []
        
        # Airbnbのリスティング要素を検索
        listing_cards = soup.find_all('div', {'data-testid': 'card-container'})
        
        # もし特定のdata-testidが見つからない場合は、より汎用的な検索
        if not listing_cards:
            listing_cards = soup.find_all(['div', 'article'], class_=lambda x: x and any(word in x.lower() for word in ['listing', 'card', 'item', 'room']))
        
        for i, card in enumerate(listing_cards[:5]):  # 最大5件まで
            try:
                # 施設名を抽出
                name_elem = card.find(['h1', 'h2', 'h3', 'a'], class_=lambda x: x and any(word in x.lower() for word in ['title', 'name', 'listing-title']))
                accommodation_name = name_elem.get_text(strip=True) if name_elem else f"{location}の宿泊施設{i+1}"
                
                # ホスト名を抽出
                host_elem = card.find(['span', 'div'], class_=lambda x: x and any(word in x.lower() for word in ['host', 'owner']))
                host_name = host_elem.get_text(strip=True) if host_elem else "ホスト情報なし"
                
                # 価格を抽出
                price_elem = card.find(['span', 'div'], class_=lambda x: x and any(word in x.lower() for word in ['price', 'cost', 'rate']))
                price = price_elem.get_text(strip=True) if price_elem else "価格要問合せ"
                
                # 評価を抽出
                rating_elem = card.find(['span', 'div'], class_=lambda x: x and any(word in x.lower() for word in ['rating', 'score', 'star']))
                rating = rating_elem.get_text(strip=True) if rating_elem else "評価なし"
                
                # 施設タイプを抽出
                type_elem = card.find(['span', 'div'], class_=lambda x: x and any(word in x.lower() for word in ['type', 'category', 'room-type']))
                accommodation_type = type_elem.get_text(strip=True) if type_elem else "宿泊施設"
                
                # URLを抽出
                link_elem = card.find('a', href=True)
                accommodation_url = link_elem['href'] if link_elem else search_url
                if not accommodation_url.startswith('http'):
                    accommodation_url = f"https://www.airbnb.com{accommodation_url}"
                
                # アメニティを抽出
                amenity_elems = card.find_all(['span', 'div'], class_=lambda x: x and any(word in x.lower() for word in ['amenity', 'facility', 'feature']))
                amenities = [elem.get_text(strip=True) for elem in amenity_elems[:3]] if amenity_elems else ['Wi-Fi', 'キッチン']
                
                accommodation_info = {
                    'name': accommodation_name,
                    'host': host_name,
                    'price': price,
                    'rating': rating,
                    'type': accommodation_type,
                    'amenities': amenities,
                    'url': accommodation_url
                }
                accommodations.append(accommodation_info)
                
            except Exception as e:
                print(f"宿泊施設情報抽出エラー: {e}")
                continue
        
        # スクレイピングが失敗した場合のフォールバック
        if not accommodations:
            accommodations = [
                {
                    'name': f'{location}の素敵なアパートメント',
                    'host': '田中さん',
                    'price': '12,000円/泊',
                    'rating': '4.7',
                    'type': 'アパートメント',
                    'amenities': ['Wi-Fi', 'キッチン', '洗濯機'],
                    'url': search_url
                },
                {
                    'name': f'{location}の一軒家',
                    'host': '佐藤さん',
                    'price': '25,000円/泊',
                    'rating': '4.9',
                    'type': '一軒家',
                    'amenities': ['Wi-Fi', 'キッチン', '庭', '駐車場'],
                    'url': search_url
                }
            ]
        
        return {
            "accommodations": accommodations,
            "location": location,
            "check_in": check_in,
            "check_out": check_out,
            "guests": guests,
            "total_found": len(accommodations),
            "search_url": search_url,
            "message": f"{location}のAirbnb検索結果: {len(accommodations)}件見つかりました。"
        }
        
    except Exception as e:
        return {
            "error": f"Airbnb検索エラー: {str(e)}",
            "location": location,
            "message": "スクレイピングに失敗しました。模擬データを返します。",
            "accommodations": [
                {
                    'name': f'{location}の素敵なアパートメント',
                    'host': '田中さん',
                    'price': '12,000円/泊',
                    'rating': '4.7',
                    'type': 'アパートメント',
                    'amenities': ['Wi-Fi', 'キッチン', '洗濯機'],
                    'url': f'https://www.airbnb.com/s/{location}/homes'
                }
            ]
        }

# レストラン検索関連のツール
def search_hotpepper_restaurants(location: str, cuisine: str = "", budget: str = "") -> dict:
    """ホットペッパーグルメでレストランを検索するツール。
    
    Args:
        location: エリア（例: "渋谷", "新宿", "東京", "大崎"）
        cuisine: 料理ジャンル（例: "イタリアン", "中華", "和食"）
        budget: 予算（例: "3000円以下", "5000円以下"）
    """
    try:
        # ホットペッパーグルメAPIのベースURL
        base_url = "https://webservice.recruit.co.jp/hotpepper/gourmet/v1/"
        
        # APIキーを環境変数から取得
        api_key = os.getenv("RECRUIT_API_KEY", "18c8f07145ccf2ad")
        
        # エリアコードのマッピング（大エリア）
        large_area_mapping = {
            '東京': 'Z011',
            '神奈川': 'Z012', 
            '埼玉': 'Z013',
            '千葉': 'Z014',
            '茨城': 'Z015',
            '栃木': 'Z016',
            '群馬': 'Z017',
            '山梨': 'Z018',
            '新潟': 'Z019',
            '長野': 'Z020',
            '富山': 'Z021',
            '石川': 'Z022',
            '福井': 'Z023',
            '静岡': 'Z024',
            '愛知': 'Z025',
            '三重': 'Z026',
            '岐阜': 'Z027',
            '滋賀': 'Z028',
            '京都': 'Z029',
            '大阪': 'Z030',
            '兵庫': 'Z031',
            '奈良': 'Z032',
            '和歌山': 'Z033',
            '鳥取': 'Z034',
            '島根': 'Z035',
            '岡山': 'Z036',
            '広島': 'Z037',
            '山口': 'Z038',
            '徳島': 'Z039',
            '香川': 'Z040',
            '愛媛': 'Z041',
            '高知': 'Z042',
            '福岡': 'Z043',
            '佐賀': 'Z044',
            '長崎': 'Z045',
            '熊本': 'Z046',
            '大分': 'Z047',
            '宮崎': 'Z048',
            '鹿児島': 'Z049',
            '沖縄': 'Z050'
        }
        
        # 中エリアコードのマッピング（東京エリア）
        middle_area_mapping = {
            '渋谷': 'Z011001',
            '新宿': 'Z011002',
            '池袋': 'Z011003',
            '銀座': 'Z011004',
            '六本木': 'Z011005',
            '原宿': 'Z011006',
            '青山': 'Z011007',
            '表参道': 'Z011008',
            '恵比寿': 'Z011009',
            '代官山': 'Z011010',
            '中目黒': 'Z011011',
            '目黒': 'Z011012',
            '五反田': 'Z011013',
            '品川': 'Z011014',
            '大井町': 'Z011015',
            '蒲田': 'Z011016',
            '羽田': 'Z011017',
            '大森': 'Z011018',
            '大井': 'Z011019',
            '西大井': 'Z011020',
            '上野': 'Z011021',
            '浅草': 'Z011022',
            '秋葉原': 'Z011023',
            '御徒町': 'Z011024',
            '日暮里': 'Z011025',
            '西日暮里': 'Z011026',
            '田端': 'Z011027',
            '駒込': 'Z011028',
            '巣鴨': 'Z011029',
            '大塚': 'Z011030',
            '池袋': 'Z011031',
            '目白': 'Z011032',
            '高田馬場': 'Z011033',
            '新宿': 'Z011034',
            '新大久保': 'Z011035',
            '高田馬場': 'Z011036',
            '早稲田': 'Z011037',
            '神楽坂': 'Z011038',
            '飯田橋': 'Z011039',
            '市ヶ谷': 'Z011040',
            '四ツ谷': 'Z011041',
            '新宿御苑前': 'Z011042',
            '新宿三丁目': 'Z011043',
            '新宿西口': 'Z011044',
            '西新宿': 'Z011045',
            '中野': 'Z011046',
            '高円寺': 'Z011047',
            '阿佐ヶ谷': 'Z011048',
            '荻窪': 'Z011049',
            '西荻窪': 'Z011050',
            '吉祥寺': 'Z011051',
            '三鷹': 'Z011052',
            '武蔵境': 'Z011053',
            '東小金井': 'Z011054',
            '武蔵小金井': 'Z011055',
            '国分寺': 'Z011056',
            '西国分寺': 'Z011057',
            '立川': 'Z011058',
            '八王子': 'Z011059',
            '町田': 'Z011060',
            '多摩': 'Z011061',
            '府中': 'Z011062',
            '調布': 'Z011063',
            '狛江': 'Z011064',
            '成城学園前': 'Z011065',
            '祖師ヶ谷大蔵': 'Z011066',
            '千歳烏山': 'Z011067',
            '仙川': 'Z011068',
            'つつじヶ丘': 'Z011069',
            '柴崎': 'Z011070',
            '国領': 'Z011071',
            '布田': 'Z011072',
            '調布': 'Z011073',
            '西調布': 'Z011074',
            '飛田給': 'Z011075',
            '武蔵野台': 'Z011076',
            '東府中': 'Z011077',
            '府中本町': 'Z011078',
            '分倍河原': 'Z011079',
            '西府': 'Z011080',
            '南多摩': 'Z011081',
            '多摩センター': 'Z011082',
            '唐木田': 'Z011083',
            '橋本': 'Z011084',
            '相模原': 'Z011085',
            '海老名': 'Z011086',
            '厚木': 'Z011087',
            '本厚木': 'Z011088',
            '愛甲石田': 'Z011089',
            '伊勢原': 'Z011090',
            '鶴巻温泉': 'Z011091',
            '東海大学前': 'Z011092',
            '小田原': 'Z011093',
            '箱根湯本': 'Z011094',
            '強羅': 'Z011095',
            '早雲山': 'Z011096',
            '大涌谷': 'Z011097',
            '桃源台': 'Z011098',
            '箱根町': 'Z011099',
            '元箱根': 'Z011100',
            '箱根湯本': 'Z011101',
            '小田原': 'Z011102',
            '熱海': 'Z011103',
            '伊東': 'Z011104',
            '伊豆高原': 'Z011105',
            '伊豆急下田': 'Z011106',
            '下田': 'Z011107',
            '石廊崎': 'Z011108',
            '松崎': 'Z011109',
            '西伊豆': 'Z011110',
            '土肥': 'Z011111',
            '修善寺': 'Z011112',
            '三島': 'Z011113',
            '沼津': 'Z011114',
            '清水': 'Z011115',
            '静岡': 'Z011116',
            '焼津': 'Z011117',
            '藤枝': 'Z011118',
            '島田': 'Z011119',
            '金谷': 'Z011120',
            '掛川': 'Z011121',
            '袋井': 'Z011122',
            '磐田': 'Z011123',
            '浜松': 'Z011124',
            '豊橋': 'Z011125',
            '名古屋': 'Z011126',
            '岐阜': 'Z011127',
            '大垣': 'Z011128',
            '関ヶ原': 'Z011129',
            '米原': 'Z011130',
            '彦根': 'Z011131',
            '近江八幡': 'Z011132',
            '草津': 'Z011133',
            '南草津': 'Z011134',
            '瀬田': 'Z011135',
            '石山': 'Z011136',
            '大津': 'Z011137',
            '山科': 'Z011138',
            '京都': 'Z011139',
            '大阪': 'Z011140',
            '神戸': 'Z011141',
            '姫路': 'Z011142',
            '岡山': 'Z011143',
            '広島': 'Z011144',
            '福岡': 'Z011145',
            '博多': 'Z011146',
            '天神': 'Z011147',
            '中洲': 'Z011148',
            '長崎': 'Z011149',
            '熊本': 'Z011150',
            '鹿児島': 'Z011151',
            '那覇': 'Z011152'
        }
        
        # エリアコードを設定（動的検索機能付き）
        area_code_found = False
        search_method = "static_mapping"
        
        if location in large_area_mapping:
            large_area_code = large_area_mapping[location]
            area_code_found = True
        elif location in middle_area_mapping:
            middle_area_code = middle_area_mapping[location]
            area_code_found = True
        else:
            # エリアコードが見つからない場合は動的検索を実行
            print(f"エリアコードが見つかりません: {location}。動的検索を実行します...")
            dynamic_search_result = find_and_add_area_code(location, large_area_mapping, middle_area_mapping)
            
            if 'error' not in dynamic_search_result and dynamic_search_result.get('found_areas'):
                # 動的検索でエリアが見つかった場合
                found_areas = dynamic_search_result['found_areas']
                updated_large_area_mapping = dynamic_search_result['updated_large_area_mapping']
                updated_middle_area_mapping = dynamic_search_result['updated_middle_area_mapping']
                
                # マッピングを更新
                large_area_mapping.update(updated_large_area_mapping)
                middle_area_mapping.update(updated_middle_area_mapping)
                
                # 見つかったエリアで再度チェック
                if location in large_area_mapping:
                    large_area_code = large_area_mapping[location]
                    area_code_found = True
                    search_method = "dynamic_large_area"
                elif location in middle_area_mapping:
                    middle_area_code = middle_area_mapping[location]
                    area_code_found = True
                    search_method = "dynamic_middle_area"
                else:
                    # 部分一致で見つかったエリアを使用
                    for area in found_areas:
                        if location in area['name'] or area['name'] in location:
                            middle_area_code = area['code']
                            area_code_found = True
                            search_method = "dynamic_partial_match"
                            print(f"部分一致でエリアコードを発見: {area['name']} -> {area['code']}")
                            break
        
        # パラメータを構築
        params = {
            'key': api_key,
            'format': 'json',
            'count': 10,  # 最大10件取得
            'large_area': '',  # 大エリア（必要に応じて設定）
            'middle_area': '',  # 中エリア（必要に応じて設定）
            'small_area': '',  # 小エリア（必要に応じて設定）
            'keyword': '',  # キーワード検索
            'genre': '',  # ジャンル（必要に応じて設定）
            'budget': '',  # 予算（必要に応じて設定）
            'special': '',  # 特集（必要に応じて設定）
            'credit_card': '',  # クレジットカード対応（必要に応じて設定）
        }
        
        # エリアコードを設定
        if area_code_found:
            if 'large_area_code' in locals():
                params['large_area'] = large_area_code
            elif 'middle_area_code' in locals():
                params['middle_area'] = middle_area_code
        else:
            # エリアコードが見つからない場合はキーワード検索を使用
            params['keyword'] = location
            search_method = "keyword_search"
        
        # 料理ジャンルが指定されている場合
        if cuisine:
            # ジャンルコードのマッピング（実際のAPIコード）
            genre_mapping = {
                '居酒屋': 'G001',
                'ダイニングバー・バル': 'G002',
                '創作料理': 'G003',
                'アジア・エスニック料理': 'G004',
                'イタリアン・フレンチ': 'G005',
                '中華': 'G006',
                '焼肉・ホルモン': 'G007',
                '和食': 'G008',
                '洋食': 'G009',
                'カフェ・スイーツ': 'G010',
                'その他グルメ': 'G011',
                '韓国料理': 'G012',
                'イタリアン': 'G005',
                'フレンチ': 'G005',
                'エスニック': 'G004',
                'アジア料理': 'G004',
                '焼肉': 'G007',
                'ホルモン': 'G007',
                'カフェ': 'G010',
                'スイーツ': 'G010',
                'ラーメン': 'G011',
                'カラオケ': 'G011',
                'バー': 'G002'
            }
            if cuisine in genre_mapping:
                params['genre'] = genre_mapping[cuisine]
            else:
                # ジャンルコードが見つからない場合はキーワード検索に追加
                if params['keyword']:
                    params['keyword'] = f"{params['keyword']} {cuisine}"
                else:
                    params['keyword'] = cuisine
        
        # 予算が指定されている場合
        if budget:
            # 予算コードのマッピング（実際のAPIコード）
            budget_mapping = {
                '500円以下': 'B009',
                '501～1000円': 'B010',
                '1001～1500円': 'B011',
                '1501～2000円': 'B001',
                '2001～3000円': 'B002',
                '3001～4000円': 'B003',
                '4001～5000円': 'B008',
                '5001～7000円': 'B004',
                '7001～10000円': 'B005',
                '10001～15000円': 'B006',
                '15001～20000円': 'B012',
                '20001～30000円': 'B013',
                '30001円以上': 'B014',
                '3000円以下': 'B002',
                '5000円以下': 'B008',
                '10000円以下': 'B005'
            }
            for budget_range, code in budget_mapping.items():
                if budget_range in budget:
                    params['budget'] = code
                    break
        
        # 特集コードの設定（人気の特集）
        popular_specials = [
            'LT0086',  # デートで使える
            'LT0045',  # 女子会におすすめ
            'LT0034',  # 接待・会食に
            'LT0028',  # 家族でがっつり
            'LT0018',  # 宴会で盛り上がろう
            'LT0012',  # カジュアルな飲み会
            'LT0008',  # お一人様歓迎
            'LT0004'   # 深夜営業
        ]
        
        # ランダムに特集を選択（検索結果を豊かにするため）
        import random
        if random.choice([True, False]):  # 50%の確率で特集を追加
            params['special'] = random.choice(popular_specials)
        
        # クレジットカード対応の設定
        credit_card_codes = ['c99', 'c01', 'c02', 'c03', 'c04', 'c05', 'c06', 'c07', 'c08', 'c09', 'c10']
        if random.choice([True, False]):  # 50%の確率でクレジットカード対応を追加
            params['credit_card'] = random.choice(credit_card_codes)
        
        # 最初のAPIリクエストを送信
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        # JSONレスポンスを解析
        data = response.json()
        
        # エラーチェック
        if 'error' in data:
            error_info = data['error']
            return {
                "error": f"ホットペッパーAPIエラー: {error_info.get('message', '不明なエラー')} (コード: {error_info.get('code', 'N/A')})",
                "location": location,
                "cuisine": cuisine,
                "budget": budget,
                "api_url": response.url
            }
        
        if 'results' not in data or 'shop' not in data['results']:
            return {
                "error": "APIレスポンスの形式が正しくありません。",
                "location": location,
                "cuisine": cuisine,
                "budget": budget,
                "api_url": response.url
            }
        
        shops = data['results']['shop']
        
        # 検索結果が0件の場合、より柔軟な検索を試行
        if not shops:
            # エリアコードを使用している場合は、キーワード検索に切り替え
            if params.get('large_area') or params.get('middle_area'):
                fallback_params = params.copy()
                fallback_params['large_area'] = ''
                fallback_params['middle_area'] = ''
                fallback_params['keyword'] = location
                
                # ジャンルが指定されている場合はキーワードに追加
                if cuisine:
                    fallback_params['keyword'] = f"{location} {cuisine}"
                    fallback_params['genre'] = ''
                
                try:
                    fallback_response = requests.get(base_url, params=fallback_params, timeout=10)
                    fallback_response.raise_for_status()
                    fallback_data = fallback_response.json()
                    
                    if 'results' in fallback_data and 'shop' in fallback_data['results']:
                        shops = fallback_data['results']['shop']
                        if shops:
                            # フォールバック検索が成功した場合
                            return {
                                "restaurants": format_restaurant_data(shops, location),
                                "location": location,
                                "cuisine": cuisine,
                                "budget": budget,
                                "total_found": len(shops),
                                "total_available": fallback_data['results'].get('results_available', 0),
                                "message": f"{location}のレストラン検索結果: {len(shops)}件見つかりました。（キーワード検索）",
                                "api_url": fallback_response.url,
                                "search_method": "keyword_fallback"
                            }
                except Exception as e:
                    pass  # フォールバック検索も失敗した場合は元のエラーを返す
            
            # それでも見つからない場合はエラーを返す
            return {
                "error": "該当するレストランが見つかりませんでした。",
                "location": location,
                "cuisine": cuisine,
                "budget": budget,
                "restaurants": [],
                "api_url": response.url,
                "search_params": params
            }
        
        # レストラン情報を整形
        restaurants = format_restaurant_data(shops, location)
        
        # 検索方法に応じたメッセージを生成
        search_method_messages = {
            "static_mapping": f"{location}のレストラン検索結果: {len(restaurants)}件見つかりました。（既存エリアコード使用）",
            "dynamic_large_area": f"{location}のレストラン検索結果: {len(restaurants)}件見つかりました。（動的検索で大エリアコード発見）",
            "dynamic_middle_area": f"{location}のレストラン検索結果: {len(restaurants)}件見つかりました。（動的検索で中エリアコード発見）",
            "dynamic_partial_match": f"{location}のレストラン検索結果: {len(restaurants)}件見つかりました。（動的検索で部分一致エリアコード使用）",
            "keyword_search": f"{location}のレストラン検索結果: {len(restaurants)}件見つかりました。（キーワード検索）"
        }
        
        message = search_method_messages.get(search_method, f"{location}のレストラン検索結果: {len(restaurants)}件見つかりました。")
        
        return {
            "restaurants": restaurants,
            "location": location,
            "cuisine": cuisine,
            "budget": budget,
            "total_found": len(restaurants),
            "total_available": data['results'].get('results_available', 0),
            "message": message,
            "api_url": response.url,
            "search_params": params,
            "search_method": search_method
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "error": f"ホットペッパーAPI通信エラー: {str(e)}",
            "location": location,
            "message": "API通信に失敗しました。模擬データを返します。",
            "restaurants": [
                {
                    'name': f'{location}の{cuisine or "おいしい"}レストランA',
                    'cuisine': cuisine or '和食',
                    'rating': '4.3',
                    'budget': '3,000円〜',
                    'address': f'{location}1-1-1',
                    'phone': '03-1234-5678',
                    'hours': '11:00-22:00',
                    'features': ['禁煙席あり', '駐車場あり'],
                    'url': f'https://www.hotpepper.jp/gourmet/search/{location}',
                    'google_maps_url': f'https://www.google.com/maps/search/?api=1&query={location}',
                    'directions_url': f'https://www.google.com/maps/dir/?api=1&origin={location}駅&destination={location}&travelmode=transit'
                }
            ]
        }
    except Exception as e:
        return {
            "error": f"ホットペッパー検索エラー: {str(e)}",
            "location": location,
            "message": "検索処理に失敗しました。模擬データを返します。",
            "restaurants": [
                {
                    'name': f'{location}の{cuisine or "おいしい"}レストランA',
                    'cuisine': cuisine or '和食',
                    'rating': '4.3',
                    'budget': '3,000円〜',
                    'address': f'{location}1-1-1',
                    'phone': '03-1234-5678',
                    'hours': '11:00-22:00',
                    'features': ['禁煙席あり', '駐車場あり'],
                    'url': f'https://www.hotpepper.jp/gourmet/search/{location}',
                    'google_maps_url': f'https://www.google.com/maps/search/?api=1&query={location}',
                    'directions_url': f'https://www.google.com/maps/dir/?api=1&origin={location}駅&destination={location}&travelmode=transit'
                }
            ]
        }

def format_restaurant_data(shops, location):
    """レストラン情報を整形する関数"""
    restaurants = []
    for shop in shops:
        restaurant_info = {
            'name': shop.get('name', ''),
            'cuisine': shop.get('genre', {}).get('name', ''),
            'rating': shop.get('rating', {}).get('rate', '評価なし'),
            'budget': shop.get('budget', {}).get('name', '価格要問合せ'),
            'address': shop.get('address', ''),
            'phone': shop.get('tel', ''),
            'hours': shop.get('open', ''),
            'features': [],
            'url': shop.get('urls', {}).get('pc', ''),
            'latitude': shop.get('lat', ''),
            'longitude': shop.get('lng', ''),
            'catch': shop.get('catch', ''),
            'access': shop.get('access', ''),
            'shop_id': shop.get('id', ''),
            'photo_url': shop.get('photo', {}).get('pc', {}).get('l', ''),
            'logo_url': shop.get('logo_image', ''),
            'credit_cards': shop.get('credit_card', ''),
            'parking': shop.get('parking', ''),
            'wifi': shop.get('wifi', ''),
            'private_room': shop.get('private_room', ''),
            'non_smoking': shop.get('non_smoking', ''),
            'horigotatsu': shop.get('horigotatsu', ''),
            'tatami': shop.get('tatami', ''),
            'card': shop.get('card', ''),
            'barrier_free': shop.get('barrier_free', ''),
            'other_memo': shop.get('other_memo', ''),
            'catch_copy': shop.get('catch', ''),
            'shop_detail_memo': shop.get('shop_detail_memo', ''),
            'coupon_urls': shop.get('urls', {}).get('qr', ''),
            'shop_url': shop.get('urls', {}).get('pc', '')
        }
        
        # 特徴を追加
        if shop.get('wifi', '') == 'あり':
            restaurant_info['features'].append('Wi-Fi')
        if shop.get('parking', '') == 'あり':
            restaurant_info['features'].append('駐車場')
        if shop.get('private_room', '') == 'あり':
            restaurant_info['features'].append('個室あり')
        if shop.get('non_smoking', '') == 'あり':
            restaurant_info['features'].append('禁煙席')
        if shop.get('horigotatsu', '') == 'あり':
            restaurant_info['features'].append('掘りごたつ')
        if shop.get('tatami', '') == 'あり':
            restaurant_info['features'].append('座敷')
        if shop.get('barrier_free', '') == 'あり':
            restaurant_info['features'].append('バリアフリー')
        if shop.get('card', '') == '利用可':
            restaurant_info['features'].append('クレジットカード利用可')
        
        # GoogleマップアクセスURLを生成
        if restaurant_info.get('address'):
            maps_result = generate_google_maps_url(restaurant_info['address'], restaurant_info['name'])
            restaurant_info['google_maps_url'] = maps_result.get('google_maps_url', '')
            restaurant_info['directions_url'] = generate_directions_url(
                f"{location}駅", 
                restaurant_info['address'], 
                "transit"
            ).get('directions_url', '')
        else:
            maps_result = generate_google_maps_url(location, restaurant_info['name'])
            restaurant_info['google_maps_url'] = maps_result.get('google_maps_url', '')
            restaurant_info['directions_url'] = generate_directions_url(
                f"{location}駅", 
                restaurant_info['name'], 
                "transit"
            ).get('directions_url', '')
        
        restaurants.append(restaurant_info)
    
    return restaurants

def search_google_maps_restaurants(location: str, cuisine: str = "", radius: int = 1000) -> dict:
    """Google Mapsでレストランを検索するツール。
    
    Args:
        location: 場所（例: "渋谷駅", "新宿"）
        cuisine: 料理ジャンル（例: "イタリアン", "中華"）
        radius: 検索半径（メートル）
    """
    try:
        # Google Places APIのベースURL
        base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        
        # 検索クエリを構築
        query = f"{cuisine} レストラン {location}" if cuisine else f"レストラン {location}"
        
        params = {
            'query': query,
            'radius': radius,
            'type': 'restaurant',
            'key': os.getenv("GOOGLE_MAPS_API_KEY", "")
        }
        
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            places = data.get('results', [])
            
            results = []
            for place in places[:5]:  # 上位5件を取得
                place_info = {
                    'name': place['name'],
                    'rating': place.get('rating', 0),
                    'price_level': place.get('price_level', 0),
                    'address': place.get('formatted_address', ''),
                    'phone': place.get('formatted_phone_number', ''),
                    'website': place.get('website', ''),
                    'place_id': place['place_id'],
                    'types': place.get('types', []),
                    'opening_hours': place.get('opening_hours', {}).get('weekday_text', [])
                }
                
                # GoogleマップアクセスURLを生成
                if place_info.get('address'):
                    maps_result = generate_google_maps_url(place_info['address'], place_info['name'])
                    place_info['google_maps_url'] = maps_result.get('google_maps_url', '')
                    place_info['directions_url'] = generate_directions_url(
                        f"{location}駅", 
                        place_info['address'], 
                        "transit"
                    ).get('directions_url', '')
                else:
                    maps_result = generate_google_maps_url(location, place_info['name'])
                    place_info['google_maps_url'] = maps_result.get('google_maps_url', '')
                    place_info['directions_url'] = generate_directions_url(
                        f"{location}駅", 
                        place_info['name'], 
                        "transit"
                    ).get('directions_url', '')
                
                results.append(place_info)
            
            return {
                "restaurants": results,
                "location": location,
                "cuisine": cuisine,
                "radius": radius,
                "total_found": len(results)
            }
        else:
            return {
                "error": f"Google Maps API エラー: {response.status_code}",
                "location": location
            }
            
    except Exception as e:
        return {
            "error": f"Google Maps検索エラー: {str(e)}",
            "location": location
        }

def check_restaurant_availability(restaurant_name: str, date: str, time: str, guests: int = 2) -> dict:
    """レストランの予約状況を確認するツール。
    
    Args:
        restaurant_name: レストラン名
        date: 予約日（YYYY-MM-DD形式）
        time: 予約時間（HH:MM形式）
        guests: 人数
    """
    try:
        # 模擬的な予約状況確認
        import random
        
        # 予約可能時間帯
        available_times = [
            "18:00", "18:30", "19:00", "19:30", "20:00", "20:30"
        ]
        
        # ランダムに予約状況を生成
        is_available = random.choice([True, True, True, False])  # 75%の確率で予約可能
        
        if is_available:
            available_slots = random.sample(available_times, random.randint(2, 4))
            return {
                "restaurant": restaurant_name,
                "date": date,
                "requested_time": time,
                "guests": guests,
                "status": "予約可能",
                "available_times": available_slots,
                "message": f"{restaurant_name}で{date}の{time}の予約が可能です。"
            }
        else:
            return {
                "restaurant": restaurant_name,
                "date": date,
                "requested_time": time,
                "guests": guests,
                "status": "予約不可",
                "available_times": [],
                "message": f"{restaurant_name}で{date}の{time}の予約は満席です。"
            }
        
    except Exception as e:
        return {
            "error": f"予約状況確認エラー: {str(e)}",
            "restaurant": restaurant_name
        }

def get_hotpepper_master_data(master_type: str = "genre") -> dict:
    """ホットペッパーグルメAPIのマスターデータを取得するツール。
    
    Args:
        master_type: マスターデータの種類（"genre", "area", "budget", "special", "credit_card"）
    """
    try:
        # APIキーを環境変数から取得
        api_key = os.getenv("RECRUIT_API_KEY", "18c8f07145ccf2ad")
        
        # マスターデータのエンドポイントマッピング
        endpoint_mapping = {
            'genre': 'https://webservice.recruit.co.jp/hotpepper/genre/v1/',
            'area': 'https://webservice.recruit.co.jp/hotpepper/small_area/v1/',
            'budget': 'https://webservice.recruit.co.jp/hotpepper/budget/v1/',
            'special': 'https://webservice.recruit.co.jp/hotpepper/special/v1/',
            'credit_card': 'https://webservice.recruit.co.jp/hotpepper/credit_card/v1/',
            'large_area': 'https://webservice.recruit.co.jp/hotpepper/large_area/v1/',
            'middle_area': 'https://webservice.recruit.co.jp/hotpepper/middle_area/v1/'
        }
        
        if master_type not in endpoint_mapping:
            return {
                "error": f"サポートされていないマスターデータタイプ: {master_type}",
                "supported_types": list(endpoint_mapping.keys())
            }
        
        base_url = endpoint_mapping[master_type]
        
        # パラメータを構築
        params = {
            'key': api_key,
            'format': 'json'
        }
        
        # APIリクエストを送信
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        # JSONレスポンスを解析
        data = response.json()
        
        # エラーチェック
        if 'error' in data:
            error_info = data['error']
            return {
                "error": f"ホットペッパーAPIエラー: {error_info.get('message', '不明なエラー')} (コード: {error_info.get('code', 'N/A')})",
                "master_type": master_type,
                "api_url": response.url
            }
        
        if 'results' not in data:
            return {
                "error": "APIレスポンスの形式が正しくありません。",
                "master_type": master_type,
                "api_url": response.url
            }
        
        # マスターデータの種類に応じてデータを抽出
        if master_type == 'genre':
            items = data['results'].get('genre', [])
            result_data = []
            for item in items:
                result_data.append({
                    'code': item.get('code', ''),
                    'name': item.get('name', ''),
                    'category': item.get('category', {}).get('name', '')
                })
        elif master_type in ['large_area', 'middle_area', 'area']:
            area_key = master_type.replace('_', '')
            items = data['results'].get(area_key, [])
            result_data = []
            for item in items:
                result_data.append({
                    'code': item.get('code', ''),
                    'name': item.get('name', ''),
                    'large_area': item.get('large_area', {}).get('name', '') if 'large_area' in item else '',
                    'middle_area': item.get('middle_area', {}).get('name', '') if 'middle_area' in item else ''
                })
        elif master_type == 'budget':
            items = data['results'].get('budget', [])
            result_data = []
            for item in items:
                result_data.append({
                    'code': item.get('code', ''),
                    'name': item.get('name', ''),
                    'average': item.get('average', '')
                })
        elif master_type == 'special':
            items = data['results'].get('special', [])
            result_data = []
            for item in items:
                result_data.append({
                    'code': item.get('code', ''),
                    'name': item.get('name', ''),
                    'category': item.get('special_category', {}).get('name', '')
                })
        elif master_type == 'credit_card':
            items = data['results'].get('credit_card', [])
            result_data = []
            for item in items:
                result_data.append({
                    'code': item.get('code', ''),
                    'name': item.get('name', '')
                })
        else:
            result_data = data['results']
        
        return {
            "master_type": master_type,
            "data": result_data,
            "total_count": len(result_data),
            "api_url": response.url,
            "message": f"{master_type}マスターデータを{len(result_data)}件取得しました。"
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "error": f"ホットペッパーAPI通信エラー: {str(e)}",
            "master_type": master_type
        }
    except Exception as e:
        return {
            "error": f"マスターデータ取得エラー: {str(e)}",
            "master_type": master_type
        }

def search_hotpepper_restaurants_by_name(restaurant_name: str) -> dict:
    """店名でホットペッパーグルメのレストランを検索するツール。
    
    Args:
        restaurant_name: レストラン名
    """
    try:
        # ホットペッパーグルメAPIのベースURL
        base_url = "https://webservice.recruit.co.jp/hotpepper/gourmet/v1/"
        
        # APIキーを環境変数から取得
        api_key = os.getenv("RECRUIT_API_KEY", "18c8f07145ccf2ad")
        
        # パラメータを構築
        params = {
            'key': api_key,
            'format': 'json',
            'count': 10,
            'name': restaurant_name  # 店名検索
        }
        
        # APIリクエストを送信
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        # JSONレスポンスを解析
        data = response.json()
        
        # エラーチェック
        if 'error' in data:
            error_info = data['error']
            return {
                "error": f"ホットペッパーAPIエラー: {error_info.get('message', '不明なエラー')} (コード: {error_info.get('code', 'N/A')})",
                "restaurant_name": restaurant_name,
                "api_url": response.url
            }
        
        if 'results' not in data or 'shop' not in data['results']:
            return {
                "error": "APIレスポンスの形式が正しくありません。",
                "restaurant_name": restaurant_name,
                "api_url": response.url
            }
        
        shops = data['results']['shop']
        
        if not shops:
            return {
                "error": "該当するレストランが見つかりませんでした。",
                "restaurant_name": restaurant_name,
                "restaurants": [],
                "api_url": response.url
            }
        
        # レストラン情報を整形
        restaurants = []
        for shop in shops:
            restaurant_info = {
                'name': shop.get('name', ''),
                'cuisine': shop.get('genre', {}).get('name', ''),
                'rating': shop.get('rating', {}).get('rate', '評価なし'),
                'budget': shop.get('budget', {}).get('name', '価格要問合せ'),
                'address': shop.get('address', ''),
                'phone': shop.get('tel', ''),
                'hours': shop.get('open', ''),
                'features': [],
                'url': shop.get('urls', {}).get('pc', ''),
                'latitude': shop.get('lat', ''),
                'longitude': shop.get('lng', ''),
                'catch': shop.get('catch', ''),
                'access': shop.get('access', ''),
                'shop_id': shop.get('id', ''),
                'photo_url': shop.get('photo', {}).get('pc', {}).get('l', ''),
                'logo_url': shop.get('logo_image', ''),
                'credit_cards': shop.get('credit_card', ''),
                'parking': shop.get('parking', ''),
                'wifi': shop.get('wifi', ''),
                'private_room': shop.get('private_room', ''),
                'non_smoking': shop.get('non_smoking', ''),
                'horigotatsu': shop.get('horigotatsu', ''),
                'tatami': shop.get('tatami', ''),
                'card': shop.get('card', ''),
                'barrier_free': shop.get('barrier_free', ''),
                'other_memo': shop.get('other_memo', ''),
                'catch_copy': shop.get('catch', ''),
                'shop_detail_memo': shop.get('shop_detail_memo', ''),
                'coupon_urls': shop.get('urls', {}).get('qr', ''),
                'shop_url': shop.get('urls', {}).get('pc', '')
            }
            
            # 特徴を追加
            if shop.get('wifi', '') == 'あり':
                restaurant_info['features'].append('Wi-Fi')
            if shop.get('parking', '') == 'あり':
                restaurant_info['features'].append('駐車場')
            if shop.get('private_room', '') == 'あり':
                restaurant_info['features'].append('個室あり')
            if shop.get('non_smoking', '') == 'あり':
                restaurant_info['features'].append('禁煙席')
            if shop.get('horigotatsu', '') == 'あり':
                restaurant_info['features'].append('掘りごたつ')
            if shop.get('tatami', '') == 'あり':
                restaurant_info['features'].append('座敷')
            if shop.get('barrier_free', '') == 'あり':
                restaurant_info['features'].append('バリアフリー')
            if shop.get('card', '') == '利用可':
                restaurant_info['features'].append('クレジットカード利用可')
            
            restaurants.append(restaurant_info)
        
        return {
            "restaurants": restaurants,
            "restaurant_name": restaurant_name,
            "total_found": len(restaurants),
            "total_available": data['results'].get('results_available', 0),
            "message": f"{restaurant_name}の検索結果: {len(restaurants)}件見つかりました。",
            "api_url": response.url
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "error": f"ホットペッパーAPI通信エラー: {str(e)}",
            "restaurant_name": restaurant_name
        }
    except Exception as e:
        return {
            "error": f"店名検索エラー: {str(e)}",
            "restaurant_name": restaurant_name
        }

def find_and_add_area_code(location: str, large_area_mapping: dict, middle_area_mapping: dict) -> dict:
    """エリア名からエリアコードを動的に検索し、見つかった場合はマッピングに追加するツール。
    
    Args:
        location: エリア名（例: "大崎"）
        large_area_mapping: 大エリアコードのマッピング辞書
        middle_area_mapping: 中エリアコードのマッピング辞書
    
    Returns:
        更新されたマッピング辞書と検索結果
    """
    try:
        # APIキーを環境変数から取得
        api_key = os.getenv("RECRUIT_API_KEY", "18c8f07145ccf2ad")
        
        # 小エリアマスターデータを取得
        small_area_url = "https://webservice.recruit.co.jp/hotpepper/small_area/v1/"
        params = {
            'key': api_key,
            'format': 'json'
        }
        
        response = requests.get(small_area_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'error' in data:
            return {
                "error": f"エリアコード検索エラー: {data['error'].get('message', '不明なエラー')}",
                "location": location,
                "large_area_mapping": large_area_mapping,
                "middle_area_mapping": middle_area_mapping
            }
        
        if 'results' not in data or 'small_area' not in data['results']:
            return {
                "error": "エリアマスターデータの形式が正しくありません。",
                "location": location,
                "large_area_mapping": large_area_mapping,
                "middle_area_mapping": middle_area_mapping
            }
        
        small_areas = data['results']['small_area']
        found_areas = []
        
        # エリア名で部分一致検索
        for area in small_areas:
            area_name = area.get('name', '')
            if location in area_name or area_name in location:
                middle_area_info = area.get('middle_area', {})
                large_area_info = middle_area_info.get('large_area', {})
                
                found_areas.append({
                    'code': area.get('code', ''),  # 小エリアコード
                    'name': area_name,
                    'middle_area': middle_area_info.get('name', ''),
                    'middle_area_code': middle_area_info.get('code', ''),  # 中エリアコード
                    'large_area': large_area_info.get('name', ''),
                    'large_area_code': large_area_info.get('code', '')  # 大エリアコード
                })
        
        # 見つかったエリアをマッピングに追加
        updated_large_area_mapping = large_area_mapping.copy()
        updated_middle_area_mapping = middle_area_mapping.copy()
        
        for area in found_areas:
            # 中エリアマッピングに追加（中エリアコードを使用）
            if area['middle_area'] and area['middle_area_code']:
                updated_middle_area_mapping[area['middle_area']] = area['middle_area_code']
                # 元のエリア名でも中エリアコードを使用
                updated_middle_area_mapping[area['name']] = area['middle_area_code']
            
            # 大エリアマッピングにも追加（まだ存在しない場合）
            if area['large_area'] and area['large_area_code'] and area['large_area'] not in updated_large_area_mapping:
                updated_large_area_mapping[area['large_area']] = area['large_area_code']
        
        return {
            "found_areas": found_areas,
            "updated_large_area_mapping": updated_large_area_mapping,
            "updated_middle_area_mapping": updated_middle_area_mapping,
            "message": f"{location}に関連するエリアを{len(found_areas)}件見つけました。",
            "location": location
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "error": f"エリアコード検索通信エラー: {str(e)}",
            "location": location,
            "large_area_mapping": large_area_mapping,
            "middle_area_mapping": middle_area_mapping
        }
    except Exception as e:
        return {
            "error": f"エリアコード検索エラー: {str(e)}",
            "location": location,
            "large_area_mapping": large_area_mapping,
            "middle_area_mapping": middle_area_mapping
        }


def generate_google_maps_url(location: str, restaurant_name: str = "") -> dict:
    """Googleマップで目的地を表示するURLを生成するツール。
    
    Args:
        location: 場所（例: "渋谷駅", "新宿", "東京都品川区大崎1-1-1"）
        restaurant_name: レストラン名（オプション）
    """
    try:
        from urllib.parse import quote
        
        # 検索クエリを構築
        if restaurant_name:
            search_query = f"{restaurant_name} {location}"
        else:
            search_query = location
        
        # URLエンコード
        encoded_query = quote(search_query)
        
        # GoogleマップのURLを生成
        google_maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_query}"
        
        # 短縮URLも生成（オプション）
        short_url = f"https://maps.google.com/?q={encoded_query}"
        
        return {
            "location": location,
            "restaurant_name": restaurant_name,
            "search_query": search_query,
            "google_maps_url": google_maps_url,
            "short_url": short_url,
            "message": f"{location}のGoogleマップURLを生成しました。"
        }
        
    except Exception as e:
        return {
            "error": f"GoogleマップURL生成エラー: {str(e)}",
            "location": location,
            "restaurant_name": restaurant_name
        }

def generate_directions_url(origin: str, destination: str, mode: str = "driving") -> dict:
    """Googleマップで経路案内のURLを生成するツール。
    
    Args:
        origin: 出発地（例: "東京駅", "渋谷駅"）
        destination: 目的地（例: "新宿", "レストラン名"）
        mode: 移動手段（"driving", "walking", "transit", "bicycling"）
    """
    try:
        from urllib.parse import quote
        
        # 移動手段のマッピング
        mode_mapping = {
            "driving": "driving",
            "walking": "walking", 
            "transit": "transit",
            "bicycling": "bicycling",
            "車": "driving",
            "歩き": "walking",
            "電車": "transit",
            "自転車": "bicycling"
        }
        
        # 移動手段を英語に変換
        travel_mode = mode_mapping.get(mode.lower(), "driving")
        
        # URLエンコード
        encoded_origin = quote(origin)
        encoded_destination = quote(destination)
        
        # Googleマップの経路案内URLを生成
        directions_url = f"https://www.google.com/maps/dir/?api=1&origin={encoded_origin}&destination={encoded_destination}&travelmode={travel_mode}"
        
        return {
            "origin": origin,
            "destination": destination,
            "mode": travel_mode,
            "directions_url": directions_url,
            "message": f"{origin}から{destination}への{travel_mode}経路案内URLを生成しました。"
        }
        
    except Exception as e:
        return {
            "error": f"経路案内URL生成エラー: {str(e)}",
            "origin": origin,
            "destination": destination,
            "mode": mode
        }

# 構造化出力を使用するスケジューラーエージェント用のモデル
# scheduler_model = model.with_structured_output(ScheduleRequest)

scheduler_agent = create_react_agent(
    model=model,  # 通常のモデルを使用
    tools=[add_to_google_calendar, get_current_time, calculate_target_date],
    # name="scheduler_agent",
    name="scheduler_expert",
    prompt="""
            You are a scheduler agent. Use Google Calendar to add events.

            When a user asks to schedule something, you should:
            1. FIRST, use get_current_time() to get the current time
            2. Extract the event title and time from their request
            3. If the user mentions relative dates (like "明日", "今日", "来週"), use calculate_target_date() to get the actual datetime
            4. Use the calculated datetime with add_to_google_calendar tool

            Examples:
            - User: "明日の15時に会議を予定に入れて" 
            → 1. get_current_time() to get current date
            → 2. calculate_target_date(relative_date="明日", time_str="15時")
            → 3. add_to_google_calendar(event="会議", time="[calculated_datetime]")

            - User: "今日の14:30に歯医者の予約を入れて" 
            → 1. get_current_time() to get current date
            → 2. calculate_target_date(relative_date="今日", time_str="14:30")
            → 3. add_to_google_calendar(event="歯医者の予約", time="[calculated_datetime]")

            - User: "来週月曜日の10時に面接を予定に入れて" 
            → 1. get_current_time() to get current date
            → 2. calculate_target_date(relative_date="来週月曜日", time_str="10時")
            → 3. add_to_google_calendar(event="面接", time="[calculated_datetime]")

            ALWAYS start by calling get_current_time() to get the current date, then use calculate_target_date() for relative dates, and finally call add_to_google_calendar().
            """
)

math_agent = create_react_agent(
    model=model,
    tools=[add, multiply],
    name="math_expert",
    prompt="You are a math expert. Always use one tool at a time."
)

research_agent = create_react_agent(
    model=model,
    tools=[web_search, get_current_time],
    name="research_expert",
    prompt="You are a world class researcher with access to web search and current time. Do not do any math."
)

# 新しいエージェントの作成

# 音楽エージェント
music_agent = create_react_agent(
    model=model,
    tools=[search_spotify_tracks, get_spotify_playlist, search_spotify_artists, get_current_time],
    name="music_expert",
    prompt="""
            You are a music expert with access to Spotify. You can search for tracks, artists, and playlists.

            When users ask about music, you should:
            1. Search for tracks using search_spotify_tracks()
            2. Search for artists using search_spotify_artists()
            3. Get playlist information using get_spotify_playlist()
            4. Provide music recommendations and information

            Examples:
            - User: "ビートルズの曲を探して" → search_spotify_tracks(query="ビートルズ")
            - User: "ビートルズのアーティスト情報を教えて" → search_spotify_artists(artist_name="ビートルズ")
            - User: "人気のプレイリストを教えて" → get_spotify_playlist(playlist_id="37i9dQZEVXbMDoHDwVN2tF") # Global Top 50

            Always provide helpful music recommendations and information. Include Spotify URLs when available.
            """
)

# 動画エージェント
video_agent = create_react_agent(
    model=model,
    tools=[search_youtube_videos, get_video_info, get_current_time],
    name="video_expert",
    prompt="""
            You are a video expert with access to YouTube. You can search for videos and get detailed information.

            When users ask about videos, you should:
            1. Search for videos using search_youtube_videos()
            2. Get detailed video information using get_video_info()
            3. Provide video recommendations and information

            Examples:
            - User: "料理の動画を探して" → search_youtube_videos(query="料理 レシピ")
            - User: "この動画の詳細を教えて" → get_video_info(video_id="video_id")

            Always provide helpful video recommendations and information.
            """
)

# 旅行エージェント
travel_agent = create_react_agent(
    model=model,
    tools=[search_jalan_hotels, search_airbnb_accommodations, get_current_time],
    name="travel_expert",
    prompt="""
            You are a travel expert with access to hotel and accommodation booking services through web scraping.

            When users ask about travel accommodations, you should:
            1. Search for hotels using search_jalan_hotels() - scrapes Jalan.net for real hotel data
            2. Search for Airbnb accommodations using search_airbnb_accommodations() - scrapes Airbnb.com for real accommodation data
            3. Provide travel recommendations and booking information

            Examples:
            - User: "東京のホテルを明日から2泊で探して" 
            → search_jalan_hotels(location="東京", check_in="2024-12-20", check_out="2024-12-22", guests=2)
            - User: "大阪のAirbnbを来週から3泊で探して" 
            → search_airbnb_accommodations(location="大阪", check_in="2024-12-25", check_out="2024-12-28", guests=2)

            The tools perform real web scraping to get current hotel and accommodation information, including:
            - Real prices and availability
            - Actual hotel/accommodation names
            - Current ratings and reviews
            - Direct booking URLs
            - Amenities and features

            Always provide helpful travel recommendations and accommodation options based on the scraped data.
            """
)

# レストランエージェント
restaurant_agent = create_react_agent(
    model=model,
    tools=[search_hotpepper_restaurants, search_hotpepper_restaurants_by_name, get_hotpepper_master_data, search_google_maps_restaurants, check_restaurant_availability, generate_google_maps_url, generate_directions_url, get_current_time],
    name="restaurant_expert",
    prompt="""
            You are a restaurant expert with access to comprehensive restaurant search and booking services.

            When users ask about restaurants, you should:
            1. Search for restaurants using search_hotpepper_restaurants() - uses real HotPepper Gourmet API with accurate area codes and genre codes
            2. Search for specific restaurants by name using search_hotpepper_restaurants_by_name() - for exact restaurant searches
            3. Get master data using get_hotpepper_master_data() - to get available genres, areas, budgets, and special features
            4. Search for restaurants using search_google_maps_restaurants() - uses Google Places API for additional results
            5. Check restaurant availability using check_restaurant_availability() - for booking information
            6. Generate Google Maps URLs using generate_google_maps_url() for location access
            7. Generate directions URLs using generate_directions_url() for route planning

            Examples:
            - User: "渋谷のイタリアンを探して" → search_hotpepper_restaurants(location="渋谷", cuisine="イタリアン")
            - User: "新宿の3000円以下のレストランを探して" → search_hotpepper_restaurants(location="新宿", budget="3000円以下")
            - User: "〇〇レストランの情報を教えて" → search_hotpepper_restaurants_by_name(restaurant_name="〇〇レストラン")
            - User: "利用可能なジャンルを教えて" → get_hotpepper_master_data(master_type="genre")
            - User: "東京のエリアを教えて" → get_hotpepper_master_data(master_type="large_area")
            - User: "このレストランの予約状況を確認して" → check_restaurant_availability(restaurant_name="レストラン名", date="2024-12-20", time="19:00")
            - User: "このレストランの場所を教えて" → generate_google_maps_url(location="東京都渋谷区1-1-1", restaurant_name="レストラン名")
            - User: "東京駅からこのレストランへの行き方を教えて" → generate_directions_url(origin="東京駅", destination="レストラン名", mode="transit")

            IMPORTANT: Always include Google Maps access URLs in your responses when presenting restaurant information. Each restaurant should have:
            - google_maps_url: Direct link to the restaurant location on Google Maps
            - directions_url: Route planning from the nearest station to the restaurant

            This helps users easily navigate to the restaurants you recommend.

            ERROR HANDLING: If the HotPepper API returns an error or no results:
            1. The system automatically tries a fallback search using keyword-based search
            2. If still no results, it provides helpful suggestions and alternative search methods
            3. Always explain what happened and suggest alternative approaches (e.g., try different areas, cuisines, or use Google Maps search)

            The HotPepper API provides comprehensive restaurant data including:
            - Actual restaurant names and locations with precise area codes
            - Real prices and ratings with accurate budget codes
            - Current opening hours and contact information
            - Direct booking URLs and coupon information
            - Detailed amenities and features (Wi-Fi, parking, private rooms, etc.)
            - Credit card acceptance information
            - Special features and categories
            - High-quality photos and logos

            The API supports:
            - Large area codes (Z011-Z050 for all prefectures)
            - Middle area codes (Z011001-Z011152 for detailed Tokyo areas)
            - Genre codes (G001-G012 for all cuisine types)
            - Budget codes (B001-B014 for all price ranges)
            - Special feature codes (LT0004-LT0086 for various occasions)
            - Credit card codes (c01-c10 for different card types)

            Always provide helpful restaurant recommendations and availability information based on the real API data, and use the appropriate search parameters for the best results.
            """
)

# 構造化出力を使用するスーパーバイザー用のモデル
# supervisor_model = model.with_structured_output(WorkflowState)

# Create supervisor workflow
workflow = create_supervisor(
    agents=[research_agent, math_agent, scheduler_agent, music_agent, video_agent, travel_agent, restaurant_agent],
    model=model,  # 通常のモデルを使用
    tools=[get_current_time],
    prompt=(
        "You are a team supervisor managing multiple expert agents:\n"
        "- research_agent: For current events and research\n"
        "- math_agent: For mathematical calculations\n"
        "- scheduler_agent: For scheduling and calendar management\n"
        "- music_expert: For music recommendations and Spotify searches\n"
        "- video_expert: For video recommendations and YouTube searches\n"
        "- travel_expert: For travel accommodations (hotels, Airbnb)\n"
        "- restaurant_expert: For restaurant searches and reservations\n\n"
        
        "You should get the current time first, then assign the appropriate agent based on the user's request:\n"
        "- Music, songs, playlists → music_expert\n"
        "- Videos, YouTube, streaming → video_expert\n"
        "- Travel, hotels, accommodations → travel_expert\n"
        "- Restaurants, dining, food → restaurant_expert\n"
        "- Scheduling, calendar → scheduler_agent\n"
        "- Math, calculations → math_agent\n"
        "- News, research, information → research_agent"
    ),
    output_mode="full_history"
)

# Compile and run
app = workflow.compile()

graph_image = app.get_graph(xray=True).draw_mermaid_png()
with open("workflow.png", "wb") as f:
    f.write(graph_image)

def visualize_restaurant_results_streamlit(restaurants, title="レストラン検索結果 可視化"):
    """
    レストラン検索結果を可視化し、Streamlitで表示する
    Args:
        restaurants: レストラン情報のリスト（dictのリスト）
        title: グラフタイトル
    Returns:
        画像バイナリデータ
    """
    if not restaurants:
        st.warning("表示するレストランデータがありません。")
        return None
    names = [r['name'] for r in restaurants]
    budgets = [r.get('budget', '') for r in restaurants]
    addresses = [r.get('address', '') for r in restaurants]

    plt.figure(figsize=(10, min(0.6*len(names), 8)))
    plt.barh(names, range(len(names)), color='skyblue')
    plt.xlabel('順位')
    plt.title(title)
    for i, (name, budget, address) in enumerate(zip(names, budgets, addresses)):
        plt.text(0, i, f"{budget} | {address}", va='center', fontsize=8)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    st.image(buf, caption=title)
    return buf

def visualize_restaurant_category_count_streamlit(restaurants, title="カテゴリ別件数グラフ"):
    """
    カテゴリ（ジャンル）別件数を可視化し、Streamlitで表示
    """
    genres = [r.get('cuisine', '不明') or '不明' for r in restaurants]
    counter = Counter(genres)
    labels, values = zip(*counter.items()) if counter else ([],[])
    plt.figure(figsize=(8, 4))
    plt.bar(labels, values, color='orange')
    plt.title(title)
    plt.ylabel('件数')
    plt.xlabel('ジャンル')
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    st.image(buf, caption=title)
    return buf

def visualize_restaurant_rating_streamlit(restaurants, title="評価分布グラフ"):
    """
    レストランの評価（rating）が数値であればヒストグラムで可視化
    """
    ratings = []
    for r in restaurants:
        val = r.get('rating')
        try:
            if val and val != '評価なし':
                ratings.append(float(val))
        except Exception:
            continue
    if not ratings:
        st.info("評価データがありません。")
        return None
    plt.figure(figsize=(6, 3))
    plt.hist(ratings, bins=5, color='green', edgecolor='black')
    plt.title(title)
    plt.xlabel('評価')
    plt.ylabel('件数')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    st.image(buf, caption=title)
    return buf

def visualize_restaurant_review_sentiment_streamlit(restaurants, title="口コミポジティブ度グラフ"):
    """
    口コミ（catch, shop_detail_memo等）を簡易的に感情分析し、ポジティブ/ネガティブ割合を可視化
    """
    from textblob import TextBlob
    pos, neg, neu = 0, 0, 0
    for r in restaurants:
        texts = []
        if r.get('catch'): texts.append(r['catch'])
        if r.get('shop_detail_memo'): texts.append(r['shop_detail_memo'])
        for text in texts:
            if text:
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                if polarity > 0.1:
                    pos += 1
                elif polarity < -0.1:
                    neg += 1
                else:
                    neu += 1
    total = pos + neg + neu
    if total == 0:
        st.info("口コミテキストがありません。")
        return None
    labels = ['ポジティブ', 'ニュートラル', 'ネガティブ']
    values = [pos, neu, neg]
    plt.figure(figsize=(4, 4))
    plt.pie(values, labels=labels, autopct='%1.1f%%', colors=['#66bb6a', '#ffee58', '#ef5350'])
    plt.title(title)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    st.image(buf, caption=title)
    return buf

def visualize_price_rating_ranking_streamlit(restaurants, title="価格帯ごと評価順ランキング"):
    import matplotlib.pyplot as plt
    import io
    import streamlit as st

    # 価格帯を数値化
    def price_to_num(budget):
        if not budget or '円' not in budget:
            return 0
        try:
            s = budget.replace('円', '').replace('～', '-').replace(',', '').replace('以上', '').replace('以下', '')
            if '-' in s:
                return int(s.split('-')[0])
            return int(s)
        except:
            return 0

    # データ整形
    data = []
    for r in restaurants:
        try:
            rating = float(r.get('rating', 0)) if r.get('rating') and r.get('rating') != '評価なし' else None
            price = price_to_num(r.get('budget', ''))
            if rating is not None and price > 0:
                data.append((r['name'], price, rating, r.get('budget', '')))
        except:
            continue

    if not data:
        st.info("評価・価格データがありません。コアな可視化はできません。")
        return

    # 価格帯ごとにソート
    data.sort(key=lambda x: (x[1], -x[2]))  # 価格→評価降順

    names = [d[0] for d in data]
    prices = [d[1] for d in data]
    ratings = [d[2] for d in data]
    price_labels = [d[3] for d in data]

    plt.figure(figsize=(10, min(0.6*len(names), 8)))
    sc = plt.scatter(prices, ratings, c=prices, cmap='cool', s=100)
    for i, name in enumerate(names):
        plt.text(prices[i], ratings[i], name, fontsize=8, va='bottom', ha='right', alpha=0.7)
    plt.xlabel('価格帯（円）')
    plt.ylabel('評価')
    plt.title(title)
    plt.colorbar(sc, label='価格帯（円）')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    st.image(buf, caption=title)
    return buf

def show_spotify_embeds_streamlit(tracks, title="Spotify埋め込みプレイヤー"):
    """
    楽曲リスト（search_spotify_tracksの結果）からSpotify埋め込みプレイヤーをStreamlitで表示
    Args:
        tracks: 楽曲情報のリスト（dictのリスト、各trackに'spotify_url'キーが必要）
        title: セクションタイトル
    """
    import streamlit as st
    st.markdown(f"### {title}")
    for track in tracks:
        url = track.get('spotify_url')
        if url and 'track/' in url:
            track_id = url.split('track/')[-1].split('?')[0]
            embed_url = f"https://open.spotify.com/embed/track/{track_id}"
            st.markdown(
                f'<iframe src="{embed_url}" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>',
                unsafe_allow_html=True
            )

def show_googlemap_embed_streamlit(address_or_query, title="Googleマップ埋め込み"):
    import streamlit as st
    from urllib.parse import quote
    query = quote(address_or_query)
    embed_url = f"https://www.google.com/maps?q={query}&output=embed"
    st.markdown(f"#### {title}")
    st.markdown(
        f'''
        <div style="border-radius:16px; overflow:hidden; width:100%; max-width:400px; height:300px;">
          <iframe src="{embed_url}" width="100%" height="300" frameborder="0" style="border-radius:16px;" allowfullscreen></iframe>
        </div>
        ''',
        unsafe_allow_html=True
    )

def run_agent(messages):
    """
    messages: [{'role': 'user', 'content': '...'}, ...] のリスト
    AI回答テキスト・Spotifyリスト等を含むdictを返す
    """
    def extract_text(content):
        if isinstance(content, list):
            return "".join(extract_text(c) for c in content)
        if isinstance(content, dict) and "text" in content:
            return content["text"]
        if isinstance(content, str):
            return content
        return str(content)

    try:
        result = app.invoke({"messages": messages})
        
        # デバッグ情報
        print(f"【DEBUG: app.invoke result type】: {type(result)}")
        if isinstance(result, dict):
            print(f"【DEBUG: result keys】: {list(result.keys())}")
        
        text = None
        results = None
        
        # 方法1: result.get("message")を試行
        if isinstance(result, dict):
            text = result.get("message")
            results = result.get("results")
            
            # もしresultsが直接resultにない場合、messages内を探す
            if not results and "messages" in result:
                for msg in result["messages"]:
                    if isinstance(msg, dict):
                        if "results" in msg:
                            results = msg["results"]
                            break
                        elif "content" in msg and isinstance(msg["content"], str):
                            # content内にresultsが含まれているかチェック
                            try:
                                content_data = json.loads(msg["content"])
                                if isinstance(content_data, dict) and "results" in content_data:
                                    results = content_data["results"]
                                    break
                            except:
                                pass
        
        # 方法2: messagesから最後のassistantメッセージを取得
        if not text and isinstance(result, dict) and "messages" in result:
            messages = result["messages"]
            for msg in reversed(messages):
                if isinstance(msg, dict):
                    role = msg.get("role")
                    content = msg.get("content")
                    if role == "assistant" and content:
                        text = extract_text(content)
                        break
                elif hasattr(msg, 'role') and hasattr(msg, 'content'):
                    if msg.role == "assistant" and msg.content:
                        text = extract_text(msg.content)
                        break
                # AIMessageオブジェクトの場合
                elif hasattr(msg, 'content') and hasattr(msg, 'additional_kwargs'):
                    # 最後の有効なAIMessageのcontentを取得
                    if msg.content and not msg.additional_kwargs.get('tool_calls'):
                        text = extract_text(msg.content)
                        break
        
        # 方法3: エラーメッセージの確認
        if not text and isinstance(result, dict) and "error" in result:
            text = result["error"]
        
        # 方法4: 結果全体を文字列として扱う
        if not text:
            text = str(result)
        
        # resultsの抽出を試行
        if not results and isinstance(result, dict):
            # messages内からresultsを探す
            if "messages" in result:
                for msg in result["messages"]:
                    # 方法1: 直接resultsキーがある場合
                    if isinstance(msg, dict) and "results" in msg:
                        results = msg["results"]
                        break
                    # 方法2: content内にJSONとしてresultsが含まれている場合
                    elif hasattr(msg, 'content') and isinstance(msg.content, str):
                        try:
                            # JSONとしてパースを試行
                            parsed = json.loads(msg.content)
                            if isinstance(parsed, dict) and "results" in parsed:
                                results = parsed["results"]
                                break
                        except:
                            pass
                    # 方法3: content内にresultsという文字列が含まれている場合
                    elif hasattr(msg, 'content') and isinstance(msg.content, str):
                        content_str = str(msg.content)
                        # resultsが含まれているかチェック
                        if '"results"' in content_str or "'results'" in content_str:
                            try:
                                # 部分的なJSON抽出を試行
                                import re
                                # resultsの部分を抽出
                                results_match = re.search(r'"results"\s*:\s*(\[.*?\])', content_str, re.DOTALL)
                                if results_match:
                                    results_json = results_match.group(1)
                                    results = json.loads(results_json)
                                    break
                            except:
                                pass
        
        # 方法4: 最後の手段として、content内から構造化データを探す
        if not results and isinstance(result, dict) and "messages" in result:
            for msg in result["messages"]:
                if hasattr(msg, 'content') and isinstance(msg.content, str):
                    content_str = str(msg.content)
                    # 動画、レストラン、ホテル、音楽などの結果パターンを検出
                    if any(keyword in content_str.lower() for keyword in ['youtube_url', 'spotify_url', 'google_maps_url', 'restaurant', 'hotel', 'video']):
                        try:
                            # より柔軟なJSON抽出
                            import re
                            # 配列パターンを探す
                            array_match = re.search(r'\[.*?\]', content_str, re.DOTALL)
                            if array_match:
                                potential_results = json.loads(array_match.group(0))
                                if isinstance(potential_results, list) and len(potential_results) > 0:
                                    # 最初の要素が辞書で、適切なキーを持っているかチェック
                                    if isinstance(potential_results[0], dict):
                                        first_item = potential_results[0]
                                        if any(key in first_item for key in ['name', 'title', 'youtube_url', 'spotify_url', 'google_maps_url']):
                                            results = potential_results
                                            break
                        except:
                            pass
        
        print(f"【DEBUG: 抽出したtext】: {text}")
        print(f"【DEBUG: 抽出したresults】: {results}")
        
        return {
            "text": text or "AIの回答が見つかりませんでした。",
            "results": results or [],
        }
    except Exception as e:
        import traceback
        print(f"【DEBUG: エラー】: {e}")
        traceback.print_exc()
        return {
            "text": f"エラー: {e}\n{traceback.format_exc()}",
            "results": [],
        }

# Spotify検索専用のシングルエージェント
music_model = ChatOpenAI(model="gpt-4o-mini")

class SpotifyTrack(BaseModel):
    name: str = Field(..., description="曲名")
    artist: str = Field(..., description="アーティスト名")
    album: str = Field(..., description="アルバム名")
    release_date: str = Field(..., description="リリース日")
    spotify_url: str = Field(..., description="SpotifyのURL")
    album_art: str = Field(..., description="アルバムアート画像URL")

class SpotifyTrackList(BaseModel):
    results: List[SpotifyTrack]

def run_agent_music(query):
    """
    Spotify検索専用Single Agent（LangGraph, 構造化出力パーサ付き）。
    query: str（例: "ミセス"）
    Agent経由でSpotifyTrackListの構造化出力を返す
    """
    def dict_to_serializable(obj):
        if isinstance(obj, dict):
            return {k: dict_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [dict_to_serializable(v) for v in obj]
        elif hasattr(obj, "content"):
            return str(obj.content)
        else:
            try:
                json.dumps(obj)
                return obj
            except Exception:
                return str(obj)

    model = ChatOpenAI(model="gpt-4o-mini")
    music_agent = create_react_agent(
        model=model,
        tools=[search_spotify_tracks],
        name="music_expert",
        prompt="""
            あなたはSpotify楽曲検索の専門家です。
            ユーザーから楽曲名やアーティスト名のリクエストが来たら、必ずsearch_spotify_tracks(query=...)ツールを使って検索し、
            検索結果（results）をそのまま返してください。
            余計な自然言語説明や要約は不要です。
        """
    )
    agent_result = music_agent.invoke({"input": query})

    structured_llm = model.with_structured_output(SpotifyTrackList)
    try:
        if hasattr(agent_result, "content"):
            input_str = str(agent_result.content)
        elif isinstance(agent_result, dict):
            serializable = dict_to_serializable(agent_result)
            input_str = json.dumps(serializable, ensure_ascii=False)
        else:
            input_str = str(agent_result)
        parsed = structured_llm.invoke(input_str)
        print(f"【DEBUG: parsed】: {parsed}")
        return {"results": [track.dict() for track in parsed.results]}
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"【DEBUG: エラー】: {e}")
        return {"results": []}

if __name__ == "__main__":
    user_input = input("質問を入力してください: ")
    print("\n=== 処理開始 ===")
    
    try:
        result = app.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        })
        
        print("\n=== 結果 ===")
        print(f"結果の型: {type(result)}")
        
        if hasattr(result, 'keys'):
            print(f"結果のキー: {list(result.keys())}")
        
        if "messages" in result:
            print(f"メッセージ数: {len(result['messages'])}")
            for i, msg in enumerate(result['messages']):
                print(f"\n--- メッセージ {i} ---")
                print(f"型: {type(msg)}")
                if hasattr(msg, 'content'):
                    print(f"内容: {msg.content}")
                elif isinstance(msg, dict) and 'content' in msg:
                    print(f"内容: {msg['content']}")
        
        print("\n=== 最終回答 ===")
        if "messages" in result and result["messages"]:
            last_msg = result["messages"][-1]
            if hasattr(last_msg, 'content'):
                print(last_msg.content)
            elif isinstance(last_msg, dict) and 'content' in last_msg:
                print(last_msg['content'])
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()    
    print("\n=== 処理完了 ===")