import os

import pytest
from neo4j import GraphDatabase

from neo4jsbml import connect, snode
from conftest import is_connected, is_not_connected


@pytest.fixture(scope="module")
def neo4j_password(data_directory):
    return os.path.join(data_directory, "database", "password.txt")


@pytest.fixture(scope="module")
def neo4j_config(data_directory):
    return os.path.join(data_directory, "database", "config.ini")


class TestConnect:
    def test_uri(self, init_driver):
        assert init_driver.uri == "neo4j://localhost:7687"

    @is_connected
    def test_is_connected(self, init_driver):
        assert init_driver.is_connected() is True

    @is_not_connected
    def test_is_connected(self, init_driver):
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
        con_b = connect.Connect.from_config(path=neo4j_config)
        assert con_b.protocol == "neo4j"
        assert con_b.url == "localhost"
        assert con_b.port == 7687
        assert con_b.user == "neo4j"
        assert con_b.database == "neo4j"
        assert con_b.password == ""
