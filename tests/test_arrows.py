from neo4jsbml import arrows


class TestNode:
    def test_from_dict(self, node_one_dict):
        node = arrows.Node.from_dict(data=node_one_dict)
        assert node.id == "n11"
        assert node.labels == ["Model"]
        assert node.properties == dict(
            id="str", name="str", metaid="str", sboTerm="str"
        )

    def test_to_dict(self, node_one_dict):
        node = arrows.Node.from_dict(data=node_one_dict)
        assert node.to_dict() == node_one_dict

    def test_repr(self, node_one_dict):
        node = arrows.Node.from_dict(data=node_one_dict)
        assert str(node) == str(node_one_dict)


class TestRelationship:
    def test_from_dict(self, rel_one_dict):
        rel = arrows.Relationship.from_dict(data=rel_one_dict)
        assert rel.id == "n21"
        assert rel.from_id == "n13"
        assert rel.to_id == "n12"
        assert rel.label == "HAS_COMPARTMENT"
        assert rel.properties == {}

    def test_to_dict(self, rel_one_dict):
        rel = arrows.Relationship.from_dict(data=rel_one_dict)
        del rel_one_dict["style"]
        assert rel.to_dict() == rel_one_dict

    def test_repr(self, rel_one_dict):
        rel = arrows.Relationship.from_dict(data=rel_one_dict)
        del rel_one_dict["style"]
        assert str(rel) == str(rel_one_dict)


class TestArrows:
    def test_load(self, pathway_one_path):
        arrow = arrows.Arrows.from_json(path=pathway_one_path)

        assert len(arrow.nodes) == 4
        assert arrow.nodes[-1].id == "n21"
        assert len(arrow.relationships) == 6
        assert arrow.relationships[-1].id == "n34"
