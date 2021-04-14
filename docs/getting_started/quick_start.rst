Quick Start
===========

Instantiate a basic instance of RIPEstat:

.. code-block:: python

  import rsaw

  ripe = rsaw.RIPEstat()

``sourceapp``
-------------

You can specify the ``sourceapp`` parameter to add a unique identifier to every
call. See the
`RIPE Stat Data API Documentation <https://stat.ripe.net/docs/data_api#Overview>`_ 
for details.

.. code-block:: python

  ripe = rsaw.RIPEstat(sourceapp='YourId')

``data_overload_limit``
-----------------------

As documented in the RIPE Data API documentation, the data overload prevention
is to protect users from getting more data than they can handle. It should only
be applicable to browser connections, however it can be specified here to explicitly
disable.

.. code-block:: python

  ripe = rsaw.RIPEstat(data_overload_limit='ignore')
  
Usage examples
--------------

With the ``ripe`` instance you can interact with the RIPEstat API:

.. code-block:: python

  # Find all announced prefixes for a Autonomous System
  prefixes = ripe.announced_prefixes(3333)

  for network in prefixes:
      print(network.prefix, network.timelines)

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

See the API section for details and examples on each data call.
