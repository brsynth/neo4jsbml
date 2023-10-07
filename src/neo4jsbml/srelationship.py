import copy
import json
import logging
from typing import Any, Dict, List, Optional

from neo4jsbml import _version, entity


class SRelationship(entity.Entity):
    """Associate a Relationship from arrows to the Relationship object.
    Inherit from Entity.

    Attributes
    ----------
    from_label: str
        The label of the node starting the relationship
    to_label: str
        The label of the node ending the relationship
    from_id: str
        The "id" of the node starting the relationship
    to_id: str
        The "id" of the node ending the relationship
    label: str
        The "type" as defined by arrows

    Methods
    -------
    __init__(id: str, from_id: str, to_id: str, label: str, properties: Dict[str, str])
        Instanciate a new object. All parameters are required.

    swap() -> None
    Invert "from" and "to" attributes

    @classmethod
    from_arrow(data: Dict[str, Any]) -> "Relationship":
        Create a SRelationship from a dictionary coming from arrow.

    @classmethod
    from_dict(data: Dict[str, Any]) -> Node
        Create a SRelationship from a dictionary

    to_dict() -> Dict[str, Any]
        Map attribute labels with their values

    __repr__()
        Represent a SRelationship as a dictionary
    """

    def __init__(
        self,
        from_label: str,
        to_label: str,
        from_id: str,
        to_id: str,
        label: str,
        *args,
        **kwargs
    ) -> None:
        super(SRelationship, self).__init__(*args, **kwargs)
        self.from_label = from_label
        self.to_label = to_label
        self.from_id = from_id
        self.to_id = to_id
        self.label = label

    def swap(self) -> None:
        """Invert relationships.
        Return
        ------
        None
        """
        from_label = self.from_label
        from_id = self.from_id

        self.from_label = self.to_label
        self.from_id = self.to_id
        self.to_label = from_label
        self.to_id = from_id

    @classmethod
    def from_arrow(cls, data: Dict[str, Any]) -> "SRelationship":
        """Create a SRelationship from a dictionary coming from arrow.

        Parameters
        ----------
        data: Dict[str, Any]
            a dictionary

        Return
        ------
        Relationship
        """
        ndata = dict(
            id=data["id"],
            from_label="",
            to_label="",
            from_id=data["fromId"],
            to_id=data["toId"],
            label=data["type"],
            properties=data["properties"],
        )
        return SRelationship.from_dict(data=ndata)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SRelationship":
        """Create a SRelationship from a dictionary.

        Parameters
        ----------
        data: Dict[str, Any]
            a dictionary

        Return
        ------
        Relationship
        """
        return SRelationship(
            id=data["id"],
            from_label=data["from_label"],
            to_label=data["to_label"],
            from_id=data["from_id"],
            to_id=data["to_id"],
            label=data["label"],
            properties=copy.deepcopy(data["properties"]),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Create a dictionary from a SRelationship.

        Return
        ----------
        Dict[str, Any]
        """
        return dict(
            id=self.id,
            from_label=self.from_label,
            to_label=self.to_label,
            from_id=self.from_id,
            to_id=self.to_id,
            label=self.label,
            properties=self.properties,
        )

    def __repr__(self):
        """Represent a SRelationship as a dictionary.

        Return
        ------
        str
        """
        return str(self.to_dict())
