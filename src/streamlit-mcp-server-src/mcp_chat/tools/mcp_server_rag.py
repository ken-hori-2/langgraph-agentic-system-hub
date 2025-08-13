from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from typing import Any

# Load environment variables from .env file (contains API keys)
load_dotenv(override=True)


def create_retriever() -> Any:
    """
    Creates and returns a document retriever based on FAISS vector store.

    This function performs the following steps:
    1. Loads a PDF document(place your PDF file in the data folder)
    2. Splits the document into manageable chunks
    3. Creates embeddings for each chunk
    4. Builds a FAISS vector store from the embeddings
    5. Returns a retriever interface to the vector store

    Returns:
        Any: A retriever object that can be used to query the document database
    """
    try:
        # Step 1: Load Documents
        # PyMuPDFLoader is used to extract text from PDF files
        # PDFファイルを読み込む（ファイルが存在しない・壊れている場合は例外が発生）
        loader = PyMuPDFLoader("data/sakamoto_paper.pdf")
        docs = loader.load()
    except Exception as e:
        # 例外発生時はエラー内容を返す（呼び出し元でそのまま返される）
        return f"PDFの読み込みでエラーが発生しました: {str(e)}"

    # Step 2: Split Documents
    # Recursive splitter divides documents into chunks with some overlap to maintain context
    # ドキュメントをチャンクに分割（文脈保持のため一部重複あり）
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    split_documents = text_splitter.split_documents(docs)

    # Step 3: Create Embeddings
    # OpenAI's text-embedding-3-small model is used to convert text chunks into vector embeddings
    # OpenAIの埋め込みモデルでテキストをベクトル化
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Step 4: Create Vector Database
    # FAISS is an efficient similarity search library that stores vector embeddings
    # and allows for fast retrieval of similar vectors
    # FAISSでベクトルストアを作成（類似検索用）
    vectorstore = FAISS.from_documents(documents=split_documents, embedding=embeddings)

    # Step 5: Create Retriever
    # The retriever provides an interface to search the vector database
    # and retrieve documents relevant to a query
    # ベクトルストアから検索するためのリトリーバーを作成
    retriever = vectorstore.as_retriever()
    return retriever


# Initialize FastMCP server with configuration
mcp = FastMCP(
    "Retriever",
    instructions="A Retriever that can retrieve information from the database.",
    host="0.0.0.0",
    port=8005,
)


@mcp.tool()
async def retrieve(query: str) -> str:
    """
    Retrieves information from the document database based on the query.

    This function creates a retriever, queries it with the provided input,
    and returns the concatenated content of all retrieved documents.

    Args:
        query (str): The search query to find relevant information

    Returns:
        str: Concatenated text content from all retrieved documents
    """
    # Create a new retriever instance for each query
    # Note: In production, consider caching the retriever for better performance
    retriever = create_retriever()

    # Use the invoke() method to get relevant documents based on the query
    # retrieverがエラーメッセージ（str型）の場合はそのまま返す
    if isinstance(retriever, str):
        return retriever

    # クエリに基づいて関連ドキュメントを取得
    retrieved_docs = retriever.invoke(query)

    # 検索結果が空の場合の処理
    if not retrieved_docs:
        return "該当する情報が見つかりませんでした。"

    # 取得したドキュメントの内容を連結して返す
    return "\n".join([doc.page_content for doc in retrieved_docs])


if __name__ == "__main__":
    # Run the MCP server with stdio transport for integration with MCP clients
    mcp.run(transport="stdio")
