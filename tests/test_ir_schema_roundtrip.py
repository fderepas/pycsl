"""test_ir_schema_roundtrip.py — Phase A gate for the typed IR sum schema.

Asserts `to_dict(from_dict(d)) == d` for every IR node (stmt + expr) in the
corpus IR JSON goldens. The typed sums (`StmtIR` / `ExprIR`) are an ADDITIVE
in-memory representation (ir-schema-spec.md Phase A): the JSON wire format is
unchanged, and nothing in the pipeline consumes the sums yet. This test is the
only consumer — it verifies the bridge (`from_dict` / `to_dict`) is a faithful
inverse, so Phase B can migrate Module6 consumers onto the sums one method at
a time without drift.
"""
import glob
import json
import os
import sys

import pytest

# Make src/pycsl importable (bare-import style used by the pycsl modules).
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "src", "pycsl"))

from ir_schema import (  # noqa: E402
    AssignStmt,
    ExprIR,
    StmtIR,
    expr_from_dict,
    from_dict,
    stmt_from_dict,
    to_dict,
)

_CORPUS_DIRS = [
    os.path.join(os.path.dirname(__file__), "..", "test-suite", "corpus",
                 "conformance", "core"),
    os.path.join(os.path.dirname(__file__), "..", "test-suite", "corpus",
                 "pycsl-reference"),
]

# Field-type strings that appear under a `"type"` key in type_decls (not IR
# expr nodes) — excluded from the expr round-trip.
_NON_EXPR_TYPES = {
    "int", "list", "tuple", "dict", "set", "frozenset", "str", "string",
    "bool", "float", "Any", "array int", "array string",
    "map int (option int)", "seq int", "list int", "option int",
    "array (int, int)", "ref int", "ref (seq int)", "ref (array int)",
}


def _ir_files():
    files = []
    for d in _CORPUS_DIRS:
        files.extend(glob.glob(os.path.join(d, "*.ir.json")))
    return sorted(files)


