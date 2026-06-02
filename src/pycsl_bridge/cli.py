"""pycsl-bridge command-line entry point.

Usage:
    pycsl-bridge --rocq-config rocq.toml --lean-config lean.toml \\
                 [--manifest pycsl-bridge.manifest.toml] \\
                 [--on-disagreement halt|warn|force] \\
                 [--check] [--no-emit] [--no-check] [-v]

Workflow (pycsl-bridge-plan.md §4):

  1. Run rocq2pycsl + lean2pycsl in IR-dump mode using the two configs.
  2. Reconcile the envelopes via the canonicalizer.
  3. On disagreement: halt (default), warn, or force-emit per the flag.
  4. Write the annotated Python (chosen side per qualname, with
     informational `# proof rocq:` / `# proof lean:` traceability
     lines).
  5. Write/refresh the manifest.
  6. Optionally re-run pycsl on the emitted file.

Trust attribution is emitted as regular Python comments (`# proof
rocq: …` / `# proof lean: …`) for v1. The full `#@ proof <prover>:
<qualname>` PyCSL directive specified in the plan §2.4 is deferred
until the corresponding parser extension lands.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

from pycsl_emit.checker import Verdict, run_pycsl
from pycsl_emit.emitter import annotate_source
from pycsl_emit.translator import DividesStyle, NameMap, render

from .linker.manifest import Manifest, check_manifest, write_manifest
from .reconciler import (
    QualnameResult,
    Reconciliation,
    Status,
    format_disagreement,
    reconcile_envelopes,
)


# ──────────────────────────────────────────────────────────────────────


@dataclass
class BridgeOutcome:
    reconciliation: Reconciliation
    annotated_source: str | None
    annotated_path: Path | None
    manifest_path: Path | None
    verdict: Verdict | None
    disagreements: list[QualnameResult] = field(default_factory=list)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        outcome = run(
            rocq_config=Path(args.rocq_config),
            lean_config=Path(args.lean_config),
            python_src=Path(args.python_src) if args.python_src else None,
            output=Path(args.output) if args.output else None,
            manifest=Path(args.manifest) if args.manifest else None,
            on_disagreement=args.on_disagreement,
            check_manifest_only=args.check,
            no_emit=args.no_emit,
            no_check=args.no_check,
            verbose=args.verbose,
        )
    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"[!] pycsl-bridge: {e}", file=sys.stderr)
        return 2

    if outcome.disagreements and args.on_disagreement == "halt":
        return 1
    if outcome.verdict is not None and not outcome.verdict.all_valid:
        return 1
    return 0


def run(
    *,
    rocq_config: Path,
    lean_config: Path,
    python_src: Path | None = None,
    output: Path | None = None,
    manifest: Path | None = None,
    on_disagreement: str = "halt",
    check_manifest_only: bool = False,
    no_emit: bool = False,
    no_check: bool = False,
    verbose: bool = False,
) -> BridgeOutcome:
    """Programmatic API. Used by tests and by callers that want the
    structured outcome."""
    rocq_env = _dump("rocq2pycsl", rocq_config, verbose=verbose)
    lean_env = _dump("lean2pycsl", lean_config, verbose=verbose)
    rec = reconcile_envelopes(rocq_env, lean_env)

    if verbose:
        _print_reconciliation_summary(rec)

    if check_manifest_only:
        if manifest is None:
            raise ValueError("--check requires --manifest")
        ok = check_manifest(rec, manifest)
        if not ok:
            print(
                f"[!] manifest drift: regenerate with "
                f"`pycsl-bridge --rocq-config {rocq_config} "
                f"--lean-config {lean_config} --manifest {manifest}`",
                file=sys.stderr,
            )
            raise ValueError("manifest out of date")
        if verbose:
            print(f"[+] manifest {manifest} is up to date")
        return BridgeOutcome(
            reconciliation=rec,
            annotated_source=None,
            annotated_path=None,
            manifest_path=manifest,
            verdict=None,
            disagreements=rec.disagreements,
        )

    disagreements = rec.disagreements
    if disagreements and on_disagreement == "halt":
        for r in disagreements:
            print(format_disagreement(r))
        # Manifest is still written so CI can compare against the
        # disagreement state — the manifest itself records the status.
        manifest_path = (
            write_manifest(rec, manifest) if manifest is not None else None
        )
        return BridgeOutcome(
            reconciliation=rec,
            annotated_source=None,
            annotated_path=None,
            manifest_path=manifest_path,
            verdict=None,
            disagreements=disagreements,
        )

    if disagreements and on_disagreement == "warn":
        for r in disagreements:
            print(format_disagreement(r), file=sys.stderr)

    # Phase 4: emit annotated Python.
    annotated_source: str | None = None
    annotated_path: Path | None = None
    if not no_emit:
        if python_src is None:
            raise ValueError("--python-src required unless --no-emit is set")
        annotated_source = _emit_dual_attribution(python_src, rec)
        annotated_path = output or python_src.with_suffix(".annotated.py")
        annotated_path.parent.mkdir(parents=True, exist_ok=True)
        annotated_path.write_text(annotated_source)
        if verbose:
            print(f"[+] wrote {annotated_path}")

    # Phase 5: refresh manifest.
    manifest_path: Path | None = None
    if manifest is not None:
        manifest_path = write_manifest(rec, manifest)
        if verbose:
            print(f"[+] wrote {manifest_path}")

    # Phase 6: re-run pycsl.
    verdict: Verdict | None = None
    if annotated_path is not None and not no_check:
        verdict = run_pycsl(annotated_path)
        if verbose:
            print(f"[*] pycsl: {verdict.summary()}")

    return BridgeOutcome(
        reconciliation=rec,
        annotated_source=annotated_source,
        annotated_path=annotated_path,
        manifest_path=manifest_path,
        verdict=verdict,
        disagreements=disagreements,
    )


# ──────────────────────────────────────────────────────────────────────


def _dump(provenance: str, config_path: Path, *, verbose: bool) -> dict[str, Any]:
    """Invoke `<tool>.cli.dump_ir` directly. Faster and more robust
    than shelling out to the CLI binaries."""
    if provenance == "rocq2pycsl":
        from rocq2pycsl.cli import dump_ir as _dump_ir
        from rocq2pycsl.extractor import Backend as _Backend
    else:
        assert provenance == "lean2pycsl"
        from lean2pycsl.cli import dump_ir as _dump_ir
        from lean2pycsl.extractor import Backend as _Backend
    return _dump_ir(config_path=config_path, backend=_Backend.LARK, verbose=verbose)


def _emit_dual_attribution(python_src: Path, rec: Reconciliation) -> str:
    """Annotate the Python source, picking each qualname's chosen side
    and injecting `#@ proof rocq:`/`#@ proof lean:` trace directives
    (PyCSL §2.1.11).

    The proof-attribution lines are prepended to the `#@` annotation
    block so they appear flush above `requires` in the emitted file.
    `Module2_Parser` accepts them; `Module6_WhyMLTranspiler` drops
    them — they exist purely for traceability.
    """
    current = python_src.read_text()
    for qn, r in rec.results.items():
        chosen = r.chosen
        attribution = _attribution_lines(r)
        annotations = attribution + _contract_to_lines(chosen)
        current = annotate_source(
            current,
            chosen["python_name"],
            annotations,
        )
    return current


def _contract_to_lines(chosen: dict[str, Any]) -> list[str]:
    style = DividesStyle(chosen["divides_style"])
    # Honor the proof-side → Python-side arg_map carried through the
    # IR dump (Phase 6 of tuesday-01: class methods need `balance` →
    # `self._balance` rewrites).
    raw_map = chosen.get("arg_map") or {}
    nm = NameMap(mapping=dict(raw_map)) if raw_map else NameMap.identity()
    out: list[str] = []
    for r in chosen["requires"]:
        out.append(f"requires {render(r, style=style, names=nm)}")
    for e in chosen["ensures"]:
        out.append(f"ensures {render(e, style=style, names=nm)}")
    out.append(f"assigns {chosen['assigns']}")
    if chosen.get("variant") is not None:
        out.append(f"\\variant {render(chosen['variant'], style=style, names=nm)}")
    elif chosen.get("diverges"):
        out.append("\\diverges")
    return out


def _attribution_lines(r: QualnameResult) -> list[str]:
    """Build the `#@ proof rocq: …` / `#@ proof lean: …` traceability
    directives (PyCSL §2.1.11).

    Returned strings omit the leading `#@ ` — the annotator prepends
    that token when materializing the lines.
    """
    lines: list[str] = []
    if r.rocq is not None:
        for t in r.rocq["theorems"]:
            lines.append(f"proof rocq: {t}")
    if r.lean is not None:
        for t in r.lean["theorems"]:
            lines.append(f"proof lean: {t}")
    return lines


def _print_reconciliation_summary(rec: Reconciliation) -> None:
    counts = {s: len(rec.by_status(s)) for s in Status}
    parts = ", ".join(f"{s.value}={counts[s]}" for s in Status)
    print(f"[*] reconciliation: {parts}")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pycsl-bridge",
        description="Reconcile rocq2pycsl + lean2pycsl IR dumps and emit "
                    "annotated Python with dual attribution.",
    )
    p.add_argument("--rocq-config", required=True)
    p.add_argument("--lean-config", required=True)
    p.add_argument("--python-src", help="Hand-ported Python source file")
    p.add_argument("--output", help="Where to write the annotated file "
                                    "(default: alongside --python-src)")
    p.add_argument("--manifest", help="Path to the pycsl-bridge manifest")
    p.add_argument(
        "--on-disagreement",
        choices=["halt", "warn", "force"],
        default="halt",
        help="halt: print diff and exit 1 (default). "
             "warn: emit anyway, log to stderr. "
             "force: emit silently using the rocq side.",
    )
    p.add_argument("--check", action="store_true",
                   help="Compare the on-disk manifest against the regenerated "
                        "one and exit non-zero on drift")
    p.add_argument("--no-emit", action="store_true",
                   help="Skip annotated-Python emission")
    p.add_argument("--no-check", action="store_true",
                   help="Skip the final pycsl run on the emitted file")
    p.add_argument("-v", "--verbose", action="store_true")
    return p


if __name__ == "__main__":
    sys.exit(main())
