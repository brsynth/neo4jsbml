import os

import pytest
from neo4jsbml import sbml

cur_dir = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(cur_dir, "dataset")


@pytest.fixture(scope="session")
def data_directory():
    return data_dir


@pytest.fixture(scope="session")
def iml_path(data_directory):
    return os.path.join(data_directory, "iML1515.xml.gz")


@pytest.fixture(scope="function")
def sbml_iml(iml_path):
    return sbml.Sbml.from_sbml(path=iml_path)


@pytest.fixture(scope="session")
def iml_toy_path(data_directory):
    return os.path.join(data_directory, "iML1515.toy.xml.gz")


@pytest.fixture(scope="function")
def sbml_toy(iml_toy_path):
    return sbml.Sbml.from_sbml(path=iml_toy_path)


@pytest.fixture(scope="session")
def pathway_one_path(data_directory):
    return os.path.join(data_directory, "PathwayModelisation-0.4.1.json")


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
        fromId="n12",
        toId="n13",
        type="IN_COMPARTMENT",
        properties=dict(),
        style=dict(),
    )
