import json
import logging
from typing import Any, Dict, List

from neo4jsbml import _version


class Node(object):
    """Associate a Node from arrows to the Node object.

    Attributes
    ----------
    id: str
        The "id" as defined by arrows
    labels: List[str]
        The "labels" as defined by arrows
    properties: Dict[str, str]
        The properties as defined by arrows.
        Key are the name of the property to search in the SBML.
        Values are unused.

    Methods
    -------
    __init__(id: str, labels: List[str], properties: Dict[str, str]) -> None
        Instanciate a new object. All parameters are required.

    @classmethod
    from_dict(data: Dict[str, Any]) -> Node
        Create a Node from a dictionary

    to_dict() -> Dict[str, Any]
        Map attribute labels with their values

    __repr__()
        Represent a Node as a dictionary
    """

    LABEL_ID = "id"

    def __init__(self, id: str, labels: List[str], properties: Dict[str, str]) -> None:
        self.id = id
        self.labels = labels
        self.properties = properties

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Node":
        """Create a Node from a dictionary.

        Parameters
        ----------
        data: Dict[str, Any]
            a dictionary

        Return
        ------
        Node
        """
        return Node(id=data["id"], labels=data["labels"], properties=data["properties"])

    def to_dict(self) -> Dict[str, Any]:
        """Create a dictionary from a Node.

        Return
        ----------
        Dict[str, Any]
        """
        return dict(id=self.id, labels=self.labels, properties=self.properties)

    def __repr__(self):
        """Represent a Node as a dictionary.

        Return
        ------
        str
        """
        return str(self.to_dict())


class Relationship(object):
    """Associate a Relationship from arrows to the Relationship object.

    Attributes
    ----------
    id: str
        The "id" as defined by arrows
    from_id: str
        The "id" of the node starting the relationship
    to_id: str
        The "id" of the node ending the relationship
    label: str
        The "type" as defined by arrows
    properties: Dict[str, str]
        The properties as defined by arrows.
        Key are the name of the property to search in the SBML.
        Values are unused.

    Methods
    -------
    __init__(id: str, from_id: str, to_id: str, label: str, properties: Dict[str, str])
        Instanciate a new object. All parameters are required.

    @classmethod
    from_dict(data: Dict[str, Any]) -> Node
        Create a Relationship from a dictionary

    to_dict() -> Dict[str, Any]
        Map attribute labels with their values

    __repr__()
        Represent a Node as a dictionary
    """

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
        """Create a Relationship from a dictionary.

        Parameters
        ----------
        data: Dict[str, Any]
            a dictionary

        Return
        ------
        Relationship
        """
        return Relationship(
            id=data["id"],
            from_id=data["fromId"],
            to_id=data["toId"],
            label=data["type"],
            properties=data["properties"],
        )

    def to_dict(self) -> Dict[str, Any]:
        """Create a dictionary from a Relationship.

        Return
        ----------
        Dict[str, Any]
        """
        return dict(
            id=self.id,
            fromId=self.from_id,
            toId=self.to_id,
            type=self.label,
            properties=self.properties,
        )

    def __repr__(self):
        """Represent a Relationship as a dictionary.

        Return
        ------
        str
        """
        return str(self.to_dict())


class Arrows(object):
    """Store entities as defined by arrows.app

    Attributes
    ----------
    nodes: List[Node]
        Nodes object
    relationships: List[Relationship]
        Relationship object

    Methods
    -------
    __init__(nodes: List["Node"], relationships: Optional[List["Relationship"]])
        Instanciate a new object. nodes parameters is required.

    @classmethod
    from_json(path: str) -> Arrows
        Create an Arrows object from a JSON file
    """

    def __init__(
        self, nodes: List["Node"], relationships: Optional[List["Relationship"]] = None
    ) -> None:
        self.nodes = nodes
        self.relationships = relationships

    @classmethod
    def from_json(cls, path: str) -> "Arrows":
        """Create an Arrows object from a JSON file.
        Add an "id" attribute to the properties or renamed it if it has not the same case
        to identify the node.
        Ignore Relationship which has no type.

        Parameters
        ----------
        path: str
            a JSON file

        Return
        ------
        Arrows
        """
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
