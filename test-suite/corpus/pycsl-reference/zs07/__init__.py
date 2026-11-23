# u69 witness 10407 (review rt78 o1, route #621 narrowed): the package __init__ defines a function `b`
# beside a submodule b.py that nothing imports, so the attribute `zs07.b` stays this function.


#@ ensures \result == 1
#@ assigns \nothing
def b() -> int:
    return 1
