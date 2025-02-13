# tests/test_rag_flow.py

# %%
import unittest
import logging
from dsl_gen.core.vector_store import get_vectorstore
from pathlib import Path
import time
from dsl_gen import CFG
import os
import random
# %%


class TestRAGFlow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        log_path = Path(__file__).parent / 'logs' / \
            f"{time.strftime('%Y%m%d_%H%M%S')}_test_api.log"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(),
                      logging.FileHandler(log_path)]
        )

    def setUp(self):
        self.vectorstore = None

    def test_read_from_file(self):
        self.vectorstore = get_vectorstore()


# %%
if __name__ == "__main__":
    unittest.main()
