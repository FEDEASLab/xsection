# Configuration file for the Sphinx documentation builder.
#
# https://www.sphinx-doc.org/en/master/usage/configuration.html
#
from pathlib import Path
project = 'xsection'
copyright = '2025'
author = 'Claudio Perez'
description = "Analysis of structural cross sections."
version = '0.0.0'
release = '0.0.0'

# General configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    # 'autoapi.extension',
    "myst_nb",
    'sphinx_tabs.tabs',
    'sphinx_copybutton',
    'sphinx.ext.mathjax',
    'sphinx.ext.githubpages',
    'sphinx_sitemap'
]
nb_execution_mode = "off"
myst_enable_extensions = [
    "dollarmath",
    "attrs_inline"
]

# autoapi_dirs = ['../src/mdof']


templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

source_suffix = '.rst'
root_doc = 'index'
language = 'en'

# -- Options for HTML output -------------------------------------------------
html_extra_path = ["robots.txt"]
html_baseurl = "https://peer-open-source.github.io/xsection/" #"https://xsection.io/"
html_title = project
html_theme = "pydata_sphinx_theme"
html_static_path = ['_static']
html_favicon = './_static/images/favicon.ico'
html_css_files = [
    'css/home-css/'+str(file.name) for file in (Path(__file__).parents[0]/"_static/css/home-css/").glob("vars*.css")
] + [
     'css/css/'+str(file.name) for file in (Path(__file__).parents[0]/"_static/css/css/").glob("*.css")
] + [
    "css/veux.css",
]

sitemap_url_scheme = "{link}"
sitemap_excludes = [
    f"{html_baseurl}index.html"
]
html_additional_pages = {'index': 'home.html'}
html_context = {
    "description": description,
    "introduction": "xsection is a Python library for analyzing structural cross sections.",
    "examples": [
    ],
    "features": [
        # {"title": "Free", "body": "All source code contributed to xsection is licensed under a <em>pure</em> BSD."},
        # {"title": "Accurate", "body": "."},
        # {"title": "Integrated", "body": 'xsection is designed to integrate with state-of-the-art open-source software like <a href="https://xara.so">xara</a>.'},
    ],
    "home_image": "_static/images/home.png",
    "cannonical_home": "https://xsection.io",
    **globals()
}
html_show_sphinx = False
html_show_sourcelink = False
html_theme_options = {
    "show_toc_level": 3,
    "github_url": f"https://github.com/fedeaslab/{project}",
#   "footer_items": [], #["copyright", "sphinx-version"],
    "logo": {
        #   "text": "xsection",
        "alt_text": "xsection Documentation - Home",
        "image_light": "_static/images/xsection.png",
        "image_dark":  "_static/images/xsection.png",
    }
}

autodoc_member_order = 'bysource'


html_static_path = ["_static"]

g = f"{html_baseurl}examples"# "https://gallery.stairlab.io"
def _add_examples(app, pagename, templatename, context, doctree):
    if templatename == "home.html":
        context["home_image"] = "_static/images/girder-light.png"
        context["examples"] = [
            {"title": "Basic Shapes",  "link": f"{g}/introduction.html",      "image": "../_static/images/gallery/W14x211.png", "description": "Material and section constants."},
            {"title": "Transforms",    "link": f"{g}/transformations.html",     "image": "../_static/images/gallery/transform.png", "description": "Transform shapes."},
            {"title": "Composites",   "link": f"{g}/composite.html",    "image": "../_static/images/gallery/concrete.png", "description": "."},
        ]

def _add_css(app, pagename, templatename, context, doctree):
    if pagename == "dontaddonthispage":
        return

    app.add_css_file("xsection.css")

def setup(app):
    app.connect("html-page-context", _add_css)
    app.connect("html-page-context", _add_examples)



mathjax3_config = {
  "loader": {"load": ['[tex]/color']},
  "tex": {
      "packages": {'[+]': ['color']},
      "inlineMath": [['$', '$'], ['\\(', '\\)']]
  }
}
