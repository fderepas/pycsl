r"""Test 2880 — route #269 R1 (expected FAIL): `m` claims TERMINATION (no `\diverges`) and
calls `C().spin(k)`, a method honestly declared `#@ \diverges`. The FRESH-receiver call form
reaches Module 6's generic arm as a receiver-less `val spin_1`, which no `\diverges` rule saw,
so it stayed a terminating stub and `\result == 7` PROVED at 8b0bfbbd. CPython: `m(1)` never
returns. Every stub spelling of a `\diverges` callee now carries `diverges`, so Why3's
termination VC for `m` fails.
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
        C().spin(k)
        return 7

if __name__ == "__main__":
    import threading
    t = threading.Thread(target=C().m, args=(1,), daemon=True)
    t.start()
    t.join(1.0)
    print("does not terminate" if t.is_alive() else "returned")
