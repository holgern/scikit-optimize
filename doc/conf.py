#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

import os
import re

# import pkg_resources
import sys

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
import warnings

from packaging.version import parse

import skopt

sys.path.insert(0, os.path.abspath('sphinxext'))
import sphinx_gallery  # noqa: E402
from github_link import make_linkcode_resolve  # noqa: E402
from importlib.metadata import version, PackageNotFoundError  # noqa: E402

#  __version__ = pkg_resources.get_distribution('skopt').version
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

# -- Project information -----------------------------------------------------

project = 'scikit-optimize'
copyright = '2017 - 2024, scikit-optimize contributors (BSD License)'
author = 'The scikit-optimize contributors'

# The short X.Y version
try:
    _version = version("skopt")
except PackageNotFoundError:
    _version = version("scikit-optimize")
version = parse(_version).base_version
version = ".".join(version.split(".")[:2])
# The full version, including alpha/beta/rc tags
release = _version

# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'numpydoc',
    'sphinx.ext.linkcode',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.imgconverter',
    'sphinx_gallery.gen_gallery',
    'sphinx_issues',
    'sphinx.ext.mathjax',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
]

numpydoc_class_members_toctree = False

# For maths, use mathjax by default and svg if NO_MATHJAX env variable is set
# (useful for viewing the doc offline)
if os.environ.get('NO_MATHJAX'):
    extensions.append('sphinx.ext.imgmath')
    imgmath_image_format = 'svg'
    mathjax_path = ''
else:
    extensions.append('sphinx.ext.mathjax')
    mathjax_path = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/' 'tex-chtml.js'

autodoc_default_options = {'members': True, 'inherited-members': True}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['templates']

# generate autosummary even if no references
autosummary_generate = True

# The suffix of source filenames.
source_suffix = '.rst'


# The master toctree document.
master_doc = 'contents'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns = ['_build', 'templates', 'includes', 'themes']

default_role = 'literal'

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

html_theme = 'sphinx_book_theme'


# html_theme_options = {'google_analytics': False,
#                      'mathjax_path': mathjax_path}

# Add any paths that contain custom themes here, relative to this directory.
html_theme_path = ['themes']

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}
html_short_title = 'scikit-optimize'

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = 'image/logo.png'

html_favicon = 'image/favicon.ico'

# Additional templates that should be rendered to pages, maps page names to
# template names.
html_additional_pages = {
    'index': 'index.html',
    'documentation': 'documentation.html',
}  # redirects to index

# If false, no module index is generated.
html_domain_indices = False

# If false, no index is generated.
html_use_index = False

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}

# Add any paths that contain custom themes here, relative to this directory.
html_theme_path = ['themes']


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'scikit-optimizedoc'
html_copy_source = True

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
    'preamble': r"""
    \usepackage{amsmath}\usepackage{amsfonts}\usepackage{bm}
    \usepackage{morefloats}\usepackage{enumitem} \setlistdepth{10}
    """
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        'scikit-optimize.tex',
        'scikit-optimize Documentation',
        'The scikit-optimize Contributors.',
        'manual',
    ),
]


# If false, no module index is generated.
latex_domain_indices = False

trim_doctests_flags = True

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'scikit-optimize', 'scikit-optimize Documentation', [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        'scikit-optimize',
        'scikit-optimize Documentation',
        author,
        'scikit-optimize',
        'One line description of project.',
        'Miscellaneous',
    ),
]

# intersphinx configuration
intersphinx_mapping = {
    'python': (f'https://docs.python.org/{sys.version_info.major}', None),
    'numpy': ('https://docs.scipy.org/doc/numpy/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/reference', None),
    'matplotlib': ('https://matplotlib.org/', None),
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable/', None),
    'joblib': ('https://joblib.readthedocs.io/en/latest/', None),
    'sklearn': ('https://scikit-learn.org/stable/', None),
}


binder_branch = 'master'


