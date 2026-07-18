#!/usr/bin/env python3
"""Front-end IR-resolution passes (refactor.md Phase C, C2b).

The four post-Module5 IR->IR passes the orchestrator used to run inline, now
relocated into the front-end package so the front-end emits the fully-RESOLVED
IR — the wire the language-agnostic core consumes. PURE relocation: no logic
changed, so every driver's emitted WhyML stays byte-identical.

The passes, in the exact order the orchestrator applies them:

  1. ``resolve_imports`` — multi-file import resolution. Re-runs Modules 1-5 on
     dependency source files (imported here as ``frontend.ModuleN``) and injects
     trusted stubs / records / constants into the importing module's IR.
  2. ``apply_inheritance`` — monomorphize each subclass's base method(s) onto it.
  3. ``apply_composition`` — Tier-1 ``compose_from`` mixin check + flatten.
  4. ``apply_inline_globals`` — inline method calls on module-level globals
     (re-exported from ``frontend.ir_inline``).

``resolve`` is a single convenience entry running all four in order; the
orchestrator may also call the individual passes (they are public).
"""
from __future__ import annotations

import copy
import json as _json
import os
from typing import Any, Dict, List, Optional, Set, Tuple

from frontend import pure_ast as _ast  # dependency import-discovery parses via the pure-Python front-end

# These re-run Modules 1-3 + 5 on dependency files (Module 4 was dropped — B-final).
from frontend.Module1_Ingestor import Module1_Ingestor
from frontend.Module2_Parser import Module2_Parser
from frontend.Module3_Weaver import Module3_Weaver
from frontend.Module5_IREmitter import Module5_IREmitter

# inline.md: inline method calls on module-level globals (relocated to frontend).
from frontend.ir_inline import apply_inline_globals


# ── Multi-file import helpers ──────────────────────────────────

def _collect_calls(obj: Any) -> Set[str]:
    """Recursively collect function names from Call nodes in IR."""
    calls = set()
    if isinstance(obj, dict):
        if obj.get("type") == "Call":
            calls.add(obj["func"])
        for v in obj.values():
            calls |= _collect_calls(v)
    elif isinstance(obj, list):
        for item in obj:
            calls |= _collect_calls(item)
    return calls


def _rewrite_ir_calls(obj: Any, old_name: str, new_name: str) -> None:
    """Recursively rewrite Call nodes: func old_name → new_name."""
    if isinstance(obj, dict):
        if obj.get("type") == "Call" and obj.get("func") == old_name:
            obj["func"] = new_name
        for v in obj.values():
            _rewrite_ir_calls(v, old_name, new_name)
    elif isinstance(obj, list):
        for item in obj:
            _rewrite_ir_calls(item, old_name, new_name)


# B1 (b1-plan.md): opt-in extra import roots. Set by `resolve(...)` from the CLI
# `--import-path` flag; searched *after* the built-in roots so default behaviour
# (and byte output) is unchanged. This lets a single-file verification resolve a
# dependency that lives elsewhere in the repo (e.g. the self-annotate mirror's
# `from ir_schema import AssignStmt`, where `ir_schema.py` is in `src/pycsl/`).
_EXTRA_IMPORT_PATHS: List[str] = []


def _resolve_module_path(module_dotted: str, level: int, main_file: str) -> Optional[str]:
    """Convert dotted module path to filesystem .py path.
    Returns the resolved path or None if file not found.
    Searches: main file's directory, CWD, repo `src/`, `Lib/`, then any
    `--import-path` roots (`_EXTRA_IMPORT_PATHS`)."""
    parts = module_dotted.split(".")

    if level > 0:
        # Relative import: resolve from main file's directory
        base = os.path.dirname(os.path.abspath(main_file))
        for _ in range(level - 1):
            base = os.path.dirname(base)
        candidate = os.path.join(base, *parts) + ".py"
        if os.path.isfile(candidate):
            return candidate
        pkg_init = os.path.join(base, *parts, "__init__.py")
        if os.path.isfile(pkg_init):
            return pkg_init
        return None

    # Absolute import: try main file's directory, CWD, the repo `src/` (so the
    # promoted standard library `pycsl_lib.X` resolves to `src/pycsl_lib/X`
    # regardless of cwd), then built-in Lib/ stubs
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lib_dir = os.path.join(script_dir, "Lib")
    src_dir = os.path.dirname(script_dir)  # …/pycsl/src
    for base in [os.path.dirname(os.path.abspath(main_file)), os.getcwd(),
                 src_dir, lib_dir, *_EXTRA_IMPORT_PATHS]:
        candidate = os.path.join(base, *parts) + ".py"
        if os.path.isfile(candidate):
            return candidate
        pkg_init = os.path.join(base, *parts, "__init__.py")
        if os.path.isfile(pkg_init):
            return pkg_init
    return None


def _get_module_exports(filepath: str) -> Optional[Set[str]]:
    """Return the set of public names exported by a module.
    Uses __all__ if defined, otherwise all non-underscore function names."""
    with open(filepath) as f:
        tree = _ast.parse(f.read())
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Assign):
            for target in node.targets:
                if isinstance(target, _ast.Name) and target.id == '__all__':
                    if isinstance(node.value, (_ast.List, _ast.Tuple)):
                        return {elt.value for elt in node.value.elts
                                if isinstance(elt, _ast.Constant)
                                and isinstance(elt.value, str)}
    # No __all__: return all function names that don't start with _
    return None  # caller should use all non-underscore functions


def _process_dependency(filepath: str, needed_names: Set[str], cache: Dict[str, Any],
                        deep: bool = False, processing_set: Optional[Set[str]] = None) -> List[Dict[str, Any]]:
    """Run Modules 1→5 on filepath, return list of func_ir dicts for
    the requested names (plus their transitive in-file callees),
    all marked trusted.  Results are cached by filepath.
    With deep=True, recursively resolve the dependency's own imports."""
    filepath = os.path.abspath(filepath)
    if filepath in cache:
        ir_data = cache[filepath]
    else:
        # Circular import guard
        if processing_set is not None and filepath in processing_set:
            print(f"[!] Circular import detected: '{filepath}' — skipping "
                  f"(add \\trusted stubs for the circular part)")
            return []
        if processing_set is not None:
            processing_set.add(filepath)

        with open(filepath) as f:
            dep_source = f.read()
        ingestor = Module1_Ingestor(dep_source)
        extracted = ingestor.process()
        parser_mod = Module2_Parser()
        weaver = Module3_Weaver(dep_source, extracted, parser_mod)
        unified = weaver.process()
        # Module 4 DROPPED (B-final): its checks all migrated to the IR seam, so the dep
        # sub-pipeline goes straight from the woven AST to Module 5.
        emitter = Module5_IREmitter(unified)
        ir_data = _json.loads(emitter.generate_json())

        # With --deep, resolve the dependency's own imports recursively
        if deep:
            dep_tree = _ast.parse(dep_source)
            resolve_imports(dep_tree, filepath, ir_data,
                            deep=True, cache=cache,
                            processing_set=processing_set)

        cache[filepath] = ir_data
        if processing_set is not None:
            processing_set.discard(filepath)

    all_funcs = {f["name"]: f for f in ir_data["functions"]}
    if not needed_names:
        return []

    # BFS for transitive in-file dependencies
    reachable = set()
    worklist = [n for n in needed_names if n in all_funcs]
    reachable.update(worklist)
    while worklist:
        fname = worklist.pop()
        func = all_funcs.get(fname)
        if not func:
            continue
        callees = _collect_calls(func["body"]) & set(all_funcs.keys())
        for callee in callees:
            if callee not in reachable:
                reachable.add(callee)
                worklist.append(callee)

    # Emit in the dependency's SOURCE (definition) order — `reachable` is a set,
    # so iterating it directly is hash-seed-nondeterministic; for a multi-name
    # import (e.g. `from m import a, b`) that would make the injected function
    # ORDER vary run-to-run, breaking the canonical-IR contract the conformance
    # corpus depends on. Iterating `all_funcs` (insertion-ordered = source order)
    # and filtering to `reachable` is deterministic and stable.
    result = []
    for name, func in all_funcs.items():
        if name in reachable:
            func = dict(func)  # shallow copy
            func["trusted"] = True
            result.append(func)
    return result


