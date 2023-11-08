import json
import logging
from typing import Any, Dict, List, Optional

import networkx as nx
from neo4jsbml import _version, snode, srelationship


class Arrows(object):
    """Store entities as defined by arrows.app

    Attributes
    ----------
    nodes: List[snode.SNode]
        Nodes object
    relationships: List[srelationship.SRelationship]
        Relationship object

    Methods
    -------
    __init__(nodes: List[snode.SNode], relationships: Optional[List["srelationship.SRelationship"]])
        Instanciate a new object. nodes parameters is required.

    @classmethod
    from_json(path: str) -> Arrows
        Create an Arrows object from a JSON file
    """

    def __init__(
        self,
        nodes: List[snode.SNode],
        relationships: Optional[List[srelationship.SRelationship]] = None,
    ) -> None:
        self.nodes = nodes
        self.relationships = relationships

    def to_graph(self) -> nx.MultiGraph:
        """Convert Arrows object to a networkx graph.

        Return
        ------
        nx.MultiGraph
        """
        graph = nx.MultiGraph()
        for snode in self.nodes:
            data = snode.to_dict()
            node_id = data.pop("id")
            graph.add_node(snode.id, **data)
        if self.relationships:
            for srelationship in self.relationships:
                data = srelationship.to_dict()
                from_id = data.pop("from_id")
                to_id = data.pop("to_id")
                graph.add_edge(from_id, to_id, **data)
        return graph

    @classmethod
    def from_json(cls, path: str) -> "Arrows":
        """Create an Arrows object from a JSON file.
        Add an "id" attribute to the properties or renamed it if it has not the same case
        to identify the node.
        Ignore SRelationship which has no type.

        Parameters
        ----------
        path: str
            a JSON file

        Return
        ------
        Arrows
        """
        data = {}
        with open(path) as hd:
            data = json.load(hd)
        # Parsing nodes
        nodes = []
        for arrow_node in data["nodes"]:
            # Check for ID in properties
            is_id_found = False
            id_label = snode.SNode.LABEL_ID
            for key in arrow_node["properties"].keys():
                if key.lower() == snode.SNode.LABEL_ID:
                    is_id_found = True
                    if key != id_label:
                        id_label = key
            if id_label != snode.SNode.LABEL_ID:
                arrow_node["properties"][snode.SNode.LABEL_ID] = arrow_node[
                    "properties"
                ].pop(id_label)
                logging.warning(
                    'Entity: %s has an "%s" in properties, but it will be renamed into: %s'
                    % (":".join(arrow_node["labels"]), id_label, snode.SNode.LABEL_ID)
                )
            if not is_id_found:
                logging.warning(
                    'Entity: %s has not "id" in properties, it will be added'
                    % (":".join(arrow_node["labels"]),)
                )
                arrow_node["properties"][snode.SNode.LABEL_ID] = "str"
            # Append node
            nodes.append(snode.SNode.from_dict(arrow_node))
        # Parsing relationships
        relationships = []
        for arrow_rel in data["relationships"]:
            if arrow_rel["type"] == "str":
                logging.warning(
                    "A relationship must be have a type filled, %s will be skipped"
                    % (arrow_rel["id"],)
                )
                continue
            relationships.append(srelationship.SRelationship.from_arrow(arrow_rel))
        return Arrows(nodes=nodes, relationships=relationships)
