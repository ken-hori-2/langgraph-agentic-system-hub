from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv
from tavily import TavilyClient

# 環境変数の読み込み
load_dotenv()

# MCPサーバーの初期化
mcp = FastMCP("TavilySearch")

# Tavily APIクライアントの初期化
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

@mcp.tool()
async def search(query: str, search_depth: str = "advanced") -> str:
    """指定されたクエリでWeb検索を実行します。
    
    Args:
        query: 検索クエリ
        search_depth: 検索の深さ（"basic" または "advanced"）
    """
    try:
        response = tavily_client.search(
            query=query,
            search_depth=search_depth,
            include_answer=True,
            include_raw_content=True
        )
        
        # 検索結果を整形
        results = []
        if response.get("answer"):
            results.append(f"回答: {response['answer']}")
        
        if response.get("results"):
            results.append("\n検索結果:")
            for i, result in enumerate(response["results"], 1):
                results.append(f"\n{i}. {result['title']}")
                results.append(f"   URL: {result['url']}")
                if result.get("content"):
                    results.append(f"   {result['content'][:200]}...")
        
        return "\n".join(results)
    except Exception as e:
        return f"検索中にエラーが発生しました: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
    # mcp.run(transport="http", host="127.0.0.1", port=8001) 