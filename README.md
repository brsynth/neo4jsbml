# Neo4jSbml

[![Github Version](https://img.shields.io/github/v/release/brsynth/neo4jsbml?display_name=tag&sort=semver)](version)  
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)  
[![GitHub Super-Linter](https://github.com/brsynth/brsynth/workflows/Tests/badge.svg)](https://github.com/marketplace/actions/super-linter) [![Coverage](https://img.shields.io/coveralls/github/brsynth/neo4jsbml)](coveralls)  

## Install

```sh
git clone git@github.com:brsynth/neo4jsbml.git
cd neo4jsbml
conda env create -n neo4jsbml -f recipes/workflow.yml
conda activate neo4jsbml
pip install --no-deps .
```

## Usage

```sh
python -m neo4jsbml \
    # Database parameters
    --input-protocol-str ["neo4j", "bolt"] \
    --input-url-str "localhost:7687" \
    --input-user-str "neo4j" \
    --input-password-file <file> \
    --input-database-str <file> \
    # Input file
    --input-file-sbml <file> \
    --input-id-str <id> \
    # Parameters
    --input-modelisation-str <modelisation>
```
