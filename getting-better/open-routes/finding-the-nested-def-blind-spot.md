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
problems. MEASURED EXACTLY: the integrity gate's own walk enumerated **863** of the **915**
un-trusted, un-abstract mirror functions — 52 invisible — while the FIDELITY plane descends
and therefore counts every one of the 52 among the verbatim un-trusted twins it calls verified.
The two planes disagreed about the same mirror by 52 functions
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

## What the fixed gate actually found — and the number that went backwards

With the walk descending, the population is **915** un-trusted functions instead of 863. The
first run reported 1 `val` and 41 ABSENT. Both numbers were then adjudicated rather than
believed:

**The 41 ABSENT are not 41 unverified functions.** Spot-checked by emitting the files by hand:
`module6_whyml/ir_scanner.py`'s three closures ARE emitted (as `irscanner___has_return` etc. —
the plane's mangling-aware regex matches them). And `module6_whyml/functions.py::
_build_method_param_result_ensures_map`'s closures `classify` / `refs_param` / `rename` do not
appear, because the emitter's RECOGNIZERS consume them into the parent's model — the parent is
emitted as a `let` whose body is a fold, with lifted helpers named after the PARENT
(`__lmem`, `__gtype`, `__gnm`, `__gvar`, `__f`). Whether that fold is faithful is
`check-bespoke-model-drift.py`'s question. So the gate gained a shape rule:

> **FOLDED** — a nested closure absent from the emission whose ENCLOSING DEF is itself
> emitted as a definition. The parent's body is the thing that carries the claim.

With the rule: 915 un-trusted, 859 definitions, **41 folded**, **1 `val`**, **0 unexpectedly
absent**.

**The 1 `val` is real**, and a second like it was hiding. `Module6_WhyMLTranspiler::
_sig_val_from_let::_hdr_name` is un-trusted inside a `\trusted` parent: the parent is an
opaque `val`, so nothing anywhere carries the closure's claim. Asking the question STATICALLY
— *is the enclosing function `\trusted`?* — needs no emission and has no blind spot, and it
finds a second: `core_ir_semantic::_returns_literal_none::walk`. The emission-based check
misses that one because `classify` matches on the BARE name and `core_ir_semantic.py` has
**five** closures called `walk`, the other four of which are emitted. It hid behind its
siblings.

## Both were given honest `\trusted` markers, and the count went 458 back to 460

    460  at the start of the session
    458  after `errors.py::message` and `proof2why3/sertop.py::__exit__` were PROVED
    460  after `_hdr_name` and `_returns_literal_none::walk` took honest markers

Fidelity: 886 -> 888 -> **886**. The session's headline number is exactly where it started.

That is the right outcome and it should be said plainly: **two functions were removed from the
trusted set by proving them, and two were added to it by discovering they had never been
verified at all.** The count is unchanged; the map is two entries more accurate. A campaign
that reports only the count would record this session as zero progress, and a campaign that
refused the two honest markers to protect the count would be reporting 458 over a number that
was never true.

The blast-radius aggregate moved with it, 833 -> **834**, and that is recorded in the constant
rather than absorbed — along with the asymmetry it exposed: the aggregate is invariant under a
conversion (trusted -> trust-dependent) but NOT under the reverse, because a newly-trusted
function pulls in callers that were previously trust-free. `walk` is called all over
`core_ir_semantic.py`, and the same-file lower bound jumped 336 -> 343 on that one marker.

## The check was validated nine minutes after it landed

Increment F added a STATIC refusal — *an un-trusted closure inside a `\trusted` parent is
verified nowhere* — at 04:02Z. At 04:11Z the conversion screen, re-run on six candidates the
census had just recovered, reported:

    pycsl.py::_is_false_goal      **LOWERS**
    pycsl.py::_probe_one          **LOWERS**

Both are nested closures inside `\trusted` parents. Converting either would have retired a
marker, passed the emission check, passed fidelity, dropped the count — and proved nothing,
because the parent is emitted as an opaque `val`. Without the check landed nine minutes
earlier, this session would have had two more "landable" candidates that land nothing.

**CENSUS over all 410 strict candidates: 5 are trusted-parent traps.**

    Module6_WhyMLTranspiler.py   _emit_funcs                 inside _transpile_modular
    pycsl.py                     _finalize                   inside _dispatch_provers
    pycsl.py                     _gate_vacuity_then_succeed  inside _run_proofs
    pycsl.py                     _is_false_goal              inside _probe_one
    pycsl.py                     _probe_one                  inside _run_vacuity_gate

This is a **CHECK 0**: purely static, needs no emission and no prover, and it disqualifies a
candidate before the expensive checks run. It should be the first filter any future conversion
screen applies, ahead of `--no-proof` lowering. `pycsl.py::_finalize` is on the list and is
also the function whose byte-identical emit-diff started this whole thread — the two
instruments agree on it from opposite directions.

And the emitter already knew. `module6_whyml/functions.py`'s nested-lift refusal carries a
`func.get("trusted_parent")` exemption: the lowering has tracked the concept all along, while
no plane asked the corresponding question about the MARKER.

## The gap, measured exactly rather than subtracted

The first write-up of this finding said the gate had been checking "836 of 888". **Both
numbers were wrong**, and in the way that is worth recording: 836 was arrived at by
SUBTRACTING the census (52) from the FIDELITY plane's count (888) — two different populations,
neither of them the gate's. The gate counts un-trusted AND un-abstract functions, the fidelity
plane counts verbatim un-trusted twins, and they do not have the same members.

Running the OLD walk and the NEW walk side by side over the same mirror, which is what should
have been done in the first place:

    OLD walk (stops at a `def`, no compound-statement descent)   863
    NEW walk (descends)                                          913   (915 before the two
                                                                        honest markers)
    difference                                                    50   (52 before them)

So the correct sentence is: **the integrity gate enumerated 863 of the 915 un-trusted
functions in the mirror.** A number produced by subtracting one plane's count from another
plane's census is exactly the kind of number this finding is about.
