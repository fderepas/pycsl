r"""Test 2881 — route #269 R1 (expected FAIL): `C.m` claims TERMINATION and calls
`super().spin(k)`, where `B.spin` is declared `#@ \diverges`. The `super()` receiver form is
lowered by the generic arm to a receiver-less `val spin_1` with no `diverges`, so `\result
== 7` PROVED at 8b0bfbbd. CPython: `C().m(1)` never returns. The stub now carries
`diverges` and `m`'s termination VC fails.
"""
# pycsl-expected: FAIL
class B:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 0
    #@ assigns \nothing
    #@ \diverges
    def spin(self, k: int) -> int:
        while k > 0:
            k = k + 1
        return 0

class C(B):
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 7
    #@ assigns \nothing
    def m(self, k: int) -> int:
        super().spin(k)
        return 7

if __name__ == "__main__":
    import threading
    t = threading.Thread(target=C().m, args=(1,), daemon=True)
    t.start()
    t.join(1.0)
    print("does not terminate" if t.is_alive() else "returned")
