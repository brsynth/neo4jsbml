from neo4jsbml import srelationship


class TestSRelationship:
    def test_from_arrow(self, rel_one_arrow):
        rel = srelationship.SRelationship.from_arrow(data=rel_one_arrow)
        assert rel.id == "n21"
        assert rel.from_id == "n13"
        assert rel.to_id == "n12"
        assert rel.label == "HAS_COMPARTMENT"
        assert rel.properties == {}

    def test_to_dict(self, rel_one_dict):
        rel = srelationship.SRelationship.from_dict(data=rel_one_dict)
        del rel_one_dict["style"]
        assert rel.to_dict() == rel_one_dict

    def test_repr(self, rel_one_dict):
        rel = srelationship.SRelationship.from_dict(data=rel_one_dict)
        del rel_one_dict["style"]
        assert str(rel) == str(rel_one_dict)
