"""Static gate GT1 — `Optional[Any]` refused/reported (O5/OD3).

Spec clause O5 (optional-twoplane-spec.md §1.1) and OD3 (§3): if `X` is
`Any` (`Optional[Any]`), the static plane does NOT import gradual
consistency. `Optional[Any]` is treated as the two-arm union `{Any,
None}` where `Any` is an opaque, operation-barren type (GT1); the
`None` arm remains a fully-typed arm (O3 still holds), but the `Any`
arm supports no operation without explicit narrowing. Every `Any`
occurrence is reported in `--soundness-report`. `Optional[Any]` is NOT
a universal sink.

This driver declares `Optional[Any]` and returns a constant int (no
operation on the `Any` arm). The `Any` arm must be dropped/reported
(GT1); the `None` arm remains fully typed (O3).

Expected (from spec): prove; Any arm dropped/reported (GT1).
"""

from typing import Any, Optional


#@ requires True
#@ ensures True
#@ assigns \nothing
def f(x: Optional[Any]) -> int:
    return 0


if __name__ == "__main__":
    assert f(1) == 0
    assert f(None) == 0
    print("PASS")
