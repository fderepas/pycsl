# u71 witness 10435 helper: a dependency whose wildcard import of zp35 loads zp35/b.py.
from zp35 import *


#@ ensures \result == 3
#@ assigns \nothing
def three() -> int:
    return 3
