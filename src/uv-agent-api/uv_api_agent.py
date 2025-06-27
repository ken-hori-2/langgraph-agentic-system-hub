# agent.py
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import Dict, Any, TypedDict, List
from langchain_google_community import GoogleSearchAPIWrapper
from langchain.agents import Tool
from langgraph.prebuilt import create_react_agent
import os
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver

# メモリーの初期化
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

class AgentState(TypedDict):
    input: str
    result: str
    chat_history: List[Any]

def create_tools() -> List[Tool]:
    # Google検索ツールの作成
    def search_google(query: str) -> str:
        try:
            search = GoogleSearchAPIWrapper()
            return search.run(query)
        except Exception as e:
            return f"検索中にエラーが発生しました: {str(e)}"

    google_search_tool = Tool.from_function(
        func=search_google,
        name="Google_Search",
        description="インターネットで情報を検索します。"
    )

    return [google_search_tool]

def agent_node(state: AgentState) -> AgentState:
    question = state["input"]
    chat_history = state.get("chat_history", [])
    
    try:
        # LLMの初期化
        llm = ChatOpenAI(temperature=0.7)
        
        # ツールの準備
        tools = create_tools()
        
        # ReActエージェントの作成
        agent = create_react_agent(llm, tools)
        
        # 会話履歴を含めたメッセージの作成
        messages = chat_history + [HumanMessage(content=question)]
        
        # エージェントの実行
        result = agent.invoke(
            {
                "messages": messages
                # "messages": [
                #     (
                #         "human",
                #         (
                #             "Execute the following task and provide a detailed response.\n\n"
                #             f"Task: {question}\n\n"
                #             "Requirements:\n"
                #             "1. Use the provided tools as needed.\n"
                #             "2. Execute thoroughly and comprehensively.\n"
                #             "3. Provide as specific facts and data as possible.\n"
                #             "4. Summarize the findings clearly.\n"
                #         ),
                #     )
                # ]
            }
        )

        # 会話履歴を更新
        memory.save_context(
            {"input": question},
            {"output": result["messages"][-1].content}
        )

        return {
            "input": question,
            "result": result["messages"][-1].content,
            "chat_history": memory.chat_memory.messages
        }
    except Exception as e:
        error_message = f"エージェントの実行中にエラーが発生しました: {str(e)}"
        print(error_message)  # サーバー側のログに出力
        return {
            "input": question,
            "result": error_message,
            "chat_history": chat_history
        }

# LangGraph構築
builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.set_entry_point("agent")
builder.set_finish_point("agent")

# 実行グラフ作成
graph = builder.compile()