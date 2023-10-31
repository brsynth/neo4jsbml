import os

import pytest
from neo4j import GraphDatabase

from neo4jsbml import connect, singleton, snode
from conftest import is_connected, is_not_connected


@pytest.fixture(scope="module")
def neo4j_password(data_dir):
    return os.path.join(data_dir, "database", "password.txt")


@pytest.fixture(scope="module")
def neo4j_config(data_dir):
    return os.path.join(data_dir, "database", "config.ini")


class TestConnect:
    def test_uri(self, init_driver):
        assert init_driver.uri == "neo4j://localhost:7687"

    @is_connected
    def test_is_connected(self, init_driver):
        assert init_driver.is_connected() is True

    @is_not_connected
    def test_is_not_connected(self, init_driver):
        assert init_driver.is_connected() is False

    def test_read_password(self, neo4j_password):
        pwd = connect.Connect.read_password(path=neo4j_password)
        assert pwd == "this_is_not_a_real_password"

    @is_connected
    def test_create_nodes(self, init_driver, node_one_dict):
        nod = snode.SNode.from_dict(data=node_one_dict)
        init_driver.create_nodes(nodes=[nod])

    def test_relationships(self):
        pass

    def test_from_config(self, neo4j_config):
        singleton.Singleton.clean()
        con_b = connect.Connect.from_config(path=neo4j_config)
        assert con_b.protocol == "neo4j"
        assert con_b.url == "localhost"
        assert con_b.port == "7687"
        assert con_b.user == "neo4j"
        assert con_b.database == "neo4j"
        assert con_b.password == "abc"

    def test_from_auradb(self, auradb_path):
        singleton.Singleton.clean()
        con_c = connect.Connect.from_auradb(path=auradb_path)
        assert con_c.protocol == "neo4j+s"
        assert con_c.url == "test.neo4j.io"
        assert con_c.port is None
        assert con_c.user == "neo4j"
        assert con_c.database == "Instance01"
        assert con_c.password == "thepassword"
