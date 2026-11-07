r"""Test 2774 — route #263 (expected FAIL): an AVAILABILITY policy (`#@ happy ... total`) on a
`parse` whose only callee is itself. Route #206 rejects a total target that reaches a
bodyless/`\diverges` callee, not one that recurses through its own stub: PROVED at 283d1033.
CPython: RecursionError. Now refused by the method-recursion rule (and marking `parse`
`\diverges` is rejected by route #93).
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ happy availability:
#@     targets parse
#@     total
class Parser:
    def __init__(self) -> None:
        self.k: int = 0

    #@ ensures \result >= 0
    #@ assigns \nothing
    def parse(self, n: int) -> int:
        return self.parse(n)

if __name__ == "__main__":
    import sys; sys.setrecursionlimit(100)
    try:
        print(Parser().parse(1))
    except RecursionError:
        print("RecursionError")
