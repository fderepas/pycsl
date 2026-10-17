r"""Test 2775 — route #263 (expected FAIL): `m` claims TERMINATION (no `\diverges`) and calls
`spin`, a method honestly declared `#@ \diverges` whose loop never ends for `k > 0`. The stub
`self_spin_1` was a plain — terminating — `val`, so `m`'s termination came for free: PROVED
`\result == 7` at 283d1033. CPython: `m(1)` never returns. The stub of a `\diverges` method
now carries `diverges`, so Why3's termination VC for `m` fails.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 0
    #@ assigns \nothing
    #@ \diverges
    def spin(self, k: int) -> int:
        while k > 0:
            k = k + 1
        return 0

    #@ ensures \result == 7
    #@ assigns \nothing
    def m(self, k: int) -> int:
        self.spin(k)
        return 7

if __name__ == "__main__":
    import threading
    t = threading.Thread(target=C().m, args=(1,), daemon=True)
    t.start()
    t.join(1.0)
    print("does not terminate" if t.is_alive() else "returned")
