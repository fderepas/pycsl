# Generation #31 — summary (DRAFT, updated as the window runs; started 2026-09-25T04:18Z)

> This file is written INCREMENTALLY, not at the deadline. Every number in it is measured and
> carries the commit that measured it. Where a number was wrong and corrected, both are here —
> the correction is usually the more useful entry.

## The one-sentence version (rewritten 2026-09-26T10:00Z, and the first version was wrong
## about which number matters)

The generation turned the TCB-reduction campaign's instruments on the campaign itself, and the
instruments lost twice. First on SCOPE: the conversion population is a fifth of what the marker
count implied, and the integrity gate on the count had been checking 92% of the population it
was meant to. Then, on the second day, on SUBSTANCE: **`bin/run-soundness-planes.sh --slow` had
never been run by any gate — twenty-eight invocations, all printing "all 48 plane(s) green" —
and one run of it found SIX conversions this session had banked that were hollow**, five
input-blind and one yield-erasing, two of them with the verdict already written in their own
source comment. All six were re-trusted.

What the generation is actually worth is not the marker count, which ended HIGHER than it
started (460 -> 451, after 446 and then +6 for the reverts). It is:

  * the four CONVERSION ORACLES are no longer behind a flag, so that failure cannot repeat;
  * `bin/price-the-conversions.py` measured, for the first time, what a conversion ESTABLISHES
    — and then 91 new PROVED functional postconditions took it from 146 of 922 to 237 (26%);
  * three spec-LANGUAGE walls were located precisely (backlog #60), one of them removed;
  * `bin/screen-conversion-candidate.sh` makes the amended criterion executable in 5 minutes
    instead of 3 hours of prover time, and refused its first candidate;
  * `bin/check-cross-module-contract-parity.py` asks a question nothing asked: may an
    IMPORTING module ASSUME a clause its DEFINER does not PROVE? (Hard zero; negative-tested.)

## What landed

| increment | commit | what |
|---|---|---|
| A | (gated 04:08Z) | the compose_from repairs, corpus repairs, `check-corpus-executes.py`, `--expect-moved`, the `__new__` ARITY refusal |
| D | `af7f32c1` | **two `\trusted` markers RETIRED AND PROVED** — `errors.py::message`, `proof2why3/sertop.py::__exit__` |
| E | `594aa07d` | the frame plane's EXTERNAL-EFFECT half — 16 stubs that shell out under `assigns \nothing`, all named |
| — | `e8f33b10` | `check-yield-erasure.py` descends into nested defs (a trap closed while its population is 0) |
| F | `f184e94f` | the integrity gate on the conversion count had been checking **863 of 915** |
| — | `74f5db2c` | the two honest markers pay their ledger debts: reasons synced (unclassified 458 -> 456), termination ratchet 53 -> 55 with both members named |

## The measurements that re-scoped the campaign

### The conversion population is 62, not 410

Over the 410 strict `\trusted` candidates, comparing each mirror body to its live twin **using
the fidelity plane's own `_normalize` and `_signature`**:

    VERBATIM    62   a proof can retire it
    FACADE     235   `pass` / `return None` — a proof can NEVER retire it; it needs a PORT
    DIFFERS    105   a real body, but not the live one
    AMBIGUOUS    8   the name is defined more than once in the file — reported, not guessed

A facade cannot land because un-`\trusted` mirror methods must be VERBATIM copies of live.
Deleting the marker moves the facade into that population, where `pass` must equal a 200-line
parser: it fails the FIRST plane, before a prover starts.

**The porting programme, sized for the first time: 22,252 live lines across the 235 facades,
45% of it in `module6_whyml/expressions.py` alone** — the file whose mirror proof already takes
2h57m at its current, mostly-stubbed size.

The number was wrong twice and all three values are recorded, because HOW it was wrong is the
lesson: 61 (keyed on bare names — a file with two `visit`s let a facade match the other one's
live body), 56 (compared raw source text — four `#@` lines on a nested closure scored as a
"stale copy" at 0.991), 62 (asks the plane that decides).

### Of the 62, six lower and two land

    errors.py::message                     LANDED — 4 frame `ensures` assumed -> proved, x4 classes
    proof2why3/sertop.py::__exit__         LANDED — zero new `val`; the live body really is `pass`
    audit_proof_reverify.py::_cache_root   check 1 refuses — `os.mkdir` -> a nullary `val`, no `writes`
    ir_schema.py::validate_ir              check 1 refuses — 20 new abstract ops, `ir_keys_0 ()` NULLARY
    frontend/pure_ast.py::iter_child_nodes a generator; `check-yield-erasure.py` already refuses it
    pycsl.py::_finalize                    BYTE-IDENTICAL emission; converting it proves nothing

**Every check-1 refusal is the same shape**: an operation the value model cannot carry becomes
an abstract `val` that does not take the thing it operates on — a directory, a dict's keys, a
generator's yields. The `let` typechecks, the prover discharges it, and the program that was
verified is not the program that runs.

### The other 56 name one capability

36 of them are Why3 TYPE errors, and **both directions appear** — six `int` where `string` is
wanted, five `string` where `int` is wanted. That is not a missing coercion. It is a value
model carrying a Python `str` as a Why3 `string` in parameter/return position and as an `int`
in record-FIELD position. `errors.py::__str__`'s own `\trusted` comment predicted it:

> A faithful string field model retires this marker AND several others.

The census makes "several others" a number. And the sharpest instance: `errors.py::message`,
the marker this session proved, is a method on the SAME class whose `__str__` cannot convert
for exactly this reason. It could be proved only because its body never touches a string field.

### The integrity gate had been checking 863 of 915

`check-untrusted-emitted.py` exists so that *"the count improves, the TCB does not"* cannot
happen. Its walk stopped at a `def`. The FIDELITY plane descends. So 52 nested un-trusted
closures sat inside the population this project calls verified while that gate had never looked
at one.

Found by check 1 on `pycsl.py::_finalize` returning a byte-identical emission. Fixing it took
three changes — the walk descends (863 -> 915), a new `FOLDED` shape for closures the emitter's
recognizers consume into an emitted parent's model (41), and a STATIC refusal for a closure
inside a `\trusted` parent (2, one of which the emission check could not see because
`core_ir_semantic.py` has five closures called `walk`).

**Validated nine minutes after landing**: the screen produced `_is_false_goal` and `_probe_one`
as LOWERS, and both are trusted-parent traps the new check refuses. Census: 5 of the 410.

## The accounting

    460  session start
    458  message + __exit__ PROVED, all four checks
    460  _hdr_name + _returns_literal_none::walk take HONEST markers
    455  FIVE more retired by PORTING the live body in and proving the result
    886 -> 888 -> 886 -> 891 verbatim un-trusted
    834 -> 817 trusted-or-dependent

Two functions left the trusted set by being proved, two joined it by being found never to have
been verified, and then five left it by being PORTED. **Five markers, seventeen off the
trusted-or-dependent aggregate** — retiring a marker on a function nothing trusted-depends on
removes its whole dependent cone with it, which is the thing the marker count has never been
able to show. The ratchet that measured it was added six hours earlier for the opposite reason.

### Increment H, in full

    proof2why3/sertop.py::__enter__               1-line port
    frontend/Module2_Parser.py::_err              2-line port, converts TWO functions
    module6_whyml/identifiers.py::stable_hash     1-line port
    proof2why3/parser.py::__repr__                1-line port
    frontend/monomorphize.py::_rewrite_call_sites 5-line port

`_err` is the one to read: the ported body calls `_contractparser__cur`, which was sitting in
the emission as an unused `val` and becomes a `let` with it, and `ensures { false }` survives,
so the emitted `let` now PROVES that `_err` never returns normally where the `val` assumed it.

REFUSED and not landed: two Z3 timeouts (7.4M and 3.19 BILLION steps — a COST boundary, not a
correctness one) and the five `pure_ast.py` candidates together, on check 1, for three new
abstract operations.

### The I4 fixpoint also works, and it is not a fixpoint

Dry-run on an offline tree: the carrier flips FAILED -> SUCCESS and BOTH controls hold. The
thing a generation called "the deferred I4 fixpoint" is one rule stated twice and implemented
once — `_m5_get_field_key_type` already covered `Set[str]` (*a set's element IS its key*) while
`_m5_get_dict_key_type` covered only `Dict[str, V]`. Reading the key type from the DECLARATION
makes both ends of a call edge agree by construction. No propagation pass, nothing to converge.

## Ratchets that rose, each with its members named

    MIN_TRUST_FREE            540 -> 538
    MAX_TRUSTED_OR_DEPENDENT  833 -> 834   (a NEW ratchet, added and then moved the same session)
    MAX_SILENT                 53 -> 55
    MAX_UNCLASSIFIED          458 -> 456   (this one FELL — a classified arrival counts)

Wall-lesson (l6) is the rule that came out of it: a ratchet may rise only in a commit that names
the members that moved it and the capability that retires them.

### The 235 facades are not a dead population — a PORT lands where a proof cannot

A facade cannot be screened as it stands: `pass` always lowers, so nothing could be learned
about any of the 235. Porting the live body makes a candidate MEASURABLE.

`proof2why3/sertop.py::__enter__` was taken end to end as the proof of concept: a ONE-LINE
port (`return None` -> `return self`), an 11-line all-additive emit diff identical in shape to
`__exit__`'s — `val` becomes `let`, four frame `ensures` move from assumed to proved, no new
`val` — and `[+] Verification SUCCESS!`.

Tiered by the size of the live body a port would move: **22 facades at <= 5 lines, 50 at
<= 10**, 73 at <= 25, 50 at <= 60, 62 above. The instinct from "22,252 lines" is to call the
programme infeasible; the tiering says there is a head of ~50 portable in an afternoon.

But a port does not make a candidate LAND. Screening the 50 cheap ones after porting them
returns the same three walls the 62 verbatim candidates met — overwhelmingly the value model
(`int` / `string` / `array` / `seq`), then the in-place mutator refusal. That is the fourth
independent measurement this session pointing at one capability.

### The instrument failed four times, and each failure is in the record

    the census keyed on BARE names                  61 -> 56   caught by the screen's own output
    the census compared RAW SOURCE TEXT             56 -> 62   caught by a 0.991 "stale copy"
    "836 of 888" was SUBTRACTED, not measured      -> 863 of 915
    `port_one.py` crashed BEFORE writing            10 false `PORTS+LOWERS`

The last one is the sharpest. `ast.walk` yields context nodes (`Load`) with no position, the
`x.lineno` fallback raised, the crash happened before the file was written, and the screen
classified on the first word of the message — a traceback does not start with `ABORT`. So it
emitted the PRISTINE file, which lowers, and reported success for ten candidates it had never
touched. **7 of 7 was not evidence that porting works; it was evidence that nothing was being
measured.** The fix is general: a crash must look like an abort.

### The I4 fixpoint: landed, measured, reverted in five minutes

The one capability this session tried to build. A carrier written a generation ago, gated
FAILED ever since, with its landing instructions inside it. The two-line patch **flipped the
carrier, held both controls, and proved three new corpus witnesses** — and then broke four
mirror files in thirty seconds, every one of them:

    This expression has type string -> option.Option.option int,
    but is expected to have type int -> option.Option.option int

a promoted `map string` reaching a sibling `val` BRIDGE still declared `map int`. **"Both ends
read the declaration" is false**: a bridge has no Python declaration to read. Promoting the
definition side moves one end of the call edge and leaves the other. The fixpoint was not
deferred out of laziness; it is load-bearing.

Landed 07:58Z, reverted 08:03Z. The refusal written into the plan BEFORE any edit is what made
the reversal automatic rather than a decision.

**And it is the third "necessary but not sufficient" of the session.** A `--no-proof` LOWERS is
not a proof. A green whole-file proof is not a conversion. **A carrier that flips is not a
capability.** Each is a cheap gate that answers a real question and only that question; the
expensive gate behind it is the one that decides — and this session found all three by running
the expensive one anyway.

## The porting vein, run to the end of what is reachable

Increments H, I, J, K and L each landed ported markers, every one adjudicated by the four
checks and gated at 4029/4047:

    H  460 -> 455   __enter__, _err, stable_hash, __repr__, _rewrite_call_sites
    I  455 -> 453   pure_ast::error, pure_ast::unsupported          (3h06 of prover time)
    J  453 -> 452   Module6_WhyMLTranspiler::__init__               (172-line port)
    K  452 -> 451   expressions::_emit_metatype_tags                (5h27, the longest proof)
    L  451 -> 450   pure_ast::iter_fields                           (2h25; I predicted refusal)

**Ten markers retired by proof in one session, and the trusted-or-dependent aggregate fell
833 -> 799.** The aggregate is the number the marker count cannot show: increment H moved it
seventeen on five markers, increment I sixteen on two, because a marker on a widely-called
helper carries its whole dependent cone with it.

### The three results worth carrying out of the porting work

1. **A port's difficulty is not its length.** `Module6_WhyMLTranspiler::__init__` is 172 lines
   and introduces ZERO abstract operations. `pycsl.py::_parse_args` is 174 lines, also proves,
   and introduces TEN — the whole of `argparse` going uninterpreted, `ArgumentParser()` a
   nullary oracle. Two ports of the same size, both green, and only the emit-diff separates
   them.
2. **Batch to share a PROOF, never to share a VERDICT.** Five `pure_ast.py` candidates together
   gave three new ops and `Unknown (why3: Out of …)`. Split, `error` + `unsupported` proved and
   `iter_fields` proved. When a batch fails, every member is unadjudicated.
3. **A moved emission is not a checked emission.** Porting `__init__` moved `pycsl.mlw` too —
   its `module6_whymltranspiler` record type gained TWELVE fields the facade had omitted, so
   the port made the model faithful. `--expect-moved` caught it undeclared; the file was then
   re-proved by hand (42 min, green).

## Still open at the time of writing

* increment G — the I4 fixpoint (a set's element type). Patch prepared and measured: 1 corpus
  mover, 10 mirror movers, and the mirror re-proof bill is the expensive half (~6-8 hours,
  dominated by `expressions.py` at ~3h). Plan in `$SCRATCH/g31/g_plan.md`.
* the string/list FIELD value model — 36 named, reproducible witnesses.
* the nested-closure lift — backlog #54; retires both honest markers and gates 5 traps.
* the 22,252-line porting programme.

## DAY TWO (2026-09-26) — the audit, and what replaced the marker count

### The five REDs, and two of them were this session's own conversions

`--slow` adds 25 planes. Every gate script ran the battery with no arguments. Run once at
21:48Z on the increment-N tree: **5 of 73 RED.**

| plane | verdict | whose |
|---|---|---|
| `check-emitted-vacuity` | FIVE new erasures: `error`, `unsupported`, `_err`, `_rewrite_call_sites` (BOTH args), `stable_hash` | THIS SESSION |
| `check-yield-erasure` | `pure_ast.py::iter_fields` — a `unit` body, `true` contract, the yielded pair replaced by `any int` | THIS SESSION |
| `check-shadowed-selfcalls` | 17 > 14 — `error` (19 bypassing sites), `_err` (7), `unsupported` (2) | THIS SESSION |
| `check-getattr-erasure` | corpus 1859/1860 unregistered | pre-existing |
| `check-stdlib-modules-verify` | `re/__init__.py` newly not verifying | pre-existing |

`unsupported`'s own surviving comment said, before the marker was removed: *"converting emits
`_parser__unsupported erased=['what'] of ['what']` — input-blind."* `_err`'s said it *"was
converted, then REVERTED by two planes in succession."* Both commits deleted the marker and
left the comment saying "STAYS trusted". **The prediction was in the file, the oracle was in
the repo, and the gate ran neither.**

The `re/__init__.py` red was worth its own finding: the goal `_check_class_inv_rematch` is
FALSE (nothing constrains `start`), Alt-Ergo answers `Unknown (why3: Out of memory)` rather
than `Invalid`, and the hole existed because #34 fixed a `#@`-binding bug that turned two
silently-discarded class invariants into real obligations. **An instrument that starts working
produces a red that looks like a regression.**

### What a conversion is worth, priced for the first time

    146   16%   a FUNCTIONAL postcondition        ->  237   26%  after this session's work
    495   54%   PURITY only (`assigns \nothing`)  ->  460
    207   22%   a NON-TRIVIAL FRAME only          ->  161
     74    8%   neither (50 of them nested closures, no `#@` block by design) -> 64

Five out of six conversions proved no functional postcondition. That is not nothing — purity,
type safety, termination and the SYNTHESIZED per-field frame preservation are all real, and
`errors.py::message` carries no `#@` line at all yet emits four `ensures { self.f = old
self.f }` its abstract `val` merely assumed. It is also not what "verified" is usually read to
mean, and the difference is the whole value of the number.

### 91 postconditions, and the three walls that stopped the rest

    19   irx.py (10, the whole typed IR-accessor layer, against the FAITHFUL
         `map string (option string)`), proof2why3/ir.py (3), expr_ghost_collections (3),
         audit_proof, crosscheck, expr_ghost_spec_ops
    72   frontend/Module5_IREmitter.py's IR CONSTRUCTORS — `\result["type"] == "<tag>"` now
         lowers to `kind_of result`, the projection the BODY position has used for
         generations. 72 of 74; the two that fail are a measured TIMEOUT (39,981,778 and
         80,324,449 steps), not a falsehood, and are left as `ensures True` with the numbers
         at the site.

and the walls, all three SPEC-LANGUAGE rather than proof (backlog #60):

  * a dict subscript on `\result` was `unbound symbol 'subscript_get'` — REMOVED this session;
  * the contract grammar has NO METHOD CALL AT ALL, only a bare-name call (three probes), which
    blocks every emitter mixin handler's postcondition — hundreds of functions;
  * `.strip()` is refused in a contract, which blocks the two kernel-axiom allowlist predicates.

**AND THE IMPORTING MODULE CANNOT STATE THE 72 AT ALL.** `pycsl.mlw` types the same function's
stub `map int (option int)`, not `emit_ir`: the same function has TWO MODELLED RETURN TYPES IN
TWO FILES. The clause is dropped there — a `val` with fewer `ensures` assumes less — and
`bin/check-cross-module-contract-parity.py` was written the same hour to make that safe
direction a CHECKED fact. Measured: 248 symbols appear as both a stub and a definition, 67
carry exactly what is proved, 447 carry fewer, and ZERO carry more.

### Three instrument failures in my own tooling, all fail-loud, all recorded

  (q6)  an oracle that is not in the gate is not a gate — and a population measured once is a
        fact about that hour (the yield population was measured at 0 BEFORE the conversion that
        populated it)
  (r6)  editing a running shell script skipped an hour-long gate stage — AND IT HAPPENED AGAIN
        TEN HOURS LATER on a different file, so the lesson is now a mechanism: while a gate
        runs, only `getting-better/**` and scratch are writable
  (s6)  a scratch tree built from `src` emits a DIFFERENT PROGRAM — the emitter's import search
        includes CWD and this repo keeps a TRACKED `json/` package at the ROOT, so every screen
        this session ran was six declarations short of the program the gate measures
