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


def collect_module_const_int_dicts(node: ast.Module) -> Dict[str, Dict[str, int]]:
    """Module-level constant str->int dict literals: a top-level
    `NAME = {"k1": <int>, "k2": <int>, ...}` whose keys are ALL plain string
    literals and whose values are ALL int literals OR references to a
    module-level int constant (`_BINOP_PREC = {"->": _PREC_ARROW, ...}`), bound
    EXACTLY ONCE at module scope, not `#@ shared`, never written via `global`.
    The int-const references are resolved against `collect_module_constants` so
    the returned map is str->int. Preserves source (insertion) order.

    Analogue of `collect_module_const_dicts` (str->str) for the str->int shape
    (`proof2why3/emit_why3._BINOP_PREC`, a precedence table read at a
    `NAME.get(k, default)` site). Consumed ONLY by the Module-6 term->string
    catamorphism emitter (class-variant-impl.md T-string), which is gated on the
    term-pp recognizer — so the field is inert for every corpus program (no term
    ADT). Fail-closed: any non-string key or unresolved/non-int value excludes the
    whole dict."""
    int_consts = collect_module_constants(node)
    counts: Dict[str, int] = {}
    candidates: Dict[str, Dict[str, int]] = {}
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
        entries: Dict[str, int] = {}
        ok = True
        for k, v in zip(value.keys, value.values):
            if not (isinstance(k, ast.Constant) and isinstance(k.value, str)):
                ok = False
                break
            iv = _module_const_int(v)
            if iv is None and isinstance(v, ast.Name):
                rv = int_consts.get(v.id)
                iv = rv if isinstance(rv, int) else None
            if iv is None:
                ok = False
                break
            entries[k.value] = iv
        if ok and entries and len(entries) == len(value.keys):
            candidates[target] = entries
    shared = {d.variable for d in getattr(node, "csl_shared_decls", [])}
    written_via_global = {n for g in ast.walk(node) if isinstance(g, ast.Global)
                          for n in g.names}
    return {n: v for n, v in candidates.items()
            if counts.get(n, 0) == 1 and n not in shared
            and n not in written_via_global}


_COMPOUND_SCALAR_WHYML = {"str": "string", "int": "int", "bool": "int", "float": "real"}


def _compound_paren(w: str) -> str:
    """Parenthesize a WhyML type for use as an `option`/`list` argument. A tuple
    type is already fully bracketed (`(string, string)`) and a bare scalar has no
    space, so both are left as-is; a multi-token type (`option string`) is wrapped."""
    if " " not in w:
        return w
    if w.startswith("(") and w.endswith(")"):
        return w
    return f"({w})"


def _compound_ann_whyml(ann: Any, aliases: Dict[str, Any]) -> Optional[str]:
    """Map a Python type-annotation AST node to a PURE (immutable) WhyML type
    string, resolving module-level `NAME = <type>` aliases. Supports the faithful
    slot vocabulary the compound-key const-map lowering needs:

      str→string  int/bool→int  float→real
      Optional[T]→`option <T>`   List[T]→`list <T>`   Tuple[A, B, ...]→`(A, B, ...)`

    Returns None (fail-closed) for any unrecognized construct, so the enclosing
    const dict is simply not collected and keeps its opaque fallback."""
    if isinstance(ann, ast.Name):
        if ann.id in _COMPOUND_SCALAR_WHYML:
            return _COMPOUND_SCALAR_WHYML[ann.id]
        if ann.id in aliases:
            return _compound_ann_whyml(aliases[ann.id], aliases)
        return None
    if isinstance(ann, ast.Subscript):
        base = ann.value
        if not isinstance(base, ast.Name):
            return None
        sl = ann.slice
        if isinstance(sl, ast.Index):          # py<3.9 compat
            sl = sl.value
        if base.id == "Optional":
            inner = _compound_ann_whyml(sl, aliases)
            return None if inner is None else f"option {_compound_paren(inner)}"
        if base.id == "List":
            inner = _compound_ann_whyml(sl, aliases)
            return None if inner is None else f"list {_compound_paren(inner)}"
        if base.id in ("Tuple", "tuple"):
            elts = sl.elts if isinstance(sl, ast.Tuple) else [sl]
            if not elts:
                return None
            parts = []
            for e in elts:
                if isinstance(e, ast.Constant) and e.value is Ellipsis:
                    return None                # variadic Tuple[T, ...] — not a fixed tuple
                w = _compound_ann_whyml(e, aliases)
                if w is None:
                    return None
                parts.append(w)
            return "(" + ", ".join(parts) + ")"
    return None


