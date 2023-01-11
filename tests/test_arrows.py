from neo4jsbml.arrows import Arrows
from tests.main_test import Main_test


class TestArrows(Main_test):
    def test_load(self):
        arrow = Arrows.from_json(path=Main_test.pathway_one_json)

        self.assertEqual(len(arrow.nodes), 4)
        self.assertEqual(arrow.nodes[-1].id, "n21")
        self.assertEqual(len(arrow.relationships), 6)
        self.assertEqual(arrow.relationships[-1].id, "n34")
