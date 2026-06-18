"""core_ir_semantic.py — the language-agnostic IR semantic-check seam.

This is the core's *semantic-analysis on the IR* step (spec §6.2; refactor.md
Phase B), distinct from ``ir_schema.validate_ir`` (which does structural/shape
validation, §6.1). It runs after the IR is ingested and validated, makes **no**
reference to any source language, and is the **migration target** for the
language-agnostic logic checks formerly entangled with the Python AST in
Module 4. Each such check moves here one at a time (refactor.md B2..Bn), each
gated by an unchanged full-corpus pass/fail **and** error-message diff.

Because the IR carries source spans (§4.4 — ``line``/``col`` on each function),
a check raised here reports against the original source line in *any*
front-end's language, exactly as an AST-based Module 4 check did.

Migrated so far:
  - B1: the §4.4 front-end span contract (every function carries a span).
  - B2: ``no_exception`` well-formedness (was Module 4 ``_validate_no_exception``).
  - B3: ``assigns``-region base typing (was Module 4 ``_validate_assigns_regions``).
  - B4: predicate bases — ``\\length`` not on dict/set, ``\\valid``/``\\separated``
        bases must be list/bytes (was Module 4 ``_validate_predicate_bases``). This
        one is a *surface-tracking* expr-walker: the error context varies by where
        the predicate sits — function contract, while-loop invariant (with the
        innermost loop's line), or ghost expression (simple / subscript).
  - B-final: ghost string ``+=``/``-=``/``*=`` ban — a string-typed ghost variable
        does not support augmented assignment (use the ``^`` concat operator). Walks
        the IR body's ``GhostAssign`` nodes; the ghost's declared type rides the
        function ``symbol_table`` (Module 5 now builds it, including ghost decls).
        Was Module 4's ``_build_function_scope`` ghost-string-op raise.
"""
from __future__ import annotations

import warnings
from typing import Any

from errors import PyCSLSemanticError


def run_ir_semantic_checks(ir: Any, *, stage: str = "ir-semantic") -> None:
    """Run the language-agnostic semantic checks on the IR (read-only, in place)."""
    # Module-level set of types a typed quantifier binder may name (scalars +
    # collection sorts + every declared datatype/class — classes are type_decls in
    # the IR, exactly like Module4's {datatypes} | {ClassDefs}). Used by B4's
    # quant-binder check; computed once per IR.
    known_binder_types = {"int", "bool", "str", "float", "list", "bytes",
                          "bytearray", "dict"} | {
        td.get("name") for td in ir.get("type_decls", []) if td.get("name")}
    module_constants = ir.get("module_constants") or {}
    # B-final STEP 4: bare names of `#@ \trusted` functions (Module 5 plumbs them as a
    # module-level list); `_check_lemma` rejects a plain lemma body that calls one.
    trusted_funcs = set(ir.get("trusted_funcs") or [])
    for func in ir.get("functions", []):
        _check_span(func, stage)
        _check_no_exception(func)
        _check_assigns_regions(func)
        _check_contract_exprs(func, known_binder_types)
        _check_contract_scope(func, module_constants)
        _check_subscript_assignments(func)
        _check_checkpoints(func)
        _check_mutable_defaults(func)
        _check_acts(func)
        _check_ghost_string_ops(func)
        _check_diverges(func)
        _check_lemma(func, trusted_funcs)
    # Module-level (cross-method) checks run once over the whole IR.
    _check_happy(ir)
    _check_mutex_invariants(ir)
    _check_class_invariants(ir)
    _check_concurrency(ir)
    _check_fresh_globals(ir, stage)


def _collect_call_targets(node: Any, acc: set) -> None:
    """Collect the bare/dotted callee name of every ``Call`` IR node reachable
    from ``node`` (the ``func`` slot, both ``f(...)`` and ``x.m(...)`` shapes)."""
    if isinstance(node, dict):
        if node.get("type") == "Call":
            f = node.get("func")
            if isinstance(f, str):
                acc.add(f)
                acc.add(f.rsplit(".", 1)[-1])
        for v in node.values():
            _collect_call_targets(v, acc)
    elif isinstance(node, list):
        for v in node:
            _collect_call_targets(v, acc)


def _check_fresh_globals(ir: Any, stage: str) -> None:
    """fresh-globals.md — SOUNDNESS CONFINEMENT for ``#@ fresh_globals``.

    ``#@ fresh_globals`` re-establishes each module-global singleton's CONSTRUCTOR
    post-state as an ASSUMED fact at the function's body entry. That is sound ONLY for
    a STANDALONE entry point that runs on a freshly-imported global (import ran the
    constructor) and is NEVER entered with a pre-mutated global. So the directive is
    confined to a top-level formal-test DRIVER that:

      (1) is NOT a method (``self``-receiver) — a method runs on an arbitrary live
          ``self`` / shared global, NOT a fresh construction; and
      (2) is NOT called by any other function in the unit — a callee inherits its
          caller's (possibly already-mutated) global, so assuming the fresh state
          would be UNSOUND.

    Either violation is a hard error: an unsound surfacing is worse than a missed
    proof. (A library function that another module imports and calls would also be
    rejected by (2) once that call is in scope; a top-level driver that nothing calls
    is the only admissible site.)"""
    funcs = ir.get("functions", []) or []
    fresh = [f for f in funcs if f.get("fresh_globals")]
    if not fresh:
        return
    # Union of every call target across ALL function bodies (so a `fresh_globals`
    # function that is invoked anywhere is caught).
    call_targets: set = set()
    for f in funcs:
        _collect_call_targets(f.get("body", []), call_targets)
    for f in fresh:
        name = f.get("name", "<anonymous>")
        short = name.rsplit("__", 1)[-1]
        where = f"function '{name}' (line {f.get('line', 0)})"
        if f.get("kind") == "method":
            raise PyCSLSemanticError(
                f"{where}: `#@ fresh_globals` is not allowed on a method. It "
                f"re-establishes the module-global constructor post-state as an "
                f"assumed entry fact, which is sound only for a standalone driver "
                f"that runs on a freshly-imported global — a method runs on an "
                f"arbitrary live `self`/shared global, so assuming the fresh state "
                f"would be unsound. See config/skills/pycsl-stdlib-coverage (fresh_globals).",
                stage=stage,
                code="PYCSL-SEM-FRESH-GLOBALS",
            )
        if name in call_targets or short in call_targets:
            raise PyCSLSemanticError(
                f"{where}: `#@ fresh_globals` is only allowed on a top-level driver "
                f"that no other verified function calls. '{short}' is called "
                f"elsewhere; a callee inherits its caller's (possibly already-mutated) "
                f"global, so re-establishing the fresh constructor state at its entry "
                f"would be unsound. Remove the call, or drop `#@ fresh_globals`.",
                stage=stage,
                code="PYCSL-SEM-FRESH-GLOBALS",
            )


