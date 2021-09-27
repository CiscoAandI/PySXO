from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="PySXO",
    install_requires=[
        "requests >= 2.19.0",
        "attrdict >= 2.0.1"
    ]
)