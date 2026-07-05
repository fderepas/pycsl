"""module_collect.py — front-end helpers that collect module-level declarations.

B-final STEP 6 (refactor.md): relocated verbatim from ``Module4_SemanticAnalyzer.py``
when Module 4 was dropped from the pipeline. ``collect_module_constants`` and
``collect_module_globals`` are pure AST→dict collectors with no semantic-check coupling;
they are consumed by Module 5 (``Module5_IREmitter.visit_Module``) to emit the
``module_constants`` / ``module_globals`` IR fields. Kept in a neutral front-end module
so the deleted Module 4 leaves no import behind.
"""
from __future__ import annotations

from frontend import pure_ast as ast  # consume the same pure-Python tree Module3 builds
from typing import Any, Dict, Optional


def _module_const_int(value: Any) -> Optional[int]:
    """Int value of an int-literal expr (incl. unary `-N`), else None. Mirrors
    `Module5._const_int_value`."""
    if (isinstance(value, ast.Constant) and isinstance(value.value, int)
            and not isinstance(value.value, bool)):
        return int(value.value)
    if (isinstance(value, ast.UnaryOp) and isinstance(value.op, ast.USub)
            and isinstance(value.operand, ast.Constant)
            and isinstance(value.operand.value, int)
            and not isinstance(value.operand.value, bool)):
        return -int(value.operand.value)
    return None


def collect_module_constants(node: ast.Module) -> Dict[str, int]:
    """Module-level integer constants: a top-level `NAME = <int literal>` (or annotated)
    bound EXACTLY ONCE at module scope, that is not a `#@ shared` global and is never
    written via `global`. These are safe to inline as literals in contracts and bodies
    (mirrors class-body constants, `Module5._collect_class_constants`). A reassigned name
    is mutable global state and is excluded — contracts cannot soundly reference it in the
    per-function frame model (see module-constants-plan.md Q2). Consumed by Module 5
    (IR emission)."""
    counts: Dict[str, int] = {}
    candidates: Dict[str, int] = {}
    for child in getattr(node, "body", []):
        target = None
        value = None
        if (isinstance(child, ast.Assign) and len(child.targets) == 1
                and isinstance(child.targets[0], ast.Name)):
            target, value = child.targets[0].id, child.value
        elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
            target, value = child.target.id, child.value
        if target is None:
            continue
        counts[target] = counts.get(target, 0) + 1
        iv = _module_const_int(value)
        if iv is not None:
            candidates[target] = iv
        # 0442.md C5 (no-more-int): a string-literal module constant folds to a real
        # Why3 `string`, not an int hash. Collected here so contracts may reference it.
        elif isinstance(value, ast.Constant) and isinstance(value.value, str):
            candidates[target] = value.value
    shared = {d.variable for d in getattr(node, "csl_shared_decls", [])}
    written_via_global = {n for g in ast.walk(node) if isinstance(g, ast.Global)
                          for n in g.names}
    return {n: v for n, v in candidates.items()
            if counts.get(n, 0) == 1 and n not in shared
            and n not in written_via_global}


def collect_module_const_dicts(node: ast.Module) -> Dict[str, Dict[str, str]]:
    """Module-level constant str->str dict literals: a top-level
    `NAME = {"k1": "v1", "k2": "v2", ...}` (or annotated) whose keys AND values are
    ALL plain string literals, bound EXACTLY ONCE at module scope, not a `#@ shared`
    global and never written via `global`. Returns `{name: {k: v, ...}}` preserving
    source order (Python dict insertion order == AST `keys`/`values` order).

    These lower FAITHFULLY at a `NAME.get(k, default)` reflection site to a chained
    string-valued if-then-else (`if k = "k1" then "v1" else ... else default`) —
    exactly like a class-body scalar constant folds to its literal, but for the
    str->str mapping shape (e.g. `identifiers.OP_MAP`). A dict with any non-string
    key or value, an empty dict, or a reassigned name is excluded (fail-closed: it
    keeps the opaque behavior). Consumed by Module 5 (IR emission) and recognized in
    Module 6 (`_lower_dict_get_call`)."""
    counts: Dict[str, int] = {}
    candidates: Dict[str, Dict[str, str]] = {}
    for child in getattr(node, "body", []):
        target = None
        value = None
        if (isinstance(child, ast.Assign) and len(child.targets) == 1
                and isinstance(child.targets[0], ast.Name)):
            target, value = child.targets[0].id, child.value
        elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
            target, value = child.target.id, child.value
        if target is None:
            continue
        counts[target] = counts.get(target, 0) + 1
        if not isinstance(value, ast.Dict) or not value.keys:
            continue
        entries: Dict[str, str] = {}
        ok = True
        for k, v in zip(value.keys, value.values):
            if not (isinstance(k, ast.Constant) and isinstance(k.value, str)
                    and isinstance(v, ast.Constant) and isinstance(v.value, str)):
                ok = False
                break
            entries[k.value] = v.value
        # A key repeated in the literal would collapse in `entries` but the source
        # order of the FIRST occurrence is what Python keeps; require no collapse so
        # the chained-ITE arm order faithfully mirrors the literal.
        if ok and entries and len(entries) == len(value.keys):
            candidates[target] = entries
    shared = {d.variable for d in getattr(node, "csl_shared_decls", [])}
    written_via_global = {n for g in ast.walk(node) if isinstance(g, ast.Global)
                          for n in g.names}
    return {n: v for n, v in candidates.items()
            if counts.get(n, 0) == 1 and n not in shared
            and n not in written_via_global}


