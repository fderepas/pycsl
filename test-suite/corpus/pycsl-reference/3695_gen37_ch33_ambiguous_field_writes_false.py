r"""Test 3695 -- gen #37 ch33 (expected FAIL): false twin of 3694: claiming `self.i == \old(self.i) + 1` after TWO bumps must NOT prove (the frame is real, not dropped).
"""
# pycsl-expected: FAIL
class P:
    def __init__(self) -> None:
        self.i: int = 0

    #@ ensures self.i == \old(self.i) + 1
    #@ assigns self.i
    def bump(self) -> None:
        self.i = self.i + 1

    #@ ensures self.i == \old(self.i) + 1
    #@ assigns self.i
    def bump2(self) -> None:
        self.bump()
        self.bump()


class Q:
    def __init__(self) -> None:
        self.i: int = 5
