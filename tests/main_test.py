import os
import unittest


class MainTest(unittest.TestCase):
    dataset_path = os.path.join(os.path.dirname(__file__), "dataset")
    # Models
    iml = os.path.join(dataset_path, "iML1515.xml.gz")
    # Pathways
    pathway_one_json = os.path.join(dataset_path, "PathwayModelisation-0.4.1.json")
    # arrows.py - Node
    node_one_dict = dict(
        id="n21",
        labels=["Model"],
        properties=dict(id="str", name="str", metaid="str", sboTerm="str"),
    )
    node_two_dict = dict(
        id="n2",
        position=dict(x=-482.6, y=-158),
        null_one=None,
        null_two="",
        labels=["Compartment"],
        properties=dict(
            id="str", metaid="str", name="str", sboTerm="int", spatialDimensions="int"
        ),
    )
