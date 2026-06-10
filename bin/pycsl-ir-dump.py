#!/usr/bin/env python3
"""pycsl-ir-dump.py — Dump Module 5 IR JSON for a PyCSL source file.

Used by the CC.5 byte-diff tooling to extract the canonical IR for
real-corpus tests. The IR is then consumed by `bin/ir-to-rocq-ast.py`
to produce a Rocq AST literal, and by `Module6_WhyMLTranspiler` to
produce the Module 6 WhyML emission. The byte-diff compares the two.

Usage:  bin/pycsl-ir-dump.py <source.py>  [--function NAME] [--resolved] [--deep]
        Prints the IR JSON to stdout.

With ``--resolved``, the dumped IR is the *resolved* Module-5 IR — i.e. the IR
AFTER the FOUR post-Module5 IR-resolution passes the orchestrator applies before
Module 6 consumes it, via the front-end's single resolution entry
``frontend.ir_resolve.resolve`` (relocated there in refactor.md Phase C / C2b).
The passes run IN ORDER: (1) ``resolve_imports`` (load dependency files and
inject the imported functions/classes the driver calls), (2) ``apply_inheritance``
(monomorphize base methods onto subclasses), (3) ``apply_composition`` (Tier-1
``compose_from``/``mixin`` flattening) and (4) ``apply_inline_globals`` (inline
method calls on module-level global instances). Import resolution uses the SOURCE
PATH to locate dependency files; ``--deep`` recurses transitive imports (matching
``pycsl --deep``). For a driver with no imports, ``resolve_imports`` is a no-op,
so ``--resolved`` output is byte-identical to the historical 3-pass application.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

# Use venv site-packages if available.
ROOT = Path(__file__).resolve().parent.parent
VENV_SP = ROOT / ".venv" / "lib"
for candidate in VENV_SP.glob("python*/site-packages"):
    sys.path.insert(0, str(candidate))

sys.path.insert(0, str(ROOT / "src" / "pycsl"))

from frontend.Module1_Ingestor import Module1_Ingestor   # noqa: E402
from frontend.Module2_Parser import Module2_Parser        # noqa: E402
from frontend.Module3_Weaver import Module3_Weaver       # noqa: E402
from frontend.Module5_IREmitter import Module5_IREmitter  # noqa: E402


def dump_ir(source_path: str, resolved: bool = False, deep: bool = False) -> str:
    src = Path(source_path).read_text()
    # Module 1: ingest Python source
    ingestor = Module1_Ingestor(src)
    extracted = ingestor.process()
    # Modules 2+3: parse PyCSL annotations and weave
    parser_mod = Module2_Parser()
    weaver = Module3_Weaver(src, extracted, parser_mod)
    unified_ast = weaver.process()
    # Module 4 DROPPED (B-final reorder): semantic checks moved to the IR seam.
    # Module 5: IR emission (straight from the woven AST)
    ir_json = Module5_IREmitter(unified_ast).generate_json()
    if not resolved:
        return ir_json
    # --resolved: apply the SAME four post-Module5 IR-resolution passes the
    # orchestrator (pycsl.py `_run_pipeline`) runs before Module 6 consumes the
    # IR, via the front-end's single resolution entry `frontend.ir_resolve.resolve`.
    # The passes run IN ORDER: import resolution → inheritance → composition →
    # inline-globals. Import resolution needs the SOURCE PATH (to locate
    # dependency files) and `deep` (recurse transitive imports); the AST
    # argument is threaded for call-site compatibility but no longer consulted
    # (the import LIST is IR-sourced via ir_data["imports"]).
    # When the driver has no imports, `resolve_imports` is a no-op, so the
    # 4-pass `resolve` is byte-identical to the historical 3-pass application.
    from frontend.ir_resolve import resolve as _ir_resolve  # noqa: E402
    import contextlib  # noqa: E402
    ir_data = json.loads(ir_json)
    # `resolve_imports` prints informational "[*] Imported from ..." lines to
    # stdout (as the full pipeline does). This tool's contract is that stdout
    # carries ONLY the IR JSON, so redirect those lines to stderr.
    with contextlib.redirect_stdout(sys.stderr):
        _ir_resolve(ir_data, unified_ast, source_path, deep=deep)
    return json.dumps(ir_data)


def main() -> None:
    args = sys.argv[1:]
    fn_filter = None
    resolved = False
    deep = False
    if "--resolved" in args:
        resolved = True
        args.remove("--resolved")
    if "--deep" in args:
        deep = True
        args.remove("--deep")
    if "--function" in args:
        i = args.index("--function")
        fn_filter = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1:
        print("usage: pycsl-ir-dump.py <source.py> [--function NAME] [--resolved] [--deep]",
              file=sys.stderr)
        sys.exit(2)
    ir_json = dump_ir(args[0], resolved=resolved, deep=deep)
    if fn_filter:
        data = json.loads(ir_json)
        data["functions"] = [f for f in data["functions"]
                             if f.get("name") == fn_filter]
        ir_json = json.dumps(data, indent=2)
    else:
        ir_json = json.dumps(json.loads(ir_json), indent=2)
    print(ir_json)


if __name__ == "__main__":
    main()
