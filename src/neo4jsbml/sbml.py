import logging
import re
from typing import Any, Dict, List, Optional

import libsbml

from neo4jsbml import _version, arrows, snode, srelationship


class Sbml(object):
    """Help to map entities coming from Arrows and SBML.

    Attributes
    ----------
    tag: str
        identify nodes from an extra arguments for Neo4j
    document: libsml.Document
        a document
    model: libsml.Model
        a model extract from the document

    Raises
    -----
    ValueError
        if no model found in the document

    Methods
    -------
    __init__(document: libsbml.SBML_DOCUMENT, tag: Optional[str])
        Instanciate a new object. tag parameter is optional

    format_nodes(nodes: List[arrows.Node]) -> List[Dict[str, Any]]
        Create nodes, from the schema and the values in the SBML file.

    format_relationships(relationships: List[arrows.Relationship]) -> List[Dict[str, Any]]:
        Create relationships, from the schema and the values in the SBML file

    @classmethod
    find_method(obj: Any, method: str) -> List[str]
        Given an object, search a method name by intropection

    @classmethod
    from_sbml(path: str, tag: Optional[str] = None) -> "Sbml"
        Create an Sbml object given a SBML file
    """

    def __init__(self, document: libsbml.SBML_DOCUMENT, tag: Optional[str]) -> None:
        self.tag = tag
        self.document = document
        self.model = self.document.getModel()
        self.node_map_item: Dict[str, List[str]] = {}
        self.node_map_label: Dict[str, str] = {}
        self.logger = logging.getLogger(name=_version.__app_name__)
        if self.model is None:
            raise ValueError("No model found")

    def format_nodes(self, nodes: List[snode.SNode]) -> List[snode.SNode]:
        """Create nodes, from the schema and the values in the SBML file.

        Parameters
        ----------
        nodes: List[snode.SNode]
            the nodes stored into the Arrows object

        Return
        ------
        List[node.Node]
        """
        res = []
        for arrow_node in nodes:
            label = arrow_node.labels[0]
            self.node_map_label[arrow_node.id] = label
            for ix, item in enumerate(self.model.getListOfAllElements()):
                if item.getElementName().lower() != label.lower():
                    continue
                dbb_node = snode.SNode(id="", labels=arrow_node.labels, properties={})
                data: Dict[str, Any] = {}
                for prop in arrow_node.properties:
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
                    data["id"] == "%s.%s" % (label, ix)
                # Update map
                if arrow_node.id not in self.node_map_item.keys():
                    self.node_map_item[arrow_node.id] = []
                self.node_map_item[arrow_node.id].append(data["id"])

                dbb_node.id = data.pop("id")
                dbb_node.properties = data
                dbb_node.clean_properties()

                res.append(dbb_node)
        return res

    def format_relationships(
        self, relationships: List[srelationship.SRelationship]
    ) -> List[srelationship.SRelationship]:
        """Create relationships, from the schema and the values in the SBML file.

        Parameters
        ----------
        relationships: List[relationship.Relationship]
            the relationships stored into the Arrows object

        Return
        ------
        List[relationship.Relationship]
        """
        res = []
        self.logger.debug("node_map_item: " + str(self.node_map_item))
        print(self.node_map_label)
        print(self.node_map_item)
        for arrow_rel in relationships:
            left_label = self.node_map_label[arrow_rel.from_id]
            right_label = self.node_map_label[arrow_rel.to_id]

            self.logger.debug("left_label: " + str(left_label))
            self.logger.debug("right_label: " + str(right_label))
            left_ids = self.node_map_item.get(arrow_rel.from_id)
            if left_ids is None:
                self.logger.warning(
                    "Missing data into the model: %s, skip"
                    % (self.node_map_label.get(arrow_rel.from_id),)
                )
                continue
            right_ids = self.node_map_item.get(arrow_rel.to_id)
            if right_ids is None:
                self.logger.warning(
                    "Missing data into the model: %s, skip"
                    % (self.node_map_label.get(arrow_rel.from_id),)
                )
                continue

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
                    % (left_label, right_label, rel.label)
                )
                continue

            # Loop over item
            if not is_forward:
                z_ids = left_ids
                left_ids = right_ids
                right_ids = z_ids

            for left_id in left_ids:
                for right_id in right_ids:

                    left_obj = self.document.getElementBySId(left_id)
                    right_obj = self.document.getElementBySId(right_id)

                    cur_id = eval("left_obj.%s()" % (methods[0],))
                    if cur_id == right_id:
                        dbb_rel = srelationship.SRelationship(
                            id="",
                            from_label=left_label,
                            to_label=right_label,
                            from_id=left_id,
                            to_id=right_id,
                            label=arrow_rel.label,
                            properties={},
                        )

                        if not is_forward:
                            dbb_rel.from_id = right_id
                            dbb_rel.to_id = left_id
                        res.append(dbb_rel)
        return res

    @classmethod
    def find_method(cls, obj: Any, method: str) -> List[str]:
        """Given an object, search a method name by intropection.

        Parameters
        ----------
        obj: Any
            any object
        method: str
            a method to search

        Return
        ------
        List[str]
        """
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
    def from_sbml(cls, path: str, tag: Optional[str] = None) -> "Sbml":
        """Create an Sbml object given a SBML file.

        Parameters
        ----------
        path: str
            a SBML file
        tag: Optional[str] (default: None)
            an extra identifier for the node

        Raises
        ------
        ValueError
            if an error is encountered during the loading of the file
        Return
        ------
        Sbml
        """
        doc = libsbml.readSBML(path)
        errors = doc.getNumErrors()
        if errors > 0:
            logging.error(doc.printErrors())
            raise ValueError("Error when parsing SBML -> abort")
        return Sbml(document=doc, tag=tag)