def _check_span(func: Any, stage: str) -> None:
    """§4.4 front-end contract: every function carries a source span, so any
    migrated check can locate its error. Holds by construction for the Python
    front-end (Module 5 stamps ``line``/``col``); catches a non-conforming one."""
    if "line" not in func:
        name = func.get("name", "<anonymous>")
        raise PyCSLSemanticError(
            f"IR function '{name}' carries no source span; a front-end must "
            f"stamp §4.4 spans (line/col) on every node",
            stage=stage,
            code="PYCSL-SEM-SPAN",
        )


def _check_no_exception(func: Any) -> None:
    """B2 — ``no_exception`` well-formedness, migrated verbatim from Module 4's
    ``_validate_no_exception`` (which ran on the AST). Pure contract data, all
    present in the IR: ``no_exception`` (names), ``no_exception_all``, and
    ``raises[].exc_type``. Reports with the IR's name + §4.4 span, reproducing
    Module 4's messages exactly (no ``stage`` prefix — matching the original raise):

      - a ``no_exception`` name must be a known exception;
      - ``no_exception E`` and ``raises { E -> _ }`` for the same E is contradictory;
      - ``no_exception \\all`` with any ``raises`` clause is rejected.
    """
    from exception_model import KNOWN_EXCEPTIONS  # lazy: keep the import surface small

    contracts = func.get("contracts") or {}
    no_exc = list(contracts.get("no_exception", []) or [])
    no_exc_all = bool(contracts.get("no_exception_all", False))
    raises = contracts.get("raises", []) or []
    raised_names = {r.get("exc_type") for r in raises}

    where = f"function '{func.get('name', '<anonymous>')}' (line {func.get('line', 0)})"

    for name in no_exc:
        if name not in KNOWN_EXCEPTIONS:
            raise PyCSLSemanticError(
                f"{where}: no_exception names unknown exception '{name}'. "
                f"Known: {sorted(KNOWN_EXCEPTIONS)}.",
                code="PYCSL-SEM-NOEXC",
            )
        if name in raised_names:
            raise PyCSLSemanticError(
                f"{where}: contradictory annotations — no_exception {name} "
                f"and raises {{ {name} -> ... }} cannot both apply.",
                code="PYCSL-SEM-NOEXC",
            )
    if no_exc_all and raised_names:
        raise PyCSLSemanticError(
            f"{where}: no_exception \\all requires the raises set to be empty; "
            f"found raises {{ {', '.join(sorted(raised_names))} -> ... }}.",
            code="PYCSL-SEM-NOEXC",
        )


def _check_assigns_regions(func: Any) -> None:
    """B3 — `assigns`-region bases must be list-typed variables in scope, migrated
    verbatim from Module 4's ``_validate_assigns_regions`` (which ran on the AST).
    The IR carries the assigns targets (each an ``{"type": "AssignsRegion",
    "base": ...}`` node) and the ``symbol_table`` (var → type), so the check runs
    on the IR alone and reports with the IR function name.

    (The undefined-base path is in practice shadowed by the general contract-scope
    check that still runs in Module 4 — kept here for fidelity to the original.)
    """
    where = f"function '{func.get('name', '<anonymous>')}'"
    symtab = func.get("symbol_table") or {}
    for target in func.get("contracts", {}).get("assigns", []) or []:
        if isinstance(target, dict) and target.get("type") == "AssignsRegion":
            base = target.get("base")
            arr_type = symtab.get(base)
            if arr_type is None:
                raise PyCSLSemanticError(
                    f"Assigns region references undefined variable '{base}' in {where}.",
                    code="PYCSL-SEM-ASSIGNS",
                )
            if arr_type not in ("list", "List", "Any"):
                raise PyCSLSemanticError(
                    f"Assigns region on non-list variable '{base}' "
                    f"(type '{arr_type}') in {where}.",
                    code="PYCSL-SEM-ASSIGNS",
                )


# --- B4: predicate bases (surface-tracking expr-walker) ----------------------

_PB_ARRAY_BASE_TYPES = ("list", "List", "bytes", "bytearray", "Any", None)
_PB_LENGTHLESS_TYPES = ("dict", "Dict", "set", "Set", "frozenset", "FrozenSet")


def _check_contract_exprs(func, known) -> None:
    """B4 — the contract-expression checks, migrated from Module 4 (which ran them on
    the AST in ``_validate_predicate_bases`` and ``_validate_quant_binders``):
      - `\\length` not on a dict/set; `\\valid`/`\\separated` bases must be list/bytes;
      - a typed quantifier binder `\\forall x: T` must resolve `T` to a known type.
    Unlike the flat-metadata checks (B2/B3), these walk the contract EXPRESSION trees,
    and the error context depends on the predicate's *surface* — which the core
    reconstructs from the IR (matching Module 4's AST visitor):
      - function contracts (requires/ensures/assigns/variants) → ``function 'F'``;
      - WHILE-loop invariants/variants → ``while loop at line N inside function 'F'``
        (innermost enclosing while);
      - FOR-loop invariants/variants → ``for loop at line N inside function 'F'`` (a
        Python ``for`` desugars to a ``while`` only at Module-6 emission, so at
        IR-semantic time the node is still a ``for`` and carries the same fields);
      - ghost values → ``function 'F' (ghost 'g')`` (simple) /
        ``function 'F' (ghost 'g[...]')`` (subscript, GhostArraySet).
    Gated by drivers 0667–0673 (predicate bases) and 0556/0674/0675 (quant binders)
    staying XFAIL with byte-identical messages.
    """
    symtab = func.get("symbol_table") or {}
    fname = func.get("name", "<anonymous>")
    fctx = f"function '{fname}'"
    contracts = func.get("contracts") or {}
    for key in ("requires", "ensures", "assigns", "function_variants"):
        for clause in contracts.get(key, []) or []:
            _pb_expr(clause, fctx, symtab, known)
    _pb_body(func.get("body", []) or [], fname, symtab, known)