# ── py-expr-structural-dep-wall-response.md: structural-only shape-import ──
#
# The FABLE oracle's BREAKABLE verdict (criterion C1-C3, response §4) licenses
# harvesting a dependency's plain record `type_decl` SHAPE (field names + WhyML
# field types ONLY) WITHOUT running the dependency's semantic/UB verification
# (Module3+), for the ~20 non-list `_py_expr_*` handlers whose param is a
# pure_ast node (`ast.BinOp`, …) — pure_ast's ~90 node classes are `type()`-
# synthesized from the static `_NODE_SPEC` dict, so `_process_dependency`'s full
# Module1->Module5 run CRASHES in Module3_Weaver on pure_ast's deprecated
# `Num`/`Str`/`Ellipsis` compat shim (UB-7.6: non-trivial `__new__`). This mode
# is a DISJOINT pass from `_process_dependency` — it never runs Module3, never
# reads a `contracts_map`, and produces ONLY bare-record `type_decl`s, so the
# three obligations hold BY CONSTRUCTION, not by convention:
#   C1 (verification-independence): `_harvest_node_spec_records` can only ever
#      emit a plain field-bag (`class_invariants: []`, no refinement) — there is
#      no code path in this module that could attach an invariant to a harvested
#      decl, so the decl's meaning cannot depend on whether Module3 would have
#      accepted or rejected the source class.
#   C2 (no proof-bearing content): the harvest reads the `_NODE_SPEC` dict
#      literal ONLY; it never touches a `contracts_map`/`csl_ensures` — no
#      B-side `ensures` can ride along in this pass.
#   C3 (B verified elsewhere): pure_ast.py is a member of the self-annotation
#      suite (`bin/run-self-annotation-suite.sh`) — its own verification is a
#      separate, tracked pass from this one.
# Spike scope (per the oracle's obligation 2): ONE hand-authored table entry,
# `BinOp`, feeding the `_py_expr_binop` conversion. NOT batched to the other
# ~20 non-list `_py_expr_*` handlers — each addition to `_PURE_AST_FIELD_TABLE`
# is a deliberate, reviewed act (mirrors `_synthesize_typeddict_functional`'s
# scope discipline).

