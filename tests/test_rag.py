# %%
import unittest
import logging
from dsl_gen.core.flows import build_rag_flow
from langgraph.graph import END
from pathlib import Path
import time

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
        test_input = {
            "question": "如何用Python实现快速排序？",
            "context": {}
        }
        for step in self.flow.stream(test_input):
            if END in step:
                result = step[END]
                self.assertIn("compiled_result", result)
                self.assertTrue(result["compiled_result"].valid)

    def test_retry_flow(self):
        test_input = {
            "question": "包含错误的代码请求",
            "context": {}
        }
        execution_steps = []
        for step in self.flow.stream(test_input):
            execution_steps.append(step)

        self.assertEqual(len(execution_steps), 4)  # 3次重试 + 最终失败
        self.assertIn("max_retries_exceeded", execution_steps[-1][END]["context"])

# %%
if __name__ == "__main__":
    unittest.main()