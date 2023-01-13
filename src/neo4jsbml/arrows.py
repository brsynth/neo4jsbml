import json
import logging
from typing import Any, Dict, List

from neo4jsbml import _version


class Node(object):
    LABEL_ID = "id"

    def __init__(self, id: str, labels: List[str], properties: Dict[str, str]) -> None:
        self.id = id
        self.labels = labels
        self.properties = properties

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Node":
        return Node(id=data["id"], labels=data["labels"], properties=data["properties"])

    def to_dict(self) -> Dict[str, Any]:
        return dict(id=self.id, labels=self.labels, properties=self.properties)

    def __repr__(self):
        return str(self.to_dict())


class Relationship(object):
    def __init__(
        self, id: str, from_id: str, to_id: str, label: str, properties: Dict[str, str]
    ) -> None:
        self.id = id
        self.from_id = from_id
        self.to_id = to_id
        self.label = label
        self.properties = properties

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Relationship":
        return Relationship(
            id=data["id"],
            from_id=data["fromId"],
            to_id=data["toId"],
            label=data["type"],
            properties=data["properties"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return dict(
            id=self.id,
            fromId=self.from_id,
            toId=self.to_id,
            type=self.label,
            properties=self.properties,
        )

    def __repr__(self):
        return str(self.to_dict())


class Arrows(object):
    def __init__(
        self, nodes: List["Node"], relationships: List["Relationship"]
    ) -> None:
        self.nodes = nodes
        self.relationships = relationships

    @classmethod
    def from_json(cls, path: str) -> "Arrows":
        logger = logging.getLogger(name=_version.__app_name__)
        data = {}
        with open(path) as hd:
            data = json.load(hd)
        # Parsing nodes
        nodes = []
        for node in data["nodes"]:
            # Check for ID in properties
            is_id_found = False
            id_label = Node.LABEL_ID
            for key in node["properties"].keys():
                if key.lower() == Node.LABEL_ID:
                    is_id_found = True
                    if key != id_label:
                        id_label = key
            if id_label != Node.LABEL_ID:
                node["properties"][Node.LABEL_ID] = node["properties"].pop(id_label)
                logger.warning(
                    'Entity: %s has an "%s" in properties, but it will be renamed into: %s'
                    % (" ".join(node["labels"]), id_label, Node.LABEL_ID)
                )
            if not is_id_found:
                logger.warning(
                    'Entity: %s has not "id" in properties, it will be added'
                )
                node["properties"][Node.LABEL_ID] = "str"
            # Append node
            nodes.append(Node.from_dict(node))
        # Parsing relationships
        relationships = []
        for relationship in data["relationships"]:
            if relationship["type"] == "str":
                logger.warning(
                    "A relationship must be have a type filled, %s will be skipped"
                    % (relationship["id"],)
                )
                continue
            relationships.append(Relationship.from_dict(relationship))
        return Arrows(nodes=nodes, relationships=relationships)
