from neo4jsbml.arrows import Arrows


class TestArrows:
    def test_load(self, pathway_one_path):
        arrow = Arrows.from_json(path=pathway_one_path)

        assert len(arrow.nodes) == 4
        assert arrow.nodes[-1].id == "n21"
        assert len(arrow.relationships) == 6
        assert arrow.relationships[-1].id == "n34"
