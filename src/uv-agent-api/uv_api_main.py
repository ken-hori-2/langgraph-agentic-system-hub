# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uv_api_agent import graph, memory
from typing import List, Dict

app = FastAPI(
    title="AI Agent API",
    description="LangGraphを使用したAIエージェントのAPI",
    version="1.0.0"
)

# class Request(BaseModel):
#     input: str

#     class Config:
#         schema_extra = {
#             "example": {
#                 "input": "こんにちは、元気ですか？"
#             }
#         }
class Query(BaseModel):
    input: str

# 会話履歴を保持するためのグローバル変数
current_state = {
    "input": "",
    "result": "",
    "chat_history": []
}

@app.post("/ask", response_model=dict)
async def ask_endpoint(query: Query):
    try:
        # 現在の状態を更新
        current_state["input"] = query.input
        
        # エージェントを呼び出し
        result = graph.invoke(current_state)
        
        # 状態を更新
        current_state.update(result)
        
        return {"response": result["result"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "AI Agent API へようこそ！"}

@app.get("/history")
async def get_history():
    return {"history": memory.chat_memory.messages}

@app.delete("/history")
async def clear_history():
    memory.chat_memory.clear()
    current_state["chat_history"] = []
    return {"message": "会話履歴をクリアしました"}