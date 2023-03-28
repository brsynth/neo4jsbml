import configparser
import logging
from typing import Any, Dict, List, Optional

import neo4j

from neo4jsbml import _version, singleton, snode, srelationship


class Connect(metaclass=singleton.Singleton):
    """Connect

    Attributes
    ----------
    protocol: str (default: neo4j)
        the name of the protocol to connect to the database
    database: str (default: neo4j)
        database name
    url: str (default: localhost)
        the domain name
    port: int (default: 7687)
        the port number to connect to the database
    user: str (default: neo4j)
        the username to connect to the database
    password: Optional[str]
        the password to connect to the database
    password_path: Optional[str]
        the password provided by a file
    stats: Dict[str, int]
        statistics dictionnary updated by create_nodes(), create_relationships
        Keys: nodes, relationships
        Values: number of inserted entities

    Methods
    -------
    is_connected -> bool
        test if the connection is established

    @classmethod
    def read_password(path: str) -> str
        read a password from a file

    def create_nodes(nodes: List[Dict[str, Any]]) -> None
        insert nodes into Neo4j

    def create_relationships(relations: List[Any]) -> None
        insert relationships into Neo4j

    @classmethod
    def from_config(cls, path: str) -> "Connect"
        create a Connect from an .ini file
    """

    PROTOCOLS = ["neo4j", "neo4j+s", "neo4j+ssc", "bolt", "bolt+s", "bolt+ssc"]

    def __init__(
        self,
        url: str = "localhost",
        protocol: str = "neo4j",
        database: str = "neo4j",
        user: Optional[str] = None,
        port: int = 7687,
        password: Optional[str] = None,
        password_path: Optional[str] = None,
    ) -> None:
        self.protocol = protocol
        self.url = url
        self.port = port

        self.user = user
        self.database = database

        self.password = password
        if password_path is not None:
            self.password = Connect.read_password(path=password_path)
        if self.user is not None:
            self.driver = neo4j.GraphDatabase.driver(
                self.uri, auth=(self.user, self.password)
            )
        else:
            self.driver = neo4j.GraphDatabase.driver(self.uri)
        self.stats: Dict[str, int] = {}

    def is_connected(self) -> bool:
        """Test if the connection is established.

        Return
        ------
        bool
        """
        is_connected = True
        try:
            self.driver.verify_connectivity()
        except neo4j.exceptions.ServiceUnavailable:
            is_connected = False
        return is_connected

    @property
    def uri(self) -> str:
        return self.protocol + "://" + self.url + ":" + str(self.port)

    @classmethod
    def read_password(cls, path: str) -> str:
        """Read a password from a file.

        Parameters
        ----------
        path: str
            a path of the file

        Return
        ------
        str
        """
        with open(path) as fid:
            return fid.read().splitlines()[0]

    def create_nodes(self, nodes: List[snode.SNode]) -> None:
        """Insert nodes into Neo4j.

        Parameters
        ----------
        nodes: List[Dict[str, Any]]
            the nodes to create
        """
        for node in nodes:
            with self.driver.session(default_access_mode=neo4j.WRITE_ACCESS) as session:
                query = (
                    "MERGE (n:"
                    + ":".join(node.labels)
                    + " "
                    + node.id_to_neo4j()
                    + ") ON CREATE SET n += "
                    + node.properties_to_neo4j()
                    + " ON MATCH SET n += "
                    + node.properties_to_neo4j()
                    + " RETURN n;"
                )
                res = session.run(query)
                res.single()

    def create_relationships(
        self, relationships: List[srelationship.SRelationship]
    ) -> None:
        """Insert relationships into Neo4j.

        Parameters
        ----------
        relationships: List[Any]
            the relationships to create
        """
        for rel in relationships:
            with self.driver.session(default_access_mode=neo4j.WRITE_ACCESS) as session:
                query = (
                    "MATCH (a:"
                    + rel.from_label
                    + " "
                    + rel.id_to_neo4j(id='$rel["from_id"]')
                    + ") MATCH (b:"
                    + rel.to_label
                    + " "
                    + rel.id_to_neo4j(id='$rel["to_id"]')
                    + ") MERGE (a)-[r:"
                    + rel.label
                    + ']->(b) ON CREATE SET r += $rel["properties"] RETURN r'
                )
                res = session.run(
                    query,
                    rel=rel.to_dict(),
                )
                res.single()

    def __del__(self):
        """Close the driver"""
        self.driver.close()

    @classmethod
    def from_config(cls, path: str) -> "Connect":
        """Create a Connect from an .ini file

        Parameters
        ----------
        path: str
            a path of an .ini file

        Return
        ------
        Connect
        """
        config = configparser.ConfigParser()
        config.read(path)
        data: Dict[str, Any] = {}
        if config.has_section("connection"):
            section = config["connection"]
            if section.get("protocol"):
                data["protocol"] = section.get("protocol")
            if section.get("url"):
                data["url"] = section.get("url")
            if section.get("port"):
                data["port"] = section.get("port")
        if config.has_section("database"):
            section = config["database"]
            if section.get("user"):
                data["user"] = section.get("user")
            if section.get("name"):
                data["database"] = section.get("name")
            if section.get("password"):
                data["password"] = section.get("password")

        return Connect(**data)
