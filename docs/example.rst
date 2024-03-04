*******
Example
*******

SBML specification - L3V2
=========================

Some examples of Arrow's schemas and Neo4j views coming from the :download:`(SBML specification) <_static/specification/sbml.level-3.version-2.core.release-2.pdf>` chapter 7.

1 - A simple example application of SBML
----------------------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L3V2.7-1.json>`
| :download:`Model (XML.zip) <_static/model/L3V2.7-1.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L3V2.7-1.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L3V2.7-1.svg
    :align: center

2 - A simple example using the conversionFactor attribute
---------------------------------------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L3V2.7-2.json>`
| :download:`Model (XML.zip) <_static/model/L3V2.7-2.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L3V2.7-2.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L3V2.7-2.svg
    :align: center

3 - An alternative formulation of the conversionFactor example
--------------------------------------------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L3V2.7-3.json>`
| :download:`Model (XML.zip) <_static/model/L3V2.7-3.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L3V2.7-3.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L3V2.7-3.svg
    :align: center

4 - Example of a discrete version of a simple dimerization reaction
-------------------------------------------------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L3V2.7-4.json>`
| :download:`Model (XML.zip) <_static/model/L3V2.7-4.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L3V2.7-4.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L3V2.7-4.svg
    :align: center

5 - Example involving assignment rules
--------------------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L3V2.7-5.json>`
| :download:`Model (XML.zip) <_static/model/L3V2.7-5.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L3V2.7-5.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L3V2.7-5.svg
    :align: center

6 - Example involving algebraic rules
-------------------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L3V2.7-6.json>`
| :download:`Model (XML.zip) <_static/model/L3V2.7-6.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L3V2.7-6.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L3V2.7-6.svg
    :align: center

7 - Example with combinations of boundaryCondition and constant values on Species with RateRule objects
-------------------------------------------------------------------------------------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L3V2.7-7.json>`
| :download:`Model (XML.zip) <_static/model/L3V2.7-7.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L3V2.7-7.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L3V2.7-7.svg
    :align: center

8 - Example of translation from a multi-compartmental model to ODEs
-------------------------------------------------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L3V2.7-8.json>`
| :download:`Model (XML.zip) <_static/model/L3V2.7-8.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L3V2.7-8.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L3V2.7-8.svg
    :align: center

9 - Example involving function definitions
------------------------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L3V2.7-9.json>`
| :download:`Model (XML.zip) <_static/model/L3V2.7-9.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L3V2.7-9.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L3V2.7-9.svg
    :align: center

10 - Example involving delay functions
--------------------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L3V2.7-10.json>`
| :download:`Model (XML.zip) <_static/model/L3V2.7-10.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L3V2.7-10.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L3V2.7-10.svg
    :align: center

11 - Example involving events
-----------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L3V2.7-11.json>`
| :download:`Model (XML.zip) <_static/model/L3V2.7-11.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L3V2.7-11.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L3V2.7-11.svg
    :align: center

12 - Example involving two-dimensional compartments
---------------------------------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L3V2.7-12.json>`
| :download:`Model (XML.zip) <_static/model/L3V2.7-12.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L3V2.7-12.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L3V2.7-12.svg
    :align: center

13 - Example of a reaction located at a membrane
------------------------------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L3V2.7-13.json>`
| :download:`Model (XML.zip) <_static/model/L3V2.7-13.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L3V2.7-13.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L3V2.7-13.svg
    :align: center

14 - Example using an event with a non-persistent trigger and a delay
---------------------------------------------------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L3V2.7-14.json>`
| :download:`Model (XML.zip) <_static/model/L3V2.7-14.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L3V2.7-14.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L3V2.7-14.svg
    :align: center

SBML plugins
============

Some plugins can be used by Neo4jSbml:
* Flux Balance Constraints :download:`(specification) <_static/specification/sbml.level-3.version-1.fbc.version-2.release-1.pdf>`
* Groups :download:`(specification) <_static/specification/sbml.level-3.version-1.groups.version-1.release-1.pdf>`
* Layout :download:`(specification) <_static/specification/sbml.level-3.version-1.layout.version-1.release-1.pdf>`
* Qualitative Models :download:`(specification) <_static/specification/sbml.level-3.version-1.qual.version-1.release-1.pdf>`

