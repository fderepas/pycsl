"""Select which Lean theorems become contracts for a given function.

Selection precedence per lean2pycsl-plan.md §6:

  1. `@[pycsl_spec "qualname"]` attribute on the theorem (primary —
     the plan's recommended idiom because Lean's attribute system makes
     the authoring intent explicit).
  2. TOML `[functions.<qualname>.extra_specs.include]` list (escape
     hatch for theorems lacking the attribute, e.g. when reusing
     mathlib lemmas you can't tag).
  3. **No heuristic mode.** Mathlib is too large; a heuristic sweep
     would suck in unrelated lemmas (plan §6, last paragraph).

This differs from rocq2pycsl's selector, which allows an opt-in
heuristic. The Lean plan explicitly rules that out.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .lean_ast import LTheorem, LeanDef, LeanModule


@dataclass(frozen=True)
class SelectionResult:
    """What the selector decided for one function."""
    func: LeanDef
    theorems: tuple[LTheorem, ...]
    rule: str   # "attribute" | "extra_specs" | "none"


def select(
    module: LeanModule,
    func: LeanDef,
    *,
    extra_specs: Iterable[str] | None = None,
    target_qualname: str | None = None,
) -> SelectionResult:
    """Return the theorems chosen as contracts for `func`.

    `target_qualname` is the qualname used in `@[pycsl_spec "X"]`
    attributes. Defaults to `func.name` if not specified, matching the
    common case where the Lean theorem and Python function share a
    name.

    `extra_specs` is the explicit-include list from TOML — applied on
    top of (or instead of) attribute-tagged theorems.
    """
    target = target_qualname or func.name

    # Rule 1: tagged theorems.
    tagged = tuple(
        t for t in module.theorems if t.pycsl_spec_target == target
    )

    # Rule 2: explicit-include list (always combined with attribute
    # discovery — if a user names the same theorem in both places,
    # it appears once).
    explicit = list(extra_specs or [])
    if explicit:
        by_name = {t.name: t for t in module.theorems}
        missing = [n for n in explicit if n not in by_name]
        if missing:
            raise KeyError(
                f"extra_specs theorems not found in "
                f"{module.source_path or '<module>'}: {missing}"
            )
        extras = tuple(by_name[n] for n in explicit if by_name[n] not in tagged)
        if tagged or extras:
            rule = "attribute" if tagged and not extras else (
                "extra_specs" if extras and not tagged else "both"
            )
            return SelectionResult(
                func=func, theorems=tagged + extras, rule=rule
            )

    if tagged:
        return SelectionResult(func=func, theorems=tagged, rule="attribute")

    return SelectionResult(func=func, theorems=(), rule="none")
