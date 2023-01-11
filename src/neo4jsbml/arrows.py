import json
from typing import Any, Dict, List


class Node(object):
    def __init__(self, id: str, labels: List[str], properties: Dict[str, str]) -> None:
        self.id = id
        self.labels = labels
        self.properties = properties

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Node":
        return Node(id=data["id"], labels=data["labels"], properties=data["properties"])


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


class Arrows(object):
    def __init__(
        self, nodes: List["Node"], relationships: List["Relationship"]
    ) -> None:
        self.nodes = nodes
        self.relationships = relationships

    @classmethod
    def from_json(cls, path: str) -> "Arrows":
        data = {}
        with open(path) as hd:
            data = json.load(hd)
        # Parsing nodes
        nodes = []
        for node in data["nodes"]:
            nodes.append(Node.from_dict(node))
        # Parsing relationships
        relationships = []
        for relationship in data["relationships"]:
            relationships.append(Relationship.from_dict(relationship))

        return Arrows(nodes=nodes, relationships=relationships)
