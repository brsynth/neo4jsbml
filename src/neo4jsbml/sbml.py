import hashlib
import itertools
import logging
import re
from typing import Any, Dict, Generator, List, Optional, Union

import libsbml
import networkx as nx
from neo4jsbml import arrows, connect, graph_method, snode, srelationship


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

    @classmethod
    find_method(obj: Any, label: str, exact: bool, start: str) -> List[str]
        Given an object, search a method name by intropection
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

    @classmethod
    def find_method(
        cls, obj: Any, label: str, exact: bool = False, start: str = "get"
    ) -> List[str]:
        """Given an object, search a method name by intropection.

        Parameters
        ----------
        obj: Any
            any object
        label: str
            a method to search
        exact: bool
            expect exact match
        start: str
            beginning of the expression (default: get)

        Return
        ------
        List[str]
        """
        # Exact match
        regex = re.compile(r"^" + start + label + "$", re.IGNORECASE)
        candidates = list(filter(regex.match, obj.__dir__()))
        if len(candidates) == 1:
            return candidates
        if exact:
            return []
        # Partial match
        regex = re.compile(r"" + start + ".*" + label, re.IGNORECASE)
        candidates = list(filter(regex.search, obj.__dir__()))
        return candidates

    @classmethod
    def cast_properties(cls, value: str) -> Optional[Union[str, float, int, bool]]:
        # Check isdigit
        m = re.match(r"^-?\d+(\.\d+)?$", value)
        if m and m.group(1):
            return float(value)
        elif m and m.group(1) is None:
            return int(value)
        # Check is bool
        m = re.match(r"(True)|(False)", value, re.I)
        if m and m.group(1):
            return True
        elif m and m.group(2):
            return False
        # Undefined
        if value == "" or value == "nan":
            return None
        # Return str
        return value


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

     extract_entities(self, current_id: Optional[str]) -> None
        Extract entities of Neo4j based on the graph, GraphMethod

    add_node_properties(self, current: Any, data: Dict[str, Any], props: Dict[str, Any]) -> None
        Set properties found in Arrows, mapping to Neo4j, to a libsbml object

    add_neighbor_properties(self, current: Any, data: Dict[str, Any], props: Dict[str, Any], successors: List[str]) -> None
        Sometimes a node associated to another in Neo4j takes place as property

    annotate(self, modelisation: arrows.Arrows) -> None
        Annotate the graph_method attribute with a modelisation

    conciliate_labels(self) -> None
        Associate a label found in Neo4j to a label from the gaph_method attribute

    to_sbml(self, path: str) -> None
        Export the document attribute to a SBML file

    @classmethod
    from_specifications(level: int, version: int, connection: connect.Connect) -> "SbmlFromNeo4j"
        Create an Sbml object given a SBML file
    """

    def __init__(self, connection: connect.Connect, *args, **kwargs) -> None:
        super(SbmlFromNeo4j, self).__init__(*args, **kwargs)
        self.gm = graph_method.GraphMethod.from_document(document=self.document)
        self.connection = connection

    def extract_entities(self, current_id: Optional[str]) -> None:
        """Extract entities of Neo4j based on the graph, GraphMethod

        Parameters
        ----------
        current_id: Optional[str]
            current id of the graph_methods property

        Return
        ------
        None
        """
        if current_id is None:
            model = self.document.createModel()
            cur_id = self.gm.retrieve_id(prop="labels", value="Model")
            if self.gm.graph.nodes[cur_id]["modelisation"]:
                datas = self.connection.query_node(
                    label=self.gm.graph.nodes[cur_id]["labels_neo4j"]
                )
                if datas and len(datas) == 1:
                    self.add_node_properties(
                        current=model,
                        data=datas[0],
                        props=self.gm.graph.nodes[cur_id].get("properties", {}),
                    )
            self.gm.graph.nodes[cur_id]["objects"] = {cur_id: model}
            return self.extract_entities(
                current_id=cur_id,
            )
        for child_id in self.gm.graph.successors(current_id):
            label = self.gm.graph.nodes[child_id]["labels"]
            if self.gm.graph.nodes[child_id]["modelisation"]:
                # Query Neo4j
                datas = self.connection.query_node(
                    label=self.gm.graph.nodes[child_id]["labels_neo4j"],
                )
                # Loop over multiple nodes in Neo4j
                for data in datas:
                    # Get predecessor
                    current = None
                    predecessor = list(self.gm.graph.predecessors(child_id))[0]
                    if self.gm.graph.nodes[child_id]["level"] == 1:
                        # We want the "model" object included or not in Neo4j
                        current = list(
                            self.gm.graph.nodes[current_id]["objects"].values()
                        )[0]
                    else:
                        neighbors = self.connection.query_neighbor(
                            elementId=data["nodeId"]
                        )
                        child_relationship = self.gm.graph.nodes[child_id].get(
                            "relationship"
                        )
                        for neighbor in neighbors:
                            if graph_method.GraphMethod.compare_labels(
                                first=neighbor["nodeLabels"][0],
                                second=self.gm.graph.nodes[predecessor]["labels_neo4j"],
                            ):
                                if child_relationship:
                                    if (
                                        graph_method.GraphMethod.compare_labels(
                                            first=neighbor["relationship"][0][1],
                                            second=child_relationship["label"],
                                        )
                                        and neighbor["nodeId"]
                                        in self.gm.graph.nodes[predecessor][
                                            "objects"
                                        ].keys()
                                    ):
                                        current = self.gm.graph.nodes[predecessor][
                                            "objects"
                                        ][neighbor["nodeId"]]
                                else:
                                    current = self.gm.graph.nodes[predecessor][
                                        "objects"
                                    ][neighbor["nodeId"]]
                                break
                    if current is None:
                        continue
                    cur_obj = eval("current.create%s()" % (label,))
                    # Add properties attached to the node
                    self.add_node_properties(
                        current=cur_obj,
                        data=data,
                        props=self.gm.graph.nodes[child_id].get("properties"),
                    )
                    # Add properties attached as a neighbor
                    successor_labels = [
                        self.gm.graph.nodes[x]["labels"]
                        for x in self.gm.graph.successors(child_id)
                    ]
                    self.add_neighbor_properties(
                        current=cur_obj,
                        data=data,
                        props=self.gm.graph.nodes[child_id].get("properties"),
                        successors=successor_labels,
                    )
                    # Save
                    if "objects" not in self.gm.graph.nodes[child_id].keys():
                        self.gm.graph.nodes[child_id]["objects"] = {}
                    self.gm.graph.nodes[child_id]["objects"][data["nodeId"]] = cur_obj
                    # Iterate
                    self.extract_entities(
                        current_id=child_id,
                    )
            """
            else:
                # Loop over successors to know if we need to create a new object and pursuing or to skip
                pathways = nx.dfs_tree(self.graph, child_id)
                counts = [self.graph[x]["modelisation"] for x in pathways]
                if sum(counts) > 0:
                    cur_obj = eval("current.create%s()" % (label,))
                    self.extract_entities(
                        current=cur_obj,
                        current_id=child_id,
                    )
            """

    def add_node_properties(
        self, current: Any, data: Dict[str, Any], props: Dict[str, Any]
    ) -> None:
        """Set properties found in Arrows, mapping to Neo4j, to a libsbml object

        Parameters
        ----------
        current: Any
            A libsbml object
        data: Dict[str, Any]
            Query from Neo4j regarding a node
        props: Dict[str, Any]
            Properties of a graph_method node

        Return
        ------
        None
        """
        for prop in props.keys():
            # Check if Modelisation's property is in database
            if prop in data["node"].keys():
                # Check if libsbml has the method
                methods = Sbml.find_method(obj=current, label=prop, start="set")
                if len(methods) != 1:
                    continue
                # Check if Neo4j's data has the method
                for key, value in data["node"].items():
                    if prop == key:
                        # Add property
                        nvalue = Sbml.cast_properties(value=value)
                        # Check if property is empty
                        if nvalue is not None:
                            if key.lower() == "math":
                                ast_value = libsbml.parseL3Formula(
                                    nvalue
                                )  # Throw F841 error, local variable is assigned to but never used
                                eval("current.%s(ast_value)" % (methods[0],))
                            elif value == nvalue:
                                eval('current.%s("%s")' % (methods[0], value))
                            else:
                                eval("current.%s(%s)" % (methods[0], nvalue))
                        break

    def add_neighbor_properties(
        self,
        current: Any,
        data: Dict[str, Any],
        props: Dict[str, Any],
        successors: List[str],
    ) -> None:
        """Sometimes a node associated to another in Neo4j takes place as property

        Parameters
        ----------
        current: Any
            A libsbml object
        data: Dict[str, Any]
            Query from Neo4j regarding a node
        props: Dict[str, Any]
            Properties of a graph_method node
        successors: List[str]
            Listing of node connected

        Return
        ------
        None
        """

        # Extract neighbors from data
        neighbors = self.connection.query_neighbor(elementId=data["nodeId"])
        for neighbor in neighbors:
            for prop in props.keys():
                labels = neighbor["nodeLabels"]
                # Skip if an object will be added instead a property
                if labels[0] in successors:
                    continue
                # Check if libsbml has the method
                methods = Sbml.find_method(obj=current, label=labels[0], start="set")
                if len(methods) != 1:
                    continue
                # Extract id from neighbor
                neighbor_format = dict()
                for key, value in neighbor["nodeNeighbor"].items():
                    neighbor_format[key.lower()] = value
                neighbor_id = neighbor_format.get("id", "")
                neighbor_id = Sbml.cast_properties(value=neighbor_id)
                # Add property
                if neighbor_id is not None:
                    eval('current.%s("%s")' % (methods[0], neighbor_id))
                    break

    def annotate(self, modelisation: arrows.Arrows) -> None:
        """Annotate the graph_method attribute with a modelisation

        Paramters
        ---------
        modelisation: arrows:Arrows
            A modelisation

        Return
        ------
        None
        """
        self.gm.annotate(modelisation=modelisation)

    def conciliate_labels(self) -> None:
        """Associate a label found in Neo4j to a label from the gaph_method attribute

        Return
        ------
        None
        """
        # Query
        labels = self.connection.query_labels()
        # Format query
        labels = [x["label"] for x in labels]
        labels = list(set(itertools.chain(*labels)))
        # Associate label
        for node_id in self.gm.graph.nodes:
            if (
                self.gm.graph.nodes[node_id]["modelisation"]
                and "labels_neo4j" not in self.gm.graph.nodes[node_id].keys()
            ):
                label = self.gm.graph.nodes[node_id]["labels"]
                # Give priority on Arrows
                if "labels_arrows" in self.gm.graph.nodes[node_id].keys():
                    label = self.gm.graph.nodes[node_id]["labels_arrows"]
                regex = re.compile(r"^" + label + "$", re.IGNORECASE)
                candidates = list(filter(regex.search, labels))
                if len(candidates) == 1:
                    self.gm.graph.nodes[node_id]["labels_neo4j"] = candidates[0]

    @classmethod
    def from_specifications(
        cls,
        connection: connect.Connect,
        level: int = 3,
        version: int = 2,
    ) -> "SbmlFromNeo4j":
        """Create an SbmlFromNeo4j object given the version of the specifications.

        Parameters
        ----------
        level: int
            Number of the level
        version: int
            Number of the version
        connection: connect.Connect
            Connection object

        Return
        ------
        SbmlFromNeo4j
        """
        doc = libsbml.SBMLDocument(level, version)
        return SbmlFromNeo4j(connection=connection, document=doc)

    def to_sbml(self, path: str) -> None:
        """Export the document attribute to a SBML file

        Parameters
        ----------
        path: str
            The path of the file

        Return
        ------
        None
        """
        data = libsbml.writeSBMLToString(self.document)
        with open(path, "w") as fd:
            fd.write(data)


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
                        methods = Sbml.find_method(obj=element, label=prop)
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
            methods.extend(Sbml.find_method(obj=from_obj, label=to_label, exact=False))
        if len(set(methods)) == 0:
            for to_id in to_ids:
                to_obj = self.get_element_by_id(value=to_id)
                methods.extend(
                    Sbml.find_method(obj=to_obj, label=from_label, exact=False)
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
                methods = Sbml.find_method(obj=from_obj, label=label, exact=False)
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
                methods = Sbml.find_method(obj=from_obj, label=label)
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
                methods = Sbml.find_method(obj=element, label=to_label, exact=True)

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