_PURE_AST_FIELD_TABLE: Dict[str, List[Tuple[str, str]]] = {
    # node name -> [(field name, IR field-type tag), ...], in `_NODE_SPEC` FIELD
    # order (order is part of the fidelity cross-check below). "ExprIR" fields
    # are expr children lowered by the importer's OWN `_py_expr_to_ir`
    # dispatcher; "int" fields are non-expr leaves (an operator-class instance,
    # read only by the trusted `_py_op_to_str` dispatcher) — obligation 3
    # (field-totality): BinOp's 3 fields are always set by the parser (no
    # `_OPTIONAL_FIELDS` entry for `BinOp` in pure_ast.py), so a TOTAL WhyML
    # record is faithful here.
    "BinOp": [("left", "ExprIR"), ("op", "int"), ("right", "ExprIR")],
    # non-list _py_expr_* batch (tier 1): UnaryOp's 2 fields (`op`, `operand`)
    # are total (no `_OPTIONAL_FIELDS` entry) — `op` tagged "int" like BinOp's
    # (read only through the trusted `_py_op_to_str` dispatcher), `operand`
    # tagged "ExprIR" (lowered by `_py_expr_to_ir`).
    "UnaryOp": [("op", "int"), ("operand", "ExprIR")],
    # _py_expr fixed-child batch (mini-M1): Starred's 2 fields (`value`, `ctx`)
    # are total (no `_OPTIONAL_FIELDS` entry). `value` tagged "ExprIR" (lowered
    # by `_py_expr_to_ir`); `ctx` tagged "int" like BinOp's/UnaryOp's `op` — an
    # expr_context leaf (Load/Store/Del) the live `_py_expr_starred` body never
    # reads, carried opaque for record totality only.
    "Starred": [("value", "ExprIR"), ("ctx", "int")],
    # _py_expr fixed-child batch (mini-M1): IfExp's 3 fields (`test`, `body`,
    # `orelse`) are total (no `_OPTIONAL_FIELDS` entry), all tagged "ExprIR"
    # (each lowered by `_py_expr_to_ir`) — feeds `_py_expr_ifexp`, which reuses
    # the GENERIC `IrTer3` ctor (module6_whyml/preamble.py `_emit_exprir_theory`,
    # ghost-handler-wall Q2) rather than a new per-node constructor.
    "IfExp": [("test", "ExprIR"), ("body", "ExprIR"), ("orelse", "ExprIR")],
    # _py_expr multi-branch batch (mini-M1): Name's 2 fields (`id`, `ctx`) are
    # total (no `_OPTIONAL_FIELDS` entry). `id` tagged "string" — the FIRST
    # string-typed field in this structural-import path — because the live
    # `_py_expr_name` body READS it as a string (guards `expr.id == "Ellipsis"`
    # / `== "None"` and the `{"type":"Var","name":expr.id}` return); `ctx`
    # tagged "int" like BinOp's/UnaryOp's `op` — an expr_context leaf
    # (Load/Store/Del) the body never reads, carried opaque for record totality.
    # Feeds `_py_expr_name`, whose 3 return paths (IrNum 0 / IrNone / IrVar id)
    # travel through the pre-existing `Return_emit_ir` early-return exception
    # (module6_whyml/statements.py `_wrap_body_with_return_catch`) and the
    # pre-existing `IrNum`/`IrNone`/`IrVar` ctors — NO new theory constructor.
    "Name": [("id", "string"), ("ctx", "int")],
    # isinstance-on-emit_ir batch (self-tcb-reduction M5): Attribute's 3 fields
    # (`value`, `attr`, `ctx`) are total (no `_OPTIONAL_FIELDS` entry). `value`
    # tagged "ExprIR" (the child expr, lowered by `_py_expr_to_ir`); `attr` tagged
    # "string" (read as the attribute-name string in both return dicts); `ctx`
    # tagged "int" — the expr_context leaf, carried opaque for record totality.
    # Feeds `_py_expr_attribute`, whose `isinstance(expr.value, ast.Name)` INPUT-
    # side type test on the already-ExprIR-typed `value` child now lowers to the
    # emit_ir ADT discriminant `(is_var expr.value)` (module6_whyml/expressions.py
    # `_handle_isinstance` + `_AST_CLASS_TO_IR_KIND`), `expr.value.id` to
    # `(name_of expr.value)` (`_EMIT_IR_STR_ATTRS["id"]`), and the
    # `obj_ir = self._py_expr_to_ir(expr.value)` local to a `ref (IrOther "")`
    # emit_ir sentinel (statements.py `_collect_emit_ir_result_locals`, the
    # emit_ir-returning-call recognizer). Returns real IrFieldGet / IrAttr ctors.
    "Attribute": [("value", "ExprIR"), ("attr", "string"), ("ctx", "int")],
    # isinstance-on-emit_ir batch (self-tcb-reduction M5): NamedExpr's 2 fields
    # (`target`, `value`) are total (no `_OPTIONAL_FIELDS` entry), both tagged
    # "ExprIR". Feeds `_py_expr_walrus`, whose
    # `target_name = expr.target.id if isinstance(expr.target, ast.Name) else
    # "_walrus"` computes a STRING via the same isinstance-on-a-child capability as
    # Attribute (`isinstance(expr.target, ast.Name)` -> `(is_var expr.target)`,
    # `expr.target.id` -> `(name_of expr.target)`), then returns the new
    # `IrNamedExpr` ctor (module6_whyml/expressions.py `_IRNODE_CTORS["NamedExpr"]`
    # + preamble.py `_emit_exprir_theory`) carrying the target-name string and the
    # `self._py_expr_to_ir(expr.value)` emit_ir sub-node.
    "NamedExpr": [("target", "ExprIR"), ("value", "ExprIR")],
    # variadic content-law comprehension (FABLE-sanctioned): Tuple's 2 fields (`elts`,
    # `ctx`) are total (no `_OPTIONAL_FIELDS` entry). `elts` tagged "ExprIRList" — the
    # FIRST list-of-ExprIR field in this structural-import path — which `_harvest_node_spec
    # _records` expands to a `{"type":"list","value_type":"emit_ir"}` field, i.e.
    # `array emit_ir` (preamble.py record emitter, i-feel-good.md I-E `List[str]`→`array
    # string` precedent, value_type "emit_ir" instead of "string"); `ctx` tagged "int" —
    # the expr_context leaf, carried opaque for record totality. Feeds `_py_expr_tuple`,
    # whose `[self._py_expr_to_ir(e) for e in expr.elts]` comprehension lowers (module6_whyml
    # /expressions.py `_content_comp` variadic branch) to `(list_content_comp_N expr.elts)`
    # : `irlist` carrying a length + per-index content law over the SHARED
    # `emit_ir_disp__py_expr_to_ir` `val function`, then builds the new `IrMkTupleN` ctor
    # (expressions.py `_IRNODE_CTORS["Tuple"]` + preamble.py `_emit_exprir_theory`).
    "Tuple": [("elts", "ExprIRList"), ("ctx", "int")],
    # variadic content-law comprehension (FABLE-sanctioned), batch 2: List and Set share
    # Tuple's element-list shape. List's fields (`elts`, `ctx`) and Set's single field
    # (`elts`) are total (no `_OPTIONAL_FIELDS` entry for either); `elts` tagged
    # "ExprIRList" -> `array emit_ir`, `ctx` "int" (the expr_context leaf, opaque). Feed
    # `_py_expr_list` (`{"type":"ArrayLit","elts":[self._py_expr_to_ir(e) for e in
    # expr.elts]}` -> `IrListN`) and `_py_expr_set` (`{"type":"SetLit","elts":[…]}` ->
    # `IrSetN`); the `elts` comprehension lowers to `(list_content_comp_N expr.elts)` over
    # the SHARED `emit_ir_disp__py_expr_to_ir`. (`_csl_call_expr`'s Call node uses the
    # CSL-AST `CallExpr` dataclass record, not this pure_ast table — its `args` retype is
    # in Module2_Parser.py.)
    "List": [("elts", "ExprIRList"), ("ctx", "int")],
    "Set":  [("elts", "ExprIRList")],
    # optional-field ext (monomorphic-option ADTs): Slice's 3 fields (`lower`,
    # `upper`, `step`) are ALL declared optional (`_OPTIONAL_FIELDS['Slice'] =
    # ('lower','upper','step')`, pure_ast.py) — the FIRST all-optional record in
    # this structural-import path. Each tagged "OptExprIR" -> a
    # `{"type":"option","value_type":"emit_ir"}` field, i.e. `option emit_ir`
    # (the Forall/Exists `domain` precedent). Feeds `_py_expr_slice`, whose body
    # `lower = self._py_expr_to_ir(expr.lower) if expr.lower else None` (×3) then
    # `return {"type":"Slice","lower":lower,"upper":upper,"step":step}` is
    # rewritten by functions.py `_recognize_slice_builder` to a single
    # `{"type":"SliceN",...}` construction with the ternaries inlined, which
    # expressions.py `_lower_sliceN_optfield` lowers to `(IrSliceN <opt> <opt>
    # <opt>)` — each bound `match expr.X with Some _v -> IrOSome (disp _v) | None
    # -> IrONone`, faithfully carrying the present/absent option (NO dropped
    # field; unlike the spec-side IrSlice which drops step). This LIFTS the
    # earlier "Slice blocked" note below (an Optional-ExprIR field tag NOW
    # exists, and IrSliceN keeps all three bounds).
    "Slice": [("lower", "OptExprIR"), ("upper", "OptExprIR"), ("step", "OptExprIR")],
    # stmt-list-append-mutation wall (self-tcb-reduction M5, C-bucket): the FIRST
    # STATEMENT node in this structural-import path (base `'stmt'`, not `'expr'` —
    # the harvest cross-checks field NAMES only, so a stmt node records identically).
    # `_NODE_SPEC['Return'] = ('stmt', ('value',), None)`; its single field `value`
    # is optional (`_OPTIONAL_FIELDS['Return'] = ('value',)`), tagged "OptExprIR" ->
    # `option emit_ir` (the Slice precedent). This is the STATEMENT-node param-
    # resolution enabler: `_py_stmt_return(self, stmt: ast.Return, …)` now types its
    # `stmt` param as the `Return` record, so the body's `self._py_expr_to_ir(stmt.value)
    # if stmt.value else None` ternary reads `stmt.value : option emit_ir` and lowers
    # (module6_whyml/expressions.py `_slice_bound_to_iropt_ir`, routed from
    # `_lower_stmt_ir_node`'s `"opt"` child kind) to `iropt_ir` — the OPTIONAL return
    # value carried by the retyped `SReturn iropt_ir` ctor (a bare `return` -> `IrONone`,
    # `return e` -> `IrOSome (py_expr_to_ir e)`). Feeds the mutable-ref stmt-append
    # convention (`ir_stmts := Seq.snoc !ir_stmts (SReturn <opt>)`).
    "Return": [("value", "OptExprIR")],
    # SUB-BODY recursion (self-tcb-reduction M5, C-bucket): the COMPOUND statement
    # nodes whose `_process_*` handler builds an SWhile/SIf/SFor. Field NAMES/order
    # match `_NODE_SPEC` exactly (the harvest cross-check is name-only). `test`/`iter`
    # → "ExprIR" (`self._py_expr_to_ir(node.test)` → emit_ir). `body` (and If's
    # `orelse`) → "StmtIRList", the FIRST opaque statement-list field: it expands to
    # `{"type":"list","value_type":"int"}` → `array int`, matching the trusted
    # `_py_stmts_to_ir(stmts: array int) : seq stmt_ir` dispatcher's param — the
    # sub-body list `self._py_stmts_to_ir(node.body)` then materializes to `stmt_list`
    # via `(seq_to_sl <seq>)` at the ctor arg (expressions.py `_lower_stmt_ir_node`
    # "stmtlist" child). Fields the ctor DROPS (While/For's `orelse`, For's `target`/
    # `type_comment`) are tagged opaque "int" — their dict values are never lowered
    # (SWhile = test+body; SFor = iter+body; SIf = test+body+orelse). @mutable_state-
    # gated end-to-end → corpus byte-inert.
    "While": [("test", "ExprIR"), ("body", "StmtIRList"), ("orelse", "int")],
    "If": [("test", "ExprIR"), ("body", "StmtIRList"), ("orelse", "StmtIRList")],
    "For": [("target", "int"), ("iter", "ExprIR"), ("body", "StmtIRList"),
            ("orelse", "int"), ("type_comment", "int")],
    # pyconst_val value-variant ADT (self-tcb-reduction M5, B-bucket): Constant's
    # 2 fields (`value`, `kind`) match `_NODE_SPEC['Constant'] = ('expr',
    # ('value','kind'), None)` in order. `value` tagged "PyConstVal" — the FIRST
    # value-scalar-union field in this structural-import path — which the preamble
    # record emitter maps to the `pyconst_val` discriminated-union ADT
    # (module6_whyml/preamble.py `_emit_exprir_theory`): the discriminated union of
    # the Python constant scalar kinds (None/bool/int/str) an `ast.Constant.value`
    # holds. This LIFTS the "value-type-discrimination" blocker cited below: the
    # `value` field is no longer a single opaque leaf but a proper sum, so
    # `_py_expr_constant`'s INPUT-side `isinstance(expr.value, bool/str/int)` /
    # `expr.value is None` value-type tests lower to the `is_pv*` discriminants
    # (module6_whyml/expressions.py `_handle_isinstance` / the `is None` handler),
    # and `expr.value` reads through the `pv*_of` projectors. `kind` tagged "int"
    # like Name's/Attribute's `ctx` — an opaque leaf the live `_py_expr_constant`
    # body never reads, carried for record totality only (every parser construction
    # sets `kind=None`; its `_OPTIONAL_FIELDS` membership does not affect the
    # structural harvest, which cross-checks field NAMES only).
    "Constant": [("value", "PyConstVal"), ("kind", "int")],
    #
    # `_py_expr_attribute` — CONVERTED (isinstance-on-emit_ir batch, see the
    # "Attribute" table entry above). Its `isinstance(expr.value, ast.Name)` guard
    # is exactly the isinstance-on-a-CHILD-NODE capability that landed here: the
    # `value` child is ExprIR-typed, so the INPUT-side type test lowers to the
    # emit_ir ADT discriminant `(is_var expr.value)` and `expr.value.id` to
    # `(name_of expr.value)`. The FieldGet/Attribute split is a real if/else.
    #
    # `_py_expr_constant` — the value-type-discrimination capability that BLOCKED
    # it has now LANDED (the "Constant" table entry above + the `pyconst_val` ADT):
    # `expr.value is None` / `isinstance(expr.value, bool/str/int)` lower to the
    # `is_pvnone`/`is_pvbool`/`is_pvstr`/`is_pvint` discriminants. The None/bool/
    # str/int CORE thus lowers faithfully. The bytes / complex / Ellipsis branches
    # (`[IrNum(b) for b in expr.value]` per-byte comprehension over the bytes
    # payload; `int(expr.value.real)` complex trunc; `expr.value is ...`) need
    # further value-model infra (a PVBytes iterable + a bytes content-comprehension,
    # a PVComplex real+trunc, a PVEllipsis singleton); until that lands the WHOLE
    # body cannot be ported faithfully, so `_py_expr_constant` stays `\trusted` this
    # round (no half-body conversion) — the ADT + recognizers are banked for the
    # follow-on. See value-model-wall-stand-alone.md.
    #
    # `_py_expr_slice` — CONVERTED (optional-field ext, see the "Slice" table
    # entry above). The two blockers cited historically are BOTH lifted: an
    # Optional-ExprIR field tag ("OptExprIR" → `option emit_ir`) now exists, and
    # the new `IrSliceN` ctor keeps ALL THREE bounds (lower/upper/step) as real
    # `iropt_ir` values — it does NOT reuse the spec-side `IrSlice` (which drops
    # step). The body's `disp(expr.X) if expr.X else None` ternaries are handled
    # by `_recognize_slice_builder`/`_lower_sliceN_optfield` (no `isinstance`
    # input-side test is involved — the option field IS the discriminant).
    #
    # `_py_expr_subscript` was INVESTIGATED for this batch and found blocked, not
    # just unattempted (see the non-list-py-expr-batch report): Subscript's body
    # branches on `isinstance(slice_node, ast.Slice)` — an INPUT-side type test
    # the structural mode cannot express (each harvested pure_ast node is an
    # opaque record, not a member of a common discriminated union); the sound
    # OUTPUT-side rewrite (discriminate on `_py_expr_to_ir(expr.slice).get("type")`
    # instead) needs `_is_emit_ir_expr` (module6_whyml/expressions.py) /
    # `_is_emit_ir_val` (module6_whyml/statements.py
    # `_collect_emit_ir_result_locals`) to recognize a `self._py_expr_to_ir(...)`
    # CALL as an ExprIR-typed value/receiver — a real Module6 capability gap
    # (today they only special-case `.to_dict()`/`.get()` chains and field/Var
    # shapes, not a generic recursive-dispatcher call). No table entry until that
    # capability lands.
}


