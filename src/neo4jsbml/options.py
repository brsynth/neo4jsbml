import argparse
import logging
import os
import sys
from typing import Union

from neo4jsbml import connect


def add_dbb_connection(parser: argparse._ActionsContainer) -> None:
    pind = parser.add_argument_group("Database connection - Individual parameter")
    pind.add_argument(
        "--input-protocol-str",
        default=connect.Connect.PROTOCOLS[0],
        choices=connect.Connect.PROTOCOLS,
        help="Protocol used to connect the database",
    )
    pind.add_argument(
        "--input-url-str",
        default="localhost",
        help="URL to connect to the database Neo4j",
    )
    pind.add_argument(
        "--input-port-int",
        help="Port number to connect to the database Neo4j",
    )
    pind.add_argument(
        "--input-user-str",
        default="neo4j",
        help="The login to the database",
    )
    pind.add_argument(
        "--input-password-txt",
        help="A password in a file",
    )
    pind.add_argument(
        "--input-database-str",
        default="neo4j",
        help="The name of the database",
    )

    pconf = parser.add_argument_group("Database connection - Configuration file")
    pconf.add_argument(
        "--input-config-ini",
        help='A configuration file, format "ini"',
    )
    pconf.add_argument(
        "--input-auradb-txt",
        help='A configuration file provided by AuraDB, format "txt"',
    )


def add_input_model(parser: argparse._ActionsContainer) -> None:
    parser.add_argument(
        "--input-model-sbml",
        required=True,
        help="SBML file model",
    )


def add_input_modelisation(parser: argparse._ActionsContainer) -> None:
    parser.add_argument(
        "--input-arrows-json",
        required=True,
        help="Modelisation created and downloaded from arrow",
    )
