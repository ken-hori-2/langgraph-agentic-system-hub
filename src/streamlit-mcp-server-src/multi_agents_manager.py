import asyncio
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Dict, Any, TypedDict, Optional
from dataclasses import dataclass
import uuid

# OUTPUT_TOKEN_INFOはapp_multiagents.pyからimportする前提
# 例: from .app_multiagents import OUTPUT_TOKEN_INFO

@dataclass
class AgentState:
    """エージェントワークフローの状態"""
    user_query: str
    selected_agent: Optional[str] = None
    agent_response: Optional[str] = None
    tools: Optional[list] = None
    error: Optional[str] = None

class SupervisorAgent:
    """エージェント選択を担当するsupervisor"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
    
    def select_agent(self, state: AgentState) -> Dict[str, Any]:
        """ユーザークエリを分析して適切なエージェントを選択"""
        prompt = ChatPromptTemplate.from_template("""
        あなたはユーザーの質問を分析し、適切なエージェントを選択するsupervisorです。
        
        利用可能なエージェント:
        - agent1: 一般的な質問、情報収集、ツール使用
        - agent2: 専門的な分析、詳細な調査
        
        ユーザーの質問: {user_query}
        
        この質問に対して適切なエージェントを選択してください。
        選択するエージェント名のみを回答してください（agent1またはagent2）:
        """)
        
        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({"user_query": state.user_query})
        
        # 結果をクリーンアップ
        agent_name = result.strip()
        if "agent2" in agent_name:
            selected_agent = "agent2"
        else:
            selected_agent = "agent1"  # デフォルト
        
        return {"selected_agent": selected_agent}

class WorkerAgent:
    """タスク実行を担当するworker"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
    
    def execute_task(self, state: AgentState) -> Dict[str, Any]:
        """選択されたエージェントでタスクを実行"""
        try:
            # 選択されたエージェントに基づいてReActエージェントを作成
            agent = create_react_agent(
                self.llm,
                state.tools or [],
                checkpointer=MemorySaver(),
            )
            
            # エージェント固有のプロンプトを設定
            agent_prompt = self._get_agent_prompt(state.selected_agent)
            
            # エージェントを実行
            from langchain_core.messages import HumanMessage
            result = agent.invoke({
                "messages": [HumanMessage(content=f"{agent_prompt}\n\n{state.user_query}")]
            })
            
            return {"agent_response": result["messages"][-1].content}
            
        except Exception as e:
            return {"error": f"エージェント実行エラー: {str(e)}"}
    
    def _get_agent_prompt(self, agent_name: str) -> str:
        """エージェント固有のプロンプトを取得"""
        prompts = {
            "agent1": "あなたは一般的な質問に答えるエージェントです。提供されたツールを使用して、親切で詳細な回答を提供してください。",
            "agent2": "あなたは専門的な分析を行うエージェントです。提供されたツールを使用して、深い洞察と詳細な分析を提供してください。"
        }
        return prompts.get(agent_name, prompts["agent1"])

class MultiAgentsManager:
    def __init__(self, mcp_client_cls, output_token_info, default_model="claude-3-7-sonnet-latest"):
        self.mcp_client_cls = mcp_client_cls
        self.output_token_info = output_token_info
        self.default_model = default_model
        self.mcp_client = None
        self.tool_count = 0
        self.llm = None
        self.graph = None
        self.supervisor = None
        self.worker = None

    async def initialize(self, mcp_config, selected_model=None):
        """MCPクライアントとLangGraphワークフローを初期化"""
        if selected_model is None:
            selected_model = self.default_model
        
        # MCPクライアントの初期化
        self.mcp_client = self.mcp_client_cls(mcp_config)
        tools = await self.mcp_client.get_tools()
        self.tool_count = len(tools)
        
        # LLMの初期化
        if selected_model in self.output_token_info:
            self.llm = ChatOpenAI(
                model=selected_model,
                temperature=0.1,
                max_tokens=self.output_token_info[selected_model]["max_tokens"],
            )
        else:
            self.llm = ChatOpenAI(
                model=selected_model,
                temperature=0.1,
                max_tokens=4096,
            )
        
        # SupervisorとWorkerの初期化
        self.supervisor = SupervisorAgent(self.llm)
        self.worker = WorkerAgent(self.llm)
        
        # LangGraphワークフローの作成
        self.graph = self._create_workflow(tools)

    def _create_workflow(self, tools: list) -> StateGraph:
        """LangGraphワークフローを作成"""
        workflow = StateGraph(AgentState)
        
        # ノードの追加
        workflow.add_node("supervisor", self.supervisor.select_agent)
        workflow.add_node("worker", self.worker.execute_task)
        
        # エントリーポイントとエッジの設定
        workflow.set_entry_point("supervisor")
        workflow.add_edge("supervisor", "worker")
        workflow.add_edge("worker", END)
        
        # メモリ付きでコンパイル
        compiled_graph = workflow.compile(checkpointer=MemorySaver())
        
        graph_image = compiled_graph.get_graph(xray=True).draw_mermaid_png()
        with open("ApplicationConfiguration.png", "wb") as f:
            f.write(graph_image)
        
        return compiled_graph

    async def process_query(self, user_query: str, thread_id: str = None) -> str:
        """ユーザークエリを処理して結果を返す"""
        if not self.graph:
            return "エージェントが初期化されていません"
        
        try:
            # 初期状態を作成
            initial_state = AgentState(
                user_query=user_query,
                tools=self._get_tools_for_agents()
            )
            
            # チェックポイント設定
            config = {}
            if thread_id:
                config["configurable"] = {"thread_id": thread_id}
            else:
                # デフォルトのthread_idを生成
                config["configurable"] = {"thread_id": str(uuid.uuid4())}
            
            # ワークフローを実行
            result = await self.graph.ainvoke(initial_state, config=config)
            
            if result.get("error"):
                return f"エラー: {result['error']}"
            
            return result.get("agent_response", "応答が生成されませんでした")
            
        except Exception as e:
            return f"処理エラー: {str(e)}"

    def _get_tools_for_agents(self) -> list:
        """エージェント用のツールを取得"""
        if self.mcp_client:
            # 非同期でツールを取得する必要があるため、ここでは空リストを返す
            # 実際の実装では、ツールを事前に取得して保持するか、
            # 非同期処理を適切に処理する必要がある
            return []
        return []

    def get_agent_names(self) -> list:
        """利用可能なエージェント名のリストを返す"""
        return ["agent1", "agent2"]

    def get_tool_count(self) -> int:
        """MCPツール数を返す"""
        return self.tool_count 