# Ideas for a convergence metric — an independent second opinion (2026-09-13)

Question asked, verbatim: *"Which metric could I use to make sure we are doing in the right
direction and that we'll converge some day by being back on the 'reducing the amount of
trusted' track?"*

Everything numeric below was measured today with the command shown, read-only, at HEAD
`6af17b7a` (2026-09-13 14:09 UTC). Where I could not measure something I say so.

---

## 0. The answer in six lines

1. The sentence bundles two questions that need two instruments: **(a) is the soundness hunt
   converging?** and **(b) when can marker reduction resume?** (b) is NOT gated on (a) — see §2.
2. **Primary metric for (a): probe yield with a recorded denominator**, split into first-order
   routes (a pre-existing defect) and second-order routes (the carrier is a campaign repair).
   Converging = first-order yield per probe falls toward 0 *with the probing process held
   fixed*; second-order yield falls to 0. Cheap to start today (a TSV ledger); an
   independent sampler is the phase-2 upgrade that removes hunter bias (§3.4).
3. **Primary metric for (b): body-verified fraction of the live verifier**, 914 / 3236 defs =
   **28.2 %** today. It replaces the 459 count, which has no denominator and hides 41
   unmirrored files. The resume trigger is a separate, heavy, already-existing instrument:
   `bin/probe-conversion-candidates.py` CLEAN count (§3.7) — currently 1 of 446, i.e. zero.

> **CORRECTION ADDED 2026-09-13 BY THE PHASE-2 IMPLEMENTATION — DO NOT QUOTE 28.2 % .**
> That number computes verified defs as `mirror defs − markers`, which treats *absence of a
> `\trusted` marker* as *evidence of proof*. It is not. Recomputed from PROOF VERDICTS
> (`rc=0` + zero non-Valid goals, proof must postdate the last change to the mirror file and
> to its live counterpart):
>
> ```
> $ bin/verified-fraction.py --staleness=file
>   (1) verified / live        499 / 3225 = 15.47 %
>   (2) unproven-perimeter     644 defs in 27 of 53 mirror files
>   (3) unmirrored ratchets    MAX_UNMIRRORED_DEFS=549  MAX_UNMIRRORED_FILES=41
>       OLDEST PROOF RELIED ON 2026-09-02
> ```
>
> Only **26 of 53** mirror files have a fresh passing whole-file proof on record; 18 have no
> proof at all, 7 have a stale one, 2 have a FAILING one. Under the stricter rule — a proof
> is stale if ANY commit to `src/pycsl` postdates it, which is defensible because the emitter
> is one program — the answer is **0 / 3225 = 0.00 %**. Both are printed; see
> `bin/verified-fraction.py --staleness=strict`. The corrected fraction is roughly **HALF**
> the figure below, and the gap IS the unproven perimeter.

4. **The thing you can do this week that is genuinely "back on the reducing-trusted
   track" without a new capability**: shrink the *assumption-honesty deficit* — 70 `\trusted`
   stubs whose live body raises and whose stub says nothing (§3.6). It is already ratcheted.
5. **Most surprising finding**: no route file records a plane, ratchet, or differential corpus
   going red as the way a route was *discovered*. All 56 routes were found by the driver
   probing. The 34 planes have only ever confirmed closures and caught regressions. So the
   campaign has no instrument independent of the hunter — which is exactly why "is it
   converging" cannot currently be answered, only narrated.
6. Weak metrics, one line each, are in §4. Do not use raw route count, open-ledger size,
   or "N planes green" as convergence signals; each is explained there.

---

## 1. The evidence base (measured today)

