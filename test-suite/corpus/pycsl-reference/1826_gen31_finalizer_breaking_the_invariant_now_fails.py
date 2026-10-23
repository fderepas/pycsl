r"""Test 1826 — gen #31 (expected FAIL): a `__del__` that breaks the class invariant.

This is 0402 with the finalizer setting `self._n = -1` instead of 0, under
`#@ class invariant self._n >= 0`.

BEFORE dunders were emitted it PROVED — `[+] Verification SUCCESS! All contracts formally
proven` — because `_should_skip_method` dropped `__del__` before any IR was built and
NOTHING ever looked at the body. `#@ allow_finalizer` meant "we ignore your finalizer".

It now FAILS on `Sub-goal type invariant of goal withfinalizer____del__'vc`. That is the
whole point of the pairing: 0402 shows the accepted case still verifies, and this file shows
the check is real rather than vacuous. Without it, 0402's new `#@ assigns self._n` would be
indistinguishable from a clause added to silence a goal.

Measured by the INDEPENDENT REVIEWER of the emit-dunders report (oracle O4), which is also
why it exists: the report had priced 0402 as a one-line repair and said nothing about the
perimeter getting STRONGER.
"""
# pycsl-expected: FAIL
""  # pycsl
#@ class invariant self._n >= 0
#@ allow_finalizer
class WithFinalizer:
    def __init__(self) -> None:
        self._n: int = 0

    #@ assigns self._n
    def __del__(self) -> None:
        self._n = -1


if __name__ == "__main__":
    pass