class SubSectionTitleOrder:
    """Sort example gallery by title of subsection.

    Assumes README.txt exists for all subsections and uses the
    subsection with dashes, '---', as the adornment.
    """

    def __init__(self, src_dir):
        self.src_dir = src_dir
        self.regex = re.compile(r"^([\w ]+)\n-", re.MULTILINE)

    def __repr__(self):
        return f'<{self.__class__.__name__}>'

    def __call__(self, directory):
        src_path = os.path.normpath(os.path.join(self.src_dir, directory))
        readme = os.path.join(src_path, "README.txt")

        try:
            with open(readme) as f:
                content = f.read()
        except FileNotFoundError:
            return directory

        title_match = self.regex.search(content)
        if title_match is not None:
            return title_match.group(1)
        return directory


sphinx_gallery_conf = {
    'doc_module': 'skopt',
    'backreferences_dir': os.path.join('modules', 'generated'),
    'show_memory': False,
    'reference_url': {'skopt': None},
    'examples_dirs': ['../examples'],
    'gallery_dirs': ['auto_examples'],
    'default_thumb_file': 'image/logo.png',
    'subsection_order': SubSectionTitleOrder('../examples'),
    'filename_pattern': '',
    'ignore_pattern': 'utils.py',
    'binder': {
        'org': 'holgern',
        'repo': 'scikit-optimize',
        'binderhub_url': 'https://mybinder.org',
        'branch': binder_branch,
        'dependencies': './binder/requirements.txt',
        'use_jupyter_lab': True,
    },
    # avoid generating too many cross links
    'inspect_global_variables': False,
}


# The following dictionary contains the information used to create the
# thumbnails for the front page of the scikit-learn home page.
# key: first image in set
# values: (number of plot in set, height of thumbnail)
carousel_thumbs = {
    'sphx_glr_sklearn-gridsearchcv-replacement_001.png': 600,
    'sphx_glr_plot_ask-and-tell_002.png': 600,
    'sphx_glr_bayesian-optimization_004.png': 600,
    'sphx_glr_strategy-comparison_002.png': 600,
    'sphx_glr_visualizing-results_008.png': 600,
}


# enable experimental module so that experimental estimators can be
# discovered properly by sphinx


def make_carousel_thumbs(app, exception):
    """Produces the final resized carousel images."""
    if exception is not None:
        return
    print('Preparing carousel images')

    image_dir = os.path.join(app.builder.outdir, '_images')
    for glr_plot, max_width in carousel_thumbs.items():
        image = os.path.join(image_dir, glr_plot)
        if os.path.exists(image):
            c_thumb = os.path.join(image_dir, glr_plot[:-4] + '_carousel.png')
            sphinx_gallery.gen_rst.scale_image(image, c_thumb, max_width, 190)


def filter_search_index(app, exception):
    if exception is not None:
        return

    # searchindex only exist when generating html
    if app.builder.name != 'html':
        return

    print('Removing methods from search index')

    searchindex_path = os.path.join(app.builder.outdir, 'searchindex.js')
    with open(searchindex_path) as f:
        searchindex_text = f.read()

    searchindex_text = re.sub(r'{__init__.+?}', '{}', searchindex_text)
    searchindex_text = re.sub(r'{__call__.+?}', '{}', searchindex_text)

    with open(searchindex_path, 'w') as f:
        f.write(searchindex_text)


# Config for sphinx_issues

# we use the issues path for PRs since the issues URL will forward
issues_github_path = 'holgern/scikit-optimize'


def setup(app):
    # to hide/show the prompt in code examples:
    app.connect('build-finished', make_carousel_thumbs)
    app.connect('build-finished', filter_search_index)


# The following is used by sphinx.ext.linkcode to provide links to github
linkcode_resolve = make_linkcode_resolve(
    'skopt',
    'https://github.com/holgern/'
    'scikit-optimize/blob/{revision}/'
    '{package}/{path}#L{lineno}',
)

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message='Matplotlib is currently using agg, which is a'
    ' non-GUI backend, so cannot show the figure.',
)

# Reduces the output of estimators
# sklearn.set_config(print_changed_only=True)


# -- Extension configuration -------------------------------------------------
link_github = True

linkcheck_ignore = [
    r'(../)?auto_examples/',
]
