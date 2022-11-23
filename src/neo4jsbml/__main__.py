import argparse
import logging
import os
import sys

from neo4jsbml import _version


def main():
    """CLI for neo4jsbml"""

    desc = ""  \
        ""

    parser = argparse.ArgumentParser(
        description=desc,
        prog='python -m neo4jsbml'
    )

    - protocol: bolt, neo4j, ?
- url (default: localhost:3000)
- user (default: neo4j)
- password
- database (default: neo4j)

- fichier sbml
- id model
- entités

    # Input
    parser_input = parser.add_argument_group(
        'Input'
    )
    parser_input.add_argument(
        '--input-protocol-str',
        default="neo4j",
        choices=["neo4j", "bolt"],
        help="Protocol",
    )
    parser_input.add_argument(
        "--input-url-str",
        default="localhost:3000",
        help="",
    )
    parser_input.add_argument(
        "--input-user-str",
        default="neo4j",
        help="",
    )
    parser_input.add_argument(
        "--input-password-file",
        required=True,
        help="",
    )
    parser_input.add_argument(
        "--input-database-str",
        default="neo4j",
        help="",
    )
    parser_input.add_argument(
        "--input-file-sbml",
        required=True,
        help="",
    )
    parser_input.add_argument(
        "--input-id-sbml",
        help="",
    )
    parser_input.add_argument(
        "--input-modelisation-str",
        default="sbml",
        choices=["sbml", "pathway"],
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
    logger.setLevel(args.log_level)

    # TODO: Check arguments.

    # Connection to database
    logger.info('Connection to database')
    con = Connect(
        user=
        password=
        protocol=
        datasbase=
        url=
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
