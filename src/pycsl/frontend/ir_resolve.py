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

# PYTHON-AST NODE CTOR FAMILY (`_fin` recognizer vein, increment 9) — THE SUM TYPE.
#
# wall-lessons (zz) measured that 34 of the 42 still-`\trusted` `_fin`-gated `_Parser`
# methods have a PASSTHROUGH return (`return x` beside `return self._fin(_N("Await")(
# value=x), t)`), which a PER-CLASS WhyML record can never type — the two returns have
# different types, so the function has no WhyML type at all. The sum type those returns
# need already exists: it is `emit_ir`, and the `-> "ExprIR"` RETURN INTERFACE already
# gives every un-converted sibling exactly that type at zero marker cost. What was
# missing is the other half — a FAITHFUL CONSTRUCTOR for the node the method builds.
#
# This table is that half: pure_ast node class -> (`emit_ir` constructor, payload in
# ASDL FIELD ORDER as (field name, WhyML payload type)). It is the SINGLE SOURCE for
#   * `module6_whyml/preamble.py::_emit_exprir_theory` — the ADT arms,
#   * `module6_whyml/expressions.py::_call_irnode_constructor` — the BY-NAME binding
#     (an unbound payload slot DECLINES, so a dropped/reordered child is impossible),
#   * the `wanted` harvest below — a class that is only ever CONSTRUCTED (never named in
#     an annotation) still needs its `_PURE_AST_FIELD_TABLE` entry harvested, because
#     that entry is what supplies `init_params` to the by-name binding.
# Every member needs a `_PURE_AST_FIELD_TABLE` entry whose field names match
# `_NODE_SPEC`'s, and the whole family is gated OUT of every other file by
# `preamble._uses_pyast_parser` (the file defines `_Parser._fin`).
_PYAST_IRNODE_CTORS: Dict[str, Tuple[str, List[Tuple[str, str]]]] = {
    # `Await(value)` — `_NODE_SPEC['Await'] == ('expr', ('value',), <loc attrs>)`, ONE
    # total child (no `_OPTIONAL_FIELDS` entry): the awaited expression.
    "Await": ("IrPyAwait", [("value", "emit_ir")]),
    # `Constant(value, kind)` — `_NODE_SPEC['Constant'] == ('expr', ('value','kind'),
    # None)` with `kind` in `_OPTIONAL_FIELDS['Constant']` (only a legacy `u""` literal
    # carries one). `value` is the ONE field that is NOT a node and NOT a string: Python
    # models EVERY literal with this class, so the slot is the bespoke `irconst` value
    # carrier rather than a bare `string` — modelling a numeric or `None` literal as a
    # STRING would be exactly the read-the-wrong-thing erasure this family exists to
    # remove. `irconst` starts with the two shapes the converted sites actually build
    # (`ICStr` for a decoded f-string/segment literal, `ICNone` for a bare `None`); any
    # other value expression makes the construction DECLINE (fail-closed), which is what
    # keeps the number-literal sites (`_parse_number` -> int|float|complex) on their
    # recorded [MODEL] boundary instead of silently mis-modelling them.
    "Constant": ("IrPyConstant", [("value", "irconst"), ("kind", "iropt_str")]),
    # `JoinedStr(values)` — `_NODE_SPEC['JoinedStr'] == ('expr', ('values',), None)`, ONE
    # total child list: the alternating Constant / FormattedValue parts of an f-string.
    # An ordinary `irlist`, like every other variadic child list in the family.
    "JoinedStr": ("IrPyJoinedStr", [("values", "irlist")]),
    # `IfExp(test, body, orelse)` — `_NODE_SPEC['IfExp'] == ('expr', ('test','body',
    # 'orelse'), <loc attrs>)`, THREE total children (no `_OPTIONAL_FIELDS` entry). A
    # DEDICATED arm, not the generic `IrTer3`: an `IfExp` must stay distinguishable from
    # every other 3-child node.
    "IfExp": ("IrPyIfExp", [("test", "emit_ir"), ("body", "emit_ir"),
                            ("orelse", "emit_ir")]),
    # `UnaryOp(op, operand)` — `_NODE_SPEC['UnaryOp'] == ('expr', ('op','operand'),
    # <loc attrs>)`, both total. `op` is a 0-field `unaryop` SINGLETON
    # (`_N("Not")()`), carried as its class-name `string` — the whole of its content.
    "UnaryOp": ("IrPyUnaryOp", [("op", "string"), ("operand", "emit_ir")]),
    # `Starred(value, ctx)` — `_NODE_SPEC['Starred'] == ('expr', ('value','ctx'),
    # <loc attrs>)`, both total. `ctx` is a 0-field `expr_context` SINGLETON
    # (`_N("Load")()`), carried as its class-name `string`. NOT the pre-existing
    # `IrStarred emit_ir`, which DROPS `ctx`.
    "Starred": ("IrPyStarred", [("value", "emit_ir"), ("ctx", "string")]),
    # `keyword(arg, value)` — `_NODE_SPEC['keyword'] == ('AST', ('arg','value'), <loc
    # attrs>)` and `arg` IS in `_OPTIONAL_FIELDS['keyword']`: a `**kwargs` splat really
    # carries NO name (`_N("keyword")(arg=None, value=v)` in `_call_args`), so the slot is
    # the monomorphic `iropt_str`, never a bare string that would model the absent name as
    # the empty one. `value` is the argument expression.
    "keyword": ("IrPyKeyword", [("arg", "iropt_str"), ("value", "emit_ir")]),
    # `Name(id, ctx)` — `_NODE_SPEC['Name'] == ('expr', ('id','ctx'), None)`, both total.
    # `id` is the identifier STRING the live body binds from a token; `ctx` a 0-field
    # `expr_context` singleton carried as its class-name string.
    "Name": ("IrPyName", [("id", "string"), ("ctx", "string")]),
    # `Attribute(value, attr, ctx)` — `_NODE_SPEC['Attribute'] == ('expr', ('value',
    # 'attr','ctx'), None)`, all total: the receiver NODE, the attribute-name string, and
    # the `expr_context` singleton. NOT the pre-existing `IrAttr emit_ir string`, which
    # has no `ctx` slot.
    "Attribute": ("IrPyAttribute", [("value", "emit_ir"), ("attr", "string"),
                                    ("ctx", "string")]),
    # `MatchAs(pattern, name)` — `_NODE_SPEC['MatchAs'] == ('pattern', ('pattern',
    # 'name'), None)`. BOTH fields are in `_OPTIONAL_FIELDS['MatchAs']` (a bare `_`
    # wildcard carries neither), but the `as`-pattern construction this arm serves
    # supplies BOTH, so the total shape is faithful THERE. A construction that passes
    # `None` leaves a payload slot unbound and `_call_irnode_constructor` DECLINES —
    # fail-closed, never a dropped child. An `iropt_ir`/`iropt_str` variant is the
    # reopening capability if a None-carrying MatchAs site is ever converted.
    "MatchAs": ("IrPyMatchAs", [("pattern", "emit_ir"), ("name", "string")]),
    # `BoolOp(op, values)` — `_NODE_SPEC['BoolOp'] == ('expr', ('op','values'),
    # <loc attrs>)`, both total. `op` is a 0-field `boolop` singleton carried as its
    # class-name string; `values` is the VARIADIC operand list, carried as the
    # monomorphic `irlist` cons-list (the same payload `IrMkTupleN`/`IrListN` use).
    "BoolOp": ("IrPyBoolOp", [("op", "string"), ("values", "irlist")]),
    # `MatchOr(patterns)` — `_NODE_SPEC['MatchOr'] == ('pattern', ('patterns',), None)`,
    # one total VARIADIC child list.
    "MatchOr": ("IrPyMatchOr", [("patterns", "irlist")]),
    # `Global(names)` / `Nonlocal(names)` — `_NODE_SPEC['Global'] == ('stmt',
    # ('names',), <loc attrs>)` and likewise for `Nonlocal`, ONE total child each (no
    # `_OPTIONAL_FIELDS` entry). `names` is a list of IDENTIFIER STRINGS, not of nodes,
    # so the slot is the `seq string` payload the `Compare.ops` arm introduced — never
    # `irlist`, which would model an identifier as a NODE. The two are the ONLY family
    # members whose payload field set is exactly `{"names"}`, which is what makes the
    # variable-class-name PARAMETER dispatch in `global_stmt` resolve to exactly this
    # pair.
    "Global": ("IrPyGlobal", [("names", "seq string")]),
    "Nonlocal": ("IrPyNonlocal", [("names", "seq string")]),
    # `Tuple(elts, ctx)` — `_NODE_SPEC['Tuple'] == ('expr', ('elts','ctx'), <loc attrs>)`,
    # both total: the VARIADIC element list and the `expr_context` singleton. NOT the
    # pre-existing `IrMkTupleN irlist`, which has no `ctx` slot.
    "Tuple": ("IrPyTuple", [("elts", "irlist"), ("ctx", "string")]),
    # `comprehension(target, iter, ifs, is_async)` — `_NODE_SPEC['comprehension'] ==
    # ('AST', ('target','iter','ifs','is_async'), ())`, all FOUR total (no
    # `_OPTIONAL_FIELDS` entry). Bringing it into the FAMILY (it was previously only a
    # HARVESTED RECORD) is what lets a comprehension list be an ordinary `irlist` child:
    # `emit_ir` cannot carry a `seq <record>` payload at all, because `comprehension`
    # holds `emit_ir` children and Why3 rejects the resulting `seq` recursion as
    # non-strictly-positive. `is_async` is the 0/1 flag the live `comp_for` body sets
    # literally. The record DECLARATION stays (the field table is untouched), and the ctor
    # table is consulted only under `_uses_pyast_parser`, so no other mirror moves.
    "comprehension": ("IrPyComprehension", [("target", "emit_ir"), ("iter", "emit_ir"),
                                            ("ifs", "irlist"), ("is_async", "int")]),
    # `GeneratorExp(elt, generators)` — `_NODE_SPEC['GeneratorExp'] == ('expr',
    # ('elt','generators'), <loc attrs>)`, both total: the yielded expression and the
    # VARIADIC list of `comprehension` clauses, now an ordinary `irlist` because
    # `comprehension` is a family member.
    "GeneratorExp": ("IrPyGeneratorExp", [("elt", "emit_ir"), ("generators", "irlist")]),
    # `List(elts, ctx)` — `_NODE_SPEC['List'] == ('expr', ('elts','ctx'), <loc attrs>)`,
    # both total: the VARIADIC element list and the `expr_context` 0-field singleton
    # carried as its class-name string. The direct sibling of `IrPyTuple`.
    "List": ("IrPyList", [("elts", "irlist"), ("ctx", "string")]),
    # `ListComp(elt, generators)` — `_NODE_SPEC['ListComp'] == ('expr',
    # ('elt','generators'), <loc attrs>)`, both total. Now that `comprehension` is a
    # family member the clause list is an ordinary `irlist`, exactly as for GeneratorExp.
    "ListComp": ("IrPyListComp", [("elt", "emit_ir"), ("generators", "irlist")]),
    # `Dict(keys, values)` — `_NODE_SPEC['Dict'] == ('expr', ('keys','values'), <loc
    # attrs>)`, both total. `keys` REALLY HOLDS `None` ELEMENTS (`{**a, 'k': v}` parses to
    # `keys=[None, 'k']`), so its slot is the OPTIONAL-element carrier `iroptlist`, never
    # an `irlist` — which would have to model the absent key as a NODE.
    "Dict": ("IrPyDict", [("keys", "iroptlist"), ("values", "irlist")]),
    "Set": ("IrPySet", [("elts", "irlist")]),
    "SetComp": ("IrPySetComp", [("elt", "emit_ir"), ("generators", "irlist")]),
    "DictComp": ("IrPyDictComp", [("key", "emit_ir"), ("value", "emit_ir"),
                                  ("generators", "irlist")]),
    # `Call(func, args, keywords)` — `_NODE_SPEC['Call'] == ('expr', ('func','args',
    # 'keywords'), None)`, all three total: the callee NODE and the two VARIADIC child
    # lists (positional args, `keyword` nodes), each carried as the monomorphic `irlist`.
    # NOT the pre-existing `IrCall`, which carries a NAME string and one list — it cannot
    # hold a computed callee expression, and it has no `keywords` slot at all.
    "Call": ("IrPyCall", [("func", "emit_ir"), ("args", "irlist"),
                          ("keywords", "irlist")]),
    # `ClassDef(name, bases, keywords, body, decorator_list, type_params)` —
    # `_NODE_SPEC['ClassDef'] == ('stmt', ('name','bases','keywords','body',
    # 'decorator_list','type_params'), None)`, all SIX total (no `_OPTIONAL_FIELDS`
    # entry): the class-name string plus five VARIADIC child lists. The direct sibling
    # of `IrPyFunctionDef`, minus the signature/returns slots a class has no room for.
    "ClassDef": ("IrPyClassDef", [("name", "string"), ("bases", "irlist"),
                                  ("keywords", "irlist"), ("body", "irlist"),
                                  ("decorator_list", "irlist"),
                                  ("type_params", "irlist")]),
    # `Subscript(value, slice, ctx)` — `_NODE_SPEC['Subscript'] == ('expr', ('value',
    # 'slice','ctx'), None)`, all three total: the subscripted NODE, the index/slice
    # NODE, and the `expr_context` 0-field singleton carried as its class-name string.
    # NOT the pre-existing `IrIndex emit_ir emit_ir`, which DROPS `ctx`.
    "Subscript": ("IrPySubscript", [("value", "emit_ir"), ("slice", "emit_ir"),
                                    ("ctx", "string")]),
    # `Yield(value)` — `_NODE_SPEC['Yield'] == ('expr', ('value',), None)` and `value` IS
    # in `_OPTIONAL_FIELDS['Yield']` (a bare `yield` really carries nothing), so the slot
    # is the monomorphic `iropt_ir`, never a bare emit_ir that would model the absent
    # value as a NODE.
    "Yield": ("IrPyYield", [("value", "iropt_ir")]),
    # `YieldFrom(value)` — `_NODE_SPEC['YieldFrom'] == ('expr', ('value',), None)` and it
    # is NOT in `_OPTIONAL_FIELDS`: `yield from` always has an operand.
    "YieldFrom": ("IrPyYieldFrom", [("value", "emit_ir")]),
    # `BinOp(left, op, right)` — `_NODE_SPEC['BinOp'] == ('expr', ('left','op','right'),
    # <loc attrs>)`, all total. `op` is a 0-field `operator` singleton carried as its
    # class-name string. NOT the pre-existing `IrBinOp string emit_ir emit_ir`, whose
    # payload ORDER is (op, left, right) — the CSL spelling — while the ASDL field order
    # is (left, op, right); a separate arm keeps the by-name binding unambiguous and the
    # two ASTs' BinOps distinguishable.
    "BinOp": ("IrPyBinOp", [("left", "emit_ir"), ("op", "string"),
                            ("right", "emit_ir")]),
    # THE STATEMENT CLUSTER. `If(test, body, orelse)` / `While(test, body, orelse)` —
    # `_NODE_SPEC` gives both `('stmt', ('test','body','orelse'), None)`, all total. The
    # two SUB-BODIES are lists of STATEMENT nodes, which under this family are `emit_ir`
    # exactly like expression nodes, so they ride the same `irlist` variadic payload as
    # `BoolOp.values`. This is the first place the model carries a compound statement's
    # real sub-bodies instead of the opaque `array int` the "StmtIRList" record tag gives.
    "If": ("IrPyIf", [("test", "emit_ir"), ("body", "irlist"),
                      ("orelse", "irlist")]),
    "While": ("IrPyWhile", [("test", "emit_ir"), ("body", "irlist"),
                            ("orelse", "irlist")]),
    # `Module(body, type_ignores)` — `_NODE_SPEC['Module'] == ('mod', ('body',
    # 'type_ignores'), ())`, both total VARIADIC child lists. The parser's own top-level
    # result: `body` is the real statement list the file parsed to, `type_ignores` is
    # ALWAYS the empty list at this site (the parser never produces a `# type: ignore`
    # record), which the `irlist` slot now carries as the genuinely empty `ILNil` rather
    # than declining.
    "Module": ("IrPyModule", [("body", "irlist"), ("type_ignores", "irlist")]),
    # `match_case(pattern, guard, body)` — `_NODE_SPEC['match_case'] == ('match_case',
    # ('pattern','guard','body'), None)`; `guard` IS in `_OPTIONAL_FIELDS` (a `case p:`
    # with no `if` really carries nothing), so it is the monomorphic `iropt_ir`, never a
    # bare emit_ir that would model the absent guard as a NODE. `body` is the case's
    # statement list.
    "match_case": ("IrPyMatchCase", [("pattern", "emit_ir"), ("guard", "iropt_ir"),
                                     ("body", "irlist")]),
    # `Match(subject, cases)` — `_NODE_SPEC['Match'] == ('stmt', ('subject','cases'),
    # None)`, both total: the subject expression and the VARIADIC list of `match_case`
    # nodes, which under this family are `emit_ir` like every other node.
    "Match": ("IrPyMatch", [("subject", "emit_ir"), ("cases", "irlist")]),
    # `MatchStar(name)` — `_NODE_SPEC['MatchStar'] == ('pattern', ('name',), None)`, one
    # field, and it IS in `_OPTIONAL_FIELDS['MatchStar']`: a bare `*_` really carries NO
    # name. The slot is therefore the monomorphic `iropt_str`, never a plain `string` —
    # which would model the anonymous star as a capture NAMED `""` (lesson (aq)'s exact
    # erasure).
    "MatchStar": ("IrPyMatchStar", [("name", "iropt_str")]),
    # `MatchSequence(patterns)` — `_NODE_SPEC['MatchSequence'] == ('pattern',
    # ('patterns',), None)`, one total VARIADIC child list, carried as `irlist` exactly
    # like `MatchOr.patterns`.
    "MatchSequence": ("IrPyMatchSequence", [("patterns", "irlist")]),
    # `ExceptHandler(type, name, body)` — `_NODE_SPEC['ExceptHandler'] ==
    # ('excepthandler', ('type','name','body'), None)`, and `_OPTIONAL_FIELDS
    # ['ExceptHandler'] == ('type','name')`: a bare `except:` carries NO exception type
    # and an `except E:` without `as` carries NO bind name. Both slots are therefore the
    # monomorphic options (`iropt_ir` for the type EXPRESSION, `iropt_str` for the bind
    # name); `body` is the handler's statement list.
    "ExceptHandler": ("IrPyExceptHandler", [("type", "iropt_ir"),
                                            ("name", "iropt_str"),
                                            ("body", "irlist")]),
    # `Try(body, handlers, orelse, finalbody)` / `TryStar(...)` — `_NODE_SPEC` gives both
    # `('stmt', ('body','handlers','orelse','finalbody'), None)`, all four total VARIADIC
    # child lists (an absent `else:`/`finally:` is the EMPTY list, not a missing field).
    # The two classes are DISTINCT arms, not a flag: `try` and `try*` have different
    # semantics, and the source picks between them with `cls = "TryStar" if is_star else
    # "Try"` — the CLASS-NAME TERNARY the recognizer resolves to these two ctors.
    "Try": ("IrPyTry", [("body", "irlist"), ("handlers", "irlist"),
                        ("orelse", "irlist"), ("finalbody", "irlist")]),
    "TryStar": ("IrPyTryStar", [("body", "irlist"), ("handlers", "irlist"),
                                ("orelse", "irlist"), ("finalbody", "irlist")]),
    # `For(target, iter, body, orelse, type_comment)` / `AsyncFor(...)` — `_NODE_SPEC`
    # gives both `('stmt', ('target','iter','body','orelse','type_comment'), None)`, and
    # `_OPTIONAL_FIELDS` marks ONLY `type_comment` (a `# type:` comment, which this parser
    # never produces) — hence the `iropt_str` slot, which the construction fills with the
    # honest `IrSNone`. `target`/`iter` are single expression children; `body`/`orelse`
    # are statement lists (`orelse` is EMPTY when there is no `else:`, not absent). Two
    # DISTINCT arms, chosen by the source's own `cls = "AsyncFor" if async_ else "For"`.
    "For": ("IrPyFor", [("target", "emit_ir"), ("iter", "emit_ir"),
                        ("body", "irlist"), ("orelse", "irlist"),
                        ("type_comment", "iropt_str")]),
    "AsyncFor": ("IrPyAsyncFor", [("target", "emit_ir"), ("iter", "emit_ir"),
                                  ("body", "irlist"), ("orelse", "irlist"),
                                  ("type_comment", "iropt_str")]),
    # `With(items, body, type_comment)` / `AsyncWith(...)` — `_NODE_SPEC` gives both
    # `('stmt', ('items','body','type_comment'), None)`, `_OPTIONAL_FIELDS` marks only
    # `type_comment`. `items` is the VARIADIC list of `withitem` NODES, which under this
    # family are `emit_ir` like every other node.
    "With": ("IrPyWith", [("items", "irlist"), ("body", "irlist"),
                          ("type_comment", "iropt_str")]),
    "AsyncWith": ("IrPyAsyncWith", [("items", "irlist"), ("body", "irlist"),
                                    ("type_comment", "iropt_str")]),
    # `FunctionDef(name, args, body, decorator_list, returns, type_comment, type_params)`
    # / `AsyncFunctionDef(...)` — `_NODE_SPEC` gives both seven TOTAL fields, and
    # `_OPTIONAL_FIELDS` marks `returns` and `type_comment`: a `def f():` with no `->`
    # really carries NO return annotation. `name` is the identifier STRING; `args` is the
    # single `arguments` node; `body`/`decorator_list`/`type_params` are child lists.
    # Two DISTINCT arms, chosen by the source's own
    # `cls = "AsyncFunctionDef" if async_ else "FunctionDef"`.
    "FunctionDef": ("IrPyFunctionDef", [("name", "string"), ("args", "emit_ir"),
                                        ("body", "irlist"),
                                        ("decorator_list", "irlist"),
                                        ("returns", "iropt_ir"),
                                        ("type_comment", "iropt_str"),
                                        ("type_params", "irlist")]),
    # `TypeAlias(name, type_params, value)` — `_NODE_SPEC['TypeAlias'] == ('stmt',
    # ('name','type_params','value'), None)`, all three TOTAL (no `_OPTIONAL_FIELDS`
    # entry). `name` is an expression NODE (a `Name`, or a `Subscript` for a generic
    # name), `type_params` the PEP-695 binder list, `value` the aliased expression.
    # `arguments(posonlyargs, args, vararg, kwonlyargs, kw_defaults, kwarg, defaults)` —
    # `_NODE_SPEC['arguments']` gives all seven, and `_OPTIONAL_FIELDS['arguments'] ==
    # ('vararg','kwarg')`: a signature without `*a` / `**kw` really carries neither, so
    # those two are the monomorphic `iropt_ir` (each is an `arg` NODE) and the other five
    # are child lists. `kw_defaults` genuinely contains `None` HOLES in CPython; this
    # parser's `lambdef` no-parameter site passes the EMPTY list for it, which the
    # `irlist` slot carries as the honest `ILNil`.
    "arguments": ("IrPyArguments", [("posonlyargs", "irlist"), ("args", "irlist"),
                                    ("vararg", "iropt_ir"),
                                    ("kwonlyargs", "irlist"),
                                    ("kw_defaults", "irlist"),
                                    ("kwarg", "iropt_ir"),
                                    ("defaults", "irlist")]),
    # `Compare(left, ops, comparators)` — `_NODE_SPEC['Compare'] == ('expr',
    # ('left','ops','comparators'), None)`, all three total. `ops` is a list of 0-FIELD
    # `cmpop` SINGLETONS (`_N("NotIn")()`), each carried as its class-name STRING (the
    # increment-10 rule), so the slot is a pure `seq string` — legal inside the
    # mutable-free emit_ir group (the `IrComposeFromDecl (seq string)` precedent), and no
    # new ADT is needed. `comparators` is the expression list.
    "Compare": ("IrPyCompare", [("left", "emit_ir"), ("ops", "seq string"),
                                ("comparators", "irlist")]),
    # `Lambda(args, body)` — `_NODE_SPEC['Lambda'] == ('expr', ('args','body'), None)`,
    # both total: the `arguments` node and the body expression.
    "Lambda": ("IrPyLambda", [("args", "emit_ir"), ("body", "emit_ir")]),
    # The PEP-695 `type_param` family, all three read straight off `_NODE_SPEC`:
    # `'TypeVar': ('type_param', ('name','bound'), None)`,
    # `'TypeVarTuple': ('type_param', ('name',), None)`,
    # `'ParamSpec': ('type_param', ('name',), None)`.
    # `name` is the identifier STRING `_name_str` returns. `TypeVar.bound` is in
    # `_OPTIONAL_FIELDS` — `type X[T] = ...` has no bound and `type X[T: int] = ...` does —
    # so its slot is `iropt_ir`, a TRUE `IrONone` on the unbounded path rather than a node
    # standing in for an absent one. `TypeVarTuple` and `ParamSpec` carry only the name,
    # which is the whole of their content.
    "TypeVar": ("IrPyTypeVar", [("name", "string"), ("bound", "iropt_ir")]),
    "TypeVarTuple": ("IrPyTypeVarTuple", [("name", "string")]),
    "ParamSpec": ("IrPyParamSpec", [("name", "string")]),
    "TypeAlias": ("IrPyTypeAlias", [("name", "emit_ir"),
                                    ("type_params", "irlist"),
                                    ("value", "emit_ir")]),
    "AsyncFunctionDef": ("IrPyAsyncFunctionDef",
                         [("name", "string"), ("args", "emit_ir"),
                          ("body", "irlist"), ("decorator_list", "irlist"),
                          ("returns", "iropt_ir"), ("type_comment", "iropt_str"),
                          ("type_params", "irlist")]),
}


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
    # CLASS-BY-NAME FACTORY vein: `Expression` is the `mod` wrapper `ast.parse(mode=
    # "eval")` returns — ONE total field (`_NODE_SPEC['Expression'] == ('mod',
    # ('body',), ())`, no `_OPTIONAL_FIELDS` entry), the expression tree itself, so it
    # is tagged "ExprIR" exactly like BinOp's children.
    "Expression": [("body", "ExprIR")],
    # `_fin` RECOGNIZER vein: `arg` is the ASDL parameter node —
    # `_NODE_SPEC['arg'] == ('AST', ('arg','annotation','type_comment'), <location attrs>)`,
    # and `_OPTIONAL_FIELDS['arg'] == ('annotation','type_comment')`, so the LAST TWO are
    # optionals ("OptExprIR" -> `option emit_ir`, "OptStr" -> `option string`) and the first
    # is the parameter NAME, a real string (`_lambda_arg` binds it from `_name_str`).
    "arg": [("arg", "string"), ("annotation", "OptExprIR"), ("type_comment", "OptStr")],
    # CLASS-BY-NAME FACTORY vein: `comprehension` is the `for`-clause of a comp/genexp —
    # `_NODE_SPEC['comprehension'] == ('AST', ('target','iter','ifs','is_async'), ())`, four
    # TOTAL fields (no `_OPTIONAL_FIELDS` entry). `target`/`iter` are expr children;
    # `ifs` is a LIST of expr children (the "ExprIRList" tag -> `array emit_ir`);
    # `is_async` is the 0/1 flag the live `comp_for` body sets literally.
    "comprehension": [("target", "ExprIR"), ("iter", "ExprIR"),
                      ("ifs", "ExprIRList"), ("is_async", "int")],
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
    # output-side slice-discrimination (self-tcb-reduction M5): Subscript's 3 fields
    # (`value`, `slice`, `ctx`) are total (no `_OPTIONAL_FIELDS` entry). `value` and
    # `slice` tagged "ExprIR" (both `self._py_expr_to_ir(...)`-lowered sub-nodes), `ctx`
    # "int" (the expr_context leaf, opaque). Feeds `_py_expr_subscript`, whose input-side
    # `isinstance(node.slice, ast.Slice)` test was rewritten to the SOUND output-side form
    # `self._py_expr_to_ir(expr.slice).get("type") == "Slice"`: the `slice_ir` local is
    # recognized as an emit_ir node (statements.py `_collect_emit_ir_result_locals`, the
    # emit_ir-returning-call recognizer types it "ExprIR"), and `.get("type") == "Slice"`
    # lowers (expressions.py `_emit_ir_kind_discriminant` + `_KIND_DISCRIMINANT["Slice"]`)
    # to the constructor discriminant `(is_slice slice_ir)`. Returns distinct real ctors —
    # `IrSliceAccess` (`_IRNODE_CTORS["SliceAccess"]`) vs `IrSub` (`_IRNODE_CTORS["Subscript"]`).
    "Subscript": [("value", "ExprIR"), ("slice", "ExprIR"), ("ctx", "int")],
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
    # CLASS-BY-NAME FACTORY vein (self-tcb-reduction, relaunch #4): `alias` is the first
    # ALL-LEAF `_NODE_SPEC` node harvested — `name` a plain string, `asname` an
    # `Optional[str]` (`_OPTIONAL_FIELDS['alias'] = ('asname',)`, pure_ast.py). It is the
    # target of `_N("alias")(name=…, asname=…)` in `_import_as_name` / `_dotted_as_name`,
    # which Module5 now resolves to a direct `alias(…)` construction, so the ordinary
    # record-literal path builds it. The "OptStr" tag is the string twin of "OptExprIR":
    # `{"type":"option","value_type":"string"}` -> `option string` (preamble.py already
    # emits that shape for `Optional[str]` record fields), collapsing to `int` off
    # @mutable_state so the corpus is byte-inert.
    "alias": [("name", "string"), ("asname", "OptStr")],
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
    # SAssign + str-Constant recognizer (self-tcb-reduction M5, C-bucket): the Expr
    # statement wrapper. `_NODE_SPEC['Expr'] = ('stmt', ('value',), None)`; its single
    # (mandatory, non-optional) field `value` is tagged "ExprIR" -> `emit_ir` (the
    # already-lowered expr child). This types `_py_stmt_expr(self, stmt: ast.Expr, …)`'s
    # `stmt` param as the `Expr` record, so the body's `self._py_expr_to_ir(stmt.value)`
    # reads `stmt.value : emit_ir` and the docstring-skip guard `isinstance(stmt.value,
    # ast.Constant) and isinstance(stmt.value.value, str)` collapses to the emit_ir
    # discriminant `(is_str stmt.value)` (module6_whyml/expressions.py
    # `_recognize_str_constant_guard`) — a string-literal Constant lowers to exactly
    # IrStr, so the two input-side isinstance tests agree with `is_str` on every real
    # node. Feeds the mutable-ref stmt-append convention (`ir_stmts := Seq.snoc !ir_stmts
    # (SExpr (py_expr_to_ir stmt.value))`), with the SExpr-suppressing early `return`
    # on the docstring branch lowered via `Return_void`.
    "Expr": [("value", "ExprIR")],
    # SAssign + str-Constant recognizer (self-tcb-reduction M5, C-bucket): the
    # AnnAssign (`x: T = v`) statement. `_NODE_SPEC['AnnAssign'] = ('stmt', ('target',
    # 'annotation', 'value', 'simple'), None)`; `value` is optional
    # (`_OPTIONAL_FIELDS['AnnAssign'] = ('value',)`), tagged "OptExprIR" -> `option
    # emit_ir` (the Return precedent). `target` tagged "ExprIR" -> `emit_ir` (a Name
    # node); the `annotation`/`simple` fields the live body never reads are tagged
    # opaque "int" (carried for record totality only, like For's dropped `target`/
    # `type_comment`). This types `_py_stmt_annassign`'s `stmt` param as the `AnnAssign`
    # record, so the body's guard `isinstance(stmt.target, ast.Name) and stmt.value is
    # not None` lowers to `(is_var stmt.target) && (is-Some stmt.value)` and the append
    # `{"stmt":"Assign","target":stmt.target.id,"value":self._py_expr_to_ir(stmt.value)}`
    # to `SAssign (name_of stmt.target) (py_expr_to_ir <unwrapped value>)` — the new
    # `SAssign string emit_ir` ctor. `stmt.target.id` -> `name_of` (the `.id` leaf
    # projection); the option value is unwrapped under the is-Some guard by
    # `_lower_stmt_ir_node`'s "str"/"expr"-with-opt-unwrap child kinds.
    "AnnAssign": [("target", "ExprIR"), ("annotation", "int"),
                  ("value", "OptExprIR"), ("simple", "int")],
    # SAssert increment (self-tcb-reduction M5, C-bucket): the `assert test, msg`
    # statement. `_NODE_SPEC['Assert'] = ('stmt', ('test', 'msg'), None)`; `msg` is
    # optional (`_OPTIONAL_FIELDS['Assert'] = ('msg',)`), tagged "OptExprIR" ->
    # `option emit_ir` (the Return/AnnAssign precedent). `test` tagged "ExprIR" ->
    # `emit_ir` (`self._py_expr_to_ir(stmt.test)`). This types `_py_stmt_assert`'s
    # `stmt` param as the `Assert` record so the build-up-then-append body
    # `ir_node = {"stmt":"Assert","test":..}; if stmt.msg and isinstance(stmt.msg,
    # Constant) and isinstance(stmt.msg.value, str): ir_node["msg"] = stmt.msg.value;
    # ir_stmts.append(ir_node)` lowers to `SAssert (py_expr_to_ir stmt.test)
    # <iropt_str>` — the new `SAssert emit_ir iropt_str` ctor. The msg option field
    # feeds the "assert_msg" child kind (expressions.py `_lower_stmt_ir_node`):
    # `match stmt.msg with Some _m -> (if is_str _m then IrSSome (value_of _m) else
    # IrSNone) | None -> IrSNone` — present-as-string-literal-Constant iff the guard
    # holds, faithful to the isinstance(Constant)+isinstance(str) test.
    "Assert": [("test", "ExprIR"), ("msg", "OptExprIR")],
    # `_fin` RECOGNIZER vein: `Raise` — `_NODE_SPEC['Raise'] == ('stmt', ('exc','cause'), ...)`
    # and BOTH fields are in `_OPTIONAL_FIELDS['Raise']`, so both are `option emit_ir`
    # ("OptExprIR"): a bare `raise` carries a TRUE `None` in each, and `raise E from C`
    # carries both nodes.
    "Raise": [("exc", "OptExprIR"), ("cause", "OptExprIR")],
    # `_fin` RECOGNIZER vein: `Import` — one TOTAL field, a LIST of `alias` nodes (the
    # "RecList:<Rec>" tag). `_NODE_SPEC['Import'] == ('stmt', ('names',), ...)`, no
    # `_OPTIONAL_FIELDS` entry.
    "Import": [("names", "RecList:alias")],
    # `_fin` RECOGNIZER vein, increment 8: `ImportFrom` — `_NODE_SPEC['ImportFrom'] ==
    # ('stmt', ('module','names','level'), None)`. `module` is in
    # `_OPTIONAL_FIELDS['ImportFrom']` and the live `import_from` body really leaves it
    # `None` for a bare `from . import x`, so it is "OptStr" (-> `option string`);
    # `names` is the same LIST-OF-`alias` shape `Import.names` has ("RecList:alias");
    # `level` is nominally optional in the factory but the ONLY construction site (this
    # parser) always passes the computed dot count, and CPython's own `ast.ImportFrom`
    # always carries an int there, so "int" is the faithful tag.
    "ImportFrom": [("module", "OptStr"), ("names", "RecList:alias"),
                   ("level", "int")],
    # SAugAssign/SFieldAugAssign/SArraySet increment (self-tcb-reduction M5, C-bucket):
    # the `x op= v` / `self.f op= v` / `c[k] op= v` augmented-assignment statement.
    # `_NODE_SPEC['AugAssign'] = ('stmt', ('target', 'op', 'value'), None)`; all three
    # fields are non-optional. `target` tagged "ExprIR" -> `emit_ir` (the assignment
    # target, an already-lowered Name/Attribute/Subscript node — the three
    # `isinstance(stmt.target, ast.Name/Attribute/Subscript)` dispatch guards lower to
    # `is_var`/`is_attribute`/`is_sub` via the isinstance-on-emit_ir recognizer). `op`
    # tagged "int" like BinOp's/UnaryOp's `op` (the opaque operator leaf `_py_op_to_str`
    # maps to a string). `value` tagged "ExprIR" -> `emit_ir` (`self._py_expr_to_ir(stmt.
    # value)`). This types `_py_stmt_augassign`'s `stmt` param as the `AugAssign` record so
    # the body's three-branch dispatch lowers to `SAugAssign (name_of stmt.target)
    # (py_op_to_str stmt.op) (py_expr_to_ir stmt.value)` (Name branch, `stmt.target.id` ->
    # `name_of`), `SFieldAugAssign (name_of stmt.target) (py_op_to_str stmt.op) (py_expr_to_ir
    # stmt.value)` (self-field branch, `stmt.target.attr` -> `name_of`, `stmt.target.value`
    # -> `avalue_of`, `== 'self'` -> `str_eq_op`), and `SArraySet (py_expr_to_ir (avalue_of
    # stmt.target)) <slice_ir> (IrBinOp ..)` (Subscript branch, `stmt.target.slice` ->
    # `sindex_of`, output-side `slice_ir.get("type") == "Slice"` guard).
    "AugAssign": [("target", "ExprIR"), ("op", "int"), ("value", "ExprIR")],
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
                elif ftype.startswith("RecList:"):
                    # `_fin` RECOGNIZER vein: a LIST-OF-HARVESTED-RECORD field (`Import.names`
                    # is a list of `alias`). Expands to `{"type":"list","value_type":"<Rec>"}`
                    # — the preamble record emitter maps `list` + a value_type naming a
                    # DECLARED RECORD to `array <record>` (the `List[_Tok]` precedent), so the
                    # field carries real records instead of the int-erased `array int`. The
                    # element record must itself be harvested, which the `wanted` set below
                    # arranges by naming it here.
                    fields.append({"name": fname, "type": "list",
                                   "value_type": ftype.split(":", 1)[1], "mutable": True})
                elif ftype == "OptStr":
                    # CLASS-BY-NAME FACTORY vein: the string twin of "OptExprIR" — an
                    # `Optional[str]` pure_ast field (`alias.asname`) expands to
                    # `{"type":"option","value_type":"string"}` -> `option string`.
                    fields.append({"name": fname, "type": "option",
                                   "value_type": "string", "mutable": True})
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
                # CLASS-BY-NAME FACTORY vein: synthesize the CONSTRUCTOR every harvested
                # node class actually has. `_build_nodes` gives each class the shared
                # `AST.__init__`, which binds positional args to `cls._fields` IN ORDER and
                # keyword args BY NAME (pure_ast.py:111) — so `init_params` = the field
                # names and `init_body` = "field f := param f" is an EXACT model of it, not
                # an approximation. Without it `_record_types[...]["init_params"]` is empty,
                # the WL-07 keyword binding in `expressions.py` has nothing to bind through,
                # and every constructed node collapses to its all-defaults witness
                # (measured: `alias(name=…, asname=…)` emitted `{ py_alias_name = 0;
                # py_alias_asname = 0 }`, discarding both arguments).
                "init_params": [fname for fname, _ in table_entry],
                "init_body": [{"field": fname,
                               "value": {"type": "Var", "name": fname}}
                              for fname, _ in table_entry],
                "init_ensures": [],
                "is_mixin": False, "compose_from": [],
            }
        break  # only one `_NODE_SPEC` assignment is ever expected
    return records


