import logging
import re
from typing import Any, Dict, List, Optional

import libsbml

from neo4jsbml import arrows, relationship


class Sbml(object):
    def __init__(self, document: libsbml.SBML_DOCUMENT, tag: Optional[str]) -> None:
        self.tag = tag
        self.document = document
        self.model = self.document.getModel()
        if self.model is None:
            raise ValueError("No model found")

    def format_nodes(self, nodes: List[arrows.Node]) -> List[Dict[str, Any]]:
        res = []
        for node in nodes:
            label = node.labels[0]
            for item in self.model.getListOfAllElements():
                if item.element_name.lower() != label.lower():
                    continue
                data: Dict[str, Any] = {"labels": node.labels}
                for prop in node.properties:
                    methods = Sbml.find_method(obj=item, method=prop)
                    if len(methods) == 0:
                        logging.warning(
                            "No method found for label: %s with the property: %s"
                            % (label, prop)
                        )
                        continue
                    if len(methods) > 1:
                        logging.warning(
                            "Several methods found for label: %s with the property: %s, %s"
                            % (label, prop, " ".join(methods))
                        )
                        continue
                    data[prop] = eval("item.%s()" % (methods[0],))
                if self.tag is not None:
                    data["tag"] = self.tag
                res.append(data)
        return Sbml.format_results(res)

    @classmethod
    def find_method(cls, obj: Any, method: str) -> List[str]:
        # Exact match
        regex = re.compile(r"^get" + method + "$", re.IGNORECASE)
        methods = list(filter(regex.match, obj.__dir__()))
        if len(methods) == 1:
            return methods
        # Partial match
        regex = re.compile(r"get.*" + method, re.IGNORECASE)
        methods = list(filter(regex.search, obj.__dir__()))
        return methods

    @classmethod
    def format_results(cls, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for ix, result in enumerate(results):
            keys = []
            for k, v in result.items():
                if v is None or v == "":
                    keys.append(k)
            for k in keys:
                del result[k]
            results[ix] = result
        return results

    @classmethod
    def from_sbml(cls, path: str, tag: Optional[str] = None) -> "Sbml":
        doc = libsbml.readSBML(path)
        errors = doc.getNumErrors()
        if errors > 0:
            logging.error(doc.printErrors())
            raise ValueError("Error when parsing SBML -> abort")
        return Sbml(document=doc, tag=tag)
