# tests/test_rag_flow.py

# %%
import unittest
import logging
from dsl_gen.core.flows import build_rag_flow
from pathlib import Path
import time
from dsl_gen import CFG
import os
import random
# %%


class TestRAGFlow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        log_path = Path(__file__).parent/'logs' / \
            f"{time.strftime('%Y%m%d_%H%M%S')}_test_api.log"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(),
                      logging.FileHandler(log_path)]
        )

    def setUp(self):
        self.flow = build_rag_flow()

    def test_normal_flow(self):
        challenges_path = CFG.PATH_CFG.CHALLENGES_PATH

        selected_file = Path(challenges_path) / "c000.json"
        result = self.flow.invoke({"challenge_path": selected_file})
        print(result["compiled"])

        selected_file = random.choice(os.listdir(challenges_path))
        result = self.flow.invoke({"challenge_path": selected_file})
        print(result["compiled"])

        question = "Create a table Catalog containing 3 columns : 10 \"item\"s and their \"OrderDate\" and \"DeliveryDate\" (the dates should be in date data type). Define a new column \"Leadtime\" for each item. Finally, show the table containing each item with their Leadtime, but only for those with Leadtime longer than 20 days."
        result = self.flow.invoke({"question": question})
        print(result["compiled"])

    def test_retry_flow(self):
        pass
        # raise NotImplementedError("Test not implemented")


# %%
if __name__ == "__main__":
    unittest.main()
