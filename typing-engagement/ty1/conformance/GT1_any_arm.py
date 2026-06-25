"""Static gate GT1 — `Any` arm refused/dropped (C4/D3).

Spec clause C4 (union-twoplane-spec.md §1.1) and D3 (§3): the static plane
refuses `Any` as a Union arm (GT1). The `Any` arm is dropped from the
synthesized variant; the construct is reported in `--soundness-report`.
This driver declares `Union[Any, int]`; the int arm must still discharge
its per-arm VC (the Any arm contributes nothing).

Expected (from spec): prove the int arm; Any arm dropped/reported (GT1).
"""

from typing import Any, Union


#@ requires True
#@ ensures \result >= 0
#@ assigns \nothing
def f(x: Union[Any, int]) -> int:
    return 5


if __name__ == "__main__":
    assert f(1) == 5
    assert f("a") == 5
    print("PASS")
