from neo4jsbml import snode


class TestNode:
    def test_from_dict(self, node_one_dict):
        nod = snode.SNode.from_dict(data=node_one_dict)
        assert nod.id == "n11"
        assert nod.labels == ["Model"]
        assert nod.properties == dict(id="str", name="str", metaid="str", sboTerm="str")

    def test_to_dict(self, node_one_dict):
        nod = snode.SNode.from_dict(data=node_one_dict)
        assert nod.to_dict() == node_one_dict

    def test_repr(self, node_one_dict):
        nod = snode.SNode.from_dict(data=node_one_dict)
        assert str(nod) == str(node_one_dict)

    def test_clean_properties(self, node_one_dict):
        nod = snode.SNode.from_dict(data=node_one_dict)
        assert len(nod.properties.keys()) == len(node_one_dict["properties"].keys())
        nod.clean_properties()
        assert len(nod.properties.keys()) == len(node_one_dict["properties"].keys())
        nod.add_property(label="null_one", value="")
        print(nod.properties)
        assert len(nod.properties.keys()) == len(node_one_dict["properties"].keys()) + 1
        nod.clean_properties()
        assert len(nod.properties.keys()) == len(node_one_dict["properties"].keys())
