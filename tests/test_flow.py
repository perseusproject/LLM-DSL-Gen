# tests/test_rag_flow.py

# %%
import unittest
import logging
from dsl_gen.core.flows import build_rag_flow
from langgraph.graph import END
from pathlib import Path
import time

# %%
class TestRAGFlow(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        log_path = Path(__file__).parent/'logs'/f"{time.strftime('%Y%m%d_%H%M%S')}_test_api.log"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(), 
                      logging.FileHandler(log_path)]
        )
    
    def setUp(self):
        self.flow = build_rag_flow()

    def test_normal_flow(self):
        from dsl_gen.core.flows import build_rag_flow
        result = self.flow.invoke({"question": "How to implement RAG?"})
        print(result["compiled"])  # 获取最终结果

    def test_retry_flow(self):
        raise NotImplementedError("Test not implemented")
# %%
if __name__ == "__main__":
    unittest.main()