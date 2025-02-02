from backend import getClient
import logging
import argparse

parser = argparse.ArgumentParser(description='Model Completion Test')

logger = logging.getLogger('global')
llm = getClient('ollama')

logger.info("Requiring completion")
response = llm.invoke("写一段 Python 代码计算斐波那契数列")

print(response.content)