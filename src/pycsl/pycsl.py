#!/usr/bin/env python3
import argparse
import ast as _ast
import json as _json
import os
import sys
import subprocess

# Ensure sibling modules are importable regardless of cwd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the PyCSL Pipeline Modules
from Module1_Ingestor import Module1_Ingestor
from Module2_Parser import Module2_Parser
from Module3_Weaver import Module3_Weaver
from Module4_SemanticAnalyzer import Module4_SemanticAnalyzer, PyCSLSemanticError
from Module5_IREmitter import Module5_IREmitter
from Module6_WhyMLTranspiler import Module6_WhyMLTranspiler


# ── Multi-file import helpers ──────────────────────────────────

def _collect_calls(obj):
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


def _extract_imports(tree):
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


def _rewrite_ir_calls(obj, old_name, new_name):
    """Recursively rewrite Call nodes: func old_name → new_name."""
    if isinstance(obj, dict):
        if obj.get("type") == "Call" and obj.get("func") == old_name:
            obj["func"] = new_name
        for v in obj.values():
            _rewrite_ir_calls(v, old_name, new_name)
    elif isinstance(obj, list):
        for item in obj:
            _rewrite_ir_calls(item, old_name, new_name)


def _resolve_module_path(module_dotted, level, main_file):
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


def _get_module_exports(filepath):
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


def _process_dependency(filepath, needed_names, cache,
                        deep=False, processing_set=None):
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


def _resolve_imports(validated_ast, main_file, ir_data,
                     deep=False, cache=None, processing_set=None):
    """Detect imports, resolve source files, inject trusted stubs into ir_data.
    Returns set of imported function local names.
    With deep=True, recursively resolve dependencies' own imports."""
    imports = _extract_imports(validated_ast)
    if not imports:
        return set()

    # Determine which functions are actually called in the main file's IR
    all_calls = set()
    for f in ir_data["functions"]:
        all_calls |= _collect_calls(f["body"])

    if cache is None:
        cache = {}
    if processing_set is None:
        processing_set = set()
    imported_names = set()
    from collections import defaultdict

    # Separate direct name imports, wildcard imports, and module imports
    direct_imports = [(l, o, m, lv)
                      for l, o, m, lv, is_mod in imports
                      if not is_mod and l != '*']
    wildcard_imports = [(m, lv)
                        for l, o, m, lv, is_mod in imports
                        if l == '*']
    module_imports = [(l, o, m, lv)
                      for l, o, m, lv, is_mod in imports if is_mod]

    # --- Handle direct name imports (from mod import name) ---
    by_module = defaultdict(list)
    for local, original, module_path, level in direct_imports:
        by_module[(module_path, level)].append((local, original))

    for (module_path, level), names in by_module.items():
        needed = [(local, orig) for local, orig in names
                  if local in all_calls]
        if not needed:
            continue

        resolved = _resolve_module_path(module_path, level, main_file)
        if resolved is None:
            for local, orig in needed:
                print(f"[*] Import '{module_path}.{orig}': external module, "
                      f"no local source found — skipping (add \\trusted stub "
                      f"if verification of callers needs its contract)")
            continue

        orig_names = [orig for _, orig in needed]
        dep_funcs = _process_dependency(resolved, orig_names, cache,
                                        deep=deep,
                                        processing_set=processing_set)

        for func_ir in dep_funcs:
            for local, orig in needed:
                if func_ir["name"] == orig and local != orig:
                    func_ir["name"] = local
            existing = {f["name"] for f in ir_data["functions"]}
            if func_ir["name"] not in existing:
                ir_data["functions"].insert(0, func_ir)
                imported_names.add(func_ir["name"])

        resolved_locals = [local for local, _ in needed]
        print(f"[*] Imported from '{module_path}': "
              f"{resolved_locals} (trusted stubs)")

    # --- Handle wildcard imports (from mod import *) ---
    for module_path, level in wildcard_imports:
        resolved = _resolve_module_path(module_path, level, main_file)
        if resolved is None:
            print(f"[*] Import '{module_path}.*': external module, "
                  f"no local source found — skipping")
            continue

        # Process the module to cache its IR
        _process_dependency(resolved, [], cache,
                            deep=deep, processing_set=processing_set)
        abs_resolved = os.path.abspath(resolved)
        dep_ir = cache.get(abs_resolved)
        if dep_ir is None:
            continue

        # Determine exported names (respect __all__ if present)
        explicit_all = _get_module_exports(resolved)
        if explicit_all is not None:
            exported = explicit_all
        else:
            exported = {f["name"] for f in dep_ir["functions"]
                        if not f["name"].startswith("_")}

        # Filter to names actually called in the main file
        needed_names = sorted(exported & all_calls)
        if not needed_names:
            continue

        dep_funcs = _process_dependency(resolved, needed_names, cache,
                                        deep=deep,
                                        processing_set=processing_set)
        for func_ir in dep_funcs:
            existing = {f["name"] for f in ir_data["functions"]}
            if func_ir["name"] not in existing:
                ir_data["functions"].insert(0, func_ir)
                imported_names.add(func_ir["name"])

        print(f"[*] Imported from '{module_path}.*': "
              f"{needed_names} (wildcard, trusted stubs)")

    # --- Handle module imports (import mod / import mod as alias) ---
    # Calls appear as dotted names: "alias.func" or "mod.sub.func"
    for local_name, original_name, module_path, level in module_imports:
        prefix = local_name + "."
        # Find all calls matching this module prefix
        matching_calls = [c for c in all_calls if c.startswith(prefix)]
        if not matching_calls:
            continue

        resolved = _resolve_module_path(module_path, level, main_file)
        if resolved is None:
            for call in matching_calls:
                func_name = call[len(prefix):]
                print(f"[*] Import '{module_path}.{func_name}': external module, "
                      f"no local source found — skipping")
            continue

        # Extract bare function names from dotted calls
        func_names = [call[len(prefix):] for call in matching_calls]
        dep_funcs = _process_dependency(resolved, func_names, cache,
                                        deep=deep,
                                        processing_set=processing_set)

        for func_ir in dep_funcs:
            existing = {f["name"] for f in ir_data["functions"]}
            if func_ir["name"] not in existing:
                ir_data["functions"].insert(0, func_ir)
                imported_names.add(func_ir["name"])

        # Rewrite dotted calls in IR to bare function names
        for call in matching_calls:
            bare_name = call[len(prefix):]
            for f in ir_data["functions"]:
                _rewrite_ir_calls(f, call, bare_name)

        print(f"[*] Imported from '{module_path}': "
              f"{func_names} (trusted stubs, module-qualified)")

    return imported_names