def _harvest_pyast_ctor_params(validated_ast: Any) -> Dict[str, List[str]]:
    """PYTHON-AST NODE CTOR FAMILY (increment 12): the positional `__init__` parameter
    order of each `_PYAST_IRNODE_CTORS` member, read STRUCTURALLY off the compiled file's
    own `_NODE_SPEC` field tuple.

    Every pure_ast node class gets the shared `AST.__init__`, which binds positional args
    to `cls._fields` IN ORDER and keyword args BY NAME — so the `_NODE_SPEC` field tuple
    IS `init_params`. Deriving it here (instead of from a `_PURE_AST_FIELD_TABLE` entry)
    is what keeps a family member from dragging a harvested RECORD into every OTHER
    mirror that mentions the same class: adding `BoolOp` to the field table retyped the
    `PEx_BoolOp` arm of Module5's `pyast_expr` ADT from its bespoke opaque node type to
    the harvested record while the handler's own signature stayed opaque — a byte diff
    that looked innocuous and was an L3-tc ERROR (wall-lessons (ww)).

    DRIFT CHECK, fail-closed: an entry is published ONLY when the ctor payload's field
    NAMES equal the `_NODE_SPEC` field tuple exactly, in order. A renamed, reordered,
    added or removed ASDL field therefore silently REMOVES the entry, the construction
    declines, and the whole conversion fails closed — never a mis-bound child."""
    out: Dict[str, List[str]] = {}
    for stmt in getattr(validated_ast, "body", []):
        if not (isinstance(stmt, _ast.Assign)
                and len(stmt.targets) == 1
                and isinstance(stmt.targets[0], _ast.Name)
                and stmt.targets[0].id == "_NODE_SPEC"
                and isinstance(stmt.value, _ast.Dict)):
            continue
        for k, v in zip(stmt.value.keys, stmt.value.values):
            if not (isinstance(k, _ast.Constant) and isinstance(k.value, str)):
                continue
            spec = _PYAST_IRNODE_CTORS.get(k.value)
            if spec is None:
                continue
            if not (isinstance(v, _ast.Tuple) and len(v.elts) >= 2
                    and isinstance(v.elts[1], _ast.Tuple)):
                continue
            fields = [e.value for e in v.elts[1].elts
                      if isinstance(e, _ast.Constant) and isinstance(e.value, str)]
            if fields != [fn for fn, _ty in spec[1]]:
                continue        # drift -> refuse, the construction declines
            out[k.value] = fields
        break   # only one `_NODE_SPEC` assignment is ever expected
    return out


