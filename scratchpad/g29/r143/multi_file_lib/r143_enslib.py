"""G29 route #143 helper — an ENSURES clause reading this module's constant."""
BASE = -1


#@ ensures \result == BASE
#@ assigns \nothing
def base() -> int:
    return BASE
