import hashlib
import itertools
import logging
import re
from typing import Any, Dict, Generator, List, Optional

import libsbml
import networkx as nx
from neo4jsbml import arrows, graph_method, snode, srelationship


class Sbml(object):
    """Help to map entities coming from Arrows and SBML.

    Attributes
    ----------
    document: libsml.Document
        a document
    plugins: List[str]
        a list of plugin name

    Methods
    -------
    __init__(document: libsbml.SBML_DOCUMENT, *args, **kwargs)
        Instanciate a new object.

    @classmethod
    iterate_over_attribute(obj: Any) -> Generator:
        Generator to select useful attributes

    @classmethod
    has_method(obj: Any, method: str) -> bool
        Given an object, check if an object as a method.
    """

    PLUGINS = ["fbc", "groups", "layout", "qual"]

    def __init__(self, document: libsbml.SBML_DOCUMENT, *args, **kwargs) -> None:
        self.document = document

    @classmethod
    def iterate_over_attribute(cls, obj: Any) -> Generator:
        """Iterate over attributes of an object

        Parameters
        ----------
        obj: Any
            any object

        Return
        ------
        Generator
        """
        # Exact match
        for attribute in dir(obj):
            if (
                not attribute.startswith("__")
                and not attribute.startswith("enable")
                and not attribute.startswith("get")
                and not attribute.startswith("is")
                and not attribute.startswith("matches")
                and not attribute.startswith("remove")
                and not attribute.startswith("set")
                and not attribute.startswith("unset")
                and not attribute.startswith("write")
            ):
                attr = getattr(obj, attribute, None)

                if attr and not callable(attr):
                    yield attribute

    @classmethod
    def has_method(cls, obj: Any, method: str) -> bool:
        """Given an object, check if an object as a method.

        Parameters
        ----------
        obj: Any
            any object

        Return
        ------
        bool
        """
        return method in obj.__dir__()


class SbmlFromNeo4j(Sbml):
    """Help to map entities coming from Arrows and SBML.

    Attributes
    ----------
    model: libsml.Model
        a model extract from the document

    Methods
    -------
    __init__(document: libsbml.SBML_DOCUMENT)
        Instanciate a new object

    @classmethod
    from_specifications(level: int, version: int) -> "SbmlFromNeo4j"
        Create an Sbml object given a SBML file
    """

    def __init__(self, *args, **kwargs) -> None:
        super(SbmlFromNeo4j, self).__init__(*args, **kwargs)
        self.model = self.document.createModel()
        self.graph_methods = graph_method.GraphMethod.from_document(
            document=self.document
        )

    @classmethod
    def from_specifications(cls, level: int = 3, version: int = 2) -> "SbmlFromNeo4j":
        """Create an SbmlFromNeo4j object given the version of the specifications.

        Parameters
        ----------
        level: int
            Number of the level
        version: int
            Number of the version

        Return
        ------
        SbmlFromNeo4j
        """
        doc = libsbml.SBMLDocument(level=level, version=version)
        return SbmlFromNeo4j(document=doc)


