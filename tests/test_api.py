import logging
import unittest
import time
from pathlib import Path
from dsl_gen.agents import getClient

class TestLLM(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        log_path = Path(__file__).parent/'logs'/f"{time.strftime('%Y%m%d_%H%M%S')}_test_api.log"
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(), 
                      logging.FileHandler(log_path)]
        )

    def test_completion(self):
        for model in ['openai', 'ollama', 'deepseek']:
            with self.subTest(model=model):
                try:
                    print('Testing model:', model)
                    llm = getClient(model)
                    response = llm.invoke("Write a python function that returns the sum of two numbers.")
                    data = response.model_dump(mode='python')
                    print(data)
                    print(data.keys())
                    print('-'*100)

                    self.assertIn('content', data, "Response should contain 'content' field")
                    self.assertIsInstance(data['content'], str, "Content should be a string")
                    self.assertGreater(len(data['content']), 0, "Content should not be empty")
                    self.assertIn("def", data['content'], "Response should contain a Python function")
                    self.assertIn("return", data['content'], "Response should contain a return statement")
                except Exception as e:
                    print(e)
                    self.fail(f"Failed to complete the prompt with model {model}")

if __name__ == '__main__':
    unittest.main()
