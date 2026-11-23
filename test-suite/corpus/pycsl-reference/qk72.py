# u72 helper (review rt80 O4 / O5): another library-private `_h` (returns 2) used only inside `y`.


#@ ensures \result == 2
#@ assigns \nothing
def _h() -> int:
    return 2


#@ ensures \result == 2
#@ assigns \nothing
def y() -> int:
    return _h()