def _pb_body(stmts, fname, symtab, known) -> None:
    """Walk a statement list, applying the contract-expr checks to while-invariants
    and ghost values with their surface-specific context, recursing into nested bodies."""
    for s in stmts:
        if isinstance(s, dict):
            _pb_stmt(s, fname, symtab, known)


def _pb_stmt(s, fname, symtab, known) -> None:
    st = s.get("stmt")
    if st == "While":
        lctx = f"while loop at line {s.get('line', 0)} inside function '{fname}'"
        for clause in (s.get("invariants") or []):
            _pb_expr(clause, lctx, symtab, known)
        for clause in (s.get("variants") or []):
            _pb_expr(clause, lctx, symtab, known)
        _pb_body(s.get("body", []) or [], fname, symtab, known)
    elif st == "For":
        # A Python `for` desugars to a WhyML `while` only at emission (Module 6), so at
        # IR-semantic time the node is still a `for`; validate its loop invariants/variants
        # exactly as the `while` branch does (the For node carries the same `invariants`/
        # `variants`/`line` fields), then recurse the body.
        lctx = f"for loop at line {s.get('line', 0)} inside function '{fname}'"
        for clause in (s.get("invariants") or []):
            _pb_expr(clause, lctx, symtab, known)
        for clause in (s.get("variants") or []):
            _pb_expr(clause, lctx, symtab, known)
        _pb_body(s.get("body", []) or [], fname, symtab, known)
    elif st == "GhostAssign":
        _pb_expr(s.get("value"),
                 f"function '{fname}' (ghost '{s.get('target')}')", symtab, known)
    elif st == "GhostArraySet":
        gctx = f"function '{fname}' (ghost '{s.get('target')}[...]')"
        _pb_expr(s.get("index"), gctx, symtab, known)
        _pb_expr(s.get("value"), gctx, symtab, known)
    else:
        # Other compound statements (If/Match/Try/With/…): descend into nested
        # statement lists to find deeper whiles / ghosts.
        for v in s.values():
            _pb_descend(v, fname, symtab, known)


def _pb_descend(v, fname, symtab, known) -> None:
    if isinstance(v, dict):
        if "stmt" in v:
            _pb_stmt(v, fname, symtab, known)
        else:
            for x in v.values():
                _pb_descend(x, fname, symtab, known)
    elif isinstance(v, list):
        for x in v:
            _pb_descend(x, fname, symtab, known)


def _pb_expr(node, ctx, symtab, known) -> None:
    """Recursively check predicate bases (`\\length`/`\\valid`/`\\separated`) and typed
    quantifier binders in a contract-expr tree, against the surface context. Messages
    reproduce Module 4 verbatim."""
    if isinstance(node, list):
        for x in node:
            _pb_expr(x, ctx, symtab, known)
        return
    if not isinstance(node, dict):
        return
    t = node.get("type")
    if t == "ArrayLen":
        var = node.get("var", "")
        if not str(var).startswith("self.") and var != "\\result":
            typ = symtab.get(var)
            if typ in _PB_LENGTHLESS_TYPES:
                raise PyCSLSemanticError(
                    f"\\length is not supported on the {typ}-typed '{var}' in "
                    f"{ctx}: dicts/sets are modelled as total maps "
                    f"(`map int (option int)`) with no cardinality. Use \\has_key(d, k) "
                    f"for key presence, or a list/array for a length-bearing collection.",
                    code="PYCSL-SEM-PREDBASE",
                )
    elif t == "Valid":
        base = node.get("base")
        arr_type = symtab.get(base)
        if arr_type not in _PB_ARRAY_BASE_TYPES:
            raise PyCSLSemanticError(
                f"\\valid base '{base}' is not a list/bytes parameter "
                f"in {ctx} (got type '{arr_type}').",
                code="PYCSL-SEM-PREDBASE",
            )
    elif t == "Separated":
        for base in (node.get("base1"), node.get("base2")):
            arr_type = symtab.get(base)
            if arr_type not in _PB_ARRAY_BASE_TYPES:
                raise PyCSLSemanticError(
                    f"\\separated base '{base}' is not a list/bytes parameter "
                    f"in {ctx} (got type '{arr_type}').",
                    code="PYCSL-SEM-PREDBASE",
                )
    elif t in ("Forall", "Exists"):
        bt = node.get("binder_type")
        if bt is not None and bt not in known:
            raise PyCSLSemanticError(
                f"Quantifier binder '{node.get('var')}: {bt}' in {ctx} has an "
                f"unresolved type '{bt}'. A typed binder must name a scalar "
                f"(int/bool/str/float) or a declared `#@ datatype` / class — "
                f"it is never silently defaulted to int. "
                f"Known types: {sorted(known)}.",
                code="PYCSL-SEM-QUANTBINDER")
    # NOTE: `\proj` index-literal checking is NOT migrated here. It is a *precondition
    # guard* Module 5 depends on (ProjExpr emission reads `index.value`, assuming a
    # literal), so it must run BEFORE Module 5 — it stays in Module 4. Migrating it
    # would first require hardening Module 5's ProjExpr emission to tolerate a
    # non-literal index (refactor.md: a Module-5-hardening prerequisite).
    for v in node.values():
        _pb_expr(v, ctx, symtab, known)


# --- contract scope + \result usage (function_contracts) --------------------

def _check_contract_scope(func, module_constants) -> None:
    """The two surviving checks of Module 4's ``_validate_contract``: (1) ``\\result``
    is only allowed in ``ensures``; (2) every variable referenced in a contract must be
    in scope (the function ``symbol_table`` or a ``module_constant``). Both ride the same
    surfaces as the predicate/quant walk — function clauses (only ``ensures`` admits
    ``\\result``), while-loop invariants/variants, and ghost values — reconstructing the
    same context strings. Variable extraction mirrors Module 4's ``extract_variables``
    via ``_ir_free_vars`` (binders, ``\\result`` and ``self`` fields excluded)."""
    symtab = func.get("symbol_table") or {}
    fname = func.get("name", "<anonymous>")
    fctx = f"function '{fname}'"
    contracts = func.get("contracts") or {}
    for key, allow_result in (("requires", False), ("ensures", True),
                              ("assigns", False), ("function_variants", False)):
        for clause in contracts.get(key, []) or []:
            _cs_clause(clause, fctx, allow_result, symtab, module_constants)
    _cs_body(func.get("body", []) or [], fname, symtab, module_constants)


