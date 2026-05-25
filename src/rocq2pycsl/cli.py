"""rocq2pycsl command-line entry point.

Usage:
    rocq2pycsl --config rocq2pycsl.toml [--backend lark|serapi]
               [--dry-run] [--no-check] [--strict] [--verbose]

Workflow per rocq2pycsl-plan.md §3:

  Phase 0: scaffold              (handled by package install)
  Phase 1: extract               (extractor.extract)
  Phase 2: translate             (translator.translate_function)
  Phase 3: emit annotated Python (pycsl_emit.emitter.annotate_source)
  Phase 4: verify round-trip     (pycsl_emit.checker.run_pycsl)

The TOML schema follows rocq2pycsl-plan §6:

    [input]
    rocq    = "proofs/Euclid.v"
    python  = "src/euclid.py"
    output  = "src/euclid.annotated.py"

    [pycsl]
    extra_flags = ["--memory-model", "hoare"]
    prover      = "Alt-Ergo,2.6.2,"

    [functions.gcd]
    python_name      = "gcd"
    spec_theorems    = ["gcd_divides", "gcd_greatest"]
    arg_map          = { a = "a", b = "b" }
    divides_style    = "operational"
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from pycsl_emit.checker import Verdict, run_pycsl
from pycsl_emit.config import Config, load_config
from pycsl_emit.emitter import annotate_source
from pycsl_emit.translator import render

from .extractor import Backend, extract
from .extractor.selector import select
from .translator import FunctionContract, translate_function


# ──────────────────────────────────────────────────────────────────────


@dataclass
class RunOutcome:
    """Final status: how many functions translated, how many obligations valid."""
    annotated_path: Path
    annotated_source: str
    functions: dict[str, FunctionContract]
    verdict: Verdict | None  # None when --no-check or extraction failed


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        outcome = run(
            config_path=Path(args.config),
            backend=Backend(args.backend),
            dry_run=args.dry_run,
            no_check=args.no_check,
            strict=args.strict,
            verbose=args.verbose,
        )
    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"[!] rocq2pycsl: {e}", file=sys.stderr)
        return 2

    if outcome.verdict is not None and not outcome.verdict.all_valid:
        # pycsl ran but at least one obligation failed.
        if args.verbose:
            for o in outcome.verdict.unproven():
                print(f"  unproven: {o.theorem} ({o.kind}): {o.detail}")
        return 1
    return 0


def run(
    *,
    config_path: Path,
    backend: Backend = Backend.LARK,
    dry_run: bool = False,
    no_check: bool = False,
    strict: bool = False,
    verbose: bool = False,
) -> RunOutcome:
    """Programmatic API mirroring the CLI. Used by tests and by callers
    that want to consume the structured outcome."""
    cfg = load_config(config_path)
    rocq_path = _resolve_rocq_path(cfg, config_path)

    # Phase 1: extract.
    mod = extract(rocq_path, backend=backend)
    raw_source = Path(rocq_path).read_text()
    if verbose:
        print(
            f"[*] extracted {len(mod.theorems)} theorem(s) and "
            f"{len(mod.functions)} definition(s) from {rocq_path}"
        )

    # Phase 2: translate each configured function.
    contracts: dict[str, FunctionContract] = {}
    for qualname, spec in cfg.functions.items():
        func = mod.function(spec.python_name)
        if func is None:
            raise KeyError(
                f"function {spec.python_name!r} not found in {rocq_path}; "
                f"available: {[f.name for f in mod.functions]}"
            )
        explicit = spec.raw.get("spec_theorems")
        sel = select(
            mod,
            func,
            explicit=explicit,
            raw_source=raw_source,
            allow_heuristic=bool(spec.raw.get("allow_heuristic", False)),
        )
        if not sel.theorems:
            raise KeyError(
                f"no contracts selected for {qualname}; "
                f"add `spec_theorems = [...]` to the [functions.{qualname}] "
                f"TOML section or `(* @pycsl-spec {func.name} *)` markers in "
                f"the .v source"
            )
        if verbose:
            print(
                f"[*] {qualname}: {sel.rule} selection picked "
                f"{[t.name for t in sel.theorems]}"
            )

        contract = translate_function(func, sel.theorems, strict=strict)
        if verbose and contract.unsupported:
            for thm, reason, _ in contract.unsupported:
                print(f"    skipped {thm}: {reason}")
        contracts[qualname] = contract

    # Phase 3: emit annotated Python.
    python_path = _resolve(cfg.python, config_path)
    output_path = _resolve(cfg.output, config_path)
    annotated = _emit_all(python_path.read_text(), cfg, contracts)

    if dry_run:
        if verbose:
            print(f"[*] --dry-run: not writing {output_path}")
        return RunOutcome(
            annotated_path=output_path,
            annotated_source=annotated,
            functions=contracts,
            verdict=None,
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(annotated)
    if verbose:
        print(f"[+] wrote {output_path}")

    # Phase 4: verification round-trip.
    if no_check:
        return RunOutcome(
            annotated_path=output_path,
            annotated_source=annotated,
            functions=contracts,
            verdict=None,
        )

    verdict = run_pycsl(
        output_path,
        extra_args=cfg.pycsl.cli_args(),
        timeout=cfg.pycsl.timeout,
    )
    if verbose:
        print(f"[*] pycsl: {verdict.summary()}")

    return RunOutcome(
        annotated_path=output_path,
        annotated_source=annotated,
        functions=contracts,
        verdict=verdict,
    )


# ──────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="rocq2pycsl",
        description="Extract PyCSL contracts from a Rocq .v file.",
    )
    p.add_argument("--config", required=True, help="Path to TOML config")
    p.add_argument(
        "--backend",
        choices=[b.value for b in Backend],
        default=Backend.LARK.value,
        help="Extractor backend (default: lark)",
    )
    p.add_argument("--dry-run", action="store_true",
                   help="Render the annotated file but don't write it")
    p.add_argument("--no-check", action="store_true",
                   help="Skip the pycsl round-trip after emission")
    p.add_argument("--strict", action="store_true",
                   help="Fail on any unsupported Gallina fragment")
    p.add_argument("-v", "--verbose", action="store_true")
    return p


def _resolve(path_str: str, config_path: Path) -> Path:
    """Resolve `path_str` relative to the directory containing the config."""
    p = Path(path_str)
    if p.is_absolute():
        return p
    return (config_path.parent / p).resolve()


def _resolve_rocq_path(cfg: Config, config_path: Path) -> Path:
    """Pull the .v path out of the raw TOML (it's not part of the shared schema)."""
    rocq_str = cfg.raw.get("input", {}).get("rocq")
    if not rocq_str:
        raise KeyError("missing required field input.rocq")
    if not isinstance(rocq_str, str):
        raise ValueError("input.rocq must be a string")
    return _resolve(rocq_str, config_path)


def _emit_all(
    source: str,
    cfg: Config,
    contracts: dict[str, FunctionContract],
) -> str:
    """Render contracts for every configured function and stitch them in."""
    current = source
    for qualname, contract in contracts.items():
        spec = cfg.functions[qualname]
        lines = _contract_to_lines(contract, divides_style=spec.divides_style, name_map=spec.arg_map)
        current = annotate_source(current, spec.python_name, lines)
    return current


def _contract_to_lines(
    contract: FunctionContract,
    *,
    divides_style,
    name_map,
) -> list[str]:
    """Flatten a FunctionContract into PyCSL `#@` line bodies in canonical order:
    requires*, ensures*, assigns, [variant | diverges]."""
    out: list[str] = []
    for r in contract.requires:
        out.append(f"requires {render(r, style=divides_style, names=name_map)}")
    for e in contract.ensures:
        out.append(f"ensures {render(e, style=divides_style, names=name_map)}")
    out.append(f"assigns {contract.assigns}")
    if contract.variant is not None:
        out.append(f"\\variant {render(contract.variant, style=divides_style, names=name_map)}")
    elif contract.diverges:
        out.append("\\diverges")
    return out


if __name__ == "__main__":
    sys.exit(main())
