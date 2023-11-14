import argparse
import json
import logging
import os
import sys

from neo4jsbml import _version, arrows, connect, options, sbml

AP = argparse.ArgumentParser(description="")
AP_subparsers = AP.add_subparsers(help="Sub-commnands (use with -h for more info)")


def _cmd_sbml_to_neo4j(args):
    """Import SBML file into Neo4j"""
    # Check arguments.
    logging.info("Start - sbml-to-neo4j")
    if not os.path.isfile(args.input_model_sbml):
        logging.error("Model SBML file does not exist: %s" % (args.input_model_sbml,))
        AP.exit(1)
    if not os.path.isfile(args.input_arrows_json):
        logging.error(
            "Modelisation JSON file does not exist: %s" % (args.input_arrows_json,)
        )
        AP.exit(1)

    is_dry_run = False
    if args.parameter_dry_run:
        logging.info("Dry run mode, no data will be loaded into the database")
        is_dry_run = True

    # Connection to database
    logging.info("Connection to database")
    con = None
    if args.input_config_ini:
        if not os.path.isfile(args.input_config_ini):
            logging.error("File provided does not exist: %s" % (args.input_config_ini,))
            AP.exit(1)
        logging.warning("Configuration file is provided, ignore indiviual arguments")
        con = connect.Connect.from_config(path=args.input_config_ini)
    elif args.input_auradb_file:
        if not os.path.isfile(args.input_auradb_txt):
            logging.error("File provided does not exist: %s" % (args.input_auradb_txt,))
            AP.exit(1)
        logging.warning(
            "Configuration file AuraDB is provided, ignore indiviual arguments"
        )
        con = connect.Connect.from_auradb(path=args.input_auradb_txt)
    else:
        con = connect.Connect(
            protocol=args.input_protocol_str,
            url=args.input_url_str,
            port=args.input_port_int,
            user=args.input_user_str,
            database=args.input_database_str,
            password_path=args.input_password_txt,
        )
    if con.is_connected() is False and is_dry_run is False:
        logging.error("Unable to connect to the database")
        AP.exit(1)

    # Load model
    logging.info("Load SBML file")
    sbm = sbml.SbmlToNeo4j.from_sbml(
        path=args.input_model_sbml, tag=args.parameter_tag_property_str
    )

    # Load modelisation
    logging.info("Load modelisation file")
    arr = arrows.Arrows.from_json(path=args.input_arrows_json)

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

    logging.info("End - sbml-to-neo4j")
    return 0


P_stn = AP_subparsers.add_parser("sbml-to-neo4j", help=_cmd_sbml_to_neo4j.__doc__)
options.add_dbb_connection(parser=P_stn)
# Input
P_stn_input = P_stn.add_argument_group("Input")
options.add_input_model(parser=P_stn_input)
options.add_input_modelisation(parser=P_stn_input)
# Parameters
P_stn_params = P_stn.add_argument_group("Parameters")
P_stn_params.add_argument(
    "--parameter-dry-run",
    action="store_true",
    help="Dry run: parse Schema file only",
)
P_stn_input.add_argument(
    "--parameter-tag-property-str",
    help='Add a "tag" property for each entity, to set a custom ID',
)
P_stn.set_defaults(func=_cmd_sbml_to_neo4j)


def _cmd_sbml_from_neo4j(args):
    """Create SBML file from Neo4j"""
    # Check arguments.
    logging.info("Start - sbml-from-neo4j")
    if not os.path.isfile(args.input_arrows_json):
        logging.error(
            "Modelisation JSON file does not exist: %s" % (args.input_arrows_json,)
        )
        AP.exit(1)

    # Connection to database
    logging.info("Connection to database")
    con = None
    if args.input_config_ini:
        if not os.path.isfile(args.input_config_ini):
            logging.error("File provided does not exist: %s" % (args.input_config_ini,))
            AP.exit(1)
        logging.warning("Configuration file is provided, ignore indiviual arguments")
        con = connect.Connect.from_config(path=args.input_config_ini)
    elif args.input_auradb_file:
        if not os.path.isfile(args.input_auradb_txt):
            logging.error("File provided does not exist: %s" % (args.input_auradb_txt,))
            AP.exit(1)
        logging.warning(
            "Configuration file AuraDB is provided, ignore indiviual arguments"
        )
        con = connect.Connect.from_auradb(path=args.input_auradb_txt)
    else:
        con = connect.Connect(
            protocol=args.input_protocol_str,
            url=args.input_url_str,
            port=args.input_port_int,
            user=args.input_user_str,
            database=args.input_database_str,
            password_path=args.input_password_txt,
        )
    if con.is_connected() is False:
        logging.error("Unable to connect to the database")
        AP.exit(1)

    # Init
    logging.info("Initialize data")
    sbml_from_neo4j = sbml.SbmlFromNeo4j.from_specifications(
        level=args.parameter_sbml_level_int, version=args.parameter_sbml_version_int
    )
    sbml_from_neo4j.connection = con

    # Load modelisation
    logging.info("Load modelisation file")
    arr = arrows.Arrows.from_json(path=args.input_arrows_json, add_id=False)

    # Filter modelisation based on libsbml
    logging.info("Filter modelisation based on libsbml")
    sbml_from_neo4j.annotate(modelisation=arr)

    # Extract entities
    logging.info("Extract entities")
    sbml_from_neo4j.conciliate_labels()
    sbml_from_neo4j.extract_entities(current_id=None)

    # Write model
    logging.info("Write model")
    sbml_from_neo4j.to_sbml(path=args.output_model_sbml)

    logging.info("End - sbml-from-neo4j")
    return 0


