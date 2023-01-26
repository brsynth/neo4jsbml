import logging
import re
from typing import Any, Dict, List, Optional

import libsbml

from neo4jsbml import arrows, snode, srelationship


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
    find_method(obj: Any, label: str) -> List[str]
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
                    methods = Sbml.find_method(obj=item, label=prop)
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

    def find_by_label(
        self,
        arrow_label: str,
        from_label: str,
        to_label: str,
        from_ids: List[str],
        to_ids: List[str],
    ) -> List[srelationship.SRelationship]:
        res: List[srelationship.SRelationship] = []
        # Determine forward or reverse
        is_forward = True
        from_obj = self.document.getElementBySId(from_ids[0])
        to_obj = self.document.getElementBySId(to_ids[0])

        # Search relationships by method name
        methods = Sbml.find_method(obj=from_obj, label=to_label)
        if len(methods) == 0:
            methods = Sbml.find_method(obj=to_obj, label=from_label)
            if len(methods) == 1:
                is_forward = False

        if len(methods) > 1 or len(methods) < 1:
            return res

        if is_forward is False:
            z_ids = from_ids
            from_ids = to_ids
            to_ids = z_ids

        for from_id in from_ids:
            for to_id in to_ids:
                from_obj = self.document.getElementBySId(from_id)
                to_obj = self.document.getElementBySId(to_id)

                cur_id = eval("from_obj.%s()" % (methods[0],))
                if cur_id == to_id:
                    dbb_rel = srelationship.SRelationship(
                        id="",
                        from_label=from_label,
                        to_label=to_label,
                        from_id=from_id,
                        to_id=to_id,
                        label=arrow_label,
                        properties={},
                    )

                    if is_forward is False:
                        dbb_rel.from_id = to_id
                        dbb_rel.to_id = from_id
                    res.append(dbb_rel)
        return res

    def find_by_relationships(
        self,
        arrow_label: str,
        from_label: str,
        to_label: str,
        from_ids: List[str],
        to_ids: List[str],
    ) -> List[srelationship.SRelationship]:
        res: List[srelationship.SRelationship] = []
        for from_id in from_ids:
            from_obj = self.document.getElementBySId(from_id)
            methods = []
            labels = [arrow_label] + arrow_label.split("_")
            for label in labels:
                methods = Sbml.find_method(obj=from_obj, label="listof" + label)
                if len(methods) > 0:
                    break
            if len(methods) == 0:
                continue
            list_of_els = eval("from_obj.%s()" % (methods[0],))
            for from_el in list_of_els:
                from_el_name = from_el.getElementName()
                if from_el_name.endswith("Reference"):
                    from_el_name = from_el_name.removesuffix("Reference")
                    methods = Sbml.find_method(obj=from_el, label=from_el_name)
                    if len(methods) == 1:
                        to_id = eval("from_el.%s()" % (methods[0],))
                        dbb_rel = srelationship.SRelationship(
                            id="",
                            from_label=from_label,
                            to_label=to_label,
                            from_id=from_id,
                            to_id=to_id,
                            label=arrow_label,
                            properties={},
                        )
                        res.append(dbb_rel)
        for to_id in to_ids:
            to_obj = self.document.getElementBySId(to_id)
            methods = []
            labels = [arrow_label] + arrow_label.split("_")
            for label in labels:
                methods = Sbml.find_method(obj=to_obj, label="listof" + label)
                if len(methods) > 0:
                    break
            if len(methods) == 0:
                continue
            list_of_els = eval("to_obj.%s()" % (methods[0],))
            for to_el in list_of_els:
                to_el_name = to_el.getElementName()
                if to_el_name.endswith("Reference"):
                    to_el_name = to_el_name.removesuffix("Reference")
                    methods = Sbml.find_method(obj=to_el, label=to_el_name)
                    if len(methods) == 1:
                        from_id = eval("to_el.%s()" % (methods[0],))
                        dbb_rel = srelationship.SRelationship(
                            id="",
                            from_label=from_label,
                            to_label=to_label,
                            from_id=from_id,
                            to_id=to_id,
                            label=arrow_label,
                            properties={},
                        )
                        res.append(dbb_rel)
        return res

    def find_by_all_elements(
        self,
        arrow_label: str,
        from_label: str,
        to_label: str,
        from_ids: List[str],
        to_ids: List[str],
    ) -> List[srelationship.SRelationship]:
        res: List[srelationship.SRelationship] = []
        for from_id in from_ids:
            from_obj = self.document.getElementBySId(from_id)
            for from_el in from_obj.getListOfAllElements():
                methods = Sbml.find_method(obj=from_el, label=to_label)
                if len(methods) == 1:
                    to_id = eval("from_el.%s()" % (methods[0],))
                    dbb_rel = srelationship.SRelationship(
                        id="",
                        from_label=from_label,
                        to_label=to_label,
                        from_id=from_id,
                        to_id=to_id,
                        label=arrow_label,
                        properties={},
                    )
                    res.append(dbb_rel)
        for to_id in to_ids:
            to_obj = self.document.getElementBySId(to_id)
            for to_el in to_obj.getListOfAllElements():
                methods = Sbml.find_method(obj=to_el, label=from_label)
                if len(methods) == 1:
                    from_id = eval("to_el.%s()" % (methods[0],))
                    dbb_rel = srelationship.SRelationship(
                        id="",
                        from_label=from_label,
                        to_label=to_label,
                        from_id=from_id,
                        to_id=to_id,
                        label=arrow_label,
                        properties={},
                    )
                    res.append(dbb_rel)
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
        res: List[srelationship.SRelationship] = []
        for arrow_rel in relationships:
            from_label = self.node_map_label[arrow_rel.from_id]
            to_label = self.node_map_label[arrow_rel.to_id]

            from_ids = self.node_map_item.get(arrow_rel.from_id)
            to_ids = self.node_map_item.get(arrow_rel.to_id)
            if from_ids is None or to_ids is None:
                logging.warning(
                    "No relationship between: %s - %s"
                    % (
                        from_label,
                        to_label,
                    )
                )
                continue
            # Find by label
            srel = self.find_by_label(
                arrow_label=arrow_rel.label,
                from_label=from_label,
                to_label=to_label,
                from_ids=from_ids,
                to_ids=to_ids,
            )
            if len(srel) > 0:
                logging.info(
                    "Map entities by their label: %s - %s" % (from_label, to_label)
                )
                res.extend(srel)
                continue
            # Find by relationships
            srel = self.find_by_relationships(
                arrow_label=arrow_rel.label,
                from_label=from_label,
                to_label=to_label,
                from_ids=from_ids,
                to_ids=to_ids,
            )
            if len(srel) > 0:
                logging.info(
                    "Map entities by the relationship's name: %s - %s"
                    % (from_label, to_label)
                )
                res.extend(srel)
                continue
            # Find by all elements
            srel = self.find_by_all_elements(
                arrow_label=arrow_rel.label,
                from_label=from_label,
                to_label=to_label,
                from_ids=from_ids,
                to_ids=to_ids,
            )
            if len(srel) > 0:
                logging.info(
                    "Map entities by their id: %s - %s" % (from_label, to_label)
                )
                res.extend(srel)
                continue

            logging.warning(
                "No method was found for entities: %s and %s, belongs to the relationships: %s"
                % (from_label, to_label, arrow_rel.label)
            )
        return res

    @classmethod
    def find_method(cls, obj: Any, label: str) -> List[str]:
        """Given an object, search a method name by intropection.

        Parameters
        ----------
        obj: Any
            any object
        label: str
            a method to search

        Return
        ------
        List[str]
        """
        # Exact match
        regex = re.compile(r"^get" + label + "$", re.IGNORECASE)
        candidates = list(filter(regex.match, obj.__dir__()))
        if len(candidates) == 1:
            return candidates
        # Partial match
        regex = re.compile(r"get.*" + label, re.IGNORECASE)
        candidates = list(filter(regex.search, obj.__dir__()))
        return candidates

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
