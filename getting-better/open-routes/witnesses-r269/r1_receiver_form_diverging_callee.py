r"""Test 2782 — route #263 (expected FAIL): 2775 through a FRESH receiver, `C().spin(k)` — the
IR's `receiver` form, lowered to a generic contract-less `val spin_1` that no dotted-call
rule sees, so it stayed a terminating stub. PROVED `\result == 7` at 283d1033. CPython:
`m(1)` never returns. Refused.
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
