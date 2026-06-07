#!/usr/bin/env python3
from __future__ import annotations

import argparse
import pure_ast as _ast  # dependency import-discovery parses via the pure-Python front-end
import copy
import hashlib
import json as _json
import os
import sys
import subprocess
import tempfile
from typing import Any, Dict, List, Optional, Set, Tuple

# Ensure sibling modules are importable regardless of cwd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the PyCSL Pipeline Modules
from Module1_Ingestor import Module1_Ingestor
from Module2_Parser import Module2_Parser
from Module3_Weaver import Module3_Weaver
from Module4_SemanticAnalyzer import Module4_SemanticAnalyzer
from errors import PyCSLError, PyCSLParseError
from Module5_IREmitter import Module5_IREmitter
from Module6_WhyMLTranspiler import Module6_WhyMLTranspiler
from ir_schema import validate_ir
from ir_inline import apply_inline_globals as _apply_inline_globals
from ConcurrencyChecker import ConcurrencyChecker


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


def _extract_imports(tree: _ast.AST) -> List[Tuple[str, str, str, int, bool]]:
    """Walk AST for import statements, return list of
    (local_name, original_name, module_path, level, is_module) tuples.
    is_module is True for 'import mod' / 'import mod as alias'.
    Wildcard imports use local_name='*', original_name='*'."""
    imports = []
    for node in _ast.walk(tree):
        if isinstance(node, _ast.ImportFrom) and node.module:
            for alias in node.names:
                if alias.name == '*':
                    imports.append(("*", "*", node.module, node.level or 0, False))
                    continue
                local = alias.asname if alias.asname else alias.name
                imports.append((local, alias.name, node.module, node.level or 0, False))
        elif isinstance(node, _ast.Import):
            for alias in node.names:
                local = alias.asname if alias.asname else alias.name
                imports.append((local, alias.name, alias.name, 0, True))
    return imports


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


