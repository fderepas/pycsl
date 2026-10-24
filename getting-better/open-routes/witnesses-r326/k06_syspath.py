import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "alt"))
from sp19 import f
#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return f()

if __name__ == "__main__":
    assert g() == 2, g()
