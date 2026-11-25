r"""Test 10475 -- run #9 u73, route #631 control (PASS). The program derives a class from an imported CLASS
(`class C(zu73n.Base)`); the class base now counts as a module-object escape (every store receiver judged),
but no reached module has a module-level hook and no store names a submodule, so `cd <tree root> && python
<this file>` prints "result 1" and pycsl proves it.
"""
# pycsl-expected: PASS
import zu73n.b


class C(zu73n.Base):
    pass


#@ ensures \result == 1
def g() -> int:
    return zu73n.b.one()


if __name__ == "__main__":
    print("result", g())