| quantity | value | command |
|---|---|---|
| `\trusted` markers in mirror | **459** (all 459 lines are the identical text `#@ \trusted reviewer: pycsl-self-annotate` — no reason tag) | `grep -rhE '^\s*#@\s*\\trusted' src/self-annotate/src --include=*.py \| sed -E 's/^\s+//' \| sort \| uniq -c` |
| mirror `def`s | 1373 in 53 files | `grep -rhcE '^\s*def ' src/self-annotate/src --include=*.py \| paste -sd+ \| bc` |
| live `def`s | **3236** in 94 files | same over `src/pycsl` |
| live files with no mirror | **41 of 94** | python set difference of the two trees |
| live `def`s inside the 53 mirrored files | 1929 (so ~556 unmirrored by this count; `check-mirror-coverage.py` ratchet says 549/41 — different def-matching rule, same order) | see §3.5 |
| body-verified live defs (mirror defs − markers) | 1373 − 459 = **914** | arithmetic |
| markers at three past commits | 650 (eaaf85f7, 08-21) → 451 (b39d07b2, 09-02) → 456 (309d8bf4, 09-09) → 459 now | `git grep -chE '^[[:space:]]*#@[[:space:]]+\\trusted' <h> -- 'src/self-annotate/src/*.py' 'src/self-annotate/src/**/*.py' \| awk -F: '{s+=$NF} END{print s}'` |
| `raise PyCSL*Error` sites in live tree | 176 → 179 → 196 → **222** at the same four points | `git grep -nE 'raise PyCSL[A-Za-z]*Error' <h> -- 'src/pycsl/*.py' 'src/pycsl/**/*.py' \| wc -l` |
| distinct `PYCSL-…` refusal codes | 40 → 40 → 54 → **61** | `git grep -hoE 'PYCSL-[A-Z0-9][A-Z0-9-]+' <h> -- … \| sort -u \| wc -l` |
| pycsl-reference corpus `.py` | 906 → 913 → 1051 → **1208** | `git ls-tree -r --name-only <h> -- test-suite/corpus/pycsl-reference \| grep -c '\.py$'` |
| of which `# pycsl-expected: FAIL` | 184 → 184 → 287 → **401** | `git grep -l '^# pycsl-expected: FAIL' <h> -- 'test-suite/corpus/pycsl-reference/*.py' \| wc -l` |
| expected-PASS (difference) | 722 → 729 → 764 → **807** | arithmetic |
| route-named witness files / of which expected-FAIL | 268 / 187 | `ls test-suite/corpus/pycsl-reference \| grep -ci route` ; `grep -l '^# pycsl-expected: FAIL' …/*route*.py \| wc -l` |
| route files | 56 (#42–#98) | `ls getting-better/open-routes/route*.md \| wc -l` |
| routes by first commit mention, per day | 09-04: 9 · 09-05: 3 · 09-08: 10 · 09-09: 3 · 09-10: 2 · 09-11: **21** · 09-12: 9 · 09-13: 8 | `git log --reverse --date=short --format='%ad\|%s' \| grep -oE '^[0-9-]+\|.*ROUTE #[0-9]+'` then first date per number |
| time from first mention to `CLOSED(#49)` commit | 0–1 day for every route with a CLOSED commit (40 of them) | same log, `CLOSED\(#49\): ROUTE #N` |
| routes whose header cites an earlier route as carrier/mask/repair, in #77–#98 | 10 of 22; of those, **6 are explicitly "the carrier is a campaign repair"**: #86 (survivor of #85), #88 (survivor of #83), #89 (re-armed by #85/#87), #90 (composition of #42+#51), #95 (from w66's hardening), #98 (from #96) | `head -60 route*.md \| grep -oE 'route ?#[0-9]+'` + reading |
| routes carrying a severity tag | sev-1: 9 (#77, #85, #91–#96, #98), sev-2: 1 (#97); earlier routes untagged | `grep -liE 'sev(erity)?[- ]?1\b' route*.md` |
| routes recording a differential plane / ratchet going RED as the discovery | **0 of 56** | `grep -liE '(value\|no-exception)-differential[^.]{0,80}(RED\|found\|caught)' route*.md \| wc -l`; corroborated by the header of `bin/check-value-differential.py` ("Every one was found by a human-authored probe") |
| value-differential / no-exception-differential drivers | 56 (+1 negative) / 45 | `ls test-suite/value-differential/*.py \| wc -l` |
| soundness planes | 19 fast + 15 slow | `bin/run-soundness-planes.sh` PLANES / SLOW_PLANES arrays |
| `check-trusted-raises-honesty` | **SILENT 70**, declared 5, `MAX_SILENT = 70` | `bin/check-trusted-raises-honesty.py:73`; handoff gen #16 |
| `check-trusted-frame-honesty` | RATCHET 0 (was 82 on 2026-09-02 morning, 0 by evening — commits `bac0330d`, `46b9b592`) | `git log --format='%ad %s' -- bin/check-trusted-frame-honesty.py` |
| `check-mirror-coverage` ratchets | 549 defs / 41 files (born 550/41 at `40c29023`, 09-03) | `bin/check-mirror-coverage.py:54-55` |
| "no finding / do not re-probe" lines in the handoff | 48 | `grep -ciE 'NO FINDING\|probed clean\|DO NOT RE-PROBE\|fail(s\|ed)? closed' getting-better/driver-handoff-latest.md` |
| free conversions | "1 CLEAN of 446" (backlog §#32, 2026-09-02) — not re-measured today (needs emission; forbidden while the box is loaded) | `getting-better/driver-backlog.md:333` |
| other trust surfaces | `src/pycsl_lib` 2 markers; test corpus 39 (fixtures); mirror `\abstract` 0 | same grep over those trees |

Two readings of that table that matter for everything below:

* **The hunt's throughput is not a population signal.** Every route closes within a day of
  being found, so the open ledger sits at 0–2 whatever the true remaining population is. The
  handoff already says this in its own words ("an empty ledger is a prompt to generate, not a
  floor" — five times over). Per-day discovery (9, 3, 10, 3, 2, 21, 9, 8) tracks how many
  probes the driver ran that day, not how many defects remain — 09-11's 21 was one new
  generator (the carve-out census) applied to a fresh vein.
* **The repair instrument is a refusal, and refusals accumulate.** +43 raise sites and +21
  distinct refusal codes in eleven days. Nothing is wrong with that per se, but the corpus
  that would tell you what the refusals *cost* is now instrument-dominated: 187 of 401
  expected-FAIL files are route witnesses, so "expected-PASS share fell from 79.8 % to
  66.8 %" is mostly the witnesses arriving, not capability leaving. A capability-cost metric
  has to exclude witnesses (see §4).

---

## 2. Two questions, not one — and (b) is not gated on (a)

**(a) Is the soundness hunt converging?** Convergence means the *remaining* population of
routes is small and shrinking. A count of routes found can never say this: an adaptive hunter
(one who picks the next probe from the last finding) produces a discovery rate that tracks
their ideas, not the population. Two things are needed that the campaign does not currently
record as data: a **denominator** (probes run, including the 48 "no finding" outcomes that
today live only in prose) and an **independence check** (a second sampler that does not read
the first one's notes, so the overlap between the two estimates what is left).

**(b) When can marker reduction resume?** The backlog answered this on 2026-09-02 and it has
not changed: *"ZERO free conversions remain … Every remaining marker needs a NEW CAPABILITY"*
(`driver-backlog.md:333`). Marker reduction is therefore gated on **building a named
capability** (certified IR-node ADT, string-keyed set-op lowering, multi-variant certificate
bundle, …), not on the hunt reaching any threshold. The link between (a) and (b) runs the
other way: a capability is an emitter change, and the campaign's own record says emitter
changes are where routes come from (#42's `is` whitelist was a capability; six of the last 22
routes are repairs-of-repairs). So the honest coupling is a *process* gate on each capability
(both-direction witnesses + differential drivers shipped with it), not a metric threshold on
the hunt. **Nothing in the hunt's state should be used as a reason to keep (b) frozen**, and
one part of (b) can resume tomorrow (§3.6).

---

## 3. Candidate metrics

Format for each: what it measures · how to compute it here · what "converging" looks like ·
what falsifies it · what it cannot see · cost to instrument.

### 3.1 Probe yield with a recorded denominator — PRIMARY for (a)

**Measures.** Routes found per probe run, per generation, with each probe classified by
generator (continue-census, carve-out census, "probe every operation on a declared-safe
carrier", re-run carriers of a fresh repair, oracle audit, hand) and each outcome classified
LIVE / FAIL-CLOSED / INCOMPLETE / OUT-OF-SCOPE. Split LIVE into **first-order** (the carrier
predates the campaign) and **second-order** (the carrier is a campaign repair, hardening,
control, or remediation message).

**Compute.** Not computable from the repo today as data. The denominator exists only in prose
(48 no-finding lines in the handoff; "3 hits in 7 probes", "2 of 6", "top four gave three").
Instrument: a `getting-better/open-routes/probes.tsv` the driver appends one line to per
probe — `date  gen  generator  candidate  verdict  route#  order(1|2)`. One `awk` then gives
yield per generator per generation. Back-fill the last ~60 probes from the handoff and
`carve-out-census-gen9.md` in an hour.

**Converging.** First-order yield per probe falls across generations *for the same generator*
(generator-normalised, or it measures the driver's inventiveness). Second-order yield falls to
zero and stays there for three generations. Absolute first-order finds per generation fall
even as probes per generation stay flat.

**Falsified by.** A new generator restoring first-order yield to gen-#8 levels (21 routes in a
day). That is not a failure of the metric — it is the metric doing its job: it says the
population was not exhausted, only the previous generator was.

**Cannot see.** Defects no generator reaches. Yield falls to zero both when defects run out
and when ideas run out, and this metric cannot tell the two apart. §3.3 and §3.4 exist for
that reason. It also cannot see routes in code the corpus never exercises — #96 lived in a
2×2 cell "nobody in-tree writes", and the handoff's line *"that emptiness is why the bug
survived, not why it was harmless"* is the blind spot stated exactly.

**Cost.** Cheap: a TSV and a driver-rule line. Zero prover time.

### 3.2 Second-order route fraction (repair recurrence) — companion to 3.1

**Measures.** Of routes found in a window, the share whose carrier is a campaign artefact.
Measured today from route headers: **6 of 22 in #77–#98 (27 %)**.

**Compute.** Column `order` of the TSV above; until then, `head -60 route*.md` and read the
mechanism paragraph (the driver already writes "SURVIVOR OF", "carrier surviving", "re-armed
by", "composition of" — grep those).

**Converging.** Falls to 0 and stays there. Note the ambiguity in the other direction: a
*rising* share means either the first-order population is exhausted (good) or repairs are
being written narrowly (bad). Disambiguate with the absolute first-order count from 3.1 —
if first-order finds are also near zero, it is the good reading.

**Cannot see.** A second-order route whose author did not recognise it as one. #98 was
recognised because gen #16 re-ran #96's carriers with a renamed parameter; a generation that
did not would have filed it as first-order.

**Cost.** Free once 3.1 exists.

### 3.3 Capture–recapture estimate of the remaining population — the only metric here that speaks to "how many are left"

**Measures.** Lincoln–Petersen: two *independent* samplers find n₁ and n₂ routes with m in
common; N̂ ≈ n₁·n₂ / m, and N̂ − (routes known) is the estimated remainder. It is the standard
answer to "how many bugs remain" in software-reliability practice, and it needs only what the
campaign already produces plus one thing it does not: a blinded second sampler.

**Compute.** Run a *fresh* agent window against HEAD with the route ledger, handoff and
progress log withheld (the repo already has this discipline: the `self-tcb-reduction-driver`
skill's "INDEPENDENT `XXX-response.md` from a fable reviewer that never sees the sub-loop's
contents", and the backlog's "FRESH-EYES DELEGATION BROKE THE FALSE FLOOR" entry). Give it a
fixed probe budget (say 40 probes) and the CPython-ground-truth rule. Count its LIVE findings
(n₂), and how many are already closed routes or open ones (m). Run it once per two or three
generations.

**Converging.** m/n₂ → 1 (everything the blind hunter finds is already known) with n₂ > 0 —
that is the sign change. If n₂ = 0 the sample is uninformative (the #44 rule: a gate that
looked at nothing), so report it as "no measurement", not as convergence.

**Falsified by.** m/n₂ low: the blind hunter keeps finding things the driver did not. That is
the honest "not converging" verdict, and it also tells you which generators the driver lacks.

**Cannot see.** Both samplers share the same blind spots if they share the same *method*
(agent reading the emitter). Independence is about *information*, not about method, and the
estimate is biased low when the two samplers find the same "easy" routes first. A generated
corpus (3.4) as the second sampler has a different method and fixes that, at higher cost.

**Cost.** One agent window per measurement; no new code. The box constraint applies: the
blind hunter's probes need prover time, so schedule it when the reference suite is not running.

### 3.4 Independent sampler yield — a generated differential corpus (phase-2 upgrade of 3.1)

**Measures.** Routes per N mechanically generated total programs, with CPython as the oracle.
The harness already exists in exactly this shape — `bin/check-value-differential.py` (56
drivers) and `bin/check-no-exception-differential.py` (45) — but the drivers are hand-written
and, measured today, have never discovered a route; they confirm closures. A generator that
produces, say, 200 small programs per run from templates over the constructs the campaign has
touched (field literals, `__init__` capture shapes, aliasing, `is`, dict/set ops, `del`,
`assert`, frames on trusted stubs, renamed parameters) turns the plane from a ratchet into a
sampler with a fixed, repeatable process.

**Compute.** New script `bin/gen-differential-drivers.py` writing into a
`test-suite/value-differential/generated/` subtree that the standing run skips (the
`negative-test/` precedent), then the existing plane over it. Yield = RED / generated.

**Converging.** RED per 200 falls to 0 across three consecutive runs with the *template set
frozen*. When a new template family is added, expect a bump; report yield per family.

**Falsified by.** Any RED — and a RED here is worth more than a RED from the driver, because
the sampler did not know what it was looking for.

**Cannot see.** Constructs outside the template set; anything needing `#@ requires` richer
than `\result == <int>`; unsound *refusal messages* (#90's remediation-advice exploit).

**Cost.** ~1–2 days to write; each run costs prover time proportional to 200 files (order of
a few minutes each under `--timelimit 5`; not to be run concurrently with the suite).

### 3.5 Body-verified fraction of the live verifier — PRIMARY for (b); replaces the 459 count

**Measures.** (mirror defs − markers) / live defs = **914 / 3236 = 28.2 %**. Within the
mirrored perimeter only: 914 / 1929 = 47.4 %.

> **CORRECTION ADDED 2026-09-13 BY THE PHASE-2 IMPLEMENTATION — DO NOT QUOTE 28.2 % .**
> That number computes verified defs as `mirror defs − markers`, which treats *absence of a
> `\trusted` marker* as *evidence of proof*. It is not. Recomputed from PROOF VERDICTS
> (`rc=0` + zero non-Valid goals, proof must postdate the last change to the mirror file and
> to its live counterpart):
>
> ```
> $ bin/verified-fraction.py --staleness=file
>   (1) verified / live        499 / 3225 = 15.47 %
>   (2) unproven-perimeter     644 defs in 27 of 53 mirror files
>   (3) unmirrored ratchets    MAX_UNMIRRORED_DEFS=549  MAX_UNMIRRORED_FILES=41
>       OLDEST PROOF RELIED ON 2026-09-02
> ```
>
> Only **26 of 53** mirror files have a fresh passing whole-file proof on record; 18 have no
> proof at all, 7 have a stale one, 2 have a FAILING one. Under the stricter rule — a proof
> is stale if ANY commit to `src/pycsl` postdates it, which is defensible because the emitter
> is one program — the answer is **0 / 3225 = 0.00 %**. Both are printed; see
> `bin/verified-fraction.py --staleness=strict`. The corrected fraction is roughly **HALF**
> the figure below, and the gap IS the unproven perimeter.

This is the number Metric A is trying to be. It has a
denominator, so it can say "nearly done"; it counts the 41 unmirrored files and ~550
unmirrored defs that the 459 figure cannot see (the `check-mirror-coverage.py` header calls
itself "the plane the metric structurally cannot see", and it is right); and it makes the
"correct direction" rises legible — spending a marker to turn 1521 Valid + 24 non-Valid into
1509 Valid + 0 non-Valid *lowers* this fraction by one def and *raises* rc=0 file count by one,
and both should be reported side by side rather than the marker count alone.

**Compute.** Three greps in the table above, or extend `bin/count-trusted-directives.py` to
print `verified/live` (it already walks the mirror AST; add a walk of `src/pycsl`). Report
the pair `(verified defs, live defs)` so growth of the live tree is visible separately.

**Converging.** Rises. The theoretical ceiling is below 100 % (the backlog's `[CORRECTNESS]`
boundaries — `_err`'s raise, the char-lexer, `_try` higher-order backtracking — are recorded
as never convertible); the honest target is "100 % minus the tagged [CORRECTNESS] set", which
§3.8 makes countable.

**Falsified by.** The fraction rising because live defs were *deleted* or moved to an
unmirrored file. Pin it with the existing `MAX_UNMIRRORED_DEFS`/`MAX_UNMIRRORED_FILES`
ratchets (549/41) — they must not rise while the fraction rises.

**Cannot see.** Quality of what is assumed (a `\trusted` stub with a dishonest frame or raise
counts the same as an honest one — §3.6); whether a "verified" body's contract is *meaningful*
(the vacuity planes cover part of this); and LOC-weighting — I did not measure LOC per def
because docstrings and contracts make the two trees incomparable without an AST pass.

**Cost.** Cheap: ~30 lines in `count-trusted-directives.py`.

### 3.6 Assumption-honesty deficit — the cheapest way back onto the reducing-trusted track

**Measures.** How much each remaining assumption *claims beyond what a reviewer certified*.
Today: silent raises **70** (of 459 stubs whose live body has a direct `raise` and whose
stub declares no `#@ raises`; `MAX_SILENT = 70`), frame offenders 0, stale markers 0,
unattached 0. A `\trusted` val with no `raises` clause tells Why3 the call cannot raise; that
is a stronger assumption than "the reviewer trusts this body", and it is exactly the shape gen
#16 hit twice in one day (the ratchet went 71 > 70, and was repaired the right way — by
declaring, not by moving the bound).

**Compute.** `python3 bin/check-trusted-raises-honesty.py --verbose` (fast set, ~50 s, no
prover). Sum with `check-trusted-frame-honesty` RATCHET and the `stale`/`unattached` lines of
`count-trusted-directives.py --emit-dir`.

**Converging.** 70 → 0, by adding `#@ raises <E> when <cond>` to each stub (the in-tree idiom
`ir_schema.py:171`), lowering `MAX_SILENT` as you go, and re-proving the mirrors whose
emission moves — gen #16 measured that a `raises` on a val that is declared but never called
in-file adds no VC, so many of the 70 are cheap. **This reduces the amount that is trusted
without reducing the count that is trusted**, and it is the only such move available without a
capability build.

**Falsified by.** Declaring `raises E when True` on a stub whose live body raises only on a
path the `requires` excludes — the plane's own header admits it over-counts those. Each
declaration should be `when <the real condition>` where the condition is expressible, and
the over-count noted otherwise.

**Cannot see.** Raises through a callee (the plane counts direct `raise` only — stated in its
header); assumptions in `ensures` that are simply false (that is what the route hunt is for).

**Cost.** Zero instrumentation. Roughly 70 one-line mirror edits plus whole-file re-proofs of
the touched mirrors (which is prover time: the `statements.py` mirror alone took 88 min on
09-13 — one at a time, never alongside the suite).

### 3.7 Free-conversion count — the resume trigger for (b)

**Measures.** Stubs whose verbatim port type-checks and emits as a real definition with no
facade marker: `bin/probe-conversion-candidates.py` CLEAN count. Last measured **1 of 446**
(2026-09-02), and that one was already refuted on the vacuity plane. This is the number that
says "marker reduction can resume": when it becomes > 0 after a capability lands, the ladder
has work again.

**Compute.** `bin/probe-conversion-candidates.py <mirror.py>` per mirror file; it ports,
emits, classifies and restores. **Heavy** — it emits every candidate — so run it once per
capability landing, not per generation, and never on a loaded box.

**Converging.** Not a convergence metric; a *trigger*. Plot it against capabilities built:
markers-unlocked-per-capability is the yield of the (b) track, and the backlog already
carries the numerator in prose ("reachable subset = 1 of 19", "converts ZERO standalone").

**Falsified by.** CLEAN candidates that fail the real battery (proof, byte-diff, fidelity) —
the script's own caveat. CLEAN is a candidate filter.

**Cannot see.** Stubs not in the canonical bodyless shape (`NO-TRUSTED-STUB`, reported as
coverage loss); loop invariants/variants the port will need.

**Cost.** Exists. Prover/emission time only.

### 3.8 Marker reason taxonomy — makes Metric A decomposable (cheap, do it this week)

**Measures.** Why each of the 459 markers is there. Today every marker is the identical
string; the backlog's `[CORRECTNESS]` / `[COST/SCALE]` tags live in prose paragraphs, and the
"spent for rc=0" markers (e.g. the untyped-walk stub in `core_ir_semantic`) are
indistinguishable from a never-attempted stub. So the 451 → 459 rise cannot be read from the
count, and neither can the ceiling of §3.5.

**Compute.** Add a second token to the directive — e.g. `#@ \trusted reviewer: … reason:
untyped-walk` / `reason: cost-scale:string-setops` / `reason: correctness:noreturn` /
`reason: spent-rc0` / `reason: unclassified` — and have `count-trusted-directives.py` print the
histogram. Check with `bin/doc-coherency.py --check` and `bin/audit-pycsl-language.sh` that
adding a token to the directive is byte-inert for emission (it should be: the marker is a
comment to Module 2), and gate the edit on the mirror emission-diff as any mirror edit is.

**Converging.** `unclassified` → 0; `spent-rc0` and `cost-scale:*` buckets each map to a
named capability in the backlog; the remaining ceiling of §3.5 is then a number, not an
essay. Markers-unlocked-per-capability (§3.7) becomes computable by bucket.

**Cannot see.** Whether the classification is true — a `correctness` tag is a claim; the
campaign's record ("V1-floor REFUTED", "ten refuted boundaries") says such claims are wrong
often. Re-probe a random 10 % per quarter with §3.7.

**Cost.** One pass over 459 lines (mechanical for the ones the backlog already names), plus
the emission-diff gate. No prover time if byte-inert.

---

## 4. Metrics I would NOT make primary, and why (one line each)

* **Raw route count / routes per day.** Only goes up; tracks probes run, not defects left
  (09-11: 21, because a new generator opened a vein). Useful only as the numerator of §3.1.
* **Open-ledger size.** Sits at 0–2 because closure takes < 1 day; the handoff itself says an
  empty ledger is a prompt, not a floor.
* **"N/N planes green".** A ratchet battery says nothing regressed since the last baseline; it
  has never found a route. Also the population was mis-stated as 34 for two generations —
  count the `ok` lines, as gen #15 did.
* **`\trusted` marker count (Metric A) on its own.** No denominator; blind to 41 unmirrored
  files; rises for correct reasons; carries no reason tag. Keep it as a column, demote it.
* **Refusal-site count (222) or refusal-code count (61).** Accumulates by construction; a
  refusal is the *instrument*, so counting it measures activity.
* **Expected-PASS share of the corpus (66.8 %).** Instrument-dominated: 187 of the 401
  expected-FAIL files are route witnesses. The capability-cost number you actually want is
  *pre-existing corpus files flipped PASS → FAIL by a repair*, which the commit log records
  per route ("cost exactly one corpus file": #84 → 0065, #90 → 1057) but no plane totals.
  Cheap to total from `git log --grep='cost exactly'`; I count two such flips in the campaign.
* **Suite failure baseline (18).** A completeness backlog, moved 19 → 18 once on 09-12; too
  coarse and too slow to steer by, and it is a count, not a rate.
* **Corpus size (1208).** Up and to the right forever.
* **Differential-corpus size (56 / 45).** Growing it is good practice but the number itself is
  not a signal; the *yield* of a generated version is (§3.4).

---

## 5. Blind-spot summary — say it before the metric is trusted

| metric | cannot see |
|---|---|
| 3.1 probe yield | defects no generator reaches; "ideas ran out" vs "defects ran out" |
| 3.2 second-order share | second-order routes not recognised as such; ambiguous when rising |
| 3.3 capture–recapture | shared *method* bias; uninformative when the blind sample finds 0 |
| 3.4 generated sampler | constructs outside the template set; unsound advice text; rich `requires` |
| 3.5 verified fraction | quality of assumptions; contract meaningfulness; LOC weight (unmeasured) |
| 3.6 honesty deficit | raises via callees; false `ensures` on trusted stubs |
| 3.7 free conversions | needs a battery after CLEAN; non-canonical stubs uncounted |
| 3.8 reason taxonomy | a tag is a claim, and this repo's boundary claims get refuted |

Every metric above is stated with its blind spot for the reason the task gave: #42's
whitelist, w66's compensator, and #96's "stays visible" residue were each a control whose
blind spot was not written next to the number it produced.

---

## 6. What I would do this week, in order, with cost

1. **Start the probe ledger (§3.1/3.2)** — add `probes.tsv` and one rule line to the driver
   skill ("every probe appends a row, LIVE or not"). Back-fill the last three generations from
   the handoff. ~1 h, no prover time. From gen #17 on, report *yield per generator* in the
   START HERE block instead of "N routes found".
2. **Extend `count-trusted-directives.py` to print `verified/live` and the marker-reason
   histogram (§3.5, §3.8).** ~2 h. Tag the markers the backlog already names; leave the rest
   `unclassified` and let that bucket be the number that must go to zero.
3. **Declare the 70 silent raises (§3.6)**, batch by mirror file, lowering `MAX_SILENT` each
   batch, one mirror re-proof at a time. This is the concrete "back on the reducing-trusted
   track" move; it needs no capability and it is already gated.
4. **Schedule one blind recapture window (§3.3)** at the next quiet point on the box — 40
   probes, ledger withheld. Its m/n₂ is the first number this campaign will have that speaks
   to how many routes remain rather than how many were found.
5. **Then** the generated differential sampler (§3.4), 1–2 days, as the standing instrument
   that replaces the blind agent for routine measurement.
6. For (b): pick the one named reopening capability with the largest `cost-scale:*` bucket
   from step 2, build it with its own both-direction witnesses and differential drivers, and
   re-run §3.7 once. That — not any state of the hunt — is what makes the marker count move
   again.