def _harvest_node_spec_singletons(validated_ast: Any) -> List[str]:
    """PYTHON-AST NODE CTOR FAMILY (increment 10): the 0-FIELD ASDL node classes of the
    compiled file's OWN `_NODE_SPEC` — the ones whose field tuple is EMPTY
    (`'Load': ('expr_context', (), ())`, `'Not': ('unaryop', (), ())`, ...).

    Such a class carries NO information beyond its own IDENTITY: `_N("Load")()` is a
    constant, and every construction of it is interchangeable with every other. Its
    faithful WhyML model is therefore the class NAME as a `string` — nothing is erased —
    and that is the ONLY expressible model, because a 0-field WhyML record does not
    exist. Read structurally off the `_NODE_SPEC` dict literal (NOT off
    `_PURE_AST_FIELD_TABLE`, which lists only the classes with fields), so the set cannot
    drift from the source. Returns [] for a file with no `_NODE_SPEC`, which is every
    file but one."""
    out: List[str] = []
    for stmt in getattr(validated_ast, "body", []):
        if not (isinstance(stmt, _ast.Assign)
                and len(stmt.targets) == 1
                and isinstance(stmt.targets[0], _ast.Name)
                and stmt.targets[0].id == "_NODE_SPEC"
                and isinstance(stmt.value, _ast.Dict)):
            continue
        for k, v in zip(stmt.value.keys, stmt.value.values):
            if not (isinstance(k, _ast.Constant) and isinstance(k.value, str)):
                continue
            if not (isinstance(v, _ast.Tuple) and len(v.elts) >= 2
                    and isinstance(v.elts[1], _ast.Tuple)):
                continue
            if not v.elts[1].elts:            # EMPTY field tuple -> a singleton
                out.append(k.value)
        break   # only one `_NODE_SPEC` assignment is ever expected
    return sorted(out)


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


