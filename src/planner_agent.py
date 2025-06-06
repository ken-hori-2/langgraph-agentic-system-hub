# Create server parameters for stdio connection
# from mcp import ClientSession, StdioServerParameters
# from mcp.client.stdio import stdio_client

# from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

async def main():
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # クライアントを初期化
    client = MultiServerMCPClient(
        {
            "spotify": {
                "command": "python",
                "args": ["mcp_server_spotify.py"],
                "env": {
                    "SPOTIFY_USER_ID": os.getenv("SPOTIFY_USER_ID"),
                    "SPOTIFY_TOKEN": os.getenv("SPOTIFY_TOKEN"),
                    "PYTHONIOENCODING": "utf-8"
                },
                "transport": "stdio"
            },
            "tavily": {
                "command": "python",
                "args": ["mcp_server_search.py"],
                "env": {
                    "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY"),
                    "PYTHONIOENCODING": "utf-8"
                },
                "transport": "stdio"
            },
            "time": {
                "command": "python",
                "args": ["mcp_server_time.py"],
                "env": {
                    "PYTHONIOENCODING": "utf-8"
                },
                "transport": "stdio"
            },
            
            
            # "my_tool": {
            # # "transport": "http",
            # "transport": "streamable_http",
            # "base_url": "http://127.0.0.1:8005" # /mcp"
            # }
        }
    )

    # ツールを取得
    tools = await client.get_tools()

    # エージェントの作成と実行
    agent = create_react_agent(model, tools)
    
    print("AIアシスタントが起動しました。終了するには 'quit' または 'exit' と入力してください。")
    print("利用可能な機能:")
    print("- Spotifyでの音楽検索")
    print("- Web検索（Tavily）")
    print("- 現在時刻の取得")
    
    while True:
        # ユーザーからの入力を取得
        user_input = input("\n質問を入力してください: ").strip()
        
        # 終了コマンドの確認
        if user_input.lower() in ['quit', 'exit']:
            print("AIアシスタントを終了します。")
            break
        
        # 空の入力をスキップ
        if not user_input:
            continue
        
        try:
            # エージェントの応答を取得
            agent_response = await agent.ainvoke({"messages": user_input})
            
            # メッセージの履歴を表示
            for message in agent_response["messages"]:
                if hasattr(message, 'content') and isinstance(message, AIMessage):
                    print("\n回答:", message.content)
        except Exception as e:
            print(f"\nエラーが発生しました: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())