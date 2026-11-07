r"""Test 1397 — ROUTES #136/#137 positive control: a BARE dynamic `exec` inside a function (its assignments land in the discarded locals snapshot, so tests 0638/0639/0644 keep demonstrating the `\in_scope` havoc and the frame taint), a CONSTANT `eval` with no walrus, and a module-scope field store on a genuinely fresh module-class instance all still prove.
"""
# pycsl-expected: PASS
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n: int = 0


g = C()
g.n = 5


#@ ensures \result == 0
#@ assigns \nothing
def f(code: str) -> int:
    exec(code)
    return 0


#@ ensures \result == 0
#@ assigns \nothing
def h() -> int:
    if eval("2 + 3") == 5:
        return 0
    return 0
