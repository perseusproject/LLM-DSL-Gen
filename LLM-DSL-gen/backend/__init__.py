from typing import Optional
from config import MODEL_CFG
import logging
from langchain_openai import ChatOpenAI

logger = logging.getLogger('global')

_llm_client = None

def getClient(backend: Optional[str] = 'ollama'):

    global _llm_client

    cfg = {
        'openai': MODEL_CFG.OpenAI,
        'ollama': MODEL_CFG.Ollama,
        'deepseek': MODEL_CFG.DeepSeek,
    }[backend]
    
    if _llm_client is None:
        _llm_client =  ChatOpenAI(
            model = cfg.model,
            openai_api_base = cfg.base_url,
            openai_api_key = cfg.api_key
        )
    
    logger.info("Model loaded: %s", cfg.model)
    return _llm_client
    