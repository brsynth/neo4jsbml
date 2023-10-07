import os

import pytest
from neo4jsbml import connect, sbml

cur_dir = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(cur_dir, "dataset")


@pytest.fixture(scope="session")
def data_directory():
    return data_dir


@pytest.fixture(scope="session")
def config_path(data_directory):
    return os.path.join(data_directory, "database", "localhost.ini")


@pytest.fixture(scope="session")
def auradb_path(data_directory):
    return os.path.join(data_directory, "database", "auradb.txt")


@pytest.fixture(scope="session")
def iml_path(data_directory):
    return os.path.join(data_directory, "model", "iML1515.xml.gz")


@pytest.fixture(scope="function")
def sbml_iml(iml_path):
    return sbml.Sbml.from_sbml(path=iml_path)


@pytest.fixture(scope="session")
def iaf1260_path(data_directory):
    return os.path.join(data_directory, "model", "iAF1260.xml.gz")


@pytest.fixture(scope="session")
def ecore_path(data_directory):
    return os.path.join(data_directory, "model", "e_coli_core.xml.gz")


@pytest.fixture(scope="session")
def iml_toy_path(data_directory):
    return os.path.join(data_directory, "model", "iML1515.toy.xml.gz")


@pytest.fixture(scope="function")
def sbml_toy(iml_toy_path):
    return sbml.Sbml.from_sbml(path=iml_toy_path)


@pytest.fixture(scope="session")
def pathway_one_path(data_directory):
    return os.path.join(data_directory, "arrows", "PathwayModelisation-1.0.0.json")


@pytest.fixture(scope="session")
def pathway_two_path(data_directory):
    return os.path.join(data_directory, "arrows", "PathwayModelisation-2.0.2.json")


@pytest.fixture(scope="function")
def node_one_dict():
    return dict(
        id="n11",
        labels=["Model"],
        properties=dict(id="str", name="str", metaid="str", sboTerm="str"),
    )


@pytest.fixture(scope="function")
def node_two_dict():
    return dict(
        id="n12",
        position=dict(x=-482.6, y=-158),
        null_one=None,
        null_two="",
        labels=["Compartment"],
        properties=dict(
            id="str", metaid="str", name="str", sboTerm="int", spatialDimensions="int"
        ),
    )


@pytest.fixture(scope="function")
def node_three_dict():
    return dict(
        id="n13",
        labels=["Species"],
        properties=dict(id="str", name="str", metaid="str", sboTerm="str"),
    )


@pytest.fixture(scope="function")
def rel_one_dict():
    return dict(
        id="n21",
        from_label="",
        to_label="",
        from_id="n13",
        to_id="n12",
        label="HAS_COMPARTMENT",
        properties=dict(),
        style=dict(),
    )


@pytest.fixture(scope="function")
def rel_one_arrow():
    return dict(
        id="n21",
        fromId="n13",
        toId="n12",
        type="HAS_COMPARTMENT",
        properties=dict(),
        style=dict(),
    )


@pytest.fixture(scope="function")
def rel_two_dict():
    return dict(
        id="n21",
        from_label="",
        to_label="",
        from_id="n12",
        to_id="n13",
        label="IN_COMPARTMENT",
        properties=dict(),
        style=dict(),
    )


@pytest.fixture(scope="function")
def rel_two_arrow():
    return dict(
        id="n21",
        fromId="n12",
        toId="n13",
        type="IN_COMPARTMENT",
        properties=dict(),
        style=dict(),
    )


@pytest.fixture(scope="function")
def init_driver():
    return connect.Connect(
        protocol="neo4j",
        url="localhost",
        port=7687,
        user="neo4j",
        database="neo4j",
        password="",
    )


is_connected = pytest.mark.skipif(
    not connect.Connect(
        protocol="neo4j",
        url="localhost",
        port=7687,
        user="neo4j",
        database="neo4j",
        password="",
    ).is_connected(),
    reason="not connected",
)
is_not_connected = pytest.mark.skipif(
    connect.Connect(
        protocol="neo4j",
        url="localhost",
        port=7687,
        user="neo4j",
        database="neo4j",
        password="",
    ).is_connected(),
    reason="connected",
)
