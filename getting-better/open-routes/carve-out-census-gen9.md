# CARVE-OUT CENSUS — GEN #9

## PROBE RESULTS SO FAR (4 of 10 resolved) — READ THIS BEFORE SPENDING ANYTHING

| # | candidate | verdict |
|---|-----------|---------|
| 1 | annotated store inside `__init__` | **LIVE, and the mechanism story was WRONG — became ROUTE #83.** The predicted cause (the `AnnAssign` Attribute hole) is REAL but IRRELEVANT: the UN-ANNOTATED control proves the same false claim. The actual cause is `for stmt in child.body:  # top-level only`. **Had the candidate's repair been built, it would have fixed the annotated spelling, left the commoner un-annotated one open, and passed every gate.** |
| 2 | bare `with <ctx>:` | **REFUTED — FAIL-CLOSED.** Routes #38/#39 refuse it with an explicit `whyml-emit` error that names itself and covers the BARE form, not only the `as` form. The candidate read `_with_bindings` and missed the later guard. DO NOT RE-PROBE. |
| 3 | `try/except/else` drops the `else` | **REFUTED — FAIL-CLOSED.** Route #37 raises an explicit `whyml-emit` error for an `else:` that jumps out. The NON-jumping `else` is modelled FAITHFULLY (true claim proves, false refused). DO NOT RE-PROBE. |
| 4 | `assert` lowers to `()` | **LIVE — became ROUTE #84**, and it is the sharpest find of the generation: the same mutation OUTSIDE an assert is a PIPELINE ERROR, so the assert LAUNDERS A REFUSED CONSTRUCT past its own guard. |

| 7 | `_array_coerce_arg` -> `(Array.make 1 0)` | **REFUTED — FAIL-CLOSED.** A generator into `sorted(...)` is refused; the `*args` splat form RAISES `TypeError` in CPython and so is out of the value plane's scope entirely. DO NOT RE-PROBE. |
| 8 | `@mutable_state` set/dict PARAM mutation -> `()` | **REFUTED — FAIL-CLOSED IN BOTH DIRECTIONS.** Neither `\result == False` nor `\result == True` proves for `s.add(5); return 5 in s`. Incomplete, not unsound. Consistent with gen #8's finding on the neighbouring local-actual carrier. DO NOT RE-PROBE. |

**HIT RATE 2 of 6, AND EVERY ONE OF THE FOUR MISSES WAS "A LATER GUARD THE SWEEP DID NOT READ".** That is
the systematic bias of a text-pattern census: it finds the carve-out COMMENT but cannot see a
refusal that lives in a different module and fires later. **Probe before believing — and when a
candidate turns out live, probe its MECHANISM story separately from its EXISTENCE, because #83
shows those can come apart.**

Candidates 5, 6, 9 and 10 remain UNPROBED. On the evidence above they are the LOW-VALUE tail:
every refuted candidate was refuted the same way, and 9 and 10 were already ranked low on
reachability and latency respectively.

---

# THE ORIGINAL RANKED LIST (candidates, as written before probing)

**STATUS: A RANKED CANDIDATE LIST FROM A READ-ONLY SWEEP. NOTHING HERE IS A ROUTE UNTIL IT IS
PROBED IN BOTH DIRECTIONS AT HEAD.** Every claim below was produced by a sub-agent and is
therefore UNVERIFIED — rule (o). Probe before believing, and record the no-findings too.

The generator, restated: **a prose carve-out in the module upstream of a guard is an unexploited
route with a signpost on it.** The refinement that matters for ranking: an erasure to a
**DEFINITE** value (a literal `0`, an empty array, a `Pass`, a `true`) is dangerous, because the
emitter then proves definite facts from it; an erasure to an **UNCONSTRAINED** value is merely
incomplete. And the program must stay **TOTAL** — if reaching the construct makes CPython raise,
the value-differential plane rules it out of scope (that is #77's residue mistake, and #80 is
what happens when the "it raises" claim is itself wrong).

## THE RANKED CANDIDATES

1. **`__init__` IS EXCLUDED FROM THE ANNOTATED-STORE NORMALIZER.** `desugar.py:413-418` protects
   every `AnnAssign` in the whole `__init__` subtree (via `ast.walk`, so nested in `if`/`for`
   too), and `Module5_IREmitter._py_stmt_annassign:1891` has **no `else`** for an Attribute
   target — so `self.v: int = n` inside a conditional in `__init__` emits NO IR AT ALL.
   Candidate carrier: `C(7).v` claiming `0`. DEFINITE. **This is the one the gen-#8 ladder named
   as "the annotated-store-inside-`__init__` drop" — it is now located precisely.**

