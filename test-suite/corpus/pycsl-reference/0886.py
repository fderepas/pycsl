# pycsl-flags: --no-proof
"""Test 0886 — E0 regression: @staticmethod parameter extraction with a tuple-unpack for-loop.

Guards the fix in `src/pycsl/module6_whyml/functions.py::_build_param_list` (method branch).
Before the fix that branch built the WhyML signature by iterating the pollution-prone
`symbol_table` (which Module4 also fills with for-loop tuple targets and locals) AND skipped
`local_refs`. For this method that produced the WRONG signature

    let foo__total_keys (self) (d) (k: int) (v: int) : int

i.e. the `for k, v in ...` loop tuple-target `k, v` was promoted to method parameters, while
the real parameter `base` — reassigned in the body (`base = base + 1`), hence a local ref —
was DROPPED, yielding `unbound function or predicate symbol 'base'` at type-check.

After the fix the branch iterates the unpolluted `_formal_params` (source order, `self`
excluded) and keeps reassigned params, so the signature is correct:

    let foo__total_keys (self) (d: map int (option int)) (base: int) : int   and L3-tc ✓.

Gated at `--no-proof`: the E0 property verified here is the emitted signature + the WhyML
type-check. Full proof of the tuple-unpack loop's termination needs the iterator/char
sequence model (the "Wall 2" work, W2 in value-model-wall-stand-alone-plan-2.md), which is
orthogonal to this parameter-extraction fix.
"""
from typing import Dict


class Foo:
    #@ requires True
    #@ ensures \result >= 0
    #@ assigns \nothing
    @staticmethod
    def total_keys(d: Dict[int, int], base: int) -> int:
        base = base + 1
        total = base
        for k, v in d.items():
            total = total + 1
        return total
