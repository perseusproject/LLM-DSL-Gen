# -*- coding: utf-8 -*-
# dsl_gen/agents/llm_coder.py

from .api import getClient
from dsl_gen.core.rag import RAGState
from langchain_core.messages import BaseMessage
from dsl_gen import CFG
from typing import List
import logging

logger = logging.getLogger('dsl_gen')


def _generate_answer(messages: List[BaseMessage]):
    client = getClient(CFG.CODER.active_model)
    response = client.invoke(messages)
    response_dict = response.model_dump()
    logger.debug("Model response: %s...",
                 response_dict["content"][:100])
    return response_dict


def llm_coder(state: RAGState) -> RAGState:
    """llm_coder node"""
    return {**state, "completion": _generate_answer(state["messages"])}
