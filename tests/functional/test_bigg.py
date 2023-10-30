import os
import sys

import pytest
from neo4j import GraphDatabase

from neo4jsbml import cmd, singleton
from neo4jsbml._version import __app_name__
from conftest import is_connected, neo4jsbml_sbml_to_neo4j


@is_connected
class TestiML1515:
    def test_nodes(self, init_driver, config_path, pathway_two_path, iml_path):
        neo4jsbml_sbml_to_neo4j(
            config=config_path, arrows=pathway_two_path, model=iml_path
        )
        query = "CALL db.labels() YIELD label CALL apoc.cypher.run('MATCH (:`'+label+'`) RETURN count(*) as count',{}) YIELD value RETURN label, value.count"
        data = init_driver.query(value=query, expect_data=True)

        assert data == [
            {"label": "Compartment", "value.count": 3},
            {"label": "Species", "value.count": 1877},
            {"label": "Parameter", "value.count": 5},
            {"label": "Reaction", "value.count": 2712},
            {"label": "model", "value.count": 1},
            {"label": "UnitDefinition", "value.count": 1},
            {"label": "GeneProduct", "value.count": 1516},
        ]

    def test_relationships(self, init_driver, config_path, pathway_two_path, iml_path):
        neo4jsbml_sbml_to_neo4j(
            config=config_path, arrows=pathway_two_path, model=iml_path
        )
        query = "CALL db.relationshipTypes() YIELD relationshipType as type CALL apoc.cypher.run('MATCH ()-[:`'+type+'`]->() RETURN count(*) as count',{}) YIELD value RETURN type, value.count"
        data = init_driver.query(value=query, expect_data=True)

        assert data == [
            {"type": "IN_COMPARTMENT", "value.count": 1877},
            {"type": "HAS_PRODUCT", "value.count": 5328},
            {"type": "HAS_LOWERFLUXBOUND", "value.count": 2712},
            {"type": "HAS_PARAMETER", "value.count": 5},
            {"type": "HAS_UNIT", "value.count": 5},
            {"type": "HAS_UPPERFLUXBOUND", "value.count": 2712},
            {"type": "IS_IMPLIED", "value.count": 4624},
            {"type": "IS_REACTANT", "value.count": 5247},
        ]


@is_connected
class TestiAF1260:
    def test_nodes(self, init_driver, config_path, pathway_two_path, iaf1260_path):
        neo4jsbml_sbml_to_neo4j(
            config=config_path, arrows=pathway_two_path, model=iaf1260_path
        )
        query = "CALL db.labels() YIELD label CALL apoc.cypher.run('MATCH (:`'+label+'`) RETURN count(*) as count',{}) YIELD value RETURN label, value.count"
        data = init_driver.query(value=query, expect_data=True)

        assert data == [
            {"label": "Compartment", "value.count": 3},
            {"label": "Species", "value.count": 1668},
            {"label": "Parameter", "value.count": 8},
            {"label": "Reaction", "value.count": 2382},
            {"label": "model", "value.count": 1},
            {"label": "UnitDefinition", "value.count": 1},
            {"label": "GeneProduct", "value.count": 1261},
        ]

    def test_relationships(
        self, init_driver, config_path, pathway_two_path, iaf1260_path
    ):
        neo4jsbml_sbml_to_neo4j(
            config=config_path, arrows=pathway_two_path, model=iaf1260_path
        )
        query = "CALL db.relationshipTypes() YIELD relationshipType as type CALL apoc.cypher.run('MATCH ()-[:`'+type+'`]->() RETURN count(*) as count',{}) YIELD value RETURN type, value.count"
        data = init_driver.query(value=query, expect_data=True)

        assert data == [
            {"type": "IN_COMPARTMENT", "value.count": 1668},
            {"type": "HAS_PRODUCT", "value.count": 4714},
            {"type": "HAS_LOWERFLUXBOUND", "value.count": 2382},
            {"type": "HAS_PARAMETER", "value.count": 8},
            {"type": "HAS_UNIT", "value.count": 8},
            {"type": "HAS_UPPERFLUXBOUND", "value.count": 2382},
            {"type": "IS_IMPLIED", "value.count": 3747},
            {"type": "IS_REACTANT", "value.count": 4517},
        ]