class SbmlToNeo4j(Sbml):
    """Help to map entities coming from Arrows and SBML.

    Attributes
    ----------
    tag: str
        identify nodes from an extra arguments for Neo4j
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

    validate_id(value: Any) -> bool
        Check if an ID is in the SBML document

    candidate_obj_plugin(obj: Any) -> List[Any]
        Check if an object can activate one or several plugins

    @classmethod
    find_method(obj: Any, label: str) -> List[str]
        Given an object, search a method name by intropection

    @classmethod
    from_sbml(path: str, tag: Optional[str] = None) -> "SbmlToNeo4j"
        Create an Sbml object given a SBML file
    """

    def __init__(self, tag: Optional[str] = None, *args, **kwargs) -> None:
        super(SbmlToNeo4j, self).__init__(*args, **kwargs)
        self.tag = tag
        self.model = self.document.getModel()
        self.node_map_item: Dict[str, List[str]] = {}
        self.node_map_label: Dict[str, str] = {}
        self.elements: Dict[str, Any] = {}
        self.element_alls: Dict[str, Any] = {}  # speed up element retrievial

        if self.model is None:
            raise ValueError("No model found")
        self.plugins = []
        for plugin in self.PLUGINS:
            if self.document.getPlugin(plugin) is not None:
                self.plugins.append(plugin)

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
            if len(arrow_node.labels) < 1:
                logging.warning("None label is found for a node: %s" % (arrow_node.id,))
                continue
            label = arrow_node.labels[0]
            self.node_map_label[arrow_node.id] = label
            for ix, item in enumerate(self.document.getListOfAllElements()):
                if item.getElementName().lower() != label.lower():
                    continue
                dbb_node = snode.SNode(id="", labels=arrow_node.labels, properties={})
                data: Dict[str, Any] = {}

                # Iterate over plugin oject
                objs = self.candidate_obj_plugin(obj=item)
                for prop in arrow_node.properties:
                    prop_found = False
                    for ix, element in enumerate(objs):
                        methods = self.find_method(obj=element, label=prop)
                        if len(methods) < 1:
                            continue
                        if len(methods) > 1:
                            msg = (
                                "Several methods found for label: %s with the property: %s, %s"
                                % (label, prop, " ".join(methods))
                            )
                            if ix > 1:
                                msg += ", corresponding to the plugin: %s" % (
                                    self.plugins[ix],
                                )
                            logging.warning(msg)
                            continue
                        if prop.lower() == "id":
                            prop = "id"
                        # Check if value need to be formatted: str, math, ... (?)
                        value = eval("element.%s()" % (methods[0],))
                        if type(value) == libsbml.XMLNode:
                            try:
                                value = value.toXMLString()
                            except Exception:
                                pass
                        elif type(value) == libsbml.ASTNode:
                            try:
                                value = libsbml.formulaToL3String(value)
                            except Exception:
                                pass
                        data[prop] = value
                        prop_found = True
                        break
                    if prop_found is False:
                        logging.warning(
                            "No method found for label: %s with the property: %s"
                            % (label, prop)
                        )

                # Fill tag if needed
                if self.tag is not None:
                    data["tag"] = self.tag
                # Overwrite id attribute
                data["id"] = self.create_id(value=item)
                # Add name attribute
                if data.get("name", None) is None or data.get("name", "") == "":
                    data["name"] = data["id"]
                # Update map
                if arrow_node.id not in self.node_map_item.keys():
                    self.node_map_item[arrow_node.id] = []
                self.node_map_item[arrow_node.id].append(data["id"])
                self.elements[data["id"]] = item

                dbb_node.id = data.pop("id")
                dbb_node.properties = data
                dbb_node.clean_properties()

                res.append(dbb_node)

        # Populate element_alls
        for item in self.document.getListOfAllElements():
            self.element_alls[self.create_id(value=item)] = item

        for record in res:
            logging.debug(record)

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

        # Search relationships by method name, at least one exists
        methods = []
        for from_id in from_ids:
            from_obj = self.get_element_by_id(value=from_id)
            methods.extend(self.find_method(obj=from_obj, label=to_label, exact=False))
        if len(set(methods)) == 0:
            for to_id in to_ids:
                to_obj = self.get_element_by_id(value=to_id)
                methods.extend(
                    self.find_method(obj=to_obj, label=from_label, exact=False)
                )
            if len(set(methods)) == 1:
                is_forward = False
        methods = list(set(methods))
        if len(methods) > 1 or len(methods) < 1:
            return res

        if is_forward is False:
            z_ids = from_ids
            from_ids = to_ids
            to_ids = z_ids

        for from_id in from_ids:
            from_obj = self.get_element_by_id(value=from_id)
            for to_id in to_ids:
                target_id = ""
                to_obj = self.get_element_by_id(value=to_id)
                if from_obj is None or to_obj is None:
                    continue
                is_found = False
                # Try without argument
                try:
                    target_id = eval("from_obj.%s()" % (methods[0],))
                    is_found = True
                except Exception:
                    pass
                # Try str argument
                if is_found is False:
                    try:
                        target_obj = eval('from_obj.%s("%s")' % (methods[0], to_id))
                        target_id = self.create_id(value=target_obj)
                        is_found = True
                    except Exception:
                        pass
                # Try int argument
                if is_found is False:
                    try:
                        target_obj = eval("from_obj.%s(%s)" % (methods[0], to_id))
                        target_id = self.create_id(value=target_obj)
                        is_found = True
                    except Exception:
                        pass

                if is_found is False:
                    continue
                if target_id == to_id:
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

    def _find_by_relationships(
        self,
        arrow_label: str,
        from_label: str,
        to_label: str,
        from_ids: List[str],
        to_ids: List[str],
    ) -> List[srelationship.SRelationship]:
        res: List[srelationship.SRelationship] = []
        for from_id in from_ids:
            from_obj = self.get_element_by_id(value=from_id)
            if from_obj is None:
                continue
            methods = []
            labels = [arrow_label] + arrow_label.split("_")
            objs = self.candidate_obj_plugin(obj=from_obj)
            to_id = ""
            for from_obj, label in itertools.product(objs, labels):
                methods = self.find_method(obj=from_obj, label=label, exact=False)
                if len(methods) > 0:
                    try:
                        to_id = eval("from_obj.%s()" % (methods[0],))
                    except Exception:
                        pass
                if to_id != "":
                    break

            if self.validate_id(value=to_id):
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

    def find_by_relationships(
        self,
        arrow_label: str,
        from_label: str,
        to_label: str,
        from_ids: List[str],
        to_ids: List[str],
    ) -> List[srelationship.SRelationship]:
        res: List[srelationship.SRelationship] = []
        res.extend(
            self._find_by_relationships(
                arrow_label=arrow_label,
                from_label=from_label,
                to_label=to_label,
                from_ids=from_ids,
                to_ids=to_ids,
            )
        )
        if len(res) > 0:
            return res
        res_invert = self._find_by_relationships(
            arrow_label=arrow_label,
            from_label=to_label,
            to_label=from_label,
            from_ids=to_ids,
            to_ids=from_ids,
        )
        for record in res_invert:
            record.swap()
        res.extend(res_invert)
        return res

    def _find_by_relationships_listof(
        self,
        arrow_label: str,
        from_label: str,
        to_label: str,
        from_ids: List[str],
        to_ids: List[str],
    ) -> List[srelationship.SRelationship]:
        res: List[srelationship.SRelationship] = []
        for from_id in from_ids:
            from_obj = self.get_element_by_id(value=from_id)
            if from_obj is None:
                continue
            methods = []
            labels = [arrow_label] + arrow_label.split("_")
            labels = ["listof" + x for x in labels]
            for label in labels:
                methods = self.find_method(obj=from_obj, label=label)
                if len(methods) > 0:
                    break
            if len(methods) == 0:
                continue
            list_of_els = eval("from_obj.%s()" % (methods[0],))
            for from_el in list_of_els:
                from_el_name = from_el.getElementName()
                from_el_id = self.create_id(value=from_el)
                if from_el_name.endswith("Reference") and not to_label.lower().endswith(
                    "reference"
                ):
                    for attribute in Sbml.iterate_over_attribute(obj=from_el):
                        to_id = eval("from_el.%s" % (attribute,))
                        if self.validate_id(value=to_id):
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
                            break
                elif self.validate_id(value=from_el_id):
                    dbb_rel = srelationship.SRelationship(
                        id="",
                        from_label=from_label,
                        to_label=to_label,
                        from_id=from_id,
                        to_id=from_el_id,
                        label=arrow_label,
                        properties={},
                    )
                    res.append(dbb_rel)
        return res

    def find_by_relationships_listof(
        self,
        arrow_label: str,
        from_label: str,
        to_label: str,
        from_ids: List[str],
        to_ids: List[str],
    ) -> List[srelationship.SRelationship]:
        res: List[srelationship.SRelationship] = []
        res.extend(
            self._find_by_relationships_listof(
                arrow_label=arrow_label,
                from_label=from_label,
                to_label=to_label,
                from_ids=from_ids,
                to_ids=to_ids,
            )
        )
        if len(res) > 0:
            return res
        res_invert = self._find_by_relationships_listof(
            arrow_label=arrow_label,
            from_label=to_label,
            to_label=from_label,
            from_ids=to_ids,
            to_ids=from_ids,
        )
        for record in res_invert:
            record.swap()
        res.extend(res_invert)
        return res

    def _find_by_all_elements(
        self,
        arrow_label: str,
        from_label: str,
        to_label: str,
        from_ids: List[str],
        to_ids: List[str],
    ) -> List[srelationship.SRelationship]:
        res: List[srelationship.SRelationship] = []
        for from_id in from_ids:
            from_obj = self.get_element_by_id(value=from_id)
            if from_obj is None:
                continue
            for element in from_obj.getListOfAllElements():
                to_id = None
                methods = self.find_method(obj=element, label=to_label, exact=True)

                if len(methods) == 1:
                    try:
                        to_id = eval("element.%s()" % (methods[0],))
                    except Exception:
                        pass
                if (
                    to_id is None
                    and element.getElementName().lower() == to_label.lower()
                ):
                    to_id = self.create_id(value=element)
                if to_id and not isinstance(to_id, str):
                    to_id = self.create_id(value=element)
                if to_id and to_id != "":
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
        res.extend(
            self._find_by_all_elements(
                arrow_label=arrow_label,
                from_label=from_label,
                to_label=to_label,
                from_ids=from_ids,
                to_ids=to_ids,
            )
        )
        if len(res) > 0:
            return res
        res_invert = self._find_by_all_elements(
            arrow_label=arrow_label,
            from_label=to_label,
            to_label=from_label,
            from_ids=to_ids,
            to_ids=from_ids,
        )
        for record in res_invert:
            record.swap()
        res.extend(res_invert)
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
            srel = self.find_by_relationships_listof(
                arrow_label=arrow_rel.label,
                from_label=from_label,
                to_label=to_label,
                from_ids=from_ids,
                to_ids=to_ids,
            )
            if len(srel) > 0:
                logging.info(
                    "Map entities by the relationship's name (listOf): %s - %s"
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
        if self.tag is not None:
            for srelation in res:
                srelation.add_property(label="tag", value=self.tag)

        for record in res:
            logging.debug(record)

        return res

    def validate_id(self, value: str) -> bool:
        """Check if an ID is in the SBML document.

        Paramerters
        -----------
        value: str
            an ID to check

        Return
        ------
        bool
            True if the ID is found in the model
        """
        if not isinstance(value, str):
            return False
        if value == "":
            return False
        if self.elements.get(value):
            return True
        if self.document.getElementBySId(value) is not None:
            return True
        return value in self.element_alls.keys()

    def get_element_by_id(self, value: str) -> Optional[Any]:
        """Return an element belonging to the model from its ID.

        Parameters
        -----------
        value: str
            the ID of the element to retrieve

        Return
        ------
        Any
            An element in the model
        """
        if self.document.getElementBySId(value):
            return self.document.getElementBySId(value)
        if self.elements.get(value):
            return self.elements.get(value)
        return self.element_alls.get(value, None)

    def create_id(self, value: Any) -> str:
        """Sometimes an element of the model has no ID.
        If the ID exists it will be returned otherwise, an hash computed on the string representation is used.

        Parameters
        -----------
        value: Any
            An element of the model

        Return
        ------
        str
            The ID of the element
        """
        # Use Id or IdAttribute if it set
        ident = value.getId()
        if Sbml.has_method(obj=value, method="getIdAttribute"):
            id_attribute = value.getIdAttribute()
            if id_attribute != "" and id_attribute != ident:
                ident += "-" + id_attribute
        if ident and ident != "":
            return ident
        # Use str representation
        value_str = value.toXMLNode().toXMLString()
        ident = hashlib.md5(value_str.encode("utf8")).hexdigest()
        return ident

    def candidate_obj_plugin(self, obj: Any) -> List[Any]:
        """Check if an object can activate one or several plugins

        Parameters
        ----------
        obj: Any
            an object to activate some plugins

        Return
        ------
        List[Any]
        """
        candidates = [obj]
        for plugin in self.plugins:
            candidates.append(obj.getPlugin(plugin))
        return candidates

    @classmethod
    def find_method(cls, obj: Any, label: str, exact: bool = False) -> List[str]:
        """Given an object, search a method name by intropection.

        Parameters
        ----------
        obj: Any
            any object
        label: str
            a method to search
        exact: bool
            expect exact match

        Return
        ------
        List[str]
        """
        # Exact match
        regex = re.compile(r"^get" + label + "$", re.IGNORECASE)
        candidates = list(filter(regex.match, obj.__dir__()))
        if len(candidates) == 1:
            return candidates
        if exact:
            return []
        # Partial match
        regex = re.compile(r"get.*" + label, re.IGNORECASE)
        candidates = list(filter(regex.search, obj.__dir__()))
        return candidates

    @classmethod
    def from_sbml(cls, path: str, tag: Optional[str] = None) -> "SbmlToNeo4j":
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
        SbmlToNeo4j
        """
        doc = libsbml.readSBML(path)
        errors = doc.getNumErrors()
        if errors > 0:
            logging.error(doc.printErrors())
            raise ValueError("Error when parsing SBML -> abort")
        return SbmlToNeo4j(tag=tag, document=doc)
