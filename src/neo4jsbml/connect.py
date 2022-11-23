import logging
from typing import Any, Dict, List

import neo4j
from neo4jsbml import singleton

class Connect(metaclass=singleton.Singleton):
    """Connect"""

    def __init__(self, user: str, password: str, protocol: str, database: str, url: str) -> None:
        self._password = password
        self.protocol = protocol
        self.database = database
        self.url = url
        self.user = user

        self.driver = neo4j.GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        self.batch = 5000

    @property
    def uri(self) -> str:
        return self.protocol + "://" + self.url

    @property
    def password(self) -> str:
        with open(self._password) as fid:
            return fid.read().splitlines()[0]

    def create_nodes(self, entity: str, nodes: List[Dict[str, Any]]) -> None:
        for i in range(0, len(nodes), self.batch):
            with self.driver.session(default_access_mode=neo4j.WRITE_ACCESS) as session:
                session.run("WITH $nodes as entities UNWIND entities as entity CREATE (n:$entity) SET n += entity", entity=entity, nodes=nodes[i : i + self.batch],)

    def create_relationships(self, relations: List[Any]) -> None:
        # List: Dict: EntiteGauche, IdEntiteGauche, Relation, EntiteDroite, IdEntiteDroite, Attributs
        for i in range(0, len(relations), self.batch):
            with self.driver.session(default_access_mode=neo4j.WRITE_ACCESS) as session:
                session.run("WITH $relations as relations UNWIND relations as rel MATCH (a:rel[0] {id: rel[1]}) MATCH (b:rel[2] {id: rel[3]}) CALL apoc.create.relationship(a, rel[4], rel[5], b)", relations=[x.to_list() for x in relations],)

    @staticmethod
    def enable_log(level, output_stream):
        handler = logging.StreamHandler(output_stream)
        handler.setLevel(level)
        logging.getLogger("neo4j").addHandler(handler)
        logging.getLogger("neo4j").setLevel(level)

    def __del__(self):
        self.driver.close()