def _const_str_set_elems(value: Any) -> Optional[list]:
    """String elements of a module-level constant str-set literal, in SOURCE order
    (duplicates dropped, first occurrence kept — Python set semantics), else None.

    Recognizes the two faithful shapes:
      * a set-display literal  `{"a", "b", ...}`  (`ast.Set`), and
      * `frozenset({...})` / `frozenset([...])` / `frozenset((...))` and the
        `set(...)` counterparts wrapping an all-string-literal set/list/tuple.
    ALL elements must be plain `str` constants; a non-string element, an empty
    collection, a starred element, or any other shape yields None (fail-closed —
    the site keeps its opaque behavior)."""
    inner = value
    if isinstance(value, ast.Call):
        func = value.func
        if not (isinstance(func, ast.Name) and func.id in ("frozenset", "set")):
            return None
        # exactly one positional arg, no keywords/starargs
        if len(value.args) != 1 or getattr(value, "keywords", []):
            return None
        inner = value.args[0]
    if not isinstance(inner, (ast.Set, ast.List, ast.Tuple)):
        return None
    elts = getattr(inner, "elts", None)
    if not elts:
        return None
    seen: Dict[str, bool] = {}
    ordered: list = []
    for e in elts:
        if not (isinstance(e, ast.Constant) and isinstance(e.value, str)):
            return None
        if e.value not in seen:
            seen[e.value] = True
            ordered.append(e.value)
    return ordered or None


def collect_module_const_sets(node: ast.Module) -> Dict[str, list]:
    """Module-level constant string-set literals: a top-level `NAME = {"a", "b", ...}`
    (or `frozenset({...})` / `set([...])`, annotated `NAME: Set[str] = ...` included)
    whose elements are ALL plain string literals, bound EXACTLY ONCE at module scope,
    not a `#@ shared` global and never written via `global`. Returns `{name: [e, ...]}`
    with elements in source order (duplicates dropped).

    These lower FAITHFULLY at an `x in NAME` membership site to a disjunction of string
    equalities (`x = "a" || x = "b" || ...`) — EXACTLY as an inline set-display literal
    `x in {"a", "b"}` already lowers in `_emit_membership`; the named module constant is
    simply expanded to its literal (the set-analogue of `collect_module_const_dicts`).
    A set with any non-string element, an empty set, or a reassigned/shadowed name is
    excluded (fail-closed: the membership keeps its opaque `contains_check` behavior).
    Consumed by Module 5 (IR emission) and recognized in Module 6 (`_emit_membership`)."""
    counts: Dict[str, int] = {}
    candidates: Dict[str, list] = {}
    for child in getattr(node, "body", []):
        target = None
        value = None
        if (isinstance(child, ast.Assign) and len(child.targets) == 1
                and isinstance(child.targets[0], ast.Name)):
            target, value = child.targets[0].id, child.value
        elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
            target, value = child.target.id, child.value
        if target is None:
            continue
        counts[target] = counts.get(target, 0) + 1
        elems = _const_str_set_elems(value)
        if elems is not None:
            candidates[target] = elems
    shared = {d.variable for d in getattr(node, "csl_shared_decls", [])}
    written_via_global = {n for g in ast.walk(node) if isinstance(g, ast.Global)
                          for n in g.names}
    return {n: v for n, v in candidates.items()
            if counts.get(n, 0) == 1 and n not in shared
            and n not in written_via_global}


def collect_module_globals(node: ast.Module, class_names: set) -> Dict[str, ast.Call]:
    """inline.md Phase 1 — module-level global OBJECT instances: a top-level
    `g = C(<args>)` where `C` is a class defined in the module, bound EXACTLY ONCE at
    module scope, not a `#@ shared` global and never written via `global`. Returns
    `{name: constructor-Call-ast}`. These are single, named, statically-known objects
    (the simplest aliasing story), modeled as a Why3 mutable-record global; method calls
    on them are inlined (`ir_inline.py`). A reassigned name is excluded (a global
    instance is bound once — see Scope in inline.md). Mirrors `collect_module_constants`."""
    counts: Dict[str, int] = {}
    candidates: Dict[str, ast.Call] = {}
    for child in getattr(node, "body", []):
        target = None
        value = None
        if (isinstance(child, ast.Assign) and len(child.targets) == 1
                and isinstance(child.targets[0], ast.Name)):
            target, value = child.targets[0].id, child.value
        elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
            target, value = child.target.id, child.value
        if target is None:
            continue
        counts[target] = counts.get(target, 0) + 1
        if (isinstance(value, ast.Call) and isinstance(value.func, ast.Name)
                and value.func.id in class_names):
            candidates[target] = value
    shared = {d.variable for d in getattr(node, "csl_shared_decls", [])}
    written_via_global = {n for g in ast.walk(node) if isinstance(g, ast.Global)
                          for n in g.names}
    return {n: c for n, c in candidates.items()
            if counts.get(n, 0) == 1 and n not in shared
            and n not in written_via_global}
