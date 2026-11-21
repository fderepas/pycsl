r"""Test 9228 -- route #575 CONTROL (expected PASS at base and HEAD): names bound once to REAL containers / strs and
searched are admitted: a module tuple alias `TUP_A = (1, 2)`, a module str `STR_AB = "ab"` and a module alias
`SEP = os.sep` searched for a str needle.
"""
# pycsl-expected: PASS
import os

TUP_A = (1, 2)
STR_AB = "ab"
SEP = os.sep


#@ no_exception \all
def f1(k: int) -> int:
    return 1 if k in TUP_A else 0


#@ no_exception \all
def f3(s: str) -> int:
    return 1 if s in STR_AB else 0


#@ no_exception \all
def f4(s: str) -> int:
    return 1 if s in SEP else 0


if __name__ == "__main__":
    print(f1(1), f3("a"), f4("/"))
