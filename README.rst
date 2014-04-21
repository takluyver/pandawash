Magic commands to clean up pandas series

This IPython extension makes it easy to clean up data in a pandas DataFrame,
while preserving a clear record of what you've done. It inserts template code
into your notebook, which you can quickly modify to clean up data.

Installation::

    %install_ext https://github.com/takluyver/pandawash/raw/master/pandawash.py

Use::

    %load_ext pandawash

    %groupcol df['colname']
    %numcol df['colname'] numtype
    %boundscheckcol df['colname'] min-max
    %regexcol df['colname'] pattern

See the `Demo notebook <http://nbviewer.ipython.org/github/takluyver/pandawash/blob/master/Pandawash%20Demo.ipynb>`_ for examples.
