"""prsw setup.py"""

import re
from os import path

from setuptools import find_packages, setup

PACKAGE_NAME = "prsw"
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
    "test": ["pytest >= 2.7.3"],
}
extras["dev"] += extras["lint"] + extras["test"]

setup(
    name=PACKAGE_NAME,
    author="Jonathan P. Voss",
    author_email="jvoss@onvox.net",
    python_requires="~=3.7",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Utilities",
    ],
    description=(
        "PRSW, the Python RIPE Stat Wrapper, is a python package that"
        " simplifies access to the RIPE Stat public data API."
    ),
    extras_require=extras,
    install_requires=["requests >=2"],
    keywords="RIPE RIPEStat api wrapper",
    license="Simplified BSD License",
    long_description=README,
    packages=find_packages(exclude=["tests", "tests.*", "tools", "tools.*"]),
    project_urls={
        "Documentation": "https://prsw.readthedocs.io/",
        "Issue Tracker": "https://github.com/jvoss/prsw/issues",
        "Source Code": "https://github.com/jvoss/prsw",
    },
    version=VERSION,
)
