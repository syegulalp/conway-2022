A simple example of Conway's Game Of Life, using Pyglet for visualization and Cython for speed.

This version uses Cython's "pure Python" syntax, so it can be run both with and without Cython compilation. This demonstrates clearly the difference in speed between regular Python and Cython.

Install requirements before doing anything else. A venv is recommended. Use `python compile.py` to build the extension modules.

Change into the `src` directory and run `conway.py` to see the demo.

The numbers that pop up in the console during runtime are the average time taken by the program to compute a new generation of the playing field.