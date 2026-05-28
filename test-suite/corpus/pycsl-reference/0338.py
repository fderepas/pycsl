"""Test 0338 — PyCSL Dict-as-function (cross-prover, tuesday-01).

The Coq `nat -> option nat` / Lean `Nat → Option Nat` representation
of finite maps lets both pipelines produce a clean cross-prover
contract for `dict_insert_lookup`. PyCSL's WhyML transpiler currently
doesn't support `d[k] = v` subscript assignment, so `--no-proof`
mode validates parsing only.
"""
#@ requires k >= 0
#@ requires v >= 0
#@ ensures \result == v
#@ assigns \nothing
def dict_insert_lookup(d: dict, k: int, v: int) -> int:
    # The cross-prover spec models a pure lookup-after-insert; on the
    # Python side, PyCSL doesn't yet support `d[k] = v` subscript
    # assignment, so the implementation just returns the inserted value.
    return v
