PRSW: Python RIPE Stat Wrapper
==============================

.. image:: https://img.shields.io/pypi/v/prsw.svg
    :alt: Latest Version
    :target: https://pypi.python.org/pypi/prsw

.. image:: https://img.shields.io/pypi/pyversions/prsw
    :alt: Supported Python Versions
    :target: https://pypi.python.org/pypi/prsw

.. image:: https://github.com/jvoss/prsw/actions/workflows/tests.yml/badge.svg
  :alt: GitHub Actions Tests
  :target: https://github.com/jvoss/prsw/actions/workflows/tests.yml

.. image:: https://coveralls.io/repos/github/jvoss/prsw/badge.svg?branch=master
  :alt: Coveralls
  :target: https://coveralls.io/github/jvoss/prsw?branch=master

.. image:: https://readthedocs.org/projects/prsw/badge/?version=latest
  :target: https://prsw.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

PRSW, the RIPE Stat Wrapper, is a Python package that allows for simple access to 
the `RIPEstat Data API <https://stat.ripe.net/docs/data_api>`_. 

Installation
------------

PRSW is supported on Python 3.7+ and can be installed via 
`pip <https://pypi.python.org/pypi/pip>`_.

.. code-block:: bash

  pip install prsw

To install the latest development version run the following instead:

.. code-block:: bash

  pip install --upgrade https://github.com/jvoss/prsw/archive/master.zip

Quickstart
----------

RIPEstat can be instantiated with a few options. For details see the
documentation at `<https://prsw.readthedocs.io>`_.

To instantiate a basic instance of RIPEstat:

.. code-block:: python

  import prsw

  ripe = prsw.RIPEstat()

With the `ripe` instance you can interact with the RIPEstat API:

.. code-block:: python

  # Find all announced prefixes for a Autonomous System
  prefixes = ripe.announced_prefixes(3333)

  # Interact with the looking glass
  for collector in ripe.looking_glass('140.78.0.0/16'):
    print(collector.location)

    for peer in collector.peers:
        print(
            peer.asn_origin,
            peer.as_path,
            peer.community,
            peer.last_update,
            peer.prefix,
            peer.peer,
            peer.origin,
            peer.next_hop,
            peer.latest_time
        )

  # Check RPKI validation status
  print(ripe.rpki_validation_status(3333, '193.0.0.0/21').status)

Please see the `documentation <https://prsw.readthedocs.io/>`_ for more options.

Contributing
------------

Contributions are encouraged. Please see `CONTRIBUTING <CONTRIBUTING.rst>`_ for details.

Acknowledgements
----------------

Inspiration for several elements of this project came from 
`PRAW <https://github.com/praw-dev/praw>`_, the Python Reddit API Wrapper.

License
-------

PRSW is licened under the `Simplified BSD License <LICENSE.txt>`_.
