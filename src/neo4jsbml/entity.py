import copy
import json
import logging
from abc import ABCMeta
from typing import Any, Dict, List, Optional

from neo4jsbml import _version


class Entity(metaclass=ABCMeta):
    """Associate a Node from arrows to the Node object.

    Attributes
    ----------
    id: str
        The "id" attribute
    properties: Dict[str, str]
        The properties as defined by arrows.
        Key are the name of the property to search in the SBML.
        Values are unused.

    Methods
    -------
    add_property(self, label: str, value: str, overwrite: bool = True) -> None
        Add a property to the properties attribute

    has_property(self, label: str) -> bool
        Check if a node has a property

    clean_properties(self)
        Remove empty values

    id_to_neo4j(self) -> str
        Format id to query Neo4j

    properties_to_neo4j() -> str
        Format properties to insert in query
    """

    def __init__(self, id: str, properties: Dict[str, str], *args, **kwargs) -> None:
        self.id = id
        self.properties = properties

    def clean_properties(self):
        """Remove empty values.

        Return
        ------
        None
        """
        keys = []
        for k, v in self.properties.items():
            if v is None or v == "":
                keys.append(k)
        for k in keys:
            del self.properties[k]

    def has_property(self, label: str) -> bool:
        """Check if a node has a property.

        Parameters
        ----------
        label: str
            a key to check

        Return
        ------
        bool
        """
        if label in self.properties.keys():
            return True
        return False

    def add_property(self, label: str, value: str, overwrite: bool = True) -> None:
        """Add a property to the properties attribute.

        Parameters
        ----------
        label: str
            a key
        value: str
            a value
        overwrite: bool (default: True)
            if the key exists, replace or not the value

        Return
        ------
        None
        """
        if (self.has_property(label=label) and overwrite) or not self.has_property(
            label=label
        ):
            self.properties[label] = value

    def id_to_neo4j(self, id: Optional[str] = None) -> str:
        """Format ids to insert in query

        Parameters
        ----------
        id: str (default: None
        Return
        ------
        str
        """
        data = "{id: "
        if id is None:
            data += '"' + self.id + '"'
        else:
            data += id
        if "tag" in self.properties.keys():
            data += ', tag: "' + self.properties["tag"] + '"'
        data += "}"
        return data

    def properties_to_neo4j(self) -> str:
        """Format properties to insert in query

        Return
        ------
        str
        """
        data = "{"
        for k, v in self.properties.items():
            data += k
            data += ': "'
            data += str(v)
            data += '", '
        data = data[:-2]
        data += "}"
        return data
