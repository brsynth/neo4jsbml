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
class TestL2V5Core:
    def setUp(self, config_path):
        neo4jsbml_clean(config=config_path)

    def test_ex_1(self, data_dir, config_path):
        neo4jsbml_sbml_to_neo4j(
            config=config_path,
            arrows=os.path.join(data_dir, "arrows", "L2V5.7-1.json"),
            model=os.path.join(data_dir, "model", "L2V5.7-1.xml"),
        )
        with tempfile.NamedTemporaryFile(suffix=".json") as fod:
            neo4jsbml_statistics(config=config_path, output=fod.name)
            assert compare_json(
                result=fod.name,
                expect=os.path.join(data_dir, "statistics", "L2V5.7-1.json"),
            )

    def test_ex_2(self, data_dir, config_path):
        neo4jsbml_sbml_to_neo4j(
            config=config_path,
            arrows=os.path.join(data_dir, "arrows", "L2V5.7-2.json"),
            model=os.path.join(data_dir, "model", "L2V5.7-2.xml"),
        )
        with tempfile.NamedTemporaryFile(suffix=".json") as fod:
            neo4jsbml_statistics(config=config_path, output=fod.name)
            assert compare_json(
                result=fod.name,
                expect=os.path.join(data_dir, "statistics", "L2V5.7-2.json"),
            )

    def test_ex_3(self, data_dir, config_path):
        neo4jsbml_sbml_to_neo4j(
            config=config_path,
            arrows=os.path.join(data_dir, "arrows", "L2V5.7-3.json"),
            model=os.path.join(data_dir, "model", "L2V5.7-3.xml"),
        )
        with tempfile.NamedTemporaryFile(suffix=".json") as fod:
            neo4jsbml_statistics(config=config_path, output=fod.name)
            assert compare_json(
                result=fod.name,
                expect=os.path.join(data_dir, "statistics", "L2V5.7-3.json"),
            )

    def test_ex_4(self, data_dir, config_path):
        neo4jsbml_sbml_to_neo4j(
            config=config_path,
            arrows=os.path.join(data_dir, "arrows", "L2V5.7-4.json"),
            model=os.path.join(data_dir, "model", "L2V5.7-4.xml"),
        )
        with tempfile.NamedTemporaryFile(suffix=".json") as fod:
            neo4jsbml_statistics(config=config_path, output=fod.name)
            assert compare_json(
                result=fod.name,
                expect=os.path.join(data_dir, "statistics", "L2V5.7-4.json"),
            )

    def test_ex_5(self, data_dir, config_path):
        neo4jsbml_sbml_to_neo4j(
            config=config_path,
            arrows=os.path.join(data_dir, "arrows", "L2V5.7-5.json"),
            model=os.path.join(data_dir, "model", "L2V5.7-5.xml"),
        )
        with tempfile.NamedTemporaryFile(suffix=".json") as fod:
            neo4jsbml_statistics(config=config_path, output=fod.name)
            assert compare_json(
                result=fod.name,
                expect=os.path.join(data_dir, "statistics", "L2V5.7-5.json"),
            )

    def test_ex_6(self, data_dir, config_path):
        neo4jsbml_sbml_to_neo4j(
            config=config_path,
            arrows=os.path.join(data_dir, "arrows", "L2V5.7-6.json"),
            model=os.path.join(data_dir, "model", "L2V5.7-6.xml"),
        )
        with tempfile.NamedTemporaryFile(suffix=".json") as fod:
            neo4jsbml_statistics(config=config_path, output=fod.name)
            assert compare_json(
                result=fod.name,
                expect=os.path.join(data_dir, "statistics", "L2V5.7-6.json"),
            )

    def test_ex_7(self, data_dir, config_path):
        neo4jsbml_sbml_to_neo4j(
            config=config_path,
            arrows=os.path.join(data_dir, "arrows", "L2V5.7-7.json"),
            model=os.path.join(data_dir, "model", "L2V5.7-7.xml"),
        )
        with tempfile.NamedTemporaryFile(suffix=".json") as fod:
            neo4jsbml_statistics(config=config_path, output=fod.name)
            assert compare_json(
                result=fod.name,
                expect=os.path.join(data_dir, "statistics", "L2V5.7-7.json"),
            )

    def test_ex_8(self, data_dir, config_path):
        neo4jsbml_sbml_to_neo4j(
            config=config_path,
            arrows=os.path.join(data_dir, "arrows", "L2V5.7-8.json"),
            model=os.path.join(data_dir, "model", "L2V5.7-8.xml"),
        )
        with tempfile.NamedTemporaryFile(suffix=".json") as fod:
            neo4jsbml_statistics(config=config_path, output=fod.name)
            assert compare_json(
                result=fod.name,
                expect=os.path.join(data_dir, "statistics", "L2V5.7-8.json"),
            )

    def test_ex_9(self, data_dir, config_path):
        neo4jsbml_sbml_to_neo4j(
            config=config_path,
            arrows=os.path.join(data_dir, "arrows", "L2V5.7-9.json"),
            model=os.path.join(data_dir, "model", "L2V5.7-9.xml"),
        )
        with tempfile.NamedTemporaryFile(suffix=".json") as fod:
            neo4jsbml_statistics(config=config_path, output=fod.name)
            assert compare_json(
                result=fod.name,
                expect=os.path.join(data_dir, "statistics", "L2V5.7-9.json"),
            )

    def test_ex_10(self, data_dir, config_path):
        neo4jsbml_sbml_to_neo4j(
            config=config_path,
            arrows=os.path.join(data_dir, "arrows", "L2V5.7-10.json"),
            model=os.path.join(data_dir, "model", "L2V5.7-10.xml"),
        )
        with tempfile.NamedTemporaryFile(suffix=".json") as fod:
            neo4jsbml_statistics(config=config_path, output=fod.name)
            assert compare_json(
                result=fod.name,
                expect=os.path.join(data_dir, "statistics", "L2V5.7-10.json"),
            )

    def test_ex_11(self, data_dir, config_path):
        neo4jsbml_sbml_to_neo4j(
            config=config_path,
            arrows=os.path.join(data_dir, "arrows", "L2V5.7-11.json"),
            model=os.path.join(data_dir, "model", "L2V5.7-11.xml"),
        )
        with tempfile.NamedTemporaryFile(suffix=".json") as fod:
            neo4jsbml_statistics(config=config_path, output=fod.name)
            assert compare_json(
                result=fod.name,
                expect=os.path.join(data_dir, "statistics", "L2V5.7-11.json"),
            )
