# Most `\trusted` candidates are facades, not proof problems — 235 of 410

> **THE NUMBER WAS WRONG TWICE AND IS RECORDED THREE TIMES, because how it was wrong is the
> useful part.** 61, then 56, then **62**. Each revision came from an instrument disagreeing
> with the census, within the hour, and each one is a different lesson:
>
> * **61 -> 56.** The census keyed function bodies on the BARE name, so a file with two
>   definitions of `visit` let a FACADE match the OTHER `visit`'s live body. Caught by the
>   screen reporting LOWERS for `pure_ast.py::visit`, whose body is `pass`. Re-keyed on the
>   QUALIFIED name; five candidates moved out and eight became AMBIGUOUS rather than guessed.
> * **56 -> 62.** The census compared RAW SOURCE TEXT. `pycsl.py::_dispatch_provers` scored
>   0.991 "stale copy" when its ONLY difference from live is four `#@` annotation lines on a
>   NESTED closure — which the fidelity plane explicitly PERMITS, along with docstrings and
>   quote style. Six candidates were being called DIFFERS for carrying exactly the annotations
>   the mirror exists to carry.
>
> **The fix is the lesson this generation keeps relearning: ask the plane that decides.** The
> final census imports `check-self-annotate-mirror-sync.py`'s own `_normalize` and
> `_signature` and uses its qualified-name walk, so "VERBATIM" now means precisely what the
> gate that would block the conversion means by it, and cannot drift from it again.
> Both headline stubs survive all three versions, which is the check that mattered each time.

> **CORRECTED 03:42Z, one hour after it was written, by the census's own first hit.**
> The first version said 61 and 238. It keyed function bodies on the BARE name, so a
> file with two definitions of `visit` let a FACADE body match the OTHER `visit`'s live
> body and be counted VERBATIM. The screen caught it: `frontend/pure_ast.py::visit`
> reported **LOWERS**, and its mirror body is `pass`. Re-keyed on the QUALIFIED name
> (`Class.method`), five candidates move out — `Module2_Parser.__init__`,
> `Module5_IREmitter.__init__`, `pure_ast.visit`, `pure_ast.visit_Constant`,
> `statements.rec` — and eight more are reported **AMBIGUOUS** rather than guessed at.
> The corrected table is below; every number in the prose has been moved with it.
> Both headline stubs survive the correction, which is the check that mattered.

**Generation #31, 03:36Z. Measured, not estimated.** A static census over the 410 STRICT
`\trusted` conversion candidates, cross-referencing each mirror body against its live twin:

| mirror body vs live | count | can it ever land? |
|---|---|---|
| **VERBATIM** (live body is, or contains, the mirror body) | **61** | yes |
| **FACADE** (`pass`, `return None`, `return <literal>` — nothing else) | **238** | **no** |
| **DIFFERS** (a real body, but not the live one) | **109** | **no, not as written** |
| mirror-missing | 2 | n/a |

## Why a facade can never land

`bin/check-self-annotate-sync.sh` states the mirror's load-bearing invariant in its own header:

> The mirror is HETEROGENEOUS: un-`\trusted` methods are **verbatim copies** of the live
> emitter (+ `#@` annotations), while `\trusted` methods are intentionally-divergent bodyless
> stubs.

Removing the `#@ \trusted` marker from a facade moves it into the un-trusted population, where
the fidelity plane demands its body equal the live body. `pass` does not equal a 200-line
parser. The conversion fails the FIRST plane it reaches, before a prover is ever started.

So a facade is not a candidate that is *hard* to convert. It is not a candidate at all. The
work it needs is not a proof — it is a PORT: copy the live body into the mirror, and only then
ask whether it lowers.

## What this invalidates, and what it does not

**Invalidated: the screen's LOWERS verdict on a facade.** The conversion screen runs
`convert_one.py` (which deletes the marker and nothing else) and then Module 6 in `--no-proof`
mode. Over a facade it is asking *"does `pass` lower and typecheck?"*, and the answer is
of course yes. Three of the five LOWERS hits found so far are exactly this:

    frontend/Module2_Parser.py  _parse_quantifier   body: `pass`        FACADE
    frontend/Module2_Parser.py  _try                body: `pass`        FACADE
    frontend/Module2_Parser.py  parse_contract      body: `return None` FACADE

Only `frontend/Module2_Parser.py::__init__` is verbatim in that file.

**Not invalidated: the two headline stubs.** The census is validated by the two cases already
worked by hand, and it agrees with both:

    errors.py::message                        VERBATIM  -> converts, proves, check 1 PASSES
    audit_proof_reverify.py::_cache_root      VERBATIM  -> converts, proves, check 1 FAILS

