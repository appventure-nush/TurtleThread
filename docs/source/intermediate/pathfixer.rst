PathFixer
============


Using PathFixer
-------------------------
.. versionadded:: 0.3.0

This will automatically fix paths if there are many stitches that are too short. **This will usually mess up the pattern!** 
You should fix the pattern instead of using PathFixer when possible; patterns made properly. 

You can also set ``min_turtle_dist`` to some larger value to make the minimum stitch distance larger. This defaults to ``10.0``. 

If using normal ``LetterDrawer``, use a font size of at least ``120``. If using ``SimplexLetterDrawer``, use a scale of at least ``5.0``. 

Example usage: 

.. literalinclude:: text/eg_simplex.py
    :language: python
    :linenos:
    :emphasize-lines: 23, 24


.. if-builder:: html
  .. raw:: html

    <div style="display:flex; gap:40px; align-items:flex-start;">

      <div style="display: grid; text-align:center; gap: 10px; ">
        <div><strong>Before Fix</strong></div>
        <img src="../../_static/figures/pathfixer/before_fix.png" width="300"/>
      </div>

      <div style="display: grid; text-align:center; gap: 10px; ">
        <div><strong>After Fix</strong></div>
        <img src="../../_static/figures/pathfixer/after_fix.png" width="300"/>
      </div>

    </div>

.. if-builder:: simplepdf 
  
  **Before Fix**

   .. image:: ../../_static/figures/pathfixer/before_fix.png
      :width: 300px

   **After Fix**

   .. image:: ../../_static/figures/pathfixer/after_fix.png
      :width: 300px