def _harvest_node_spec_records(tree: Any) -> Dict[str, Dict[str, Any]]:
    """Piece 2 (structural harvest): recognize the module-level `_NODE_SPEC =
    {...}` dict literal (pure_ast.py's ASDL-derived node table — the same
    dict-literal-recognition PATTERN `_synthesize_typeddict_functional`
    (Module5_IREmitter.py) uses for a functional `TypedDict(...)` call) and
    synthesize a plain record `type_decl` for each entry ALSO present in
    `_PURE_AST_FIELD_TABLE`.

    C1/C2 are enforced BY CONSTRUCTION here, not by convention: this function
    reads ONLY the literal dict AST node plus `_PURE_AST_FIELD_TABLE` — there is
    no `contracts_map`, no `csl_class_invariants`, no `ensures` anywhere in its
    scope, so no invariant or proof-bearing content can ever be attached to a
    harvested decl.

    Obligation 2 (fidelity): cross-checks each table entry's field NAMES (in
    order) against the actual `_NODE_SPEC` tuple for that node; a mismatch (the
    hand-authored table drifted from the real spec) is DROPPED — the caller
    falls back to the pre-existing opaque `int` typing rather than emitting a
    wrong-shaped record."""
    records: Dict[str, Dict[str, Any]] = {}
    for stmt in getattr(tree, "body", []) or []:
        if not (isinstance(stmt, _ast.Assign) and len(stmt.targets) == 1
                and isinstance(stmt.targets[0], _ast.Name)
                and stmt.targets[0].id == "_NODE_SPEC"
                and isinstance(stmt.value, _ast.Dict)):
            continue
        for k, v in zip(stmt.value.keys, stmt.value.values):
            if not (isinstance(k, _ast.Constant) and isinstance(k.value, str)):
                continue
            node_name = k.value
            table_entry = _PURE_AST_FIELD_TABLE.get(node_name)
            if table_entry is None:
                continue
            # v is `(base_name, fields_tuple, attributes)` — cross-check the
            # fields tuple's element NAMES/ARITY against the table (obligation 2).
            if not (isinstance(v, _ast.Tuple) and len(v.elts) >= 2
                    and isinstance(v.elts[1], _ast.Tuple)):
                continue
            spec_field_names = [e.value for e in v.elts[1].elts
                                if isinstance(e, _ast.Constant)
                                and isinstance(e.value, str)]
            if spec_field_names != [fname for fname, _ in table_entry]:
                continue  # table drifted from _NODE_SPEC — refuse, stay opaque
            # variadic content-law comprehension: the "ExprIRList" tag (a list-of-ExprIR
            # field, e.g. Tuple.elts) expands to a `{"type":"list","value_type":"emit_ir"}`
            # field — the preamble record emitter then maps `list`+value_type `emit_ir` to
            # `array emit_ir` (i-feel-good.md I-E, value_type "emit_ir"). Every other tag is
            # a scalar field carried through verbatim.
            fields = []
            for fname, ftype in table_entry:
                if ftype == "ExprIRList":
                    fields.append({"name": fname, "type": "list",
                                   "value_type": "emit_ir", "mutable": True})
                elif ftype == "StmtIRList":
                    # SUB-BODY recursion (C-bucket): an opaque statement-list field
                    # (While/If/For's `body`, If's `orelse`) — the raw `List[ast.stmt]`
                    # the trusted `_py_stmts_to_ir` dispatcher consumes. Expands to a
                    # `{"type":"list","value_type":"int"}` field → `array int` (the
                    # ExprIRList precedent with value_type "int"), matching the
                    # dispatcher's `array int` param; collapses to `int` off
                    # @mutable_state (corpus byte-inert).
                    fields.append({"name": fname, "type": "list",
                                   "value_type": "int", "mutable": True})
                elif ftype == "OptExprIR":
                    # optional-field ext (monomorphic-option ADTs): an
                    # `Optional[ExprIR]` pure_ast field (Slice.lower/upper/step,
                    # each in `_OPTIONAL_FIELDS['Slice']`) expands to a
                    # `{"type":"option","value_type":"emit_ir"}` field — the
                    # preamble record emitter maps `option`+value_type `emit_ir`
                    # to `option emit_ir` (the Forall/Exists `domain` precedent),
                    # collapsing to `int` off @mutable_state (corpus byte-inert).
                    fields.append({"name": fname, "type": "option",
                                   "value_type": "emit_ir", "mutable": True})
                else:
                    fields.append({"name": fname, "type": ftype, "mutable": True})
            records[node_name] = {
                "kind": "record", "name": node_name, "fields": fields,
                "class_invariants": [],
                "field_defaults": {fname: 0 for fname, _ in table_entry},
                "has_hash": False, "has_eq": False, "is_unhashable": False,
                "constants": {}, "bases": [],
                "init_params": [], "init_body": [], "init_ensures": [],
                "is_mixin": False, "compose_from": [],
            }
        break  # only one `_NODE_SPEC` assignment is ever expected
    return records


