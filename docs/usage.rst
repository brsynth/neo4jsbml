Usage
=====

Installation
------------

To use neo4jsbml, first install it using conda:

.. code-block:: console

   $ conda install -c conda-forge -n neo4jsbml

Principles
----------
First of all, the users create a schema defining which entities will be selected from the SBML model, see Figure 1A. Building a schema required several rules. The general idea is to map the name of the different items found in the schema corresponding to items as they are defined in the SBML specifications (Hucka et al., 2019). So, the label of the nodes need to be matched to a SBML component name. In the same way, the properties are selected by their name if they match to the properties of the SBML component. The SBML specifications indicate which components are linked to other components but this relationship is not defined.  However, the relationships can be nested into another. Thus, the label and the direction of the relationship between two SBML components refers to a method which links two components. 

The SBML model is loaded by neo4jsbml, thanks to the libsbml library (Hucka et al., 2019), and the selected data will be loaded in the Neo4j database with the python Neo4j driver from the schema. Lastly, the entities and the relationships from the SBML model are queryable by Cypher into Neo4j (Figure 1B). An identifier can be associated for each entity created into Neo4j to avoid collision when several models are loaded in the same database.
Define your schema with Arrows
------------------------------

Import your data into Neo4j
---------------------------

Configure access to Neo4j
-------------------------

