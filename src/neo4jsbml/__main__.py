import argparse
import logging
import os
import sys

from neo4jsbml import _version, arrows, connect, sbml


def main():
    desc = "Import SBML file into Neo4"
    parser = argparse.ArgumentParser(description=desc, prog="python -m neo4jsbml")

    # Database connection
    parser_dbb = parser.add_argument_group("Database connection - Individual parameter")
    parser_dbb.add_argument(
        "--input-protocol-str",
        default=connect.Connect.PROTOCOLS[0],
        choices=connect.Connect.PROTOCOLS,
        help="Protocol used to connect the database",
    )
    parser_dbb.add_argument(
        "--input-url-str",
        default="localhost",
        help="URL to connect to the database Neo4j",
    )
    parser_dbb.add_argument(
        "--input-port-int",
        default=7687,
        type=int,
        help="Port number to connect to the database Neo4j",
    )
    parser_dbb.add_argument(
        "--input-user-str",
        default="neo4j",
        help="The login to the database",
    )
    parser_dbb.add_argument(
        "--input-password-file",
        help="A password in a file",
    )
    parser_dbb.add_argument(
        "--input-database-str",
        default="neo4j",
        help="The name of the database",
    )
    parser_dbb.add_argument(
        "--input-batch-int",
        default=connect.Connect.BATCH,
        type=int,
        help="The number of items to include in a batch",
    )
    parser_dbb_config = parser.add_argument_group(
        "Database connection - Configuration file"
    )
    parser_dbb_config.add_argument(
        "--input-config-file",
        help='A configuration file, format "ini"',
    )

    # Input
    parser_input = parser.add_argument_group("Input")
    parser_input.add_argument(
        "--input-file-sbml",
        required=True,
        help="",
    )
    parser_input.add_argument(
        "--input-id-str",
        default="chassis",
        help="Id of document",
    )
    parser_input.add_argument(
        "--input-modelisation-json",
        required=True,
        help="Modelisation created and downloaded from arrow",
    )

    # Parameters
    parser_parameters = parser.add_argument_group("Parameters")
    parser_parameters.add_argument(
        "--log-level",
        choices=[
            "debug",
            "info",
            "warning",
            "error",
            "critical",
            "silent",
            "quiet",
        ],
        default="info",
        help="Adds a console logger for the specified level (default: info)",
    )
    # Compute
    args = parser.parse_args()

    # Logging.
    logger = logging.getLogger(name=_version.__app_name__)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%d-%m-%Y %H:%M"
    )
    st_handler = logging.StreamHandler()
    st_handler.setFormatter(formatter)
    logger.addHandler(st_handler)
    logger.setLevel(args.log_level)

    # Check arguments.
    logger.info("Start - %s" % (_version.__app_name__,))
    if not os.path.isfile(args.input_file_sbml):
        logger.error("Model SBML file does not exist: %s" % (args.input_file_sbml,))
    if not os.path.isfile(args.input_modelisation_json):
        logger.error(
            "Modelisation JSON file does not exist: %s"
            % (args.input_modelisation_json,)
        )

    # Connection to database
    logger.info("Connection to database")
    con = connect.Connect()
    if args.input_config_file:
        logger.warning("Configuration file is provided, ignore indiviual arguments")
        con = connect.Connect.from_config(path=args.input_config_file)
    else:
        con = connect.Connect(
            protocol=args.input_protocol_str,
            url=args.input_url_str,
            port=args.input_port_int,
            user=args.input_user_str,
            database=args.input_database_str,
            password_path=args.input_password_file,
            batch=args.input_batch_int,
        )

    # Load model
    logger.info("Load SBML file")
    sbm = sbml.Sbml.from_sbml(path=args.input_file_sbml, id=args.input_id_str)

    # Load modelisation
    logger.info("Load modelisation file")
    arr = arrows.Arrows.from_json(path=args.input_modelisation_json)

    # Create entities
    logger.info("Create nodes")
    con.create_nodes(nodes=sbm.Sbml.format_nodes(nodes=arr.nodes))

    # Create relationships
    logger.info("Create relationships")
    con.create_relationships(
        relationships=sbm.Sbml.format_relationships(relationships=arr.relationships)
    )

    logger.info("End - %s" % (_version.__app_name__,))

    return 0


if __name__ == "__main__":
    sys.exit(main())
