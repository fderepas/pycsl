# u72 helper (review rt80 O2-O5): a library-private `_h` (returns 1) used only inside `x`.


#@ ensures \result == 1
#@ assigns \nothing
def _h() -> int:
    return 1


#@ ensures \result == 1
#@ assigns \nothing
def x() -> int:
    return _h()
