import libsbml
from tests.main_test import MainTest

from neo4jsbml.arrows import Arrows, Node, Relationship
from neo4jsbml.sbml import Sbml


class TestSbml(MainTest):
    def setUp(self):
        self.sbml = Sbml.from_sbml(path=MainTest.iml)

    def test_load(self):
        self.assertEqual(self.sbml.document.__class__.__name__, "SBMLDocument")
        self.assertEqual(self.sbml.model.__class__.__name__, "Model")
        self.assertIs(self.sbml.tag, None)
        sbml = Sbml.from_sbml(path=MainTest.iml, tag="test")
        self.assertEqual(sbml.tag, "test")

    def test_method(self):
        methods = Sbml.find_method(self.sbml.document, "notes")
        self.assertEqual(methods, ["getNotes"])
        methods = Sbml.find_method(self.sbml.model, "Id")
        self.assertEqual(methods, ["getId"])
        methods = Sbml.find_method(self.sbml.model, "Idl")
        self.assertEqual(methods, ["getAllElementIdList", "getAllElementMetaIdList"])

    def test_format_results(self):
        data = Sbml.format_results(results=MainTest.node_one_dict)
        self.assertEqual(data, MainTest.node_one_dict)
        data = Sbml.format_results(results=MainTest.node_two_dict)
        self.assertNotIn("null_one", data.keys())
        self.assertNotIn("null_two", data.keys())
        self.assertEqual(data.keys(), 4)

    def test_format_nodes(self):
        node_two = Node.from_dict(data=MainTest.node_two_dict)
        nodes = self.sbml.format_nodes(nodes=[node_two])
        self.assertEqual(
            nodes,
            [
                {
                    "labels": ["Compartment"],
                    "id": "c",
                    "name": "cytosol",
                    "sboTerm": -1,
                    "spatialDimensions": 0,
                },
                {
                    "labels": ["Compartment"],
                    "id": "e",
                    "name": "extracellular space",
                    "sboTerm": -1,
                    "spatialDimensions": 0,
                },
                {
                    "labels": ["Compartment"],
                    "id": "p",
                    "name": "periplasm",
                    "sboTerm": -1,
                    "spatialDimensions": 0,
                },
            ],
        )
