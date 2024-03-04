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
class TestBigg:
    def setUp(self, config_path):
        neo4jsbml_clean(config=config_path)

    def test_iml1515(self, data_dir, config_path):
        neo4jsbml_sbml_to_neo4j(
            config=config_path,
            arrows=os.path.join(data_dir, "arrows", "PathwayModelisation-2.0.2.json"),
            model=os.path.join(data_dir, "model", "iML1515.xml.gz"),
        )
        with tempfile.NamedTemporaryFile(suffix=".json") as fod:
            neo4jsbml_statistics(config=config_path, output=fod.name)
            assert compare_json(
                result=fod.name,
                expect=os.path.join(data_dir, "statistics", "iML1515.json"),
            )

    def test_iaf1260(self, data_dir, config_path):
        neo4jsbml_sbml_to_neo4j(
            config=config_path,
            arrows=os.path.join(data_dir, "arrows", "PathwayModelisation-2.0.2.json"),
            model=os.path.join(data_dir, "model", "iAF1260.xml.gz"),
        )
        with tempfile.NamedTemporaryFile(suffix=".json") as fod:
            neo4jsbml_statistics(config=config_path, output=fod.name)
            assert compare_json(
                result=fod.name,
                expect=os.path.join(data_dir, "statistics", "iAF1260.json"),
            )