2. **A BARE `with <ctx>:` (no `as`) ERASES THE CONTEXT MANAGER.** The carve-out at
   `Module5_IREmitter.py:5537` says the refusal "keys on the `as` clause alone", and a bare
   `with` with no `#@ critical` falls to `ir_stmts.extend(body_ir)` — `__enter__`/`__exit__` and
   their mutations gone. Route #20 closed the `as` form; this is the same defect ONE TOKEN OVER,
   the #77/#80 geometry. DEFINITE.

3. **`try/except/else` DROPS THE `else` WHENEVER ITS LOWERED TEXT CONTAINS `raise`**
   (`stmt_control_flow.py:1803-1810`) — and `return`/`break`/`continue` all lower to `raise`,
   so the MOST COMMON `else` shape is the dropped one. Route #21's refusal covers
   `_final and handlers` and never looks at `orelse`. DEFINITE.

4. **`assert` LOWERS TO `()`, SIDE EFFECTS INCLUDED** (`statements.py:3221`). The
   "conservative and sound" justification covers the CONTROL effect of a FAILING assert; it says
   nothing about evaluating a side-effecting TEST that SUCCEEDS. Candidate carrier:
   `assert xs.pop() == 3` then `len(xs)` — the assertion HOLDS, so CPython does not raise and
   the program is total. DEFINITE.

5. `map int (option int)` argument coercion substitutes `(const None)` — **the EMPTY map, not an
   unknown one** (`expressions.py:7396`). This is verbatim the claim route #48 refuted, and the
   refutation is quoted 2000 lines below in the same file; #48's fix went to the CONSTRUCTOR arm
   and this ARGUMENT-COERCION arm still stands. DEFINITE.

6. Truthiness of an `hval` map local emits the literal `true` (`expressions.py:663`), so
   `if not vinfo:` is decidably false and the branch CPython takes on an empty map is DEAD in
   the model — the #25/#26/#27 structure, and this arm sits AFTER their refusal. DEFINITE.

7. `_array_coerce_arg` turns any IR-dropped iterable into `(Array.make 1 0)`
   (`expressions.py:940`) — the LENGTH is definite (1) even though the consuming abstract op is
   unconstrained, so `len(...)` folds to a decidable 1. MIXED.

8. A `@mutable_state` set/dict PARAMETER mutation lowers to `()` (`statements.py:3101`) on the
   stated grounds that "no contract here reads it" — a claim about the CURRENT CORPUS, not about
   the lowering. The non-`@mutable_state` twin is REJECTED outright at `:3111`, so the decorator
   converts a hard refusal into a silent no-op. DEFINITE. (Gen #8 probed a NEIGHBOURING shape —
   the set-param mutation observed through a LOCAL ACTUAL — and found a PIPELINE ERROR, not a
   route. This is a different carrier; check it is not the same one before spending.)

9. The four ASDL location attributes stamped onto a node lower to `()`
   (`statements.py:2640`). DEFINITE but TRIPLE-GATED — a user would have to be writing a mirror
   of PyCSL's own parser. LOW reachability.

10. An empty-list placeholder is substituted by the int witness `0` (`expressions.py:7347`). The
    exculpation rests on two CONTINGENT facts about the callee (`\trusted`, `ensures true`)
    that are NOT asserted at the substitution site, which is gated on the ARGUMENT's spelling.
    Latent, with an unenforced premise — worth a guard even if inert today.

## REPORTED NOT-LIVE BY THE SWEEP — VERIFY BEFORE TRUSTING, BUT DO NOT RE-WALK BLIND

`_py_stmt_augassign` / `_py_stmt_assign` fall-throughs now carry explicit refusals
(`Module5_IREmitter.py:1748`, `:1808`); `for...else` / `while...else` / `except*` / extended
slice / `assert` inside a catching `try` all RAISE in `desugar.py:291-355`; route #21's
`try/except/finally` raises at `stmt_control_flow.py:1738`; route #18's array-local reassign
raises at `statements.py:439`. `generic_fold.py`'s ~200 `return None` sites are recognizer
DECLINES falling back to a `\trusted val`, not value erasures — the whole family was excluded
deliberately and that exclusion looks right.

## A CROSS-CUTTING OBSERVATION WORTH MORE THAN ANY SINGLE CANDIDATE

Several carve-outs justify themselves with a CENSUS OF PYCSL'S OWN FOUR SOURCE POPULATIONS
("0 in the corpus, N in the live emitter", "no contract here reads it", "1450 asserts across
this tree stay exactly as they are"). **That is a statement about PyCSL's sources, never a
property of the lowering, and it does not constrain what a user can write.** A justification of
that shape is a signpost in exactly the way #78's "a sound under-approximation" was — it is an
admission that the arm is unsound in general and merely unexercised here. Grep for it.
