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
