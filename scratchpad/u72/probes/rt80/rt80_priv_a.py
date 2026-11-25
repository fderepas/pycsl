#@ ensures \result == 1
#@ assigns \nothing
def _h() -> int:
    return 1


#@ ensures \result == 1
#@ assigns \nothing
def x() -> int:
    return _h()
