Stitch Types
============

Running/Triple Stitch
---------------------

  The running stitch is the most basic stitch, stitching after a constant distance.
  The triple stitch is the same as a running stitch, except each stitch is stitched three times, resulting in a thicker
  and more secure thread.

  .. literalinclude:: eg_running.py
      :language: python
      :linenos:

  .. image:: ../../_static/figures/stitches/running.png

Jump Stitch
-----------

  The jump stitch will move the needle from one position to another.
  It is visualised as a grey 'X' at the starting point and a grey circle at the ending point.

  .. literalinclude:: eg_jump.py
      :language: python
      :linenos:

  .. image:: ../../_static/figures/stitches/jump.png

Zigzag Stitch
-------------

  The zigzag stitch creates a zigzag pattern. 

  .. literalinclude:: eg_zigzag.py
      :language: python
      :linenos:

  .. image:: ../../_static/figures/stitches/zigzag.png

  It can be used to add texture to the border of a shape.

  - Note that a stitch length of less than 3 units is not recommended, as it may cause the embroidery machine to jam.

Satin Stitch
------------

  The satin stitch creates a bulky, solid stitch.

  .. literalinclude:: eg_satin.py
      :language: python
      :linenos:

  .. image:: ../../_static/figures/stitches/satin.png

  It is used to form defined borders. Internally, it is just a zigzag stitch with a stitch length of ``0.3mm`` (3 units).

  - Note that satin stitches are very dense, hence they take a long time to be embroidered. 
  - It is also recommended not to overlap satin stitches as it may cause the embroidery machine to jam.

Cross Stitch
------------

  The cross stitch leaves a stitch pattern with a cross pattern.

  .. literalinclude:: eg_cross.py
      :language: python
      :linenos:

  .. image:: ../../_static/figures/stitches/cross.png

  - Note that this is not a 'traditional' or 'hand-embroidered' cross stitch, but a modified variant as embroidery machines
    are unable to replicate that form of cross stitch.

Z Stitch
--------

  The Z stitch creates a Z-shaped pattern, similar to a zigzag stitch.

  .. literalinclude:: eg_z.py
      :language: python
      :linenos:

  .. image:: ../../_static/figures/stitches/z.png
