# neo4j-sbml

## Getting started
Enumerate pathway with efmtools (10.1093/bioinformatics/btn401).
Compute Elementaray Flux Modes (EFMs) on the whole stoichiometry matrix, then retain reaction containing `includeNodes`.
This parameter filter nodes based on the value of the `id` property.
The schema needs to respect this following:
```sh
(s1:Species)-[HAS_SUBSTRATE]-(r:Reaction)-[HAS_PRODUCT]-(s2:Species)
```
The property `stoichiometry` embedded by `Species` is used to set the stoichiometry of the reaction (default: `"1"`).
The property `reversible` embedded by `Reaction` is also used (default: `false`)

The procedure adds a new property on the nodes `Species`, `Reaction` with the name defined by the argument `labelPathwayPrefix` with a value of a list of integers indidicated which nodes are implied in the pathway ID.

Note: this plugin is used in a Desktop Neo4j instance.

### Install
Download JAR file from Release, then copy the JAR file into the `plugin` directory of a Neo4j instance.

### Run


In Neo4j browser:
```sh
CALL brsynth.enumeratePathway('includeNodes=List[str], labelPathwayPrefix=str')
```

## Built with these main libraries

*Alphabetic order*
* [efmtool](https://csb.ethz.ch/tools/software/efmtool.html) - Compute Elementary Flux Modes
* [neo4j](https://github.com/neo4j/neo4j) - Graphs for Everyone
* [neo4j-apoc](https://github.com/neo4j-contrib/neo4j-apoc-procedures) - Procedures on Cypher Neo4j