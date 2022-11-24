import argparse
import logging
import os
import sys

from neo4jsbml import _version, connect
from neo4jsbml.sbml import Sbml


def main():
    """CLI for neo4jsbml"""

    desc = ""  \
        ""

    parser = argparse.ArgumentParser(
        description=desc,
        prog='python -m neo4jsbml'
    )

    # Database connection
    parser_dbb = parser.add_argument_group(
        'Database connection'
    )
    parser_dbb.add_argument(
        '--input-protocol-str',
        default="neo4j",
        choices=["neo4j", "bolt"],
        help="Protocol used to connect the database",
    )
    parser_dbb.add_argument(
        "--input-url-str",
        default="localhost:7687",
        help="URL to connect to the database Neo4j with the port associated",
    )
    parser_dbb.add_argument(
        "--input-user-str",
        default="neo4j",
        help="The login to the database",
    )
    parser_dbb.add_argument(
        "--input-password-file",
        required=True,
        help="A password in a file",
    )
    parser_dbb.add_argument(
        "--input-database-str",
        default="neo4j",
        help="The name of the database",
    )
    # Input
    parser_input = parser.add_argument_group(
        'Input'
    )
    parser_input.add_argument(
        "--input-file-sbml",
        required=True,
        help="",
    )
    parser_input.add_argument(
        "--input-id-str",
        help="Id of document",
    )
    parser_input.add_argument(
        "--input-modelisation-str",
        default="sbml-3.1-1",
        choices=["sbml-3.1-1", "pathway"],
        help="",
    )

    # Compute
    args = parser.parse_args()

    # Logging.
    logger = logging.getLogger(name='main')
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%d-%m-%Y %H:%M'
    )
    st_handler = logging.StreamHandler()
    st_handler.setFormatter(formatter)
    logger.addHandler(st_handler)
    # logger.setLevel(args.log_level)

    # Check arguments.
    if not os.path.isfile(args.input_file_sbml):
        logging.error("SBML file does not exist: %s" % (args.input_file_sbml,))

    # Connection to database
    logger.info('Connection to database')
    con = connect.Connect(
        user=args.input_user_str,
        password=args.input_password_file,
        protocol=args.input_protocol_str,
        database=args.input_database_str,
        url=args.input_url_str,
    )

    sbml = Sbml(
        id=args.input_id_str,
        path=args.input_file_sbml,
        modelisation=args.input_modelisation_str,
    )

    # Create entity
    logging.info("Create node: Document")
    con.create_nodes(entity="Document", nodes=sbml.get_document())
    logging.info("Create node: Model")
    con.create_nodes(entity="Model", nodes=sbml.get_model())

    logging.info("Create node: Species")
    con.create_nodes(entity="Species", nodes=sbml.get_species())
    logging.info("Create node: Compartment")
    con.create_nodes(entity="Compartment", nodes=sbml.get_compartments())
    logging.info("Create node: Reaction")
    con.create_nodes(entity="Reaction", nodes=sbml.get_reactions())
    logging.info("Create node: Parameter")
    con.create_nodes(entity="Parameter", nodes=sbml.get_parameters())

    # Create relationships
    logging.info("Create relationship: Document-Model")
    con.create_relationships(sbml.get_relationships_document_model())
    logging.info("Create relationship: Model-Reactions")
    con.create_relationships(sbml.get_relationships_model_reactions())
    logging.info("Create relationship: Model-Compartments")
    con.create_relationships(sbml.get_relationships_model_compartments())
    logging.info("Create relationship: Model-Parameters")
    con.create_relationships(sbml.get_relationships_model_parameters())
    logging.info("Create relationship: Species-Compartment")
    con.create_relationships(sbml.get_relationships_species_compartments())

    return 0


if __name__ == '__main__':
    sys.exit(main())