def _resolve_module_path(module_dotted: str, level: int, main_file: str) -> Optional[str]:
    """Convert dotted module path to filesystem .py path.
    Returns the resolved path or None if file not found.
    Searches: main file's directory first, then CWD."""
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

    # Absolute import: try main file's directory, CWD, then built-in Lib/ stubs
    script_dir = os.path.dirname(os.path.abspath(__file__))
    lib_dir = os.path.join(script_dir, "Lib")
    for base in [os.path.dirname(os.path.abspath(main_file)), os.getcwd(), lib_dir]:
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
        analyzer = Module4_SemanticAnalyzer()
        validated = analyzer.process(unified)
        emitter = Module5_IREmitter(validated)
        ir_data = _json.loads(emitter.generate_json())

        # With --deep, resolve the dependency's own imports recursively
        if deep:
            dep_tree = _ast.parse(dep_source)
            _resolve_imports(dep_tree, filepath, ir_data,
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

    result = []
    for name in reachable:
        func = dict(all_funcs[name])  # shallow copy
        func["trusted"] = True
        result.append(func)
    return result


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
            if local == orig:
                prefix = f"{orig.lower()}__"
                for fname, f in dep_funcs.items():
                    if fname.startswith(prefix) and fname not in existing_funcs:
                        mf = dict(f)
                        mf["trusted"] = True
                        ir_data["functions"].insert(0, mf)
                        existing_funcs.add(fname)
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
                    mf = dict(f)
                    mf["trusted"] = True
                    ir_data["functions"].insert(0, mf)
                    existing_funcs.add(fname)
                    injected_helpers += 1
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
    `<class>__*` method stubs, so `_apply_inheritance` can monomorphize the
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


def _apply_inheritance(ir_data: Dict[str, Any]) -> None:
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


def _apply_composition(ir_data: Dict[str, Any]) -> None:
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


def _resolve_imports(validated_ast: _ast.AST, main_file: str, ir_data: Dict[str, Any],
                     deep: bool = False, cache: Optional[Dict[str, Any]] = None,
                     processing_set: Optional[Set[str]] = None) -> Set[str]:
    """Detect imports, resolve source files, inject trusted stubs into ir_data.
    Returns set of imported function local names."""
    imports = _extract_imports(validated_ast)
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
    # later `_apply_inheritance` pass can monomorphize them onto the subclass.
    imported_names |= _resolve_imported_base_classes(
        module_imports, main_file, ir_data, deep, cache, processing_set)
    return imported_names


def _proof_reference_mlw_name(source_file: str) -> str:
    """Return the stable <source>.mlw filename stored in a proof directory."""
    return os.path.splitext(os.path.basename(source_file))[0] + ".mlw"


def _make_temp_mlw_path() -> str:
    """Allocate a per-invocation temporary WhyML file path."""
    fd, path = tempfile.mkstemp(prefix=".pycsl_", suffix=".mlw")
    os.close(fd)
    return path


def _generate_rocq_obligations(mlw_path: str, output_dir: str, unproven_count: int,
                               source_file: Optional[str] = None) -> None:
    """Generate Rocq proof obligations for goals that SMT provers could not discharge."""
    os.makedirs(output_dir, exist_ok=True)

    # Add a Makefile for cleaning compilation artifacts
    makefile_path = os.path.join(output_dir, "Makefile")
    if not os.path.exists(makefile_path):
        with open(makefile_path, "w") as mf:
            mf.write(".PHONY:default, clean\n\ndefault:\n\nclean:\n")
            mf.write("\trm -rf *.glob *.vo *.vok *.vos *~ \n")

    # Copy the WhyML source as reference
    mlw_basename = (os.path.basename(mlw_path) if source_file is None
                    else _proof_reference_mlw_name(source_file))
    mlw_dest = os.path.join(output_dir, mlw_basename)
    import shutil
    shutil.copy2(mlw_path, mlw_dest)

    # Run why3 prove with Coq prover to generate .v skeletons
    cmd = [
        "why3", "prove",
        "-P", "Coq,8.20.1,",
        "-a", "split_vc",
        "-o", output_dir,
        mlw_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        # Collect generated .v files
        v_files = [f for f in os.listdir(output_dir) if f.endswith(".v")]
        if v_files:
            print(f"\n[*] Generated {len(v_files)} Rocq proof obligation(s) in {output_dir}/")
            for vf in sorted(v_files):
                print(f"    → {output_dir}/{vf}")
            print(f"    → {mlw_dest}  (WhyML source reference)")
            print(f"\n[*] To complete the proofs:")
            print(f"    1. Edit the .v file(s) — fill in proof scripts between 'Proof.' and 'Qed.'")
            print(f"    2. Compile: coqc -R ~/.opam/default/lib/coq/user-contrib/Why3 Why3 <file>.v")
        else:
            print(f"\n[*] No .v files generated — Coq prover may not have produced skeletons.")
            print(f"    The WhyML source is saved at: {mlw_dest}")
            print(f"    You can open it in Why3 IDE: why3 ide {mlw_dest}")
    except FileNotFoundError:
        print(f"\n[!] Could not run 'why3 prove -P Coq'. Is why3-coq installed?")
        print(f"    The WhyML source is saved at: {mlw_dest}")


def _sha256_file(path: str) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _find_coqc() -> Optional[str]:
    """Locate the coqc binary, checking opam default first."""
    opam_coqc = os.path.expanduser("~/.opam/default/bin/coqc")
    if os.path.isfile(opam_coqc) and os.access(opam_coqc, os.X_OK):
        return opam_coqc
    import shutil as _sh
    return _sh.which("coqc")


def _find_why3_coq_lib() -> Optional[str]:
    """Locate the Why3 Coq library directory."""
    opam_lib = os.path.expanduser("~/.opam/default/lib/why3/coq")
    if os.path.isdir(opam_lib):
        return opam_lib
    return None


def _check_rocq_proofs(proof_dir: str, mlw_path: str, unproven_goal_names: List[str]) -> int:
    """Check for pre-existing Rocq proofs and replay them with coqc.

    Returns the number of goals successfully proved by Rocq.
    """
    if not os.path.isdir(proof_dir):
        return 0

    coqc = _find_coqc()
    if not coqc:
        print("[!] coqc not found — cannot replay Rocq proofs.")
        return 0

    why3_coq = _find_why3_coq_lib()
    if not why3_coq:
        print("[!] Why3 Coq library not found — cannot replay Rocq proofs.")
        return 0

    # Staleness check: compare current .mlw with stored .mlw
    stored_mlw = None
    for f in os.listdir(proof_dir):
        if f.endswith(".mlw"):
            stored_mlw = os.path.join(proof_dir, f)
            break

    if stored_mlw:
        current_hash = _sha256_file(mlw_path)
        stored_hash = _sha256_file(stored_mlw)
        if current_hash != stored_hash:
            print(f"[!] Rocq proofs found but .mlw hash mismatch — proofs may be stale.")
            print(f"    Current:  {current_hash[:16]}...")
            print(f"    Stored:   {stored_hash[:16]}...")
            print(f"    Regenerate proofs with: pycsl --rocq {proof_dir}/ {mlw_path}")
            return 0

    # Find .v proof files
    v_files = sorted(f for f in os.listdir(proof_dir) if f.endswith(".v"))
    if not v_files:
        return 0

    proved_count = 0
    print(f"\n[*] {len(v_files)} Rocq proof(s) found in {proof_dir}/ — replaying with coqc...")

    for vf in v_files:
        vpath = os.path.join(proof_dir, vf)
        cmd = [coqc, "-R", why3_coq, "Why3", vpath]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                print(f"[*] Rocq proof verified: {vf}")
                proved_count += 1
            else:
                print(f"[!] Rocq proof FAILED to compile: {vf}")
                if result.stderr.strip():
                    for line in result.stderr.strip().splitlines()[:3]:
                        print(f"    {line}")
        except subprocess.TimeoutExpired:
            print(f"[!] Rocq proof compilation timed out: {vf}")
        except FileNotFoundError:
            print(f"[!] coqc not found during proof replay.")
            return proved_count

    return proved_count


def _parse_args() -> argparse.Namespace:
    """Build and return the parsed CLI argument namespace."""
    parser = argparse.ArgumentParser(description="PyCSL: Python Contract Specification Language Verifier")
    parser.add_argument("file", help="The Python file to verify")

    # Flags are grouped by concern for readable `--help`; grouping affects only the
    # help layout, not the parsed namespace.
    g_prover = parser.add_argument_group("prover selection")
    g_prover.add_argument("-p", "--prover", default=None,
                        help="Single prover to use (e.g. 'Alt-Ergo,2.6.2,' or 'Z3,4.13.3,'). "
                             "Overrides --provers and agents-config.json.")
    g_prover.add_argument("--provers", default=None,
                        help="Comma-separated list of Why3 prover IDs to try in order "
                             "(e.g. 'Alt-Ergo,2.6.2,,Z3,4.13.3,'). "
                             "Why3 tries each prover per goal and accepts the first Valid. "
                             "Overrides agents-config.json. "
                             "Default: Alt-Ergo then Z3.")
    g_prover.add_argument("--memory-model", default=None,
                        choices=["hoare", "typed", "store", "concurrent"],
                        help="Memory model for WhyML emission (default: hoare). "
                             "'typed'/'store' use a global heap (map loc int). "
                             "'concurrent' enables mutex-discipline verification.")

    g_scope = parser.add_argument_group("scope / output")
    g_scope.add_argument("--keep-mlw", action="store_true",
                        help="Keep the generated WhyML (.mlw) file for debugging")
    g_scope.add_argument("--soundness-report", action="store_true",
                        help="Emit a Soundness Ledger (07-1143 R4): classify every "
                             "function/VC as Modelled (body-verified), Specified "
                             "(axiomatic contract), Stubbed (signature-only), or "
                             "Confinement (HAPPY \\preserves), flag trusted dependencies, "
                             "and print JSON + a human summary. Skips proving.")
    g_scope.add_argument("--fun", action="append", default=None, metavar="NAME",
                        help="Only verify the named function and its transitive "
                             "call-dependencies (may be repeated). "
                             "Other functions become trusted stubs.")
    g_scope.add_argument("--deep", action="store_true",
                        help="Recursively resolve transitive imports in "
                             "dependency files (default: only direct imports "
                             "of the main file are resolved).")

    g_proof = parser.add_argument_group("proof modes")
    g_proof.add_argument("--no-proof", action="store_true",
                        help="Skip the proof step. Only run the pipeline "
                             "(parse, typecheck, transpile) and report success "
                             "if valid WhyML is generated.")
    g_proof.add_argument("--rocq", metavar="DIR", default=None,
                        help="On SMT prover failure, generate Rocq (Coq) "
                             "proof obligations in DIR. Why3 emits .v files "
                             "with proof skeletons that you complete manually "
                             "and compile with coqc.")
    g_proof.add_argument("--rocq-proofs", metavar="DIR", default=None, nargs="?",
                        const="__auto__",
                        help="Check DIR for pre-existing Rocq proofs when SMT "
                             "provers fail. Each .v file is replayed with coqc "
                             "for full verification. If DIR is omitted, "
                             "auto-detects <file>.proofs/ next to the input.")

    g_strict = parser.add_argument_group("strictness / extra checks")
    g_strict.add_argument("--strict-concurrent-checks", action="store_true",
                        help="Escalate ConcurrencyChecker warnings (unprotected "
                             "shared access, nested locking without lock_order) to "
                             "hard errors. Off by default to preserve backward "
                             "compatibility for existing concurrent-model corpora. "
                             "See config/skills/pycsl-ub-catalog/SKILL.md §7.3.")
    g_strict.add_argument("--allow-unverified-imports", action="store_true",
                        help="Permit imports on the C-extension deny-list "
                             "(ctypes, cffi, numpy.ctypeslib, cython) without "
                             "a #@ \\trusted opt-in on the importing function. "
                             "Off by default. See config/skills/pycsl-ub-catalog/SKILL.md §7.4.")
    g_strict.add_argument("--strict-hash-eq-consistency", action="store_true",
                        help="Emit the UB-7.2 hash/eq consistency property as a "
                             "Why3 goal that must be discharged (typically via "
                             "an external proof citation). Off by default — emits "
                             "as an axiom and trusts the user.")
    g_strict.add_argument("--check-behavioral-subtyping", action="store_true",
                        help="Layer D: emit Liskov refinement goals for "
                             "overriding methods (pre_base ⇒ pre_sub, "
                             "post_sub ⇒ post_base). Fails if an override "
                             "strengthens a precondition or weakens a "
                             "postcondition.")
    g_strict.add_argument("--strict-no-exception-propagation", action="store_true",
                        help="(Experimental, off by default.) Under `no_exception` "
                             "treat unannotated callees pessimistically: any call "
                             "from a `no_exception`-enabled function to an abstract "
                             "callee becomes an unsatisfiable VC. See the NoException "
                             "workplan §1.4 / docs/pycsl-static-semantics-reference §2.1.13.")

    g_audit = parser.add_argument_group("proof auditing")
    g_audit.add_argument("--audit-proof", action="store_true",
                        help="Audit every #@ proof rocq / lean directive "
                             "in the file. Confirms each cited theorem is "
                             "declared inside the matching nested namespace "
                             "in the proof file. Audit-only: skips transpile "
                             "and verify. Exit 0 PASS / 1 FAIL.")
    g_audit.add_argument("--audit-proof-rocq", action="store_true",
                        help="Like --audit-proof but only Rocq directives.")
    g_audit.add_argument("--audit-proof-lean", action="store_true",
                        help="Like --audit-proof but only Lean directives.")
    g_audit.add_argument("--rocq-proofs-path", metavar="DIR", default=None,
                        help="Override default Rocq proof dir for --audit-proof "
                             "(default: <file>.proofs/rocq/).")
    g_audit.add_argument("--lean-proofs-path", metavar="DIR", default=None,
                        help="Override default Lean proof dir for --audit-proof "
                             "(default: <file>.proofs/lean/).")
    g_audit.add_argument("--reverify-proofs", action="store_true",
                        help="With --audit-proof: actually invoke coqc / "
                             "lake env lean on the cited proof files and check "
                             "that each cited theorem's assumption set is in "
                             "the kernel-axiom allow-list "
                             "(src/pycsl/proof_axiom_allowlist.py). Closes the "
                             "syntactic-only gap of the default --audit-proof. "
                             "Cached by SHA-256 in .audit-cache/. "
                             "See sticky-01.md Phase 0.")
    return parser.parse_args()


def _build_soundness_report(ir_data: Dict[str, Any], filename: str) -> Dict[str, Any]:
    """07-1143 R4 — the Soundness Ledger. Classify every function (and thus its VCs)
    into one of four provenance buckets and record what trust each rests on:

      - Modelled    : body-verified — a real proof.
      - Specified   : a `\\trusted`/`\\abstract` method WITH a contract (ensures) — the
                      contract is assumed (axiomatic), so it enters the TCB.
      - Stubbed     : a `\\trusted`/`\\abstract` method with no contract — proves nothing.
      - Confinement : a method carrying `#@ \\preserves` — its HAPPY-boundary promise is
                      assumed, so it enters the TCB.

    Conservative by construction: any non-body provenance is reported as trust (never
    under-reported). `trusted_dependencies` lists the trusted/abstract callees a Modelled
    function relies on, so a body proof that rests on an assumed stub is visible."""
    funcs = ir_data.get("functions", [])
    trusted_names = {f["name"] for f in funcs if f.get("trusted") or f.get("abstract")}
    counts = {"Modelled": 0, "Specified": 0, "Stubbed": 0, "Confinement": 0}
    vcs: List[Dict[str, Any]] = []
    for f in funcs:
        name = f["name"]
        ens = bool(f.get("contracts", {}).get("ensures"))
        if f.get("preserves"):
            bucket = "Confinement"
        elif f.get("trusted") or f.get("abstract"):
            bucket = "Specified" if ens else "Stubbed"
        else:
            bucket = "Modelled"
        counts[bucket] += 1
        deps = sorted((_collect_calls(f.get("body", [])) & trusted_names) - {name})
        vcs.append({
            "function": name, "bucket": bucket, "has_contract": ens,
            "trusted": bool(f.get("trusted")), "abstract": bool(f.get("abstract")),
            "preserves": bool(f.get("preserves")), "trusted_dependencies": deps,
        })
    return {"file": filename, "summary": counts, "vcs": vcs}


def _print_soundness_report(report: Dict[str, Any]) -> None:
    """Print the R4 Soundness Ledger: machine-parseable JSON, then a human summary."""
    print("=== SOUNDNESS REPORT (JSON) ===")
    print(_json.dumps(report, indent=2))
    print("\n=== SOUNDNESS REPORT (summary) ===")
    s = report["summary"]
    total = sum(s.values())
    print(f"file: {report['file']}   functions/VCs: {total}")
    for bucket in ("Modelled", "Specified", "Stubbed", "Confinement"):
        print(f"  {bucket:<12}: {s[bucket]}")
    tcb = [v for v in report["vcs"] if v["bucket"] in ("Specified", "Confinement")]
    if tcb:
        print("  --- TCB entries (assumed, not body-verified) ---")
        for v in tcb:
            why = ("\\preserves" if v["bucket"] == "Confinement"
                   else "axiomatic contract")
            print(f"    {v['function']}  [{v['bucket']}]  ({why})")
    dep = [v for v in report["vcs"] if v["bucket"] == "Modelled" and v["trusted_dependencies"]]
    if dep:
        print("  --- body proofs resting on trusted/abstract stubs ---")
        for v in dep:
            print(f"    {v['function']}  depends on: {', '.join(v['trusted_dependencies'])}")


def _run_pipeline(source_code: str, memory_model: str, args: argparse.Namespace) -> str:
    """Run Modules 1–6 on *source_code*. Returns WhyML code string."""
    print(f"[*] Parsing and Semantic Analysis for '{args.file}'...")
    print(f"[*] Memory model: {memory_model}")

    # [Modules 1-3] Ingest, Parse, and Weave
    ingestor = Module1_Ingestor(source_code)
    extracted_data = ingestor.process()

    parser_mod = Module2_Parser()
    weaver = Module3_Weaver(source_code, extracted_data, parser_mod)
    unified_ast = weaver.process()

    # [Module 4] Semantic Analysis
    analyzer = Module4_SemanticAnalyzer()
    validated_ast = analyzer.process(unified_ast)

    # [ConcurrencyChecker] Static concurrency analysis (warnings only)
    # [Import classifier] UB-7.4 — C-extension boundary
    from import_classifier import check_imports
    from pathlib import Path as _Path
    _project_root = _Path(__file__).resolve().parents[2]  # …/pycsl/
    check_imports(
        validated_ast,
        stub_dir=_project_root / "src" / "pycsl_lib",
        allow_unverified=getattr(args, "allow_unverified_imports", False),
        filename=getattr(args, "file", "<input>"),
    )

    cc = ConcurrencyChecker(
        validated_ast,
        strict_mode=getattr(args, "strict_concurrent_checks", False),
        filename=getattr(args, "file", "<input>"),
    )
    cc_warnings = cc.check()
    if cc_warnings:
        print(cc.summary())

    # [Module 5] IR Generation
    emitter = Module5_IREmitter(validated_ast)
    json_ir = emitter.generate_json()

    # Validate IR structure before handing off to Module 6
    ir_data = _json.loads(json_ir)
    validate_ir(ir_data)

    # [UB-7.1] Mutation-during-iteration check. Walks function bodies for
    # `for x in C: ...` whose body mutates C (and the loop isn't opted
    # out via `#@ allow_iteration_mutation`). Raises PyCSLSemanticError
    # on the first violation. See ub-catalog §7.1.
    from module6_whyml.ir_scanner import IRScanner as _IRScanner
    from errors import PyCSLSemanticError as _PyCSLSemanticError
    for _func in ir_data.get("functions", []):
        _viols = _IRScanner.find_iteration_mutations(_func.get("body", []))
        if _viols:
            v = _viols[0]
            raise _PyCSLSemanticError(
                f"{args.file} (function '{_func.get('name')}', for-loop near "
                f"line {v.get('loop_line', '?')}): UB-7.1 — the loop body "
                f"mutates the iterated collection '{v.get('iterable_name')}'. "
                f"This is undefined behaviour in CPython "
                f"(iterator state corruption). Either rewrite to iterate "
                f"over a snapshot (`for k in list({v.get('iterable_name')}):`) "
                f"or annotate the loop with `#@ allow_iteration_mutation` "
                f"to acknowledge the boundary. "
                f"See config/skills/pycsl-ub-catalog/SKILL.md §7.1."
            )

    # Multi-file import resolution
    imported_names = _resolve_imports(validated_ast, args.file, ir_data, deep=args.deep)
    # Layers B+C — apply class inheritance (same-file + imported) as an IR pass,
    # then re-sync json_ir (Module 6 is built from it).
    _apply_inheritance(ir_data)
    _apply_composition(ir_data)   # Tier-1 mixin composition (check + flatten)
    _apply_inline_globals(ir_data)   # inline.md: inline method calls on module globals

    # 07-1143 R4: the Soundness Ledger is a provenance view of the fully-resolved IR
    # (after imports/inheritance/composition), so it runs here and short-circuits before
    # WhyML emission / proving.
    if getattr(args, "soundness_report", False):
        _print_soundness_report(_build_soundness_report(ir_data, args.file))
        sys.exit(0)

    json_ir = _json.dumps(ir_data)

    # --fun filter: mark non-selected functions as trusted
    if args.fun:
        ir_data = _json.loads(json_ir)
        all_func_names = {f["name"] for f in ir_data["functions"]}
        fun_names = set(args.fun)
        missing = fun_names - all_func_names
        if missing:
            print(f"[!] Error: Function(s) not found: {', '.join(sorted(missing))}")
            print(f"    Available: {', '.join(sorted(all_func_names))}")
            sys.exit(1)
        call_graph = {f["name"]: _collect_calls(f["body"]) & all_func_names
                      for f in ir_data["functions"]}
        reachable = set(fun_names)
        worklist = list(fun_names)
        while worklist:
            fname = worklist.pop()
            for callee in call_graph.get(fname, set()):
                if callee not in reachable:
                    reachable.add(callee)
                    worklist.append(callee)
        for f in ir_data["functions"]:
            if f["name"] not in reachable:
                f["trusted"] = True
        json_ir = _json.dumps(ir_data)
        verified_names = sorted(reachable & all_func_names)
        trusted_names = sorted(all_func_names - reachable)
        if trusted_names:
            print(f"[*] --fun filter: verifying {verified_names}, trusting {trusted_names}")

    # [Module 6] WhyML Transpilation
    transpiler = Module6_WhyMLTranspiler(
        json_ir, memory_model=memory_model,
        strict_no_exception_propagation=getattr(args, "strict_no_exception_propagation", False),
        strict_hash_eq_consistency=getattr(args, "strict_hash_eq_consistency", False),
        check_behavioral_subtyping=getattr(args, "check_behavioral_subtyping", False),
    )
    return transpiler.transpile()


def _run_proofs(mlw_code: str, mlw_filename: str, provers: List[str], args: argparse.Namespace) -> None:
    """Write *mlw_code* to *mlw_filename*, invoke Why3, handle Rocq proofs and cleanup."""
    with open(mlw_filename, "w") as f:
        f.write(mlw_code)

    if args.no_proof:
        print(f"[+] Verification SUCCESS (--no-proof: WhyML generated, proof skipped).")
        if not args.keep_mlw and os.path.exists(mlw_filename):
            os.remove(mlw_filename)
        sys.exit(0)

    print(f"[*] Running Proof Engine (provers: {' → '.join(provers)})...")
    try:
        # split_vc decomposes each function's monolithic VC into per-invariant/per-branch
        # sub-goals.  Most sub-goals are trivially linear; only genuinely hard arithmetic
        # goals remain, and they benefit from Z3 NIA in isolation (rather than as part of a
        # huge combined query that triggers OOM).
        cmd = ["why3", "prove", "-a", "split_vc"]
        # inductive.md: a universally-quantified CONSEQUENCE of an inductive predicate
        # (`#@ lemma … ensures \forall x; p(x) ==> Q`) is proved by induction on the
        # predicate's derivation, which the SMT backend cannot do alone (it times out).
        # `induction_pr` — applied AFTER `split_vc` has introduced the `p(x)` premise into
        # the hypotheses — discharges it. It is a no-op on goals with no inductive-predicate
        # hypothesis, and is added only when the module declares an inductive predicate, so
        # non-inductive files are unaffected.
        if "\n  inductive " in mlw_code:
            cmd += ["-a", "induction_pr"]
        for p in provers:
            cmd += ["-P", p]
        cmd += ["--timelimit", "30", mlw_filename]

        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout.strip()

        print("\n--- Verification Results ---")
        if output:
            print(output)
        if result.stderr.strip():
            print("\nWarnings/Errors from Why3:")
            print(result.stderr.strip())

        unknown_goals = [line for line in output.splitlines()
                         if "Unknown" in line or "Timeout" in line]
        invalid_goals = [line for line in output.splitlines() if "Invalid" in line]
        smt_proved = len([line for line in output.splitlines() if "Valid" in line])

        if result.returncode == 0 and not unknown_goals and not invalid_goals and ("Valid" in output or not output):
            print(f"\n[+] Verification SUCCESS! All contracts formally proven.")
        else:
            unproven_count = len(unknown_goals) + len(invalid_goals)
            rocq_proved = 0
            proof_dir = None

            if args.rocq_proofs is not None:
                proof_dir = (os.path.splitext(args.file)[0] + ".proofs"
                             if args.rocq_proofs == "__auto__" else args.rocq_proofs)
            else:
                auto_dir = os.path.splitext(args.file)[0] + ".proofs"
                if os.path.isdir(auto_dir):
                    proof_dir = auto_dir

            if proof_dir and os.path.isdir(proof_dir):
                rocq_proved = _check_rocq_proofs(proof_dir, mlw_filename, unknown_goals)

            remaining = unproven_count - rocq_proved
            if remaining <= 0 and rocq_proved > 0:
                print(f"\n[+] Verification SUCCESS! All contracts formally proven "
                      f"({smt_proved} SMT + {rocq_proved} Rocq).")
            else:
                if unknown_goals:
                    print(f"\n[-] {len(unknown_goals)} goal(s) remain unproven after all provers:")
                    for g in unknown_goals:
                        print(f"    {g.strip()}")
                if invalid_goals:
                    print(f"\n[-] {len(invalid_goals)} goal(s) are Invalid:")
                    for g in invalid_goals:
                        print(f"    {g.strip()}")
                if rocq_proved > 0:
                    print(f"\n[*] {rocq_proved} goal(s) proved by Rocq, "
                          f"but {remaining} goal(s) still unproven.")
                print("\n[-] Verification FAILED or INCOMPLETE. Check the solver output.")
                if args.rocq:
                    _generate_rocq_obligations(mlw_filename, args.rocq, unproven_count, args.file)
                    sys.exit(2)
                sys.exit(1)

    except FileNotFoundError:
        print("\n[!] ERROR: 'why3' command not found. Please ensure Why3 is installed and in your PATH.")
        sys.exit(1)
    finally:
        if not args.keep_mlw and os.path.exists(mlw_filename):
            os.remove(mlw_filename)


def _run_audit_mode(args: argparse.Namespace) -> int:
    """Handle --audit-proof / --audit-proof-rocq / --audit-proof-lean.

    Short-circuits the rest of the pipeline. Returns the exit code.

    With --reverify-proofs, after the namespace-presence audit passes,
    each cited proof file is recompiled via coqc / lake env lean and
    its Print Assumptions / #print axioms output is checked against
    the kernel-axiom allow-list (see sticky-01.md Phase 0).
    """
    from pathlib import Path
    from audit_proof import audit_rocq, audit_lean, AuditReport, print_report
    py = Path(args.file)
    rocq_dir = Path(args.rocq_proofs_path) if args.rocq_proofs_path else None
    lean_dir = Path(args.lean_proofs_path) if args.lean_proofs_path else None
    reverify = getattr(args, "reverify_proofs", False)
    project_root = Path(__file__).resolve().parents[2]
    report = AuditReport()
    if args.audit_proof or args.audit_proof_rocq:
        report.extend(audit_rocq(py, rocq_dir, reverify=reverify,
                                  project_root=project_root))
    if args.audit_proof or args.audit_proof_lean:
        report.extend(audit_lean(py, lean_dir, reverify=reverify,
                                  project_root=project_root))
    print_report(report, f"Axiom-attribution audit ({py.name})")
    return report.exit_code


def _resolve_runtime_config(args: argparse.Namespace) -> Tuple[str, List[str]]:
    """Resolve `(memory_model, provers)` from CLI flags and agents-config.json. The CLI
    `--memory-model`/`--prover`/`--provers` flags override the config; the config overrides
    the built-in defaults (hoare; Alt-Ergo then Z3). (Extracted from `main`.)"""
    _config = {}
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "agents", "agents-config.json")
    if os.path.exists(config_path):
        with open(config_path) as _cf:
            _config = _json.load(_cf)

    memory_model = args.memory_model or _config.get("memory-model", "hoare")

    _DEFAULT_PROVERS = ["Alt-Ergo,2.6.2,", "Z3,4.13.3,"]
    if args.prover is not None:
        provers = [args.prover]
    elif args.provers is not None:
        provers = [p.strip() for p in args.provers.split(",,") if p.strip()]
    else:
        cfg_provers = _config.get("provers", _DEFAULT_PROVERS)
        provers = ([p.strip() for p in cfg_provers.split(",,") if p.strip()]
                   if isinstance(cfg_provers, str) else cfg_provers)
    return memory_model, provers


def main() -> None:
    args = _parse_args()

    if not os.path.exists(args.file):
        print(f"[!] Error: File '{args.file}' not found.")
        sys.exit(1)

    # Audit-only mode short-circuits the pipeline.
    if args.audit_proof or args.audit_proof_rocq or args.audit_proof_lean:
        sys.exit(_run_audit_mode(args))

    memory_model, provers = _resolve_runtime_config(args)

    with open(args.file, "r") as f:
        source_code = f.read()

    try:
        mlw_code = _run_pipeline(source_code, memory_model, args)
    except PyCSLError as e:
        print(f"\n[!] PIPELINE ERROR:\n{e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] UNEXPECTED PIPELINE ERROR:\n{e}")
        sys.exit(1)

    base_name = os.path.splitext(args.file)[0]
    mlw_filename = f"{base_name}.mlw" if args.keep_mlw else _make_temp_mlw_path()
    _run_proofs(mlw_code, mlw_filename, provers, args)


if __name__ == "__main__":
    main()
