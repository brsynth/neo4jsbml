from neo4jsbml import arrows


class TestArrows:
    def test_load(self, pathway_one_path):
        arrow = arrows.Arrows.from_json(path=pathway_one_path)

        assert len(arrow.nodes) == 3
        assert arrow.nodes[-1].id == "n2"
        assert len(arrow.relationships) == 3
        assert arrow.relationships[-1].id == "n2"
