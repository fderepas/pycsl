r"""Test 1884 — gen #31 WITNESS (expected FAIL): a `#@ footprint` name is checked even
when the file declares no `#@ happy` at all.

The validation exists and its own comment says why it must — "a typo would silently confine
nothing (a soundness hole, since the method would appear constrained but get no per-site
check)" — and it sat TWO LINES BELOW an early return:

    if not happy_props:
        return
    ...
    param_happy_names = {hp.name for hp in happy_props if hp.param is not None}

So the one case it missed was a `#@ footprint` written into a file with NO confinement
discipline: exactly the case where the user is most likely to be mistaken about what they
have. This file measured `[+] Verification SUCCESS! All contracts formally proven.`

The measured triple that bounds the severity, taken on a file that DOES declare a happy
property: no footprint -> FAILED; typo'd footprint -> REFUSED; correct footprint -> SUCCESS.
So the guard works where it runs; it simply did not run here.

Control: 1885, the same file with the directive removed.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ class invariant \length(self.disk) >= 1024
class Disk:
    def __init__(self) -> None:
        self.disk: list = [0] * 1024


d = Disk()


#@ footprint no_such_property(0)
#@ assigns d.disk
def writer(v: int) -> None:
    d.disk[0] = v
