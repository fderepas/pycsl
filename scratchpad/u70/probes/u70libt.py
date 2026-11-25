#@ ensures \result == 1
#@ assigns \nothing
def _h() -> int:
    return 1


#@ ensures \result == _h()
#@ assigns \nothing
def f() -> int:
    return _h()
