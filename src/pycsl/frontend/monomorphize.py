"""Whole-module monomorphization for PEP 484 / PEP 695 generics (typing TY3).

This module implements the step-5 IR-resolution pass
(`apply_monomorphization(ir_data)`) wired into `frontend.ir_resolve.resolve`. It
operates purely on the RESOLVED IR dict (after import/inheritance/composition/
inline-globals) and BEFORE Module 6 (WhyML emission).

The strategy (per `docs/typing-global-overview.md` §4.1 and the two-plane spec
`typing-engagement/ty3/typevar-generic-twoplane-spec.md`):

  1. COLLECT — scan the IR for concrete instantiation sites
     (`C[<concrete-type>]()` constructor calls, `x: C[<concrete-type>]`
     annotations) and record `(generic_name, concrete_type)` pairs.
  2. GT3/GT4 LOUD-FAIL — `ParamSpec`/`TypeVarTuple` (GT3) and polymorphic
     recursion (GT4) are rejected with dedicated error codes (never approximated).
  3. BOUNDS — a TypeVar bound is an instantiation-time obligation: the concrete
     type must satisfy the bound (invariant checking per GT2; `Any` refused per GT1).
  4. EMIT — for each `(generic, concrete_type)` pair, deep-copy the generic's
     type_decl and methods, substituting the TypeVar by the concrete type in field
     types, signatures, and contract clauses, with name-mangling
     (`Stack` → `Stack_int`, `stack__push` → `stack_int__push`). Rewrite the
     call sites / annotations to the specialized names.
  5. CLASSIFY — specialized copies are Interpreted; an un-instantiated generic
     stays declaration-only (method bodies trusted, no VCs) and is recorded
     Ignored/GT8 in the soundness report.

The pass is total-additive: a module with NO generics is byte-identical (the
pass early-returns when no type_decl/function carries `type_params`).
"""
from __future__ import annotations

import copy
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from errors import PyCSLSemanticError

# The pure-Python front-end (PEP 695 type_params live on ClassDef/FunctionDef).
from frontend import pure_ast as _ast


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def apply_monomorphization(
    ir_data: Dict[str, Any], validated_ast: Any = None
) -> None:
    """Run whole-module monomorphization on the resolved IR, IN PLACE.

    No-op (early return) when no type_decl/function carries `type_params` —
    keeping every non-generic module byte-identical (the total-additivity rule).

    `validated_ast` is the woven pure_ast tree; COLLECT scans it for module-level
    instantiation sites (`Stack[int]()` in `if __name__ == ...` blocks that are
    NOT in the IR functions list) AND the IR (annotation subscripts)."""
    generics = _collect_generic_decls(ir_data)
    if not generics:
        return

    # STEP B (before COLLECT finalizes): GT3 loud-fail on ParamSpec/TypeVarTuple.
    _check_gt3_schema_only(generics)

    # STEP A — COLLECT concrete instantiations from the IR + the AST.
    instantiations = _collect_instantiations(ir_data, generics)
    if validated_ast is not None:
        instantiations |= _collect_instantiations_ast(validated_ast, generics)

    # GT4 — polymorphic recursion loud-fail (needs the collected set + AST).
    _check_gt4_polymorphic_recursion(ir_data, generics, instantiations,
                                     validated_ast)

    # GT1 — refuse `Any` as a type argument.
    for (gname, ctype) in instantiations:
        if ctype == "Any":
            raise PyCSLSemanticError(
                f"monomorphization: generic {gname!r} instantiated with `Any` — "
                f"GT1: Any never instantiates a TypeVar (the consistency relation "
                f"is deliberately unsound; see typing-global-overview.md §5 GT1).",
                stage="monomorphize", code="PYCSL-TY3-GT1",
            )

    # STEP C — BOUNDS check (invariant per GT2).
    _check_bounds(generics, instantiations)

    # STEP D — EMIT specialized copies + rewrite call/annotation sites.
    _emit_specializations(ir_data, generics, instantiations)

    # STEP E — CLASSIFY (soundness-report hook). The specialized copies are
    # ordinary monomorphic IR (Interpreted by default); record the
    # monomorphization provenance so --soundness-report can tag them. An
    # un-instantiated generic is recorded Ignored/GT8 (declaration-only).
    _record_classification(ir_data, generics, instantiations)


