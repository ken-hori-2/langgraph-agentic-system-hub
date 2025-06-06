from langchain_core.messages import AIMessage
import asyncio

async def mock_main():
    print("モックのmain関数が呼び出されました")
    
    # モックのツールを定義
    mock_tools = [
        {
            "name": "spotify_search",
            "description": "Spotifyで音楽を検索します",
            "mock_function": lambda x: print(f"Spotify検索が呼び出されました: {x}")
        },
        {
            "name": "web_search",
            "description": "Web検索を実行します",
            "mock_function": lambda x: print(f"Web検索が呼び出されました: {x}")
        },
        {
            "name": "get_current_time",
            "description": "現在時刻を取得します",
            "mock_function": lambda: print("現在時刻の取得が呼び出されました")
        }
    ]
    
    print("AIアシスタントが起動しました。終了するには 'quit' または 'exit' と入力してください。")
    print("利用可能な機能:")
    print("- Spotifyでの音楽検索")
    print("- Web検索（Tavily）")
    print("- 現在時刻の取得")
    
    while True:
        user_input = input("\n質問を入力してください: ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            print("AIアシスタントを終了します。")
            break
        
        if not user_input:
            continue
        
        try:
            # 入力に応じて適切なモック関数を呼び出す
            if "spotify" in user_input.lower() or "音楽" in user_input:
                mock_tools[0]["mock_function"](user_input)
            elif "検索" in user_input:
                mock_tools[1]["mock_function"](user_input)
            elif "時刻" in user_input:
                mock_tools[2]["mock_function"]()
            
            # モックの応答を生成
            mock_response = {
                "messages": [
                    AIMessage(content=f"モックの応答: {user_input}")
                ]
            }
            
            for message in mock_response["messages"]:
                if hasattr(message, 'content') and isinstance(message, AIMessage):
                    print("\n回答:", message.content)
        except Exception as e:
            print(f"\nエラーが発生しました: {str(e)}")

if __name__ == "__main__":
    asyncio.run(mock_main()) 