def _process_dependency_structural(filepath: str,
                                   struct_cache: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Piece 1: structural-only dependency-compile mode. Parses `filepath` with
    the pure-Python front-end parser ONLY — Module1's contract extraction and
    Module3's semantic/UB verification are NOT run (this is the point: it skips
    the UB-7.6 crash on pure_ast's `Num`/`Str`/`Ellipsis` compat shim) — and
    returns the `_NODE_SPEC`-harvested records (piece 2). Cached separately from
    the verified-dependency `cache` used by `_process_dependency`: the two
    passes are disjoint (a real verified compile of the same file elsewhere,
    e.g. via `_resolve_imported_classes`, is unaffected by this cache, and vice
    versa)."""
    filepath = os.path.abspath(filepath)
    if filepath in struct_cache:
        return struct_cache[filepath]
    with open(filepath) as f:
        dep_source = f.read()
    tree = _ast.parse(dep_source)
    records = _harvest_node_spec_records(tree)
    struct_cache[filepath] = records
    return records


def _resolve_pure_ast_param_records(validated_ast: Any, main_file: str,
                                    ir_data: Dict[str, Any],
                                    struct_cache: Dict[str, Any]) -> None:
    """Piece 3: cross-file dotted-param resolution. For a param annotated
    `<alias>.<NodeName>` where `<alias>` is the local name bound by a
    `from <pkg> import pure_ast as <alias>` import (`ir_data["imports"]`) and
    `<NodeName>` is a structurally-harvested pure_ast record (piece 1+2), patch
    the function's `symbol_table[param]` from the opaque `Any`->int fallback to
    the harvested record's name, so Module6 types the param as the record. The
    harvested `type_decl` is injected into `ir_data["type_decls"]` (additive
    only, de-duped by name — never overwrites an existing decl of the same
    name).

    No-op (byte-identical) unless BOTH a `pure_ast`-alias import AND a matching
    dotted param annotation are present in `main_file` — the whole corpus has
    neither, so this pass is corpus-inert for every existing driver."""
    aliases: List[Tuple[str, str, int]] = []  # (local, dotted module path, level)
    for entry in ir_data.get("imports", []):
        if len(entry) < 5:
            continue
        local, original, module, level, is_mod = entry[:5]
        if is_mod or original != "pure_ast":
            continue
        dotted = f"{module}.{original}" if module else original
        aliases.append((local, dotted, level))
    if not aliases:
        return

    harvested: Dict[str, Dict[str, Any]] = {}
    alias_names: Set[str] = set()
    for local, dotted, level in aliases:
        resolved = _resolve_module_path(dotted, level, main_file)
        if resolved is None:
            continue
        recs = _process_dependency_structural(resolved, struct_cache)
        if recs:
            alias_names.add(local)
            harvested.update(recs)
    if not harvested:
        return

    used: Set[str] = set()
    func_by_name = {f["name"]: f for f in ir_data.get("functions", [])}

    def _patch(func_name: str, fn_node: Any) -> None:
        func_ir = func_by_name.get(func_name)
        if func_ir is None:
            return
        symtab = func_ir.get("symbol_table")
        if symtab is None:
            return
        for arg in fn_node.args.args:
            ann = arg.annotation
            if not (isinstance(ann, _ast.Attribute)
                    and isinstance(ann.value, _ast.Name)
                    and ann.value.id in alias_names
                    and ann.attr in harvested):
                continue
            symtab[arg.arg] = ann.attr
            used.add(ann.attr)

    for node in getattr(validated_ast, "body", []) or []:
        if isinstance(node, _ast.ClassDef):
            cname = node.name.lower()
            for m in node.body:
                if isinstance(m, _ast.FunctionDef):
                    _patch(f"{cname}__{m.name}", m)
        elif isinstance(node, _ast.FunctionDef):
            _patch(node.name, node)

    if not used:
        return
    existing = {td.get("name") for td in ir_data.get("type_decls", [])}
    for name in sorted(used):
        if name in existing:
            continue
        ir_data.setdefault("type_decls", []).append(harvested[name])
        existing.add(name)


# gap-13: the two directory-uniqueness CLASS-INVARIANT axioms must survive the
# importer strip below. Unlike the heavy scan axioms, the importer is EXACTLY
# where they are needed: the class invariant's ESTABLISHMENT VC lives on the
# `_filesystem` module-global instance (importer), and its MAINTENANCE VC lives
# on every imported `assigns self.disk` syscall stub (importer). Both are
# low-fan-out, byte-local decode facts (no `dir_lookup` existential), so they do
# NOT cause the gap-9 E-matching blowup that motivated stripping the scan axioms.
_DIR_CLASS_INV_AXIOMS = frozenset({
    "UnixFs.Dir.empty_disk_slots_dead",
    "UnixFs.Dir.block5_decode_frame",
})


def _strip_dir_scan_proofs(func: Dict[str, Any]) -> Dict[str, Any]:
    """gap-9: drop `#@ proof … UnixFs.Dir.scan_reflects_present` (and its
    `slot_inode_nonneg` companion) citations from an INJECTED trusted stub.

    A trusted stub's contract is ASSUMED in the importer, so its body is NOT
    re-verified there — the heavy scan axiom (`dir_lookup … <-> exists k …`)
    would only pollute the importer's proof context with a high-fan-out
    E-matching trigger (Alt-Ergo/Z3 OOM on the `access`/`mkdir` wrapper VCs that
    merely need the propositional `name_present` link from the syscall stub's
    own ensures). The axiom is cited where it is actually USED — the standalone
    `UnixInodeFileSystem.py` body verification. The `slot_inode`/`slot_name`/
    `dir_lookup` `val function` decls the `name_present` inductive needs are
    still emitted by `_emit_inductive_decls` (independent of the citation).

    gap-13 EXCEPTION: the two directory-uniqueness CLASS-INVARIANT axioms
    (`_DIR_CLASS_INV_AXIOMS`) are KEPT — the importer is where the invariant's
    establishment (`_filesystem` global) and maintenance (imported syscall
    stubs) VCs need them, and they are low-fan-out decode-locality facts (no
    `dir_lookup` existential), so they do not reintroduce the gap-9 blowup."""
    proofs = func.get("proof")
    if not proofs:
        return func
    kept = [p for p in proofs
            if not str(p.get("qualname", "")).startswith("UnixFs.Dir.")
            or str(p.get("qualname", "")) in _DIR_CLASS_INV_AXIOMS]
    if len(kept) != len(proofs):
        func = dict(func)
        func["proof"] = kept
    return func


def _contract_referenced_var_names(dep_funcs: List[Dict[str, Any]]) -> Set[str]:
    """Collect every Var/object NAME referenced inside the contracts of the
    injected stubs — including the object of an `Attribute`/`FieldGet`
    (`_filesystem.disk` → `_filesystem`). Used to scope module-global
    propagation to globals the injected contracts actually touch (gap-9)."""
    referenced: Set[str] = set()

    def _walk(node: Any) -> None:
        if isinstance(node, dict):
            t = node.get("type")
            if t == "Var" and isinstance(node.get("name"), str):
                referenced.add(node["name"])
            obj = node.get("object")
            if isinstance(obj, str):
                referenced.add(obj)
            for v in node.values():
                _walk(v)
        elif isinstance(node, (list, tuple)):
            for v in node:
                _walk(v)

    for func in dep_funcs:
        contracts = func.get("contracts", {}) or {}
        _walk(contracts.get("requires", []))
        _walk(contracts.get("ensures", []))
        _walk(contracts.get("assigns", []))
    return referenced


def _find_record_type_from_dep_imports(
        rec_name: str, dep_file: str, cache: Dict[str, Any],
        deep: bool, processing_set: Set[str]) -> Optional[Dict[str, Any]]:
    """11-1039-spec-10 (multi-hop): a propagated module-global's record TYPE may
    not live in its own module's `type_decls` — the os PACKAGE (`os/__init__.py`)
    instantiates `_filesystem = UnixInodeFileSystem()` but only IMPORTS the
    `UnixInodeFileSystem` record (`from .UnixInodeFileSystem import …`); with the
    standard `--deep`-off pipeline the package's own imports are not transitively
    resolved, so the record is absent from the package IR's `type_decls`. Follow
    the dependency's OWN `imports` one hop to the module that DEFINES `rec_name`,
    process it, and return its `type_decl`. Returns None if not found (fail-loud
    downstream: an unbound type, never a silently-unsound emission)."""
    dep_ir = cache.get(os.path.abspath(dep_file)) or {}
    for entry in dep_ir.get("imports", []):
        # [local, original, module, level, is_module]
        if len(entry) < 5:
            continue
        local, original, module, level, _is_mod = entry[:5]
        if local != rec_name:
            continue
        sub_resolved = _resolve_module_path(module, level, dep_file)
        if sub_resolved is None:
            continue
        _process_dependency(sub_resolved, [], cache, deep=deep,
                            processing_set=processing_set)
        sub_ir = cache.get(os.path.abspath(sub_resolved)) or {}
        for td in sub_ir.get("type_decls", []):
            if td.get("name") == original:
                return td
    return None


def _contract_referenced_names(dep_funcs: List[Dict[str, Any]]) -> Set[str]:
    """Collect every callee name applied inside the contracts (`requires`/`ensures`)
    of the injected dependency stubs. Used by 11-0632-spec-8 Part 1 to scope inductive
    propagation to predicate names the public contracts actually reference (so unrelated
    internal predicates do not cross the import boundary)."""
    referenced: Set[str] = set()

    def _walk(node: Any) -> None:
        if isinstance(node, dict):
            if node.get("type") == "Call" and isinstance(node.get("func"), str):
                referenced.add(node["func"])
            for v in node.values():
                _walk(v)
        elif isinstance(node, (list, tuple)):
            for v in node:
                _walk(v)

    for func in dep_funcs:
        contracts = func.get("contracts", {}) or {}
        _walk(contracts.get("requires", []))
        _walk(contracts.get("ensures", []))
    return referenced


def _contract_referenced_var_names(dep_funcs: List[Dict[str, Any]]) -> Set[str]:
    """Collect every bare-variable name read inside the contracts
    (`requires`/`ensures`/`assigns`) of the injected dependency stubs — both
    plain `Var` references and the `object` of an `Attribute` projection
    (`_filesystem.disk` → `_filesystem`). Used by 11-1039-spec-10 to scope
    module-global propagation to ONLY the globals an injected public contract
    actually references (so unrelated dependency globals do not cross the import
    boundary, keeping the propagation byte-additive)."""
    referenced: Set[str] = set()

    def _walk(node: Any) -> None:
        if isinstance(node, dict):
            ntype = node.get("type")
            if ntype == "Var" and isinstance(node.get("name"), str):
                referenced.add(node["name"])
            elif ntype == "Attribute":
                obj = node.get("object")
                if isinstance(obj, dict) and obj.get("type") == "Var" \
                        and isinstance(obj.get("name"), str):
                    referenced.add(obj["name"])
            for v in node.values():
                _walk(v)
        elif isinstance(node, (list, tuple)):
            for v in node:
                _walk(v)

    for func in dep_funcs:
        contracts = func.get("contracts", {}) or {}
        _walk(contracts.get("requires", []))
        _walk(contracts.get("ensures", []))
        _walk(contracts.get("assigns", []))
    return referenced


def _inject_functions(dep_funcs: List[Dict[str, Any]], ir_data: Dict[str, Any]) -> Set[str]:
    """Insert each dependency stub at the front of `ir_data['functions']` if no function
    of that name is present yet; return the set of names added. Shared by the three import
    resolvers (direct / wildcard / module-qualified)."""
    imported = set()
    existing = {f["name"] for f in ir_data["functions"]}
    for func_ir in dep_funcs:
        if func_ir["name"] not in existing:
            ir_data["functions"].insert(0, func_ir)
            imported.add(func_ir["name"])
            existing.add(func_ir["name"])
    return imported


def _resolve_direct_imports(direct_imports: List[Any], all_calls: Set[str], main_file: str,
                             ir_data: Dict[str, Any], deep: bool, cache: Dict[str, Any],
                             processing_set: Set[str]) -> Set[str]:
    """Inject trusted stubs for `from mod import name` imports. Returns added names."""
    from collections import defaultdict
    imported_names = set()
    by_module = defaultdict(list)
    for local, original, module_path, level in direct_imports:
        by_module[(module_path, level)].append((local, original))

    for (module_path, level), names in by_module.items():
        needed = [(local, orig) for local, orig in names if local in all_calls]
        resolved = _resolve_module_path(module_path, level, main_file)
        if resolved is None:
            for local, orig in needed:
                print(f"[*] Import '{module_path}.{orig}': external module, "
                      f"no local source found — skipping (add \\trusted stub "
                      f"if verification of callers needs its contract)")
            continue
        orig_names = [orig for _, orig in needed]
        # Process the dependency even when no *called* function is needed — an
        # import may bring only constants (1111-spec R6), and we still need the
        # dep's IR (cached) to read their values.
        dep_funcs = _process_dependency(resolved, orig_names, cache,
                                        deep=deep, processing_set=processing_set)
        for func_ir in dep_funcs:
            for local, orig in needed:
                if func_ir["name"] == orig and local != orig:
                    func_ir["name"] = local
        imported_names |= _inject_functions(dep_funcs, ir_data)
        # 1111-spec R6 (no-more-int): propagate the imported module's
        # compile-time constant VALUES so the importer folds `SEEK_SET` to its
        # literal `0` (via Module6's `_module_constants`), instead of emitting a
        # value-less `val constant sEEK_SET : int`. Local definitions win on a
        # name clash (only fill names the importer does not already define).
        dep_consts = (cache.get(os.path.abspath(resolved), {}) or {}).get("module_constants", {})
        if dep_consts:
            own = ir_data.setdefault("module_constants", {})
            for local, orig in names:
                if orig in dep_consts and local not in own:
                    own[local] = dep_consts[orig]
        # 11-0632-spec-8 Part 1 (carry a contract-referenced LOGIC symbol across the
        # import boundary): an injected stub's `#@ ensures` may apply a module-level
        # `#@ inductive` predicate (gap-7's `present`) declared in the dependency. The
        # dependency emits the predicate as a logic `inductive …` block standalone, but
        # the importer never received the decl — so its lowering falls back to a program
        # `val present_1 (int):int`, which is illegal in `ensures` and mistyped. Mirror
        # the `module_constants` propagation: copy the dep's `inductive_decls` into the
        # importer's IR, de-duped by name, scoped to the predicate names the INJECTED
        # contracts actually reference (so unrelated internal predicates do not cross the
        # public boundary). Module6 then registers `present` in `_inductive_preds` and
        # `_emit_inductive_decls` emits the real logic block — the program-`val` fallback
        # is never reached.
        dep_ind = (cache.get(os.path.abspath(resolved), {}) or {}).get("inductive_decls", [])
        if dep_ind:
            referenced = _contract_referenced_names(dep_funcs)
            tgt = ir_data.setdefault("inductive_decls", [])
            have = {d["name"] for d in tgt}
            for d in dep_ind:
                if d["name"] in have:
                    continue
                names_of_d = {d["name"]} | {m["name"] for m in d.get("members", [])}
                if names_of_d & referenced:
                    tgt.append(copy.deepcopy(d))
                    have.add(d["name"])
        # 11-1039-spec-10 (carry a contract-referenced MODULE-GLOBAL across the
        # import boundary): an injected stub's `#@ ensures` may project a field of
        # a dependency module-level global object — `dir_lookup(_filesystem.disk,
        # 5, name) >= 0`. The dependency emits the global as a `let`-bound record
        # (`let _filesystem : unixinodefilesystem = <literal>`, preamble.py
        # `_emit_module_globals`) whose `.disk` projection is a LEGAL logic
        # record-field accessor. But the importer never received `module_globals`,
        # so `_module_global_classes` is empty and the contract reference falls
        # back to the opaque program forms (`val constant _filesystem : int` +
        # `val get_disk`, illegal in `ensures`). Mirror the `module_constants` /
        # `inductive_decls` propagation: copy the dep's `module_globals` (and the
        # record type each names) into the importer, de-duped by name, scoped to
        # the globals the INJECTED contracts actually reference (so unrelated
        # dependency globals do not cross). Module6 then re-emits the SAME
        # `let`-bound record and the contract resolves through the working
        # in-module branches (expressions.py 1929-1934 / 1976-1977) — byte-
        # identically to how the dependency itself emits it. Option B of the spec
        # (the only type-checking form: the disk is a mutable `array int`, so a
        # standalone pure accessor is rejected by Why3).
        dep_globals = (cache.get(os.path.abspath(resolved), {}) or {}).get("module_globals", [])
        if dep_globals:
            ref_vars = _contract_referenced_var_names(dep_funcs)
            tgt_g = ir_data.setdefault("module_globals", [])
            have_g = {g["name"] for g in tgt_g}
            # The record TYPE each propagated global names must survive into the
            # importer's `type_decls` (risk 2: the global re-references a record
            # that is otherwise pruned/never-imported, so `_filesystem.disk` must
            # resolve as the record-field projection, not the opaque fallback).
            dep_types = {td.get("name"): td
                         for td in (cache.get(os.path.abspath(resolved), {}) or {}).get("type_decls", [])}
            tgt_t = ir_data.setdefault("type_decls", [])
            have_t = {td.get("name") for td in tgt_t}
            for g in dep_globals:
                if g["name"] in have_g or g["name"] not in ref_vars:
                    continue
                tgt_g.append(copy.deepcopy(g))
                have_g.add(g["name"])
                rec_name = g.get("class")
                if rec_name and rec_name not in have_t:
                    rec_td = dep_types.get(rec_name)
                    if rec_td is None:
                        # Multi-hop: the package instantiates the global but only
                        # IMPORTS its record type (os/__init__ →
                        # UnixInodeFileSystem) — follow the dep's own imports one
                        # hop to the defining module and pull the record there.
                        rec_td = _find_record_type_from_dep_imports(
                            rec_name, resolved, cache, deep, processing_set)
                    if rec_td is not None:
                        tgt_t.append(copy.deepcopy(rec_td))
                        have_t.add(rec_name)
        resolved_locals = [local for local, _ in needed]
        if resolved_locals:
            print(f"[*] Imported from '{module_path}': {resolved_locals} (trusted stubs)")

    return imported_names


def _resolve_wildcard_imports(wildcard_imports: List[Any], all_calls: Set[str], main_file: str,
                               ir_data: Dict[str, Any], deep: bool, cache: Dict[str, Any],
                               processing_set: Set[str]) -> Set[str]:
    """Inject trusted stubs for `from mod import *` imports. Returns added names."""
    imported_names = set()
    for module_path, level in wildcard_imports:
        resolved = _resolve_module_path(module_path, level, main_file)
        if resolved is None:
            print(f"[*] Import '{module_path}.*': external module, "
                  f"no local source found — skipping")
            continue
        _process_dependency(resolved, [], cache, deep=deep, processing_set=processing_set)
        abs_resolved = os.path.abspath(resolved)
        dep_ir = cache.get(abs_resolved)
        if dep_ir is None:
            continue
        explicit_all = _get_module_exports(resolved)
        exported = explicit_all if explicit_all is not None else {
            f["name"] for f in dep_ir["functions"] if not f["name"].startswith("_")
        }
        needed_names = sorted(exported & all_calls)
        if not needed_names:
            continue
        dep_funcs = _process_dependency(resolved, needed_names, cache,
                                        deep=deep, processing_set=processing_set)
        imported_names |= _inject_functions(dep_funcs, ir_data)
        print(f"[*] Imported from '{module_path}.*': {needed_names} (wildcard, trusted stubs)")

    return imported_names


def _resolve_module_imports(module_imports: List[Any], all_calls: Set[str], main_file: str,
                             ir_data: Dict[str, Any], deep: bool, cache: Dict[str, Any],
                             processing_set: Set[str]) -> Set[str]:
    """Inject trusted stubs for `import mod` / `import mod as alias` imports. Returns added names."""
    imported_names = set()
    for local_name, original_name, module_path, level in module_imports:
        prefix = local_name + "."
        matching_calls = [c for c in all_calls if c.startswith(prefix)]
        if not matching_calls:
            continue
        resolved = _resolve_module_path(module_path, level, main_file)
        if resolved is None:
            for call in matching_calls:
                print(f"[*] Import '{module_path}.{call[len(prefix):]}': external module, "
                      f"no local source found — skipping")
            continue
        func_names = [call[len(prefix):] for call in matching_calls]
        dep_funcs = _process_dependency(resolved, func_names, cache,
                                        deep=deep, processing_set=processing_set)
        imported_names |= _inject_functions(dep_funcs, ir_data)
        for call in matching_calls:
            bare_name = call[len(prefix):]
            for f in ir_data["functions"]:
                _rewrite_ir_calls(f, call, bare_name)
        print(f"[*] Imported from '{module_path}': {func_names} (trusted stubs, module-qualified)")

    return imported_names


def _resolve_imported_classes(direct_imports: List[Any], main_file: str,
                              ir_data: Dict[str, Any], deep: bool,
                              cache: Dict[str, Any],
                              processing_set: Set[str]) -> Set[str]:
    """Layer A — cross-module class resolution.

    For each `from mod import ClassName`, if `ClassName` is a class in the
    dependency (it has a `type_decl` record there), inject that record —
    its fields, defaults, and class invariants — into the importing module's
    IR, plus the class's `<class>__*` methods as trusted stubs. This lets the
    importer construct the class (record construction with the imported
    defaults) and read its fields concretely, rather than via opaque ops.
    Returns the set of class names injected.
    """
    from collections import defaultdict
    added: Set[str] = set()
    by_module = defaultdict(list)
    for local, original, module_path, level in direct_imports:
        by_module[(module_path, level)].append((local, original))

    existing_types = {td.get("name") for td in ir_data.get("type_decls", [])}
    existing_funcs = {f["name"] for f in ir_data["functions"]}

    for (module_path, level), names in by_module.items():
        resolved = _resolve_module_path(module_path, level, main_file)
        if resolved is None:
            continue
        # Process + cache the dependency (no specific functions requested —
        # we read its type_decls directly from the cached IR).
        _process_dependency(resolved, [], cache, deep=deep,
                            processing_set=processing_set)
        dep_ir = cache.get(os.path.abspath(resolved))
        if not dep_ir:
            continue
        dep_types = {td.get("name"): td for td in dep_ir.get("type_decls", [])}
        dep_funcs = {f["name"]: f for f in dep_ir.get("functions", [])}
        for local, orig in names:
            if orig not in dep_types or local in existing_types:
                continue
            td = dict(dep_types[orig])
            td["name"] = local  # honour `import Cls as Alias`
            ir_data.setdefault("type_decls", []).append(td)
            existing_types.add(local)
            added.add(local)
            # Methods are mangled `<class_lower>__<method>`. Inject them as
            # trusted stubs in the un-aliased case (the mangling still matches
            # the record name); an alias would need re-mangling (deferred).
            injected_methods = 0
            injected_fnames: Set[str] = set()
            if local == orig:
                prefix = f"{orig.lower()}__"
                for fname, f in dep_funcs.items():
                    if fname.startswith(prefix) and fname not in existing_funcs:
                        mf = _strip_dir_scan_proofs(dict(f))
                        mf["trusted"] = True
                        ir_data["functions"].insert(0, mf)
                        existing_funcs.add(fname)
                        injected_fnames.add(fname)
                        injected_methods += 1
            # inline.md: also import module-level helper functions from the
            # dependency that class methods may call.  After inlining splices
            # a method body, bare calls to these helpers must resolve to real
            # function stubs (with correct types), not opaque int-typed vals.
            injected_helpers = 0
            if local == orig:
                prefix = f"{orig.lower()}__"
                dep_module_funcs = {
                    fn: ff for fn, ff in dep_funcs.items()
                    if not fn.startswith(prefix) and fn not in existing_funcs
                }
                for fname, f in dep_module_funcs.items():
                    mf = _strip_dir_scan_proofs(dict(f))
                    mf["trusted"] = True
                    ir_data["functions"].insert(0, mf)
                    existing_funcs.add(fname)
                    injected_fnames.add(fname)
                    injected_helpers += 1
            # gap-9: a class method's `#@ ensures` may apply a module-level
            # `#@ inductive` predicate declared in the dependency
            # (`name_present`). We deliberately do NOT copy the dep's
            # `inductive_decls` RULE into the importer: the `name_present` rule
            # carries a heavy `\exists k. slot_inode … slot_name …` premise whose
            # E-matching blows up the (large) importer wrapper VCs. Instead the
            # importer gets an OPAQUE `predicate name_present (array int) string`
            # (the `_emit_contract_logic_symbol` fallback, type-corrected by
            # `_imported_predicate_arg_types`); the public-API wrappers reason
            # via the lighter, equivalent `dir_lookup(disk, 5, name) >= 0` form,
            # so the opaque predicate's exact value is never needed at the
            # boundary. Record the dep's inductive predicate SIGNATURES so the
            # fallback can recover the right param types.
            dep_ind = dep_ir.get("inductive_decls", [])
            if dep_ind:
                sigs = ir_data.setdefault("_imported_inductive_sigs", {})
                for d in dep_ind:
                    for m in [d] + d.get("members", []):
                        if m.get("name") and m.get("signature"):
                            sigs[m["name"]] = m["signature"]
            print(f"[*] Imported class from '{module_path}': {local} "
                  f"(record + {injected_methods} method stub(s)"
                  f" + {injected_helpers} helper(s))")
    return added


def _resolve_imported_base_classes(module_imports: List[Any], main_file: str,
                                   ir_data: Dict[str, Any], deep: bool,
                                   cache: Dict[str, Any],
                                   processing_set: Set[str]) -> Set[str]:
    """Layer A′ — resolve a subclass's base that lives behind a *module* import.

    For `import ast` + `class X(ast.NodeVisitor)`, Module5 records the base as
    the bare attribute tail `NodeVisitor`; the `from`-import path never sees it
    because the import is a module import. Here we look up each still-unresolved
    base name among the module-imported dependencies and inject its record +
    `<class>__*` method stubs, so `apply_inheritance` can monomorphize the
    base's methods onto the subclass (giving an inherited-method call its
    postcondition at the call site).
    """
    added: Set[str] = set()
    type_decls = ir_data.get("type_decls", [])
    existing_types = {td.get("name") for td in type_decls}
    existing_funcs = {f["name"] for f in ir_data["functions"]}
    needed = {b for td in type_decls for b in td.get("bases", [])
              if b not in existing_types}
    if not needed:
        return added

    for local, orig, module_path, level in module_imports:
        if not needed:
            break
        resolved = _resolve_module_path(module_path, level, main_file)
        if resolved is None:
            continue
        _process_dependency(resolved, [], cache, deep=deep,
                            processing_set=processing_set)
        dep_ir = cache.get(os.path.abspath(resolved))
        if not dep_ir:
            continue
        dep_types = {td.get("name"): td for td in dep_ir.get("type_decls", [])}
        dep_funcs = {f["name"]: f for f in dep_ir.get("functions", [])}
        for bname in list(needed):
            if bname not in dep_types:
                continue
            ir_data.setdefault("type_decls", []).append(dict(dep_types[bname]))
            existing_types.add(bname)
            needed.discard(bname)
            added.add(bname)
            prefix = f"{bname.lower()}__"
            injected = 0
            for fname, f in dep_funcs.items():
                if fname.startswith(prefix) and fname not in existing_funcs:
                    mf = dict(f)
                    mf["trusted"] = True
                    ir_data["functions"].insert(0, mf)
                    existing_funcs.add(fname)
                    injected += 1
            print(f"[*] Imported base class from '{module_path}': {bname} "
                  f"(record + {injected} method stub(s))")
    return added


def apply_inheritance(ir_data: Dict[str, Any]) -> None:
    """Layers B+C — merge each subclass's base(s) into it at the IR level.

    Runs AFTER import resolution, so same-file AND imported bases are present.
    For each record `type_decl` carrying `bases`, merge the base's fields
    (union; subclass wins on name collision), class invariants (conjunction),
    field defaults and constants (union), and monomorphize the base's methods
    onto the subclass (clone the method IR, rename `<sub>__m`, re-type `self`).
    A method body refers to its own state via the self-relative `self.x` /
    `self.m(...)` forms, so re-typing the clone is enough — they re-resolve
    against the subclass record. Idempotent (a merged `bases` list is cleared);
    base classes are merged before the subclasses that extend them.
    """
    type_decls = ir_data.get("type_decls", [])
    records = {td["name"]: td for td in type_decls if td.get("kind") == "record"}
    funcs = ir_data.setdefault("functions", [])

    def merge_one(td: Dict[str, Any]) -> None:
        if not td.get("bases"):
            return
        sub = td["name"]
        own_field_names = {f["name"] for f in td["fields"]}
        existing_func_names = {f.get("name") for f in funcs}
        prefix_sub = f"{sub.lower()}__"
        own_tails = {f["name"][len(prefix_sub):] for f in funcs
                     if f.get("name", "").startswith(prefix_sub)}
        merged_fields: List[Dict[str, Any]] = []
        seen: Set[str] = set()
        merged_invs: List[Dict[str, Any]] = []
        merged_defaults: Dict[str, Any] = {}
        merged_consts: Dict[str, Any] = {}
        for bname in td["bases"]:
            base = records.get(bname)
            if base is None:
                continue
            if base.get("bases"):
                merge_one(base)  # resolve the chain first
            for f in base["fields"]:
                if f["name"] not in seen and f["name"] not in own_field_names:
                    merged_fields.append(f)
                    seen.add(f["name"])
            merged_invs += base.get("class_invariants", [])
            merged_defaults.update(base.get("field_defaults", {}))
            merged_consts.update(base.get("constants", {}))
            prefix_base = f"{bname.lower()}__"
            for fn in list(funcs):
                name = fn.get("name", "")
                if not name.startswith(prefix_base):
                    continue
                tail = name[len(prefix_base):]
                new_name = f"{sub.lower()}__{tail}"
                if tail in own_tails:
                    # Subclass overrides this base method — record the pair so
                    # `--check-behavioral-subtyping` can emit a Liskov goal.
                    ir_data.setdefault("overrides", []).append({
                        "sub_method": new_name, "base_method": name,
                        "sub_type": sub.lower(), "base_type": bname.lower(),
                    })
                    continue
                if new_name in existing_func_names:
                    continue
                clone = copy.deepcopy(fn)
                clone["name"] = new_name
                clone["self_type"] = sub
                funcs.append(clone)
                existing_func_names.add(new_name)
                own_tails.add(tail)
        td["fields"] = merged_fields + td["fields"]
        td["class_invariants"] = merged_invs + td.get("class_invariants", [])
        td["field_defaults"] = {**merged_defaults, **td.get("field_defaults", {})}
        td["constants"] = {**merged_consts, **td.get("constants", {})}
        td["bases"] = []  # mark merged

    for td in list(records.values()):
        merge_one(td)


def apply_composition(ir_data: Dict[str, Any]) -> None:
    """Tier-1 mixin composition (mixin.md / mixin-ready.md) — an IR→IR pass after
    inheritance. For each `#@ compose_from M1, M2, …` class it (1) CHECKS the
    composition is sound and (2) FLATTENS the composed mixins' provided methods into
    the composer so its own methods can call them.

    Checks (each a hard PyCSLSemanticError, with teeth — the negative drivers stay
    failing):
      • unique provider — every mixin `depends_method`/`requires_method` must have
        EXACTLY one provider among the composed mixins (0 → missing; ≥2 → unresolved
        collision, Tier-2 `#@ resolve` not implemented).
      • field classification (D1) — a mixin method may write a `self.<f>` only if `f`
        is declared `#@ shared_state`/`#@ touches_field` or is one of the mixin's own
        __init__ fields.

    Flatten: clone each provided method `<mixin>__m → <composer>__m` (retype self), so
    a `self.<m>(…)` in the composer resolves to the concrete provider's contract (which
    each mixin was already verified once against in isolation, S1). The provider⊑
    dependency refinement goal is S2b.
    """
    from errors import PyCSLSemanticError
    compositions = ir_data.get("compositions") or []
    if not compositions:
        return
    type_decls = ir_data.get("type_decls", [])
    records = {td["name"]: td for td in type_decls if td.get("kind") == "record"}
    funcs = ir_data.setdefault("functions", [])

    def self_field_writes(body: Any) -> Set[str]:
        written: Set[str] = set()
        def walk(n: Any) -> None:
            if isinstance(n, dict):
                if (n.get("stmt") in ("FieldAssign", "FieldAugAssign")
                        and n.get("object") == "self"):
                    written.add(n.get("field"))
                for v in n.values():
                    walk(v)
            elif isinstance(n, list):
                for x in n:
                    walk(x)
        walk(body)
        return written

    for comp in compositions:
        C = comp["composer"]; c = C.lower()
        mixin_names = comp["mixins"]
        mixin_funcs = {M: [f for f in funcs if f.get("name", "").startswith(M.lower() + "__")]
                       for M in mixin_names}
        # gather providers (method -> [(mixin, func)]) and dependencies
        providers: Dict[str, List[Any]] = {}
        deps: List[Any] = []
        for M in mixin_names:
            for f in mixin_funcs[M]:
                for pm in f.get("provides", []):
                    providers.setdefault(pm, []).append((M, f))
                for d in f.get("method_deps", []):
                    deps.append((M, d))
        # --- check: unique provider per dependency ---
        for M, d in deps:
            n = len(providers.get(d["method"], []))
            if n == 0:
                raise PyCSLSemanticError(
                    f"Mixin composition '{C}': dependency '{d['method']}' (declared by "
                    f"mixin '{M}' via #@ {d['kind']}_method) has NO provider among the "
                    f"composed mixins {mixin_names}. Every dependency needs exactly one "
                    f"provider — add a mixin that `#@ provides {d['method']}`.")
        for pm, provs in providers.items():
            if len(provs) > 1:
                owners = ", ".join(M for M, _ in provs)
                raise PyCSLSemanticError(
                    f"Mixin composition '{C}': method '{pm}' is provided by more than one "
                    f"mixin ({owners}) — an unresolved collision. Resolve it with "
                    f"`#@ resolve {pm} from <Mixin>` (Tier 2); composition never silently "
                    f"picks a provider.")
        # --- check: field classification (no undeclared self writes) ---
        for M in mixin_names:
            declared: Set[str] = set()
            for f in mixin_funcs[M]:
                declared |= {s["name"] for s in f.get("shared_state", [])}
                declared |= {s["name"] for s in f.get("touches_field", [])}
            declared |= {fld["name"] for fld in records.get(M, {}).get("fields", [])}
            for f in mixin_funcs[M]:
                for fld in self_field_writes(f.get("body", [])):
                    if fld not in declared:
                        raise PyCSLSemanticError(
                            f"Mixin '{M}' (composed into '{C}'): a method writes "
                            f"`self.{fld}`, a field declared neither `#@ shared_state` nor "
                            f"`#@ touches_field` nor initialised in __init__. Declare every "
                            f"field a mixin touches so composition can reason about it.")
        # --- flatten: clone provided methods into the composer ---
        existing = {f.get("name") for f in funcs}
        own_tails = {f["name"][len(c) + 2:] for f in funcs
                     if f.get("name", "").startswith(c + "__")}
        for M in mixin_names:
            m = M.lower()
            for f in mixin_funcs[M]:
                if not f.get("provides"):
                    continue
                tail = f["name"][len(m) + 2:]
                new_name = f"{c}__{tail}"
                if tail in own_tails or new_name in existing:
                    continue   # composer overrides it, or already cloned
                clone = copy.deepcopy(f)
                clone["name"] = new_name
                clone["self_type"] = C
                clone["provides"] = []   # the clone is the concrete impl, not a re-provider
                funcs.append(clone)
                existing.add(new_name)
                own_tails.add(tail)
                # Record the flattened provider so Module 6 resolves a `self.<tail>()`
                # call inside the composer to the CONCRETE `<composer>__<tail> self`
                # (carrying the provider's full state-mutating contract) rather than an
                # abstract `val` (which drops self + self-field ensures). A sibling
                # mixin's own isolation method (`<mixin>__<tail>`) is NOT in this set, so
                # it keeps resolving its genuine dependency to the abstract `val`.
                ir_data.setdefault("composed_provider_methods", []).append(new_name)


def resolve_imports(validated_ast: _ast.AST, main_file: str, ir_data: Dict[str, Any],
                    deep: bool = False, cache: Optional[Dict[str, Any]] = None,
                    processing_set: Optional[Set[str]] = None) -> Set[str]:
    """Detect imports, resolve source files, inject trusted stubs into ir_data.
    Returns set of imported function local names.

    refactor.md Phase C (C1): the import list for THIS module now comes from the
    IR field `ir_data["imports"]` (emitted by Module5.visit_Module), not from a
    fresh walk of the Python AST. Each entry is a 5-element list
    [local, original, module, level, is_module] — identical data and order to
    what `_extract_imports` produced — so the dependency-injection result stays
    byte-identical. (Dependency LOADING still runs M1–5 on the dep source; only
    the per-module import LIST is now IR-sourced.) `validated_ast` is retained in
    the signature for call-site compatibility but no longer consulted here.
    """
    imports = ir_data.get("imports", [])
    if not imports:
        return set()

    all_calls = set()
    for f in ir_data["functions"]:
        all_calls |= _collect_calls(f["body"])

    if cache is None:
        cache = {}
    if processing_set is None:
        processing_set = set()

    direct_imports = [(l, o, m, lv)
                      for l, o, m, lv, is_mod in imports
                      if not is_mod and l != '*']
    wildcard_imports = [(m, lv)
                        for l, o, m, lv, is_mod in imports
                        if l == '*']
    module_imports = [(l, o, m, lv)
                      for l, o, m, lv, is_mod in imports if is_mod]

    imported_names = set()
    # Layer A: imported CLASSES (records + method stubs) — run first so a
    # later function-stub pass doesn't mis-handle a class name as a function.
    imported_names |= _resolve_imported_classes(
        direct_imports, main_file, ir_data, deep, cache, processing_set)
    imported_names |= _resolve_direct_imports(
        direct_imports, all_calls, main_file, ir_data, deep, cache, processing_set)
    imported_names |= _resolve_wildcard_imports(
        wildcard_imports, all_calls, main_file, ir_data, deep, cache, processing_set)
    imported_names |= _resolve_module_imports(
        module_imports, all_calls, main_file, ir_data, deep, cache, processing_set)
    # Layer A′: subclass bases referenced via a module import (`import ast` +
    # `class X(ast.NodeVisitor)`) — inject the base record + methods so the
    # later `apply_inheritance` pass can monomorphize them onto the subclass.
    imported_names |= _resolve_imported_base_classes(
        module_imports, main_file, ir_data, deep, cache, processing_set)
    # py-expr-structural-dep-wall-response.md piece 3: cross-file dotted pure_ast
    # node param resolution (`expr: ast.BinOp`). Disjoint from the verified
    # `cache` above (its own `struct_cache`, structural-only — see piece 1/2);
    # no-op unless a `pure_ast`-alias import AND a matching dotted param
    # annotation are both present (corpus-inert for every other driver).
    _resolve_pure_ast_param_records(validated_ast, main_file, ir_data, {})
    return imported_names


def resolve(ir_data: Dict[str, Any], validated_ast: _ast.AST, main_file: str,
            deep: bool = False, import_paths: Optional[List[str]] = None) -> Set[str]:
    """Run the four post-Module5 IR-resolution passes IN ORDER, in place on
    `ir_data`, and return the set of imported function local names.

    Order (must match the orchestrator's historical inline sequence):
      1. resolve_imports  → 2. apply_inheritance  → 3. apply_composition
      → 4. apply_inline_globals  → 5. apply_monomorphization (typing TY3)

    `import_paths` (CLI `--import-path`, b1-plan.md) are extra roots searched by
    `_resolve_module_path` after the built-in ones — opt-in, default unchanged.
    """
    global _EXTRA_IMPORT_PATHS
    _EXTRA_IMPORT_PATHS = [os.path.abspath(p) for p in (import_paths or [])]
    imported_names = resolve_imports(validated_ast, main_file, ir_data, deep=deep)
    apply_inheritance(ir_data)
    apply_composition(ir_data)
    apply_inline_globals(ir_data)
    # typing-engagement ty3 / 33-1700-typing-spec-9: whole-module monomorphization
    # of PEP 484/695 generics (COLLECT concrete instantiations → EMIT name-mangled
    # specialized copies with substituted contracts; GT3/GT4 loud-fails). No-op
    # (early return) when no type_decl/function carries `type_params` →
    # byte-identical for every non-generic module (total additivity). COLLECT scans
    # the AST (module-level instantiation sites live in `if __name__ == ...` blocks
    # that are NOT in the IR functions list) AND the IR (annotation subscripts).
    from frontend.monomorphize import apply_monomorphization
    apply_monomorphization(ir_data, validated_ast)
    return imported_names