Neither is a facade, which is why both got as far as a real emit-diff.

## Where the 61 are

    20  pycsl.py                       3  errors.py
    11  audit_proof_reverify.py        2  proof_axiom_allowlist.py
     9  audit_proof.py                 1  each: proof2why3/sertop.py, module6_whyml/statements.py,
     6  Module6_WhyMLTranspiler.py              ir_schema.py, frontend/Module5_IREmitter.py,
     4  frontend/pure_ast.py                    frontend/Module2_Parser.py, exception_model.py

The concentration is the point: the six mirror files that were ported most faithfully hold 54
of the 61. The four big frontend modules — `Module1_Ingestor`, `Module2_Parser`,
`Module3_Weaver`, `ir_resolve` — contribute **one** candidate between them, because their
`\trusted` stubs are facades almost without exception.

## The screen was re-targeted, not restarted

At 03:36Z the running screen was stopped by its sentinel (`touch $S/STOP_SCREEN` — never
`pkill -f`, wall-lesson (c6)) with 101 of 404 done, and re-queued on the **58** verbatim
candidates it had not yet reached. That is not a small saving: the screen spends roughly
5 seconds per candidate, and 303 of the remaining 404 were unlandable by construction.

## The number that should be reported

The campaign's headline metric is 460 `\trusted` marker lines, of which 417 have a live
counterpart. **The count of markers that a proof alone can retire is 61.** The other 356 need
a port first, and a port is a different and much larger kind of work — it is the thing the
mirror's authors deferred, one stub at a time, for a reason each time.

## The second wave: 11 of the 109 DIFFERS are stale copies, not facades

`DIFFERS` is not one population. Scored by `difflib` similarity of the mirror body to the live
body:

| similarity | count | what it is |
|---|---|---|
| >= 0.95 | 3 | a stale copy — live drifted after the port, or the port dropped a line |
| >= 0.80 | 8 | a real port with a deliberate simplification |
| >= 0.50 | 9 | half a port |
| < 0.50 | **89** | a different program |

The eleven at >= 0.80, in order:

    0.991  pycsl.py                    _dispatch_provers
    0.981  pycsl.py                    _probe_one                    (and it is NESTED)
    0.980  pycsl.py                    _run_vacuity_gate
    0.937  pycsl.py                    _record_answer
    0.906  Module6_WhyMLTranspiler.py  _emit_prefunctions_infra
    0.891  pycsl.py                    _parse_args
    0.868  Module6_WhyMLTranspiler.py  _wrap_call_with_callee_raises_assert
    0.854  audit_proof_reverify.py     verify_lean_file
    0.828  pycsl.py                    _run_proofs
    0.824  pycsl.py                    _resolve_runtime_config
    0.805  Module6_WhyMLTranspiler.py  __init__

So the honest bracket for "retirable by proof, with at most a small mechanical re-port" is
**61 to 72 of 410** — and 89 of the 410 are a different program in the mirror than in the live
tree, which is the population `finding-a-verified-program-that-is-not-the-executed-program.md`
is about. That finding named the shape; this table sizes it.

## A fourth validation, and it is the one that corrected the census

The re-targeted screen's third LOWERS hit was `frontend/pure_ast.py::iter_child_nodes` — a
GENERATOR, already re-`\trusted` in gen #30 with a note in the file saying why, and already
guarded by `bin/check-yield-erasure.py` in the plane battery. The conversion erases the yields:
the body proves `assigns \nothing` while establishing nothing about what the generator
produces, which is its entire meaning.

So the screen's LOWERS verdict has now been wrong in three distinct ways in one hour:

1. over a FACADE — `pass` lowers perfectly (three Module2_Parser hits);
2. over a GENERATOR — the yields are erased and a plane already refuses it;
3. over `_cache_root` — it lowers AND proves, and check 1 refuses it because the `os.mkdir`
   becomes a nullary `val` with no `writes`.

**`--no-proof` LOWERS is a necessary condition and nothing more.** The four checks are the
condition. Of the 410 strict candidates the screen has now been run over, exactly ONE has
passed all four: `errors.py::message`.

And the fourth hit, `frontend/pure_ast.py::visit`, is what corrected the census itself — it
reported LOWERS with a body of `pass`, which a VERBATIM candidate cannot have. The bare-name
keying bug above was found by its own instrument's output disagreeing with it, within an hour,
on the first file where the two could disagree.

## The whole 56-candidate frontier, screened (03:47Z)

