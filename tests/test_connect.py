import os

import pytest
from neo4j import GraphDatabase
from neo4jsbml import connect


@pytest.fixture(scope="module")
def neo4j_password(data_directory):
    return os.path.join(data_directory, "password.txt")


@pytest.fixture(scope="module")
def neo4j_config(data_directory):
    return os.path.join(data_directory, "config.ini")


@pytest.fixture(scope="function")
def init_driver(neo4j_password):
    return connect.Connect(
        protocol="bolt",
        url="localhost",
        port=7687,
        user="neo4j",
        database="neo4j",
        password="test",
    )


class TestConnect:
    def test_uri(self, init_driver):
        assert init_driver.uri == "bolt://localhost:7687"

    def test_is_connected(self):
        con = connect.Connect(
            protocol="b",
            url="loc",
            port=0,
            user="neo4j",
            database="neo4j",
            password="test",
        )
        assert con.is_connected() == False

    def test_read_password(self, neo4j_password):
        pwd = connect.Connect.read_password(path=neo4j_password)
        assert pwd == "this_is_not_a_real_password"

    def test_create_nodes(self):
        pass

    def test_relationships(self):
        pass

    def test_from_config(self, neo4j_config):
        con_b = connect.Connect.from_config(path=neo4j_config)
        assert con_b.protocol == "bolt"
        assert con_b.url == "localhost"
        assert con_b.port == 7687
        assert con_b.user == "neo4j"
        assert con_b.database == "neo4j"
        assert con_b.password == "test"
        assert con_b.batch == 5000
