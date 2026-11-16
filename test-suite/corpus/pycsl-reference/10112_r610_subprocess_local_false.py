r"""Test 10112 -- route #610 (rt61 M1, expected FAIL): a LOCAL named `subprocess`: `subprocess.run(..)` is the user method (an effect on `s.n`). The model of the module call
applies only when the head name is the module import, bound nowhere in the function and not
rebound at module level; here it is not, so the file is REFUSED
(`PYCSL-R610-EXT-MODULE-NAME-SHADOWED`) rather than lowered as the module call.
"""
# pycsl-expected: FAIL
import subprocess
from typing import List


class S:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns self.n
    def run(self, a: List[str], capture_output: bool, text: bool) -> int:
        self.n = self.n + 1
        return 0


#@ ensures \result == 0
def f(s: S) -> int:
    subprocess = s
    try:
        r = subprocess.run(["true"], capture_output=True, text=True)
    except OSError:
        return 0
    except ValueError:
        return 0
    except UnicodeDecodeError:
        return 0
    return s.n


if __name__ == "__main__":
    r = f(S())
    print("VIOLATION contract" if r != 0 else "result", r)
