"""Test 0743 — `@dataclass` registers as a record with typed `str` fields (b14 B1).

A `@dataclass` has no `__init__`; its fields are class-body AnnAssigns. Module 5
`_collect_class_fields` recognises the `@dataclass` decorator and collects those
class-level annotations as record fields (the same record route as
TypedDict/NamedTuple), so a `@dataclass`-typed PARAMETER models as a WhyML record
and `stmt.target` is a faithful field read — a `str`-annotated field lowers to
Why3 `string` (preamble `str`→`string`), and the invariant `by`-witness gives a
`string` field the empty-string `""` default (auto_trust `_build_witness_str`).
A body-faithful contract relating `\result` to a `str` field discharges.

Before b14, a bare `@dataclass` param coarsened to the opaque `int` alias and
`stmt.target` became an abstract `getattr` val — no body-faithful contract.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class AssignStmt:
    kind: str
    target: str
    value: str


#@ requires True
#@ ensures \result == stmt.target
#@ assigns \nothing
def emit_target(stmt: AssignStmt) -> str:
    return stmt.target


if __name__ == "__main__":
    s = AssignStmt(kind="Assign", target="x", value="0")
    assert emit_target(s) == "x"
    print("PASS")
