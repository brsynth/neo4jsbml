import configparser
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
    user: str (default: neo4j)
        the username to connect to the database
    port: Optional[str]
        the port number to connect to the database
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
        protocol: str = "7687",
        database: str = "neo4j",
        user: Optional[str] = None,
        port: Optional[str] = None,
        password: Optional[str] = None,
        password_path: Optional[str] = None,
    ) -> None:
        self.url = url
        self.protocol = protocol
        self.database = database
        self.user = user
        self.port = port
        self.password = password
        if password_path:
            self.password = Connect.read_password(path=password_path)
        if self.user:
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
        if self.port:
            return self.protocol + "://" + self.url + ":" + str(self.port)
        return self.protocol + "://" + self.url

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
                que = (
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
                res = session.run(que)
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
                que = (
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
                    que,
                    rel=rel.to_dict(),
                )
                res.single()

    def query_labels(self) -> List:
        """Return all labels found in the database.

        Return
        ------
        Optional[List[str, Any]]
        """
        que = "MATCH (n) RETURN labels(n) AS label"
        res = self.query(value=que, expect_data=True, access=neo4j.READ_ACCESS)
        if res:
            return res
        return []

    def query_node(self, label: str) -> List:
        """Return all nodes based on a label with their ids.

        Parameters
        ----------
        label: str
            A label to query nodes

        Return
        ------
        Optional[List[str, Any]]
        """
        with self.driver.session(
            database=self.database, default_access_mode=neo4j.READ_ACCESS
        ) as session:
            res = session.run(
                "MATCH (n: " + label + ") RETURN n AS node, elementId(n) AS nodeId",
            )
            return res.data()

    def query_neighbor(self, elementId: str) -> List:
        """Return neighbors of a node based on a label.

        Parameters
        ----------
        elementId: str
            An id to select

        Return
        ------
        Optional[List[str, Any]]
        """
        with self.driver.session(
            database=self.database, default_access_mode=neo4j.READ_ACCESS
        ) as session:
            res = session.run(
                "MATCH (n)-[r*1..1]-(m) WHERE elementId(n) = $elementId RETURN m AS nodeNeighbor, labels(m) as nodeLabels, elementId(m) as nodeId, r AS relationship",
                elementId=elementId,
            )
            return res.data()

    def clean(self) -> None:
        """Remove data into Neo4j

        Return
        ------
        None
        """
        with self.driver.session(default_access_mode=neo4j.WRITE_ACCESS) as session:
            res = session.run("MATCH (n) DETACH DELETE n")
            res.single()
            return None

    def query(
        self, value: str, expect_data: bool = False, access: str = neo4j.WRITE_ACCESS
    ) -> Optional[List]:
        """Execute query into Neo4j.

        Parameters
        ----------
        value: str
            the query
        expect_data: bool (default: False)
            return or not a value
        access: str (default: neo4j.WRITE_ACCESS)
            Choices between [neo4j.READ_ACCESS, WRITE_ACCESS]

        Return
        ------
        A list of results if expect_data is set
        """
        with self.driver.session(default_access_mode=access) as session:
            res = session.run(value)
            if expect_data:
                return res.data()
            res.single()
            return None

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

    @classmethod
    def from_auradb(cls, path: str) -> "Connect":
        """Create a Connect from a file provided by AuraDB

        Parameters
        ----------
        path: str
            a path of the file file

        Return
        ------
        Connect
        """
        data: Dict[str, Any] = {}
        with open(path) as fid:
            lines = fid.read().splitlines()
            for line in lines:
                if not line.startswith("#") and "=" in line:
                    tab = line.split("=")
                    if len(tab) > 2:
                        continue
                    var, value = tab
                    if var == "NEO4J_URI":
                        data["protocol"], data["url"] = value.split("://")
                    elif var == "NEO4J_USERNAME":
                        data["user"] = value
                    elif var == "NEO4J_PASSWORD":
                        data["password"] = value
                    elif var == "AURA_INSTANCENAME":
                        data["database"] = value
        return Connect(**data)

    def __repr__(self):
        msg = []
        msg.append("Url: %s" % (self.url,))
        msg.append("Protocol: %s" % (self.protocol,))
        msg.append("Database: %s" % (self.database,))
        user = "<empty>"
        if self.user:
            user = self.user
        msg.append("User: %s" % (user,))
        port = "<empty>"
        if self.port:
            port = self.port
        msg.append("Port: %s" % (port,))
        password = "<empty>"
        if self.password:
            password = "initialized"
        msg.append("Password: " + password)
        msg.append("Uri: " + self.uri)
        is_connected = "false"
        if self.is_connected():
            is_connected = "true"
        msg.append("Connected: " + is_connected)
        return "\n".join(msg)