def _cs_body(stmts, fname, symtab, mc) -> None:
    for s in stmts:
        if isinstance(s, dict):
            _cs_stmt(s, fname, symtab, mc)


def _cs_stmt(s, fname, symtab, mc) -> None:
    st = s.get("stmt")
    if st == "While":
        lctx = f"while loop at line {s.get('line', 0)} inside function '{fname}'"
        for clause in (s.get("invariants") or []):
            _cs_clause(clause, lctx, False, symtab, mc)
        for clause in (s.get("variants") or []):
            _cs_clause(clause, lctx, False, symtab, mc)
        _cs_body(s.get("body", []) or [], fname, symtab, mc)
    elif st == "For":
        # A `for` is still a `for` at IR-semantic time (it desugars to a `while` only at
        # Module-6 emission); validate its loop invariants/variants exactly as the `while`
        # branch does, then recurse the body.
        lctx = f"for loop at line {s.get('line', 0)} inside function '{fname}'"
        for clause in (s.get("invariants") or []):
            _cs_clause(clause, lctx, False, symtab, mc)
        for clause in (s.get("variants") or []):
            _cs_clause(clause, lctx, False, symtab, mc)
        _cs_body(s.get("body", []) or [], fname, symtab, mc)
    elif st == "GhostAssign":
        _cs_clause(s.get("value"),
                   f"function '{fname}' (ghost '{s.get('target')}')", False, symtab, mc)
    elif st == "GhostArraySet":
        gctx = f"function '{fname}' (ghost '{s.get('target')}[...]')"
        _cs_clause(s.get("index"), gctx, False, symtab, mc)
        _cs_clause(s.get("value"), gctx, False, symtab, mc)
    else:
        for v in s.values():
            _cs_descend(v, fname, symtab, mc)


def _cs_descend(v, fname, symtab, mc) -> None:
    if isinstance(v, dict):
        if "stmt" in v:
            _cs_stmt(v, fname, symtab, mc)
        else:
            for x in v.values():
                _cs_descend(x, fname, symtab, mc)
    elif isinstance(v, list):
        for x in v:
            _cs_descend(x, fname, symtab, mc)


def _cs_clause(clause, ctx, allow_result, symtab, mc) -> None:
    if clause is None:
        return
    if not allow_result and _contains_result(clause):
        raise PyCSLSemanticError(
            f"Invalid use of '\\result' in {ctx}. It is only allowed in 'ensures'.",
            code="PYCSL-SEM-RESULT",
        )
    for v in _ir_free_vars(clause):
        if v and v not in symtab and v not in mc:
            raise PyCSLSemanticError(
                f"Undefined variable '{v}' referenced in contract for {ctx}. "
                f"Available variables in scope: {list(symtab.keys())}",
                code="PYCSL-SEM-SCOPE",
            )


def _ir_free_vars(node):
    """IR port of Module 4's ``extract_variables`` — the free (local-scope) variable
    names a contract expr references. Excludes quantifier binders, ``\\result`` (a
    ``Result`` node, not a ``Var``), and ``self`` fields (``FieldGet``); the string-base
    predicates (``\\length``/``\\valid``/``\\separated``/``\\copy``/assigns-region) carry
    their base as a string, so it is added explicitly before the generic recursion picks
    up nested ``Var`` nodes (lengths, indices, bounds)."""
    if isinstance(node, list):
        out: set = set()
        for x in node:
            out |= _ir_free_vars(x)
        return out
    if not isinstance(node, dict):
        return set()
    t = node.get("type")
    if t == "Var":
        return {node.get("name")}
    if t in ("FieldGet", "Result", "Attribute", "Call", "CallExpr"):
        # OPAQUE to scope extraction, matching Module 4's extract_variables (whose
        # `_CSL_CHILDREN_MAP` does not list calls, so their args — including type names
        # like `int` in `isinstance(x, int)` — are not recursed): field/attribute access
        # (`self.f` → FieldGet, `param.f` → Attribute), `\result`, and function calls.
        return set()
    if t == "ArrayLen":
        var = node.get("var", "")
        if str(var).startswith("self.") or var == "\\result":
            return set()
        return {var}
    if t in ("Forall", "Exists"):
        return _ir_free_vars(node.get("body")) - {node.get("var")}
    if t == "ForallItems":
        return ((_ir_free_vars(node.get("body")) - {node.get("key"), node.get("val")})
                | {node.get("coll")})
    base_names: set = set()
    if t == "Valid":
        base_names = {node.get("base")}
    elif t == "Separated":
        base_names = {node.get("base1"), node.get("base2")}
    elif t in ("GhostCopy", "GhostCopyRange"):
        base_names = {node.get("arr")}
    elif t == "AssignsRegion":
        base_names = {node.get("base")}
    out = {b for b in base_names if b}
    for v in node.values():
        out |= _ir_free_vars(v)
    return out


# --- subscript-assignment base typing (body walk) ---------------------------

def _check_subscript_assignments(func) -> None:
    """An `arr[i] = v` target must be a list/dict variable in scope — migrated from
    Module 4's ``_validate_subscript_assignments``. Walks the IR **body** (not the
    contract exprs) for `ArraySet` nodes; gated, exactly like Module 4, to *annotated*
    functions only (any `requires`/`ensures`/`assigns` — loop invariants do NOT count).
    The context is uniformly `function 'F'` (no surface tracking). The data is already
    in the IR (no plumbing): `ArraySet{array, index, value}` + `symbol_table`."""
    c = func.get("contracts") or {}
    if not (c.get("requires") or c.get("ensures") or c.get("assigns")):
        return  # unannotated function — Module 4 skips the check, so do we
    where = f"function '{func.get('name', '<anonymous>')}'"
    symtab = func.get("symbol_table") or {}
    _sa_walk(func.get("body", []) or [], where, symtab)


