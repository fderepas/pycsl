#@ ensures \result == 2
#@ assigns \nothing
def _h() -> int:
    return 2


#@ ensures \result == 2
#@ assigns \nothing
def y() -> int:
    return _h()
