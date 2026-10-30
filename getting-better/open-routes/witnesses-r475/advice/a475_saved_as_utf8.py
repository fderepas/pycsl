r"""Advice probe for route #475 ('save the module as UTF-8 and drop (or correct) its coding cookie'), from test 7461 -- a `latin-1` dependency holding the bytes C3 A9 in a string; the helper re-saved as UTF-8 with a `utf-8` cookie (x3_ha475.py).
"""
# pycsl-expected: PASS
from x3_ha475 import S


#@ ensures \result == 1
def f(n: int) -> int:
    return len(S)


if __name__ == "__main__":
    r = f(1)
    print("result", r)
