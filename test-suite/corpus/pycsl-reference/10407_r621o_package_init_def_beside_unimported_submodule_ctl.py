r"""Test 10407 -- run #9 u69, review rt78 o1, route #621 control (PASS). The package zs07's __init__ defines
`def b()` and the package directory also holds a submodule b.py that no module of the program imports.
`from zs07 import b` finds the attribute (the function) and never loads the submodule, so `cd <tree root>
&& python <this file>` prints "result 1". Base c115e0a5a PROVED it; u66 b95cb8767 REFUSED it (route #621
took the `def` for a rebinding of the submodule); the u69 narrowing admits one undecorated top-level `def`
when no reached module names a module `b` in an import or reads `<x>.b.<y>`.
"""
# pycsl-expected: PASS
from zs07 import b


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return b()


if __name__ == "__main__":
    print("result", g())