def _sa_walk(node, where, symtab) -> None:
    if isinstance(node, dict):
        if node.get("stmt") == "ArraySet":
            arr = node.get("array")
            if isinstance(arr, dict) and arr.get("type") == "Var":
                name = arr.get("name")
                arr_type = symtab.get(name)
                if arr_type is None:
                    raise PyCSLSemanticError(
                        f"Subscript assignment to undefined variable '{name}' in {where}.",
                        code="PYCSL-SEM-SUBSCRIPT",
                    )
                if arr_type not in ("list", "List", "dict", "Dict", "Any"):
                    raise PyCSLSemanticError(
                        f"Subscript assignment to non-list/dict variable '{name}' "
                        f"(type '{arr_type}') in {where}.",
                        code="PYCSL-SEM-SUBSCRIPT",
                    )
        for v in node.values():
            _sa_walk(v, where, symtab)
    elif isinstance(node, list):
        for x in node:
            _sa_walk(x, where, symtab)


# --- checkpoint \result ban (body walk) -------------------------------------

def _check_checkpoints(func) -> None:
    """A `#@ assert`/`#@ check` checkpoint may not use `\\result` (bound only at return),
    migrated from Module 4's ``_validate_checkpoints``. Walks the IR body for
    `ProofAssert` nodes (no plumbing — they are already in the IR) and checks each one's
    test for a `Result` node. Uniform `function 'F'` context."""
    where = f"function '{func.get('name', '<anonymous>')}'"
    _cp_walk(func.get("body", []) or [], where)


def _cp_walk(node, where) -> None:
    if isinstance(node, dict):
        if node.get("stmt") == "ProofAssert" and _contains_result(node.get("test")):
            raise PyCSLSemanticError(
                f"'\\result' is not allowed in a `#@ {node.get('kind')}` in {where} "
                f"(it is bound only at return; use `ensures` for return values).",
                code="PYCSL-SEM-CHECKPOINT",
            )
        for v in node.values():
            _cp_walk(v, where)
    elif isinstance(node, list):
        for x in node:
            _cp_walk(x, where)


def _contains_result(node) -> bool:
    if isinstance(node, dict):
        if node.get("type") == "Result":
            return True
        return any(_contains_result(v) for v in node.values())
    if isinstance(node, list):
        return any(_contains_result(x) for x in node)
    return False


# --- ghost string augmented-assignment ban (body walk) ----------------------

def _check_ghost_string_ops(func) -> None:
    """A string-typed ghost variable does not support an augmented assignment
    (``+=``/``-=``/``*=``); the ``^`` concat operator must be used instead — migrated
    from Module 4's ``_build_function_scope`` (which read ``current_scope``). Walks the
    IR body for ``GhostAssign`` nodes (already in the IR, no plumbing); for each with a
    non-``"="`` ``op`` whose target is ``string``-typed in the function ``symbol_table``
    (Module 5 now builds it, including ghost declarations — a ``: string`` ghost decl
    survives in the table because the later augmented assign does not overwrite it),
    raises Module 4's message verbatim. Context is ``function 'F'`` (matching Module 4's
    ``self.current_function_name``)."""
    where = f"function '{func.get('name', '<anonymous>')}'"
    symtab = func.get("symbol_table") or {}
    _gso_walk(func.get("body", []) or [], where, symtab)


def _gso_walk(node, where, symtab) -> None:
    if isinstance(node, dict):
        if node.get("stmt") == "GhostAssign":
            op = node.get("op")
            target = node.get("target")
            if op != "=" and symtab.get(target) == "string":
                raise PyCSLSemanticError(
                    f"Ghost string variable '{target}' does not support '{op}' "
                    f"in {where}. "
                    "Use the ^ operator for string concatenation: "
                    f"#@ ghost {target} = {target} ^ expr",
                    code="PYCSL-SEM-GHOSTSTR",
                )
        for v in node.values():
            _gso_walk(v, where, symtab)
    elif isinstance(node, list):
        for x in node:
            _gso_walk(x, where, symtab)


# --- \diverges justification (body walk) ------------------------------------

def _body_has_diverging_construct(body) -> bool:
    """True iff the IR body contains a loop (``While``/``For``), a critical section
    (``CriticalSection`` — a lock-acquire that may block forever), or a function/method
    call (``{"type": "Call"}`` — recursion or a diverging callee). This is the IR port of
    Module 4's ``ast.walk`` over ``ast.While/For/AsyncFor/Call`` + critical ``with``."""
    found = [False]

    def walk(node):
        if found[0]:
            return
        if isinstance(node, dict):
            if node.get("stmt") in ("While", "For", "CriticalSection"):
                found[0] = True
                return
            if node.get("type") == "Call":
                found[0] = True
                return
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for x in node:
                walk(x)

    walk(body)
    return found[0]


def _check_diverges(func) -> None:
    """B-final STEP 2 — reject ``#@ \\diverges`` on a body with NO potentially-diverging
    construct, migrated verbatim from Module 4's ``_validate_diverges``. The data is in
    the IR: the ``diverges`` flag plus body ``While``/``For``/``CriticalSection`` nodes and
    ``Call`` expressions. ``#@ \\diverges`` is the escape from Why3's termination VC; Why3
    then enforces the dual obligation (the body must actually be able to diverge) and
    rejects a provably-terminating body with *"this expression does not diverge"*. We catch
    it here with a clear message rather than emit WhyML that silently fails to type-check.
    A lemma's ``\\diverges`` is rejected (more specifically) by ``_check_lemma`` first."""
    if not func.get("diverges"):
        return
    if func.get("lemma"):
        return  # _check_lemma raises the lemma-specific message first
    if _body_has_diverging_construct(func.get("body", []) or []):
        return
    raise PyCSLSemanticError(
        f"`#@ \\diverges` on function '{func.get('name', '<anonymous>')}' is not "
        f"justified: its body has no potentially-diverging construct (no critical "
        f"section / lock-acquire, no loop, no call/recursion). A straight-line body "
        f"provably terminates, so Why3 rejects the `diverges` effect (\"this expression "
        f"does not diverge\"). Remove `#@ \\diverges`, or give the body a construct that "
        f"can actually block or loop.",
        code="PYCSL-SEM-DIVERGES",
    )


# --- lemma soundness / well-formedness (body walk + plumbed trusted set) -----

def _lemma_returns_value(body) -> bool:
    """True iff the IR body contains a ``Return`` statement carrying a non-``None`` value
    (Module 4 walked ``ast.Return`` whose value was neither absent nor the ``None``
    constant)."""
    found = [False]

    def walk(node):
        if found[0]:
            return
        if isinstance(node, dict):
            if node.get("stmt") == "Return":
                v = node.get("value")
                # `return` / `return None` → value is None (no value) or a None constant.
                if v is not None and not (
                        isinstance(v, dict) and v.get("type") in ("None", "CSLNone")):
                    found[0] = True
                    return
            for x in node.values():
                walk(x)
        elif isinstance(node, list):
            for x in node:
                walk(x)

    walk(body)
    return found[0]