1 - Flux Balance Constraints
----------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L3V1.fbc.V2R1.4-1.json>`
| :download:`Model (XML.zip) <_static/model/L3V1.fbc.V2R1.4-1.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L3V1.fbc.V2R1.4-1.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L3V1.fbc.V2R1.4-1.svg
    :align: center

2 - Groups
----------

| :download:`Arrow schema (JSON) <_static/arrows/L3V1.groups.V1R1.5-2.json>`
| :download:`Model (XML.zip) <_static/model/L3V1.groups.V1R1.5-2.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L3V1.groups.V1R1.5-2.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L3V1.groups.V1R1.5-2.svg
    :align: center

3 - Layout
----------

| :download:`Arrow schema (JSON) <_static/arrows/L3V1.layout.V1R1.4-5.json>`
| :download:`Model (XML.zip) <_static/model/L3V1.layout.V1R1.4-5.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L3V1.layout.V1R1.4-5.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L3V1.layout.V1R1.4-5.svg
    :align: center

4 - Qualitative Models
----------------------

| :download:`Arrow schema (JSON) <_static/arrows/L3V1.qual.V1R1.4-2.json>`
| :download:`Model (XML.zip) <_static/model/L3V1.qual.V1R1.4-2.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L3V1.qual.V1R1.4-2.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L3V1.qual.V1R1.4-2.svg
    :align: center

SBML specification - L2V5
=========================

Some examples of Arrow's schemas and Neo4j views coming from the :download:`(SBML specification) <_static/specification/sbml-level-2-version-5-rel-1.pdf>` chapter 7.

1 - A simple example application of SBML
----------------------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L2V5.7-1.json>`
| :download:`Model (XML.zip) <_static/model/L2V5.7-1.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L2V5.7-1.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L2V5.7-1.svg
    :align: center

2 - Example involving units
---------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L2V5.7-2.json>`
| :download:`Model (XML.zip) <_static/model/L2V5.7-2.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L2V5.7-2.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L2V5.7-2.svg
    :align: center

3 - Example of a discrete version of a simple dimerization reaction
-------------------------------------------------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L2V5.7-3.json>`
| :download:`Model (XML.zip) <_static/model/L2V5.7-3.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L2V5.7-3.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L2V5.7-3.svg
    :align: center

4 - Example involving assignment rules
--------------------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L2V5.7-4.json>`
| :download:`Model (XML.zip) <_static/model/L2V5.7-4.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L2V5.7-4.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L2V5.7-4.svg
    :align: center

5 - Example involving algebraic rules
-------------------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L2V5.7-5.json>`
| :download:`Model (XML.zip) <_static/model/L2V5.7-5.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L2V5.7-5.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L2V5.7-5.svg
    :align: center

6 - Example with combinations of boundaryCondition and constant values on Species with RateRule objects
-------------------------------------------------------------------------------------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L2V5.7-6.json>`
| :download:`Model (XML.zip) <_static/model/L2V5.7-6.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L2V5.7-6.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L2V5.7-6.svg
    :align: center

7 - Example of translation from a multi-compartmental model to ODEs
-------------------------------------------------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L2V5.7-7.json>`
| :download:`Model (XML.zip) <_static/model/L2V5.7-7.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L2V5.7-7.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L2V5.7-7.svg
    :align: center

8 - Example involving function definitions
------------------------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L2V5.7-8.json>`
| :download:`Model (XML.zip) <_static/model/L2V5.7-8.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L2V5.7-8.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L2V5.7-8.svg
    :align: center

9 - Example involving delay functions
-------------------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L2V5.7-9.json>`
| :download:`Model (XML.zip) <_static/model/L2V5.7-9.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L2V5.7-9.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L2V5.7-9.svg
    :align: center

10 - Example involving events
-----------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L2V5.7-10.json>`
| :download:`Model (XML.zip) <_static/model/L2V5.7-10.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L2V5.7-10.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L2V5.7-10.svg
    :align: center

11 - Example involving two-dimensional compartments
---------------------------------------------------

| :download:`Arrow schema (JSON) <_static/arrows/L2V5.7-11.json>`
| :download:`Model (XML.zip) <_static/model/L2V5.7-11.xml.zip>`

**Arrows**

.. figure:: _static/arrows/L2V5.7-11.svg
    :align: center

**Neo4j**

.. figure:: _static/neo4j/L2V5.7-11.svg
    :align: center
