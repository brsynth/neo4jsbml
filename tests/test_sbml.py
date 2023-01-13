import pytest
from neo4jsbml.arrows import Node, Relationship
from neo4jsbml.sbml import Sbml


@pytest.fixture(scope="function")
def node_two(node_two_dict):
    return Node.from_dict(data=node_two_dict)


@pytest.fixture(scope="function")
def node_three(node_three_dict):
    return Node.from_dict(data=node_three_dict)


class TestSbml:
    def test_load(self, iml_path, sbml_iml):
        assert sbml_iml.document.__class__.__name__ == "SBMLDocument"
        assert sbml_iml.model.__class__.__name__ == "Model"
        assert sbml_iml.tag is None
        sbml = Sbml.from_sbml(path=iml_path, tag="test")
        assert sbml.tag == "test"

    def test_method(self, sbml_iml):
        methods = Sbml.find_method(sbml_iml.document, "notes")
        assert methods == ["getNotes"]
        methods = Sbml.find_method(sbml_iml.model, "Id")
        assert methods == ["getId"]
        methods = Sbml.find_method(sbml_iml.model, "Idl")
        assert methods == ["getAllElementIdList", "getAllElementMetaIdList"]

    def test_format_results_empty(self, node_one_dict):
        data = Sbml.format_results(results=[node_one_dict])
        assert len(data) == 1
        assert len(data[0].keys()) == len(node_one_dict.keys())

    def test_format_results_effective(self, node_two_dict):
        data = Sbml.format_results(results=[node_two_dict])
        assert "null_one" not in data[0].keys()
        assert "null_two" not in data[0].keys()
        assert len(data[0].keys()) == 4

    def test_format_nodes(self, sbml_iml, node_two_dict):
        node_two = Node.from_dict(data=node_two_dict)
        nodes = sbml_iml.format_nodes(nodes=[node_two])
        assert nodes == [
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
        ]

    def test_format_relationships_forward(
        self, sbml_toy, rel_one_dict, node_two, node_three
    ):
        sbml_toy.format_nodes(nodes=[node_two, node_three])
        # Relationship - forward
        rel_one = Relationship.from_dict(data=rel_one_dict)
        rels = sbml_toy.format_relationships(relationships=[rel_one])
        assert rels == [
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
        ]

    def test_format_relationships_reverse(
        self, sbml_toy, rel_two_dict, node_two, node_three
    ):
        sbml_toy.format_nodes(nodes=[node_two, node_three])
        # Relationship - reverse
        rel_two = Relationship.from_dict(data=rel_two_dict)
        rels = sbml_toy.format_relationships(relationships=[rel_two])
        assert rels == [
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
        ]
