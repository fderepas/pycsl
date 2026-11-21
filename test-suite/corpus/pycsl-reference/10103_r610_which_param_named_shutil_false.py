r"""Test 10103 -- route #610 (rt61 M1, expected FAIL): a PARAMETER named `shutil`: `shutil.which(cmd)` is the user method, whose effect the law-free world query drops. The model of the module call
applies only when the head name is the module import, bound nowhere in the function and not
rebound at module level; here it is not, so the file is REFUSED
(`PYCSL-R610-EXT-MODULE-NAME-SHADOWED`) rather than lowered as the module call.
"""
# pycsl-expected: FAIL
import shutil
from typing import Optional


class W:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns self.n
    def which(self, c: str) -> Optional[str]:
        self.n = self.n + 1
        return None


#@ ensures shutil.n == \old(shutil.n)
def where(shutil: W, cmd: str) -> Optional[str]:
    return shutil.which(cmd)


if __name__ == "__main__":
    w = W()
    where(w, "sh")
    print("VIOLATION contract" if w.n != 0 else "result", w.n)
