# wall_v3_phase0_poison_ta.py — POISONED CONTROL for wall-plan-v3 Phase 0.
#
# This program MATCHES the T-A generic-walk idiom EXACTLY (the target modelled by
# test-suite/corpus/conformance/spikes/v2_iter_mutate_spike.mlw): isinstance(dict)/
# isinstance(list) arms, a `for k, v in obj.items()` walk with a literal-key skip
# guard, self-recursion into each value, and a by-reference Set[str] accumulator.
#
# Corpus datum: 0/756 reference programs currently match this idiom, so a correct
# fail-closed recognizer must be byte-diff-0 on the whole corpus AND fire on THIS
# single fixture — flipping the byte-diff gate red exactly once. NOT wired into the
# emitter or the corpus yet (Phase-0 negative control only).
from typing import Any, Set


def collect_targets(obj: Any, targets: Set[str]) -> None:
    if isinstance(obj, dict):
        if obj.get("type") == "NamedExpr":
            targets.add(obj["target"])
        for k, v in obj.items():
            if k == "stmt":
                continue
            collect_targets(v, targets)
    elif isinstance(obj, list):
        for item in obj:
            collect_targets(item, targets)
