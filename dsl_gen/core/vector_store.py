from typing import List, Optional
import os
import os.path as osp
from langchain_core.documents import Document
from langchain_text_splitters import (RecursiveCharacterTextSplitter,
                                      MarkdownHeaderTextSplitter)
from langchain_core.embeddings import Embeddings
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

from langchain_community.vectorstores import FAISS
import logging
from ..config import CFG

logger = logging.getLogger('dsl_gen')

PATH_CFG = CFG.PATH_CFG
MODEL_CFG = CFG.MODEL_CFG
EMBEDDING_CFG = CFG.EMBEDDING_CFG


def _get_embeddings(emb_model: str) -> Embeddings:
    if emb_model.startswith("openai/"):
        return OpenAIEmbeddings(model=emb_model[7:])
    elif emb_model.startswith("hf/"):
        return HuggingFaceEmbeddings(
            model_name=emb_model[3:],
            model_kwargs={'device': 'cpu'}
        )
    else:
        raise ValueError(f"Unsupported embedding model: {emb_model}")


def _load_cached_vectorstore(vecdb_path: str, embeddings: Embeddings) -> Optional[FAISS]:
    if osp.exists(vecdb_path):
        try:
            logger.info(f"Loading cached vectorstore from {vecdb_path}")
            return FAISS.load_local(
                folder_path=vecdb_path,
                embeddings=embeddings,
                allow_dangerous_deserialization=True  # 允许加载自定义类
            )
        except Exception as e:
            logger.warning(f"Failed to load cached vectorstore: {str(e)}")
            return None
    return None


def _process_file(file_path: str, headers_to_split_on: List[tuple], all_docs: List[Document]):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        # 带元数据的分割
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on
        )
        splits = markdown_splitter.split_text(content)
        # 二次分割保留代码块
        code_splitter = RecursiveCharacterTextSplitter.from_language(
            language="markdown",
            chunk_size=EMBEDDING_CFG.chunk_size,
            chunk_overlap=EMBEDDING_CFG.chunk_overlap,
            keep_separator=True
        )
        splits = code_splitter.split_documents(splits)
        all_docs.extend(splits)
    except Exception as e:
        logger.error(f"Error processing {file_path}: {str(e)}")

# Process markdown docs with local cache


def _process_markdown_docs() -> FAISS:
    """带本地缓存的文档处理流程"""
    vecdb_base = PATH_CFG.VECTOR_DB_DIR
    emb_model = EMBEDDING_CFG.embedding_model

    if not osp.exists(vecdb_base):
        os.makedirs(vecdb_base, exist_ok=True)

    embeddings = _get_embeddings(emb_model)

    # Load cached vectorstore if available

    emd_model_name = emb_model.replace("/", "_")
    vecdb_path = osp.join(
        vecdb_base, f"vectorstore_{emd_model_name}")

    cached_vectorstore = _load_cached_vectorstore(vecdb_path, embeddings)
    if cached_vectorstore:
        return cached_vectorstore

    # Rebuild vectorstore from scratch
    logger.info("Building new vectorstore...")

    # Chunking and splitting logic for markdown files
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    all_docs = []

    for root, _, files in os.walk(PATH_CFG.TUTO_PATH):
        for file in files:
            if not file.endswith(".md"):
                continue

            full_path = osp.join(root, file)
            _process_file(full_path, headers_to_split_on, all_docs)

    # Build vectorstore
    vectorstore = FAISS.from_documents(all_docs, embeddings)

    # Save vectorstore to cache
    try:
        vectorstore.save_local(vecdb_path)
        logger.info(f"Vectorstore saved to {vecdb_path}")
    except Exception as e:
        logger.error(f"Failed to save vectorstore: {str(e)}")

    return vectorstore


_vectorstore = None


def get_vectorstore() -> FAISS:
    """获取向量库"""
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = _process_markdown_docs()
    return _vectorstore
