# -*- coding: utf-8 -*-
# dsl_gen/core/vector_store.py

import re
import os
import os.path as osp
import logging

from langchain_core.documents import Document
from langchain_text_splitters import (RecursiveCharacterTextSplitter,
                                      MarkdownHeaderTextSplitter)

from langchain_core.embeddings import Embeddings
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

from langchain_community.vectorstores import FAISS

from typing import List, Optional
from ..config import CFG

logger = logging.getLogger('dsl_gen')

PATH_CFG = CFG.PATH_CFG
EMBEDDING_CFG = CFG.EMBEDDING_CFG


_embeddings_instance = None


def _get_embeddings(emb_model: str) -> Embeddings:
    global _embeddings_instance

    if _embeddings_instance is None:
        logger.info("Loading embedding model into memory: %s", emb_model)

        if emb_model.startswith("openai/"):
            _embeddings_instance = OpenAIEmbeddings(model=emb_model[7:])
        elif emb_model.startswith("hf/"):
            _embeddings_instance = HuggingFaceEmbeddings(
                model_name=emb_model[3:],
                model_kwargs={'device': 'cpu'})
        else:
            raise ValueError(f"Unsupported embedding model: {emb_model}")

    else:
        logging.info("Reusing existing embeddings instance: %s",
                     _embeddings_instance)
    return _embeddings_instance


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


# Tweak: MarkdownHeaderTextSplitter strips leading whitespace by default
# To work around this, we replace leading whitespace with special characters

TAB_REPLACEMENT = "輁"
SPACE_REPLACEMENT = "鶨"


def replace_leading_whitespace(text: str) -> str:
    # Auxiliary functions for _process_file
    """Replace leading whitespace with special characters"""
    lines = []
    for line in text.split('\n'):
        # Match leading whitespace
        leading_whitespace = re.match(r'^[\t ]*', line).group()
        # Replace tab and space
        replaced = leading_whitespace.replace('\t', TAB_REPLACEMENT)
        replaced = replaced.replace(' ', SPACE_REPLACEMENT)
        lines.append(replaced + line[len(leading_whitespace):])
    return '\n'.join(lines)


def restore_leading_whitespace(text: str) -> str:
    # Auxiliary functions for _process_file
    """Restore special characters to original whitespace"""
    text = text.replace(TAB_REPLACEMENT, '\t')
    text = text.replace(SPACE_REPLACEMENT, ' ')
    return text


def _process_file(file_path: str) -> List[Document]:

    headers_to_split_on = [("#", "Header 1"),
                           ("##", "Header 2"),
                           ('###', "Header 3")]

    markdown_separators = ["\n#{1,3} ", "\n\\*\\*\\*+\n", "\n\n"]

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        # Phase 1: Preprocessing - Replace leading whitespace
        processed_content = replace_leading_whitespace(raw_content)

        # Phase 2: Split document
        splits = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            strip_headers=False  # Ensure headers are not removed
        ).split_text(processed_content)

        # Phase 3: Secondary split (preserve restored whitespace)
        splitter = RecursiveCharacterTextSplitter(
            separators=markdown_separators,
            chunk_size=EMBEDDING_CFG.chunk_size,
            chunk_overlap=EMBEDDING_CFG.chunk_overlap,
            is_separator_regex=True,
            keep_separator=True
        )
        splits = splitter.split_documents(splits)

        # Phase 4: Restore original whitespace
        for doc in splits:
            doc.page_content = restore_leading_whitespace(doc.page_content)
            # Carry original file path as metadata
            doc.metadata["source"] = file_path

        logger.debug(f"Processed {file_path}: {len(splits)} documents")

        return splits

    except Exception as e:
        logger.error(f"Error processing {file_path}: {str(e)}")
        return []


def get_all_markdown_files(root_dir: str) -> List[str]:
    file_paths = []
    for root, _, files in os.walk(PATH_CFG.TUTO_PATH):
        for file in files:
            if file.endswith(".md"):
                full_path = osp.join(root, file)
                file_paths.append(full_path)
    return file_paths


def _build_vectorstore() -> FAISS:
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
    all_docs = []

    file_paths = get_all_markdown_files(PATH_CFG.TUTO_PATH)

    try:
        from tqdm import tqdm
        for full_path in tqdm(file_paths, desc="Processing Markdown files"):
            docs = _process_file(full_path)
            all_docs.extend(docs)
    except ImportError:
        logger.warning("tqdm not found, falling back to simple for loop")
        for full_path in file_paths:
            docs = _process_file(full_path)
            all_docs.extend(docs)

    logger.info(
        f"Building vectorstore from {len(file_paths)} markdown files, this may take several minutes...")

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

# All the above functions are auxiliary functions


def get_vectorstore() -> FAISS:  # Main entry point
    """TL;DR: Get a global vectorstore instance"""
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = _build_vectorstore()
    return _vectorstore


__all__ = ["get_vectorstore", "_get_embeddings", "_build_vectorstore",
           "_load_cached_vectorstore", "_process_file", "_vectorstore", "_embeddings_instance"]