def _lemma_calls_trusted(body, trusted) -> str:
    """Return the name of the first ``\\trusted`` function the IR body calls, or ``""``.
    A lemma-body call is ``{"type": "Call", "func": <bare-name>}`` — Module 5 plumbs the
    trusted set as bare names, so the match reproduces Module 4's ``n.func.id`` test."""
    hit = [""]

    def walk(node):
        if hit[0]:
            return
        if isinstance(node, dict):
            if node.get("type") == "Call":
                fn = node.get("func")
                if isinstance(fn, str) and fn in trusted:
                    hit[0] = fn
                    return
            for x in node.values():
                walk(x)
        elif isinstance(node, list):
            for x in node:
                walk(x)

    walk(body)
    return hit[0]


def _check_lemma(func, trusted_funcs) -> None:
    """B-final STEP 4 — ``#@ lemma`` soundness/well-formedness, migrated verbatim from
    Module 4's ``_validate_lemma`` (lemma.md §3). The IR carries the ``lemma`` flag
    (Module 5), the ``diverges`` flag, ``contracts.ensures``, ``return_annotation``,
    ``contracts.assigns`` (a ``\\nothing`` target is ``{"type": "Nothing"}``), the body
    (``Return``/``Call`` nodes), and the module-level plumbed ``trusted_funcs`` set.
    Enforced (messages reproduced byte-for-byte):
      - ``\\diverges`` forbidden (a non-terminating lemma proves nothing);
      - at least one ``#@ ensures`` (the conclusion);
      - return type ``None`` (a lemma computes ``unit``);
      - ``assigns \\nothing``;
      - no ``return <value>`` in the body;
      - no call to a ``\\trusted`` function (no trust-leakage)."""
    if not func.get("lemma"):
        return
    name = func.get("name", "<anonymous>")
    if func.get("diverges"):
        raise PyCSLSemanticError(
            f"`#@ lemma` '{name}' is also `#@ \\diverges`: a non-terminating "
            f"lemma proves nothing and would be unsound as a fact. Remove one.",
            code="PYCSL-SEM-LEMMA")
    contracts = func.get("contracts") or {}
    if not (contracts.get("ensures") or []):
        raise PyCSLSemanticError(
            f"`#@ lemma` '{name}' has no `#@ ensures`: a lemma must state the "
            f"fact it proves (the conclusion). Add at least one `#@ ensures`.",
            code="PYCSL-SEM-LEMMA")
    # Ghost discipline: a lemma returns unit. `-> None` → return_annotation "None";
    # no annotation → return_annotation None (both accepted).
    ra = func.get("return_annotation")
    if ra not in (None, "None"):
        raise PyCSLSemanticError(
            f"`#@ lemma` '{name}' must be annotated `-> None`: a lemma computes "
            f"nothing (its WhyML result is `unit`); the body is the proof.",
            code="PYCSL-SEM-LEMMA")
    for t in contracts.get("assigns", []) or []:
        if not (isinstance(t, dict) and t.get("type") == "Nothing"):
            raise PyCSLSemanticError(
                f"`#@ lemma` '{name}' must be `assigns \\nothing`: a lemma is "
                f"erased at extraction and may not mutate non-ghost state.",
                code="PYCSL-SEM-LEMMA")
    if _lemma_returns_value(func.get("body", []) or []):
        raise PyCSLSemanticError(
            f"`#@ lemma` '{name}' body must not `return` a value — it is a "
            f"proof (returns unit). Use `pass` for an immediate arm.",
            code="PYCSL-SEM-LEMMA")
    leaked = _lemma_calls_trusted(func.get("body", []) or [], trusted_funcs)
    if leaked:
        raise PyCSLSemanticError(
            f"`#@ lemma` '{name}' calls `\\trusted` function '{leaked}': a "
            f"checked lemma may not rest on an unverified (trusted) fact — that "
            f"would smuggle an unchecked axiom into a 'proved' lemma.",
            code="PYCSL-SEM-LEMMA")


# --- mutable default argument (front-end-resolved flag) ----------------------

def _check_mutable_defaults(func) -> None:
    """A list/dict/set default argument is a shared-aliasing bug — migrated from
    Module 4's ``_validate_no_mutable_defaults``. The Python-specific *detection*
    (literal vs `list()/dict()/set()` call, over positional + keyword-only defaults)
    is resolved by the front-end into the `has_mutable_default` IR flag (B4a-style
    plumbing); the core just reports the language-agnostic error."""
    if func.get("has_mutable_default"):
        raise PyCSLSemanticError(
            f"Mutable default argument in function '{func.get('name', '<anonymous>')}': "
            f"a list/dict/set default is a single object shared across all calls (a "
            f"shared-aliasing bug) and is outside PyCSL's value-semantics boundary "
            f"(ownership discipline R2). Use a `None` sentinel and initialise the "
            f"collection in the body.",
            code="PYCSL-SEM-MUTDEFAULT",
        )


# --- act / complete / disjoint well-formedness (plumbed pre-desugar acts) ----

