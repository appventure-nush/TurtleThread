# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'TurtleThread'
copyright = "2025, AppVenture (NUS High Computer Science Interest Group). Original by Marie Roald & Yngve Mardal Moe."
author = "AppVenture (NUS High Computer Science Interest Group)"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx_copybutton"
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
html_logo = "../logo/turtlethread_logo_notext.svg"
html_title = "<center>TurtleThread Documentation</center>"

html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#00A499",
        "color-brand-content": "#007870",
    },
    "dark_css_variables": {
        "color-brand-primary": "#00A4A1",
        "color-brand-content": "#00BAB7",
    },
}