def collect_module_const_compound_dicts(node: ast.Module) -> Dict[str, Dict[str, str]]:
    """Module-level constant dicts with a COMPOUND (tuple) key and a LIST value —
    the `TRIGGERS: Dict[Tuple[str, Optional[str]], List[Trigger]] = {...}` shape in
    `exception_model.py`. A top-level ANNOTATED assignment bound EXACTLY ONCE whose
    annotation is `Dict[<Tuple[...]>, List[<E>]]` (both slots deriving a pure WhyML
    type via `_compound_ann_whyml`, with module-level `NAME = Tuple[...]` type aliases
    resolved), not `#@ shared` / never written via `global`.

    Returns `{NAME: {"key_whyml": "(string, option string)", "elem_whyml":
    "(string, string)"}}`. Such a dict lowers FAITHFULLY: the constant becomes an
    opaque `val constant NAME : map <key_whyml> (option (list <elem_whyml>))` and a
    `NAME.get(k, [])` read becomes `(match Map.get NAME k with Some l -> l | None ->
    Nil)` — the real defaulting lookup returning `list <elem_whyml>`, sound under
    `ensures True`. Fail-closed and TIGHTLY GATED on a tuple key + list value, so a
    plain `Dict[str, int]` corpus dict is never collected (byte-identical)."""
    # Collect module-level type aliases (`Trigger = Tuple[str, str]`) so a `List[Trigger]`
    # value annotation resolves through the alias to its tuple element type.
    aliases: Dict[str, Any] = {}
    for child in getattr(node, "body", []):
        if (isinstance(child, ast.Assign) and len(child.targets) == 1
                and isinstance(child.targets[0], ast.Name)
                and isinstance(child.value, (ast.Subscript, ast.Name))):
            aliases[child.targets[0].id] = child.value

    counts: Dict[str, int] = {}
    candidates: Dict[str, Dict[str, str]] = {}
    for child in getattr(node, "body", []):
        if not (isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name)):
            continue
        target = child.target.id
        counts[target] = counts.get(target, 0) + 1
        value, annotation = child.value, child.annotation
        if not (isinstance(value, ast.Dict) and value.keys):
            continue
        # annotation must be Dict[K, V]
        if not (isinstance(annotation, ast.Subscript)
                and isinstance(annotation.value, ast.Name)
                and annotation.value.id in ("Dict", "dict")):
            continue
        sl = annotation.slice
        if isinstance(sl, ast.Index):
            sl = sl.value
        if not (isinstance(sl, ast.Tuple) and len(sl.elts) == 2):
            continue
        k_ann, v_ann = sl.elts
        # key must be a COMPOUND (tuple) type — the tight gate
        if not (isinstance(k_ann, ast.Subscript)
                and isinstance(k_ann.value, ast.Name)
                and k_ann.value.id in ("Tuple", "tuple")):
            continue
        # value must be a List[E]
        if not (isinstance(v_ann, ast.Subscript)
                and isinstance(v_ann.value, ast.Name)
                and v_ann.value.id == "List"):
            continue
        e_ann = v_ann.slice
        if isinstance(e_ann, ast.Index):
            e_ann = e_ann.value
        key_whyml = _compound_ann_whyml(k_ann, aliases)
        elem_whyml = _compound_ann_whyml(e_ann, aliases)
        if key_whyml is None or elem_whyml is None:
            continue
        candidates[target] = {"key_whyml": key_whyml, "elem_whyml": elem_whyml}
    shared = {d.variable for d in getattr(node, "csl_shared_decls", [])}
    written_via_global = {n for g in ast.walk(node) if isinstance(g, ast.Global)
                          for n in g.names}
    return {n: v for n, v in candidates.items()
            if counts.get(n, 0) == 1 and n not in shared
            and n not in written_via_global}


