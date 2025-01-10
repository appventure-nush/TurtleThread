#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# turtlethread documentation build configuration file, created by
# sphinx-quickstart on Fri Jun  9 13:47:02 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another
# directory, add these directories to sys.path here. If the directory is
# relative to the documentation root, use os.path.abspath to make it
# absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

import turtlethread
import turtlethread.turtle
import turtlethread.visualise

turtlethread.turtle.USE_SPHINX_GALLERY = True
turtlethread.visualise.USE_SPHINX_GALLERY = True

from turtlethread.sphinx_plugins.turtlethread_gallery_scraper import turtlethread_scraper

# -- General configuration ---------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

language = os.environ["TURTLETHREAD_DOC_LANGUAGE"]
# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "numpydoc",
#    "sphinx_gallery.gen_gallery",
    "sphinx_toolbox.collapse",
    "turtlethread.sphinx_plugins.manual_example_code_directive",
]

#sphinx_gallery_conf = {
#    "examples_dirs": os.path.join("../../../examples", language),  # path to your example scripts
#    "gallery_dirs": "auto_examples",  # path to where to save gallery generated output
#    "image_scrapers": (turtlethread_scraper),
#    "filename_pattern": "/gallery",
#    "reset_argv": lambda x, y: ["MOCK_TURTLE"],
#}
numpydoc_show_class_members = False
numpydoc_show_inherited_class_members = False
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates", "../../_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "TurtleThread"
copyright = "2021, Marie Roald & Yngve Mardal Moe"
author = "Marie Roald & Yngve Mardal Moe"

# The version info for the project you're documenting, acts as replacement
# for |version| and |release|, also used in various other places throughout
# the built documents.
#
# The short X.Y version.
# version = turtlethread.__version__
# The full version, including alpha/beta/rc tags.
# release = turtlethread.__version__

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output -------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_book_theme"

html_logo = "../logo/turtlethread_logo.svg"
html_favicon = "../logo/turtlethread_logo_notext.svg"
# Theme options are theme-specific and customize the look and feel of a
# theme further.  For a list of options available for each theme, see the
# documentation.
#

languages = ["nb_NO", "en"]
# other_languages = languages - {language}

html_context = {"current_language": language, "all_languages": languages}
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = ["css/custom.css", f"css/custom_{language}.css"]
html_js_files = ["javascript/print.js"]


if os.name == "nt":
    raise SystemError("Documentation cannot be built on Windows")
