#!/usr/bin/env python3
"""pycsl-ir-dump.py — Dump Module 5 IR JSON for a PyCSL source file.

Used by the CC.5 byte-diff tooling to extract the canonical IR for
real-corpus tests. The IR is then consumed by `bin/ir-to-rocq-ast.py`
to produce a Rocq AST literal, and by `Module6_WhyMLTranspiler` to
produce the Module 6 WhyML emission. The byte-diff compares the two.

Usage:  bin/pycsl-ir-dump.py <source.py>  [--function NAME] [--resolved]
        Prints the IR JSON to stdout.

With ``--resolved``, the dumped IR is the *resolved* Module-5 IR — i.e. the IR
AFTER the three PURE IR->IR post-Module5 passes that the orchestrator applies
before Module 6 consumes it: ``_apply_inheritance`` (monomorphize base methods
onto subclasses), ``_apply_composition`` (Tier-1 ``compose_from``/``mixin``
flattening) and ``apply_inline_globals`` (inline method calls on module-level
global instances). These three operate on the IR dict alone (no dependency
context), so they are safe to run from this tool. Import resolution
(``_resolve_imports``) needs dependency-loading context and is NOT applied here;
drivers that depend on cross-file imports still need their own follow-on.
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
from frontend.Module4_SemanticAnalyzer import Module4_SemanticAnalyzer  # noqa: E402
from frontend.Module5_IREmitter import Module5_IREmitter  # noqa: E402


def dump_ir(source_path: str, resolved: bool = False) -> str:
    src = Path(source_path).read_text()
    # Module 1: ingest Python source
    ingestor = Module1_Ingestor(src)
    extracted = ingestor.process()
    # Modules 2+3: parse PyCSL annotations and weave
    parser_mod = Module2_Parser()
    weaver = Module3_Weaver(src, extracted, parser_mod)
    unified_ast = weaver.process()
    # Module 4: semantic analysis
    analyzer = Module4_SemanticAnalyzer()
    validated_ast = analyzer.process(unified_ast)
    # Module 5: IR emission
    ir_json = Module5_IREmitter(validated_ast).generate_json()
    if not resolved:
        return ir_json
    # --resolved: apply the three PURE IR->IR post-Module5 passes that the
    # orchestrator runs before Module 6 consumes the IR. These take only the
    # IR dict (no dependency/import context) so they are safe here. Import
    # resolution (_resolve_imports) is intentionally NOT applied — it needs
    # dependency-loading context and is out of scope for this tool.
    from pycsl import _apply_inheritance, _apply_composition  # noqa: E402
    from ir_inline import apply_inline_globals  # noqa: E402
    ir_data = json.loads(ir_json)
    _apply_inheritance(ir_data)
    _apply_composition(ir_data)
    apply_inline_globals(ir_data)
    return json.dumps(ir_data)


def main() -> None:
    args = sys.argv[1:]
    fn_filter = None
    resolved = False
    if "--resolved" in args:
        resolved = True
        args.remove("--resolved")
    if "--function" in args:
        i = args.index("--function")
        fn_filter = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1:
        print("usage: pycsl-ir-dump.py <source.py> [--function NAME] [--resolved]",
              file=sys.stderr)
        sys.exit(2)
    ir_json = dump_ir(args[0], resolved=resolved)
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
