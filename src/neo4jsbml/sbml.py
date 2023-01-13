import logging
import re
from typing import Any, Dict, List, Optional

import libsbml

from neo4jsbml import _version, arrows, relationship


class Sbml(object):
    def __init__(self, document: libsbml.SBML_DOCUMENT, tag: Optional[str]) -> None:
        self.tag = tag
        self.document = document
        self.model = self.document.getModel()
        self.node_map_item: Dict[str, List[str]] = {}
        self.node_map_label: Dict[str, str] = {}
        self.logger = logging.getLogger(name=_version.__app_name__)
        if self.model is None:
            raise ValueError("No model found")

    def format_nodes(self, nodes: List[arrows.Node]) -> List[Dict[str, Any]]:
        res = []
        for node in nodes:
            label = node.labels[0]
            self.node_map_label[node.id] = label
            for ix, item in enumerate(self.model.getListOfAllElements()):
                if item.getElementName().lower() != label.lower():
                    continue
                data: Dict[str, Any] = {"labels": node.labels}
                for prop in node.properties:
                    methods = Sbml.find_method(obj=item, method=prop)
                    if len(methods) == 0:
                        self.logger.warning(
                            "No method found for label: %s with the property: %s"
                            % (label, prop)
                        )
                        continue
                    if len(methods) > 1:
                        self.logger.warning(
                            "Several methods found for label: %s with the property: %s, %s"
                            % (label, prop, " ".join(methods))
                        )
                        continue
                    if prop.lower() == "id":
                        prop = "id"
                    data[prop] = eval("item.%s()" % (methods[0],))
                # Fill tag if needed
                if self.tag is not None:
                    data["tag"] = self.tag
                if data.get("id", None) is None or data.get("id", "") == "":
                    data["id"] == "%.%s" % (label, ix)
                # Update map
                if node.id not in self.node_map_item.keys():
                    self.node_map_item[node.id] = []
                self.node_map_item[node.id].append(data["id"])

                res.append(data)
        return Sbml.format_results(res)

    def format_relationships(
        self, relationships: List[arrows.Relationship]
    ) -> List[Dict[str, Any]]:
        res = []
        self.logger.debug("node_map_item: " + str(self.node_map_item))
        for relationship in relationships:
            left_label = self.node_map_label[relationship.from_id]
            right_label = self.node_map_label[relationship.to_id]

            self.logger.debug("left_label: " + str(left_label))
            self.logger.debug("right_label: " + str(right_label))
            left_ids = self.node_map_item[relationship.from_id]
            right_ids = self.node_map_item[relationship.to_id]

            self.logger.debug("left_ids: " + str(left_ids))
            self.logger.debug("right_ids: " + str(right_ids))

            # Determine forward or reverse
            is_forward = True
            left_id = left_ids[0]
            right_id = right_ids[0]

            left_obj = self.document.getElementBySId(left_id)
            right_obj = self.document.getElementBySId(right_id)

            self.logger.debug("left_id: " + str(left_id))
            self.logger.debug("right_id: " + str(right_id))
            self.logger.debug("left_obj: " + str(left_obj))
            self.logger.debug("right_obj: " + str(right_obj))
            methods = Sbml.find_method(obj=left_obj, method=right_label)
            if len(methods) == 0:
                methods = Sbml.find_method(obj=right_obj, method=left_label)
                if len(methods) == 1:
                    is_forward = False

            if len(methods) < 1:
                self.logger.warning(
                    "No method was found for entities: %s and %s, belongs to the relationships: %s"
                    % (left_label, right_label, relationship.type)
                )
                continue

            # Loop over item
            if not is_forward:
                z_ids = left_ids
                left_ids = right_ids
                right_ids = z_ids

            for left_id in left_ids:
                for right_id in right_ids:
                    data = dict(left=left_label, right=right_label)

                    left_obj = self.document.getElementBySId(left_id)
                    right_obj = self.document.getElementBySId(right_id)

                    cur_id = eval("left_obj.%s()" % (methods[0],))
                    if cur_id == right_id:
                        data["relationship"] = relationship.label
                        data["left_id"] = left_id
                        data["right_id"] = right_id

                        if not is_forward:
                            data["left_id"] = right_id
                            data["right_id"] = left_id
                        res.append(data)
        return Sbml.format_results(results=res)

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
