r"""Test 7045 -- route #459 (expected PASS): CONTROL -- `G` unconditional, `H` in both arms of `if TYPE_CHECKING`, `K` in the try body and its handler; PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import TYPE_CHECKING
G = 1
if TYPE_CHECKING:
    H = 2
else:
    H = 3
try:
    K = 4
except Exception:
    K = 5
#@ no_exception \all
def f(n: int) -> int:
    return G + H + K + n
if __name__ == "__main__":
    print(f(1))