def _walk(node, path=""):
    if isinstance(node, dict):
        if "stmt" in node and isinstance(node["stmt"], str):
            yield ("stmt", path, node)
        elif ("type" in node and isinstance(node["type"], str)
              and node["type"] not in _NON_EXPR_TYPES):
            yield ("expr", path, node)
        for k, v in node.items():
            yield from _walk(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, x in enumerate(node):
            yield from _walk(x, f"{path}[{i}]")


@pytest.mark.parametrize("ir_file", _ir_files())
def test_roundtrip_corpus(ir_file):
    """Every stmt/expr node in every corpus IR JSON round-trips through the
    typed sum schema and back to a dict equal to the original."""
    with open(ir_file) as f:
        ir = json.load(f)
    count = 0
    for kind, path, node in _walk(ir):
        rt = to_dict(from_dict(node))
        assert rt == node, (
            f"{os.path.basename(ir_file)} {path}: {kind} round-trip mismatch\n"
            f"  orig: {node}\n  rt:   {rt}"
        )
        count += 1
    assert count > 0, f"{ir_file} yielded no IR nodes"


def test_import_surface():
    """Phase A contract: the sums and converters are importable from
    `ir_schema`."""
    from ir_schema import (
        AssignStmt, IfStmt, WhileStmt, ReturnStmt, BinOpExpr, VarExpr,
        ForallExpr, ContractExprIR, from_dict, to_dict,
    )
    assert issubclass(AssignStmt, StmtIR)
    assert issubclass(BinOpExpr, ExprIR)
    assert ContractExprIR is ExprIR


def test_typed_field_access():
    """The typed sums expose typed fields (the payoff Phase B consumes)."""
    d = {"stmt": "Assign", "target": "x",
         "value": {"type": "BinOp", "op": "+",
                   "left": {"type": "Var", "name": "x"},
                   "right": {"type": "Number", "value": 1}}}
    s = stmt_from_dict(d)
    assert isinstance(s, AssignStmt)
    assert s.target == "x"
    assert s.value.kind == "BinOp"
    assert s.value.left.kind == "Var"
    assert s.value.right.kind == "Number"
    assert to_dict(s) == d


def test_auto_dispatch():
    """`from_dict` auto-detects stmt vs expr by the tag key."""
    s = from_dict({"stmt": "Pass"})
    e = from_dict({"type": "Var", "name": "x"})
    assert isinstance(s, StmtIR)
    assert isinstance(e, ExprIR)
    assert s.kind == "Pass"
    assert e.kind == "Var"


def test_extras_fall_back_opaque():
    """A node carrying an extra attribution key (e.g. `act_name`) falls back
    to the opaque constructor so the round-trip still holds."""
    d = {"type": "BinOp", "op": "==>", "left": {"type": "Var", "name": "x"},
         "right": {"type": "Var", "name": "y"}, "act_name": "act_0"}
    node = expr_from_dict(d)
    assert node.kind == "BinOp"
    assert to_dict(node) == d


if __name__ == "__main__":
    for f in _ir_files():
        test_roundtrip_corpus(f)
    test_import_surface()
    test_typed_field_access()
    test_auto_dispatch()
    test_extras_fall_back_opaque()
    print(f"[+] round-trip OK across {len(_ir_files())} corpus IR files")


def test_expr_from_dict_class_preservation():
    """Phase-B-expr fidelity guard: kinds with a typed ExprIR class must NOT
    fall back to OpaqueExpr through expr_from_dict (regression guard for the
    DictLit/ListComp/SetComp/DictComp lossiness fixed in the schema)."""
    from ir_schema import (
        expr_from_dict, OpaqueExpr,
        DictLitExpr, ListCompExpr, SetCompExpr, DictCompExpr, ForallItemsExpr,
        ArrayEqExpr, SeparatedExpr, Length2DExpr, Valid2DExpr,
        SetCardExpr, StrSubExpr, GhostMakeExpr, SliceExpr,
        IsSortedExpr, SumExpr, GhostCopyRangeExpr, PermutationExpr,
    )
    E = {"type": "Var", "name": "x"}
    cases = {
        DictLitExpr:  {"type": "DictLit", "keys": [E], "values": [E]},
        ListCompExpr: {"type": "ListComp", "elt": E, "generators": [{"g": 1}]},
        SetCompExpr:  {"type": "SetComp", "elt": E, "generators": []},
        DictCompExpr: {"type": "DictComp", "key": E, "value": E, "generators": []},
        ForallItemsExpr: {"type": "ForallItems", "key": "k", "val": "v",
                          "map": "m", "body": {"type": "Bool", "value": True}},
        ArrayEqExpr:  {"type": "ArrayEq", "left": E, "right": E},
        SeparatedExpr: {"type": "Separated", "base1": "a", "len1": E, "base2": "b", "len2": E},
        Length2DExpr: {"type": "Length2D", "base": "a", "rows": E, "cols": E},
        Valid2DExpr:  {"type": "Valid2D", "base": "a", "row": E, "col": E},
        SetCardExpr:  {"type": "SetCard", "set": E, "lo": E, "hi": E},
        StrSubExpr:   {"type": "StrSub", "string": E, "lo": E, "hi": E},
        GhostMakeExpr: {"type": "GhostMake", "size": E, "default": E},
        SliceExpr:    {"type": "Slice", "lower": E, "upper": E, "step": None},
        IsSortedExpr: {"type": "IsSorted", "base": "a", "lo": E, "hi": E},
        SumExpr:      {"type": "Sum", "base": "a", "lo": E, "hi": E},
        GhostCopyRangeExpr: {"type": "GhostCopyRange", "arr": "a", "lo": E, "hi": E},
        PermutationExpr: {"type": "Permutation", "left": E, "right": E},
    }
    for cls, d in cases.items():
        node = expr_from_dict(d)
        assert isinstance(node, cls), f"{d['type']} -> {type(node).__name__}, expected {cls.__name__}"
        assert not isinstance(node, OpaqueExpr)
        assert node.to_dict() == d
