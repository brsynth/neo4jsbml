import configparser
import logging
from typing import Any, Dict, List, Optional

import neo4j

from neo4jsbml import _version, singleton


class Connect(metaclass=singleton.Singleton):
    """Connect"""

    BATCH = 5000
    PROTOCOLS = ["neo4j", "bolt"]

    def __init__(
        self,
        protocol: str,
        url: str,
        port: int,
        user: str,
        database: str,
        password: Optional[str],
        password_path: Optional[str] = None,
        batch: Optional[int] = None,
    ) -> None:
        self.protocol = protocol
        self.url = url
        self.port = port

        self.user = user
        self.database = database

        self.password = password
        if password_path is not None:
            self.password = Connect.read_password(path=password_path)

        self.driver = neo4j.GraphDatabase.driver(
            self.uri, auth=(self.user, self.password)
        )
        self.batch = Connect.BATCH
        if batch:
            self.batch = batch

    @property
    def uri(self) -> str:
        return self.protocol + "://" + self.url + ":" + str(self.port)

    @classmethod
    def read_password(cls, path: str) -> str:
        with open(path) as fid:
            return fid.read().splitlines()[0]

    def create_nodes(self, nodes: List[Dict[str, Any]]) -> None:
        # Order by label
        labels = set()
        for node in nodes:
            labels.add(node.pop("labels"))

        for label in labels:
            sub_nodes = [x for x in nodes if x["labels"] == label]
            for i in range(0, len(sub_nodes), self.batch):
                with self.driver.session(
                    default_access_mode=neo4j.WRITE_ACCESS
                ) as session:
                    res = session.run(
                        "WITH $attributes as attributes UNWIND attributes as attribute CALL apoc.merge.node([$label], attribute) YIELD node RETURN count(*)",
                        label=label,
                        attributes=sub_nodes[i : i + self.batch],
                    )
                    res.single()

    def create_relationships(self, relations: List[Any]) -> None:
        # List: Dict: EntiteGauche, IdEntiteGauche, Relation, EntiteDroite, IdEntiteDroite, Attributs
        for i in range(0, len(relations), self.batch):
            with self.driver.session(default_access_mode=neo4j.WRITE_ACCESS) as session:
                res = session.run(
                    "WITH $relations as relations UNWIND relations as rel MATCH (a:rel.left {id: rel.left_id}) MATCH (b:rel.label {id: rel.right}) CALL apoc.create.relationship(a, rel.right_id, rel.properties, b) YIELD rel RETURN rel",
                    relations=[x.to_list() for x in relations[i : i + self.batch]],
                )
                res.single()

    @staticmethod
    def enable_log(level, output_stream):
        handler = logging.StreamHandler(output_stream)
        handler.setLevel(level)
        logging.getLogger(_version.__app_name__).addHandler(handler)
        logging.getLogger(_version.__app_name__).setLevel(level)

    def __del__(self):
        self.driver.close()

    @classmethod
    def from_config(cls, path: str) -> "Connect":
        config = configparser.ConfigParser()
        config.read(path)

        return Connect(
            protocol=config["connection"]["protocol"],
            url=config["connection"]["url"],
            port=int(config["connection"]["port"]),
            user=config["database"]["user"],
            database=config["database"]["name"],
            password=config["database"]["password"],
            batch=int(config["parameters"]["batch"]),
        )
