Contributing
============

Dependencies
------------


Tests/Developement (pip)::

- tox
- coverage
- unittest2
- mock
- responses

Documentation (pip)::

- sphinx
- sphinxcontrib-napoleon
- sphinx_rtd_theme


Tests
-----

**Run** (from project root)::

`python setup.py test`

**Full Suite**::

  tox

This will run:

- Python2.7
- Python3.4
- py3kwarn
- pep8 (using flake8)
- build current docs

or::

  make test
  # and to clean up after

Clean up::
  make clean

Building PyOTRS package: ``python setup.py sdist`` (``make build`` )

Uploading package to pypi (requires credentials): ``python setup.py sdist bdist_wheel upload`` (``make upload``)

Releasing
---------

- Update CHANGELOG.rst
- Update pyotrs/version.py
- git add CHANGELOG.rst pyotrs/version.py
- git commit -m "bump to 0.x.y"
- git tag 0.x.y
- git push
- git push --tags
- python setup.py sdist bdist_wheel upload

Writing Documentation
---------------------

Google Docstring format for::

- Args: (includes **kwargs)
- Returns:
- Raises:
- Examples:

Sphinx Napoleon Docs::

    https://sphinxcontrib-napoleon.readthedocs.org/en/latest/
    https://sphinxcontrib-napoleon.readthedocs.org/en/latest/example_google.html#example-google

To including private method in the automatically generate Sphinx documentation add::

:private-members:


For a Spinx formatted "Note" or "Warning" use .rst Syntax:

- ``.. note::``
- ``.. warning::``

Some links::

    http://www.sphinx-doc.org/en/stable/markup/para.html
    http://www.sphinx-doc.org/en/stable/rest.html
    http://docutils.sourceforge.net/docs/user/rst/quickref.html#escaping
    https://gist.github.com/dupuy/1855764
