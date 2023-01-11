import os
import unittest


class Main_test(unittest.TestCase):
    dataset_path = os.path.join(os.path.dirname(__file__), "dataset")
    # Pathways
    pathway_one_json = os.path.join(dataset_path, "PathwayModelisation-0.4.1.json")
