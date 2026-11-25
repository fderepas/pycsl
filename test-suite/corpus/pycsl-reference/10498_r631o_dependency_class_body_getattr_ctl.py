r"""Test 10498 -- run #9 u75, review rt83 o6 (u73 INTRODUCED over-refusal, PASS). A reached dependency binds
`__getattr__` in a CLASS body (`class P: __getattr__ = _fwd`, a proxy idiom): a class attribute, no module
hook; `cd <tree root> && python <this file>` prints "result 4" and pycsl proves it (u73 refused it with
PYCSL-SEM-IMPORT-MODULE-HOOK).
"""
# pycsl-expected: PASS
import zu75i.b
from zu75i_proxy import three


#@ ensures \result == 4
def g() -> int:
    return zu75i.b.one() + three()


if __name__ == "__main__":
    print("result", g())
