import sys
from datetime import datetime

# Use local PRSW over any global package
sys.path.insert(0, ".")
sys.path.insert(1, "..")

from prsw import __version__

project = "PRSW"
copyright = datetime.today().strftime("%Y, Jonathan P. Voss")
author = "Jonathan P. Voss"
release = __version__
version = ".".join(__version__.split(".", 3)[:3])

exclude_patterns = []

html_theme = "sphinx_rtd_theme"
html_theme_options = {"collapse_navigation": True}

extensions = ["sphinx.ext.autodoc", "sphinx.ext.intersphinx"]


def skip_member(app, what, name, obj, skip, options):
    if name in {
        "__getitem__",
        "__init__",
        "__iter__",
        "__len__",
    }:
        return False
    return skip


def setup(app):
    app.connect("autodoc-skip-member", skip_member)
