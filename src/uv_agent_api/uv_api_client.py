import requests
import json
from typing import Optional

class AgentClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8001"):
        self.base_url = base_url

    def ask(self, question: str) -> Optional[str]:
        """
        AIエージェントに質問を送信します。

        Args:
            question (str): 質問内容

        Returns:
            Optional[str]: AIからの応答。エラーの場合はNone
        """
        try:
            response = requests.post(
                f"{self.base_url}/ask",
                json={"input": question},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()["response"]
        except requests.exceptions.RequestException as e:
            print(f"エラーが発生しました: {e}")
            return None

def main():
    client = AgentClient()
    
    print("AIエージェントとの対話を開始します。終了するには 'quit' または 'exit' と入力してください。")
    print("-" * 50)
    
    while True:
        question = input("\n質問を入力してください: ").strip()
        
        if question.lower() in ["quit", "exit"]:
            print("対話を終了します。")
            break
            
        if not question:
            print("質問を入力してください。")
            continue
            
        response = client.ask(question)
        if response:
            print("\nAIの応答:")
            print(response)
        print("-" * 50)

if __name__ == "__main__":
    main() 