def collect_module_const_pair_dicts(node: ast.Module) -> Dict[str, list]:
    """Module-level constant `str -> (str, int)` PAIR dict literals: a top-level
    `NAME = {"k1": ("s1", <int>), ...}` whose keys are ALL plain string literals and
    whose values are ALL 2-TUPLES of a plain string literal and an int literal (or a
    module-level int constant, resolved via `collect_module_constants`), bound EXACTLY
    ONCE at module scope, not `#@ shared`, never written via `global`. Returns
    `{name: [(k, s, i), ...]}` preserving source (insertion) order.

    The THIRD member of the module-const-dict family, after `collect_module_const_dicts`
    (str->str) and `collect_module_const_int_dicts` (str->int). It is the
    `frontend/pure_ast._BINOP = {"|": ("BitOr", 4), ...}` shape: a precedence table whose
    entry is DESTRUCTURED into two locals (`opname, prec = _BINOP[self.cur().string]`).
    It lowers FAITHFULLY at two sites — a `<key> in NAME` membership guard becomes the
    `str_eq_op` disjunction over the dict's ACTUAL keys, and the tuple-unpack read becomes
    one chained if-then-else PER SLOT (a `string` for the first component, an `int` for the
    second), the key bound once. Fail-closed: any non-string key, any value that is not a
    literal (str, int) 2-tuple, an empty dict, or a reassigned name excludes the whole dict
    and keeps the opaque fallback, so no corpus program's dict is ever collected."""
    int_consts = collect_module_constants(node)
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
        if not isinstance(value, ast.Dict) or not value.keys:
            continue
        entries: list = []
        seen = set()
        ok = True
        for k, v in zip(value.keys, value.values):
            if not (isinstance(k, ast.Constant) and isinstance(k.value, str)):
                ok = False
                break
            if not (isinstance(v, ast.Tuple) and len(v.elts) == 2):
                ok = False
                break
            e0, e1 = v.elts
            if not (isinstance(e0, ast.Constant) and isinstance(e0.value, str)):
                ok = False
                break
            iv = _module_const_int(e1)
            if iv is None and isinstance(e1, ast.Name):
                rv = int_consts.get(e1.id)
                iv = rv if isinstance(rv, int) else None
            if iv is None:
                ok = False
                break
            if k.value in seen:
                ok = False
                break
            seen.add(k.value)
            entries.append((k.value, e0.value, iv))
        if ok and entries and len(entries) == len(value.keys):
            candidates[target] = entries
    shared = {d.variable for d in getattr(node, "csl_shared_decls", [])}
    written_via_global = {n for g in ast.walk(node) if isinstance(g, ast.Global)
                          for n in g.names}
    return {n: v for n, v in candidates.items()
            if counts.get(n, 0) == 1 and n not in shared
            and n not in written_via_global}


