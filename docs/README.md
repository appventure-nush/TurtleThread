# Building Documentation for TurtleThread

This is the refreshed documentation for TurtleThread, which was built up from scratch with some reference to the
original documentation.  

We use Sphinx as the documentation engine.

## How do I build documentation?

On Linux/Unix, go to the `docs/` directory and use the command:  

```make html```  

The resultant HTML documentation should be in the `_build/html/` directory.

On Windows, use `make.bat` instead.

## How do I add documentation? 

Sphinx uses ReStructuredText (RST) instead of Markdown (which is probably more common?) due to its extensibility and
compatability with Python. As it is the default, we use it in this project.  

To add pages, go to the `source/` directory and find a suitable place to place your new page.  

A few key pointers:
- Remember to put the new page in under the `toctree` directive in `index.rst` (in this directory) or people won't be
able to access your page!
- Important directives you should know are `literalinclude` and `image`, see the existing pages on how to use them...
- If your pages (especially the table of contents) doesn't look up to date after `make html`, use the `make clean`
command or just delete the `_build/` directory. Sphinx caches old pages when possible to reduce build times.