def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="PyCSL: Python Contract Specification Language Verifier")
    parser.add_argument("file", help="The Python file to verify")
    parser.add_argument("-p", "--prover", default=None,
                        help="Single prover to use (e.g. 'Alt-Ergo,2.6.2,' or 'Z3,4.13.3,'). "
                             "Overrides --provers and agents-config.json.")
    parser.add_argument("--provers", default=None,
                        help="Comma-separated list of Why3 prover IDs to try in order "
                             "(e.g. 'Alt-Ergo,2.6.2,,Z3,4.13.3,'). "
                             "Why3 tries each prover per goal and accepts the first Valid. "
                             "Overrides agents-config.json. "
                             "Default: Alt-Ergo then Z3.")
    parser.add_argument("--memory-model", default=None,
                        choices=["hoare", "typed", "store"],
                        help="Memory model for WhyML emission (default: hoare). "
                             "'typed' and 'store' use a global heap (map loc int).")
    parser.add_argument("--keep-mlw", action="store_true", 
                        help="Keep the generated WhyML (.mlw) file for debugging")
    parser.add_argument("--fun", action="append", default=None, metavar="NAME",
                        help="Only verify the named function and its transitive "
                             "call-dependencies (may be repeated). "
                             "Other functions become trusted stubs.")
    parser.add_argument("--deep", action="store_true",
                        help="Recursively resolve transitive imports in "
                             "dependency files (default: only direct imports "
                             "of the main file are resolved).")
    
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"[!] Error: File '{args.file}' not found.")
        sys.exit(1)

    # Load agents-config.json once for all config resolution
    _config = {}
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "agents", "agents-config.json")
    if os.path.exists(config_path):
        with open(config_path) as _cf:
            _config = _json.load(_cf)

    # Resolve memory model: CLI flag > agents-config.json > default "hoare"
    memory_model = args.memory_model
    if memory_model is None:
        memory_model = _config.get("memory-model", "hoare")

    # Resolve prover list: --prover (single) > --provers (list) > agents-config.json > default
    _DEFAULT_PROVERS = ["Alt-Ergo,2.6.2,", "Z3,4.13.3,"]
    if args.prover is not None:
        # --prover overrides everything: single prover, no fallback
        provers = [args.prover]
    elif args.provers is not None:
        # --provers: caller-supplied ordered list (separator is the Why3 prover ID separator)
        # Each prover ID contains commas so we split on ",," (double-comma = ID boundary)
        # Support both "P1,,P2" and "P1,P2" (the latter for simple names like "z3")
        provers = [p.strip() for p in args.provers.split(",,") if p.strip()]
    else:
        cfg_provers = _config.get("provers", _DEFAULT_PROVERS)
        if isinstance(cfg_provers, str):
            provers = [p.strip() for p in cfg_provers.split(",,") if p.strip()]
        else:
            provers = cfg_provers

    with open(args.file, "r") as f:
        source_code = f.read()

    print(f"[*] Parsing and Semantic Analysis for '{args.file}'...")
    print(f"[*] Memory model: {memory_model}")

    try:
        # [Modules 1-3] Ingest, Parse, and Weave
        ingestor = Module1_Ingestor(source_code)
        extracted_data = ingestor.process()

        parser_mod = Module2_Parser()
        weaver = Module3_Weaver(source_code, extracted_data, parser_mod)
        unified_ast = weaver.process()

        # [Module 4] Semantic Analysis
        analyzer = Module4_SemanticAnalyzer()
        validated_ast = analyzer.process(unified_ast)

        # [Module 5] IR Generation
        emitter = Module5_IREmitter(validated_ast)
        json_ir = emitter.generate_json()

        # Multi-file import resolution: detect imports, resolve source files,
        # inject imported functions as trusted stubs into the IR.
        ir_data = _json.loads(json_ir)
        imported_names = _resolve_imports(validated_ast, args.file, ir_data,
                                          deep=args.deep)
        if imported_names:
            json_ir = _json.dumps(ir_data)

        # --fun filter: mark non-selected (and non-dependency) functions as trusted
        if args.fun:
            ir_data = _json.loads(json_ir)
            all_func_names = {f["name"] for f in ir_data["functions"]}

            # Validate that every --fun name exists
            fun_names = set(args.fun)
            missing = fun_names - all_func_names
            if missing:
                print(f"[!] Error: Function(s) not found: {', '.join(sorted(missing))}")
                print(f"    Available: {', '.join(sorted(all_func_names))}")
                sys.exit(1)

            call_graph = {}
            for f in ir_data["functions"]:
                call_graph[f["name"]] = _collect_calls(f["body"]) & all_func_names

            # Transitive closure via BFS
            reachable = set(fun_names)
            worklist = list(fun_names)
            while worklist:
                fname = worklist.pop()
                for callee in call_graph.get(fname, set()):
                    if callee not in reachable:
                        reachable.add(callee)
                        worklist.append(callee)

            # Mark non-reachable functions as trusted
            for f in ir_data["functions"]:
                if f["name"] not in reachable:
                    f["trusted"] = True
            json_ir = _json.dumps(ir_data)

            verified_names = sorted(reachable & all_func_names)
            trusted_names = sorted(all_func_names - reachable)
            if trusted_names:
                print(f"[*] --fun filter: verifying {verified_names}, trusting {trusted_names}")

        # [Module 6] WhyML Transpilation
        transpiler = Module6_WhyMLTranspiler(json_ir, memory_model=memory_model)
        mlw_code = transpiler.transpile()

    except SyntaxError as e:
        print(f"\n[!] SYNTAX ERROR:\n{e}")
        sys.exit(1)
    except PyCSLSemanticError as e:
        print(f"\n[!] SEMANTIC ERROR:\n{e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] UNEXPECTED PIPELINE ERROR:\n{e}")
        sys.exit(1)

    # File handling for the WhyML intermediate file
    base_name = os.path.splitext(args.file)[0]
    mlw_filename = f"{base_name}.mlw" if args.keep_mlw else ".pycsl_temp.mlw"
    
    with open(mlw_filename, "w") as f:
        f.write(mlw_code)

    print(f"[*] Running Proof Engine (provers: {' → '.join(provers)})...")
    try:
        # split_vc decomposes each function's monolithic VC into per-invariant/per-branch
        # sub-goals.  Most sub-goals are trivially linear; only genuinely hard arithmetic
        # goals remain, and they benefit from Z3 NIA in isolation (rather than as part of a
        # huge combined query that triggers OOM).
        cmd = ["why3", "prove", "-a", "split_vc"]
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

        # Determine which goals (if any) remain unproven
        unknown_goals = [line for line in output.splitlines()
                         if "Unknown" in line or "Timeout" in line]
        invalid_goals = [line for line in output.splitlines() if "Invalid" in line]

        if result.returncode == 0 and not unknown_goals and not invalid_goals and ("Valid" in output or not output):
            print("\n[+] Verification SUCCESS! All contracts formally proven.")
        else:
            if unknown_goals:
                print(f"\n[-] {len(unknown_goals)} goal(s) remain unproven after all provers:")
                for g in unknown_goals:
                    print(f"    {g.strip()}")
            if invalid_goals:
                print(f"\n[-] {len(invalid_goals)} goal(s) are Invalid:")
                for g in invalid_goals:
                    print(f"    {g.strip()}")
            print("\n[-] Verification FAILED or INCOMPLETE. Check the solver output.")
            sys.exit(1)

    except FileNotFoundError:
        print("\n[!] ERROR: 'why3' command not found. Please ensure Why3 is installed and in your PATH.")
        sys.exit(1)
    finally:
        # Clean up the temporary file unless the user asked to keep it
        if not args.keep_mlw and os.path.exists(mlw_filename):
            os.remove(mlw_filename)

if __name__ == "__main__":
    main()