# ---------------------------------------------------------------------------
# STEP 0 — generic decls
# ---------------------------------------------------------------------------

def _collect_generic_decls(ir_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Return `{generic_name: {"type_params": [...], "decl": type_decl_or_None,
    "methods": [function_ir, ...]}}` for every class/function carrying
    `type_params`. A generic class's methods are collected by `self_type`."""
    generics: Dict[str, Dict[str, Any]] = {}
    for decl in ir_data.get("type_decls", []):
        tparams = decl.get("type_params")
        if tparams:
            generics[decl["name"]] = {
                "type_params": tparams, "decl": decl, "methods": [],
                "kind": "class",
            }
    for func in ir_data.get("functions", []):
        tparams = func.get("type_params")
        if tparams:
            generics[func["name"]] = {
                "type_params": tparams, "decl": None,
                "methods": [func], "kind": "function",
            }
    # Attach methods to their enclosing generic class.
    for func in ir_data.get("functions", []):
        self_type = func.get("self_type") or ""
        if self_type in generics and generics[self_type]["kind"] == "class":
            if func not in generics[self_type]["methods"]:
                generics[self_type]["methods"].append(func)
    return generics


# ---------------------------------------------------------------------------
# STEP B — GT3: ParamSpec / TypeVarTuple are schema-only (loud-fail)
# ---------------------------------------------------------------------------

def _check_gt3_schema_only(generics: Dict[str, Dict[str, Any]]) -> None:
    for gname, info in generics.items():
        for tp in info["type_params"]:
            kind = tp.get("kind", "TypeVar")
            if kind != "TypeVar":
                raise PyCSLSemanticError(
                    f"monomorphization: generic {gname!r} declares a {kind} "
                    f"({tp.get('name')!r}) — GT3: ParamSpec/TypeVarTuple are "
                    f"schema-only and not interpreted (typing-global-overview.md "
                    f"§5 GT3). Use a plain TypeVar `T`.",
                    stage="monomorphize", code="PYCSL-TY3-GT3",
                )


# ---------------------------------------------------------------------------
# STEP A — COLLECT concrete instantiations
# ---------------------------------------------------------------------------

def _collect_instantiations(
    ir_data: Dict[str, Any],
    generics: Dict[str, Dict[str, Any]],
) -> Set[Tuple[str, str]]:
    """Walk the IR for `C[<concrete-type>]` instantiation sites. Returns the
    deduped set of `(generic_name, concrete_type_str)` pairs."""
    found: Set[Tuple[str, str]] = set()
    generic_names = set(generics)
    for func in ir_data.get("functions", []):
        for site in _find_subscript_calls(func.get("body", []), generic_names):
            found.add(site)
        # Also collect annotation subscripts in the symbol_table: a param whose
        # type is `Stack[int]` (recorded as the original annotation string).
        for _vname, vtype in (func.get("symbol_table") or {}).items():
            ct = _match_generic_annotation(vtype, generic_names)
            if ct is not None:
                found.add(ct)
        # And return_annotation (e.g. `-> Stack[int]`).
        ra = func.get("return_annotation")
        if isinstance(ra, str):
            ct = _match_generic_annotation(ra, generic_names)
            if ct is not None:
                found.add(ct)
    return found


def _find_subscript_calls(
    body: List[Dict[str, Any]], generic_names: Set[str]
) -> List[Tuple[str, str]]:
    """Walk IR statements for `Call(func=Subscript(value=Name(g), slice=<type>))`
    patterns — the constructor `Stack[int]()` form. Returns the instantiation
    pairs."""
    out: List[Tuple[str, str]] = []
    for stmt in body:
        out.extend(_scan_node_for_subscript_calls(stmt, generic_names))
    return out


def _scan_node_for_subscript_calls(
    node: Any, generic_names: Set[str]
) -> List[Tuple[str, str]]:
    """Recursively scan an IR node (dict or list) for subscript-call sites."""
    out: List[Tuple[str, str]] = []
    if isinstance(node, dict):
        # The IR shape for `C[int]()` is:
        # {"stmt": "Call", "func": {"type": "Subscript", "value": <Name>,
        #  "slice": <type-str>}, ...} OR a Call whose func is a Subscript.
        # The exact key varies; we look for any dict carrying a Subscript on a
        # generic name.
        if node.get("type") == "Subscript" or node.get("stmt") == "Subscript":
            val = node.get("value")
            slice_node = node.get("slice")
            if isinstance(val, dict) and val.get("type") == "Var":
                gname = val.get("name", "")
                if gname in generic_names:
                    ct = _type_str(slice_node)
                    if ct is not None:
                        out.append((gname, ct))
        # A Call wrapping a Subscript (the `C[int]()` constructor).
        if node.get("stmt") == "Call" or node.get("type") == "Call":
            fnode = node.get("func")
            sub = _scan_node_for_subscript_calls(fnode, generic_names)
            out.extend(sub)
        for v in node.values():
            out.extend(_scan_node_for_subscript_calls(v, generic_names))
    elif isinstance(node, list):
        for item in node:
            out.extend(_scan_node_for_subscript_calls(item, generic_names))
    return out


def _type_str(node: Any) -> Optional[str]:
    """Render an IR type node (a Name/Subscript slice) as a concrete type
    string we can substitute. Returns None for non-concrete / unrecognized."""
    if node is None:
        return None
    if isinstance(node, str):
        # Some IR shapes carry the slice as a bare string (the type name).
        return _sanitize_type_name(node)
    if isinstance(node, dict):
        t = node.get("type")
        if t == "Var":
            return _sanitize_type_name(node.get("name", ""))
        if t == "Subscript":
            # nested generic instantiation — not supported in this delivery.
            return None
    return None


def _sanitize_type_name(name: str) -> Optional[str]:
    """Normalize a concrete type name to one of the PyCSL primitive tags or a
    user class name. Returns None for Any/unrecognized."""
    if not name:
        return None
    if name == "Any":
        return "Any"  # caught by GT1 in the caller
    # PyCSL primitive tags.
    if name in ("int", "bool", "str", "bytes", "float", "list", "dict", "set"):
        # bool is modeled as int in PyCSL; keep the source name for clarity,
        # the substitution maps both to WhyML int.
        return name
    return name


def _match_generic_annotation(
    type_str: Any, generic_names: Set[str]
) -> Optional[Tuple[str, str]]:
    """Match a symbol_table/return_annotation string like `Stack[int]` against
    the generic names. Returns `(generic_name, concrete_type)` or None."""
    if not isinstance(type_str, str):
        return None
    # Match `Generic[Type]` — the annotation recorded the subscription text.
    m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\[([A-Za-z_][A-Za-z0-9_]*)\]$", type_str)
    if m:
        gname, ct = m.group(1), m.group(2)
        if gname in generic_names:
            return (gname, ct)
    return None


# ---------------------------------------------------------------------------
# AST-based COLLECT (module-level instantiation sites)
# ---------------------------------------------------------------------------

def _collect_instantiations_ast(
    tree: Any, generics: Dict[str, Dict[str, Any]]
) -> Set[Tuple[str, str]]:
    """Walk the woven AST for `C[<concrete-type>]` instantiation sites that live
    in module-level code (`if __name__ == ...` blocks, module-level assigns) —
    these are NOT in the IR functions list, so the IR scan misses them. Returns
    the deduped set of `(generic_name, concrete_type_str)` pairs."""
    found: Set[Tuple[str, str]] = set()
    generic_names = set(generics)
    for node in _ast.walk(tree):
        # `C[int]()` constructor call: Call(func=Subscript(value=Name(C),
        # slice=Name(int))).
        if isinstance(node, _ast.Call):
            sub = _extract_ast_subscript(node.func, generic_names)
            if sub is not None:
                found.add(sub)
        # `x: C[int]` annotation on an AnnAssign / function arg.
        if isinstance(node, _ast.AnnAssign):
            sub = _extract_ast_subscript(node.annotation, generic_names)
            if sub is not None:
                found.add(sub)
        # `def f(x: C[int]) -> C[int]` arg/return annotations.
        if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
            for arg in (node.args.args + node.args.posonlyargs
                        + node.args.kwonlyargs):
                sub = _extract_ast_subscript(arg.annotation, generic_names)
                if sub is not None:
                    found.add(sub)
            if node.returns is not None:
                sub = _extract_ast_subscript(node.returns, generic_names)
                if sub is not None:
                    found.add(sub)
    return found


def _extract_ast_subscript(
    node: Any, generic_names: Set[str]
) -> Optional[Tuple[str, str]]:
    """If `node` is `Generic[<concrete-type>]` on a generic name, return the
    `(generic_name, concrete_type)` pair; else None. Recognizes:
      - `Subscript(value=Name(C), slice=Name(int))` — the `C[int]` form.
    Only the bare-Name concrete type is recognized (a nested generic
    instantiation is not supported in this delivery)."""
    if not isinstance(node, _ast.Subscript):
        return None
    val = node.value
    if not isinstance(val, _ast.Name):
        return None
    gname = val.id
    if gname not in generic_names:
        return None
    slice_node = node.slice
    # PEP 695 / 3.9+: slice is the expression directly (Name).
    if isinstance(slice_node, _ast.Name):
        ct = _sanitize_type_name(slice_node.id)
        if ct is not None:
            return (gname, ct)
    return None


# ---------------------------------------------------------------------------
# GT4 — polymorphic recursion loud-fail
# ---------------------------------------------------------------------------

def _check_gt4_polymorphic_recursion(
    ir_data: Dict[str, Any],
    generics: Dict[str, Dict[str, Any]],
    instantiations: Set[Tuple[str, str]],
    validated_ast: Any = None,
) -> None:
    """Polymorphic recursion loud-fail (GT4). Under closed-world monomorphization,
    a generic function `f[T]` that recursively calls `f[T]` (with the TypeVar
    ITSELF, not a concrete type) would require specializing `f` for infinitely
    many types — monomorphization does not terminate. The check scans the AST
    (the IR body is monomorphized away) for a generic function whose body calls
    the same generic with its own TypeVar name as the type argument. Loud-fail.

    A recursive call with a CONCRETE type (`f[int]()` inside `f[T]`) is fine —
    the concrete type is collected and the specialization terminates."""
    if validated_ast is None:
        return
    # Build {generic_func_name: tvar_name} for PEP 695 generic functions.
    gen_tvars: Dict[str, str] = {}
    for gname, info in generics.items():
        if info["kind"] == "function" and info["type_params"]:
            gen_tvars[gname] = info["type_params"][0]["name"]
    if not gen_tvars:
        return
    for node in _ast.walk(validated_ast):
        if not isinstance(node, _ast.Call):
            continue
        sub = _extract_ast_subscript(node.func, set(gen_tvars))
        if sub is None:
            continue
        gname, ct = sub
        tvar = gen_tvars.get(gname)
        # Polymorphic recursion: the recursive call's type arg IS the generic's
        # own TypeVar (not a concrete type). This is the non-terminating shape.
        if tvar is not None and ct == tvar:
            raise PyCSLSemanticError(
                f"monomorphization: generic function {gname!r} calls itself with "
                f"its own TypeVar {tvar!r} — GT4: polymorphic recursion does "
                f"not terminate under monomorphization (typing-global-overview.md "
                f"§5 GT4). The recursive call must use a concrete type.",
                stage="monomorphize", code="PYCSL-TY3-GT4",
            )


# ---------------------------------------------------------------------------
# STEP C — BOUNDS (invariant per GT2)
# ---------------------------------------------------------------------------

def _check_bounds(
    generics: Dict[str, Dict[str, Any]],
    instantiations: Set[Tuple[str, str]],
) -> None:
    """For each (generic, concrete_type) with a bound B on the TypeVar, the
    concrete type must satisfy B. Today: exact match (invariant checking, GT2).
    A bound that is None admits any concrete type."""
    for (gname, ct) in instantiations:
        info = generics.get(gname)
        if info is None:
            continue
        for tp in info["type_params"]:
            bound = tp.get("bound")
            if bound is None:
                continue
            # Invariant checking (GT2): the concrete type must be EXACTLY the
            # bound. Stricter than S1 (which admits subtyping); legitimate
            # divergence-by-strictness.
            if ct != bound:
                raise PyCSLSemanticError(
                    f"monomorphization: generic {gname!r} instantiated with "
                    f"{ct!r} but its TypeVar {tp.get('name')!r} is bound to "
                    f"{bound!r} — invariant check (GT2: variance deferred) "
                    f"requires the concrete type to be exactly the bound.",
                    stage="monomorphize", code="PYCSL-TY3-BOUND",
                )


# ---------------------------------------------------------------------------
# STEP D — EMIT specialized copies + rewrite sites
# ---------------------------------------------------------------------------

def _emit_specializations(
    ir_data: Dict[str, Any],
    generics: Dict[str, Dict[str, Any]],
    instantiations: Set[Tuple[str, str]],
) -> None:
    """For each (generic, concrete_type) pair, deep-copy the generic's decl +
    methods with T substituted and name-mangled; rewrite the call/annotation
    sites to the specialized names; REMOVE the original generic decl + methods
    (they are replaced by the copies). An un-instantiated generic stays as
    declaration-only (its method bodies are marked trusted — no VCs)."""
    # Group instantiations by generic name.
    by_generic: Dict[str, List[str]] = {}
    for (gname, ct) in sorted(instantiations):
        by_generic.setdefault(gname, []).append(ct)

    new_type_decls: List[Dict[str, Any]] = []
    new_functions: List[Dict[str, Any]] = []

    # Build a rename map: (generic_name, concrete_type) -> specialized_name, and
    # a TypeVar-name -> concrete-type map per specialization.
    rename_map: Dict[Tuple[str, str], str] = {}
    tvar_map: Dict[Tuple[str, str], str] = {}
    for gname, ctypes in by_generic.items():
        info = generics[gname]
        tparam_name = info["type_params"][0]["name"]
        for ct in ctypes:
            spec_name = _mangled_name(gname, ct)
            rename_map[(gname, ct)] = spec_name
            tvar_map[(gname, ct)] = tparam_name

    # 1. Emit specialized type_decls (and remove the originals that had ≥1 inst).
    for decl in ir_data.get("type_decls", []):
        tparams = decl.get("type_params")
        if tparams and decl["name"] in by_generic:
            # The generic is being specialized — emit one copy per concrete type.
            tvar = tparams[0]["name"]
            for ct in by_generic[decl["name"]]:
                spec = _specialize_decl(decl, tvar, ct,
                                         rename_map[(decl["name"], ct)])
                new_type_decls.append(spec)
            # The ORIGINAL generic decl is dropped (replaced by the copies).
        else:
            new_type_decls.append(decl)

    # 2. Emit specialized functions (methods + generic functions).
    for func in ir_data.get("functions", []):
        self_type = func.get("self_type") or ""
        func_tparams = func.get("type_params")
        if func_tparams:
            # A PEP 695 generic top-level function.
            tvar = func_tparams[0]["name"]
            fname = func["name"]
            if fname in by_generic:
                for ct in by_generic[fname]:
                    spec = _specialize_function(
                        func, tvar, ct, rename_map[(fname, ct)],
                        new_self_type=rename_map.get((fname, ct)))
                    spec["name"] = _mangled_name(fname, ct).lower() + "__" + fname.split("__")[-1] \
                        if "__" in fname else _mangled_name(fname, ct).lower()
                    new_functions.append(spec)
                continue  # original dropped
        if self_type in by_generic:
            # A method of a generic class.
            tvar = generics[self_type]["type_params"][0]["name"]
            for ct in by_generic[self_type]:
                spec_name = rename_map[(self_type, ct)]
                spec = _specialize_function(func, tvar, ct, spec_name,
                                            new_self_type=spec_name)
                # method name mangling: Class__method -> Class_concrete__method
                orig_name = func["name"]
                method_tail = orig_name.split("__", 1)[1] if "__" in orig_name else orig_name
                spec["name"] = f"{spec_name.lower()}__{method_tail}"
                new_functions.append(spec)
            continue  # original dropped
        new_functions.append(func)

    ir_data["type_decls"] = new_type_decls
    ir_data["functions"] = new_functions

    # 3. Rewrite call sites: `Stack[int]()` -> `Stack_int()`, and annotations.
    _rewrite_call_sites(ir_data, rename_map)
    _rewrite_annotations(ir_data, rename_map)


def _mangled_name(generic_name: str, concrete_type: str) -> str:
    """`Stack` + `int` -> `Stack_int`. Non-alnum concrete chars -> `_`."""
    safe = re.sub(r"[^A-Za-z0-9_]", "_", concrete_type)
    return f"{generic_name}_{safe}"


def _specialize_decl(
    decl: Dict[str, Any], tvar: str, concrete: str, new_name: str
) -> Dict[str, Any]:
    """Deep-copy a generic type_decl with the TypeVar substituted by the
    concrete type. Field types, class invariants, init_body all get walked."""
    spec = copy.deepcopy(decl)
    spec["name"] = new_name
    # The specialized decl is NOT generic itself.
    spec.pop("type_params", None)
    # Substitute T in field types.
    for f in spec.get("fields", []):
        if f.get("type") == tvar:
            f["type"] = concrete
    # Substitute T in class invariants (walk the IR expr tree).
    spec["class_invariants"] = [
        _subst_type_in_ir(inv, tvar, concrete)
        for inv in spec.get("class_invariants", [])
    ]
    # init_body may carry type-annotated values; walk them too.
    spec["init_body"] = [
        _subst_type_in_ir(s, tvar, concrete)
        for s in spec.get("init_body", [])
    ]
    # bases: drop `Generic[T]` (the legacy base); keep others.
    spec["bases"] = [b for b in spec.get("bases", []) if b not in ("Generic",)]
    return spec


def _specialize_function(
    func: Dict[str, Any], tvar: str, concrete: str,
    new_class_name: str, new_self_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Deep-copy a generic function/method with T substituted."""
    spec = copy.deepcopy(func)
    # Substitute T in the symbol_table (param/return types).
    spec["symbol_table"] = {
        k: (concrete if v == tvar else v)
        for k, v in (spec.get("symbol_table") or {}).items()
    }
    if spec.get("return_annotation") == tvar:
        spec["return_annotation"] = concrete
    # self_type -> the specialized class name.
    if new_self_type is not None and spec.get("self_type"):
        spec["self_type"] = new_self_type
    # Substitute T in contract clauses (requires/ensures/assigns/raises) and body.
    contracts = spec.get("contracts") or {}
    for clause in ("requires", "ensures", "assigns"):
        if clause in contracts:
            contracts[clause] = [
                _subst_type_in_ir(c, tvar, concrete)
                for c in contracts[clause]
            ]
    spec["body"] = [
        _subst_type_in_ir(s, tvar, concrete)
        for s in spec.get("body", [])
    ]
    # The specialized function is NOT generic itself.
    spec.pop("type_params", None)
    return spec


def _subst_type_in_ir(node: Any, tvar: str, concrete: str) -> Any:
    """Walk an IR expr/statement tree and replace `Var(name=tvar)` with
    `Var(name=concrete)` when the TypeVar appears in a type position. This is
    conservative: it replaces ANY Var node whose name matches the TypeVar.
    Contract clauses that mention the TypeVar in a value position (rare for
    generics — the TypeVar is a type, not a value) are also rewritten, which is
    safe because the concrete type is a constant in the specialized copy."""
    if isinstance(node, dict):
        new = {}
        for k, v in node.items():
            if k == "name" and v == tvar and node.get("type") == "Var":
                new[k] = concrete
            elif k == "return_annotation" and v == tvar:
                new[k] = concrete
            else:
                new[k] = _subst_type_in_ir(v, tvar, concrete)
        # Also handle field-type strings and annotation strings.
        if "type" in new and new["type"] == tvar:
            new["type"] = concrete
        return new
    if isinstance(node, list):
        return [_subst_type_in_ir(item, tvar, concrete) for item in node]
    return node


def _rewrite_call_sites(
    ir_data: Dict[str, Any], rename_map: Dict[Tuple[str, str], str]
) -> None:
    """Rewrite `C[int]()` constructor calls to `C_int()` (the specialized
    plain constructor). Walks every function body."""
    for func in ir_data.get("functions", []):
        func["body"] = [
            _rewrite_subscript_calls_in_stmt(s, rename_map)
            for s in func.get("body", [])
        ]


def _rewrite_subscript_calls_in_stmt(
    stmt: Any, rename_map: Dict[Tuple[str, str], str]
) -> Any:
    """Recursively rewrite `Call(Subscript(Name(C), int))` -> `Call(Name(C_int))`."""
    if isinstance(stmt, dict):
        new = {}
        for k, v in stmt.items():
            if k == "func" and isinstance(v, dict):
                new[k] = _rewrite_subscript_to_name(v, rename_map)
            else:
                new[k] = _rewrite_subscript_calls_in_stmt(v, rename_map)
        return new
    if isinstance(stmt, list):
        return [_rewrite_subscript_calls_in_stmt(item, rename_map)
                for item in stmt]
    return stmt


def _rewrite_subscript_to_name(
    node: Any, rename_map: Dict[Tuple[str, str], str]
) -> Any:
    """If `node` is a Subscript on a generic name, return the specialized
    plain Name; else recurse."""
    if isinstance(node, dict):
        if node.get("type") == "Subscript" or node.get("stmt") == "Subscript":
            val = node.get("value")
            slice_node = node.get("slice")
            if isinstance(val, dict) and val.get("type") == "Var":
                gname = val.get("name", "")
                ct = _type_str(slice_node)
                if ct is not None and (gname, ct) in rename_map:
                    return {"type": "Var", "name": rename_map[(gname, ct)]}
        # Recurse into children.
        new = {}
        for k, v in node.items():
            new[k] = _rewrite_subscript_to_name(v, rename_map)
        return new
    if isinstance(node, list):
        return [_rewrite_subscript_to_name(item, rename_map) for item in node]
    return node


def _rewrite_annotations(
    ir_data: Dict[str, Any], rename_map: Dict[Tuple[str, str], str]
) -> None:
    """Rewrite `Stack[int]` annotation strings in symbol_table /
    return_annotation to the specialized name."""
    for func in ir_data.get("functions", []):
        st = func.get("symbol_table") or {}
        new_st = {}
        for k, v in st.items():
            new_st[k] = _rewrite_annotation_str(v, rename_map)
        func["symbol_table"] = new_st
        ra = func.get("return_annotation")
        if isinstance(ra, str):
            func["return_annotation"] = _rewrite_annotation_str(ra, rename_map)


def _rewrite_annotation_str(
    type_str: Any, rename_map: Dict[Tuple[str, str], str]
) -> Any:
    if not isinstance(type_str, str):
        return type_str
    m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\[([A-Za-z_][A-Za-z0-9_]*)\]$", type_str)
    if m:
        gname, ct = m.group(1), m.group(2)
        if (gname, ct) in rename_map:
            return rename_map[(gname, ct)]
    return type_str


# ---------------------------------------------------------------------------
# STEP E — CLASSIFY (soundness-report provenance)
# ---------------------------------------------------------------------------

def _record_classification(
    ir_data: Dict[str, Any],
    generics: Dict[str, Dict[str, Any]],
    instantiations: Set[Tuple[str, str]],
) -> None:
    """Record the monomorphization provenance for --soundness-report. Specialized
    copies are Interpreted (the default); an un-instantiated generic is recorded
    Ignored/GT8 (declaration-only, no specialized copy emitted)."""
    instantiated = {g for (g, _ct) in instantiations}
    uninst: List[Dict[str, Any]] = []
    for gname, info in generics.items():
        if gname not in instantiated:
            uninst.append({
                "name": gname,
                "kind": "Ignored",
                "gt": "GT8",
                "reason": "generic declared but never instantiated — no "
                          "specialized copy emitted, no per-instance VC",
            })
    if uninst:
        ir_data.setdefault("monomorphization_report", {})["uninstantiated"] = uninst
