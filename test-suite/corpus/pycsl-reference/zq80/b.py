# u66 control 10382 (review rt76 r5): a file in the namespace directory zq80/ that the module zq80.py
# shadows; CPython never imports it as `zq80.b` (zq80 is a module, not a package), so it cannot be loaded
# by its dotted name and its own corpus run is an emission only.
# pycsl-flags: --no-proof


#@ ensures \result == 2
#@ assigns \nothing
def one() -> int:
    return 2