def _check_acts(func) -> None:
    """Act-specific well-formedness, migrated from Module 4's ``_validate_acts``. The
    acts are desugared to requires/ensures in the front-end (Module 3) before the IR
    is built, so they are *plumbed* through as a separate ``acts`` IR field (each Act
    carries its `given`-guard exprs; Complete/Disjoint carry referenced names). Checks:
      1. duplicate act name;
      2. `\\result` in a `given` guard (guards run in the pre-state);
      3. a `complete`/`disjoint` referencing an undefined act;
      4. (warning) an act referenced by no `complete`/`disjoint` — likely a typo.
    Uniform `function 'F'` context."""
    acts = func.get("acts") or []
    if not acts:
        return
    where = f"function '{func.get('name', '<anonymous>')}'"
    defined: dict = {}
    for a in acts:
        if a.get("kind") != "act":
            continue
        name = a.get("name")
        if name in defined:
            raise PyCSLSemanticError(f"duplicate act name '{name}' in {where}.",
                                     code="PYCSL-SEM-ACT")
        defined[name] = a
        for gx in a.get("given_exprs", []):
            if _contains_result(gx):
                raise PyCSLSemanticError(
                    f"act '{name}' in {where}: '\\result' is not allowed in a "
                    f"'given' guard (guards are evaluated in the pre-state).",
                    code="PYCSL-SEM-ACT")
    referenced: set = set()
    for a in acts:
        kind = a.get("kind")
        if kind in ("complete", "disjoint"):
            for nm in a.get("names", []):
                referenced.add(nm)
                if nm not in defined:
                    raise PyCSLSemanticError(
                        f"`{kind}` in {where} references undefined act '{nm}'.",
                        code="PYCSL-SEM-ACT")
    # Mistyped-name / omission guard (warning, not error — declaring cases without
    # claiming coverage is legitimate), reproducing Module 4 verbatim.
    if any(a.get("kind") in ("complete", "disjoint") for a in acts):
        for nm in defined:
            if nm not in referenced:
                warnings.warn(
                    f"act '{nm}' in {where} is not referenced by any "
                    f"`complete`/`disjoint` — possible typo or omission.",
                    stacklevel=2)


# --- module-level HAPPY cross-method validation ------------------------------

def _check_happy(ir) -> None:
    """Module-level HAPPY well-formedness, migrated from Module 4's ``_validate_happy``.
    The Python-specific facts (declared properties, the module's SHORT method names, and
    methods containing a dynamic ``exec``) are resolved by the front-end into the
    top-level ``happy`` IR blob (the IR otherwise flattens method names to
    ``Class__method``); the core collects written fields from the IR and does the logic:
      1. an exempt name that is not a method  → error (a typo silently widens coverage);
      2. a non-exempt method with a dynamic ``exec``  → error (worst-case mutator);
      3. (warning) a region whose field is written nowhere  → inert property."""
    happy = ir.get("happy")
    if not happy:
        return
    method_names = set(happy.get("method_names", []))
    exec_methods = happy.get("exec_methods", [])
    # written fields = the `self.<field>[...] = v` sites (ArraySet on a FieldGet of self),
    # collected from every function body in the IR.
    written: set = set()
    for func in ir.get("functions", []):
        _hp_collect_written(func.get("body", []) or [], written)
    for hp in happy.get("properties", []):
        hname = hp.get("name")
        except_set = hp.get("except_set", [])
        for name in except_set:
            if name not in method_names:
                raise PyCSLSemanticError(
                    f"`happy {hname}`: exempt function '{name}' is not a method "
                    f"in this module. Known methods: {sorted(method_names)}. "
                    f"A typo in the exempt set would silently widen the property's "
                    f"coverage, so this is rejected.",
                    code="PYCSL-SEM-HAPPY")
        for m in sorted(set(exec_methods)):
            if m not in except_set:
                raise PyCSLSemanticError(
                    f"`happy {hname}`: method '{m}' contains a dynamic `exec(...)`, "
                    f"which may write anything (not a compile-time-constant exec, so it "
                    f"cannot be spliced/bounded). A non-exempt dynamic-exec method cannot "
                    f"be confined by this property — add it to the except set or remove the "
                    f"exec. (07-1839 P5 — exec is a worst-case mutator under HAPPY.)",
                    code="PYCSL-SEM-HAPPY")
        if hp.get("protects") is not None:
            continue
        if hp.get("field") not in written:
            warnings.warn(
                f"`happy {hname}`: no write to `self.{hp.get('field')}[...]` found in "
                f"this module — the property expands to zero obligations (inert). "
                f"Check the field name.",
                stacklevel=2)


def _hp_collect_written(node, written) -> None:
    if isinstance(node, dict):
        if node.get("stmt") == "ArraySet":
            arr = node.get("array")
            if (isinstance(arr, dict) and arr.get("type") == "FieldGet"
                    and arr.get("object") == "self"):
                written.add(arr.get("field"))
        for v in node.values():
            _hp_collect_written(v, written)
    elif isinstance(node, list):
        for x in node:
            _hp_collect_written(x, written)


def _check_concurrency(ir) -> None:
    """B-final STEP 5 — protected-access + lock-order, migrated from Module 4's
    held-mutex body walk (``_check_protected_in_stmts`` & helpers). The IR carries
    ``shared_vars`` (``[{name, mutex}]``), ``lock_order`` (an ordered mutex-name list),
    and body ``CriticalSection{mutex, body}`` nodes (both ``#@ critical`` and
    ``#@ acquires`` lower to this). Gated, exactly like Module 4, to functions in a module
    that declares at least one shared var. The walk tracks the set of HELD mutexes:

      * entering a ``CriticalSection`` adds its mutex to the held set for its body;
      * acquiring a mutex while already holding one requires a ``#@ lock_order``
        declaration, and must respect that order;
      * a shared variable may be read/written only while its protecting mutex is held.

    Statement coverage mirrors Module 4 EXACTLY (only ``If``/``While``/``For``/
    ``CriticalSection``/``Assign``/``AugAssign``/``Return``/``Expr`` are walked — other
    statements are not inspected for shared access). Messages reproduced byte-for-byte."""
    shared_list = ir.get("shared_vars") or []
    if not shared_list:
        return  # Module 4 ran this walk only when `self._shared_vars` was non-empty.
    shared = {sv.get("name"): sv.get("mutex") for sv in shared_list}
    lock_order = ir.get("lock_order")  # list or None
    for func in ir.get("functions", []):
        fname = func.get("name", "<anonymous>")
        _conc_stmts(func.get("body", []) or [], set(), fname, shared, lock_order)


def _conc_check_shared_access(var_name, held, fname, shared, write) -> None:
    if var_name not in shared:
        return
    req_mutex = shared[var_name]
    if req_mutex is None:
        return  # unprotected shared — the ConcurrencyChecker warns; this walk is lenient
    if req_mutex not in held:
        action = "write to" if write else "read of"
        raise PyCSLSemanticError(
            f"Function '{fname}': unprotected {action} shared variable '{var_name}' "
            f"(protected_by '{req_mutex}', but held mutexes are {sorted(held) or 'none'}).",
            code="PYCSL-SEM-CONCURRENCY")