def collect_module_const_str_pairs(node: ast.Module) -> Dict[str, list]:
    """Module-level constant LIST-of-str-pair literals: a top-level
    `NAME = [("s1", "d1"), ("s2", "d2"), ...]` (or annotated) whose every element is a
    2-tuple of PLAIN STRING literals, bound EXACTLY ONCE at module scope, not a
    `#@ shared` global and never written via `global`. Returns `{name: [(s, d), ...]}`
    preserving source order (AST element order == Python list order).

    This is the ordered-lookup-table shape (`_PREFIX_STRIPS` in
    `proof2why3/from_lean_json.py`, a `List[Tuple[str, str]]` scanned by
    `for src, dst in _PREFIX_STRIPS: if name == src: return dst`). It lowers
    FAITHFULLY at a linear first-match lookup site to a chained string if-then-else
    (`if name = "s1" then "d1" else if ... else name`) — the same reflection device the
    str->str const *dict* uses, but for the ordered *list-of-pairs* shape where element
    ORDER (first match wins) is semantically load-bearing. Fail-closed: any non-2-tuple
    element, any non-string component, an empty list, or a reassigned name excludes the
    whole const (keeps the opaque fallback). Consumed by Module 5 (IR emission) and,
    when a `_strip_const_name`-style first-match scan reflects it, Module 6.

    Additive by construction: the field is set only when this tightly-gated collector
    returns non-empty, so it is ABSENT for every program without such a const literal
    (byte-identical emission), exactly like the sibling `collect_module_const_*`
    collectors."""
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
        if not (isinstance(value, ast.List) and value.elts):
            continue
        pairs = []
        ok = True
        for elt in value.elts:
            if not (isinstance(elt, ast.Tuple) and len(elt.elts) == 2):
                ok = False
                break
            a, b = elt.elts
            if not (isinstance(a, ast.Constant) and isinstance(a.value, str)
                    and isinstance(b, ast.Constant) and isinstance(b.value, str)):
                ok = False
                break
            pairs.append((a.value, b.value))
        if ok and pairs:
            candidates[target] = pairs
    shared = {d.variable for d in getattr(node, "csl_shared_decls", [])}
    written_via_global = {n for g in ast.walk(node) if isinstance(g, ast.Global)
                          for n in g.names}
    return {n: v for n, v in candidates.items()
            if counts.get(n, 0) == 1 and n not in shared
            and n not in written_via_global}


def collect_module_const_str_sets(node: ast.Module) -> Dict[str, list]:
    """Module-level constant STRING SET / FROZENSET literals: a top-level
    `NAME = frozenset({"a", "b", ...})` / `NAME = {"a", "b", ...}` /
    `NAME = frozenset(["a", ...])` / `NAME = frozenset(("a", ...))` (or annotated)
    whose every element is a PLAIN STRING literal, bound EXACTLY ONCE at module
    scope, not a `#@ shared` global and never written via `global`. Returns
    `{name: [elem, ...]}` — the deduplicated element list in first-appearance order
    (a set has no intrinsic order; consumers that need one impose it, e.g.
    `sorted(...)` at the lookup site).

    This is the finite string-membership-table shape (`KNOWN_EXCEPTIONS` in
    `exception_model.py`, a `frozenset` scanned by `sorted(KNOWN_EXCEPTIONS)` /
    `x in KNOWN_EXCEPTIONS`). It lets a Module-6 recognizer lower a whole-body
    consumer FAITHFULLY over the captured elements — e.g. `return sorted(NAME)`
    to the exact constant `array string` literal (the elements sorted at emit time,
    a compile-time fold — NO WhyML sorting), or `x in NAME` to a `str_eq_op`
    disjunction. Fail-closed: any non-string element, an empty set, or a reassigned
    name excludes the whole const (keeps the opaque fallback). Consumed by Module 5
    (IR emission) and, when such a whole-body consumer reflects it, Module 6.

    Additive by construction: the field is set only when this tightly-gated collector
    returns non-empty, so it is ABSENT for every program without such a const literal
    (byte-identical emission), exactly like the sibling `collect_module_const_*`
    collectors. Measured: fires on 0 of 3130 reference-corpus programs."""
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
        elts = None
        if (isinstance(value, ast.Call) and isinstance(value.func, ast.Name)
                and value.func.id in ("frozenset", "set") and len(value.args) == 1
                and isinstance(value.args[0], (ast.Set, ast.List, ast.Tuple))):
            elts = value.args[0].elts
        elif isinstance(value, ast.Set):
            elts = value.elts
        if not elts:
            continue
        members = []
        ok = True
        seen = set()
        for elt in elts:
            if not (isinstance(elt, ast.Constant) and isinstance(elt.value, str)):
                ok = False
                break
            if elt.value not in seen:
                seen.add(elt.value)
                members.append(elt.value)
        if ok and members:
            candidates[target] = members
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
