import os
import unittest


class MainTest(unittest.TestCase):
    dataset_path = os.path.join(os.path.dirname(__file__), "dataset")
    # Models
    iml = os.path.join(dataset_path, "iML1515.xml.gz")
    iml_toy = os.path.join(dataset_path, "iML1515.toy.xml.gz")
    # Pathways
    pathway_one_json = os.path.join(dataset_path, "PathwayModelisation-0.4.1.json")
    # arrows.py - Node
    node_one_dict = dict(
        id="n11",
        labels=["Model"],
        properties=dict(id="str", name="str", metaid="str", sboTerm="str"),
    )
    node_two_dict = dict(
        id="n12",
        position=dict(x=-482.6, y=-158),
        null_one=None,
        null_two="",
        labels=["Compartment"],
        properties=dict(
            id="str", metaid="str", name="str", sboTerm="int", spatialDimensions="int"
        ),
    )
    node_three_dict = dict(
        id="n13",
        labels=["Species"],
        properties=dict(id="str", name="str", metaid="str", sboTerm="str"),
    )
    # arrows.py - Relationship
    rel_one_dict = dict(
        id="n21",
        fromId="n13",
        toId="n12",
        type="HAS_COMPARTMENT",
        properties=dict(),
        style=dict(),
    )
    rel_two_dict = dict(
        id="n21",
        fromId="n12",
        toId="n13",
        type="IN_COMPARTMENT",
        properties=dict(),
        style=dict(),
    )
