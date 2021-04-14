"""rsaw setup.py"""

import re
from os import path

from setuptools import setup

PACKAGE_NAME = "rsaw"
PATH = path.abspath(path.dirname(__file__))
with open(path.join(PATH, "README.rst"), encoding="utf-8") as fp:
    README = fp.read()
with open(path.join(PATH, PACKAGE_NAME, "__init__.py"), encoding="utf-8") as fp:
    VERSION = re.search('__version__ = "([^"]+)"', fp.read()).group(1)

extras = {
    "dev": ["packaging", "pre-commit"],
    "lint": [
        "black",
        "flake8",
        "pydocstyle",
        "sphinx",
        "sphinx_rtd_theme",
    ],
    "readthedocs": ["sphinx"],
}
# extras["dev"] += extras["lint"] + extras["test"]

setup(
    name=PACKAGE_NAME,
    author="Jonathan P. Voss",
    author_email="jonathan@expbits.io",
    python_requires="~=3.6",
    description=(
        "RSAW, the `RIPE Stat API Wrapper`, is a python package that"
        " simplifies access to the RIPE Stat public data API."
    ),
    extras_require=extras,
    install_requires=["requests >=2"],
    keywords="RIPE RIPEStat api wrapper",
    license="Simplified BSD License",
    long_description=README,
    project_urls={
        "Documentation": "https://rsaw.readthedocs.io/",
        "Issue Tracker": "https://github.com/jvoss/rsaw/issues",
        "Source Code": "https://github.com/jvoss/rsaw",
    },
    version=VERSION,
)