def _resolve_same_file_node_spec_records(validated_ast: Any,
                                         ir_data: Dict[str, Any]) -> None:
    """Piece 3b: SAME-FILE `_NODE_SPEC` harvest.

    `_harvest_node_spec_records` was only ever called for a DEPENDENCY
    (`_process_dependency_structural`), so when `pure_ast.py` itself is the file under
    verification its own ASDL table was never harvested — every node class it names was
    unavailable, and a `_N("alias")(…)` construction fell to a 0-ary opaque val
    (`py_alias_0 ()`, INPUT-BLIND) even after Module5 resolved the factory to a direct
    `alias(…)` call.

    Injects a harvested record ONLY when some function's PARAM or RETURN annotation names it
    (a bare `Name` or the quoted `Constant` form — `pure_ast.py` has no
    `from __future__ import annotations` and no `typing` import, so its annotations must be
    quoted to stay unevaluated). Injecting the whole 76-entry table unconditionally would
    re-emit the file for records nothing references.

    No-op unless the file itself defines `_NODE_SPEC` — only `pure_ast.py` does, so the
    reference corpus and every other mirror are byte-identical."""
    records = _harvest_node_spec_records(validated_ast)
    if not records:
        return
    wanted: Set[str] = set()

    def _ann_name(ann: Any) -> Optional[str]:
        if isinstance(ann, _ast.Name):
            return ann.id
        if isinstance(ann, _ast.Constant) and isinstance(ann.value, str):
            return ann.value
        return None

    def _ann_list_elem(ann: Any) -> Optional[str]:
        """LIST-OF-HARVESTED-RECORD return form: `List[R]` / `list[R]`, in the bare
        `Subscript` spelling or the QUOTED `"List[R]"` one (`pure_ast.py` must quote —
        it has no `typing` import, and lesson (ss) records that ADDING one silently
        REPLACES the `List`/`Set`/`Dict`/`Tuple` AST node classes this very module
        installs into its own globals, breaking the parser; the quoted form is the only
        safe spelling here). Returns `R` when it is a harvested `_NODE_SPEC` node class,
        else None."""
        node_ann = ann
        if isinstance(ann, _ast.Constant) and isinstance(ann.value, str):
            try:
                node_ann = _ast.parse(ann.value.strip(), mode="eval").body
            except SyntaxError:
                return None
        if not (isinstance(node_ann, _ast.Subscript)
                and isinstance(node_ann.value, _ast.Name)
                and node_ann.value.id in ("List", "list")):
            return None
        sl = node_ann.slice
        if isinstance(sl, getattr(_ast, "Index", ())):      # py<3.9 compat
            sl = sl.value
        if isinstance(sl, _ast.Name) and sl.id in records:
            return sl.id
        return None

    list_elems: Set[str] = set()
    func_by_name = {f["name"]: f for f in ir_data.get("functions", [])}
    for node in _ast.walk(validated_ast):
        if not isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
            continue
        rn = _ann_name(node.returns) if node.returns is not None else None
        if rn in records:
            wanted.add(rn)
        # `-> "List[R]"`: Module5 sees only an unrecognised string Constant, so the
        # return stays the collapsed `int` and a body that accumulates real records
        # fails L3-tc (`seq py_alias` vs `seq int`). Patch the function IR to the
        # `list` + element-record shape Module5 produces for the BARE `List[R]` form
        # (`_m5_get_list_record_elem` -> `return_value_type`), which Module6's
        # `_compute_return_type` resolves through `_record_types` to `array <rec>`.
        # The element record must ALSO be emitted PURE — Why3 forbids a mutable
        # component inside a polymorphic container — which is exactly what
        # `list_element_record_types` drives, so it is set here beside the injection.
        # PYTHON-AST NODE CTOR FAMILY (increment 11): `-> "List[ExprIR]"` — the STATEMENT
        # cluster's return interface. `block`/`_if_tail`/`_else_block`/`simple_stmt`/
        # `statement` all return a LIST OF STATEMENT NODES, and under the ctor family a
        # statement node is an `emit_ir` exactly like an expression node — so the faithful
        # return type is `array emit_ir`. Module5 sees only an unrecognised string
        # Constant, so the return stays the collapsed `unit`/`int` and every consumer of
        # `body = self.block()` int-erases. Patched to the same `list` + element shape
        # Module5 produces for a bare `List[R]`, with the element named `emit_ir`
        # (a WhyML type, not a harvested record — so it is deliberately NOT added to
        # `wanted`/`list_elems`, which drive RECORD declaration and purity).
        _le_ir = None
        if node.returns is not None:
            _na = node.returns
            if isinstance(_na, _ast.Constant) and isinstance(_na.value, str):
                try:
                    _na = _ast.parse(_na.value.strip(), mode="eval").body
                except SyntaxError:
                    _na = None
            if (isinstance(_na, _ast.Subscript)
                    and isinstance(_na.value, _ast.Name)
                    and _na.value.id in ("List", "list")):
                _sl = _na.slice
                if isinstance(_sl, getattr(_ast, "Index", ())):
                    _sl = _sl.value
                if (isinstance(_sl, _ast.Name)
                        and _sl.id in ("ExprIR", "StmtIR", "IRNode", "ContractExprIR")):
                    _le_ir = "emit_ir"
        # PYTHON-AST NODE CTOR FAMILY: `-> "Tuple[List[ExprIR], List[ExprIR]]"` — the
        # `_call_args` return interface (`args = []; keywords = []; … return args,
        # keywords`). Module5 sees only an unrecognised string Constant, so the return
        # collapses to `unit` and BOTH tuple slots int-erase at the unpack
        # (`args, keywords = self._call_args(")")` bound two `ref 0`s). Record the
        # WhyML tuple shape directly; Module6's `_compute_return_type` and
        # `_build_method_return_type_map` (the TWO producers) both read it. Deliberately
        # a SEPARATE key, not `return_annotation`, so no existing `ann ==` branch shifts.
        _tup_ir = None
        if node.returns is not None:
            _ta = node.returns
            if isinstance(_ta, _ast.Constant) and isinstance(_ta.value, str):
                try:
                    _ta = _ast.parse(_ta.value.strip(), mode="eval").body
                except SyntaxError:
                    _ta = None
            if (isinstance(_ta, _ast.Subscript)
                    and isinstance(_ta.value, _ast.Name)
                    and _ta.value.id in ("Tuple", "tuple")):
                _ts = _ta.slice
                if isinstance(_ts, getattr(_ast, "Index", ())):
                    _ts = _ts.value
                _slots = list(_ts.elts) if isinstance(_ts, _ast.Tuple) else []
                _wh = []
                for _sl2 in _slots:
                    if (isinstance(_sl2, _ast.Subscript)
                            and isinstance(_sl2.value, _ast.Name)
                            and _sl2.value.id in ("List", "list")):
                        _e2 = _sl2.slice
                        if isinstance(_e2, getattr(_ast, "Index", ())):
                            _e2 = _e2.value
                        if (isinstance(_e2, _ast.Name)
                                and _e2.id in ("ExprIR", "StmtIR", "IRNode",
                                               "ContractExprIR")):
                            _wh.append("seq emit_ir")
                            continue
                    _wh = []
                    break
                # EXACTLY the two-list shape Module6's `_refine_tuple_return_type`
                # honours (it compares against that literal and returns it). A wider
                # arity would be recorded here and then silently declined there, so
                # keep the two sides in exact agreement — fail-closed, int-erased as
                # before, for any other tuple shape.
                if len(_wh) == 2:
                    _tup_ir = "(" + ", ".join(_wh) + ")"
        if _tup_ir is not None:
            fi = func_by_name.get(node.name)
            if fi is None:
                for _f in ir_data.get("functions", []):
                    if (_f.get("line") == getattr(node, "lineno", None)
                            and str(_f.get("name", "")).endswith(node.name)):
                        fi = _f
                        break
            if fi is not None:
                fi["return_tuple_whyml"] = _tup_ir
        if _le_ir is not None:
            fi = func_by_name.get(node.name)
            if fi is None:
                for _f in ir_data.get("functions", []):
                    if (_f.get("line") == getattr(node, "lineno", None)
                            and str(_f.get("name", "")).endswith(node.name)):
                        fi = _f
                        break
            if fi is not None:
                fi["return_annotation"] = "list"
                fi["return_value_type"] = _le_ir
        le = _ann_list_elem(node.returns) if node.returns is not None else None
        if le is not None:
            wanted.add(le)
            list_elems.add(le)
            # A METHOD's function-IR name is MANGLED (`_Parser._import_as_names` ->
            # `_parser___import_as_names`), so the bare-name lookup above finds nothing
            # for one. Resolve on the def's LINE plus a name-suffix check, which is exact
            # for both plain functions and methods.
            fi = func_by_name.get(node.name)
            if fi is None:
                for _f in ir_data.get("functions", []):
                    if (_f.get("line") == getattr(node, "lineno", None)
                            and str(_f.get("name", "")).endswith(node.name)):
                        fi = _f
                        break
            if fi is not None:
                fi["return_annotation"] = "list"
                fi["return_value_type"] = le
        for arg in node.args.args:
            an = _ann_name(arg.annotation) if arg.annotation is not None else None
            if an in records:
                wanted.add(an)
                fi = func_by_name.get(node.name)
                if fi is not None and fi.get("symbol_table") is not None:
                    fi["symbol_table"][arg.arg] = an
    # A "RecList:<Rec>" FIELD names an element record that must ALSO be harvested and
    # declared, or its `array <Rec>` field type has no type to point at.
    for _n in list(wanted):
        for _f in records.get(_n, {}).get("fields", []):
            _vt = _f.get("value_type")
            if _f.get("type") == "list" and isinstance(_vt, str) and _vt in records:
                wanted.add(_vt)
    # PYTHON-AST NODE CTOR FAMILY (increment 10): the 0-FIELD ASDL SINGLETONS. A node
    # class with an EMPTY field tuple (`_NODE_SPEC['Load'] == ('expr_context', (), ())`)
    # carries NO information beyond its own IDENTITY — `_N("Load")()` is a constant. A
    # 0-field WhyML record is not even expressible, which is why these blocked the
    # `ctx`/`op` slots of every Starred/UnaryOp/BoolOp/Compare construction. The faithful
    # model is the class NAME as a `string`: it is exactly the identity, nothing is
    # erased, and it needs NO enum type, NO new ADT and NO axiom. The set is read off the
    # compiled file's OWN `_NODE_SPEC`, so it cannot drift from the source; it is absent
    # from every other file's IR, which is what keeps the lowering byte-inert.
    _singletons = _harvest_node_spec_singletons(validated_ast)
    if _singletons:
        ir_data["pyast_singleton_nodes"] = _singletons
    _ctor_params = _harvest_pyast_ctor_params(validated_ast)
    if _ctor_params:
        ir_data["pyast_ctor_init_params"] = _ctor_params
    if not wanted:
        return
    existing = {td.get("name") for td in ir_data.get("type_decls", [])}
    for name in sorted(wanted):
        if name not in existing:
            ir_data.setdefault("type_decls", []).insert(0, records[name])
    if list_elems:
        _prev = set(ir_data.get("list_element_record_types", []))
        ir_data["list_element_record_types"] = sorted(_prev | list_elems)


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
    # Piece 3b: the SAME-FILE `_NODE_SPEC` harvest, for the case where `pure_ast.py` itself
    # is the file under verification. No-op unless the file defines `_NODE_SPEC`.
    _resolve_same_file_node_spec_records(validated_ast, ir_data)
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
