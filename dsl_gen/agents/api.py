# -*- coding: utf-8 -*-
# dsl_gen/agents/api.py

from ..config import CFG
from langchain_openai import ChatOpenAI

import logging
from typing import Optional

logger = logging.getLogger('dsl_gen')

MODEL_CFG = CFG.MODEL_CFG

_llm_clients = {
    'openai': None,
    'ollama': None,
    'deepseek': None,
}

def getClient(backend: Optional[str] = CFG.MODEL_CFG.used_model) -> ChatOpenAI:

    global _llm_clients

    if _llm_clients[backend] is None:
        cfg = {
            'openai': MODEL_CFG.OpenAI,
            'ollama': MODEL_CFG.Ollama,
            'deepseek': MODEL_CFG.DeepSeek,
        }[backend]
    
        _llm_clients[backend] = ChatOpenAI(
            model = cfg.model,
            openai_api_base = cfg.base_url,
            openai_api_key = cfg.api_key
        )
    
        logger.info("Model loaded: %s, base_url: %s", cfg.model, cfg.base_url)

    return _llm_clients[backend]