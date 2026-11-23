# u71 witness 10437 helper: a dependency with a wildcard import of zp37.
from zp37 import *


#@ ensures \result == 3
#@ assigns \nothing
def three() -> int:
    return 3
