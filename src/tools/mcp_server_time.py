from mcp.server.fastmcp import FastMCP
from datetime import datetime
import pytz

mcp = FastMCP("TimeServer")

@mcp.tool()
async def get_current_time(timezone: str = "Asia/Tokyo") -> str:
    """現在の日時を取得します。
    
    Args:
        timezone: タイムゾーン（デフォルト: Asia/Tokyo）
    """
    try:
        # 指定されたタイムゾーンを取得
        tz = pytz.timezone(timezone)
        # 現在時刻を取得して指定されたタイムゾーンに変換
        current_time = datetime.now(tz)
        
        # 日時を整形
        formatted_time = current_time.strftime("%Y年%m月%d日 %H時%M分%S秒")
        return f"現在の時刻（{timezone}）: {formatted_time}"
    except pytz.exceptions.UnknownTimeZoneError:
        return f"エラー: 不明なタイムゾーン '{timezone}' が指定されました。"
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
    # mcp.run(transport="http", host="127.0.0.1", port=8002) 