"""Allow-list of kernel axioms accepted in re-verification (Phase 0).

The reverify path runs `Print Assumptions` (Rocq) and `#print axioms`
(Lean) on each cited theorem after `coqc` / `lake env lean` compile.
The output is matched against this allow-list. Anything outside
the list is a reverify FAIL — the cited proof relies on a non-standard
assumption and cannot anchor a #@ proof citation.

Per `sticky-01.md` Phase 0 §3-4 and `0342_explanation.md` §9.2.
"""
from __future__ import annotations

from typing import Set


# Coq stdlib axioms accepted by the PyCSL trust class 0b.
# Empty assumption set (`Closed under the global context`) is the
# strongest possible result; non-empty sets must be a subset of this.
ROCQ_KERNEL_AXIOM_ALLOWLIST: Set[str] = {
    # propositional extensionality — used by Mathlib + Coq stdlib;
    # accepted axiom in the wider Coq community.
    "Coq.Logic.PropExtensionality.propositional_extensionality",
    # functional extensionality on dependent functions — same status.
    "Coq.Logic.FunctionalExtensionality.functional_extensionality_dep",
    # eta-expanded variant sometimes leaks through.
    "Coq.Logic.FunctionalExtensionality.functional_extensionality",
    # propositional extensionality short-name (Coq sometimes prints
    # bare names without the full path).
    "propositional_extensionality",
    "functional_extensionality_dep",
    "functional_extensionality",
}


# Lean 4 / Mathlib kernel axioms accepted by the PyCSL trust class 0b.
LEAN_KERNEL_AXIOM_ALLOWLIST: Set[str] = {
    "propext",
    "Classical.choice",
    "Quot.sound",
}


# Rocq Print Assumptions "no axioms" string — the strongest result.
ROCQ_NO_AXIOMS_MARKER = "Closed under the global context"


def is_rocq_assumption_allowed(name: str) -> bool:
    """Return True iff a single Rocq assumption name is in the allow-list."""
    return name.strip() in ROCQ_KERNEL_AXIOM_ALLOWLIST


def is_lean_axiom_allowed(name: str) -> bool:
    """Return True iff a single Lean axiom name is in the allow-list."""
    return name.strip() in LEAN_KERNEL_AXIOM_ALLOWLIST


def parse_lean_axioms_line(line: str) -> list[str]:
    """Parse a `#print axioms` output line into a list of axiom names.

    Lean prints either:
      'foo.bar' depends on axioms: [propext, Quot.sound]
    or, if there are no axioms:
      'foo.bar' does not depend on any axioms
    """
    if "does not depend on any axioms" in line:
        return []
    if "depends on axioms:" not in line:
        return []
    bracket = line.split("depends on axioms:", 1)[1].strip()
    if not (bracket.startswith("[") and bracket.endswith("]")):
        return []
    inner = bracket[1:-1].strip()
    if not inner:
        return []
    return [name.strip() for name in inner.split(",")]


def parse_rocq_assumptions_block(block: str) -> tuple[bool, list[str]]:
    """Parse a Rocq Print Assumptions block.

    Returns (is_closed, assumption_names). is_closed=True means the
    theorem has zero assumptions ("Closed under the global context").
    Otherwise assumption_names lists each Axiom: / Variable: / etc.
    """
    if ROCQ_NO_AXIOMS_MARKER in block:
        return True, []
    names: list[str] = []
    for raw in block.splitlines():
        line = raw.strip()
        # Coq's output looks like:
        #   Axioms:
        #   propext : ...
        #   Quot.sound : ...
        # We accept any non-empty identifier on a line containing ` : `.
        if " : " in line and not line.startswith(("Axioms:", "Section Variables:",
                                                   "Constants:", "Parameters:",
                                                   "Print", "Closed")):
            name = line.split(" : ", 1)[0].strip()
            if name:
                names.append(name)
    return False, names
