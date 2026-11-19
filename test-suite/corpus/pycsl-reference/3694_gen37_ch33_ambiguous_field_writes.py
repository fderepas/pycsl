r"""Test 3694 -- gen #37 ch33 (expected PASS): a sibling call `self.bump()` whose callee assigns an AMBIGUOUS field `self.i` (also a field of Q, label `p_i`): the caller-side abstract op printed `writes { self.i }` (raw name, unbound). Now `writes { self.p_i }`; the two calls' effects compose. Honest claim (+2) must PROVE.
"""
class P:
    def __init__(self) -> None:
        self.i: int = 0

    #@ ensures self.i == \old(self.i) + 1
    #@ assigns self.i
    def bump(self) -> None:
        self.i = self.i + 1

    #@ ensures self.i == \old(self.i) + 2
    #@ assigns self.i
    def bump2(self) -> None:
        self.bump()
        self.bump()


class Q:
    def __init__(self) -> None:
        self.i: int = 5
