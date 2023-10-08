import argparse
import logging
import os
import sys

from neo4jsbml import _version, arrows, connect, sbml


def main():
    """Entrypoint for neo4jsbml"""
    desc = "Import SBML file into Neo4"
    parser = argparse.ArgumentParser(description=desc, prog=_version.__app_name__)

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
    parser_dbb_config = parser.add_argument_group(
        "Database connection - Configuration file"
    )
    parser_dbb_config.add_argument(
        "--input-config-file",
        help='A configuration file, format "ini"',
    )
    parser_dbb_config.add_argument(
        "--input-auradb-file",
        help='A configuration file provided by AuraDB, format "txt"',
    )

    # Input
    parser_input = parser.add_argument_group("Input")
    parser_input.add_argument(
        "--input-file-sbml",
        required=True,
        help="SBML file model",
    )
    parser_input.add_argument(
        "--input-tag-str",
        help="Tag of document",
    )
    parser_input.add_argument(
        "--input-modelisation-json",
        required=True,
        help="Modelisation created and downloaded from arrow",
    )

    # Parameters
    parser_params = parser.add_argument_group("Parameters")
    parser_params.add_argument(
        "--parameters-dry-run",
        action="store_true",
        help="Dry run: parse Schema file only",
    )

    # Compute
    args = parser.parse_args()

    # Logging.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%d-%m-%Y %H:%M",
    )

    # Check arguments.
    logging.info("Start - %s" % (_version.__app_name__,))
    if not os.path.isfile(args.input_file_sbml):
        logging.error("Model SBML file does not exist: %s" % (args.input_file_sbml,))
        parser.exit(1)
    if not os.path.isfile(args.input_modelisation_json):
        logging.error(
            "Modelisation JSON file does not exist: %s"
            % (args.input_modelisation_json,)
        )
        parser.exit(1)

    is_dry_run = False
    if args.parameters_dry_run:
        logging.info("Dry run mode, no data will be loaded into the database")
        is_dry_run = True

    # Connection to database
    logging.info("Connection to database")
    con = None
    if args.input_config_file:
        if not os.path.isfile(args.input_config_file):
            logging.error(
                "File provided does not exist: %s" % (args.input_config_file,)
            )
            parser.exit(1)
        logging.warning("Configuration file is provided, ignore indiviual arguments")
        con = connect.Connect.from_config(path=args.input_config_file)
    elif args.input_auradb_file:
        if not os.path.isfile(args.input_auradb_file):
            logging.error(
                "File provided does not exist: %s" % (args.input_auradb_file,)
            )
            parser.exit(1)
        logging.warning(
            "Configuration file AuraDB is provided, ignore indiviual arguments"
        )
        con = connect.Connect.from_auradb(path=args.input_auradb_file)
    else:
        con = connect.Connect(
            protocol=args.input_protocol_str,
            url=args.input_url_str,
            port=args.input_port_int,
            user=args.input_user_str,
            database=args.input_database_str,
            password_path=args.input_password_file,
        )
    if con.is_connected() is False and is_dry_run is False:
        logging.error("Unable to connect to the database")
        parser.exit(1)

    # Load model
    logging.info("Load SBML file")
    sbm = sbml.Sbml.from_sbml(path=args.input_file_sbml, tag=args.input_tag_str)

    # Load modelisation
    logging.info("Load modelisation file")
    arr = arrows.Arrows.from_json(path=args.input_modelisation_json)

    # Mapping
    logging.info("Map schema to data - nodes")
    nod = sbm.format_nodes(nodes=arr.nodes)

    logging.info("Map schema to data - relationships")
    rel = sbm.format_relationships(relationships=arr.relationships)

    # Import into neo4j
    if is_dry_run is False:
        logging.info("Import into neo4j - nodes")
        con.create_nodes(nodes=nod)

        if arr.relationships is not None and len(arr.relationships) > 0:
            logging.info("Import into neo4j - relationships")
            con.create_relationships(relationships=rel)
        else:
            logging.info("None relationship created")

    logging.info("End - %s" % (_version.__app_name__,))

    return 0


if __name__ == "__main__":
    sys.exit(main())
