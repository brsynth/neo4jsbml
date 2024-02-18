import os
import tempfile

from conftest import (
    compare_json,
    is_connected,
    neo4jsbml_clean,
    neo4jsbml_sbml_to_neo4j,
    neo4jsbml_statistics,
)


@is_connected
class TestL3V2Package:
    def setUp(self, config_path):
        neo4jsbml_clean(config=config_path)

    def test_ex_fbc(self, data_dir, config_path):
        neo4jsbml_sbml_to_neo4j(
            config=config_path,
            arrows=os.path.join(data_dir, "arrows", "L3V1.fbc.V2R1.4-1.json"),
            model=os.path.join(data_dir, "model", "L3V1.fbc.V2R1.4-1.xml"),
        )
        with tempfile.NamedTemporaryFile(suffix=".json") as fod:
            neo4jsbml_statistics(config=config_path, output=fod.name)
            assert compare_json(
                result=fod.name,
                expect=os.path.join(data_dir, "statistics", "L3V1.fbc.V2R1.4-1.json"),
            )

    def test_ex_groups(self, data_dir, config_path):
        neo4jsbml_sbml_to_neo4j(
            config=config_path,
            arrows=os.path.join(data_dir, "arrows", "L3V1.groups.V1R1.5-2.json"),
            model=os.path.join(data_dir, "model", "L3V1.groups.V1R1.5-2.xml"),
        )
        with tempfile.NamedTemporaryFile(suffix=".json") as fod:
            neo4jsbml_statistics(config=config_path, output=fod.name)
            assert compare_json(
                result=fod.name,
                expect=os.path.join(
                    data_dir, "statistics", "L3V1.groups.V1R1.5-2.json"
                ),
            )

    def test_ex_layout(self, data_dir, config_path):
        neo4jsbml_sbml_to_neo4j(
            config=config_path,
            arrows=os.path.join(data_dir, "arrows", "L3V1.layout.V1R1.4-5.json"),
            model=os.path.join(data_dir, "model", "L3V1.layout.V1R1.4-5.xml"),
        )
        with tempfile.NamedTemporaryFile(suffix=".json") as fod:
            neo4jsbml_statistics(config=config_path, output=fod.name)
            assert compare_json(
                result=fod.name,
                expect=os.path.join(
                    data_dir, "statistics", "L3V1.layout.V1R1.4-5.json"
                ),
            )

    def test_ex_qual(self, data_dir, config_path):
        neo4jsbml_sbml_to_neo4j(
            config=config_path,
            arrows=os.path.join(data_dir, "arrows", "L3V1.qual.V1R1.4-2.json"),
            model=os.path.join(data_dir, "model", "L3V1.qual.V1R1.4-2.xml"),
        )
        with tempfile.NamedTemporaryFile(suffix=".json") as fod:
            neo4jsbml_statistics(config=config_path, output=fod.name)
            assert compare_json(
                result=fod.name,
                expect=os.path.join(data_dir, "statistics", "L3V1.qual.V1R1.4-2.json"),
            )
