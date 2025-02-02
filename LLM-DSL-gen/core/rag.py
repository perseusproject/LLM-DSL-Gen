# src/backend/rag.py
import logging
from pathlib import Path
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from config import CONFIG
from backend import getClient

# 初始化日志
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class RAGSystem:
    def __init__(self):
        self.vectorstore = None
        self.embeddings = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=len,
            add_start_index=True
        )

    def initialize_embeddings(self, model_name="deepseek-r1:7b"):
        """初始化嵌入模型"""
        try:
            self.embeddings = OllamaEmbeddings(model=model_name)
            logger.info(f"Initialized embeddings with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {str(e)}")
            raise

    def load_documents(self, docs_path: str = None) -> List:
        """加载文档"""
        docs_path = docs_path or CONFIG.DOCS_PATH
        try:
            loader = DirectoryLoader(
                docs_path,
                glob="**/*.md",
                recursive=True,
                show_progress=True
            )
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} documents from {docs_path}")
            return documents
        except Exception as e:
            logger.error(f"Document loading failed: {str(e)}")
            raise

    def create_vectorstore(self, documents: List, persist_dir: str = None):
        """创建并持久化向量存储"""
        persist_dir = persist_dir or CONFIG.VECTOR_DB_DIR
        Path(persist_dir).mkdir(parents=True, exist_ok=True)

        try:
            # 分割文档
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Split into {len(chunks)} chunks")

            # 创建向量存储
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=persist_dir
            )
            logger.info(f"Vector store created at {persist_dir}")
            return self.vectorstore
        except Exception as e:
            logger.error(f"Vector store creation failed: {str(e)}")
            raise

    def query(self, question: str, k: int = 5):
        """执行查询"""
        if not self.vectorstore:
            raise ValueError("Vector store not initialized")
            
        return self.vectorstore.similarity_search(question, k=k)

# Singleton
_rag_instance = None

def get_rag_system():
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGSystem()
        _rag_instance.initialize_embeddings()
        
        # 仅当向量库不存在时重新生成
        if not Path(CONFIG.VECTOR_DB_DIR).exists():
            docs = _rag_instance.load_documents()
            _rag_instance.create_vectorstore(docs)
        else:
            # 加载已有向量库
            _rag_instance.vectorstore = Chroma(
                persist_directory=CONFIG.VECTOR_DB_DIR,
                embedding_function=_rag_instance.embeddings
            )
    return _rag_instance