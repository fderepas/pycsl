# u71 witness 10436 helper: a dependency whose wildcard import of zp36.sub loads zp36/sub/b.py.
from zp36.sub import *


#@ ensures \result == 3
#@ assigns \nothing
def three() -> int:
    return 3
