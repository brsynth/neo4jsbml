import imghdr
import sys
import tempfile

from neo4jsbml._version import __app_name__
from neo4jsbml.cmd import run


class TestAnalyzingModel:
    def test_base(self, ecore_path, config_path):
        fname = ""
        with tempfile.NamedTemporaryFile() as fd:
            fname = fd.name

        args = ["python", "-m", __app_name__]
        args += ["--input-config-file", config_path]
        args += ["--input-modelisation-json", fname]
        args += ["--input-file-sbml", ecore_path]

        ret = run(args)
        assert ret.returncode != 0
