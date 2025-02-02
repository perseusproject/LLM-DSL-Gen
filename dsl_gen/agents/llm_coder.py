# -*- coding: utf-8 -*-
# dsl_gen/agents/llm_coder.py

from .api import getClient
from dsl_gen.core.rag import RAGState
from langchain_core.messages import BaseMessage
from typing import List


def _generate_answer(messages: List[BaseMessage]):
    client = getClient()
    # type(client) = ChatOpenAI
    response = client.invoke(messages)
    return response.model_dump()


def generate_answer(state: RAGState):
    return {**state, "answer": _generate_answer(state["messages"])}