The re-targeted screen finished. Over the 56 VERBATIM candidates (plus two census artifacts
it had already been given), in `--no-proof` mode:

| verdict | count | what it is |
|---|---|---|
| **LOWERS** | 8 | and only 2 survive the four checks — see below |
| TYPE error | 36 | the value model: 17 `int`, 8 `array.Array.array`, 9 `string`/`string -> option` |
| REFUSED | 11 | 5 in-place mutators, 4 `with`-binds, 1 heterogeneous list literal, 1 `else:` block |
| CONVERTER-FAILED | 1 | `Module2_Parser.__init__` (a census artifact) |

The eight LOWERS, adjudicated:

    errors.py::message                    CHECK 1 PASSES     -> LANDING
    proof2why3/sertop.py::__exit__        CHECK 1 PASSES     -> LANDING
    audit_proof_reverify.py::_cache_root  CHECK 1 FAILS      -> refused (nullary `val`, no `writes`)
    frontend/pure_ast.py::iter_child_nodes a GENERATOR       -> refused by check-yield-erasure.py
    frontend/pure_ast.py::visit           census artifact    -> a facade
    module6_whyml/statements.py::rec      census artifact    -> a facade
    ir_schema.py::validate_ir             UNADJUDICATED      -> next, via check1.sh
    pycsl.py::_finalize                   UNADJUDICATED      -> next; it is one of the 5 NESTED stubs

**So the measured frontier is: of 410 strict markers, 56 can be retired by proof alone; of
those 56, six lower; of those six, two land today.** Everything else needs a capability — and
the 36 TYPE errors name which one, in one voice: the container/field value model.

## And the porting programme, sized

The 235 facades, by file, with the number of LIVE lines a faithful port would have to move:

    frontend/pure_ast.py            48 facades    849 live lines
    module6_whyml/expressions.py    36 facades   9976
    frontend/Module2_Parser.py      24 facades    728
    frontend/Module5_IREmitter.py   18 facades   2230
    frontend/Module3_Weaver.py      13 facades   2776
    proof2why3/canonical.py         11 facades    324
    frontend/monomorphize.py         9 facades    266
    ... 26 more files ...
    TOTAL                          235 facades  22252 live lines

**22,252 lines.** That is the size of the work the marker count has been quietly deferring,
and `module6_whyml/expressions.py` alone is 45% of it — the file whose mirror proof already
takes **2h57m** at its current, mostly-stubbed size.

## The porting programme has a cheap head — 22 facades with a live body of five lines or less

"22,252 lines" is the total, and a total is the least useful way to describe a programme. By
the LINE COUNT of the live body each port would have to move:

    live body <= 5 lines    22 facades
    live body <= 10         28
    live body <= 25         73
    live body <= 60         50
    live body >  60         62

**Fifty of the 235 need ten lines or fewer.** The whole cheap tier, named:

     2  frontend/Module2_Parser.py       _parse_assigns
     2  frontend/pure_ast.py             _const_value_getter
     2  frontend/pure_ast.py             _const_value_setter
     2  frontend/pure_ast.py             write
     2  proof2why3/parser.py             __repr__
     2  proof2why3/sertop.py             __enter__
     3  frontend/Module2_Parser.py       _err
     3  frontend/pure_ast.py             node
     3  frontend/pure_ast.py             set_precedence
     3  frontend/pure_ast.py             unparse
     3  module6_whyml/expressions.py     _e
     4  audit_proof.py                   extend
     4  frontend/ConcurrencyChecker.py   _check_function
     4  frontend/Module1_Ingestor.py     _emit_block_footer
     4  frontend/pure_ast.py             _decode_fstring_middle
     4  frontend/pure_ast.py             delimit_if
     4  proof2why3/extract_lean_meta.py  lean_meta_available
     4  proof2why3/sertop.py             parse_sexp
     5  frontend/Module2_Parser.py       _parse_expr_list
     5  frontend/Module2_Parser.py       parse
     5  frontend/pure_ast.py             next
     5  frontend/pure_ast.py             visit_MatchStar

Note the sixth entry. `proof2why3/sertop.py::__enter__` is the SIBLING of the `__exit__` this
session proved — live body `return self`, mirror body `return None`, a one-line port. It is
the natural next candidate, and it is the shape the whole tier shares: a facade a previous
window wrote in thirty seconds, standing where a two-line body belongs.

**This changes how the programme should be attacked.** The instinct from "22,252 lines" is to
call it infeasible and work the value model instead. The tiering says there is a head of ~50
functions that can be ported in an afternoon, each one then subject to the same four checks —
and each port that lands converts a marker that a proof alone could never have touched.
