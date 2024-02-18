from neo4jsbml import graph_method


class TestGraphMethod:
    def test_compare_labels(self):
        assert graph_method.GraphMethod.compare_labels(first="A", second="a")
        assert not graph_method.GraphMethod.compare_labels(first="A", second="b")

        assert graph_method.GraphMethod.compare_labels(first="A", second=["a"])
        assert not graph_method.GraphMethod.compare_labels(first="A", second=["b"])

        assert graph_method.GraphMethod.compare_labels(first=["A"], second="a")
        assert not graph_method.GraphMethod.compare_labels(first=["A"], second="b")

        assert graph_method.GraphMethod.compare_labels(first=["A"], second=["a"])
        assert not graph_method.GraphMethod.compare_labels(first=["A"], second=["b"])

        assert graph_method.GraphMethod.compare_labels(
            first=["Compartment"], second=["Compartment"]
        )
