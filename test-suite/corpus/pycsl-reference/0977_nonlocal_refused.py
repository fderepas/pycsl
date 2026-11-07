"""Test 0977 — a closure that WRITES an enclosing local through `nonlocal` is REFUSED,
because the generic lowering made the write vanish and PROVED A FALSE POSTCONDITION.

`ast.Nonlocal` has no `_PY_STMT_HANDLERS` entry, so the declaration is dropped; the nested
`def` is LIFTED to a sibling top-level function, and its assignment becomes a write to a
FRESH LOCAL of that sibling. Measured, before the refusal:

    #@ ensures \result == 1                    <-- FALSE OF THE PROGRAM
    def outer() -> int:
        x: int = 1
        def inner() -> None:
            nonlocal x
            x = 2
        inner()
        return x

    [+] Verification SUCCESS! All contracts formally proven.

The emitted module was

    let inner () : unit = let x = ref 0 in x := 2
    let outer () : int ensures { result = 1 }
      = let x = ref 0 in x := 1; let _ = (inner ()) in (); !x

Real Python returns 2 (verified by running it).

WHY THE REFUSAL IS IN MODULE 6 AND NOT IN `desugar.reject_unmodelled`, which is where the
four other #33/#34 refusals live. `module6_whyml/generic_fold.py` already carries
hand-synthesized BESPOKE lowerings for exactly this shape — the `hit = False` / nested
`def _walk` / `nonlocal hit` existence walk — and they PAIR the outer wrapper with its
lifted `_walk` sibling, so the two CONVERTED, PROVED mirror methods that use it
(`module6_whyml/preamble._inductive_refs_global_or_axiom_func` and
`._class_inv_refs_axiom_func`) are FAITHFUL and are NOT victims. A front-end refusal cannot
tell the bespoke path from the generic one; it would have rejected both. So Module 5
carries the fact into the IR as `nonlocal_writes` (emitted only when non-empty, so the IR
of every other function is byte-identical and the frozen conformance goldens do not move),
and Module 6 refuses at the ONE point where every bespoke recognizer has already had its
chance and the generic emission is about to begin. A `\trusted` / `\abstract` function is
exempt: it emits as a bodyless `val` and its body is never lowered.

CENSUS: 2 in the mirror (both bespoke-modelled, both still emit — `preamble.py` is L3-tc
green and its emitted `.mlw` is BYTE-IDENTICAL), 1 in `python-reference/0182` (already
`pycsl-expected: FAIL`), 0 in `pycsl-reference`, 0 in `src/pycsl_lib`, 3 in the live
emitter. All 819 pre-existing corpus `.mlw` are byte-identical, so no corpus file is
refused.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL


#@ requires True
#@ ensures \result == 2
#@ assigns \nothing
def outer() -> int:
    x: int = 1

    def inner() -> None:
        nonlocal x
        x = 2

    inner()
    return x
