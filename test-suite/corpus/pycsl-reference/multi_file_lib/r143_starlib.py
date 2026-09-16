"""G29 route #143 helper — the callee reads a constant this module obtains by WILDCARD import."""
from multi_file_lib.r143_consts import *


#@ raises ValueError when LIM < 0
#@ assigns \nothing
def f3(k: int) -> int:
    if LIM < 0:
        raise ValueError
    return k
