import copy
import json
import logging
from typing import Any, Dict, List, Optional

from neo4jsbml import _version, entity


class SNode(entity.Entity):
    """Associate a Node from arrows to the Node object.
    Inherit from Entity

    Attributes
    ----------
    labels: List[str]
        The "labels" as defined by arrows

    Methods
    -------
    __init__(id: str, labels: List[str], properties: Dict[str, str]) -> None
        Instanciate a new object. All parameters are required.

    @classmethod
    from_arrow(cls, data: Dict[str, Any]) -> Node
        Create a SNode from a dictionary coming from arrow

    @classmethod
    from_dict(data: Dict[str, Any]) -> Node
        Create a SNode from a dictionary

    to_dict() -> Dict[str, Any]
        Map attribute labels with their values

    __repr__()
        Represent a SNode as a dictionary
    """

    LABEL_ID = "id"

    def __init__(self, labels: List[str], *args, **kwargs) -> None:
        super(SNode, self).__init__(*args, **kwargs)
        self.labels = labels

    @classmethod
    def from_arrow(cls, data: Dict[str, Any]) -> "Node":
        """Create a Node from a dictionary coming from arrow.

        Parameters
        ----------
        data: Dict[str, Any]
            a dictionary

        Return
        ------
        Node
        """
        return SNode.from_dict(data=data)

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
        return SNode(
            id=data["id"],
            labels=data["labels"],
            properties=copy.deepcopy(data["properties"]),
        )

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
