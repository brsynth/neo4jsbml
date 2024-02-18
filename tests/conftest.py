import json
import os
import sys
import xml.etree.ElementTree as ElementTree

import pytest
from neo4jsbml import cmd, connect, sbml, singleton

cur_dir = os.path.abspath(os.path.dirname(__file__))
dir_data = os.path.join(cur_dir, "dataset")


@pytest.fixture(scope="session")
def data_dir():
    return dir_data


@pytest.fixture(scope="session")
def config_path(data_dir):
    return os.path.join(data_dir, "database", "localhost.ini")


@pytest.fixture(scope="session")
def auradb_path(data_dir):
    return os.path.join(data_dir, "database", "auradb.txt")


@pytest.fixture(scope="session")
def iml_path(data_dir):
    return os.path.join(data_dir, "model", "iML1515.xml.gz")


@pytest.fixture(scope="function")
def sbml_iml(iml_path):
    return sbml.SbmlToNeo4j.from_sbml(path=iml_path)


@pytest.fixture(scope="session")
def iaf1260_path(data_dir):
    return os.path.join(data_dir, "model", "iAF1260.xml.gz")


@pytest.fixture(scope="session")
def ecore_path(data_dir):
    return os.path.join(data_dir, "model", "e_coli_core.xml.gz")


@pytest.fixture(scope="session")
def iml_toy_path(data_dir):
    return os.path.join(data_dir, "model", "iML1515.toy.xml.gz")


@pytest.fixture(scope="function")
def sbml_toy(iml_toy_path):
    return sbml.SbmlToNeo4j.from_sbml(path=iml_toy_path)


@pytest.fixture(scope="session")
def pathway_one_path(data_dir):
    return os.path.join(data_dir, "arrows", "PathwayModelisation-1.0.0.json")


@pytest.fixture(scope="session")
def pathway_two_path(data_dir):
    return os.path.join(data_dir, "arrows", "PathwayModelisation-2.0.2.json")


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
    singleton.Singleton.clean()
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


def neo4jsbml_clean(config: str) -> None:
    args = ["neo4jsbml", "clean"]
    args += ["--input-config-ini", config]
    ret = cmd.run(args)
    if ret.returncode > 0:
        print(ret.stderr)
        print(ret.stdout)
        sys.exit(1)


def neo4jsbml_sbml_to_neo4j(config: str, arrows: str, model: str) -> None:
    neo4jsbml_clean(config=config)
    args = ["neo4jsbml", "sbml-to-neo4j"]
    args += ["--input-config-ini", config]
    args += ["--input-arrows-json", arrows]
    args += ["--input-model-sbml", model]
    ret = cmd.run(args)
    if ret.returncode > 0:
        print(ret.stderr)
        print(ret.stdout)
        sys.exit(1)


def neo4jsbml_sbml_from_neo4j(config: str, arrows: str, model: str) -> None:
    args = ["neo4jsbml", "sbml-from-neo4j"]
    args += ["--input-config-ini", config]
    args += ["--input-arrows-json", arrows]
    args += ["--output-model-sbml", model]
    ret = cmd.run(args)
    if ret.returncode > 0:
        print(ret.stderr)
        print(ret.stdout)
        sys.exit(1)


def neo4jsbml_statistics(config: str, output: str) -> None:
    args = ["neo4jsbml", "statistics"]
    args += ["--input-config-ini", config]
    args += ["--output-statistics-json", output]
    ret = cmd.run(args)
    if ret.returncode > 0:
        print(ret.stderr)
        print(ret.stdout)
        sys.exit(1)


def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj


def compare_json(result: str, expect: str) -> bool:
    data_result = {}
    with open(result) as fd:
        data_result = json.load(fd)
    data_expect = {}
    with open(expect) as fd:
        data_expect = json.load(fd)
    return ordered(data_expect) == ordered(data_result)


def _canonicalize_XML(xml: str):
    # From https://stackoverflow.com/questions/24492895/comparing-two-xml-files-in-python
    root = ElementTree.fromstring(xml)
    rootstr = ElementTree.tostring(root)
    return ElementTree.canonicalize(rootstr, strip_text=True)


def compare_xml(result: str, expect: str) -> bool:
    xml_result = ElementTree.parse(result)
    data_result = _canonicalize_XML(ElementTree.tostring(xml_result.getroot()))
    print(data_result)
    xml_expect = ElementTree.parse(expect)
    data_expect = _canonicalize_XML(ElementTree.tostring(xml_expect.getroot()))
    print(data_expect)
    return data_result == data_expect
