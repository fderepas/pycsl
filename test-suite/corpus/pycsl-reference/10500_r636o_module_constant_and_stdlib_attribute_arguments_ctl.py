r"""Test 10500 -- run #9 u75, route #636 control (PASS). The program passes a local module's literal constant
`zu75k.k.CONST` and the standard-library attributes `sys.argv` to `print` / `len`, and tests a submodule
in an `if` (an operator / test position): none of them hands a module object (or a local function / class)
out, so rule M does not refuse; `cd <tree root> && python <this file>` prints "result 1" and pycsl proves
it.
"""
# pycsl-expected: PASS
import sys
import zu75k.b
import zu75k.k


#@ ensures \result == 1
def g() -> int:
    return zu75k.b.one()


if __name__ == "__main__":
    print(zu75k.k.CONST, len(sys.argv) > 0)
    if zu75k.b is not None:
        print("result", g())
