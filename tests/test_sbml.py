import libsbml
from neo4jsbml.arrows import Arrows, Node, Relationship
from neo4jsbml.sbml import Sbml

from tests.main_test import MainTest


class TestSbml(MainTest):
    def setUp(self):
        self.sbml_iml = Sbml.from_sbml(path=MainTest.iml)
        self.sbml_toy = Sbml.from_sbml(path=MainTest.iml_toy)

        self.node_two = Node.from_dict(data=MainTest.node_two_dict)
        self.node_three = Node.from_dict(data=MainTest.node_three_dict)

    def test_load(self):
        self.assertEqual(self.sbml_iml.document.__class__.__name__, "SBMLDocument")
        self.assertEqual(self.sbml_iml.model.__class__.__name__, "Model")
        self.assertIs(self.sbml_iml.tag, None)
        sbml = Sbml.from_sbml(path=MainTest.iml, tag="test")
        self.assertEqual(sbml.tag, "test")

    def test_method(self):
        methods = Sbml.find_method(self.sbml_iml.document, "notes")
        self.assertEqual(methods, ["getNotes"])
        methods = Sbml.find_method(self.sbml_iml.model, "Id")
        self.assertEqual(methods, ["getId"])
        methods = Sbml.find_method(self.sbml_iml.model, "Idl")
        self.assertEqual(methods, ["getAllElementIdList", "getAllElementMetaIdList"])

    def test_format_results(self):
        data = Sbml.format_results(results=[MainTest.node_one_dict])
        self.assertEqual(len(data), 1)
        self.assertEqual(len(data[0].keys()), len(MainTest.node_one_dict.keys()))
        data = Sbml.format_results(results=[MainTest.node_two_dict])
        self.assertNotIn("null_one", data[0].keys())
        self.assertNotIn("null_two", data[0].keys())
        self.assertEqual(len(data[0].keys()), 4)

    def test_format_nodes(self):
        node_two = Node.from_dict(data=MainTest.node_two_dict)
        nodes = self.sbml_iml.format_nodes(nodes=[node_two])
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

    def test_format_relationships_forward(self):
        nodes = self.sbml_toy.format_nodes(nodes=[self.node_two, self.node_three])
        # Relationship - forward
        rel_one = Relationship.from_dict(data=MainTest.rel_one_dict)
        rels = self.sbml_toy.format_relationships(relationships=[rel_one])
        self.assertEqual(
            rels,
            [
                {
                    "left": "Species",
                    "left_id": "M_octapb_c",
                    "relationship": "HAS_COMPARTMENT",
                    "right": "Compartment",
                    "right_id": "c",
                },
                {
                    "left": "Species",
                    "left_id": "M_cysi__L_e",
                    "relationship": "HAS_COMPARTMENT",
                    "right": "Compartment",
                    "right_id": "e",
                },
                {
                    "left": "Species",
                    "left_id": "M_dhap_c",
                    "relationship": "HAS_COMPARTMENT",
                    "right": "Compartment",
                    "right_id": "c",
                },
            ],
        )

    def test_format_relationships_reverse(self):
        nodes = self.sbml_toy.format_nodes(nodes=[self.node_two, self.node_three])
        # Relationship - reverse
        rel_two = Relationship.from_dict(data=MainTest.rel_two_dict)
        rels = self.sbml_toy.format_relationships(relationships=[rel_two])
        self.assertEqual(
            rels,
            [
                {
                    "left": "Compartment",
                    "left_id": "c",
                    "relationship": "IN_COMPARTMENT",
                    "right": "Species",
                    "right_id": "M_octapb_c",
                },
                {
                    "left": "Compartment",
                    "left_id": "e",
                    "relationship": "IN_COMPARTMENT",
                    "right": "Species",
                    "right_id": "M_cysi__L_e",
                },
                {
                    "left": "Compartment",
                    "left_id": "c",
                    "relationship": "IN_COMPARTMENT",
                    "right": "Species",
                    "right_id": "M_dhap_c",
                },
            ],
        )
