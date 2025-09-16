from langchain.tools import Tool
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from rag.setup_rag import setup_vectorstore

vectordb = setup_vectorstore()

qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4", temperature=0),
    retriever=vectordb.as_retriever()
)

def rag_query(query: str) -> str:
    return qa_chain.run(query)

rag_tool = Tool(
    name="KnowledgeBaseTool",
    func=rag_query,
    description="Search the travel knowledge base for guides, preferences, and tips"
)
