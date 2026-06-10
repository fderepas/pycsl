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
