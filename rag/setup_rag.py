import os
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader


def setup_vectorstore():
    loader = DirectoryLoader("knowledge_base", glob="*.*")
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

    vectordb = Chroma.from_documents(splits, embeddings, persist_directory="chroma_db")
    vectordb.persist()
    return vectordb