P_sfn = AP_subparsers.add_parser("sbml-from-neo4j", help=_cmd_sbml_from_neo4j.__doc__)
options.add_dbb_connection(parser=P_sfn)
# Input
P_sfn_input = P_sfn.add_argument_group("Input")
options.add_input_modelisation(parser=P_sfn_input)
# Parameters
P_sfn_params = P_sfn.add_argument_group("Parameters")
P_sfn_params.add_argument(
    "--parameter-sbml-level-int",
    type=int,
    default=3,
    help="Level of the SBML model (default: 3)",
)
P_sfn_params.add_argument(
    "--parameter-sbml-version-int",
    type=int,
    default=2,
    help="Version of the SBML model (default: 2)",
)
# Output
P_sfn_output = P_sfn.add_argument_group("Output")
P_sfn_output.add_argument(
    "--output-model-sbml",
    help="Output the SBML model",
)
P_sfn.set_defaults(func=_cmd_sbml_from_neo4j)


def _cmd_stats(args):
    """Get statistics: entities and relationships"""
    # Check arguments.
    logging.info("Start - statistics")
    # Connection to database
    logging.info("Connection to database")
    con = None
    if args.input_config_ini:
        if not os.path.isfile(args.input_config_ini):
            logging.error("File provided does not exist: %s" % (args.input_config_ini,))
            AP.exit(1)
        logging.warning("Configuration file is provided, ignore indiviual arguments")
        con = connect.Connect.from_config(path=args.input_config_ini)
    elif args.input_auradb_file:
        if not os.path.isfile(args.input_auradb_txt):
            logging.error("File provided does not exist: %s" % (args.input_auradb_txt,))
            AP.exit(1)
        logging.warning(
            "Configuration file AuraDB is provided, ignore indiviual arguments"
        )
        con = connect.Connect.from_auradb(path=args.input_auradb_txt)
    else:
        con = connect.Connect(
            protocol=args.input_protocol_str,
            url=args.input_url_str,
            port=args.input_port_int,
            user=args.input_user_str,
            database=args.input_database_str,
            password_path=args.input_password_txt,
        )
    if con.is_connected() is False:
        logging.error("Unable to connect to the database")
        AP.exit(1)

    # Statistics
    logging.info("Get number of entities")
    data = {}
    query = "CALL db.labels() YIELD label CALL apoc.cypher.run('MATCH (:`'+label+'`) RETURN count(*) as count',{}) YIELD value RETURN label, value.count"
    res = con.query(value=query, expect_data=True)
    data["nodes"] = res

    logging.info("Get number of relationships")
    query = "CALL db.relationshipTypes() YIELD relationshipType as type CALL apoc.cypher.run('MATCH ()-[:`'+type+'`]->() RETURN count(*) as count',{}) YIELD value RETURN type, value.count"
    res = con.query(value=query, expect_data=True)
    data["relationships"] = res

    # Write output
    logging.info("Write output")
    with open(args.output_statistics_json, "w") as fod:
        json.dump(data, fod, indent=4)

    logging.info("End - statistics")
    return 0


P_stats = AP_subparsers.add_parser("statistics", help=_cmd_stats.__doc__)
options.add_dbb_connection(parser=P_stats)
P_out = P_stats.add_argument_group("Output")
P_out.add_argument(
    "--output-statistics-json",
    help="Statistics output as Json file",
)
P_stats.set_defaults(func=_cmd_stats)


def _cmd_clean(args):
    """Remove data into the database"""
    # Check arguments.
    logging.info("Start - clean")
    # Connection to database
    logging.info("Connection to database")
    con = None
    if args.input_config_ini:
        if not os.path.isfile(args.input_config_ini):
            logging.error("File provided does not exist: %s" % (args.input_config_ini,))
            AP.exit(1)
        logging.warning("Configuration file is provided, ignore indiviual arguments")
        con = connect.Connect.from_config(path=args.input_config_ini)
    elif args.input_auradb_file:
        if not os.path.isfile(args.input_auradb_txt):
            logging.error("File provided does not exist: %s" % (args.input_auradb_txt,))
            AP.exit(1)
        logging.warning(
            "Configuration file AuraDB is provided, ignore indiviual arguments"
        )
        con = connect.Connect.from_auradb(path=args.input_auradb_txt)
    else:
        con = connect.Connect(
            protocol=args.input_protocol_str,
            url=args.input_url_str,
            port=args.input_port_int,
            user=args.input_user_str,
            database=args.input_database_str,
            password_path=args.input_password_txt,
        )
    if con.is_connected() is False:
        logging.error("Unable to connect to the database")
        AP.exit(1)

    # Clean
    logging.info("Clean database")
    con.clean()

    logging.info("End - clean")
    return 0


P_clean = AP_subparsers.add_parser("clean", help=_cmd_clean.__doc__)
options.add_dbb_connection(parser=P_clean)
P_clean.set_defaults(func=_cmd_clean)


# Help.
def print_help():
    """Display this program"s help"""
    print(AP_subparsers.help)
    AP.exit()


# Version.
def print_version(_args):
    """Display this program"s version"""
    print(_version.__version__)


P_version = AP_subparsers.add_parser("version", help=print_version.__doc__)
P_version.set_defaults(func=print_version)


# Main.
def parse_args(args=None):
    """Parse the command line"""
    return AP.parse_args(args=args)


def main():
    """Entrypoint to commandline"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%d-%m-%Y %H:%M",
    )
    args = AP.parse_args()
    # No arguments or subcommands were given.
    if len(args.__dict__) < 1:
        print_help()
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
