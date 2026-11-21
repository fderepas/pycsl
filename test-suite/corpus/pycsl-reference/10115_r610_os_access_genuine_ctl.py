r"""Test 10115 -- route #610 CONTROL (expected PASS): a GENUINE `os.access` (the module name bound nowhere else) keeps lvU's law-free model: only what holds for every answer is proved.
"""
# pycsl-expected: PASS
import os


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def f(p: str) -> int:
    if os.access(p, 4):
        return 1
    return 0


if __name__ == "__main__":
    print("result", f("."))
