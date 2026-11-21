# Eleven gates reported "all 48 planes green" over four RED oracles they never ran

Generation #31, 2026-09-25T23:00Z. This is the most expensive instrument failure of the
session, and it was found by accident: a routine hand-run of the five trust planes after an
unrelated conversion.

## What happened

`bin/run-soundness-planes.sh` has TWO sets. Called with no arguments it runs 48 planes and
prints

    [+] soundness-planes: OK — all 48 plane(s) green.

Called with `--slow` it adds 25 more — "prover/emission planes" — including every oracle in
`EMIT_DIR_PLANES`, the ones that emit the mirror and read the WhyML back.

**Every gate script this session called it with no arguments.** Twenty-eight invocations
across gates A through N. So for the whole campaign the sentence "all 48 planes green" was
true and the sentence it was read as — "every plane is green" — was not.

The `--slow` battery, run at 21:48Z on the increment-N tree, reports **four REDs**:

| plane | verdict |
|---|---|
| `check-yield-erasure.py` | 1 converted generator drops its yielded VALUES (max 0) |
| `check-shadowed-selfcalls.py` | 17 shadowed conversions > allowed 14 |
| `check-getattr-erasure.py` | corpus `1859`/`1860` have UNKNOWN sites and no TSV row |
| `check-stdlib-modules-verify.py` | 83 of 104 `pycsl_lib` modules verify |

Two of the four are **this session's own work**, and both are the kind of defect the
campaign's rigor exists to prevent.

## RED 1 — `iter_fields`: a hollow conversion banked eleven times

Commit `6c8dfa35` (13:43Z, increment G) converted `frontend/pure_ast.py::iter_fields` by
porting its live body. Its message argued check 1 carefully and concluded

> That is honest opacity, not erasure … No effect erased, no input dependence erased.

about the one new abstract op, `val get__fields (x: int) : int`. The argument is correct and
it is about the wrong thing. This is what the conversion emits:

    let iter_fields (node: int) : unit
      requires { true }
      ensures  { true }
    =
      let field = ref 0 in
      let _len_idx_field = (iter_length (get__fields node)) in
      …
        try let _ = (any int) in ()
        with AttributeError -> ()

A `unit`-returning function with a `true` contract, in which the yielded pair
`(field, getattr(node, field))` is replaced by `any int` and dropped. The generator's ONLY
meaning is the sequence it produces, and the emitted body produces nothing.

**The oracle for exactly this was already written, by the previous generation, in response to
exactly this, on the function ELEVEN LINES BELOW.** `iter_child_nodes` carries a
`YIELD-ERASURE REVERT (#31)` comment and a re-instated `\trusted` marker, and it ends:

> See `bin/check-yield-erasure.py`, which now makes this class of conversion impossible to
> bank again.

It did not, because nothing ran it. The check-1 criterion this session sharpened over three
commits — the abstract-op ledger, the effect/input-dependence rule, clause 4 — has no clause
about `yield` at all, so a careful application of it admitted the conversion. A criterion is
only as wide as the failures it was written from.

## RED 2 — three conversions whose bodies no caller can see

`check-shadowed-selfcalls.py` measures converted methods whose call sites go through the
synthesized abstract `val self__<m>_<n>` instead of the concrete sibling application. Its
baseline is 14. It now reports 17, and the three added are precisely:

    19 bypassing use(s)   frontend_pure_ast.mlw::self_error_1        shadows `_parser__error`
     7 bypassing use(s)   frontend_Module2_Parser.mlw::self__err_1   shadows `_contractparser___err`
     2 bypassing use(s)   frontend_pure_ast.mlw::self_unsupported_1  shadows `_parser__unsupported`

`pure_ast.py::error` and `::unsupported` landed in `61441c3e`; `Module2_Parser.py::_err` in
`6cb8050c`. All three PROVED, all three are sound — an unconstrained result is an
over-approximation exactly like a `\trusted` stub — and all three bought their callers
nothing. In the plane's own words, a LOST CONVERSION: "the proof was paid for and the
faithfulness gain never reached any caller." Twenty-eight call sites still see an
unconstrained value.

The plane also names the remedy the previous generation used on five methods: the
`#@ sibling_concrete` directive, which routes the call sites to the real body. `traverse` is
the recorded case where it CANNOT be taken (concrete routing makes `traverse`/`visit`/
`visit_<Node>` one mutually recursive group and Why3 demands a measure the int model cannot
supply — 124 unproven goals, every one `Sub-goal termination`).

## RED 3 and RED 4 — pre-existing, and not this session's

`check-getattr-erasure.py` wants `bin/getattr-erasure-sites.tsv` rows for corpus `1859` and
`1860`, route #213's witnesses — added before this session. `check-stdlib-modules-verify.py`
reports 83 of 104 `pycsl_lib` modules verifying, with its own honest restatement ("76
module(s) with a postcondition to discharge, not 83"); it is a standing measurement, not a
regression. Both were red before increment A and are recorded here so that the next
generation does not rediscover them as news.

## The three things that have to change

1. **The gate runs `--slow`.** A plane you have to remember to run is a plane you will forget
   to run. Twenty-eight times.
2. **The fast battery must not claim what it did not check.** "all 48 plane(s) green" needs
   to say, in the same sentence, that 25 planes were not run.
3. **A population of zero is re-measured at every gate that could change it.** This session
   measured the yield population at 0 and recorded it as "a trap, not a hole". That was true
   at the hour it was taken, and increment G falsified it four hours later.

`getting-better/wall-lessons.md` (q6).
