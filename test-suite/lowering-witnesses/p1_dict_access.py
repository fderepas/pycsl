"""Witness driver — Pattern 1: dict access `d[key]` / `d.get(key, default)`.

These shapes (heavily used by the compiler's own `_handle_*` methods on IR
dicts: `stmt["target"]`, `val_ir.get("type")`, `val_ir.get("elts", [])`) were
ALREADY supported by PyCSL's `map int (option int)` dict model + the
`Map.get`/subscript lowering. This file is a regression guard confirming the
body-faithful lowering still proves after the surrounding lowering extensions.
"""
#@ requires True
#@ ensures True
def f_key(stmt) -> int:
    return stmt["target"]


#@ requires True
#@ ensures True
def f_get_type(val_ir) -> int:
    return val_ir.get("type", 0)


#@ requires True
#@ ensures True
def f_get_elts(val_ir) -> int:
    return val_ir.get("elts", 0)
