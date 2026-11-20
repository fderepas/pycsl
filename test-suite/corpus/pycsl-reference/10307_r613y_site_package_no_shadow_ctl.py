r"""Test 10307 -- run #8 u58, review rt69 G6 (PASS control). The program imports the installed `lark`, and no
resolution root holds a module named like anything lark (or any installed package) imports. Emitted.
"""
# pycsl-expected: PASS
import lark


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return len("abc")


if __name__ == "__main__":
    print("result", f())
