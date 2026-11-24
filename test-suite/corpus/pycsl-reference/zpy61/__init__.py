# u61 witnesses 10340 / 10343 (review rt74 V2D): a REGULAR package in the program's directory (the corpus
# directory, sys.path[0]) without a `b` submodule. CPython stops here for every `zpy61.*` import and
# searches `zpy61.b` only in this package's `__path__`, which this file redirects to ../zpy61_alt.
import os
__path__ = [os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "zpy61_alt")]
