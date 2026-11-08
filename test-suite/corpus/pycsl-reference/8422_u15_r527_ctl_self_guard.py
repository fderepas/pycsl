r"""Test 8422 -- route #527 (control, expected PASS): `if self.s is not None: w = self.s + "x"` on an `Optional[str]` self field; CPython returns 0
"""
# pycsl-expected: PASS
from typing import Optional


class K:
    def __init__(self) -> None:
        self.s: Optional[str] = None

    #@ no_exception \all
    def m(self) -> int:
        if self.s is not None:
            w = self.s + "x"
            return 1
        return 0


if __name__ == "__main__":
    print("result", K().m())
