import networkx as nx
from neo4jsbml import arrows


class TestArrows:
    def test_load(self, pathway_one_path):
        arrow = arrows.Arrows.from_json(path=pathway_one_path)

        assert len(arrow.nodes) == 3
        assert arrow.nodes[-1].id == "n2"
        assert len(arrow.relationships) == 3
        assert arrow.relationships[-1].id == "n2"

    def test_to_graph(self, pathway_one_path):
        arrow = arrows.Arrows.from_json(path=pathway_one_path)

        # Build Graph
        graph = nx.MultiDiGraph()
        graph.add_node(
            "n0",
            labels=["Species"],
            properties=dict(
                id="str",
                metaid="str",
                name="str",
                sboTerm="int",
                initialAmount="float",
                hasOnlySubstanceUnits="bool",
                boundaryCondition="bool",
                constant="bool",
            ),
        )
        graph.add_node(
            "n1",
            labels=["Reaction"],
            properties=dict(id="str", metaid="str", name="str", sboTerm="str"),
        )
        graph.add_node(
            "n2",
            labels=["Compartment"],
            properties=dict(
                id="str",
                metaid="str",
                name="str",
                sboTerm="int",
                spatialDimensions="int",
                size="int",
                constant="bool",
            ),
        )

        graph.add_edge(
            "n0",
            "n1",
            id="n1",
            from_label="",
            to_label="",
            from_id="n0",
            to_id="n1",
            label="IS_REACTANT",
            properties=dict(),
        )
        graph.add_edge(
            "n1",
            "n0",
            id="n0",
            from_label="",
            to_label="",
            from_id="n1",
            to_id="n0",
            label="HAS_PRODUCT",
            properties=dict(),
        )

        graph.add_edge(
            "n0",
            "n2",
            id="n2",
            from_label="",
            to_label="",
            from_id="n0",
            to_id="n2",
            label="HAS_COMPARTMENT",
            properties=dict(),
        )

        # Compare Graph
        assert nx.utils.graphs_equal(arrow.to_graph(), graph)
