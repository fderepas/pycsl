# Two planes stop at a `def`, and one of them is the integrity gate on the headline count

Generation #31, 2026-09-25T03:51Z.

## How it was found

`pycsl.py::_finalize` was one of the six verbatim `\trusted` candidates that LOWER. Check 1
— diff the emitted `.mlw` before and after retiring the marker — returned **zero diff lines.
The two files are byte-identical.** Before and after, the emission is:

    val _finalize (merged_records: int) (rc: int) : (int, int, int)

The marker is not what makes `_finalize` a `val`; the nested-def lowering is. So retiring it
would drop the marker count 458 -> 457, leave the emitted program bit-for-bit unchanged, and
prove exactly nothing.

## The gate that exists for precisely this, and why it would not fire

`bin/check-untrusted-emitted.py` is the integrity gate on the conversion count. Its own
docstring states the hazard:

> Removing a `#@ \trusted` marker is what the TCB-reduction campaign counts as a conversion.
> But removing the marker does NOT by itself guarantee that anything is verified in its
> place: PyCSL has an AUTO-TRUST SAFETY VALVE, so a body the emitter cannot lower is silently
> re-abstracted to an opaque `val` […] the count improves, the TCB does not.

It would not have fired, because its walk recursed into a `ClassDef` and **stopped at a
`FunctionDef`**:

    def walk(node, cls):
        for c in ast.iter_child_nodes(node):
            if isinstance(c, ast.ClassDef):
                walk(c, cls + (c.name,))
            elif isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef)):
                ...append...
                # and no recursion, and no descent through try:/if:/with:/for:

## The scale, measured

The FIDELITY plane (`check-self-annotate-mirror-sync.py::_walk`) *does* descend — a gen #4
note in that file records fixing this exact walk in this exact way, after finding two
`\trusted` closures inside a `try:` that the plane could not see. So every nested un-trusted
closure is already counted among the **888 verbatim un-trusted twins** — the population this
project calls verified — while the gate that checks they are actually emitted as definitions
never looked at one of them.

**CENSUS: 52 nested un-trusted mirror functions were invisible to the integrity gate.**

    module6_whyml/functions.py      22   (classify, rename, refs_param, saw, ...)
    module6_whyml/auto_trust.py      5
    core_ir_semantic.py              5   (walk x5)
    module6_whyml/preamble.py        4
    frontend/ir_resolve.py           3   (_walk x3)
    module6_whyml/ir_scanner.py      3
    module6_whyml/types.py           2   (_scan x2)
    frontend/pure_ast.py             2
    Module6_WhyMLTranspiler.py       2
    frontend/Module5_IREmitter.py    1
    module6_whyml/stmt_control_flow.py 1

And the same blind spot was found an hour earlier, independently, in
`bin/check-trusted-frame-honesty.py`: its `_mirror_nothing_stubs` walk misses **5 nested
`\trusted` stubs**, every one declaring `#@ assigns \nothing`
(`Module6_WhyMLTranspiler::_emit_funcs`, `statements.py::rec` x2, `pycsl.py::_probe_one`,
`pycsl.py::_finalize`). Two planes, the same three missing lines.

## The fix

Descend into `FunctionDef` and through compound statements, exactly as the fidelity plane
already does. Three lines in each walk.

## The general lesson, which is about instruments and not about closures

A plane that walks the AST for a population has to walk it the same way every other plane
walking that population does, or the populations silently disagree — and the disagreement
always favours the optimistic number, because the narrower walk is the one that finds fewer
problems. The fidelity plane says 888 functions are verified; the integrity gate checked 836
of them. Nobody wrote that down, because nothing printed both numbers.

**Any plane that reports a population size should be cross-checked against every other plane
that reports the same population.** That is how `count-trusted-directives` (460) was
reconciled against the blast-radius walk (434) and the frame walk, and it is how this was
found — one function that two planes disagreed about.

## The audit that should have existed, run over all 48 planes

Classifying every `bin/check-*.py` by how it walks the mirror:

* **`ast.walk` (sees every nested def automatically)** — 36 planes, including
  `check-trust-blast-radius.py`, `check-trusted-raises-honesty.py`,
  `check-trusted-termination-honesty.py`, `check-emitted-function-coverage.py`. These were
  never at risk; `ast.walk` is flat and total.
* **custom walk that DESCENDS** — `check-self-annotate-mirror-sync.py` (the fidelity plane,
  fixed in gen #4) and now `check-untrusted-emitted.py`.
* **custom walk that STOPS AT A `def`** — `check-yield-erasure.py`,
  `check-mirror-signature-drift.py`, and the `_mirror_nothing_stubs` half of
  `check-trusted-frame-honesty.py`.

Populations in the three that still stop, measured:

    check-trusted-frame-honesty._mirror_nothing_stubs    5 nested `\trusted` `assigns \nothing`
                                                           stubs invisible. NAMED in
                                                           KNOWN_EXTERNAL_EFFECT_NOTHING rather
                                                           than deleted, so the gap is visible.
    check-yield-erasure.py                               **0** nested un-trusted generators
                                                           today. A TRAP, not a hole — the walk
                                                           is wrong and nothing is in it yet.
    check-mirror-signature-drift.py                      nested defs never signature-compared,
                                                           but the FIDELITY plane compares the
                                                           full signature and descends, so this
                                                           one is covered elsewhere.

Recording the zero matters as much as recording the 52. `check-yield-erasure.py` has exactly
the defect that let 52 functions past `check-untrusted-emitted.py`, and it is clean today only
because nobody has written a nested generator in the mirror yet. It will stay clean by
accident until it doesn't.
