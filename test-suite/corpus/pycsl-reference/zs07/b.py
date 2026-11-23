# u69 witness 10407 (review rt78 o1): a submodule nothing imports; CPython never loads it for
# `from zs07 import b` (the attribute lookup succeeds first).


#@ ensures \result == 2
#@ assigns \nothing
def one() -> int:
    return 2