def _conc_check_reads(node, held, fname, shared) -> None:
    """IR port of Module 4's ``_check_expr_for_shared``: any ``Var`` reference to a shared
    variable is a read; recurse into every sub-node (matching ``ast.iter_child_nodes``)."""
    if isinstance(node, dict):
        if node.get("type") == "Var":
            _conc_check_shared_access(node.get("name"), held, fname, shared, write=False)
        for v in node.values():
            _conc_check_reads(v, held, fname, shared)
    elif isinstance(node, list):
        for x in node:
            _conc_check_reads(x, held, fname, shared)


def _conc_stmts(stmts, held, fname, shared, lock_order) -> None:
    for s in stmts:
        if isinstance(s, dict):
            _conc_stmt(s, held, fname, shared, lock_order)


def _conc_stmt(s, held, fname, shared, lock_order) -> None:
    st = s.get("stmt")
    if st == "CriticalSection":
        mutex = s.get("mutex")
        inner_held = held | {mutex} if mutex else held
        if mutex and held and lock_order is None:
            raise PyCSLSemanticError(
                f"Function '{fname}': nested mutex acquisition of '{mutex}' while holding "
                f"{sorted(held)} requires a module-level '#@ lock_order' declaration.",
                code="PYCSL-SEM-CONCURRENCY")
        if mutex and held and lock_order is not None:
            # Sorted for determinism (Module 4 iterated a set; sorting only affects the
            # inherently non-deterministic case of >1 held mutex violating the order).
            for already_held in sorted(held):
                ah_idx = lock_order.index(already_held) if already_held in lock_order else -1
                new_idx = lock_order.index(mutex) if mutex in lock_order else -1
                if ah_idx >= 0 and new_idx >= 0 and new_idx <= ah_idx:
                    raise PyCSLSemanticError(
                        f"Function '{fname}': lock_order violation — acquiring '{mutex}' "
                        f"while holding '{already_held}' violates declared order "
                        f"{lock_order}.",
                        code="PYCSL-SEM-CONCURRENCY")
        _conc_stmts(s.get("body", []) or [], inner_held, fname, shared, lock_order)
    elif st == "If":
        _conc_stmts(s.get("body", []) or [], held, fname, shared, lock_order)
        _conc_stmts(s.get("orelse", []) or [], held, fname, shared, lock_order)
    elif st in ("While", "For"):
        _conc_stmts(s.get("body", []) or [], held, fname, shared, lock_order)
    elif st == "Assign":
        target = s.get("target")
        if isinstance(target, str):
            _conc_check_shared_access(target, held, fname, shared, write=True)
        _conc_check_reads(s.get("value"), held, fname, shared)
    elif st == "AugAssign":
        target = s.get("target")
        if isinstance(target, str):
            _conc_check_shared_access(target, held, fname, shared, write=True)
    elif st == "Return":
        if s.get("value") is not None:
            _conc_check_reads(s.get("value"), held, fname, shared)
    elif st == "Expr":
        _conc_check_reads(s.get("value"), held, fname, shared)
    # Any other statement type is NOT inspected (matching Module 4's _PROTECTED_HANDLERS).


def _check_class_invariants(ir) -> None:
    """B-final STEP 3 — class-invariant scope, migrated verbatim from Module 4's
    ``visit_ClassDef`` check. For each ``type_decl`` of kind ``record``, every free
    variable a ``class_invariant`` references must be a declared field (``self.<field>``
    is lowered to ``FieldGet`` and excluded by ``_ir_free_vars``, exactly as Module 4's
    ``extract_variables`` excluded ``FieldAccess``). The IR carries ``fields`` (name +
    type) and the lowered ``class_invariants`` exprs, so the check runs on the IR alone.
    The ``Available fields`` list is the field-name list in first-appearance order
    (matching Module 4's ``list(self._class_fields.keys())``)."""
    for td in ir.get("type_decls", []):
        if td.get("kind") != "record":
            continue
        field_names = [f.get("name") for f in td.get("fields", []) or []]
        field_set = set(field_names)
        cname = td.get("name")
        context = f"class invariant for '{cname}'"
        for inv in td.get("class_invariants", []) or []:
            # Sorted for determinism (Module 4 iterated a set; sorting only differs in
            # the inherently non-deterministic multiple-undefined-var case).
            for var in sorted(v for v in _ir_free_vars(inv) if v is not None):
                if var not in field_set:
                    raise PyCSLSemanticError(
                        f"Undefined variable '{var}' in {context}. "
                        f"Class invariants should only reference self.field or constants. "
                        f"Available fields: {field_names}",
                        code="PYCSL-SEM-CLASSINV",
                    )


def _check_mutex_invariants(ir) -> None:
    """Module-level mutex-invariant scope/well-formedness, migrated from Module 4's
    ``_validate_mutex_invariant_scope`` (refactor.md B-final). For each
    ``#@ mutex_invariant <m>: <expr>``, every free variable referenced by ``<expr>``
    must be a shared variable protected by ``<m>`` (matching by full mutex name OR by
    array-mutex base, ``m.split('[')[0]``). Single-/two-letter names (loop/quantifier
    binders common in invariants) are tolerated, mirroring the AST check.

    This was a MODULE-level check (Module 4 ran it once in ``visit_Module``, before any
    ``FunctionDef`` was visited — so the ``var in self.current_scope`` branch it carried
    was over an *empty* scope and never matched). The IR has no module-level function
    scope, so only the shared-var set remains; the message is reproduced byte-for-byte.
    Free variables come from ``_ir_free_vars`` (Module 4's ``extract_variables`` port)."""
    shared_vars = ir.get("shared_vars") or []
    mutex_invariants = ir.get("mutex_invariants") or {}
    # {var_name: mutex} over the IR's `[{name, mutex}]` shared-var list.
    shared = {sv.get("name"): sv.get("mutex") for sv in shared_vars}
    for mutex, inv_expr in mutex_invariants.items():
        protected = {v for v, m in shared.items() if m == mutex or
                     (m is not None and m.split('[')[0] == mutex.split('[')[0])}
        for var in _ir_free_vars(inv_expr):
            if var in protected:
                continue
            # Allow single-letter loop variables common in invariants
            if len(var) <= 2:
                continue
            raise PyCSLSemanticError(
                f"Mutex invariant for '{mutex}': variable '{var}' is not a shared variable "
                f"protected by '{mutex}'. Protected variables: {sorted(protected)}.",
                code="PYCSL-SEM-MUTEXINV",
            )
