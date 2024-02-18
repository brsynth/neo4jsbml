import collections
import itertools
import json
import logging
from collections.abc import Iterable
from typing import Any, Dict, Generator, List, Optional, Union

import libsbml
import networkx as nx
from neo4jsbml import arrows, snode, srelationship


class GraphMethod(object):
    """Store methods to create SBML as defined by libsbml

    Attributes
    ----------
    graph: networkx.DiGraph()
        Methods of libsbml

    Methods
    -------
    __init__(nodes: List[snode.SNode], relationships: Optional[List["srelationship.SRelationship"]])
        Instanciate a new object. nodes parameters is required.

    annotate(self, modelisation: arrows.Arrows) -> None
        Map a schema coming from a modelisation to the graph attribute

    annotate(self, modelisation: arrows.Arrows) -> None
        Map a schema coming from a modelisation to the graph attribute

    retrieve_id(self, prop: str, value: str) -> Optional[str]
        Given a key and its value retrieve the id

    select_labels(self, uniq: bool = False) -> List[str]
        Retrive all labels property in the properties node

    @classmethod
    compare_labels(cls, first: Union[str, Iterable], second: Union[str, Iterable]) -> bool
        Compare two sequences

    @classmethod
    def generate_pairs(cls, graph: nx.Graph) -> Generator:
        For each node of a graph, a tuple outputs the id of the node and a neighbor

    @classmethod
    from_json(path: str) -> Arrows
        Create an Arrows object from a JSON file
    """

    def __init__(self, graph: nx.DiGraph) -> None:
        self.graph = graph

    def annotate(self, modelisation: arrows.Arrows) -> None:
        """Map a schema coming from a modelisation to the graph attribute

        Parameters
        ----------
        modelisation: arrows.Arrows
            A schema coming from arrows

        Return
        ------
        None
        """
        arrows_graph = modelisation.to_graph()
        # Label uniques
        for label in self.select_labels(uniq=True):
            cur_id = self.retrieve_id(prop="labels", value=label)
            for arrows_node in arrows_graph.nodes:
                if GraphMethod.compare_labels(
                    first=label, second=arrows_graph.nodes[arrows_node]["labels"]
                ):
                    self.graph.nodes[cur_id]["modelisation"] = True
                    self.graph.nodes[cur_id]["properties"] = arrows_graph.nodes[
                        arrows_node
                    ]["properties"]
                    break
        # Label not uniques, compare node with its predecessor both in graph_methods <-> arrows
        arrows_graph_undirected = arrows_graph.to_undirected()
        label_duplicates = self.select_labels(uniq=False)
        model_id = self.retrieve_id(prop="labels", value="Model")
        for node_id in self.graph.nodes:
            label = self.graph.nodes[node_id]["labels"]
            # Skip
            if label not in label_duplicates:
                continue
            if nx.has_path(self.graph, source=model_id, target=node_id) is False:
                continue
            graph_path = nx.shortest_path(self.graph, source=model_id, target=node_id)
            graph_path = graph_path[::-1]
            graph_path_labels = [self.graph.nodes[x]["labels"] for x in graph_path]

            for arrows_node in arrows_graph_undirected.nodes:
                if GraphMethod.compare_labels(
                    first=label,
                    second=arrows_graph_undirected.nodes[arrows_node]["labels"],
                ):
                    predecessors = nx.dfs_predecessors(
                        arrows_graph_undirected,
                        source=arrows_node,
                        depth_limit=len(graph_path),
                    )
                    arrows_path = []
                    for ix, (key, value) in enumerate(predecessors.items()):
                        if ix < 1:
                            arrows_path.append(value)
                        arrows_path.append(key)
                    arrows_path = arrows_path[: len(graph_path)]
                    arrows_path_labels = [
                        arrows_graph_undirected.nodes[x]["labels"][0]
                        for x in arrows_path
                    ]
                    # Check perfect match
                    is_matched = False
                    if GraphMethod.compare_labels(
                        first=graph_path_labels, second=arrows_path_labels
                    ):
                        is_matched = True
                    """
                    # Partial match, not considering Model entity
                    else:
                        short_graph_path_labels = graph_path_labels[:-1]
                        short_arrows_path_labels = arrows_path_labels[:-1]
                        if len(
                            short_graph_path_labels
                        ) > 1 and GraphMethod.compare_labels(
                            first=short_graph_path_labels,
                            second=short_arrows_path_labels,
                        ):
                            is_matched = True
                    """
                    if is_matched:
                        for gp_node in graph_path:
                            self.graph.nodes[gp_node]["modelisation"] = True
                        # self.graph.nodes[node_id]["modelisation"] = True
                        self.graph.nodes[node_id]["properties"] = arrows_graph.nodes[
                            arrows_node
                        ]["properties"]
                        break
        # Flag nodes based on relationship's name
        for pair_gm, pair_arrow in itertools.product(
            GraphMethod.generate_pairs(graph=self.graph),
            GraphMethod.generate_pairs(graph=arrows_graph),
        ):
            label_gm_n = self.graph.nodes[pair_gm[0]]["labels"]
            label_gm_n1 = self.graph.nodes[pair_gm[1]]["labels"]
            label_arrows_n = arrows_graph.nodes[pair_arrow[0]]["labels"]
            label_arrows_n1 = arrows_graph.nodes[pair_arrow[1]]["labels"]

            if GraphMethod.compare_labels(
                first=label_gm_n, second=label_arrows_n
            ) and GraphMethod.compare_labels(first=label_gm_n1, second=label_arrows_n1):
                continue

            relationships = arrows_graph.get_edge_data(*pair_arrow)
            if relationships is None:
                continue

            if GraphMethod.compare_labels(first=label_gm_n, second=label_arrows_n):
                for relationship in relationships.values():
                    for chunk in relationship["label"].split("_"):
                        if GraphMethod.compare_labels(first=chunk, second=label_gm_n1):
                            if (
                                "modelisation"
                                not in self.graph.nodes[pair_gm[1]].keys()
                            ):
                                self.graph.nodes[pair_gm[0]]["modelisation"] = True
                                self.graph.nodes[pair_gm[1]]["modelisation"] = True
                                self.graph.nodes[pair_gm[1]][
                                    "properties"
                                ] = arrows_graph.nodes[pair_arrow[1]]["properties"]
                                self.graph.nodes[pair_gm[1]][
                                    "labels_arrows"
                                ] = label_arrows_n1[0]
                                self.graph.nodes[pair_gm[1]][
                                    "relationship"
                                ] = relationship
                                break
            elif GraphMethod.compare_labels(first=label_gm_n1, second=label_arrows_n1):
                for relationship in relationships.values():
                    for chunk in relationship["label"].split("_"):
                        if GraphMethod.compare_labels(first=chunk, second=label_gm_n):
                            if (
                                "modelisation"
                                not in self.graph.nodes[pair_gm[0]].keys()
                            ):
                                self.graph.nodes[pair_gm[1]]["modelisation"] = True
                                self.graph.nodes[pair_gm[0]]["modelisation"] = True
                                self.graph.nodes[pair_gm[0]][
                                    "properties"
                                ] = arrows_graph.nodes[pair_arrow[0]]["properties"]
                                self.graph.nodes[pair_gm[0]][
                                    "labels_arrows"
                                ] = label_arrows_n[0]
                                self.graph.nodes[pair_gm[0]][
                                    "relationship"
                                ] = relationship
                                break

        for node_id in self.graph.nodes:
            if "modelisation" not in self.graph.nodes[node_id].keys():
                self.graph.nodes[node_id]["modelisation"] = False

    def retrieve_id(self, prop: str, value: str) -> str:
        """Given a key and its value retrieve the id

        Parameters
        ----------
        prop: str
            A property, a key
        value: str
            A value associated to a property

        Return
        ------
        str
        """
        candidates = []
        for node in self.graph.nodes:
            cur_prop = self.graph.nodes[node].get(prop)
            if cur_prop and cur_prop == value:
                candidates.append(node)
        if len(candidates) == 1:
            return candidates[0]
        return ""

    def select_labels(self, uniq: bool = False) -> List[str]:
        """Retrive all labels property in the properties node

        Parameters
        ----------
        uniq: bool
            Select unique nodes or nodes

        Return
        ------
        List[str]
        """
        labels = [self.graph.nodes[x]["labels"] for x in self.graph.nodes()]
        counter: collections.Counter = collections.Counter()
        counter.update(labels)
        if uniq:
            return [key for key, value in counter.items() if value < 2]
        return [key for key, value in counter.items() if value > 1]

    def get_level_max(self) -> int:
        """Get the maximum level.

        Return
        ------
        int
        """
        levels = []
        for node in self.graph.nodes:
            levels.append(self.graph.nodes[node].get("level", -1))
        return max(levels)

    def generate_node(self, level: int) -> Generator:
        """Generate nodeId for a specific level

        Parameters
        ----------
        level: int
            Specific level

        Return
        ------
        Generator
        """
        for node in self.graph.nodes:
            if self.graph.nodes[node]["level"] == level:
                yield node

    @classmethod
    def compare_labels(
        cls, first: Union[str, Iterable], second: Union[str, Iterable]
    ) -> bool:
        """Compare two sequences

        Parameters
        ----------
        first: str, List[str]
            a first sequence
        second:
            str, List[str]
            a second sequence

        Return
        ------
        bool
        """
        # Format
        if isinstance(first, str):
            first = first.lower()
        else:
            first = sorted([x.lower() for x in first])
        if isinstance(second, str):
            second = second.lower()
        else:
            second = sorted([x.lower() for x in second])
        # Compare
        if isinstance(first, str) and isinstance(second, str):
            return first == second
        elif isinstance(first, str):
            return first == second[0]
        elif isinstance(second, str):
            return first[0] == second
        return first == second

    @classmethod
    def generate_pairs(cls, graph: nx.Graph) -> Generator:
        """For each node of a graph, a tuple outputs the id of the node and a neighbor

        Parameters
        ----------
        graph: nx.Graph
            A networkx graph

        Return
        ------
        Generator[Tuple[str, str]]
        """
        for node_id in graph.nodes:
            for neigh_id in nx.all_neighbors(graph, node_id):
                if node_id == neigh_id:
                    continue
                yield node_id, neigh_id

    @classmethod
    def from_document(cls, document: libsbml.SBMLDocument) -> "GraphMethod":
        """
        Parameters
        ----------
        document: libsbml.SBMLDocument
            a SBML Document

        Return
        ------
        nx.DiGraph
        """

        def _add_leaf(graph: nx.DiGraph, count: int, level: int):
            node_ids = list(graph.nodes)
            for node_id in node_ids:
                if graph.nodes[node_id]["level"] < level:
                    continue
                # List method
                cur_obj = graph.nodes[node_id]["obj"]
                methods = eval("cur_obj.__dir__()")
                methods = [x for x in methods if x.startswith("create")]
                for method in methods:
                    if not method.startswith("create"):
                        continue
                    obj = eval("cur_obj." + method + "()")
                    if obj:
                        label = method.replace("create", "")
                        count += 1
                        graph.add_node(count, labels=label, level=level + 1, obj=obj)
                        graph.add_edge(node_id, count)
                del cur_obj  # rm warning var unused
            if len(node_ids) == len(graph.nodes):
                return graph
            return _add_leaf(graph=graph, count=count, level=level + 1)

        graph = nx.DiGraph()
        model = document.createModel()
        graph.add_node(0, labels="Model", level=0, obj=model)
        graph = _add_leaf(graph=graph, count=1, level=0)
        # Clean up
        for node in graph.nodes:
            del graph.nodes[node]["obj"]
        return GraphMethod(graph=graph)
