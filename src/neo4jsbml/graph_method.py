import collections
import itertools
import json
import logging
from collections.abc import Iterable
from typing import Any, Dict, List, Optional, Union

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

    @classmethod
    from_json(path: str) -> Arrows
        Create an Arrows object from a JSON file
    """

    def __init__(self, graph: nx.DiGraph) -> None:
        self.graph = graph

    def annotate(self, modelisation: arrows.Arrows) -> None:
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
        label_duplicates = self.select_labels(uniq=False)
        for node_id in self.graph.nodes:
            label = self.graph.nodes[node_id]["labels"]
            # Skip
            if label not in label_duplicates:
                continue
            # To flag
            for arrows_node in arrows_graph.nodes:
                if GraphMethod.compare_labels(
                    first=label, second=arrows_graph.nodes[arrows_node]["labels"]
                ):
                    predecessor = None
                    predecessors = list(self.graph.predecessors(node_id))
                    if len(predecessors) != 1:
                        continue
                    predecessor = predecessors[0]
                    # General case
                    is_found = False
                    for arrows_neighbor in nx.all_neighbors(arrows_graph, arrows_node):
                        if GraphMethod.compare_labels(
                            first=self.graph.nodes[predecessor]["labels"],
                            second=arrows_graph.nodes[arrows_neighbor]["labels"],
                        ):
                            self.graph.nodes[predecessor]["modelisation"] = True
                            is_found = True
                            break
                    # If first level has no neighbor, it's valid
                    if is_found or (
                        self.graph.nodes[node_id]["level"] == 1 and is_found is False
                    ):
                        self.graph.nodes[node_id]["modelisation"] = True
                        self.graph.nodes[node_id]["properties"] = arrows_graph.nodes[
                            arrows_node
                        ]["properties"]

        for node_id in self.graph.nodes:
            if "modelisation" not in self.graph.nodes[node_id].keys():
                self.graph.nodes[node_id]["modelisation"] = False

    def retrieve_id(self, prop: str, value: str) -> Optional[str]:
        candidates = []
        for node in self.graph.nodes:
            cur_prop = self.graph.nodes[node].get(prop)
            if cur_prop and cur_prop == value:
                candidates.append(node)
        if len(candidates) == 1:
            return candidates[0]
        return None

    def select_labels(self, uniq: bool = False) -> List[str]:
        labels = [self.graph.nodes[x]["labels"] for x in self.graph.nodes()]
        counter: collections.Counter = collections.Counter()
        counter.update(labels)
        if uniq:
            return [key for key, value in counter.items() if value < 2]
        return [key for key, value in counter.items() if value > 1]

    @classmethod
    def compare_labels(
        cls, first: Union[str, Iterable], second: Union[str, Iterable]
    ) -> bool:
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
