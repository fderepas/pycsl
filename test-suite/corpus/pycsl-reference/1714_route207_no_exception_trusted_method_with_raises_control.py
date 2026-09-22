r"""Test 1714 — ROUTE #207 CONTROL: a `no_exception` caller may still call a program method.

Route #207's refusal is about a BODYLESS callee whose no-raise behaviour is assumed, not
about method calls under `no_exception`. Here `helper` is an ordinary verified method with
no `raise` anywhere, so nothing is assumed and the caller's `no_exception \all` stands on
the callee's own lowered body. This file must keep PROVING; if it ever fails, the refusal
has become a ban on calling methods under `no_exception`.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


class Box:
    #@ requires n >= 0
    #@ ensures \result >= 0
    def helper(self, n: int) -> int:
        return n

    #@ requires n >= 0
    #@ no_exception \all
    #@ ensures \result == 0
    def safe(self, n: int) -> int:
        acc: int = self.helper(n)
        return 0
