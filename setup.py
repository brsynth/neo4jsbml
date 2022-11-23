import glob

import setuptools
import yaml

# Version
version = ""
fversion = glob.glob("**/_version.py", recursive=True)[0]
with open(fversion) as fid:
    lines = fid.read().splitlines()
    version = lines[1].split("=")[-1].strip().replace('"', "")

# App name - dependencies
env = {}
with open("environment.yml") as fid:
    env = yaml.safe_load(fid)
name = env["name"]
install_requires = []
for package in env["dependencies"]:
    if isinstance(package, dict):
        package = package.get("pip", [])
        install_requires += package
    else:
        install_requires.append(package)
description = "Load SBML file into a Neo4j database"

setuptools.setup(
    name=name,
    version=version,
    author=[""],
    author_email=[""],
    description=description,
    long_description_content_type="text/markdown",
    url="https://forgemia.inra.fr/cati-sysmics/wp3/neo4jsbml",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=install_requires,
)
