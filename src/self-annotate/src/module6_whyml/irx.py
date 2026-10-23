"""irx.py — the typed accessor layer over the wall-plan-v2 concrete-map IR node.

WALL-PLAN v2, Phase 1 deliverable 4 (generic-dict-str-any-2-plan.md §2 end):
the surface-area collapse.  Module-6 walkers read heterogeneous IR nodes in ~125
places; routing every read through this accessor layer means raw universal-value
reads exist in ~12 places, not ~125 — and each accessor is verified ONCE here
instead of at every call site.

Self-hosting constraint: every accessor is written in the verifiable Python
subset and PyCSL verifies it (added to `bin/run-self-annotation-suite.sh`).  Each
read is guarded by a membership test, so no `KeyError` is reachable — the
accessors are total and exception-free by construction, which PyCSL proves.

An IR node is modelled here as the schema-keyed string map `Dict[str, str]` — the
Phase-1 shape PyCSL verifies today in the default (hoare) memory model.  Phase 2
routes these same signatures through the `pyval`/`pydict` theory + `wf_ir`
(preamble `_emit_pydict_theory`), where the `irkey`-dispatch (`==` on the interned
key type) and the child-sequence readers (`ir_get_list`/`ir_children`, returning
`list pyval`) land — those two shapes need the routed theory (string `==` and
`List` returns are exactly the heterogeneity the plan's E2/E3 rules lower), so
they are deliberately deferred to Phase 2 rather than stubbed here.

Deliberately trivial code — a formality to check, not a risk (plan §2).
"""
from __future__ import annotations

from typing import Dict


#@ requires True
#@ ensures (key in node) ==> (\result == 1)
#@ ensures not (key in node) ==> (\result == 0)
#@ assigns \nothing
def ir_has_key(node: Dict[str, str], key: str) -> bool:
    """True iff `node` binds `key` — the membership guard every read leans on."""
    if key in node:
        return True
    return False


#@ requires True
#@ ensures ("type" in node) ==> (\result == node["type"])
#@ ensures not ("type" in node) ==> (\result == "")
#@ assigns \nothing
def ir_kind(node: Dict[str, str]) -> str:
    """The node's constructor tag (wire key ``"type"``), or ``""`` if untagged.
    Total: the guard makes the read exception-free."""
    if "type" in node:
        return node["type"]
    return ""


#@ requires True
#@ ensures ("type" in node) ==> (\result == node["type"])
#@ ensures not ("type" in node) ==> (\result == default)
#@ assigns \nothing
def ir_kind_or(node: Dict[str, str], default: str) -> str:
    """The node's tag, or `default` when untagged (dispatch with an explicit
    fallback branch)."""
    if "type" in node:
        return node["type"]
    return default


#@ requires True
#@ ensures (key in node) ==> (\result == node[key])
#@ ensures not (key in node) ==> (\result == default)
#@ assigns \nothing
def ir_get_str(node: Dict[str, str], key: str, default: str) -> str:
    """Read a string-valued key, falling back to `default` when absent.
    Total: no `KeyError` is reachable (the read is guarded)."""
    if key in node:
        return node[key]
    return default


#@ requires True
#@ ensures ("op" in node) ==> (\result == node["op"])
#@ ensures not ("op" in node) ==> (\result == "")
#@ assigns \nothing
def ir_op(node: Dict[str, str]) -> str:
    """The operator string of a `BinOp`/`UnaryOp`/`AugAssign` node (wire key
    ``"op"``), or ``""`` when absent — the E4 `is_PStr (get n K_op)` read."""
    return ir_get_str(node, "op", "")


#@ requires True
#@ ensures ("target" in node) ==> (\result == node["target"])
#@ ensures not ("target" in node) ==> (\result == "")
#@ assigns \nothing
def ir_target(node: Dict[str, str]) -> str:
    """The assignment target name (wire key ``"target"``), or ``""``."""
    return ir_get_str(node, "target", "")


#@ requires True
#@ ensures ("name" in node) ==> (\result == node["name"])
#@ ensures not ("name" in node) ==> (\result == "")
#@ assigns \nothing
def ir_name(node: Dict[str, str]) -> str:
    """The variable/function name (wire key ``"name"``), or ``""``."""
    return ir_get_str(node, "name", "")


#@ requires True
#@ ensures ("func" in node) ==> (\result == node["func"])
#@ ensures not ("func" in node) ==> (\result == "")
#@ assigns \nothing
def ir_func(node: Dict[str, str]) -> str:
    """The callee name of a `Call` node (wire key ``"func"``), or ``""``."""
    return ir_get_str(node, "func", "")


#@ requires True
#@ ensures ("value" in node) ==> (\result == node["value"])
#@ ensures not ("value" in node) ==> (\result == "")
#@ assigns \nothing
def ir_value_str(node: Dict[str, str]) -> str:
    """The string payload under wire key ``"value"`` (literal/return payload
    read), or ``""`` when absent."""
    return ir_get_str(node, "value", "")


#@ requires True
#@ ensures (key in node) ==> (\result == node[key])
#@ ensures not (key in node) ==> (\result == "")
#@ assigns \nothing
def ir_get_str_present(node: Dict[str, str], key: str) -> str:
    """Read a key the caller has already established is present (the `requires
    wf_ir`/`requires key in node` shape): returns the bound value, ``""`` only on
    the unreachable absent branch.  Total by the same guard."""
    if key in node:
        return node[key]
    return ""
