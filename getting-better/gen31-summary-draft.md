# Generation #31 — summary (DRAFT, updated as the window runs; started 2026-09-25T04:18Z)

> This file is written INCREMENTALLY, not at the deadline. Every number in it is measured and
> carries the commit that measured it. Where a number was wrong and corrected, both are here —
> the correction is usually the more useful entry.

## The one-sentence version

The generation's second half turned the TCB-reduction campaign's instruments on the campaign
itself, and the instruments lost: the conversion population is a fifth of what the marker count
implied, the integrity gate on the count had been checking 92% of the population it was meant
to, and the headline number ended the session exactly where it started — 460 — with two
markers retired by proof and two added by discovering they had never been verified.

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

## Still open at the time of writing

* increment G — the I4 fixpoint (a set's element type). Patch prepared and measured: 1 corpus
  mover, 10 mirror movers, and the mirror re-proof bill is the expensive half (~6-8 hours,
  dominated by `expressions.py` at ~3h). Plan in `$SCRATCH/g31/g_plan.md`.
* the string/list FIELD value model — 36 named, reproducible witnesses.
* the nested-closure lift — backlog #54; retires both honest markers and gates 5 traps.
* the 22,252-line porting programme.
