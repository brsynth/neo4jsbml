import json
import logging
from typing import Any, Dict, List, Optional

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
            cur_id = self.retrieve_id(prop="label", value=label)
            is_found = False
            for arrows_node in arrows_graph.nodes:
                if label in arrows_node.label:
                    self.graph.nodes[cur_id]["modelisation"] = True
                    is_found = True
                    break
            if is_found is False:
                self.graph.nodes[cur_id]["modelisation"] = False
        # Label not uniques
        for label in self.select_labels(uniq=False):
            is_found = False
            for arrows_node in arrows_graph.nodes:
                if label in arrows_node.label:
                    is_found = True
                    break
            # Not retained
            if is_found is False:
                for node_id in self.graph.nodes:
                    if self.graph.nodes[node_id]["label"] == label:
                        self.graph.nodes[node_id]["modelisation"] = False
                continue
            # To flag
            for node_id in self.graph.nodes:
                is_found = False
                if self.graph.nodes[node_id]["label"] == label:
                    predecessor = None
                    predecessors = self.graph.predecessor(node_id)
                    if len(predecessors) != 1:
                        continue
                    predecessor = predecessors[0]
                    # General case
                    for arrows_node in arrows_graph.nodes:
                        if label in arrows_graph.nodes[arrows_node]:
                            for arrows_predecessor in nx.all_neighbors(
                                arrows_graph, arrows_node
                            ):
                                if (
                                    predecessor
                                    in arrows_graph.nodes[arrows_predecessor]["label"]
                                ):
                                    self.graph.nodes[node_id]["modelisation"] = True
                                    self.graph.nodes[predecessor]["modelisation"] = True
                                    is_found = True
                                    break
                        if is_found:
                            break
                    # If first level has no neighbor, it's valid
                    if self.graph.nodes[node_id]["level"] == 1 and is_found is False:
                        self.graph.nodes[node_id]["modelisation"] = True

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
        labels = [x["label"] for x in self.graph.nodes()]
        counter = collections.Counter()
        counter.update(labels)
        if uniq:
            return [key for key, value in counter.items() if value < 2]
        return [key for key, value in counter.items() if value > 1]

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

        def _add_leaf(graph: nx.DiGraph(), count: int, level: int):
            # max_level = max(set([G.nodes[label]["level"] for label in G.nodes]))
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
                        graph.add_node(count, label=label, level=level + 1, obj=obj)
                        graph.add_edge(node_id, count)
            if len(node_ids) == len(graph.nodes):
                return graph
            return _add_leaf(graph=graph, count=count, level=level + 1)

        graph = nx.DiGraph()
        model = document.createModel()
        graph.add_node(0, method="Model", level=0, obj=model)
        graph = _add_leaf(graph=graph, count=1, level=0)
        return GraphMethod(graph=graph)
