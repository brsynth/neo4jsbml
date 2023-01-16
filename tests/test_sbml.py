import pytest
from neo4jsbml.sbml import Sbml
from neo4jsbml.snode import SNode
from neo4jsbml.srelationship import SRelationship


@pytest.fixture(scope="function")
def node_two(node_two_dict):
    return SNode.from_dict(data=node_two_dict)


@pytest.fixture(scope="function")
def node_three(node_three_dict):
    return SNode.from_dict(data=node_three_dict)


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

    def test_format_nodes(self, sbml_iml, node_two_dict):
        node_two = SNode.from_dict(data=node_two_dict)
        nodes = sbml_iml.format_nodes(nodes=[node_two])
        lnodes = [x.to_dict() for x in nodes]
        res = [
            {
                "id": "c",
                "labels": ["Compartment"],
                "properties": {
                    "name": "cytosol",
                    "sboTerm": -1,
                    "spatialDimensions": 0,
                },
            },
            {
                "id": "e",
                "labels": ["Compartment"],
                "properties": {
                    "name": "extracellular space",
                    "sboTerm": -1,
                    "spatialDimensions": 0,
                },
            },
            {
                "id": "p",
                "labels": ["Compartment"],
                "properties": {
                    "name": "periplasm",
                    "sboTerm": -1,
                    "spatialDimensions": 0,
                },
            },
        ]

        assert lnodes == res

    def test_format_relationships_forward(
        self, sbml_toy, rel_one_dict, node_two, node_three
    ):
        sbml_toy.format_nodes(nodes=[node_two, node_three])
        # Relationship - forward
        rel_one = SRelationship.from_dict(data=rel_one_dict)
        rels = sbml_toy.format_relationships(relationships=[rel_one])
        lrels = [x.to_dict() for x in rels]
        res = [
            {
                "id": "",
                "from_label": "Species",
                "to_label": "Compartment",
                "from_id": "M_octapb_c",
                "to_id": "c",
                "label": "HAS_COMPARTMENT",
                "properties": {},
            },
            {
                "id": "",
                "from_label": "Species",
                "to_label": "Compartment",
                "from_id": "M_cysi__L_e",
                "to_id": "e",
                "label": "HAS_COMPARTMENT",
                "properties": {},
            },
            {
                "id": "",
                "from_label": "Species",
                "to_label": "Compartment",
                "from_id": "M_dhap_c",
                "to_id": "c",
                "label": "HAS_COMPARTMENT",
                "properties": {},
            },
        ]
        assert lrels == res

    def test_format_relationships_reverse(
        self, sbml_toy, rel_two_dict, node_two, node_three
    ):
        sbml_toy.format_nodes(nodes=[node_two, node_three])
        # Relationship - reverse
        rel_two = SRelationship.from_dict(data=rel_two_dict)
        rels = sbml_toy.format_relationships(relationships=[rel_two])
        lrels = [x.to_dict() for x in rels]
        res = [
            {
                "id": "",
                "from_label": "Compartment",
                "to_label": "Species",
                "from_id": "c",
                "to_id": "M_octapb_c",
                "label": "IN_COMPARTMENT",
                "properties": {},
            },
            {
                "id": "",
                "from_label": "Compartment",
                "to_label": "Species",
                "from_id": "e",
                "to_id": "M_cysi__L_e",
                "label": "IN_COMPARTMENT",
                "properties": {},
            },
            {
                "id": "",
                "from_label": "Compartment",
                "to_label": "Species",
                "from_id": "c",
                "to_id": "M_dhap_c",
                "label": "IN_COMPARTMENT",
                "properties": {},
            },
        ]
        assert lrels == res
