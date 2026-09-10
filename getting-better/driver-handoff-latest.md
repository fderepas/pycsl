# ============ START HERE — gen #4 FINAL HEADLINE: ROUTE #59 =========================
#
# ## THE LEDGER IS NO LONGER EMPTY. ONE OPEN ROUTE, AND ITS REPAIR IS BUILT AND STAGED.
#
#   **ROUTE #59 — a dict assignment is a VALUE COPY, so aliased mutation vanishes.**
#
#       a: Dict[int,int] = {1: 1};  b = a;  b[1] = 2;  return a[1]
#       `\result == 1` **PROVES**.  CPython answers **2**.
#
#   `b = a` lowers to `let b = ref !a` — a fresh ref over a COPY of a pure Why3 map.
#   BOTH DIRECTIONS MEASURED (the true twin FAILS), so it is a route, not a gap.
#   Unsound in the SILENT direction — the FALSE claim proves — which is why no gate
#   went red and why it survived this long.
#
#   **THE LIST CARRIER OF THE IDENTICAL PROGRAM IS CORRECT.** Lists alias through a
#   shared mutable `array`; dicts copy a pure `map`. The list result alone would have
#   been a FALSE REASSURANCE — that asymmetry is the whole reason to probe carriers.
#
#   CARRIER CENSUS, ALL BOTH-WAYS — **SIX BROKEN, and the staged patch covers FOUR**:
#     covered      local->local · SYMMETRIC (mutate either, read the other) · CHAINED
#                  `a->b->c` · FIELD-INTO-LOCAL `b = self.d`
#     NOT covered  GETTER RETURN `m = self.get()` (RHS is a Call)
#                  FIELD STORE   `self.d = p` then mutate `p` (TARGET is a field)
#     SAFE         a callee mutating a dict PARAMETER (undecided; the List equivalent
#                  there is fully faithful) · the whole `set` carrier, BY A TYPE ACCIDENT
#
#   **AND #59 IS RULE R1/R3 OF A DISCIPLINE THIS PROJECT ALREADY WROTE DOWN.**
#   `docs/pycsl-ownership-discipline.md` declares shared mutable aliasing (R1) and
#   mutate-through-alias of a stored object (R3) REJECTED / out of scope. Its sibling R2
#   (mutable default arguments) is **ENFORCED** — the emitter raises a PIPELINE ERROR
#   naming "ownership discipline R2" and there is a corpus witness. R1 and R3 are
#   documented and NOT enforced, so the tool answers inside them. That also QUALIFIES the
#   doc's claim that the snapshot semantics "never proves a false postcondition": true
#   only while the boundary is ENFORCED. **So the repair is not a new restriction — it
#   does for R1/R3 exactly what the emitter already does for R2**, which is a far easier
#   thing to justify landing.
#
#   **THE REPAIR IS BUILT, FULLY MEASURED AND STAGED: `getting-better/staged-route59/`.**
#   It refuses a MUTATED alias only; a read-only rebind stays legal, because without a
#   store an alias and a copy are indistinguishable. Corpus byte-diff ZERO, mirror moves
#   exactly 2 files, battery 1/18 RED (the pre-existing one), all 53 mirrors type-clean,
#   metric unchanged. **IT OWES TWO MIRROR RE-PROOFS** — `statements.py` and its caller
#   `Module6_WhyMLTranspiler.py`. Sequence and full measurements in that directory's
#   README.
#
#   **BUT THE REPAIR IS PARTIAL — LANDING IT DOES NOT CLOSE THE ROUTE.** Probing my own
#   repair for the gap it leaves (the #58 discipline) found a carrier it misses:
#
#       def get(self) -> Dict[int,int]: return self.d     # a getter handing out the
#       m = self.get();  m[1] = 2;  return self.d[1]      # INTERNAL dict. CPython: 2
#
#   `\result == 1` PROVES. The guard keys on the RHS being a bare name or field read;
#   here it is a **Call**, so nothing fires — the same copy-on-bind ONE SYNTACTIC STEP
#   AWAY, exactly #58 relative to #53. Emission: `let m = ref (self_get_0 ())`.
#   **Handing out an internal collection from a getter is one of the most common patterns
#   in real Python, so this carrier is arguably MORE reachable than the one the repair was
#   built for.** Land the patch for the reduction it gives; do NOT mark #59 closed.
#   The extension is scoped in the route file (key on "kind == dict AND the RHS is not a
#   FRESH construction"), and it must be measured against the MIRROR — the corpus will
#   stay clean while the mirror decides.
#
#   **THE GENERALISATION IS ALREADY COSTED, AND IT IS FREE.** Both uncovered carriers are
#   ZERO on the two gated populations: a Call RHS bound then mutated is 0 live / 0 mirror
#   / 0 corpus; a field-target store whose local is mutated AFTER it is 0 mirror / 0 corpus
#   / 1 live (`_prescan_pyval_locals`, which has no mirror counterpart). **So building the
#   full six-carrier repair should cost no more than the partial one already did** — the
#   best available next increment, and it would CLOSE the route.
#   **GATE IT ON MUTATION-AFTER-STORE ORDERING, not co-occurrence.** My first costing scan
#   ignored statement order and flagged a VERIFIED mirror method
#   (`_refine_tuple_return_type`) as exercising the route; its `_st = dict(symtab)` is a
#   FRESH dict mutated BEFORE the store. An order-insensitive scan over-reports, and it
#   over-reported in the most alarming direction possible.
#
# ## THE FOUR THINGS THAT BUILD TAUGHT, AND THEY GENERALISE
#
#   1. **A BYTE-INERT CORPUS IS NOT EVIDENCE OF SAFETY.** My first cut refused every dict
#      rebind. Corpus byte-diff CLEAN; the MIRROR died on a read-only
#      `rmap = self._module_method_return_types` in `types.py`. Route #57's
#      second-population lesson, arriving exactly on schedule.
#   2. **DO NOT ADD A LIVE-ONLY HELPER.** It moved `check-mirror-coverage` 550 -> 552
#      within minutes. The handoff already warned about this from route #58's first
#      build AND IT STILL CAUGHT ME. Inline the logic; add no `def`.
#   3. **DO NOT CHANGE A LIVE SIGNATURE whose mirror stub is `\trusted`** —
#      `check-mirror-signature-drift` 0 -> 1. Move the code to a method that already has
#      what it needs.
#   4. **A `\trusted` STUB WITH NO `#@ raises` ASSERTS ITS LIVE COUNTERPART CANNOT RAISE.**
#      Adding a `raise` broke `check-trusted-raises-honesty` (70 -> 71 silent). The fix is
#      to DECLARE `#@ raises`, not to find a quieter place for the raise.
#
# ## HOW THE ROUTE WAS FOUND — A GENERATOR THAT WORKS, USE IT AGAIN
#
#   Probe a REFERENCE-SEMANTICS construct at every CARRIER, in BOTH directions. Lists
#   came back faithful; dicts did not. The same sweep also mapped, with no finding:
#   signed `//` and `%` faithful in ALL FOUR sign quadrants (the highest-yield route
#   location in any Python verifier — Python floors, C/SMT truncate); string `len`/`==`
#   modelled while ordering/concat/indexing are opaque both ways; and route #54's
#   duplicate-key collapse genuinely modelled at `str` and `int` keys.
#   **AND THE STRUCTURAL RESULT THAT SHOULD AIM THE NEXT GENERATION.** The Hoare-logic core
#   was probed and it HOLDS, each in both directions: frame enforcement (a write outside
#   `assigns` FAILS, the correct frame PROVES), `\old` (captures the PRE-state),
#   CLASS INVARIANTS (ASSUMED at entry — confirmed by a postcondition unprovable without
#   it — and CHECKED at exit), PRECONDITION DISCHARGE at the call site, and POSTCONDITION
#   FLOW to the caller. Also: NO integer wraparound, string keys genuinely distinct,
#   signed `//`/`%` faithful in all four quadrants.
#   **So every route this campaign has ever found lives in the VALUE MODEL, not the logic**
#   — #44/#50/#51/#56/#57 are `None`/sentinels, #53/#58 are floats-as-exact-reals, #54 is
#   dict-literal key collapse, #59 is reference-vs-value semantics. **PROBE
#   REPRESENTATIONS, NOT THE PROOF ENGINE.** The engine has been measured.
#
#   Set aliasing is probed (fails closed, by a type accident). Still unprobed and worth it:
#   nested dict/list containers, tuple identity, and `del d[k]` / `.pop()` as alias
#   mutations.
#
#
# ## THE LANDING PLAN FOR THE NEXT RELAUNCH — BOTH STAGED PATCHES, MEASURED TO COMPOSE
#
#   Verified at HEAD: **each patch applies cleanly, and they apply TOGETHER with no
#   overlap.** They touch disjoint files:
#
#     staged-L1        mirror expressions.py, mirror stmt_control_flow.py
#     staged-route59   LIVE statements.py, mirror statements.py
#
#   **COMBINED THEY OWE EXACTLY FOUR WHOLE-FILE MIRROR RE-PROOFS** — expressions.py,
#   stmt_control_flow.py, statements.py, and Module6_WhyMLTranspiler.py (the caller whose
#   VCs move once `_handle_assign_stmt` declares it can raise). **Four is precisely this
#   box's measured ceiling**, so land both, launch all four, and start NOTHING else —
#   no suite, no `--slow` battery, no plane emission — until they report. Gen #3 lost work
#   to exactly that over-subscription.
#
#   Expected after landing both: fidelity **0 divergences over 887**, all 18 planes GREEN
#   for the first time in this campaign, metric **457 -> 458**. Route #59 goes from OPEN to
#   PARTIALLY REPAIRED (alias carriers closed; the GETTER-RETURN and FIELD-STORE carriers
#   still open).
#
#   **THE WITNESSES ARE STAGED TOO — `getting-better/staged-route59/witnesses/`, ids
#   1125-1131 — AND THEY LAND *AFTER* THE REPAIR, NEVER BEFORE.** Six are expected-FAIL
#   negatives that PROVE at HEAD (verified), and `run-reference-tests.sh` treats an
#   expected-FAIL driver that starts proving as a finding, so copying them in now turns the
#   suite red for a defect the route file already records. If only the PARTIAL patch lands,
#   land 1125-1128 and 1131 and HOLD 1129/1130 for the generalisation.
#   **1131 is the LIST positive control and it is the one that makes the set honest**:
#   without it, a repair could satisfy all six negatives by refusing every collection
#   binding, and nothing would notice that lists — correct today — had been broken to get
#   there. Verified at HEAD: 1125 proves (the route), 1131 proves (the control).
#
#   **CHECK LIVENESS BY CPU, NOT BY LOG MTIME.** `w51g2_expressions` went four hours
#   without writing a log line and finished rc=0; killing it as hung would have thrown
#   away six hours. `ps -eo etime,time,pcpu,rss` on the `why3` children is the real signal.
# ===================================================================================
#
#
# ===================== AMENDMENT — gen #4, later in the same session ================
#
# The block below is still accurate; this records what landed AFTER it was written.
# TWENTY-NINE COMMITS TOTAL. Metric UNMOVED all generation at markers 457 · grep 482 ·
# offset 25 · unattached 0 — correct, because every increment was an oracle repair, a
# fidelity re-sync or a boundary record, and none of those add or remove trust surface.
#
# ## THE BATTERY NOW RUNS ALL THIRTY PLANES IN ONE COMMAND, AND IT IS GREEN BUT ONE
#
#   `bash bin/run-soundness-planes.sh --slow` — 18 fast + 12 prover/emission planes off
#   ONE shared mirror emission. **29 green, 1 RED**, and the RED is mirror-sync at the 2
#   divergences the staged L1 patch repairs. Log: `getting-better/proofs49/
#   w52b_slow_planes_run1.log`. First time `check-avatar-frame-parity` has EVER been
#   collected by the loop (it REQUIRES an --emit-dir), and first time
#   `count-trusted-directives`' stale-marker half has run (stale 0 over 53 matched).
#
#   **THE WIRING NEARLY SHIPPED A BUG AND THAT IS THE FINDING.** Two file-naming
#   conventions exist: five consumers use `replace(os.sep, "_")`, `count-trusted-directives`
#   used `replace("/", "__")`. Feeding the wrong one is SILENT IN BOTH DIRECTIONS —
#   measured: yield-erasure reports 0 generators against a true 3 (FALSE GREEN),
#   computed-rhs 0 against 1 (FALSE GREEN), frame-honesty "RATCHET BROKEN — 48 > 0"
#   (FALSE RED). Fixed both ways and gated: bare-vs-shared now byte-identical for every
#   plane runnable both ways.
#
# ## THE GUARD SWEEP IS COMPLETE — EVERY PLANE TOUCHED NOW FLOORS ITS *INPUT*
#
#   Ratchets bound OUTPUT (upper bounds), so an EMPTY run satisfies them all. Fixed, each
#   with the refusal DEMONSTRATED firing at rc=2 and normal output byte-identical:
#     * five planes SELF-BASELINED and returned 0 when their baseline file was missing —
#       three of them in the per-run battery. Pre-fix, a hidden baseline printed
#       "[+] baseline written" and rc=0.
#     * `check-dropped-mutation` (IN the battery) scanned 0 statements, printed OK, AND
#       advised "lower the constant" — inviting a ratchet to be tightened on nothing.
#     * `count-trusted-directives`, which owns the headline number, printed OK with
#       `markers 0`. Its stale half printed "stale: 0" from an EMPTY directory.
#     * `check-getattr-erasure` (found RED at HEAD in window #51) and
#       `check-bespoke-model-drift` (whose `gone` list never set a return code) both
#       passed on an empty population.
#     * `check-internal-crash-free` counted a TIMEOUT as a clean run — both returned None.
#       Now listed, counted and refused. Measured: 0 of 1051 today.
#     * `check-avatar-frame-parity` floored at MIN_AVATARS_SCANNED = 1 against a TRUE 83.
#       Raised to 60; a truncated 5-mirror emission now REFUSES where it used to PASS.
#   **GUARDS ARE ON THE POPULATION, NEVER ON THE METRIC** — a floor on the marker count
#   would fight the campaign's own direction, and that is written into the comments so a
#   later window does not "helpfully" convert them into ratchets.
#
#   Also: `check-ir-field-coverage` decided "is this field READ?" by regex over handler
#   source INCLUDING COMMENTS (measured: 0 fields affected today, closed anyway), and
#   printed "25 class(es) with NO identifiable handler" while ignoring it — a QUARTER of
#   the IR schema unaudited and able to grow silently, since handler matching is BY NAME.
#   `unmatched` is now baselined at 25 and ratcheted; a class newly losing its handler
#   fails and is named.
#
# ## TWO CERTIFIED BOUNDARIES, BOTH FROM THE CAMPAIGN'S OWN ROUTE GENERATORS
#
#   * **Route #57's non-scalar codomains** (`seq`/`map`/`hval`/`emit_ir`), which #57 left
#     explicitly UNMEASURED. All fail closed — but the CONTROL moves the boundary off
#     `.get` entirely: a plain SUBSCRIPT on `Dict[K, List[int]]` fails identically, so a
#     dict with a non-scalar VALUE type is not readable from corpus Python at all.
#   * **There is no THIRD float path.** #53 guards both-float, #58 folds both-int, so what
#     covers MIXED? Nothing needs to: `1.0 / 3`, `1 / 3.0` and even `1.0 + 2` do not
#     type-check, while both-float and both-int controls reach the prover and fail closed.
#   * **Route #56's carrier census is complete**: LOCAL was the route; PARAM fails closed
#     on a type accident (`_union_f_0`); FIELD is COVERED BY #56's OWN REPAIR — the
#     emission reads `if (self.v = pycsl_none)` against an UNINTERPRETED symbol.
#   All three are FRAGILE — Why3 type accidents, not guards — and each carries a
#   mechanically checkable reopening capability in its route file.
#
# ## THE TWO LESSONS THAT COST THE MOST
#
#   1. **THE OBVIOUS FIX FOR A LOOSE MATCH IS OFTEN LOAD-BEARING.** Anchoring
#      `check-untrusted-emitted`'s regex with a plain `\b` — exactly what the analysis said
#      — produced **668 phantom NOT-EMITTED lines**, because the wildcard carries the CLASS
#      MANGLING. Measure the repair, not only the defect.
#   0. **AN EMISSION FAILURE IS NOT A SEMANTIC RESULT.** This bit three times in one
#      window: `--memory-model typed/store` dying on `unbound type symbol 'option'` (they
#      cannot emit ANY dict), a `Tuple[int,int]` LOCAL ANNOTATION dying (unsupported
#      annotation, nothing to do with tuples), and the `set` alias carrier dying (the shape
#      does not lower). Each reads exactly like "fails closed" and none of them is a
#      statement about semantics. **A probe that dies BEFORE the prover must be re-run in a
#      second spelling before its failure counts** — and where it still dies, record it as
#      a TYPE ACCIDENT with a reopening capability, never as a guard.
#   2. **A PROVER TIMEOUT ON A NEGATIVE WITNESS CAN BE THE REPAIR WORKING — READ THE
#      EMISSION.** Route #56's field probe timed out at 22s; trying to prove harder hit a
#      900-second wall with NO verdict, and reading the emitted `.mlw` settled it in
#      seconds. The solver was thrashing precisely BECAUSE the answer is an opaque.
#      A timeout is never to be filed as "fails closed".
#
# ## IN FLIGHT
#
#   `w51g2_expressions`  the last route-#57 mover, live since 08:21.
#   `w52c_statements`    **the OWED post-sync re-proof**, launched 13:1x. `w51g_statements`
#                        rc=0 was collected but proved the PRE-SYNC body (it emitted at
#                        08:00; the re-sync landed ~11:20), so it does NOT discharge that
#                        debt — this run does.
#   `suite49_run8`       still going. Baseline 19 confirmed failures, run 6 was 3232/3251.
#                        **A NEW NAME is a regression; the count alone is not.**
#
# ## STILL OWED
#
#   * `expressions.py` whole-file re-proof (the `#@ sibling_concrete` marker moved it; the
#     live w51g2 run predates the marker and will NOT cover it).
#   * `statements.py` — w52c is running now.
#   * the staged L1 patch, and then ITS re-proofs of expressions + stmt_control_flow.
#
# ## VERIFIED-BUT-UNFIXED, FOR THE NEXT RELAUNCH — RE-VERIFY EACH BEFORE ACTING
#
#   * `doc-coherency.py:191` — `_DISTINCTIVE` counts a directive as documented on a bare
#     word-boundary match, and contains ordinary English (`proof`, `shared`, `critical`,
#     `variant`, `trusted`, `requires`, `ensures`). Effectively vacuous for those.
#     **Left alone deliberately: the reference suite invokes it and a run was live.**
#   * `check-param-mutator-visibility.py:141` — verdict by grepping pycsl STDOUT; the
#     `ERROR:` test runs BEFORE the DROPPED test, and DROPPED is the unsound bucket.
#   * `check-ir-field-coverage.py:72` — `TOO_GENERIC` exempts `value`/`body`/`target` BY
#     NAME, i.e. the payload-carrying fields (41 field-instances skipped).
#   * `check-constant-fallthrough.py:140` — baseline keyed on BARE FUNCTION NAME, no file,
#     no line; and its DECIDING/INERT sets miss literals like `"2"`, `"(-1)"`, `PNone`.
#   * `check-collapsed-option-reads.py:117` — key is `(filename, literal)`, so once a pair
#     is classified every later occurrence in that file is accepted unbounded.
#   * `check-refusal-reachability.py:69` — scope keyed on the `PyCSL` NAME PREFIX, and it
#     walks only `ast.FunctionDef` (no async, no module-level raise).
#   * `check-swallowed-exceptions.py:116` — ANY `raise` anywhere in the handler subtree
#     exonerates it, including inside a nested `def`.
#   * `check-mirror-coverage.py:63` — flat name sets per file, so class structure is
#     discarded and `ast.AsyncFunctionDef` is never collected.
#   * `check-shadowed-selfcalls.py:166` — `hit[0]` off a SET, so with two same-named
#     definitions in one `.mlw` the reported `concrete` count is nondeterministic.
#   * NO population guard yet: `check-refusal-reachability`, `check-mirror-field-parity`,
#     `check-mirror-signature-drift`, `check-untrusted-emitted`, `check-trusted-frame-honesty`.
#
# ===================================================================================
#
#
# ===================== START HERE — #49 (gen #4, 2026-09-10) =========================
#
# ## THE HEADLINE: THE ONE RED PLANE IS BROKEN, AND THE ORACLES THEMSELVES WERE THE VEIN
#
#   `check-shadowed-selfcalls` **15 -> 14** (bypassing sites 120 -> 119), **WITHOUT
#   re-baselining**. Gen #3's return-position lead was the wrong axis and its ordering
#   hypothesis was already refuted; the actual difference was that all four
#   demonstrably-working siblings in the same file carry `#@ sibling_concrete` and
#   `_dv_missing_default` did not. One marker. The abstract avatar
#   `val self__dv_missing_default_1` is no longer declared at all and the call is now
#   `raise (Return_str (expressionemissionmixin___dv_missing_default self nu))`.
#
#   That fix then opened the real vein. **EIGHT ORACLE DEFECTS FOUND AND FIXED**, in the
#   planes the whole campaign's trust rests on. The defect class, in one sentence:
#   **an oracle whose classification is keyed on text the audited artifact controls,
#   where a false positive silently REDUCES what the oracle examines.**
#
# ## WHAT LANDED — THIRTEEN COMMITS
#
#   1. `b4e9c762` shadowed-selfcalls 15 -> 14 (above). OWES an expressions re-proof.
#   2. `bc6691b0` **THE FIDELITY ORACLE COULD BE SWITCHED OFF BY A COMMENT.**
#      `_trusted_above` tested for the TEXT `\trusted` anywhere above a `def`, and
#      justification comments NAME the marker constantly. 46 functions were being skipped
#      with no `#@ \trusted` directive. **ONE WAS REALLY DIVERGENT.**
#   3. `0d05e62e` the same hole in THREE more planes — `self-annotate-mirror-check.sh`
#      (the SECOND fidelity script), `check-yield-erasure.py` (both lost-coverage
#      polarity) and `check-trusted-raises-honesty.py` (over-count). Deltas all null and
#      reported as null.
#   4. `f08bd325` **THE DIVERGENCE ITSELF.** `_wrap_body_with_return_catch` carried 8 of
#      the live emitter's 13 statements — FIVE dispatch arms missing (`option (...)`
#      opttuple, `pyconst_val` tuple, `emit_ir`, `term`, `_union_*`), all falling through
#      to the generic `Return r -> r`. Re-synced verbatim. Fidelity 3 -> 2 over 886.
#   5. `0f47f946` the walkers could not see a `def` nested in a `try:`/`if:`/`with:`.
#      Found by cross-checking the planes' trusted count (455) against the authoritative
#      marker count (457). They now agree at 457.
#   6. `9456111e` the re-synced honest body **PROVES** (targeted `--fun`, rc=0). That
#      also REFUTES the old note claiming f-string literal segments made it unverifiable.
#   7. `1b483029` the ten prover/emission planes wired into the collector behind
#      `--slow`, with MIN_PLANES scaling. Default path byte-identical.
#   8. `6c3b0efa` **TWO GATES DISAGREED ABOUT THE SAME MARKER.**
#      `run-reference-tests.sh` greps `^# pycsl-expected: FAIL` (anchored);
#      `check-vacuous-drivers.py` used `in src` (unanchored). 13 pycsl-reference drivers
#      name their TWIN's marker in a docstring, so they were REQUIRED TO PROVE and
#      simultaneously EXEMPT from the vacuity census. Census 894 -> 936, nothing new found.
#   9. `8f34b05a` **FIVE RATCHETS SELF-BASELINED AND RETURNED 0** when their baseline
#      file was missing; THREE are in the per-run battery. Demonstrated both ways: pre-fix
#      a hidden baseline gave rc=0 "[+] baseline written", post-fix rc=2 REFUSING.
#  10. `9f2ec980` `check-untrusted-emitted.classify()` was a SUFFIX match
#      (`classify("foo","let barfoo...")=="LET"`) and matched WhyML keywords;
#      `check-avatar-frame-parity` read `#@ assigns` as a substring.
#  11. `3359d9b6` COLLECTED `w51g_scf` rc=0.
#
# ## THE LESSON THAT COST THE MOST, AND MUST BE CARRIED
#
#   **THE OBVIOUS FIX FOR A LOOSE MATCH IS OFTEN LOAD-BEARING.** Anchoring
#   `check-untrusted-emitted`'s regex with a plain `\b` — exactly what the analysis said
#   to do — took the plane from "0 unexpectedly absent" to **668 phantom NOT EMITTED
#   lines**, because the wildcard carries the CLASS MANGLING (`_ContractParser.cur` ->
#   `let _contractparser__cur`). The right repair allows the prefix only when it really
#   is a mangling (`(?:[\w']*__)?`). MEASURE THE REPAIR, NOT ONLY THE DEFECT.
#
#   Corollaries banked this generation:
#   * **A plane's own count is a testable claim.** Cross-checking the planes' trusted
#     count against `bin/count-trusted-directives.py` is what found item 5. Do it again
#     after any plane change.
#   * **Report null deltas as null.** Five of the eight holes were EMPTY today. Saying so
#     is what makes the two that were not (items 2/4 and 8) believable.
#   * **`why3 prove --type-only` on the emitted mirror is a ~10-second gate** that would
#     have caught route #57's ill-typed landing. Run it on any mirror edit before
#     spending four hours on a whole-file proof.
#   * **`--fun <MANGLED-NAME>` gives an early proof signal in minutes**, and fails closed
#     with the list of valid names if you pass the Python name. Use it before committing
#     a mirror body change; state its limit (it TRUSTS every other function).
#
# ## IN FLIGHT — DO NOT RELAUNCH, COLLECT THEM
#
#   `w51g_statements`    live since 08:00. **ITS VERDICT IS AT THE PRE-SYNC BODY**, so
#                        statements.py owes a re-proof either way (see OWED below).
#   `w51g2_expressions`  live since 08:21. Also pre-dates commit 1's marker.
#   `suite49_run8`       started 11:48 under a memory watchdog that sheds ONLY the suite.
#                        Baseline 19 confirmed failures; run 6 was 3232/3251.
#                        **A NEW NAME in the failure list is a regression; the count alone
#                        is not.**
#   MEMORY: with two movers + the suite the box sat at 6-8 GB available, comfortable.
#   Gen #3's ceiling (about four whole-file proofs and NOTHING else) still stands.
#
# ## OWED — THE HONEST DEBT LIST
#
#   * `expressions.py` whole-file re-proof (commit 1 moved it).
#   * `statements.py` whole-file re-proof (commit 4 moved it). The targeted `--fun` run
#     says the changed function proves; that is NOT the whole-file gate.
#   * The staged L1 patch still owes ITS OWN `expressions.py` + `stmt_control_flow.py`
#     re-proofs after it lands — `w51g_scf`'s rc=0 is at the pre-L1 tree.
#
# ## THE LADDER FOR THE NEXT RELAUNCH, IN ORDER
#
#   1. **COLLECT** `w51g_statements`, `w51g2_expressions`, `suite49_run8`.
#   2. **LAND `getting-better/staged-L1/l1-both-halves-var-expr-and-for-stmt.patch`.**
#      It takes fidelity to ZERO divergences and the metric 457 -> 458. Read its numbers
#      as: fidelity **2/886 -> 0/887** (gen #3 measured 2/840, before this generation's
#      oracle repairs widened the population). Apply only after the two movers report.
#   3. **RE-PROVE `expressions.py` and `statements.py`** — the debt above. Two at a time.
#   4. **RUN `bash bin/run-soundness-planes.sh --slow`** (~20 min, newly possible). It is
#      the first time the ten prover/emission planes can be collected in one command,
#      and two of them have been found RED-at-HEAD-with-nobody-looking in past windows.
#   5. **THE ORACLE VEIN IS NOT EXHAUSTED.** A read-only sweep produced a ranked candidate
#      list; eight were verified and fixed, and the following are VERIFIED-BUT-UNFIXED,
#      each with its line already confirmed by hand:
#        - `check-ir-field-coverage.py:213` decides "field is READ" by a regex over
#          handler source INCLUDING COMMENTS — a comment naming the field switches it off.
#          Also `TOO_GENERIC` (line 72) exempts `value`/`body`/`target` BY NAME, i.e. the
#          payload-carrying fields, and `unmatched` classes never affect the return code.
#        - `check-param-mutator-visibility.py:141` decides the verdict by grepping pycsl's
#          STDOUT for `ERROR:` / `Verification SUCCESS`. The `DROPPED` bucket — the whole
#          point of the plane — is the one a text change can empty.
#        - `check-internal-crash-free.py:68` treats a TIMEOUT as a clean run (returns
#          None), and detects crashes only by the literal banner `UNEXPECTED PIPELINE
#          ERROR`.
#        - `doc-coherency.py:191` counts a directive as documented on a bare word-boundary
#          match, and `_DISTINCTIVE` contains ordinary English — `proof`, `shared`,
#          `critical`, `variant`, `trusted`, `requires`, `ensures`. Effectively vacuous
#          for those. **Do not touch this one while a suite run is live** — the suite
#          invokes it.
#        - NO zero-input guard at all: `check-getattr-erasure.py`,
#          `check-bespoke-model-drift.py` (whose `gone` list never sets a return code),
#          `check-dropped-mutation.py` (**in the per-run battery**; all roots missing =>
#          every ratchet satisfied => green), `check-refusal-reachability.py`,
#          `check-mirror-field-parity.py`, `check-mirror-signature-drift.py`,
#          `count-trusted-directives.py` itself, `check-trusted-frame-honesty.py`.
#        - `check-avatar-frame-parity.py:171` sets `MIN_AVATARS_SCANNED = 1` against a
#          true population of 83.
#      **VERIFY EACH ONE YOURSELF BEFORE ACTING — one of the sweep's confident
#      recommendations was measurably wrong (see THE LESSON above).**
#   6. **ROUTES: still ZERO OPEN.** The generators are at the top of
#      `getting-better/open-routes/README.md`. Note this generation's finding suggests a
#      THIRD generator: probe the ORACLES, not only the emitter.
#
# ## STATE
#
#   HEAD `9f2ec980` (plus collection commits) · tracked tree CLEAN apart from two
#   long-standing GITLINKS (`scratchpad/w7/base`, `scratchpad/w8/pre` are registered
#   WORKTREES, not dirt) and a 0-byte stray `str` in the repo root from an earlier window.
#   `src/self-annotate` dirty 0 · stray `.bak` 0.
#   METRIC markers **457** · grep 482 · offset 25 · unattached 0 — **UNMOVED all
#   generation, which is correct**: every increment here was an ORACLE repair or a
#   fidelity re-sync, and neither adds or removes trust surface. It should rise to 458
#   when the staged L1 patch lands.
#   PLANES 17 of 18. The one RED is `check-self-annotate-mirror-sync` at **2 divergences
#   over 886** (`_handle_var_expr`, `_handle_for_stmt`) — exactly the pair the staged L1
#   patch repairs. `check-shadowed-selfcalls` is GREEN at 14 for the first time.
#   LEDGER 3. Deadline 1789288757 (Sun Sep 13 08:39:17 UTC 2026).
#
# ===================== the earlier blocks follow ============================
#
#
# ===================== START HERE — #49/#51 (gen #3 FINAL, 2026-09-10 09:00 UTC) =====
#
# ## WHAT LANDED THIS GENERATION — FIVE COMMITS OF SUBSTANCE
#
#   **ROUTE #53 CLOSED (`adf2eda5`)** — a Python `float` was the EXACT real, so
#   `0.1 + 0.2 == 0.3` PROVED. One UNINTERPRETED DETERMINISTIC symbol now serves the spec
#   path and the body path alike. Uninterpreted stops any exact-real value/sign/ordering
#   being decided; DETERMINISTIC keeps `\result == x + x` provable by congruence (1120 is
#   that control). Cost: ONE clause, 0517's `\result >= 0.0`. Witnesses 1117-1120.
#
#   **ROUTE #58 FOUND AND CLOSED (`cf35437f`)** — found ONE HOUR after #53, by probing
#   #53's own repair for the gap it leaves. int/int true division had its OWN bridge on a
#   DIFFERENT path (the float path needs BOTH operands float, so `1 / 3` never reached it)
#   and still divided over the exact reals. Closed by FOLDING two int literals as CPython
#   folds them, rendered through the SAME `repr` normalization the float-literal leaf uses.
#   **BETTER IN ALL THREE DIRECTIONS:** unsound orderings fail closed (1121, 1122), 0813
#   keeps ALL FIVE clauses, and 1123 — TRUE in Python — FAILED at HEAD and now PROVES.
#
#   **ROUTE #57's LANDING DEFECT FIXED (`b6186687`)** — `w51g_expressions` returned rc=1
#   in ONE MINUTE with a TYPE ERROR. `_dv_absent_opaque(self, nu: str)` tested
#   `nu in (None, "", "int")`; `nu` is declared `str`, so the mirror types it `string` and
#   the `None` lowers to the INT `0`, emitting `str_eq_op nu 0`. **The expressions mirror
#   was ILL-TYPED at HEAD from the moment #57 landed**, and the CORPUS COULD NOT SEE IT.
#   Fixed with the sibling's idiom (`if not nu or nu == "int"`); corpus byte-inert 919/919.
#
#   **THE ROUTE LEDGER NOW READS ZERO OPEN ROUTES (`2b933da9`).** #46, its last advertised
#   open entry, had been CLOSED SINCE 2026-09-08 by `5f57a95d` — only the ledger was
#   stale. Caught by the freshness precondition, verified dead across both halves plus
#   four variants. THREE stale entries were corrected this window (#56, #57, #46).
#
#   **THE L1 FIDELITY FIX IS STAGED, BOTH HALVES (`f43b9099`)** —
#   `getting-better/staged-L1/`. See the ladder below; it is READY, MEASURED, NOT LANDED.
#
# ## IN FLIGHT — SIX THINGS, ALL DETACHED, DO NOT RELAUNCH
#
#   `w51g_scf`          route #57 mover, from ~07:5x
#   `w51g_statements`   route #57 mover, from 08:00
#   `w51g2_expressions` from 08:21 — THE RELAUNCH after the type fix; it is long past the
#                       one-minute failure point, so the fix holds under a real run
#   `w51h_cis_trusted`  **DONE, rc=0, LANDED as item 3.**
#
#   **MEMORY IS THE BINDING CONSTRAINT AND THREE PROOFS SATURATE THIS BOX.** At 10:43 the
#   three above alone held it at 13 of 15 GB with 1 GB available — `why3` workers run
#   ~850 MB EACH. Nothing else may be started until they finish; `free -g` first. Note the
#   background tasks that got killed were the HARNESS proactively stopping MY lightweight
#   waiter shells, NOT the kernel OOM killer touching the detached proofs, so the movers
#   themselves are not what gets picked off — but do not test that.
#
#   **THE SLOW-PLANE BATTERY AND SUITE run7 WERE KILLED BY ME, NOT BY A GATE.** Running
#   them on top of the four proofs took the box to 13 of 15 GB with SWAP FULL, and the
#   kernel began killing processes. The OOM killer picks the LARGEST RSS, and those were
#   `why3` workers at ~850 MB EACH inside the four owed movers — the exact way a previous
#   window lost `w49_expressions`/`w49_statements` to rc=137. I shed the RE-RUNNABLE and
#   kept the IRREPLACEABLE. All four survived. **MEASURED CEILING FOR THIS BOX: about
#   FOUR whole-file proofs and NOTHING ELSE. Do not start a third battery class.**
#     * suite run7 — ABANDONED, no `.rc` was ever written so there is NO verdict to read;
#       its partial log is `suite51_run7.ABANDONED.log` (untracked). **RE-RUN IT** once
#       the proofs are done: it is the owed gate on routes #53/#58 and the #57 type fix.
#       The accepted baseline is 19 confirmed failures (0211-0220 "Rocq-required",
#       0700/0701 a recorded finding, seven python-reference gaps); run 6 was 3232/3251.
#       **A NEW NAME in that list is a regression — the count alone is not.**
#     * plane battery — ABANDONED after ONE result: `check-getattr-erasure` **GREEN**
#       (window #51 had found it RED, so that stale ratchet is already repaired). The
#       other nine are unrun. `$SCRATCH/planes-battery.log`.
#
#   QUEUE G SO FAR: autotrust 0, types 0, functions 0, preamble 0, expressions 1 (the type
#   error — fixed and relaunched as w51g2), scf + statements still live.
#
# ## THE LADDER FOR THE NEXT RELAUNCH, IN ORDER
#
#   0. **NOTHING MAY BE LAUNCHED UNTIL THE FOUR PROOFS FINISH.** See the memory ceiling
#      above; run `free -g` before starting anything.
#   1. **COLLECT** the four above. `w51g2_expressions` rc=0 means route #57 is fully
#      re-proved. SUITE run7 is the gate on #53/#58; the accepted baseline is 19 confirmed
#      failures (0211-0220 are "Rocq-required", 0700/0701 a recorded finding, and seven
#      python-reference gaps) — **a NEW name in that list is a regression, the count alone
#      is not.** Run 6 was 3232/3251.
#   2. **LAND `getting-better/staged-L1/l1-both-halves-var-expr-and-for-stmt.patch`.**
#      It takes the fidelity L-PLANE — RED at HEAD for a long time — to **ZERO
#      divergences**, with **ALL 18 PLANES GREEN** and the metric 456 -> **457**. It is
#      MIRROR-ONLY, so corpus-inert BY CONSTRUCTION. **Its measured numbers were taken
#      BEFORE item 3 landed, so re-read them as: fidelity 2/840 -> 0, metric 457 -> 458.**
#      It owes exactly TWO whole-file
#      re-proofs, `expressions.py` and `stmt_control_flow.py` — the two files queue G is
#      proving right now, which is the only reason it is staged rather than landed.
#      **APPLY IT ONLY AFTER `w51g2_expressions` AND `w51g_scf` HAVE RECORDED VERDICTS.**
#   3. ~~**THE `w51_cis` DISPOSITION.**~~ **DONE AND LANDED (`d036e101`).** rc=0.
#      Without the marker: 1521 Valid + **16 TIMEOUTS** + 8 unproven. With
#      `_returns_literal_none` marked `\trusted`: 1509 Valid, **0 timeouts**, 0 unproven,
#      "All contracts formally proven". A SINGLE marker cleared EIGHT goals because
#      `_check_scalar_return_annotation` CALLS it and had inherited the failure from the
#      inlined body. Frame CHECKED not assumed (the live body is pure — no `global`, no
#      attribute write — so `assigns \nothing` is honest as an ASSUMPTION). No re-proof
#      owed, measured: `core_ir_semantic.mlw` emitted at `adf2eda5` (where the rc=0 was
#      obtained) and at HEAD is BYTE-IDENTICAL at 2997 lines. **METRIC IS NOW 457.**
#
#   4. ~~**RUN THE NINE REMAINING SLOW PLANES**~~ **ALL NINE RUN. EIGHT GREEN, ONE RED.**
#      GREEN: trusted-frame-honesty (0 model-visible frame lies; ratchets 0/1 and 0/94),
#      computed-rhs-erasure, yield-erasure, untrusted-emitted (864 un-trusted, 848 emitted
#      as definitions, 0 re-abstracted), swallowed-exceptions, bespoke-model-drift,
#      internal-crash-free, param-mutator-visibility, and getattr-erasure (which window
#      #51 had found RED — that stale ratchet is already repaired).
#      **RED: `check-shadowed-selfcalls`, 15 > allowed 14.** A LOST CONVERSION, NOT an
#      unsoundness — an unconstrained abstract result over-approximates exactly as a
#      `\trusted` stub does — but the proof was paid for and no caller sees the body.
#      BISECTED: 14 (green) at `37403f79`, 15 at `11eb06a0` (that tree + a docs-only
#      commit), so it is THIS WINDOW's and NOT from gen #3's code. NAMED by diffing the
#      verbose lists: **`_dv_missing_default`, shadowed by route #57's `_dv_absent_opaque`**,
#      which ends by returning it. **MY REPAIR WAS BUILT, MEASURED AND REFUTED** — see
#      `39f00d6f`: renaming so the callee sorts first DID reorder the emission (callee
#      1248, caller 1317) and the plane STILL said 15 with a byte-identical set, so
#      ORDERING IS NOT THE CAUSE. Narrowed for the next probe: the mirror has EXACTLY ONE
#      call site (the other three live ones are inside `\trusted` methods and never reach
#      emission), concrete sibling application demonstrably works in the SAME file for
#      `field_label`/`coerce_to_int`/`array_coerce_arg`/`is_float_expr`, and the failing
#      call is in RETURN position (`raise (Return_str ...)`) — start there.
#      **DO NOT RE-BASELINE.** The fix is "make the caller see the body", never "raise the
#      allowance". Still worth WIRING the nine into the collector behind a `--slow` flag:
#      they cost ~2 min EACH, not the "minutes each ... session-scale" the exclusion
#      comment implies, so the whole set is ~20 minutes.
#
#   5. **ROUTES: ZERO OPEN.** The hunt must now GENERATE candidates. The two generators
#      that actually produced results here are written at the top of `open-routes/README.md`.
#
# ## PROBED THIS GENERATION WITH NO FINDING — DO NOT RE-PROBE (a real budget saver)
#
#   * Every OTHER path reaching float semantics after #53/#58: `*`, `-`, `/`, unary
#     negation of a computed float, the SPEC-side `*` with a literal operand, a float LIST
#     ELEMENT, a float RECORD FIELD. All fail closed.
#   * Shapes where PYTHON RAISES or is special: `5 // 0`, `5 % 0`, `[1,2][5]`,
#     `float("inf") == 0.0`, `float("inf") > 1.0`. All fail closed.
#   * `2 ** -1 == 0` (the WL-02 int-collapse shape), `a[-1]` false claim, and
#     `len({1: 5, True: 6}) == 2` (route #54's family via BOOL/INT KEY IDENTITY — Python
#     collapses that literal to `{1: 6}`). All fail closed. And the TRUE twins PROVE:
#     `a[-1] == 9`, `{True: 5}[1] == 5`, `True + True == 2`, `1 < 2 < 3` — so negative
#     indexing and bool/int key identity are genuinely MODELLED, not merely refused.
#   * ONE completeness gap, recorded as such: `"abc"[10:20] == ""` is TRUE and does not
#     prove.
#   * `bin/check-collapsed-option-reads.py` reports 9 sites, 3 classes, ZERO unprobed —
#     that generator's worklist is EXHAUSTED.
#   * A frame audit of all 758 `\trusted` stubs (does the ASSUMED `assigns` cover the LIVE
#     body's writes?) found 5 distinct hits, seven of whose omitted fields are UNMODELLED
#     and therefore benign. The one real hit, `_Unparser.write` omitting `_source`, is an
#     already-documented CERTIFIED BOUNDARY with a written reopening capability.
#
# ## LESSONS THIS GENERATION PAID FOR
#
#   * **A repair covers the PATH it edits, not the SEMANTICS it means to fix.** #58 exists
#     because #53's guard requires BOTH operands float. After closing a route, probe the
#     other paths reaching the same semantics BEFORE recording it closed.
#   * **When a route says "fails closed", check WHICH DIRECTION was measured.** #53's file
#     called the float ordering fails-closed having measured only the TRUE direction; the
#     FALSE direction PROVED. Witness 1119.
#   * **A byte-inert corpus does NOT mean a change is safe.** The mirror is a SECOND
#     population with a STRICTER type discipline, because the emitter's own code must be
#     written in the subset it models. #57 was correctly byte-inert and still ill-typed.
#   * **Before adding a live emitter helper, check whether the ENCLOSING method is already
#     `\trusted` in the mirror.** If it is, INLINE. A new live-only function moves the
#     `check-mirror-coverage` ratchet — my first #58 build did exactly that and the plane
#     went RED within minutes. The fix is NEVER to raise the ratchet.
#   * **Re-`\trusted`-ing a PARTIALLY-MODELLED verified method converts a PROVEN frame
#     into an ASSUMED one.** `_handle_for_stmt`'s `assigns` was proven of its 37% body,
#     which writes 3 `self` fields; the LIVE body writes TEN. Its frame had to be
#     re-derived from the LIVE body — otherwise the increment meant to make the file
#     honest would have introduced a FALSE ASSUMPTION.
#   * **RE-MEASURE, NEVER INHERIT.** Three ledger entries this window said OPEN and were
#     closed; one route file understated its own defect by measuring one direction only.
#   * **RUN `bash bin/run-soundness-planes.sh` AFTER EVERY LANDING.**
#
# ## STATE
#
#   HEAD `0bd47e0e` · tracked tree CLEAN apart from two long-standing GITLINKS
#   (`scratchpad/w7/base`, `scratchpad/w8/pre` are registered WORKTREES, not dirt) and a
#   0-byte stray `str` in the repo root left by an earlier window. `src/self-annotate` 0.
#   METRIC markers **457** · grep 482 · offset 25 · unattached 0 — it rose by ONE when
#   item 3 landed, and **THAT RISE IS THE CORRECT DIRECTION**: the trust surface was
#   always that big and only the bookkeeping said otherwise. It should rise to **458**
#   when item 2 (the staged L1 patch) lands, for the same reason.
#   PLANES 17 of 18; the one RED is `check-self-annotate-mirror-sync` (2 divergences over
#   **840** — 841 before item 3, because a newly-`\trusted` function correctly leaves
#   verbatim checking), PRE-EXISTING — and item 2 is the fix that takes it to 0.
#   LEDGER 3. Window deadline 1789288757 (~71h left at 09:00).
#
# ===================== the earlier blocks follow ============================
#
#
# ===================== START HERE — #51 (FINAL, 2026-09-10 07:17 UTC) ============
#
# ## WHAT TO COLLECT FIRST, AND WHERE IT LIVES
#
#   1. **QUEUE G** — `scratchpad/w49/queue51g.sh`, started 07:07, detached, concurrency
#      TWO, 8h timeouts. Route #57's SEVEN owed movers. Verdicts land in
#      `getting-better/proofs49/w51g_*.rc` and `queue49.progress`.
#      ALREADY IN: `w51g_autotrust` rc=0. Order: autotrust, types, functions, preamble,
#      scf, then **expressions and statements LAST as a pair** (each ~3-4h).
#      **IF ONE FAILS THAT IS THE HONEST COST OF ROUTE #57 AND MUST BE WORKED, NOT HIDDEN.**
#      DO NOT RELAUNCH IT — it is setsid'd and survives worker turnover.
#
#   2. **THE `w51_cis` DISPOSITION TEST** — running OUTSIDE the repo, in the worktree
#      `/tmp/claude-1000/-home-fabrice-git-pycsl/72fe2917-7b27-4e52-98dc-bfc0f750b42c/scratchpad/wt-cis`,
#      writing to `<that scratchpad>/cis_trusted.rc` and `cis_trusted.log`.
#      THE HYPOTHESIS: mark `_returns_literal_none` `\trusted` and ALL EIGHT termination
#      goals die with the nested `walk` it encloses. INTERIM at 07:17: 20+ minutes
#      elapsed, **ZERO timeouts logged**, against EIGHT in the original `w51_cis`.
#      CONSISTENT WITH the hypothesis but NOT a verdict — do not record it as one until
#      the `.rc` exists. **If it holds, land the `\trusted` marker and the metric goes
#      456 -> 457, which is the CORRECT direction**: the trust surface was always that
#      big, only the bookkeeping said otherwise.
#
# ## THE ONE PLANE STILL RED, AND IT IS THE IMPORTANT ONE
#
#   `check-self-annotate-mirror-sync` — 2 divergences over 841 verbatim-checked functions.
#   `_handle_var_expr` is FIXED AND MEASURED in `scratchpad/wt-l1b` (divergences 2 -> 1,
#   **17 of 18 planes green, NO ratchet movement**). It was deliberately NOT landed with
#   route #57: combining an EMITTER change with a MIRROR change would destroy attribution
#   if the shared `expressions.py` re-proof failed — the bisect route #42 cost. **Land it
#   AFTER queue G, with its own re-proof.**
#   `_handle_for_stmt` remains at 37 of 99 normalized statements while counted as
#   VERIFIED. Decide it: port the missing statements, or re-`\trusted` it and let the
#   metric rise. Do not leave it counted as verified.
#
# ## A LESSON THIS WINDOW PAID FOR TWICE — RUN THE COLLECTOR AFTER EVERY LANDING
#
#   `bash bin/run-soundness-planes.sh` (18 planes, ~2 min). Within MINUTES of route #57
#   landing it caught `check-mirror-coverage` RED at 551 > 550: I had added a new
#   top-level `_dv_absent_opaque` to the live emitter and not mirrored it. The previous
#   handoff had WARNED about exactly that shape and I walked into it anyway — the only
#   reason it cost minutes instead of a window is that the plane was RUN.
#   THE FIX WAS NOT TO RAISE THE RATCHET. The plane's own message is the argument:
#   "a live function with no mirror counterpart is not `\trusted`, it is ABSENT: it
#   carries no marker, so the headline count cannot see it." An unmirrored function is
#   INVISIBLE to the metric, strictly worse than a `\trusted` one. It was mirrored as a
#   VERIFIED body, at no metric cost.
#
# ## STATE
#
#   HEAD 800daa67 · tracked tree CLEAN · `src/self-annotate` dirty 0 · 0 stray `.bak`
#   under `src/` or `bin/` · 0 untracked `.mlw` under `src/self-annotate`.
#   METRIC markers 456 · grep-substring 481 · offset 25 · unattached 0 — stable across
#   three samples, UNCHANGED all window, which is the expected shape when the work is
#   routes, refusals and opaques. Window deadline 1789288757 (~73h left at 07:00).
#
# ===================== the earlier #51 blocks follow ============================
#
# ===================== START HERE — #51 (UPDATED 2026-09-10 07:08 UTC) ===========
#
# ## TWO SOUNDNESS ROUTES CLOSED AND LANDED THIS WINDOW, BOTH WITH THEIR COSTS MEASURED
#
#   **ROUTE #56 — CLOSED (`b9217158`), RE-PROOF GREEN.** A `None` Optional-union LOCAL
#   read back as the carrier's zero. L3 corpus BYTE-INERT; L3 mirror 1 mover, and that
#   mover (`w51f_m5ir`) has since proved rc=0. Witnesses 1108-1111.
#
#   **ROUTE #57 — CLOSED (`d7796dbf`), SEVEN RE-PROOFS IN FLIGHT AS QUEUE G.**
#   `d.get(k)` on a missing key was the codomain's ZERO, not `None`. THE MOST REACHABLE
#   ROUTE IN THE LEDGER — #56 needs an `Optional` mutable local (the corpus has ZERO);
#   this needed `d.get(k)`. L3 corpus BYTE-INERT (910/910, 0/0/0); L3 mirror 7 movers,
#   0 GONE, 0 APPEARED. Witnesses 1112-1115.
#
#   BOTH fixes reuse EXISTING opaques (`pycsl_none`, `pycsl_none_str`). No new model, no
#   new axiom, LEDGER STAYS 3. Metric unchanged at markers 456 / grep 481 / offset 25 / 0.
#
#   THE FAMILY: #44, #56 and #57 are ONE defect in three costumes — **FAITHFUL STORAGE,
#   ERASING READ**. The model carries a genuine absent value (`map 'k (option 'v)`, a real
#   `Arm_*_None`) and a `match … | None -> <literal>` arm throws it away AT THE POINT OF
#   USE, so an auditor who checks the REPRESENTATION finds it faithful.
#   `bin/check-collapsed-option-reads.py` (31st plane) now enumerates every such arm, and
#   the rule for telling the fatal from the benign is written into it: **a ghost SPEC
#   construct may DEFINE its absent-key answer (`\map_get` does, and says so on two
#   normative surfaces); a BODY lowering may not.**
#
# ## IN FLIGHT — DO NOT RELAUNCH
#
#   QUEUE G (`scratchpad/w49/queue51g.sh`), started 07:07, concurrency TWO, detached,
#   8h timeouts: `w51g_autotrust`, `w51g_types`, `w51g_functions`, `w51g_preamble`,
#   `w51g_scf`, then `w51g_expressions` and `w51g_statements` LAST as a pair (each ~3-4h).
#   These are route #57's seven owed movers. **If one FAILS that is the honest cost of the
#   repair and must be worked, not hidden.**
#
# ## THE TWO THINGS STILL OWED, IN PRIORITY ORDER
#
#   1. **`w51_cis` rc=1 — core_ir_semantic, 8 TERMINATION goals.** Diagnosed in
#      `getting-better/open-routes/finding-w51cis-termination-of-an-untyped-walk.md`, and
#      RE-CLASSIFIED there from correctness to COST/SCALE after the same file refuted my
#      first reading: other walks in it (`_union_c8_walk`, `_check_union_narrowing__collect`)
#      DO carry variants and DO discharge `variant decrease` goals. The difference is the
#      PARAMETER TYPE — those are annotated (`stmts: list`), `_returns_literal_none(body)`
#      is annotated nowhere and its nested `walk` is heterogeneous (dict|list|scalar).
#      A disposition test was running at the time of writing: mark `_returns_literal_none`
#      `\trusted` and re-prove, on the hypothesis that all 8 goals die with the nested
#      walk. **If it works the metric goes UP 456 -> 457 and that is the CORRECT direction.**
#   2. **THE L1 FIDELITY PLANE IS STILL RED** — `_handle_for_stmt` carries 37 of the live
#      emitter's 99 normalized statements while being counted as VERIFIED. The
#      `_handle_var_expr` half is FIXED AND MEASURED in a worktree
#      (`scratchpad/wt-l1b`): divergences 2 -> 1, 841 checked, and **17 of 18 planes green
#      with NO ratchet movement**. It was deliberately NOT landed with route #57, because
#      combining an EMITTER change with a MIRROR change would destroy attribution if the
#      shared `expressions.py` re-proof failed — the bisect that route #42 cost.
#      Land it AFTER queue G, with its own re-proof.
#
# ===================== the earlier #51 blocks follow ============================
#
# ===================== START HERE — #51 (UPDATED 2026-09-10 07:00 UTC) ===========
#
# ## EVERY BATTERY THIS CAMPAIGN WAS WAITING ON HAS REACHED A VERDICT
#
#   w49d_statements   rc=0 (4h09)  |  w49d_expressions  rc=0
#       THE TWO SLOWEST MIRRORS IN THE TREE. Each was killed at 55m in queue B and at
#       30m in queue C; NEITHER HAD EVER REACHED A VERDICT IN THIS CAMPAIGN. With these
#       two, ALL SIX owed movers from routes #46/#50 are banked.
#   w51_scf           rc=0         — the one the handoff said to watch (route #51
#       reshaped 75 lines of a VERIFIED method and its caller, making a previously
#       DELETED branch reachable). It proves; that cost was not owed after all.
#   w51f_m5ir         rc=0         — ROUTE #56's one owed re-proof. The repair HOLDS.
#   w51_cis           rc=1         — see below. Being worked, not hidden.
#
# ## OPERATIONAL — TWO WORKERS WERE LIVE ON THIS BRANCH AND THAT IS RESOLVED
#
#   The previous window's session (#50) was still alive alongside this one; its commits
#   `905e3eab` / `309d8bf4` sit on top of `d3c047aa`. It banked w49d_statements, warned
#   that its queue E was still armed, and STOOD DOWN. Nothing it armed needs relaunching.
#   No measurement was contaminated (its last code landing 12:08, #51's first commit
#   12:51); the only duplication was run 6's verdict, recorded twice.
#
# ## w51_cis rc=1 — core_ir_semantic, EIGHT TERMINATION GOALS
#
#   It is the FIRST-EVER proof of that file, so this is a first measurement, NOT a
#   regression. All 8 unproven goals are TERMINATION: 6x `walk`, 1x
#   `_returns_literal_none`, 1x `_check_scalar_return_annotation` — the last two being
#   exactly ROUTE #51's two new Module 4 functions.
#   CAUSE: `walk` is a NESTED recursion over an UNTYPED parameter
#   (`def _returns_literal_none(body) -> bool:` has no annotation) descending through
#   `node.values()` and list elements with no well-founded measure. Why3 cannot prove a
#   structural walk terminates when the thing walked has no type to measure. Timeouts at
#   30s / 50M+ steps — the prover grinding, not refuting.
#   Both functions are un-`\trusted` and carry contracts, so they are COUNTED AS VERIFIED
#   while their termination is unproved — the same shape as the L1 finding below.
#
# ## ROUTE #56 IS CLOSED AND LANDED (`b9217158`), RE-PROOF GREEN
#
#   A `None` Optional-union LOCAL read back as the carrier's zero. Fixed by answering
#   route #44's EXISTING `pycsl_none` opaque in the non-Some arm — no new model, no new
#   axiom, ledger stays 3. Witnesses 1108-1111 all verified against the landed tree.
#   L3 corpus BYTE-INERT (906/906, 0/0/0); L3 mirror exactly 1 MOVED, and that mover
#   (`w51f_m5ir`) has since PROVED rc=0.
#
# ===================== the earlier #51 block follows ============================
#
# ===================== START HERE — #51 (INTERIM, window 5 in progress) =========
#
# WRITTEN MID-WINDOW so a cold restart loses nothing. #50's block follows unchanged
# below, then #49's. Both are still the reference for everything before 12:44 UTC on
# 2026-09-09.
#
# ## STATE
#
#   HEAD            53ac770a (tracked tree CLEAN; the only untracked non-scratchpad
#                   entry is a 0-byte file `str` in the repo root, dated Sep 8 19:48 —
#                   the PREVIOUS window's stray, not mine, left alone deliberately)
#   metric          markers 456 / grep 481 / offset 25 / unattached 0 — UNCHANGED, which
#                   is the expected shape for a window paying the soundness ladder.
#                   **EXPECT IT TO GO UP**, see the L1 item below: `_handle_for_stmt`
#                   is honestly `\trusted` work and 456 -> 457 is the CORRECT outcome.
#   IN FLIGHT       `w49d_expressions` (from 10:55), `w49d_statements` (from 10:59),
#                   queue E armed behind QUEUE49D_DONE, reference-suite run 6 (from
#                   12:08). ALL FOUR VERIFIED ALIVE at 13:30. DO NOT RELAUNCH THEM.
#
# ## THE TWO HEADLINES
#
#   **1. THE L1 FIDELITY PLANE IS RED AT HEAD AND HAS BEEN FOR A LONG TIME.**
#   `bin/check-self-annotate-sync.sh` exits 1 in the MAIN tree. Two CONVERTED (un-
#   `\trusted`, contract-carrying) mirror methods have bodies that are strict SUBSETS of
#   the live emitter. Full record: `getting-better/open-routes/finding-L1-fidelity-plane-
#   red-at-head.md`. Measured by AST statement count, not by the plane's own truncated
#   diff, which UNDERSTATES the gap tenfold:
#       `_handle_var_expr`   42 of 48 live statements   — a straight DELETION. **FIXED**
#                            in a worktree by re-inserting the 21 live lines verbatim
#                            (`_iropt_ir_local_vars`, `_optional_union_locals`); plane
#                            goes diverged=2 -> diverged=1. NOT LANDED: `w49d_expressions`
#                            is proving that very file.
#       `_handle_for_stmt`   **37 of 99** by the plane's own normalized measure
#                            (71 of 342 counting every nested ast.stmt). The attractive "the mirror
#                            legitimately DECOMPOSED it via `_classify_iterable`"
#                            hypothesis is REFUTED — `_classify_iterable` exists in LIVE
#                            too, at class level (`stmt_control_flow.py:337`), and live
#                            already calls it (`:1169`). No allowlist exists in the plane;
#                            `_handle_for_stmt` appears NOWHERE in driver-progress.log. It
#                            was never argued for, it was never looked at.
#   Also found: **`bin/sync-mirror-bodies.py` DOES NOT RUN** — it imports `libcst`, which
#   is in neither the system python nor `.venv`. The campaign's mirror-resync tool has
#   been unusable for an unknown time, which is a plausible reason a body drifted to 21%.
#
#   **2. ROUTE #56 FOUND AND ITS REPAIR BUILT, MEASURED AND STAGED.** A `None`
#   Optional-union LOCAL read back as the carrier's ZERO.
#   `getting-better/open-routes/route56-optional-union-local-read-sentinel.md`.
#   TWO shapes, both verified against real Python: `x: Optional[int] = None; if x == 0:`
#   proves `\result == 0` where Python returns 9; and the worse one,
#   `return x + 1`, proves `\result == 1` where Python RAISES TypeError. The storage is
#   faithful (`Arm_0_None` is a real constructor); the VALUE-READ projection erases it.
#   BOUNDED: the `int` carrier ALONE — `str` and `float` fail closed on a Why3 TYPE
#   ACCIDENT, which is exactly why routes #50/#51 probed this class at `str` and found
#   nothing. REPAIR: answer route #44's EXISTING `pycsl_none` opaque in the non-Some arm.
#   No new model, no new axiom, ledger stays 3. Measured: both routes close, the `x == 5`
#   precision control and the `is None` guard both still prove.
#
# ## 3. ROUTE #57 FOUND — AND IT IS THE MOST REACHABLE ROUTE IN THE LEDGER
#
#   `d.get(k)` ON A MISSING KEY IS THE INTEGER ZERO, NOT `None`.
#   `getting-better/open-routes/route57-dict-get-no-default-is-zero.md`.
#   Route #56 needs an `Optional` mutable local, a shape the corpus contains ZERO of.
#   This one needs `d.get(k)` — everyday Python. `d: Dict[int,int] = {1: 2}` with
#   `if d.get(5) == 0:` proves `\result == 1` where Python returns 0; and
#   `v = d.get(5); return v + 1` proves 1 where Python RAISES TypeError.
#   MECHANISM: the map IS `map 'k (option 'v)` with a real `None`; the READ collapses it
#   (`| None -> 0`). SAME family as #44 and #56 — faithful storage, erasing read.
#   THE SHARP PART: the zero comes from `_dv_missing_default`, justified in its own
#   docstring as "proven dead under `#@ no_exception KeyError`". That is coherent for a
#   SUBSCRIPT, which RAISES. **`.get` NEVER RAISES.** Nothing can make the arm dead.
#   BROADER THAN #56: it decides at the `str` codomain too, because `.get` picks its
#   sentinel FROM the codomain type and is therefore type-correct at every codomain —
#   whereas #56 was masked at `str` by a Why3 TYPE ACCIDENT.
#   REPAIR SPIKED, SIX MEASUREMENTS: all four route shapes close; `d.get(k, v)` still
#   proves (NO precision cost); the missing-key SUBSCRIPT is deliberately UNTOUCHED
#   (that is the documented opt-in exception stance, not this route).
#   COST NOT MEASURED and expected to be REAL — `.get` is used heavily by the emitter's
#   own source, so unlike #56 this is unlikely to be byte-inert on the mirror.
#
# ## 4. SUITE RUN 6 — ROUTE #42's RE-FIX IS CONFIRMED
#
#   FINAL: **rc=1, 3232/3251, EXACTLY the standing NINETEEN** confirmed failures
#   (0211-0220, 0700, 0701, 0043, 0048, 0079, 0080, 0082, 0095, 0110). `1053`/`1054`/
#   `1055` are back at **XFAIL** and ABSENT from the failure list; they were XPASS in
#   run 5, which is how window #50 found a closed route live at HEAD. Both controls
#   (`1056`, `1057`) PASS, so the restored refusal does not swallow route #52's own arm.
#   **NO new failure anywhere in 3251 tests**, so nothing this window landed regressed
#   anything. Artifacts committed at `962d1eaa`.
#
# ## L3 IS NOW EXECUTABLE ON THE MIRROR, AND IT SEPARATED THE TWO REPAIRS' COSTS
#
#   `bin/mirror-emit-sweep.sh` (new) + `bin/byte-diff-compare.py`, 53 of 53 emitted on
#   every side, baseline = a clean worktree at `37403f79`:
#       ROUTE #56 ALONE          1 MOVED (`frontend/Module5_IREmitter`), 0 GONE, 0 APPEARED
#       ROUTE #56 + #57 TOGETHER 8 MOVED (adds auto_trust, expressions, functions,
#                                preamble, statements, stmt_control_flow, types)
#   **SO LAND THEM SEPARATELY.** Together, a cheap soundness closure is held hostage to
#   an expensive one. #56 owes ONE re-proof, of a file already re-proved green this
#   window (`w49d_m5ir` rc=0). And because #56 does NOT move `expressions`/`statements`,
#   landing it does NOT supersede the two in-flight proofs of those files.
#   THE SWEEP'S OWN GUARD CAUGHT A DEFECT IN THE METHOD EVERY PREVIOUS WINDOW USED:
#   53 mirror files, only 50 distinct BASENAMES (the four `__init__.py`). A
#   basename-flattened mirror diff compares the wrong pairs while reporting zero. The key
#   is now the relative path with `/` -> `__`.
#
# ## THREE PLANES LANDED, AND TWO OF THEM CAME OUT OF THE ROUTES
#
#   * `bin/run-soundness-planes.sh` (29th) — a COLLECTOR for the 18 pure-static lower
#     bounds, ~2 min. rc=2 if fewer than MIN_PLANES ran EVEN IF ALL WERE GREEN.
#   * `bin/check-type-keyed-value-sentinels.py` (30th) — type-keyed arms answering a VALUE
#     constant. Two recognizers: the dict-`.get` form (route #56's spelling) AND the
#     if/elif CHAIN form, which is how route #57's site is written and which the first
#     recognizer was blind to. A plane that only finds the spelling its first route used
#     is not a plane.
#   * `bin/check-collapsed-option-reads.py` (31st) — every `| None -> <literal>` arm, the
#     shape #44, #56 and #57 all share. Scoped to LITERAL answers, not all ~353 `| None ->`
#     arms, because the rest are None-PRESERVING and listing them would bury the nine.
#   * AND `check-self-annotate-mirror-sync.py` (the L1 plane) was HARDENED: it could
#     print "OK: all 0 ... are verbatim copies" and exit 0 on a broken population.
#     MIN_CHECKED=700 now, rc=2 on a shortfall. It also now prints the SIZE of each gap.
#
# ## WHAT IS STAGED AND WHY IT IS NOT LANDED
#
#   Everything below is BLOCKED ON SUITE RUN 6, which imports the LIVE emitter per test,
#   so no `src/pycsl` edit may land while it runs (runs 2/3/4 of window #50 died of
#   exactly this). Nothing here is speculative; each is measured.
#     a. Route #56's repair + its FOUR corpus witnesses — `getting-better/staged-route56/`
#        carries the files AND the ordered landing sequence. READ THAT README FIRST.
#     a2. Route #57's repair + its FOUR corpus witnesses — `getting-better/staged-route57/`,
#        same shape. #56 and #57 are BOTH in `expressions.py` and both reuse the SAME two
#        existing opaques, so land them together.
#     b. The L1 `_handle_var_expr` re-sync (also blocked on `w49d_expressions`).
#     c. Route #53's float repair — see below.
#     d. WIRING the collector into `bin/run-reference-tests.sh`. Blocked on the L1 red,
#        NOT on the suite: wiring a gate that fails is not wiring it.
#
# ## ROUTE #53 (float is an exact real) — RE-CONFIRMED LIVE, REPAIR DECIDED
#
#   Both recorded witnesses still prove at HEAD. The defect is ONE `ensures`: the float
#   arithmetic bridge was `val float_add_op (a b: real) : real ensures {{ result = a +. b }}`,
#   which PINS it to the reals. REPAIR: make it a deterministic opaque
#   (`val function`, no ensures) and route the SPEC path through the SAME symbol.
#   Measured: route closes, congruence survives (`ensures \result == x + x` still proves).
#   COST, stated honestly: `0517`'s `#@ ensures \result >= 0.0` no longer proves — an
#   opaque tells you nothing about ordering. The obvious refinement (add IEEE-true SIGN
#   clauses) was **REFUTED for `*`**: `a >= 0 /\ b >= 0 -> r >= 0` and its siblings meet
#   at `a = 0.0` and DECIDE `r = 0.0`, but Python's `0.0 * float("inf")` is `nan`.
#   NEW GENERAL LESSON: a conjunction of inequality axioms decides an EQUALITY where their
#   antecedents overlap — check any "harmless bound" at the boundary, not in the interior.
#
# ## WHAT LANDED THIS WINDOW
#
#   * `bin/run-soundness-planes.sh` (29th) — a COLLECTOR running all 17 pure-static lower
#     bounds in ~2 min. Negative-tested rc=1 (a red plane) and rc=2 (population shrinks
#     below MIN_PLANES even when every plane that ran was GREEN).
#   * `bin/check-type-keyed-value-sentinels.py` (30th) — type-keyed arms answering a VALUE
#     constant, the gap route #56 lived in. 4 sites, all classified WITH THEIR MEASURED
#     CARRIER. Negative-tested both ways.
#   * `check-getattr-erasure` MAX_UNKNOWN 19 -> 24, JUSTIFIED not bumped: the delta is
#     exactly route #47's five own corpus witnesses, and the plane's `--mirror-only` view
#     reports 19/19 rc=0. DECLARED stays pinned 0.
#
# ## LADDER FOR THE NEXT RELAUNCH
#
#   1. Collect `suite49_run6.rc` FIRST — 1053/1054/1055 must be CONFIRMED FAIL. Then
#      `w49d_expressions` / `w49d_statements`, then queue E's `w51_scf` / `w51_cis`.
#   2. Land route #56 by `getting-better/staged-route56/README.md`. The step NOT yet done
#      is the L3 byte-diff: the mirror DOES carry Optional locals, so it is not obviously
#      byte-inert and may owe mirror re-proofs.
#   3. Land the L1 `_handle_var_expr` re-sync; then DECIDE `_handle_for_stmt` — port 271
#      statements, or re-`\trusted` it and let the metric rise to 457. Do not leave it
#      counted as verified.
#   4. Then wire the collector into `bin/run-reference-tests.sh` (green-to-green once L1
#      is green), when NO suite is live — the runner re-invokes ITSELF per test.
#   5. Route #53's float opaque; `0700`; #36's last sliver.
#
# ## PROBED THIS WINDOW WITH NO FINDING (do not re-probe)
#
#   The other THREE members of the value-sentinel class all FAIL CLOSED, measured:
#   `expressions.py:6557` and `:8309` (an omitted argument whose param default is `None`,
#   filled with `""`/`0.0`) — `def g(s: str = None)` called as `g()` leaves BOTH goals
#   Unknown, including the TRUE one; and `:13378` `_union_local_field_projection` — a
#   field read through a `None` union local dies with a Why3 usage error. So the
#   value-sentinel class has exactly ONE live member and it is route #56.
#
# ===================== START HERE — #50 (INTERIM, window 5 in progress) =========
#
# WRITTEN MID-WINDOW so a cold restart loses nothing. #49's block follows unchanged
# below and is still the reference for everything before 08:39 UTC on 2026-09-09.
#
# ## STATE
#
#   HEAD            dcfea38c (tree clean apart from in-flight battery logs)
#   metric          markers 456 / grep 481 / offset 25 / unattached 0 — UNCHANGED all
#                   window, and that is the EXPECTED shape: two soundness routes closed,
#                   a refusal, an opaque and a whitelist, and none of them costs the
#                   trust surface anything. The ladder puts soundness routes above stub
#                   conversion; this window is paying that ladder, like #49 before it.
#   IN FLIGHT       queue D (`scratchpad/w49/queue49d.sh`) — the six owed movers,
#                   concurrency TWO, detached; queue E (`scratchpad/w51/queue51e.sh`) —
#                   armed to start on QUEUE49D_DONE with the two re-proofs route #51
#                   owes; reference suite run 5.
#
# ## WHAT #50 DID
#
#   **THE HEADLINE: ROUTE #42 HAD BEEN REOPENED AND WAS LIVE AT HEAD FOR A WHOLE
#   WINDOW.** The first reference suite to COMPLETE since route #52 landed reported
#   THREE XPASS — `1053`/`1054`/`1055`, route #42's own negative witnesses, PROVING.
#   An XPASS on a route witness is the harness saying a CLOSED SOUNDNESS ROUTE IS OPEN.
#   Bisected to `223424b9` (route #52); verified NOT this window's doing (it proves at
#   the window-start HEAD too). RE-CLOSED at `62931366`.
#     THE CAUSE WAS DEAD CODE, NOT A CHANGE OF POLICY, and reading the code is what
#     showed it: route #42's refusal had been left in the file NESTED INSIDE route #52's
#     `if` body, AFTER that body's unconditional `raise`, under a guard requiring
#     `_r42_other is None` while the body dereferences `_r42_other`. Unreachable twice
#     over; it could not have run even with the raise removed. A merge accident.
#     HOW IT PASSED EVERY PLANE — and this is the transferable part: route #52 landed on
#     a recorded "corpus byte-diff ZERO over 887", which was TRUE AND USELESS. **A
#     REFUSED file emits no `.mlw` at all, so it has NO BASELINE COUNTERPART, and a
#     diff-the-common-files sweep reports zero changes while a REFUSAL HAS BECOME AN
#     EMISSION** — the one direction that can only ever be a soundness loss. The mirror
#     half of that plane guards this ("all 53 still emit"); the corpus half never did.
#     FIXED AS A PLANE, not just as a route: `bin/byte-diff-compare.py` (`681acc25`)
#     reports and fails on MOVED / GONE / **APPEARED**, `byte-diff-sweep.sh` now writes a
#     SOURCES.txt manifest so an ADDED corpus file is told apart from a refusal-turned-
#     emission exactly, and it is NEGATIVE-TESTED AGAINST THE REAL REGRESSION: pointed at
#     the route-#42-closed corpus vs the route-#42-reopened one it flags all three
#     witnesses and returns 1. It would have caught route #52 at landing time.
#     WHY IT SURVIVED A WINDOW: the XPASS rule worked perfectly and was NEVER ASKED. No
#     suite had completed since #52 landed. **A signal nobody collects is not a signal**
#     — the third time this campaign has paid for that sentence.
#
#   ROUTE #51 CLOSED ON ALL THREE SHAPES, and the third shape was NEW. Route #50 gave
#     the string `is None` arm two BINDING-justified answers and left a third — the
#     always-present `false` — justified by nothing but the operand's TYPE. Three ways
#     reach it with no binding at all: (a) a local from a CALL whose `-> str` is
#     contradicted by `return None`, (b) a `str`-declared FIELD, and (c) — found this
#     window, and the CHEAPEST in the whole class — a `str`-declared PARAMETER, which
#     needs no annotation lie, no field store, no call and no branch join.
#     TWO INCREMENTS, because the shapes do not share a repair:
#       * Module 6: always-present is now a claim about a name the function BINDS
#         (`_r51_bound_names`, collected in route #46's EXISTING pre-scan walk).
#         Parameters, `self.<f>` fields and non-name operands get the SAME
#         `pycsl_none_str` opaque #50 installed one arm above — NO NEW MODEL.
#       * Module 4: `PYCSL-SEM-RETANN` refuses a `-> str` that can `return None`,
#         because a call-bound local IS a bound name and only a TRUE annotation can
#         justify deciding with it. Closing (a) by weakening the caller would have been
#         the wrong repair.
#     THE `int` PATH ALREADY ANSWERED THIS WAY — `s: int` and `s: bool` both fail closed
#     at HEAD (route #44's opaque) — so `str` was the odd one out, not a new cost.
#     LIVE IN THE MIRROR TWICE, and the second is the serious one:
#       * `Module2_Parser::expect_name(self, val: str = None)` — a parameter contradicted
#         by ITS OWN DEFAULT — emitted `val is not None` as the literal `true`, i.e.
#         DELETED, and every no-argument call takes that path.
#       * `stmt_control_flow::_try_union_is_none_match` declared `-> str` and returned
#         `None`, so its `return None` emitted as `raise (Return_str "")` — NONE AS THE
#         EMPTY STRING ON THE RETURN PATH, route #50's defect in the one place #50 did
#         not reach — and its caller `_handle_if_stmt`'s `if union_match is not None:`
#         emitted as `if true then begin`. The fall-back-to-the-normal-lowering path was
#         DELETED, so every proof of the emitter's own if-statement handler ran over a
#         STRICT SUBSET of its reachable states.
#
#   ROUTE #55 FOUND **AND** CLOSED, by following the 27th plane's OWN NAMED FOLLOW-UP.
#     `bin/check-type-keyed-constant-answers.py` justified the dict/set present-guard
#     with a claim about the CONTRACTS ("deleting a branch cannot make an `ensures True`
#     false") and its baseline said NOTHING CHECKS IT. A real postcondition breaks it:
#     `ensures \result == 7` PROVES for a body returning 0 on the empty-dict path,
#     because `if d:` emits as the literal `true`. Set proves too; list fails closed.
#     THE REPAIR IS THE SHAPE, NOT THE TYPE — the justification was RIGHT about the
#     shape it described and the arm had outgrown it. `true` is kept only where the
#     guard is the LEFT CONJUNCT of an `and` whose other conjunct is a membership test
#     on the SAME name (an empty map makes that test False anyway, so `true` is EXACT);
#     everything else gets a per-name opaque.
#     THE BLUNT REPAIR WAS BUILT FIRST AND REFUSED, and refusing it WAS the finding:
#     opaque-everywhere moved the ONE live site (`expressions.py`, `if subst and name in
#     subst:`), losing precision to correct nothing and owing a re-proof of one of the
#     two slowest mirrors. Shape-sensitive: **0 of 53 mirrors and 0 of 905 corpus move,
#     so NO re-proof is owed at all.**
#
#   THE 27th PLANE THEN CAUGHT ITS OWN STALENESS — it refused to go green, reporting the
#     NEW `[_r55_subsumed_name]` arm as unclassified AND the old dict/set entry as
#     matching no arm. Both are written; it now records **ZERO OPEN for the first time
#     this campaign**, because route #51's entry moved OPEN -> CLOSED in the same
#     increment. A plane that finds a route and then refuses to let its own repair go
#     unclassified is the shape every plane here should have.
#
#   LADDER ITEM 5 RE-MEASURED AND IT IS **ONE FILE, NOT SEVENTEEN**. `why3 --type-only`
#     over all 907 emitted modules gives 21 failures (the growth over the handoff's 17 is
#     entirely route witnesses added since). TWENTY carry `pycsl-expected: FAIL`, for
#     which an ill-typed emission IS the fail-closed mechanism. The ONE real gap is
#     `0700` — and it is the driver for the fix that is missing: `_field_default` is a
#     NESTED helper consulted only by the IN-FUNCTION record constructor, while `0700`
#     constructs at MODULE level via `_emit_module_globals`, which still writes the int
#     default. Fails closed (completeness, not soundness). VERIFIED PRE-EXISTING at the
#     window-start HEAD in an isolated worktree.
#
#   LADDER ITEM 4 DISCHARGED BY CLASSIFICATION, and one of the 55 was REFUTED as a
#     boundary. All 55 python-reference placeholders named and partitioned exactly
#     (0 unclassified, 0 phantoms). 53 are a CERTIFIED BOUNDARY. **`0206` is not**: a
#     full 2x2 shows PyCSL models the MRO faithfully AND discriminatingly.
#
# ## VERDICTS BANKED (updated 3be29ec8)
#
#   THREE of the six owed movers are IN, all rc=0, and all cover the LANDED tree:
#     `w49d_m5ir`   rc=0  10:17  Module5_IREmitter  (started before the landings, but its
#                                emission is byte-identical across both, so it counts)
#     `w49d_m2p`    rc=0  10:55  Module2_Parser     (started AFTER both landings — so the
#                                branch route #51 made REACHABLE does not break its proof)
#     `w49d_types`  rc=0  10:58  types.py           (route #50's OWN file, after both)
#   `w49d_scf` rc=143 — KILLED BY ME at 2h00, deliberately: it was certifying the
#     SUPERSEDED `stmt_control_flow` and occupying one of only two queue slots, blocking
#     both the rest of queue D and queue E (which is where the LIVE file gets proved).
#     Re-run it ONLY if `w51_scf` fails, where its diagnostic value is unchanged.
#
# ## WHAT IS OWED
#
#   1. `w49d_expressions` and `w49d_statements` (queue D, started 10:55/10:59 — the two
#      slow ones, killed at 55m in queue B and at 30m in queue C, never yet finished in
#      this campaign), then queue E's `w51_scf` and `w51_cis`.
#      **`w51_scf` IS THE ONE TO WATCH**: 75 lines of a VERIFIED (not `\trusted`) method
#      and its caller change shape and a previously-DELETED branch becomes reachable.
#      If it FAILS that is the honest cost and must be worked, not hidden.
#   2. The reference-suite verdict (run 5, launched 10:06 on the stable tree and still
#      running at 11:22 — it is progressing, not stuck; runs 2/3/4 were each killed
#      because I landed while they ran, see the lesson below).
#   3. **STAGED, NOT LANDED — both touch what a live suite reads, which is the only
#      reason they are not in:**
#        a. the `0206` real driver (body at `scratchpad/w51/mro/m1.py`), ratchet 55 -> 54;
#        b. wiring the planes into `bin/run-reference-tests.sh`. ALL of them are green at
#           the landed tree, so this is green-to-green with no remediation. It must NOT be
#           done while a suite is live: the runner re-invokes ITSELF per test
#           (`run-reference-tests.sh --worker {}` under xargs).
#   4. Route #55 owes NOTHING — measured byte-inert on both planes.
#
# ## IN FLIGHT WHEN #50 STOPPED (12:41 UTC) — COLLECT THESE FIRST
#
#   `w49d_expressions` (started 10:55) and `w49d_statements` (10:59) — queue D's last two
#   and the two slowest mirrors in the tree; neither has EVER completed in this campaign
#   (killed at 55m in queue B, at 30m in queue C). Their 8h `timeout` is intact.
#   Queue E (`scratchpad/w51/queue51e.sh`) is armed and waits on `QUEUE49D_DONE`; it runs
#   `w51_scf` then `w51_cis`.
#   Reference suite RUN 6 **IS IN AND IT CONFIRMS THE ROUTE #42 RE-FIX**: rc=1,
#   **3232/3251, ZERO XPASS** (run 5 had three), pass count up by exactly three, and the
#   confirmed-failure list is now EXACTLY the standing nineteen. Run 6 carries FIVE
#   landings on top of run 5 and introduced ZERO new failures — the nineteen are the same
#   nineteen, name for name. Nothing further is owed on the suite plane.
#   The route #42 fix is ALREADY PROVED BYTE-INERT ON THE MIRROR (0 of 53 move), so the
#   two in-flight proofs are NOT superseded by it and their verdicts stand for HEAD.
#
# ## LADDER FOR THE NEXT RELAUNCH
#
#   1. Read `getting-better/proofs49/queue49.progress` FIRST and record every verdict.
#      **If a mover FAILS, that is the honest cost of making a deleted branch reachable
#      and it must be worked, not hidden.** `w51_scf` is the one to watch: 75 lines of a
#      VERIFIED method and its caller change shape and a previously-DELETED branch
#      becomes reachable.
#   2. `0206` IS LANDED (ratchets 82->81 and 55->54). Still to do: probe `0188`
#      (`except*`) rather than assuming it, and WIRE THE PLANES into
#      `bin/run-reference-tests.sh` — all are green at HEAD so it is green-to-green, and
#      it is the standing fix for the failure mode that let route #42 sit reopened for a
#      whole window. Do it when NO suite is live: the runner re-invokes ITSELF per test.
#   3. `0700` — lift `_field_default` out of its nested scope so BOTH construction paths
#      consult one function. **Budget for mirroring the lifted helper in the same
#      increment**: a new top-level def moves `check-mirror-coverage`, which is exactly
#      the ratchet that caught route #51's two new Module 4 functions.
#   4. Keep mining `bin/check-type-keyed-constant-answers.py`. It has now produced TWO
#      routes (#51 via its OPEN entry, #55 via its named follow-up). The method that
#      works: take an arm's stated justification, write the contract it says cannot
#      break, and run the Python. The emit_ir always-present family's FRAME half is
#      still named-and-unchecked, and the `ensures` half of THAT family is measured
#      safe only because all seven reaching methods carry `#@ ensures True` — giving any
#      of them a real postcondition would break it.
#   5. #36's last sliver (three approaches already refuted — read #45's note first).
#
# ## THE 28th PLANE LANDED THIS WINDOW
#
#   `bin/check-emit-ir-arm-postconditions.py`. The 27th plane's justification for the
#   emit_ir always-present family is CONDITIONAL, not structural — sound only while all
#   seven reaching methods carry `#@ ensures True` — and its own text names that as the
#   way to break it. Nothing failed if you did. Now something does. Negative-tested BOTH
#   ways before landing (rc=1 on a real postcondition, rc=2 when the instance count moves).
#   The two planes COMPOSE: the 27th owns the arms, the 28th owns the methods.
#
# ## AND THE PLANES THEMSELVES ARE MOSTLY UNWIRED — read this before trusting a green
#
#   `bin/run-reference-tests.sh` gates on EXACTLY ONE plane: `doc-coherency`. Every other
#   lower bound here — trusted-directives, mirror-coverage, raises-honesty,
#   vacuous-drivers, type-keyed-constant-answers, both fidelity planes, and the new 28th —
#   is DRIVER-RUN, i.e. fires only when a relaunch remembers. That is the mechanism behind
#   two of this campaign's own surprises: #49 found raises-honesty RED AT HEAD with nobody
#   looking, and #50 found the 27th plane's baseline STALE only because it happened to
#   change the arm. **A lower bound nobody runs is not a lower bound, it is a note.**
#
# ## PROBED THIS WINDOW WITH NO FINDING (do not re-probe)
#
#   The `is None` residue class at EVERY remaining simple type — a `bytes`, `float`,
#   `list` and RECORD/dataclass-declared field, all `@mutable_state`-gated, ALL FAIL
#   CLOSED; so the class #44 (int) / #50 (str local) / #51 (str call/field/param) covers
#   is now closed at the simple types. Route #51 at the TUPLE type (`_ghost_tuple_vars`)
#   — does not reproduce in either the lying `-> Tuple[int,int]` or honest
#   `Optional[Tuple[...]]` spelling, and this one is worth remembering because the arm
#   LOOKS like #51's and the Module 4 refusal (scoped to `-> str`) genuinely does NOT
#   cover it: the reason it is safe is not the refusal. The FRAME half of the 27th
#   plane's named follow-up (a `self.<field>` write on the DELETED branch under
#   `assigns \nothing`) — fails closed; it is the ENSURES half that was live.
#
# ## LESSONS BANKED THIS WINDOW (all paid for in my own process)
#
#   * **A LONG BATTERY AND A LANDING CANNOT SHARE A TREE.** The reference suite spawns a
#     fresh subprocess per test that imports the LIVE emitter, so ANY edit to
#     `src/pycsl` after it starts contaminates it. Runs 2, 3 and 4 were each killed for
#     this. Either land nothing while it runs, or run it last. Whole-file mirror proofs
#     are NOT affected the same way (python imports the emitter once, at process start),
#     which is why queue D's in-flight children stayed valid across two landings.
#   * **NEVER `git stash` WHILE A DETACHED BATTERY WRITES INTO A TRACKED PATH.** An
#     earlier `git add -A getting-better/` had made the in-flight proof logs TRACKED; the
#     stash then unlinked the inode `w49d_m5ir`'s running proof holds open. The `.rc`
#     verdict still lands (pr.sh reopens for the echo) but the log content is frozen.
#     Add specific files, never `-A`, into a directory a battery is writing to.
#   * **A RED SIGNAL INSIDE AN ACCEPTED TOTAL IS NOT A SIGNAL** — `0700` has been failing
#     inside the standing suite-failure count, with a docstring saying it PROVES, since
#     the fix it documents landed on the other path. Same shape as #49's discovery that
#     `check-trusted-raises-honesty` was RED at HEAD with nobody looking.
#   * **CHECK A NEW CHECK FOR FALSE POSITIVES BEFORE BELIEVING ITS CENSUS.** #51's Module
#     4 refusal first reported four breaking functions; two were a nested helper's early
#     `return` in a function that returns the EMPTY STRING. True radius: one.
#   * **MEASURE A FIX AND READ THE DIFF IT PRODUCES** (#49's method, and it paid twice
#     more): it is what found route #50's live mirror site, what turned route #55's blunt
#     repair into a REFUSED one, and what corrected route #55's own census from "zero
#     live sites" to one.
#   * **THE FIDELITY PLANES ARE RED AT HEAD AND ARE USED DIFFERENTIALLY.** Both
#     `check-self-annotate-sync.sh` and `self-annotate-mirror-check.sh` return rc=1 on a
#     clean tree. That is why every handoff says "byte-identical to HEAD's own runs" and
#     never "rc=0". Do not read rc=1 as a regression; diff the output against HEAD's.
#
# ===================== START HERE — #49 (INTERIM, window 4 in progress) ==========
#
# WRITTEN MID-WINDOW so a cold restart loses nothing. #48's block follows unchanged
# below and is still the reference for everything before 18:16 UTC on 2026-09-08.
#
# ## STATE
#
#   HEAD            b0e9b284 (tree clean)
#   metric          markers 456 / grep 481 / offset 25 — UNCHANGED all window, and that
#                   is the expected shape: a refusal, a whitelist and an opaque value
#                   all cost the trust surface nothing. The ladder puts soundness
#                   routes above stub conversion; this window is paying that ladder.
#   IN FLIGHT       queue C (getting-better/proofs49/, `scratchpad/w49/queue49c.sh`) —
#                   the SIX mirrors routes #46/#50 move, concurrency TWO, detached under
#                   setsid; and reference suite run 1 at jobs=3
#                   (getting-better/proofs49/suite49_run1.*). BOTH started AFTER the
#                   landing commit 5f57a95d, so both describe the final tree.
#
# ## WHAT #49 DID
#
#   ROUTE #46 CLOSED — open since #48, and #48 had BUILT AND REFUTED the obvious repair
#     (a sticky record). The landed repair is #48's designed AMBIGUITY PRE-SCAN plus
#     three things #48 could not have known without building it, each MEASURED:
#       * it carries a NESTING DEPTH. A name whose bindings are ALL at the top level of
#         the body keeps the existing linear record — emission order IS execution order
#         there — so `x = None; x = 5` loses nothing (witness 1090). Ambiguity needs a
#         CONDITIONAL binding. Without this the fix poisons the whole tree.
#       * the per-name opaque carries the LOCAL'S OWN WhyML type (`ref ""` vs `ref 0`),
#         NEVER the symbol table's Python tag: an unannotated str local is tagged `Any`.
#         The first spelling emitted `pycsl_erased_receiver_name : int` into `str_eq_op`
#         — L3-tc ✗ on FOUR mirrors.
#       * a name that ALREADY has a faithful optional carrier is skipped
#         (`_optional_union_locals`, `_iropt_ir_local_vars`, `_iropt_str_local_vars`,
#         `_emit_ir_local_vars`). EVERY ambiguous name in the pure_ast mirror is one of
#         these, which is why pure_ast does not move at all.
#       The NaN half is a REFUSAL whose taint FOLLOWS ARITHMETIC (IEEE 754), because
#       route #45 established that opacity cannot close `x == x`.
#
#   ROUTE #50 FOUND AND CLOSED — `Optional[str]` was modelled as NEVER None, with `None`
#     as the EMPTY STRING. `@mutable_state`-gated, so it is LIVE IN THE MIRROR:
#     `module6_whyml/types.py`'s `if receiver_name is None or field_name is None:`
#     emitted `if ((if false || false then 1 else 0) <> 0)` — the branch Python takes,
#     DELETED. Repair: a type-PRESERVING opaque `pycsl_none_str`, and `is None` now has
#     THREE answers keyed on the BINDING (decided under a live linear record, opaque
#     under AMBIG, unchanged always-present where the function never binds None).
#     Witness 1087 is a COMPLETENESS GAIN — it FAILED at the parent by TYPE ACCIDENT
#     (the int opaque in a string context) and proves now. Second such repair after #45.
#
#   HOW #50 WAS FOUND IS THE TRANSFERABLE PART, and it is a NEW method for this campaign:
#     **MEASURE A FIX AND READ THE DIFF IT PRODUCES.** #50 did not come from probing a
#     soundness claim. Route #46's first spelling poisoned an ambiguous local with an INT
#     opaque; the mirror emission diff showed `pycsl_erased_receiver_name` inside
#     `str_eq_op`, which sent me to read that file's emission AT HEAD — and the defect
#     was one line away.
#
#   ROUTE #51 FOUND (OPEN) — a `-> str` annotation contradicted by a `return None` is
#     BELIEVED, and route #50's always-present answer decides with it:
#     `s = self.pick(c); if s is None:` PROVES `\result == 7` where Python returns 0.
#     Census: 10 mirror sites, 3 live, ZERO corpus — but only ONE mirror site is `-> str`
#     (`stmt_control_flow::_try_union_is_none_match`); the nine `-> int` ones fail closed
#     (control q4). Recommendation recorded: refuse the lie in Module 4, SCOPED TO
#     `-> str`, blast radius one file.
#     `getting-better/open-routes/route51-scalar-annotation-lie.md`
#
#   A GATE WAS RED AT HEAD AND NOBODY HAD LOOKED — `bin/check-trusted-raises-honesty.py`
#     reported 69 > 68 because route #49's refusal was the 69th SILENT stub and #48's
#     battery ran BEFORE #47/#48/#49 landed. Fixed by MEASURING rather than shrugging:
#     rows now say `SILENT/refusal` vs `SILENT` (36 of 69 are refusals — a raise that
#     REJECTS THE FILE is not an exit path of a lowering), and the bump to 70 is itemised
#     per stub. LESSON: re-run the battery AFTER the last landing of a window, not before.
#
# ## WHAT IS OWED (and what is already banked)
#
#   BANKED at the final tree, rc=0 `[+] Verification SUCCESS`: `functions`, `exec_splice`,
#   `desugar` (queue B, all three proved BEFORE the landing and their emission does NOT
#   move under it — verified by the 53-file mirror emission diff). `pure_ast` and `sertop`
#   keep #48's standing verdicts for the same reason, re-verified this window.
#   OWED: the SIX movers, in queue C right now — expressions, statements, Module5_IREmitter,
#   stmt_control_flow, types, Module2_Parser. Plus the reference suite verdict.
#
# ## LADDER FOR THE NEXT RELAUNCH
#
#   1. Read `getting-better/proofs49/queue49.progress` FIRST and record the six verdicts.
#      If a mover FAILS, that is the honest cost of making a deleted branch reachable and
#      it must be worked, not hidden.
#   2. Route #51 — the recommendation is written and scoped; build it.
#   3. The `is None` residue class more broadly: route #50 fixed the LOCAL, #51 is the
#      CALL, and the FIELD (`self.f = None`) is still unprobed for the string case
#      (route #44 recorded the int case as residue).
#   4. Then the vacuous-driver ratchets (pycsl-reference 9/8, python-reference 82/55 —
#      note #48's tightening; the remaining 55 are mostly async/metaclass/import-machinery
#      constructs PyCSL does not model, so treat them as a CERTIFIED-BOUNDARY class rather
#      than as work, and say so explicitly rather than leaving the ratchet looking lazy).
#   5. Then the seventeen why3 --type-only failures and #36's last sliver.
#
# ## PROBED THIS WINDOW WITH NO FINDING (do not re-probe)
#
#   erased-local projections (tuple index, `len` of a set/tuple, set membership, dict
#   literal read); chained comparisons in PROGRAM code (route #33's desugar handles them
#   — the `types.py` comment claiming otherwise is about the MIRROR path and is stale);
#   `round`/`int()` on floats and string ordering (all type-rejected); negative indexing
#   (`a[-1]` lowers to `a[len-1]`, faithful); `True + True`; recursion without a variant
#   (termination IS checked — `Cannot prove termination`); a non-terminating `while`
#   (Why3 emits a `termination` sub-goal and it is Unknown, so the run FAILS); two
#   comprehensions / generators / sets / tuples compared to each other (route #41's
#   per-name opacity holds); `abs`/`max`/`min` (`abs` is an ABSTRACT val with no contract
#   — a stated completeness gap, not a route).
#
# ===================== START HERE — #48 (INTERIM, window 4 in progress) ==========
#
# THIS BLOCK IS WRITTEN MID-WINDOW so a cold restart loses nothing. It is rewritten
# at the window's end with final numbers. Everything below the "#47" heading is the
# previous history, unchanged.
#
# ## WHAT THIS WINDOW HAS DONE SO FAR
#
# **ROUTE #42 CLOSED AND FULLY BANKED**, and FOUR MORE ROUTES FOUND (#44, #45, #47,
# #48, #49 — five open at their discovery, two of them since fixed and staged), TWO
# NEW PLANES WRITTEN (the 25th and 26th), one CAPABILITY landed, and TWENTY-THREE
# vacuous drivers converted.
#
#   ROUTE #42 — `<int> is True` proved `\result == 7` where Python says False.
#     CLOSED at `bee3564c`, banked at `d7ce974c`. `is` was given its OWN IR OPERATOR
#     (`ast.Is` -> `"is"`), narrowed back to `==`/`!=` in `Module5_IREmitter.
#     generate_json` carrying the ADDITIVE `py_is` marker, and the bool-singleton test
#     is WHITELISTED in `_expr_to_whyml` — admitted only when the emitter can SHOW the
#     operand is a Python `bool`. Witnesses 1053-1057. ALL FOUR PLANES GREEN: fidelity
#     unchanged, corpus byte-diff 0 over 863, suite 3183/3202 ZERO XPASS with the same
#     nineteen failures, and the ONE changed mirror re-proved rc=0 at 2109 goals —
#     EXACTLY the count #46 recorded for it.
#
#   ROUTE #44 — `None` WAS THE INTEGER ZERO. Four shapes, and the fourth needs no
#     branch: the CONTRACT `#@ ensures \result == None` PROVED for a function returning
#     0. Landed at `c8a58cc9`. Route #41's opaque-value device with a SHARED constant
#     (`None` really is one object, so `x = None; y = None; x == y` must stay provable),
#     truthiness kept FAITHFUL as `false`, and a faithful `\result != None` arm GATED ON
#     THE PYTHON RETURN ANNOTATION — the WhyML type alone would have fired on an
#     `Optional[_Tok]` return degenerated to `int` and handed callers a false guarantee.
#     Witnesses 1058-1064.
#
#   ROUTE #45 — NaN BREAKS THE REFLEXIVITY OF `==`, AND OPACITY CANNOT FIX IT. This is
#     the first route whose repair could NOT be "make the value opaque": the value was
#     ALREADY opaque and an opaque constant is still equal to itself. NaN's comparison
#     semantics are TOTALLY DETERMINED, so the lowering is EXACT — which makes this the
#     campaign's first repair that increases COMPLETENESS as well as soundness (three
#     true contracts that could not be discharged now prove). Landed at `49a7334a`.
#     Witnesses 1065-1069.
#
#   CAPABILITY — a CHAINED COMPARISON in a `#@` clause now means the CONJUNCTION. It had
#     never meant anything: `0 <= x <= 3` lowered to `((0 <= x) <= 3)`, type-rejected.
#     MEASURED BYTE-INERT on both planes (0 of 875 corpus, 0 of 53 mirrors), so it cost
#     no re-proof. `pycsl-reference/0969`'s docstring claimed the opposite and is
#     corrected in place. Landed `4f734829`, witnesses 1074-1075.
#
# ## WHAT IS STAGED AND NOT YET LANDED — READ THIS FIRST ON A COLD START
#
# THREE routes are FIXED, WITNESSED and MEASURED but deliberately NOT in the tree,
# because the #44/#45 mirror re-proof queue was still running and three of their six
# mirrors overlap it. The patches and witnesses are on disk:
#
#   * `/tmp/w48spike/r47.patch`  — route #47 (getattr default), applies to
#     `src/pycsl/module6_whyml/expressions.py`. Witnesses `/tmp/w48spike/107*_route47*.py`
#     (also in the `/tmp/pycsl-w48-spike` worktree's corpus).
#   * route #48 (seeded collection) — the patch text is inline in the spike worktree
#     `/tmp/pycsl-w48-spike`; witnesses 1076-1079 in its corpus.
#   * `/tmp/w48spike/r49.patch` — route #49 (append through a parameter), applies to
#     `src/pycsl/module6_whyml/statements.py`. Witnesses 1080-1082 in the
#     `/tmp/pycsl-w48-chain` worktree's corpus, plus the REWRITTEN `0406.py`/`0407.py`
#     there (they are the only two corpus files the refusal costs).
#   * `/tmp/w48spike/apply_docs.py` — the §T.5.12k/l/m doc sections for all three.
#
#   IF THE WORKTREES ARE GONE, all three are fully specified in
#   `getting-better/open-routes/route4{7,8,9}-*.md` with their measurements.
#
#   MEASURED FOR ALL THREE TOGETHER: corpus byte-diff ZERO (except the two rewritten
#   detector drivers), mirror emission SIX files (desugar, exec_splice, expressions,
#   functions, statements, stmt_control_flow), all six L3-tc GREEN, mirror-coverage
#   550/41, metric 456/481/25. Every witness negative-tested BOTH ways.
#
# ## THE TWO NEW PLANES
#
#   `bin/check-singleton-constant-lowering.py` (25th) — every `if` keyed on an IR NODE
#   KIND whose body answers a Why3 CONSTANT. That is the shape behind routes #40, #41,
#   #42, #43 and #44. IT FOUND ROUTE #47 WITHIN MINUTES OF BEING WRITTEN, and then it
#   caught its own author: routes #44 and #45 each added an arm and the plane went RED
#   on both (both faithful, both now classified with the corpus control that holds them).
#
#   `bin/check-param-mutator-visibility.py` (26th) — EXECUTABLE, not static. For each
#   (receiver type, mutator) cell it GENERATES a driver whose caller asserts the
#   collection is unchanged after a mutating call — a contract FALSE of the program —
#   and runs the real pipeline: raises => REFUSED, proves => DROPPED, fails =>
#   CALLER-VISIBLE. Ten cells; exactly ONE is DROPPED (`a.append(1)`, route #49) against
#   five REFUSED siblings and four CALLER-VISIBLE write forms.
#
# ## THE METHOD THAT FOUND #48 AND #49, and it is the transferable part
#
# **GREP THE EMITTER FOR ITS OWN SOUNDNESS CLAIMS AND PROBE EACH ONE.**
# `grep -rn "sound over-approx\|fails-safe\|always-present\|sound under-approx"
# src/pycsl/module6_whyml/` gives about thirty; most are gated to mirror-only shapes, and
# the corpus-reachable ones are a short list. The FIRST one probed was route #48, whose
# comment claimed "a sound under-approximation ... never proves falsely" — the exact
# claim the measurement refutes. The second was route #49.
#
# ## OTHER MEASURED FINDINGS RECORDED THIS WINDOW
#
#   * `check-dropped-mutation`'s population is DISJOINT from route #49 (Module 5
#     statements vs a Module 6 lowering) — the 26th plane exists because of it.
#   * the vacuous-driver EMPTY classifier had a FALSE-POSITIVE CLASS: 39 of its 47
#     pycsl-reference "empty placeholders" carry real proof obligations (inductive
#     predicates, cited recursive lemmas, string-containment logic terms, refusal tests).
#     Tightened to the conjunction; 47 -> 8, python-reference unchanged at 55.
#   * TWO fail-closed completeness gaps, both recorded IN the drivers that hit them:
#     `needs_string` misses files whose strings come only from UNANNOTATED locals, so
#     `concat` is unbound and every contract over a concatenation fails (0031); and float
#     EQUALITY in a program guard is not modelled, only the orderings (0035).
#   * ~60 shapes probed across ten families with NO finding — the list is in
#     `getting-better/driver-progress.log` so nobody re-probes them. Notably the
#     division/modulo model is FAITHFUL to Python's FLOORED semantics, not Euclidean.
#
# ## STATE
#
#   metric            markers 456 / grep 481 / offset 25 — UNCHANGED all window. A
#                     refusal, a whitelist and an opaque value all cost the trust
#                     surface nothing.
#   planes            the full static battery is rc=0 on the landed tree (twenty
#                     scripts, listed in the progress log), plus the two new ones.
#   fidelity          sync 2 DIVERGED / mirror-check 3 drifted — BYTE-IDENTICAL to
#                     HEAD's own runs, i.e. the pre-existing pair and trio.
#   vacuous ratchets  python-reference 105/78 -> 82/55, pycsl-reference 9/47 -> 9/8.
#   OWED              the #44/#45 mirror re-proof queue (5 files) was still running when
#                     this block was written; then routes #47/#48/#49 land with their own
#                     6-file queue; then ONE full reference suite over everything.
#
# ==========================================================================

# ===================== #47 COLD-START VERIFICATION (12-minute window) =============
#
# I am worker #47. My whole window was ~12 minutes, so I did NOT advance the ladder.
# What I did is the one thing a 12-minute worker can do honestly: RE-MEASURE the
# claims below from the surface and record exactly which ones I checked, so the next
# worker knows what is verified and what is inherited on trust.
#
# VERIFIED FRESH AT bba0bb86 (by me, this window):
#   * metric          `python3 bin/count-trusted-directives.py` -> markers 456 ·
#                     grep-substring 481 · offset 25 · attached 456 · unattached 0.
#                     EXACTLY as #46 states. The offset is the 25 boilerplate
#                     docstring lines; every historical absolute floor figure
#                     (including "687") is overstated by 25.
#   * artifacts       every file this handoff tells you to open EXISTS:
#                     getting-better/open-routes/route42-is-bool-singleton.md,
#                     bin/check-constant-fallthrough.py, bin/check-vacuous-drivers.py,
#                     getting-better/driver-backlog.md, getting-better/driver-progress.log,
#                     getting-better/.driver-deadline (1788612973, do NOT re-arm or delete).
#   * evidence        getting-better/proofs46/ (the three whole-file re-proof logs +
#                     rc files + the suite logs #46 cites) was UNTRACKED at my start
#                     even though proofs45/ is tracked. I COMMITTED IT. The cited
#                     evidence is now in the repo, not just on this disk.
#
# NOT RE-VERIFIED BY ME (inherited from #46 on its own record — re-run before you
# quote any of it as your own measurement):
#   the 24 gate planes, mirror L3-tc 53/53, the reference suite 3178/3197 with
#   nineteen failures and zero XPASS, the byte-diff inertness, and the witness
#   subset 47/47. None of these fit in twelve minutes. #46 ran the suite FOUR times.
#
# ONE TREE NOTE, so you do not mistake it for damage: `scratchpad/w7/base` and
# `scratchpad/w8/pre` show as ` M` in `git status`. They are GIT WORKTREES (each holds
# a `.git` FILE, not a directory) left by earlier workers, so git reports them as
# changed gitlinks. `git diff` on them is EMPTY — there is no content change to
# commit or revert. LEAVE THEM ALONE; they are not this window's work and removing
# them would destroy another worker's checkout. "Tree clean" in this campaign means
# clean apart from those two.
#
# WHERE THE LADDER STANDS FOR THE NEXT WORKER — the order #46 left, unchanged:
#   0.  ROUTE #42 IS OPEN AND FULLY SCOPED. `x = 1; if x is True: return 7` proves
#       `\result == 7` while Python's `1 is True` is False. The build is named:
#       GIVE THE IR A DISTINCT `is` OPERATOR instead of Module 5's collapse to `==`.
#       A blanket refusal breaks 94 mirror sites; a type-directed one is an
#       UNDER-APPROXIMATION, which is the exact mistake #39 and #41 were about.
#       Best-scoped item in the file.
#   0b. THE VACUOUS-DRIVER POPULATION: 116/2187 python-reference + 9/867
#       pycsl-reference prove their contract from the tail `return` alone; 89 + 47
#       are EMPTY PLACEHOLDERS. Ratchets stand at 105 / 78 after #46's ELEVEN
#       conversions (0019 0022 0024 0029 0030 0034 0037 0055 0056 0057 0062).
#       Recipe: give the driver a real body and a contract that MENTIONS the
#       construct it is named for — the contract does the work a Python `assert`
#       cannot, because Module 6 DROPS `assert`. Known blocker: a contract over a
#       FLOAT LOCAL does not type-check (real-vs-int), which is why 0035 is still
#       a placeholder. That is fail-closed, a completeness gap, not a hole.
#   1.  The "fail-closed BY ACCIDENT" population -> designed refusals.
#   2.  The seventeen `why3 prove --type-only` failures (USE THE TYPE CHECKER,
#       NOT A REGEX).
#   3.  The last sliver of #36 — read #45's note first, three approaches refuted.
#
# THE STANDING LESSONS, carried forward verbatim because every one of them was paid
# for with a live defect:
#   * A REFUSAL IS ONLY AS SOUND AS THE RESOLUTION IT KEYS ON, and A WHITELIST ONLY
#     AS SOUND AS THE IDENTITY CHECK ADMITTING NAMES TO IT (#39, twice).
#   * MAKE THE VALUE OPAQUE, NOT THE CONSUMER REFUSED — and PER NAME, or the model
#     proves two distinct erased locals equal.
#   * RUN THE WHOLE SUITE AND READ NEW FAILURES AS EVIDENCE, not noise. Route #40's
#     other half was visible ONLY as a completeness regression on 0041, a test that
#     had been passing BY ACCIDENT.
#   * COUNTING A DROP IS NOT ESTABLISHING IT IS SAFE.
#   * FIX AT THE CHOKE POINT, NOT WHERE THE DEFECT IS VISIBLE.
#   * PROBE EVERY CANDIDATE END-TO-END WITH A CONTRACT FALSE OF THE PROGRAM. A
#     driver that passes without the construct it names being modelled is evidence
#     of nothing.
#   * HONESTY OVER THE NUMBER. The suite's pass rate is a LOWER bound on how much is
#     untested, not an upper bound on how much is tested.
#
# ==========================================================================

# ===================== START HERE — #46 -> next window =====================
#
# **FOUR MORE UNSOUNDNESS ROUTES CLOSED (#39, #40, #41, #43), A FIFTH FOUND AND
# SCOPED (#42), AND ALL OF THEM ARE THE SAME MISTAKE IN DIFFERENT PLACES.** Every
# one is negative-tested end to end: each witness PROVES a contract FALSE of its own
# program at its parent commit and fails closed at HEAD. The metric is UNCHANGED at
# markers 456 / grep 481 / offset 25 throughout — not one of these needed a new trust
# stub, because a refusal and an opaque value both cost the trust surface nothing.
# TWENTY witnesses added (1033-1052), TWO new planes (the twenty-third and
# twenty-fourth), THREE whole-file re-proofs rc=0 with zero bad goals, and ELEVEN
# empty placeholder drivers converted into real proof obligations.
#
#   #39  ROUTE #38's OWN REFUSAL WAS WALKED PAST BY TWO LINES OF ORDINARY PYTHON.
#        `c: CM = CM()` is an `AnnAssign`, and #38's binding census read plain
#        `Assign` nodes only; `class CM(Base)` with the protocol on the BASE was
#        never in #38's class set because the scan read each ClassDef's own body.
#        Both re-ran #38's exploit VERBATIM and proved `\result == 0` where Python
#        returns 5.                                   witnesses 1033 / 1035, 1034 ctl
#        AND THEN THE WHITELIST I WROTE TO FIX IT LAUNDERED THE SAME THING: W2
#        matches the callee's LAST SEGMENT (it must — `open`, `tempfile.X`,
#        `contextlib.closing`), so a USER class named `closing` that defines
#        `__enter__`/`__exit__` was waved through, and `g.v = 0; with closing():
#        pass; return g.v` proved `\result == 0` where Python returns 5.
#        A WHITELIST IS ONLY AS SOUND AS THE IDENTITY CHECK THAT ADMITS NAMES TO
#        IT.                                                       witness 1047
#   #40  THE `...` LITERAL WAS THE INTEGER ZERO. Flagged by relaunch #12 as "a
#        silent WRONG-VALUE erasure ... left alone deliberately" and NEVER PROBED.
#        SIX shapes proved a false contract: `if x:`, `if ...:`, `x == 0`,
#        `<int> is ...`, `x + 5`, `return ...`.          witnesses 1036-1040
#        AND THE BUILTIN NAME `Ellipsis` IS THE SAME SINGLETON AND WAS ALSO THE
#        INTEGER ZERO — `x = 0; if x is Ellipsis: return 7` proved `\result == 7`.
#        **THE FULL SUITE IS WHAT SURFACED THAT**, as a NEW failure on
#        `python-reference/0041`: a TRUE contract that had been proving BY ACCIDENT
#        (`0 = 0`) stopped proving once half the singleton became opaque. THE
#        COMPLETENESS REGRESSION WAS THE VISIBLE END OF A LIVE SOUNDNESS HOLE, and
#        nothing else in the battery could see it.       witnesses 1048 / 1049
#   #41  ROUTES #25/#26/#27 REFUSED THE GUARD AND NOTHING ELSE. The same erased
#        local (a generator expression / non-empty set / non-empty tuple) was
#        exploitable through `== 0`, `< 1` and `+ 5`; and the EMPTY tuple was
#        outside the record entirely, so `() == 0` proved.  witnesses 1041-1046
#
#   #43  A COMPLEX LITERAL WAS THE INTEGER ZERO. `_py_expr_constant` lowers a
#        complex constant to `int(value.real)` — imaginary part DISCARDED, real part
#        TRUNCATED — and there is no complex model anywhere, so the model gets an
#        ordinary integer and DECIDES on it. `3j == 0` proved (Python: False),
#        `(1+2j) == 1` proved (Python: False) and `if 3j:` proved the branch NOT
#        taken (Python: `bool(3j)` is True).            witnesses 1050-1052
#        REFUSED rather than made opaque, ON A MEASUREMENT: the whole repository
#        contains EXACTLY ONE complex literal.
#
#   **AND ONE FOUND, SCOPED AND LEFT OPEN: #42.** `x = 1; if x is True: return 7`
#   proves `\result == 7` while Python's `1 is True` is False (and `x == True` is
#   CORRECT, which localizes it to `is`). Module 5 collapses `ast.Is` to `==` and
#   Module 6 int-encodes `bool`, so the two become one operator on a bool literal.
#   NOT closed: a blanket refusal breaks the mirror (94 sites, twelve of them the
#   tri-state `classify(...) is not False` idiom inside the mirror's own
#   `module6_whyml/functions.py`), and the type-directed version is an
#   UNDER-APPROXIMATION — the exact mistake #39 and #41 were about. Fully scoped in
#   `getting-better/open-routes/route42-is-bool-singleton.md`, with the reopening
#   capability named: GIVE THE IR A DISTINCT `is` OPERATOR.
#
# ## THE ONE LESSON, and it is worth more than the three routes
#
# **A REFUSAL IS ONLY AS SOUND AS THE RESOLUTION IT KEYS ON, AND AN ERASURE IS ONLY
# AS SAFE AS ITS LEAST-CHECKED CONSUMER.**
#
#   * #38 was written as "refuse when I can SHOW this is a context manager". The
#     correct shape is "refuse unless I can SHOW this is modelled". The enumeration
#     of ways to NAME a value is open-ended; the enumeration of MODELLED forms is
#     not. #39's fix is a whitelist and the mirror's 52 `with` sites pass it.
#   * #25/#26/#27 patched the CONSUMER that had been demonstrated (the guard).
#     Route #41 shows the erasure is decidable under EVERY int operator, so the
#     value itself has to stop being a literal. Witness 1044 (`x < 1`) exists
#     precisely to show that an equality-only patch would have been the same
#     mistake one step later.
#   * The fix that worked TWICE is the same one: **make the value OPAQUE, not the
#     consumer refused.** `val function pycsl_ellipsis : int` and per-name
#     `val function pycsl_erased_<x> : int`, both with NO defining axiom, close ten
#     shapes between them and refuse nothing that merely holds or passes the value.
#     PER-NAME MATTERS: one shared constant would let the model prove `x == y` for
#     two distinct erased locals — one unsoundness traded for another.
#
# ## THE TWENTY-THIRD PLANE MAKES THAT SHAPE MECHANICAL
#
# `bin/check-constant-fallthrough.py` (subsecond, static): every Module-6 lowering
# whose FALL-THROUGH is a Why3 CONSTANT. Routes #29, #30, #31, #40 and #41 are ONE
# shape and all five were found by hand, one at a time. MEASURED 8 DECIDING (each
# classified in the gate's baseline) / 10 INERT (`return ""` — not a Why3 term, so
# a syntax error at the use site rather than a decision). It fails on a STALE
# baseline entry too, which is the half that keeps a ratchet honest. Negative-tested
# three ways. **Stated limit: a constant returned from a GUARDED branch mid-handler
# is NOT a fall-through and is not counted** — routes #22/#24 lived there, and the
# instruments for those are `check-getattr-erasure` and `check-computed-rhs-erasure`,
# which watch the real emission.
#
# ## THE MEASUREMENT LESSON, and it is the one to carry
#
# **RUN THE WHOLE SUITE, AND READ THE NEW FAILURES AS EVIDENCE ABOUT THE FIX, NOT AS
# NOISE.** Route #40 landed with five witnesses behaving, a ZERO corpus byte-diff,
# three whole-file re-proofs at exactly their historical goal counts, and every gate
# green. It was still HALF A FIX. The only instrument that could see the other half
# was the full reference suite, and what it produced was not a failure of route #40
# but a COMPLETENESS regression — `python-reference/0041` — whose cause was that the
# test had been passing BY ACCIDENT all along. A targeted battery cannot find that
# shape, because the shape is "something that used to be true for the wrong reason".
#
# The corollary, from `python-reference/0209`: **a reference driver that PASSES
# WITHOUT THE CONSTRUCT IT NAMES BEING MODELLED is not evidence of anything.** 0209
# is "the async with statement" and its `\result == 0` was true for reasons entirely
# unrelated to `async with`. The suite cannot tell you that; only reading the driver
# can. It is now `# pycsl-expected: FAIL`.
#
# ## WHAT TO DO FIRST
#
# 0. **OPEN ROUTE #42 IS SITTING IN `getting-better/open-routes/` WITH ITS
#    REPRODUCERS AND ITS BUILD.** `<int> is True` / `is False` proves a contract
#    false of the program. The build named there — a DISTINCT `is` operator in the
#    IR instead of Module 5's collapse to `==`, plus a return type for intra-module
#    calls — also unblocks the object-identity shapes (`[1] is [1]`, `C() is C()`),
#    which today fail closed only BY ACCIDENT on a Why3 type error. This is the
#    single best-scoped item in the file.
#
# 0b. **THE VACUOUS-DRIVER POPULATION IS NOW MEASURED, AND IT IS 116.**
#    `bin/check-vacuous-drivers.py` (the twenty-fourth plane, built this window)
#    reports **116 of 2187 annotated `python-reference` functions (5%) and 9 of 867
#    in `pycsl-reference` (1%)** whose contract follows from their tail `return`
#    alone — so their PASS says nothing about the construct they are named for. The
#    window found TWO of them by ACCIDENT (`0209` "the async with statement" and
#    `0044` "numbers.Complex"), each as fallout from an unrelated fix, and each had
#    been hiding a live defect. THE LIST IS THE WORK ITEM: run the gate with
#    `--verbose` and give each driver a contract that mentions what it tests. Every
#    one you fix lowers the ratchet, and the ones that then FAIL are the next routes.
#    The proxy is conservative in one direction only, so 116 is a lower bound.
#    **AND THE SHARPER NUMBER IS WORSE: 89 + 47 of those are EMPTY PLACEHOLDERS** — a
#    docstring and a single `return <literal>`, exercising nothing.
#    `python-reference/0034` is "Integer literals" and its whole body is
#    `"""Ref 2.6.1: Integer literals."""; return 0`. THE HEADLINE
#    "3178/3197 PASSED" IS PADDED BY EXACTLY THAT MANY. State it plainly when you
#    quote a pass rate: THE SUITE'S NUMBER IS A LOWER BOUND ON HOW MUCH IS UNTESTED,
#    NOT AN UPPER BOUND ON HOW MUCH IS TESTED.
#    **NINE ARE ALREADY DONE, so the shape of the work is on the record**: 0022, 0024,
#    0029, 0034, 0037, 0055, 0056, 0057 and 0062 were given real bodies and real
#    contracts, all nine prove, and PYTHON WAS RUN ON ALL NINE. The recipe is always
#    the same — THE CONTRACT DOES THE WORK THE `assert` COULD NOT, because a Python
#    `assert` is DROPPED by Module 6, which is exactly why the old bodies could have
#    contained anything at all. Ratchets are already lowered to 105 / 78 (ELEVEN
#    conversions: 0019, 0022, 0024, 0029, 0030, 0034, 0037, 0055, 0056, 0057, 0062).
#    ONE ATTEMPT WAS REVERTED RATHER THAN LANDED RED, and its diagnosis is the useful
#    part: **a contract over a FLOAT LOCAL does not type-check today**. `a = 1.5;
#    b = 1.5e0; if a == b: return 1` under `#@ ensures \result == 1` is rejected with
#    "This expression has type real, but is expected to have type int", and so is a
#    version that merely BINDS four float locals and returns an integer computed
#    without them. Fail-closed (a type error, never a false proof); a COMPLETENESS
#    gap in the float local's integration with the int return model. That is why
#    0035 "Floating-point literals" is still a placeholder.
#
# 1. **CONVERT THE "FAIL-CLOSED BY ACCIDENT" POPULATION INTO DESIGNED REFUSALS.**
#    This window ran ~100 probes; roughly a third of the ones that closed did so on
#    a Why3 TYPE ERROR or an `unbound ... symbol`, not on a refusal and not on an
#    unprovable goal. That is precisely the state route #29 was built to remove for
#    the array spec atoms ("fail-closed BY DESIGN rather than by an unrelated bug a
#    completeness fix could remove at any time"), and it is now the single largest
#    standing hazard. NAMED INSTANCES, all measured this window: a tuple/genexp
#    stored to a FIELD; `set()` and a dict literal in a guard; `frozenset`/`zip`/
#    `enumerate`/`iter`/`reversed`/`memoryview`/`sorted`/`map`/`filter`/`list`/
#    `tuple` bound to a local; a lambda local; a class-variable read (`c.k`); a
#    function-reference call (`k = h; k()`); `return (1,2)`; `if (1,2) == 0`;
#    a tuple-unpack target; `return` inside `finally`; a lemma resting on a
#    `\trusted` fact. Each is one `PIPELINE ERROR` away from being honest.
# 2. **THE MISSING-`use` FAMILY IS 17 FILES AND NONE OF THEM IS A MISSING `use`.**
#    Measured, not estimated: `why3 prove --type-only` over ALL 858 emitted
#    pycsl-reference modules gives SEVENTEEN failures and ZERO
#    `unbound type symbol 'map'/'array'/'matrix'`. My first text census claimed
#    21/16/15/13 files — all false positives from matching inside comments and
#    strings. USE THE TYPE CHECKER, NOT A REGEX. The seventeen are named in the
#    progress log; three of them (0560/0563/0575) are DELIBERATE negative tests.
#    The real remaining names are `iter_length` (0793/0794), `subscript_get` (0807),
#    `int_mem` (0639), `z_` (0303) and `a_len` (the branch-bound list sidecar).
# 3. **THE LAST SLIVER OF #36** is still parked and unchanged — read #45's note
#    before re-spiking; three approaches are already measured and refuted.
#
# ## SETTLED THIS WINDOW, DO NOT RE-DERIVE
#
# * **`@property` IS MODELLED FAITHFULLY.** `c.v` on a `@property` lowers to the
#   real call `(c__v c)`; a contract false of the getter correctly fails. It is a
#   capability, not a gap.
# * **ROUTES #32/#33 HOLD, and I checked the thing that would have unmade them.**
#   Witnesses 1013/1014 and three fresh pre-declared variants ALL fail on an
#   UNDECLARED SIDECAR (`unbound ... 'a_len'`) — the exact "looks like the tool is
#   sound here" shape. So I exercised the same fold logic with a sidecar that DOES
#   exist (a list built by `append` in both arms): the FALSE `len(a) == 2` fails,
#   the TRUE `len(a) == 3` PROVES, the FALSE `a[0] == 1` fails. The poisoning of
#   `_known_collection_sizes` is doing the work; `a_len` is a completeness gap.
# * **A `#@ lemma` CANNOT INJECT AN AXIOM.** `#@ ensures 0 == 1` on a lemma is not
#   proved — Why3 checks the lemma body. `#@ assert 0 == 1` fails too.
# * **THE FOUR STATEMENT KINDS WITH NO MODULE 5 HANDLER ALL REFUSE.**
#   `AsyncFunctionDef`, `AsyncFor`, `AsyncWith`, `TryStar` and `await` are all
#   `PIPELINE ERROR` at the front end, so `check-statement-block-coverage`'s
#   "4 kind(s) with NO Module 5 handler" line is a completeness note, not a hole.
# * **~100 further probes are listed in the progress log** across erased-value
#   equality/ordering/arithmetic, erasure-record bypass positions, dunder
#   protocols, Python-vs-Hoare semantics and the spec surface. All fail-closed.
#
# ## THE `None` RESIDUE — the one thing this window found and did NOT close
#
# `None` lowers to the literal `0` on exactly the same terms as `...` did, and has
# the same three exploits, ALL MEASURED at the window's parent commit:
#
#     x = None; if x == 0: return 7    ->  `\result == 7` PROVED.  Python: 0
#     x = 0;    if x is None: return 7 ->  PROVED.                 Python: 0
#     x = None; return x + 5           ->  `\result == 5` PROVED.  Python: TypeError
#
# **IT IS NOT CLOSED BECAUSE `None`-as-`0` IS LOAD-BEARING IN A WAY `...` IS NOT**:
# `NoneExpr -> "0"` is the Optional convention the union/carrier recognizers and
# every `is None` guard in the mirror are built on, so the opacity fix that worked
# for `...` would break the emitter wholesale. Under that convention the model is
# internally consistent; the defect is that a GENUINE int 0 is indistinguishable
# from `None`. REOPENING CAPABILITY: a tagged value model (the `pyconst_val`/hval
# ADT applied to plain int-typed locals) that can tell "denotes a Python int" from
# "denotes an opaque singleton". CLASSIFY IT AS [CORRECTNESS] TODAY — the value
# model genuinely cannot express the distinction — with the tagged-value-model
# build as the named capability that reopens it.
#
# **THE GENERAL SHAPE, which is the transferable part: A PYTHON SINGLETON MODELLED
# AS AN INTEGER LITERAL IS INDISTINGUISHABLE FROM THAT INTEGER INSIDE THE MODEL, SO
# EVERY COMPARISON AGAINST THAT INTEGER IS DECIDED THE WRONG WAY.**
#
# ## THINGS THAT COST ME TIME
#
# 1. **A HEREDOC TURNED `\result` IN A COMMENT INTO A CARRIAGE RETURN** and broke
#    `expressions.py`. Every probe then reported "closed" — because the pipeline
#    died with `UNEXPECTED PIPELINE ERROR: invalid syntax`. FAIL-CLOSED BY ACCIDENT
#    LOOKS EXACTLY LIKE FAIL-CLOSED BY DESIGN UNLESS YOU READ WHY. The probe loop
#    now prints the extracted reason next to every verdict, and no "closed" is
#    trusted until the reason has been read AND the opaque symbol has been seen in
#    the emission. Write patches with `r"""` or `\\`.
# 2. **A NESTED `def` INSIDE A REFUSAL BROKE `check-mirror-coverage` 550 -> 551.**
#    A new LIVE function has no mirror counterpart and the plane counts it. Found
#    only by running the FULL battery instead of the planes the change "should"
#    touch. Rewritten as an inline loop at each of its four uses.
# 3. **A REGEX CENSUS OF THE MISSING-`use` FAMILY WAS ENTIRELY FALSE POSITIVES.**
#    See item 2 above. The type checker is the instrument.
#
# ## STATE AT HANDOFF
#
#   metric            markers 456 / grep 481 / offset 25 — UNCHANGED across all
#                     three routes, their residues and the new plane. A refusal and
#                     an opaque value both cost the trust surface nothing.
#   corpora           pycsl-reference: byte-diff against the worktree-at-HEAD set is
#                     the FOURTEEN NEW WITNESSES AND NOTHING ELSE. Zero pre-existing
#                     emission moved, across all three routes.
#   mirror            emission moves in exactly THREE files by exactly FOUR lines:
#                     `val function pycsl_ellipsis : int` declared in
#                     Module5_IREmitter.mlw and pure_ast.mlw, `visit_Constant`'s
#                     guard going `!value = 0` -> `!value = pycsl_ellipsis` (MORE
#                     faithful than what it replaced), and
#                     `val function pycsl_erased_map_prefixes : int` declared in
#                     statements.mlw (no body moved). ALL THREE RE-PROOFS WERE RUN.
#                     `Module5_IREmitter` rc=0 **2109 Valid / 0 bad** and `pure_ast`
#                     rc=0 **3372 Valid / 0 bad**, each EXACTLY the goal count
#                     recorded for it at #45 — and `pure_ast` is the one carrying a
#                     real body change, so it is the re-proof that had something to
#                     say. `statements.py` was still running at handoff; its change
#                     is a single UNUSED `val function` declaration, which cannot
#                     move a VC. Logs + rc files: `getting-better/proofs46/`.
#   mirror L3-tc      53/53 (106 hits over 53 files), re-measured after every route
#   fidelity          check-self-annotate-sync + self-annotate-mirror-check output
#                     BYTE-IDENTICAL to HEAD at every step (the pre-existing
#                     `_handle_var_expr` / `_handle_for_stmt` pair, unchanged)
#   planes            ALL TWENTY-FOUR rc=0, two of them new this window
#                     (constant-fallthrough, vacuous-drivers). mirror-coverage 550/41 ·
#                     trusted-raises-honesty 68 · dropped-mutation 0/51/11/0 ·
#                     emitted-vacuity 8 known · computed-rhs-erasure 1/0 ·
#                     bespoke-model-drift 27 · ir-field-coverage 4 ·
#                     statement-block-coverage 3 · getattr-erasure 0/7/19 ·
#                     yield-erasure 0/2/1 · shadowed-selfcalls 14 ·
#                     clause-survival 2/853 · avatar-frame-parity 0/7 ·
#                     mirror-loop-annotations 330/5 · mirror-signature-drift 0 ·
#                     untrusted-emitted 861/845/0 · refusal-reachability 0 ·
#                     internal-crash-free 0 · constant-fallthrough 8/10 ·
#                     vacuous-drivers 116/9 trivial + 89/47 empty · doc-coherency OK
#   suite             **3178/3197, NINETEEN failures, ZERO XPASS — and the nineteen
#                     are EXACTLY #45's nineteen, test for test** (ten Rocq-replay
#                     tests that cannot execute in this opam switch at all, plus
#                     0700/0701 and python-reference 0043/0048/0079/0080/0082/0095/
#                     0110). Against #45's close, 3158/3177 with nineteen becomes
#                     3178/3197 with the SAME nineteen — TWENTY more tests discovered
#                     and every pre-existing outcome unchanged. Run THREE TIMES:
#                     3171/3192 (twenty-one — the run that FOUND route #40's
#                     residue), 3175/3194 and 3178/3197. The only names that ever
#                     moved are the two that fix and the `0209`/`0044` markings
#                     resolved. The suite re-runs its own failures serially, so none
#                     is load-induced. RUN FOUR TIMES in all; the last was after the
#                     nine driver conversions and cost nothing.
#   re-proofs         ALL THREE OWED WHOLE-FILE RE-PROOFS ARE IN, rc=0, ZERO bad
#                     goals: Module5_IREmitter 2109 Valid, pure_ast 3372 Valid,
#                     statements 17109 Valid. The first two are EXACTLY the counts
#                     recorded at #45. NOTHING IS OWED.
#   witnesses         1033-1052, TWENTY, every one PROVING a contract FALSE of its
#                     own program at its parent commit and failing closed at HEAD.
#                     The witness-subset suite (`--pycsl --start-at 1000`) is 47/47
#                     with ZERO XPASS, and the three POSITIVE controls pass: 1034
#                     (a file with no CM class, so #39's whitelist is not armed and
#                     the 33 `with <lock>` critical sections are untouched), 1031
#                     (the `@contextmanager` generator #38 deliberately left) and
#                     1029 (a non-jumping `try ... else`, #33's kept capability).
#   docs              `docs/pycsl-translational-reference.md` §T.5.10b REWRITTEN (the
#                     `with` refusal restated as the whitelist it now is, with both
#                     bypasses named), plus new §T.5.12d (the `...` literal) and
#                     §T.5.12e (an erased local is opaque on every read).
#
# ==========================================================================

# ===================== START HERE — #45 -> next window =====================
#
# **TEN ROUTES FOUND, ALL TEN CLOSED, AND EVERY ONE OF THEM PROVED A CONTRACT
# THAT IS FALSE OF ITS OWN PROGRAM.** `getting-better/open-routes/` holds NO open
# route at handoff. Six of the eight are ORDINARY PYTHON in the
# DEFAULT `hoare` model with no flags — not spec atoms, not heap models, not
# mirror-internal shapes.
#
#   #29  `\is_sorted` / `\array_eq` / `\permutation` (and `\sum`, `\length2d`,
#        `\valid2d`) erased to `ensures { true }` under `--memory-model
#        typed|store`. A DESCENDING array proved sorted.        1004-1010
#   #30  an UNINTERPRETED `match` pattern lowered to an irrefutable arm; three
#        mechanisms, one mistake. `case [1,2]:` on an int took the arm. 1011-1012
#   #31  `if <list local>:` was `true` for EVERY list. `[]` is FALSY.   1015-1016
#   #32/#33  the `len()` and element constant-folds were BRANCH-blind.  1013-1014
#   #34  the same folds were MUTATION-blind. `a = [5]; a[0] = 9; return a[0]`
#        proved `\result == 5`. Five shapes.                            1017-1022
#   #35  `x = 0 or 5` proved `x == 1`. Python's `and`/`or` return an OPERAND.
#        SIXTEEN mirror re-proofs paid: 62428 Valid, 0 bad.             1023-1024
#   #36  `i = 0; for i in range(3): pass; return i` proved 0. Python 2. The
#        SEQUENCE half (`for x in a`) proved it too and is closed as well, at zero
#        emission cost in both halves.                                1025-1027
#   #37  a `try ... else:` whose ELSE BLOCK RETURNS was DROPPED — the emission had
#        no trace of it. The TRYFINAL ratchet COUNTED the drop.       1028-1029
#   #38  a `with` over a user context manager dropped the WHOLE protocol; the
#        statement does not even reach the IR. CTXBIND counted the OTHER half.
#                                                                     1030-1031
#
# ## FIVE INTERNAL CRASHES ON REFUSAL PATHS, all fixed, and now a gate for them
#
# The window opened on ONE diagnosed crash (`0540`) and closed with FIVE:
#   * `0540` — an IR-KEY COLLISION reached before the refusal (`type_params`
#     written by two producers with two incompatible shapes).
#   * an unknown `#@ proof` citation — `PyCSLIRError` never imported in
#     `module6_whyml/preamble.py`.
#   * python-reference 0202 / 0203 / 0204 — `pure_ast.parse` raises
#     `PyCSLSyntaxError`, a subclass of the BUILTIN `SyntaxError` and not of
#     `PyCSLError`, so it walked past `main`'s handler.
# All five were found the same way: **RUN A CONSTRUCT THAT IS SUPPOSED TO BE
# REFUSED AND READ WHAT ACTUALLY COMES OUT.** The reason they survived is
# structural: a `# pycsl-expected: FAIL` driver passes the reference suite whether
# it refuses cleanly or dies on an `AttributeError`, so the population most likely
# to crash is exactly the one the suite cannot inspect.
#
# TWO GATES NOW COVER THEM. `bin/check-internal-crash-free.py` (hard 0, 960
# pycsl-reference drivers in 34s) is the behavioural one and it found the last
# three the hour it was built, by being pointed at the OTHER corpus — do that
# after any front-end change, it is a two-minute one-off. Measured clean over the
# mirror (53) and `src/pycsl_lib` too. `bin/check-refusal-reachability.py` (hard 0)
# is the static half: a `raise PyCSL*Error` whose name is unbound where it is
# raised.
#
# The `#@ proof` probe also answered the trust question behind the whole bridge,
# which is worth more than the fix: A CITATION CANNOT INJECT AN ARBITRARY AXIOM.
# The body comes from a FIXED IN-EMITTER registry of 78 entries, not from the
# cited `.proofs/` directory, so a driver author cannot make their own Rocq file's
# statement into a Why3 axiom. That matters because the ten Rocq-replay tests
# (0211-0220) cannot execute in this opam switch at all, so the replay half of the
# bridge is unexercised and the registry half is carrying the trust meanwhile.
#
# ## THE TWENTIETH PLANE, and the instrument mistake it made TWICE
#
# `bin/check-statement-block-coverage.py` took three versions. V1 searched the
# handler's own source: ten hits, seven false, because Module 5 DELEGATES
# (`_py_stmt_for` is one line). V2 unioned the source text of every transitively
# reachable method — and COULD NOT FAIL: renaming `stmt.body` to `stmt.XbodyX`
# inside `_py_stmt_with` left it GREEN, because `.body` occurs in some other
# delegate. THAT IS #44's OWN FIRST ir-field-coverage MISTAKE ARRIVING DISGUISED
# AS THE FIX FOR V1's FALSE POSITIVES. V3 carries the NAME OF THE STATEMENT
# PARAMETER through delegation and is negative-tested twice, each time for the
# right reason. If you build a coverage gate, negative-test it BEFORE you trust
# the number it prints, and be suspicious of a fix whose effect is to make a gate
# report fewer hits.
#
# ## THE RATCHET LESSON, and it is the biggest thing this window learned
#
# **COUNTING A DROP IS NOT ESTABLISHING THAT IT IS SAFE.** Routes #37 and #38 were
# both sitting under a GREEN ratchet that had been counting them, or counting the
# harmless half of them, for two windows:
#   * `TRYFINAL = 10` counted "a `try/else` whose block is not emitted". Route #21
#     had ALREADY proved, for the `finally` half of the SAME counter in the SAME
#     handler, that such a drop can be exploitable — and refused it. The `else` half
#     was left counted.
#   * `CTXBIND = 51` counts "`with ... as X` — the binding is not read". The binding
#     is the VISIBLE half; the PROTOCOL CALLS are the half that carries the state
#     change, and nothing counted or established those.
# Every remaining ratchet deserves the same treatment. The unprobed ones are
# `yield-erasure` 2, `getattr-erasure` UNKNOWN 19, `shadowed-selfcalls` 14,
# `trusted-raises-honesty` 68, `computed-rhs-erasure` 1, `clause-survival` 2,
# `avatar-frame` INHERITED 7, `mirror-field-parity` 7 and `ir-field-coverage` 4.
#
# ## THE WINDOW IN ONE LINE
#
# Ten unsoundness routes, all closed and all witnessed; five internal crashes on
# refusal paths, all fixed; two gate blind spots that had hidden every corpus file
# numbered 1000+ from BOTH the byte-diff and the reference suite; three new planes;
# sixteen whole-file mirror re-proofs paid at 62428 Valid and zero bad goals; and
# the `\trusted` metric UNCHANGED at 456 throughout, because not one of these fixes
# needed a new trust stub.
#
# ## WHAT TO DO FIRST
#
# 1. **THE LAST SLIVER OF #36.** A loop over a NON-int sequence, or one whose
#    target carries a non-int type, still leaks the pre-loop value. The two closed
#    halves pin BOTH types before writing back — the target is in none of the
#    non-int local classes AND the iterable is a `list`-typed formal parameter (or
#    the loop is index-valued). To go further you need the outer ref's DECLARED
#    WhyML type at the binder, which it does not have. MEASURED, so you do not
#    repeat them: an unconditional write-back is mirror L3-tc 51/53, an `any int`
#    havoc 52/53, "restrict to targets not assigned elsewhere" 51/53 and four
#    emissions moved, and a REFUSAL breaks 14 of the 53 mirror files outright.
#    AND BEWARE `_current_array1d_params`: it is EMPTY at the binder for a plain
#    `a: list` parameter, so a condition keyed on it never fires while every plane
#    stays green and the exploit keeps proving.
# 2. **THE MISSING-`use` FAMILY, and it is coupled to #29.** `unbound type symbol
#    'array'` / `'matrix'` / `unbound function or predicate symbol 'String.length'`
#    are one bug: the emitter writes a term needing a Why3 theory into a module
#    that never pulled it. #44 fixed ONE instance. **Those unbound symbols were the
#    only thing standing between three erased spec atoms and a live false proof** —
#    they are refused now (#29), so the completeness work is finally safe to do.
#    Doing it in the other order would have shipped a soundness regression as a bug
#    fix.
# 3. **RUN THE LANGUAGE CENSUS BEFORE THE EMITTER CENSUS.** See below.
#
# ## THE METHOD THAT PRODUCED FIVE OF THE EIGHT — it is cheap and it is different
#
# **ASK WHAT PYTHON DOES THAT A HOARE MODEL MIGHT NOT, not what the emitter falls
# through to.** The emitter census finds ERASURES; the language census finds
# MISSING SEMANTICS. A batch of six probes — object aliasing, `a = b = []`,
# simultaneous tuple swap, `or`/`and` value semantics, the loop-variable leak,
# augmented list assignment through an alias — produced #34, #35 and #36 in about
# thirty minutes, after four census passes over Module 6 had produced none of them.
# WRITE THE PROGRAM, RUN IT IN PYTHON, AND PUT A CONTRACT ON IT THAT CONTRADICTS
# WHAT PYTHON PRINTED. Forty-odd such probes are in `scratchpad/p2/`; the ones that
# came back fail-closed are listed in the progress log so nobody repeats them.
#
# The emitter census still works and produced #29/#30: run the SHAPE as a QUERY
# over the whole tree instead of reading handlers. `scratchpad/lit_census2.py`
# (every bare `return "<literal>"` in Module 6 — 39 functions, 63 returns) and
# `scratchpad/vs_census.py` (every `self._value_semantic` gate) are reusable, and
# both tell you the search was EXHAUSTIVE, which reading never can.
#
# ## TWO GATES HAD THE SAME BLIND SPOT AND BOTH ARE FIXED
#
# `bin/byte-diff-sweep.sh` and `bin/run-reference-tests.sh` both globbed `0*.py`.
# The corpus crossed 1000 in #44, so **route #28's own witnesses had never been
# byte-diffed and had never been RUN**, and neither would any witness added after
# them. Both now glob `*.py` with a zero-input guard, each negative-tested against
# an empty tree. Suite discovery 3144 -> 3171. This QUALIFIES #44's headline:
# "3124/3144 with ZERO XPASS" was true of the files the harness could see.
#
# ## THE PLACEMENT LESSON, which decided the cost of three separate routes
#
# **A FIX PLACED WHERE THE DEFECT IS VISIBLE IS NOT NECESSARILY WHERE THE DECISION
# IS MADE, AND THE DIFFERENCE IS MEASURED IN WHOLE-FILE RE-PROOFS.**
#   * #31's first version put the refusal where the old `return "true"` was and
#     broke the mirror's own emission — because that branch PREEMPTS the faithful
#     `Array.length <> 0` branch below it, which is exactly why `true` was answered
#     where a faithful length already existed.
#   * #30's first version raised at the two Module 6 sites; both are `\trusted`
#     mirror stubs, so `check-trusted-raises-honesty` went 68 -> 71 and FAILED.
#     Rewritten as a POISON MARKER turned into a refusal by
#     `pycsl.py::_run_pipeline` — which already raises and is already in that
#     plane's population — it costs the trust surface nothing. The markers are also
#     UNBOUND WHY3 SYMBOLS (verified with `why3 prove --type-only`), so an emission
#     that escaped the check is REJECTED rather than proved: defence in depth by
#     construction.
#   * #36 went from "fourteen re-proofs" to "zero" purely by narrowing WHERE the
#     write-back fires.
#
# ## THE PRICE OF A MODULE 6 LOWERING CHANGE, now a measured quantity
#
# Route #35 moved 16 of the 53 mirror emissions. All sixteen were re-proved:
# **rc=0 everywhere, ZERO bad goals, 62428 Valid, 8h18m wall at two concurrent**
# (`getting-better/proofs45/`). Every file with a previously recorded goal count
# came back at EXACTLY that count — expressions at #43's 20125, stmt_control_flow
# at #44's 12294, Module5_IREmitter 2109, pure_ast 3372. A cost/scale boundary of
# this size is payable inside one window; it is no longer a reason not to try.
#
# ## THREE THINGS THAT COST ME TIME
#
# 1. **A PROBE THAT FAILS IS EVIDENCE ABOUT THAT PROBE.** Two attempts at #32
#    failed for unrelated reasons — an array-bounds VC and an `unbound … 'a_len'` —
#    and both look exactly like "the tool is sound here". The route was three lines
#    of Python away.
# 2. **FAIL-CLOSED BY ACCIDENT IS NOT FAIL-CLOSED.** See item 2 above.
# 3. **A MEASUREMENT TAKEN WHILE ITS SUBJECT IS CHANGING IS NOT A MEASUREMENT.** I
#    left the reference suite running while editing `src/pycsl` and had to kill it;
#    later I killed a second run 27% in, on purpose, because the tree was about to
#    change. THE SUITE BELONGS AT THE END, on the final tree.
#
# ## SETTLED THIS WINDOW, DO NOT RE-DERIVE
#
# * `#@ assigns <region>` on a CONCRETE function is NOT a checked obligation: the
#   region clause is not emitted and WHY3'S INFERRED EFFECTS carry the frame. A
#   function declaring `assigns a[0..1]` and writing `a[2]` verifies, AND a caller
#   relying on the stale `a[2]` correctly FAILS. Wrong region = documentation
#   error, not a soundness hole. The `clause-survival` deficit on 0661/0662 is the
#   same benign kind.
# * `#@ \trusted` on a DRIVER's own function is an unpoliced frame, by design: a
#   stub declaring `assigns \nothing` while writing lets its caller keep the stale
#   value. That IS what `\trusted` means. The architecture in one sentence: for a
#   CONCRETE function the frame is INFERRED and conservative; for a
#   `\trusted`/`\abstract` one it is DECLARED and trusted.
# * Precondition obligations ARE enforced at call sites (probed four ways,
#   including `\forall` preconditions and class invariants).
# * `#@ no_exception` correctly refuses an unguarded division and an unguarded
#   index.
# * Loop-contract soundness: a false invariant, a non-decreasing variant, a missing
#   variant and a wrong `\old` all FAIL.
# * A Python `assert` is DROPPED by Module 6. Sound for partial correctness (the
#   model considers MORE paths than Python), and route #36's leak scan depends on
#   it — if Python asserts ever become real obligations, that exclusion goes too.
# * ~60 further language probes, all fail-closed, are listed in the progress log.
#
# ## STATE AT HANDOFF
#
#   metric            markers 456 / grep 481 — UNCHANGED across all eight routes
#   corpora           pycsl-reference: the only pre-existing emissions that moved
#                     are 0447/0453/0885/0887 (route #35), all four still prove.
#                     python-reference 2206/2208 with three moved, all three
#                     already red (0048 L3-tc, 0192/0196 XFAIL).
#   mirror            53/53 emitted, 53/53 L3-tc, and the 16 files route #35 moved
#                     are all re-proved. NOTHING IS OWED.
#   fidelity          2 DIVERGED — the pre-existing `_handle_var_expr` /
#                     `_handle_for_stmt` pair, unchanged
#   planes            all TWENTY-TWO rc=0 plus doc-coherency. Three are new:
#                     statement-block-coverage, refusal-reachability and
#                     internal-crash-free. The
#                     twenty-first, `bin/check-refusal-reachability.py`, is a HARD
#                     0 on a `raise PyCSL*Error` whose exception NAME is unbound
#                     where it is raised — a refusal that reports "UNEXPECTED
#                     PIPELINE ERROR" and delivers none of its message. The
#                     window found TWO crashes on refusal paths by hand (0540 and
#                     an unknown `#@ proof` citation); this makes the second shape
#                     exhaustive. The twentieth is:
#                     `bin/check-statement-block-coverage.py` asks of the FRONT
#                     END what `check-ir-field-coverage.py` asks of Module 6 —
#                     does the handler carry every SUB-BLOCK of a compound
#                     statement into the IR? Route #38 lived in that gap. Three
#                     baselined hits, all real, all currently refused elsewhere.
#   suite             3158/3177, ZERO XPASS (was 3124/3144 with 20 failures at
#                     #44; `0540` is fixed and 33 previously-invisible-or-new
#                     tests now run). The 19 that remain are #44's list minus
#                     0540: ten Rocq-replay tests that cannot execute in this
#                     opam switch at all, and nine named L3-tc/pipeline errors.
#                     All fail-closed. Log: `getting-better/proofs45/`.
#   witnesses         1000-1032 all behave as declared, ZERO XPASS, re-run at HEAD
#                     (33/33 on the `--start-at 1000` subset)
#   docs              `docs/pycsl-translational-reference.md` gained §T.5.12b
#                     (and/or value semantics), §T.5.12c (the loop variable),
#                     §T.5.13 (list-local truthiness and the two folds), the
#                     match-pattern partiality note and the array-atom heap-model
#                     note. THE DOCS WERE PART OF THE DEFECT in #29 and #30: they
#                     stated the value-model formula as THE lowering and were
#                     silent about the model in which it was erased.
#
# ==========================================================================

# ===================== START HERE — #44 -> next window =====================
#
# **THE INHERITED STATE WAS NOT WHAT THE HANDOFF SAID IT WAS, IN TWO PLACES.** Both were
# found by re-deriving rather than inheriting, and both are now fixed:
#
#   1. `o_scf.rc = 1`. #43's proof queue left 47 rc files; 46 are rc=0 and ONE is rc=1.
#      All 15 unproven goals sit in `controlflowstmtmixin___handle_try_stmt'vc` and every
#      one is a `termination` or `index in array bounds` sub-goal. CAUSE: route #21's
#      mirror sync copied the LIVE body over the mirror body and thereby DELETED NINE
#      `#@ loop invariant` / `#@ loop variant` lines. The live emitter carries no `#@`
#      annotations, so a verbatim body copy strips the mirror's silently. **Only the
#      whole-file proof can see this** — mirror-sync compares bodies MODULO annotations,
#      L3-tc sees types, byte-diff sees live files, vacuity sees emptiness, the marker
#      count sees `\trusted`. Six green planes, one 30-minute red one.
#      Now held by `bin/check-mirror-loop-annotations.py` (sub-second).
#
#   2. `avatar-frame INHERITED` is **7, not 1**, and the plane has been RED since
#      a3e74638. #43's three "agreeing" measurements all pointed `--emit-dir` at
#      directories with NO MIRROR EMISSIONS in them (a CORPUS emit dir contains no
#      `self__` avatar; two others held zero `.mlw`). The gate scanned 0 avatars, found 0
#      frameless ones, and printed a green 0 — which reads exactly like a tightening.
#      Restored to the measured 7 and the whole `--emit-dir` gate family is now guarded.
#
# ## SEVEN NEW UNSOUNDNESS ROUTES, #22-#28 — ALL SEVEN CLOSED
#
#   #22  `getattr(obj, "field")` on a DECLARED record field was erased to the DEFAULT
#        (or, for the 2-arg form, a fabricated 0). Proved `\result == 0` where Python
#        returns 7. CLOSED AS A CAPABILITY — the comment's own licence ("a field the
#        record DECLARES is present") turned into a machine check against
#        `_emitted_record_field_labels`. Witnesses 0991 (false) / 0992 (true).
#        It had also made ROUTE #21's OWN REFUSAL dead code:
#        `getattr(stmt, "finalbody", None)` on `TryStmt` lowered to `if (0 <> 0)`.
#   #23  An augmented store could VANISH. `_py_stmt_augassign` was `if/elif/elif` with NO
#        `else`. `self.items[0].v += 5` and `e.v += 5` both proved `\result == 0` where
#        Python returns 5. CLOSED: unsupported bases REFUSED, `p.f op= v` made a
#        CAPABILITY. `dropped-mutation` DROPPED **1 -> 0**. Witnesses 0993/0994/0995.
#   #24  A call whose CALLEE is not a plain name (`type(self)(...)`) erased to the LITERAL
#        `0`. CLOSED with an APPLIED `val opaque_dynamic_call`. `computed-rhs-erasure`
#        **2 -> 1**. Witness 0996.
#   #25  A GENERATOR EXPRESSION bound to a local and consumed in a guard:
#        `g = (i for i in [1,2,3]); if g: return 7` proved `\result == 0`. Witness 0997.
#   #26  A NON-EMPTY SET LITERAL, `s = {1,2,3}; if s:` — emitted `let s = ref 0 in` with
#        NO STORE AT ALL. Witness 0998.
#   #27  A NON-EMPTY TUPLE LITERAL, `x = (1,2); if x:` — emitted `x := 0`. Witness 0999.
#        #25/#26/#27 are ONE defect: a local whose initialiser the model cannot represent
#        is bound to the literal `0`, which is decidably FALSE in a guard while the Python
#        object is ALWAYS truthy. CLOSED by ONE refusal in `_to_bool`, placed first.
#        BOTH HOOK METHODS ARE `\trusted` IN THE MIRROR, so it cost no re-proof at all.
#        Byte-inert by an AST census that finds ZERO such boolean uses tree-wide.
#   #28  A MODULE-GLOBAL singleton field store `g.v = n` was a SILENT NO-OP: `g.v = 7;
#        return g.v` proved `\result == 0` while Python returns 7. It was never a
#        modelling limit — `g = C()` already emits `let g : c = { v = 0 }` — so it CLOSED
#        AS A CAPABILITY (witness 1001 proves the true result; 1000 is the false one).
#        Found by a mechanical census (`scratchpad/w9/census_noelse.py`): of 44 Module-5
#        handlers, THREE end in an `if/elif` chain with no `else`. `_py_stmt_augassign`
#        was #23; `_py_stmt_annassign`'s two drops were PROBED AND REFUTED; this was the
#        third. **Its mirror half is the structural rule firing live — see below.**
#
# ## THE RULE THAT FOUND #22, #24 AND #25 — use it first
#
# **AN ERASURE TO A LITERAL IS ONE `if` AWAY FROM A FALSE PROOF; AN ERASURE TO AN OPAQUE
# VALUE IS NOT. So probe an erasure by CONSUMING IT IN A GUARD, never by reading it.**
# This is sharper than "probe the erasure" and it was learned the hard way: for #24 the
# field-read probe (`o = type(self)(); return o.v`) FAILED, and I nearly wrote the site off
# as fails-safe. Only the truthiness test exposed it. The defect is never that the value is
# lost — it is that the model gets to DECIDE A BRANCH on a value it invented.
# `grep -n 'return "0"'` in `module6_whyml/expressions.py` lists the remaining candidates.
#
# ## THE THIRD RULE, and it cost me a wrong handoff entry
#
# **A PLAUSIBLE STORY THAT FITS THE EVIDENCE YOU HAVE IS NOT A FINDING.** I recorded five
# failing tests as a completeness regression — they document themselves as PROVING, they
# failed one-at-a-time on a quiet box, and "somebody slowed them down without updating the
# tests" fits all of that. It was wrong: the configured Alt-Ergo did not exist, so the
# suite had been running on one prover. What broke the story was BISECTING to the commit
# that INTRODUCED one of them and finding it failing there too — a test cannot regress
# before it exists. Twenty minutes of bisect against a day of the next window chasing a
# phantom.
#
# ## THE OTHER RULE, four instances in one window
#
# **A GATE THAT CANNOT DISTINGUISH "NOTHING IS WRONG" FROM "I LOOKED AT NOTHING" IS NOT A
# GATE.** This window alone: a refusal that never fired (#43's route-19 narrowing), a
# negative test whose `sed` deleted nothing, a DECLARED-pin that was unreachable by
# construction, and four planes that report green on an empty `--emit-dir`. Two of those
# four actively invite the mistake — `computed-rhs-erasure` prints "0 < ratchet — LOWER THE
# CONSTANT" and `emitted-vacuity` prints "known erasure(s) NO LONGER erased — REMOVE FROM
# KNOWN_ERASURES". All four now exit 2 below a minimum emitted-mirror count.
# **Always run the negative test, and check it fails for the RIGHT REASON.**
#
# ## THE TRAP #28 CAUGHT ME IN — read this before touching any Module-5 handler
#
# 25 converted mirror methods get their WhyML from a HAND-WRITTEN `_emit_<X>_bespoke`
# function keyed on the METHOD NAME, not from the generic lowering. I had already grepped
# `_emit_py_.*_bespoke` and SEEN `_emit_py_stmt_assign_bespoke`, then changed the live body
# and synced the mirror anyway. Result: mirror-sync GREEN, L3-tc GREEN, whole-file proof
# GREEN, mirror emission BYTE-IDENTICAL across all 53 — and the emitted model still read
# `else ()` where the source now appended a `FieldAssign`.
#
# **THE BYTE-IDENTICAL EMISSION IS THE TELL.** A real change to a body whose model is
# DERIVED from it MUST move the emission. If it does not, the model is hand-written.
# Now held by `bin/check-bespoke-model-drift.py`, which enumerates all 25 and fingerprints
# their bodies.
#
# ## EIGHT NEW PLANES
#
#     bin/check-mirror-loop-annotations.py          ratchet 330 lines / 5 files
#         Per-file floor on the mirror's IN-BODY `#@` directives (loop invariant/variant,
#         ghost, assert, check, reveal, label). A contract clause sits ABOVE the `def` and
#         survives a body copy; an in-body directive does not. Sound in one direction:
#         such a line is pure proof support, never a liability.
#     bin/check-getattr-erasure.py                  DECLARED 0 (PINNED) / ABSENT 7 / UNKNOWN 19
#         The route-#22 regression gate. Classifies every `_lower_getattr` fall-through by
#         WHY the field did not resolve. Drives the real emission (a static scan cannot
#         tell DECLARED from ABSENT). UNKNOWN 19 = objects of type `Any`/`object`/non-record
#         mixin, where neither presence nor absence is establishable — not demonstrated
#         exploitable, not sound by argument either, so held by a ratchet.
#     the zero-input guard   in avatar-frame-parity, yield-erasure, computed-rhs-erasure
#                            and emitted-vacuity (see above)
#     bin/check-bespoke-model-drift.py              25 methods / 23 hand-written models
#         The one failure mode where every green light is real and the conclusion is still
#         wrong. Fingerprints each bespoke-modelled body and names the `_emit_..._bespoke`
#         function that must move with it. Negative-tested by replaying #28's mistake.
#     bin/check-ir-field-coverage.py                4 unread fields (all read + classified)
#         THE CAMPAIGN'S OWN DEFECT CLASS, MADE MECHANICAL: "a lowering reads some of a
#         node's fields and silently drops the rest". 101 IR classes, 224 fields; for each,
#         does its Module 6 handler ever mention the field? The 4 hits are 3 location
#         fields (the ADT carries no location payload) and `allow_iteration_mutation`
#         (a Module-4 directive). **It has a stated blind spot: 25 classes lowered inside
#         the `t == "<Kind>"` dispatcher are NOT checked.** A fallback for them was built,
#         produced ten hits, ALL TEN were false positives (three refuted by end-to-end
#         probes), and it was REMOVED — see the note in the script before rebuilding it.
#     bin/check-swallowed-exceptions.py             141 -> 137 static, 4 firing (baselined)
#         The first BEHAVIOURAL plane: it watches what the emitter actually CATCHES during
#         a real 53-mirror emission (`sys.monitoring` EXCEPTION_HANDLED), not what the
#         source says. A broad `except Exception:` that swallows turns an INTERNAL ERROR
#         into a recognizer decline, and a decline falls through to the generic lowering —
#         which routes #22/#24 showed can be an ERASING one. It found FOUR recognizers
#         catching `Exception` where they meant `_PVWBail`; those are now tightened, after
#         measuring over BOTH corpora that they never catch anything else.
#     bin/check-trusted-raises-honesty.py           ratchet 68 SILENT / 2 declared
#         The sibling question frame-honesty never asked: is a `\trusted` stub honest about
#         what the live body RAISES? An emitted `val` with no `raises` tells Why3 the call
#         has ONE exit path. PROBED and classified as a TRUST SURFACE, not a route — the
#         obvious exploit correctly FAILS, because such a claim is the REVIEWER's, which is
#         what `\trusted` means. A number to publish and shrink.
#
# ## HOW TO RUN THE PLANES (all of them need the opam PATH)
#
#     export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
#     ./scratchpad/w9/mirror_emit.sh <repo> <outdir>     # 53 mirror .mlw, --import-path
#     ./scratchpad/w9/l3sweep.sh <out.txt>               # L3-tc 53/53 (each file prints 2)
#     bash bin/byte-diff-sweep.sh <outdir>               # pycsl-reference, 820
#     bash scratchpad/w8/pyref_sweep.sh <repo> <outdir>  # python-reference, 2142 + 75 refused
#     bin/check-emitted-vacuity.py --emit                # WITHOUT --emit it now exits 2
#     bin/check-avatar-frame-parity.py --emit-dir <MIRROR emit dir>   # NOT a corpus dir
#
# A worktree at the parent commit is the negative-test rig, and every witness this window
# was flipped against one: `git worktree add -f --detach /tmp/pycsl-baseNN <parent>`, then
# symlink `.venv` into it.
#
# ## SETTLED THIS WINDOW, DO NOT RE-DERIVE
#
# * `suite.rc`/`suite2.rc` = 1 in `scratchpad/w7`: those were `run-reference-tests.sh` runs
#   with 102 of 3123 failing, and the failures are Rocq-required tests (0211-0220) plus a
#   proof tail — i.e. the opam PATH was missing (instrument fact (cd)). Identical logs,
#   4.5h apart. Re-run cleanly this window; see `scratchpad/w9/suite_full.log`.
# * A `%` OPERATOR in a LIVE function's source makes the self-annotation preamble emit
#   `pycsl_div`/`pycsl_mod` into EVERY mirror that imports that module. Use f-strings.
# * `type(t).__name__` in a diagnostic lowers to `int_to_string (get___name__ (py_type t))`
#   and `t` is an `emit_ir` there — an L3-tc rejection. Use a literal.
# * CLOSING AN ERASURE UNCOVERS A TYPE ERROR. Making `getattr(stmt,"finalbody")` faithful
#   immediately produced an L3-tc rejection, because `finalbody` is an `array emit_ir` and
#   the int-truthiness form `x <> 0` is ill-typed on it. The repair and the erasure fix
#   must land in the same increment.
# * The metric has not moved: **markers 456 / grep 481** across all four routes. Three of
#   the four were closed WITHOUT a re-trust, two of them as capabilities.
#
# ## CLOSING STATE OF #44 — every plane green, and here are the numbers
#
#   metric                 markers 456 / grep 481 — UNCHANGED across all seven routes.
#                          Three closed as CAPABILITIES, none needed a re-trust.
#   proofs                 6 of 6 rc=0, zero bad goals: stmt_control_flow 12294,
#                          Module5_IREmitter 2109, pure_ast 3372, ir_resolve 793,
#                          frontend/__init__ 684, pycsl 735. The MANIFEST says those six
#                          are the complete set (all 53 mirrors emitted from a worktree at
#                          `afbc6803` and byte-diffed against HEAD -> exactly six moved).
#   corpora                pycsl-reference 820/820 and python-reference 2142/2142
#                          byte-identical to the pre-#44 tree, apart from 0611/0612
#                          (route #28) and the eleven new witnesses. Refusal set identical.
#   mirror L3-tc           53/53
#   fidelity               2 DIVERGED — `_handle_var_expr`, `_handle_for_stmt` — the
#                          pre-existing pair, byte-identical to #43's baseline log
#   ratchets               dropped-mutation 0/51/10/0 (DROPPED 1 -> 0) ·
#                          computed-rhs 1/0 (2 -> 1) · avatar-frame 0/7 (the honest
#                          number) · getattr-erasure DECLARED 0 PINNED / 7 / 19 ·
#                          bespoke-model-drift 27 · mirror-loop-annotations 330/5 ·
#                          trusted-raises 2/68 · mirror-coverage 550/41 · yield 2 ·
#                          shadowed 14 · frame-honesty 0/1 and 0/94 · clause-survival 2
#   conformance            core 38/0, front-end 38/0, determinism 10/10
#   vacuity (--emit)       no NEW erasure
#   reference suite        **3124/3144 — up from 3042/3144. 102 failures -> 20, ZERO XPASS.**
#                          ZERO XPASS is the number that matters: the harness used to
#                          report an expected-FAIL test that PROVED as a PASS, so all 241
#                          negative witnesses — including every route witness this campaign
#                          has written — were unenforceable. Fixed; now XPASS is red and
#                          counts as a failure, and the current measurement is zero.
#                          The 102 were PRE-EXISTING and identical test-for-test to #43's,
#                          and no handoff in this campaign had said the suite was red.
#                          82 of them are now fixed:
#                            64  the whole `stdlib/ctypes` family, which needed
#                                `--allow-unverified-imports` in its flags line. The tests
#                                are about the ctypes STUB CONTRACTS; the deny-list has its
#                                own dedicated test (`pycsl-reference/0400`).
#                             4  the json stub tests — `json.dump(x)` called with one arg
#                                where `fp` has no default and the result returned into an
#                                `int`; `json.loads` raising JSONDecodeError and TypeError
#                                that the driver never declared. The STUBS were right.
#                             4  base64/codecs `encode` — an EMITTER bug (an abstract op
#                                declaring `array int` with no `use array.Array`, because
#                                `needs_array` is computed before any body is emitted) plus
#                                a driver declaring `-> int` for a bytes return.
#                            10  the missing prover (see the retraction below). Nothing in
#                                the code was wrong with these at all.
#                          THE REMAINING 30, all diagnosed in `scratchpad/w9/fail_causes.txt`:
#                            10  `Why3 Coq library not found` (0211-0220) — the
#                                `#@ proof rocq` bridge CANNOT BE REPLAYED in this
#                                environment at all, which means this campaign has never
#                                exercised it. Worth the next window's attention on its own.
#                             9  SMT timeout/unknown — **RETRACTED AND EXPLAINED.** I first
#                                recorded these as "a completeness regression nobody had
#                                recorded", because five of them say "STATUS — PROVES." in
#                                their own docstrings and they failed even one-at-a-time on
#                                a quiet box. THERE IS NO REGRESSION. `config/agents-config
#                                .json` and `_DEFAULT_PROVERS` named **Alt-Ergo 2.6.2** and
#                                this switch has **2.6.3**, so every DEFAULT run — the whole
#                                suite — proved with **Z3 ALONE**. TEN of the thirty
#                                failures pass once Alt-Ergo is present. Fixed, plus a loud
#                                banner when a configured prover does not resolve.
#                                What led me out of the wrong story was BISECTING: 0943
#                                fails at the very commit that INTRODUCED it, which cannot
#                                be a regression and therefore had to be the environment.
#                             1  `0540` — its docstring says it should be a PARSE ERROR and
#                                what it produces is `UNEXPECTED PIPELINE ERROR: 'str'
#                                object has no attribute 'get'`, an INTERNAL CRASH on the
#                                refusal path. Worth fixing on its own terms.
#                             9  L3-tc type errors and pipeline errors, individually listed
#                                (0700, 0701, python-reference 0043/0048/0079/0080/0082/
#                                0095/0110). Every one is fail-closed.
#
# ## THE THREE THINGS TO DO FIRST, NEXT WINDOW
#
#   1. **`0540`'s internal crash on the refusal path.** Its docstring says it should be a
#      PARSE ERROR for the un-implemented `#@ datatype Option[T]` syntax; what it produces
#      is `UNEXPECTED PIPELINE ERROR: 'str' object has no attribute 'get'`. A crash is only
#      fail-closed while nothing catches it, and the remaining L3-tc/pipeline failures
#      (0700, 0701, python-reference 0043/0048/0079/0080/0082/0095/0110) are the rest of
#      that list. Each is individually diagnosed in `scratchpad/w9/fail_causes.txt`.
#   2. **Probe with the guard rule.** `grep -n 'return "0"'` in
#      `module6_whyml/expressions.py` still lists ~12 literal-0 fall-throughs. Four of them
#      became routes #22/#24/#25/#26/#27 this window. Consume the value in an `if`, never
#      read it.
#   3. **Run `bin/check-bespoke-model-drift.py --list` BEFORE touching any Module-5 or
#      comprehension handler.** 27 mirror methods have hand-written models. Route #28
#      caught me editing one with the warning in front of me.
#
# ==========================================================================

# ===================== START HERE — #43 -> next window =====================
#
# ARRAY/MAP EXTENSION: **BANKED, 13/13.** (One qualifier: `o_pure2` confirms `pure_ast` at
# HEAD, because route #20 moved that emission afterwards. It is queued.)
#
# **TEN ROUTES FOUND THIS RELAUNCH (#12-#21), ALL TEN CLOSED.** Metric 451 -> 456.
#
# ROUTE #15 (constructor contracts) is CLOSED — it is the one that needed a BUILD rather
# than a refusal. Module 6 emits a checking-only `let <class>__init` carrying the declared
# clauses over the same record literal every allocation site builds; the inlining is
# untouched. **Mirror emissions moved: ZERO**, so the 53-file battery never arose.
# `bin/check-clause-survival.py` 4 -> 2, its own acceptance test. The three gates it needed
# — non-trivial clause, faithful constructor body, recognized parameter annotation — all
# came from measurement, and the two remaining deficits (0661/0662) go to 0 with the same
# value-model capability routes #13/#17/#18 need.
#
# ## THE THREE THINGS TO DO FIRST
#
# 1. **DRAIN THE PROOF QUEUE.** `scratchpad/w8/queue_{owed,final_pure,scf,irs}.sh` run
#    autonomously and write marker files into `scratchpad/w7/proofs/`
#    (`OWED_DONE` -> `FINAL_DONE` -> `SCF_DONE` -> `IRS_DONE`). Green so far, ZERO bad goals
#    in every one: a_expr(20125) a_m5(2088) a_pure(3373) o_desugar(18) o_ap(44) o_m3w(284).
#    If a relaunch finds them dead, re-launch with `scratchpad/w7/pr2.sh <mirror> <tag>`.
#
# 2. **PROBE A GREEN RATCHET.** Two of them were hiding live unsoundnesses this relaunch
#    (`CTXBIND = 50` -> route #20, `TRYFINAL = 9` -> route #21), each one probe away. What
#    is left un-probed: `yield-erasure`'s 2 and the two `_uses_pyast_parser`-gated no-op
#    candidates — all three need a MIRROR-INTERNAL false-contract probe, which does not
#    exist yet and is worth building.
#
# 3. **THE ONE VALUE-MODEL CAPABILITY THAT RETIRES FOUR THINGS AT ONCE**: a
#    length-carrying, REBINDABLE sequence local reopens route #13 (list mutators), #17
#    (list `del`) and #18 (array-local reassignment), AND threads a param-dependent
#    non-scalar constructor field faithfully, which takes `clause-survival` 2 -> 0. Four
#    recorded boundaries, one capability. It is the highest-leverage item left.
#
# ## A HARD PRECONDITION ON THE BIGGEST REMAINING MODEL UPGRADE
#
# Converting `_Unparser.__init__` (ONE marker; the whole class moves from the opaque
# `_pyobj_state` store to a CONCRETE RECORD, and 20 of the 21 remaining `_Unparser`
# `\trusted` stubs sit behind it) **MUST be done in the same increment as a
# context-manager protocol model, or the 24 `with self.block():` callers must be
# re-trusted.** Today `yield-erasure`'s 2 are unobservable ONLY because the emitted record
# is `type _unparser = {  }` — empty. Give the class real `_indent` / `_source` fields and
# the dropped indent/dedent tracking becomes a referenceable divergence in a file proved at
# 3373 goals. The conversion would otherwise turn an unobservable erasure into an
# exploitable one.
#
# ## THE METHOD THAT PRODUCED SEVEN OF THE TEN
#
# **Probe the thing with a prose soundness argument written beside it.** `grep` Module 6 for
# every site that emits `()` for a whole statement; take each ratchet's own description of
# its population and build the smallest program with that shape; then put a contract on it
# that is FALSE of the program and RUN Python to check. Routes #13, #16, #17, #18, #19, #20
# and #21 all came from a comment or a counter that asserted safety.
#
# ## THREE HABITS THIS RELAUNCH PAID FOR
#
# * **Ask what the instrument iterated over.** "13-file battery complete" was 10 of 13;
#   "avatar-frame 7" was the ratchet, not the measurement; `byte-diff-sweep.sh` covered 27%
#   of the corpus. Use `scratchpad/w8/pyref_sweep.sh` for the other 73%.
# * **`grep` the mirror before editing a live body.** The fidelity plane caught three
#   live/mirror desyncs here. When syncing: **copy the BODY, keep the mirror's SIGNATURE**
#   (a verbatim copy clobbered `val_ir: "ExprIR"` and stopped a file type-checking).
# * **Re-run the exploit probe after every narrowing.** Route #19's refusal silently never
#   fired once, because `_mutable_state_classes` holds `whyml_ident(name.lower())` and the
#   check compared the raw `self_type`. A refusal that never fires looks exactly like one
#   that works.
#
# ## TWO NEW PLANES THIS RELAUNCH — run them
#
#     bin/check-clause-survival.py --emit-dir <fresh emit dir>     ratchet 2
#         Does every `#@ requires`/`#@ ensures` the author wrote REACH the emission?
#         Sound in one direction: the emitter only ADDS clause lines. It found route #15.
#     bin/check-mirror-coverage.py                                 ratchets 550 / 41
#         How much of the LIVE emitter the mirror models AT ALL. 550 of 1820 live defs in
#         mirrored files (30.2%) have NO mirror counterpart, plus 41 unmirrored files.
#         **The `\trusted` count structurally cannot see these** — an absent function
#         carries no marker. Not an unsoundness; a limit on what "456" means, held by a
#         ratchet so it can only shrink.
#
# ## SETTLED, DO NOT RE-DERIVE
#
# The metric has no uncounted escape hatch in its scope (`\abstract`: 14 tree-wide, 0 in the
# mirror; `#@ assume` is not a keyword). UB-7.1's `_MUTATING_METHODS` was widened — it had
# been a fail-open masked by route #14's refusal. #34's frame-preservation fix still bites
# (re-probed). Argument binding, inheritance/override dispatch, chained comparison, walrus,
# the Module-5 handler field coverage, the Module5->Module6 IR-key boundary (111 tags), and
# clause survival for loop/class-invariant/assert/check directives are all CLEAN.
#
# ==========================================================================

# HANDOFF ADDENDUM 7 — #43: **THE ARRAY/MAP FRAME EXTENSION IS BANKED. 13 of 13.**

Every mirror whose emission the extension changed is rc=0 `Verification SUCCESS` with ZERO
bad goals: struct_format · ConcurrencyChecker · audit_proof · audit_proof_reverify ·
proof2why3/parser · types · Module6_WhyMLTranspiler · Module2_Parser · stmt_control_flow ·
statements · expressions (20125 Valid) · Module5_IREmitter (2088) · pure_ast (3373).

The relaunch inherited this battery described as COMPLETE and found it at **10 of 13** —
one run killed at its timeout, two never started. Every other plane was re-derived rather
than inherited: the changed corpus set recomputed from an 820-vs-820 emission diff against
13c4860b (exactly the 26 recorded files), all 26 re-proved fresh, every non-proof plane
re-run from the surface.

**THE ONE QUALIFIER, stated rather than buried:** twelve of the thirteen emissions are
byte-identical at HEAD; `pure_ast`'s moved afterwards under route #20, an independent later
change. `o_pure2` re-proves it at HEAD and is queued. Do not treat the two emissions as
interchangeable — instrument fact 12 is the whole reason this was tracked with a manifest.

## STILL IN FLIGHT (autonomous, `scratchpad/w8/queue_*.sh`, marker files in `w7/proofs/`)

    o_desugar  o_ap        route #16 sync / route #13 re-trust   -> then OWED_DONE
    o_m3w  o_irr  o_finit  o_m6t   route #12's one `raises` line + the statements sync
    o_stmts                        route #18 sync (3886 goals)
    o_pure2                        route #20 -> pure_ast at HEAD  -> FINAL_DONE
    o_scf                          route #21 sync (6426 goals)    -> SCF_DONE

Each writes only to `scratchpad/w7/proofs` and TMPDIR; none touches the repo tree.

# HANDOFF ADDENDUM 6 — #43, ROUTE #21, AND THE HEADLINE. **TWENTY-ONE routes enumerated
# across #33/#34/#43; TWENTY closed. This relaunch found TEN (#12-#21) and closed NINE.**
# Metric 451 -> 456, every +5 an honest re-trust or an honest new trusted stub.

## ROUTE #21 — the `TRYFINAL = 9` ratchet was also exploitable

    #@ ensures \result == 2                    <-- FALSE OF THE PROGRAM
    def f() -> int:
        x: int = 1
        try:     x = 2
        except ValueError:  x = 9
        finally: x = 3
        return x
    [+] Verification SUCCESS!                            (Python returns 3)

`_handle_try_stmt` reads `stmt.body` and `stmt.handlers` and neither `finalbody` nor
`orelse`. #33 emitted the `finally` in the one expressible case; the rest was counted and
left. THE CONTROLS LOCALISE IT: the same file WITHOUT handlers correctly FAILS, and
`try/except/else` correctly FAILS. Refused in Module 6's statement lowering. Witness
**0990**. Census 4 sites, the mirror's one is `\trusted`; both corpora byte-identical.
TRYFINAL ratchet 9 -> 10, the +1 being the witness itself.

## **TWO RATCHETS IN A ROW WERE HIDING LIVE UNSOUNDNESSES. THIS IS THE HEADLINE.**

`CTXBIND = 50` and `TRYFINAL = 9` were both reported GREEN by
`bin/check-dropped-mutation.py` on every run of this campaign, for windows. Both were
exploitable, and each took ONE probe to demonstrate. **A ratchet records that a population
has not GROWN. It says nothing about whether anything in it is EXPLOITABLE.** Every
non-zero ratchet in this project is now a list of un-probed candidates:

    dropped-mutation      1 DROPPED · 51 CTXBIND · 10 TRYFINAL · 0 DANGLING
    computed-rhs-erasure  2 rhs · 0 param          (probed this relaunch — faithfulness
                                                    gaps, not unsoundnesses)
    yield-erasure         2 suspension             ** NEVER PROBED **
    shadowed-selfcalls    14                       ** NEVER PROBED **
    frame-honesty         94 converted-total       ** NEVER PROBED **
    mirror-field-parity   7 known drift            ** NEVER PROBED **
    clause-survival       4                        (probed — all route #15)

**Start the next window by probing `yield-erasure`'s 2 and `shadowed-selfcalls`' 14.**
Take the ratchet's own description of the population, build the smallest program with that
shape, and put a contract on it that is FALSE of the program. Two ratchets, two routes, so
far.

## THE FIDELITY PLANE CAUGHT THREE LIVE/MIRROR DESYNCS THIS RELAUNCH

Every one from editing a live method that is CONVERTED in the mirror
(`desugar.reject_unmodelled`, `statements._emit_array_local_reassign`,
`stmt_control_flow._handle_try_stmt`). Two rules, both paid for here:
**copy the BODY, keep the mirror's SIGNATURE** (a verbatim copy clobbered
`val_ir: "ExprIR"` with `Dict[str, Any]` and stopped a file type-checking); and
**`grep` the mirror for the method before touching a live body.**

# HANDOFF ADDENDUM 5 — #43, ROUTE #20. **TWENTY routes enumerated across #33/#34/#43;
# NINETEEN closed. This relaunch found NINE (#12-#20) and closed EIGHT.** Metric 451 -> 456.

## ROUTE #20 — `with ... as v` was exploitable, and it was hiding inside a GREEN RATCHET

`bin/check-dropped-mutation.py` has reported `50 CTXBIND` on every run of this campaign, as
a tracked and accepted residue. **A number a gate reports as within its ratchet is not the
same as a number that has been probed.** It was a live unsoundness:

    class CM:
        #@ ensures \result == 7
        def __enter__(self) -> int:  return 7
    #@ ensures \result == 0                    <-- FALSE OF THE PROGRAM
    def f() -> int:
        v: int = 0
        with CM() as v:  return v
    [+] Verification SUCCESS!        (Python: 7; emitted `let v = ref 0 in v := 0; !v`)

`_py_stmt_with` reads `stmt.body` and the critical-section markers and NEVER reads
`stmt.items`. CLOSED with the `nonlocal_writes` shape — additive IR field `with_bindings`,
refused in Module 6's GENERIC emission so `\trusted`/`\abstract` stays exempt. A BARE
`with <lock>:` is untouched (it is a modelled CriticalSection); the refusal keys on `as`.

PRICE, every part measured before landing: ONE converted mirror method re-`\trusted`
(`pure_ast._Unparser.visit_Lambda`, reading a stale `buffer` — the only converted method in
the tree with the shape, census 62 sites); TWO `python-reference` syntax tests marked
`pycsl-expected: FAIL` (0093, 0191); the CTXBIND ratchet 50 -> 51, **and the +1 is the
witness itself**. Witness **0989**, negative-tested. Both corpora byte-identical apart from
the two newly-refused files; core AND front-end conformance 38/0 each — the new IR field
moved no golden.

## THE LESSON THIS RELAUNCH KEEPS PAYING

Four of the nine routes were found by asking what a number MEANT rather than whether it was
green:
  · "13-file battery complete" was 10 of 13 — the log's runner iterated a different list.
  · "avatar-frame INHERITED 7" was the RATCHET, printed by a gate that never printed its
    measurement. The measurement is 1.
  · "50 CTXBIND", green for windows — route #20.
  · `bin/byte-diff-sweep.sh`'s "820/820 byte-identical" covered 27% of the corpus.

**Ask what the instrument iterated over, and what the number it prints actually is.**

## PROOF STATE AT HAND-OFF

`a_expr` and `a_pure` were both still in their VACUITY phase, having finished PROVING with
ZERO bad goals (20125 and 3373 prover results, 12 live `why3` children).
`scratchpad/w8/queue_owed.sh` then runs the six owed re-proofs two at a time and writes
`scratchpad/w7/proofs/OWED_DONE`; `scratchpad/w8/queue_final_pure.sh` then re-proves
`pure_ast` at HEAD (route #20 moved its emission) and writes `FINAL_DONE`.

**Banking rule: the array/map extension needs `a_expr` rc=0 AND a pure_ast rc=0 AT HEAD
(`o_pure2`).** `a_m5` is already rc=0 with 2088 Valid and zero bad.

# HANDOFF ADDENDUM 4 — #43 FINAL AUDIT SUMMARY. **NINETEEN routes enumerated across
# #33/#34/#43; EIGHTEEN closed. This relaunch found EIGHT (#12-#19) and closed SEVEN.**
# Metric 451 -> 455, every +4 an honest re-trust or an honest new trusted stub.

## ROUTE #19 — `@mutable_state` turned a REJECTION into a silent no-op

    @mutable_state
    class C:
        #@ requires 1 not in s
        #@ ensures 1 not in s          <-- FALSE OF THE PROGRAM
        #@ assigns \nothing
        def m(self, s: Set[int]) -> None:  s.add(1)
    [+] Verification SUCCESS! All contracts formally proven.

The IDENTICAL class WITHOUT `@mutable_state` is REJECTED outright. CLOSED by turning the
source comment's own justification — "no contract here reads it" — into a MACHINE CHECK:
the exemption holds only while the mutated parameter is not NAMED in a contract clause.
Spelled in `_reset_function_state` because it is the one place holding both the contract
and the body AND is `\trusted` in the mirror, so it adds no field, no fidelity divergence
and NO emission change. Witness **0988**. Both corpora byte-identical.

**TWO NARROWINGS, BOTH CAUGHT BY MEASUREMENT, AND THE SECOND IS THE ONE TO REMEMBER:** the
class test first compared the raw `self_type` while `_mutable_state_classes` holds
`whyml_ident(name.lower())`, so the refusal SILENTLY NEVER FIRED. A refusal that never fires
is indistinguishable from one that works — only re-running the probe tells them apart.
**Re-run the exploit probe after every narrowing.**

## THE METHOD THAT PRODUCED #17, #18 AND #19 — start here next window

`grep` Module 6 for every site that emits `()` for a whole statement, then probe each with a
contract false of the program. 13 sites in `statements.py`; three were live unsoundnesses.
**Every one of the three had a comment beside it ASSERTING soundness.** A no-op lowering
with a prose soundness argument is the highest-yield thing to probe in this codebase.

Census outcome, so it is not rebuilt: 2 unsoundnesses (#17, #18) + 1 in the adjacent
expr-statement handler (#19) + 1 REFUTED (`_handle_sum_node_expr`'s `return "0"` — probed
under all four `--memory-model` choices, all correctly FAIL) + 2 that need a
MIRROR-INTERNAL probe (`statements.py:1634` `<emit_ir>[k] = v`, `statements.py:2252` the
four ASDL location stamps — both gated on `_uses_pyast_parser()`, unreachable from a corpus
file) + the rest structural.

## THE BYTE-DIFF PLANE COVERED 27% OF THE CORPUS

`bin/byte-diff-sweep.sh` sweeps only `pycsl-reference`. `python-reference` — 2217 tests,
2144 emitting — had never been byte-diffed. `scratchpad/w8/pyref_sweep.sh` closes it, and
every refusal this relaunch landed is byte-inert on BOTH corpora. **Run both from now on.**

## WHAT IS OWED, IN ORDER

1. **The proof battery** (addendum 3 lists all nine files). `a_expr` and `a_pure` were still
   in their VACUITY phase at hand-off — both had finished PROVING with ZERO bad goals
   (20125 and 3373 prover results) and were grinding the per-goal vacuity loop with 12 live
   `why3` children. **The array/map extension may be banked only when both are rc=0.**
   Instrument note: `pycsl.py`'s embedded vacuity loop is far slower than
   `bin/check-emitted-vacuity.py --emit`, which does the whole 53-mirror set in ~11 s.
2. **Route #15** — constructor contracts. Mirror-inert, two additive IR fields, 13 corpus
   re-proofs. `bin/check-clause-survival.py` 4 -> 0 is the acceptance test.
   **ITS RISKIEST ASSUMPTION IS ALREADY MEASURED.** The checking-only constructor function
   was hand-inserted into corpus 0706's real emission and run through Why3:
   `let c__init () : c ensures { result.x = 0 } = { x = 0 }` gives
   `Goal c__init'vc — Valid`, and that goal INCLUDES the record's class-invariant
   obligation; the same function with `ensures { result.x = 99 }` gives `Unknown`. It
   type-checks AND discriminates. Files: `scratchpad/w8/spike15/`. What is left is
   plumbing plus the 13 corpus and 21 `pycsl_lib` constructor checks that may fail — each
   a finding — and the 38 front-end goldens under a machine-checked guard.
3. **One value-model capability retires THREE refusals**: a length-carrying, REBINDABLE
   sequence local reopens routes #13, #17 and #18.
4. The two mirror-internal no-op candidates above.
5. `src/pycsl_lib` L3-tc 92 -> 90: `warn.simplefilter` and `sysmod.path_insert` are real
   route-#14 victims awaiting a stdlib-policy repair.

# HANDOFF ADDENDUM 3 — #43, ROUTES #17 and #18, and THE PROOF BATTERY THAT IS OWED.
# **EIGHTEEN routes enumerated across #33/#34/#43; seventeen closed.** Metric 451 -> 455.

## THE METHOD THAT FOUND #17 AND #18 — use it first next window

Stop probing one shape at a time. **`grep` Module 6 for every site that emits `()` for a
whole statement, then probe each with a contract false of the program.** That single census
produced routes #17 and #18 back to back, and both had a comment beside them ASSERTING
soundness:

  · route #17, `_handle_del_subscript_stmt` — its own docstring calls the blanket `del`
    no-op "UNSOUND ... a severity-1 fail-OPEN" for dicts and then keeps it for "list
    `del a[i]`, a self-field, an unknown receiver".
  · route #18, `_emit_array_local_reassign` — "other shapes fall through to a no-op
    (soundness depends on the caller treating the array as opaque after this point —
    typically handled by `\trusted` upstream)".

**A no-op lowering with a prose soundness argument beside it is the single highest-yield
thing to probe in this codebase.** Two for two.

## ROUTE #17 — `del <list>[i]` is a no-op

    xs: List[int] = [1, 2, 3]; del xs[0]; return xs[0]
    #@ ensures \result == 1        [+] Verification SUCCESS!      (Python returns 2)

Emitted `(); 1`. Worse than the dict case it was split from: Python's list `del` SHIFTS
every later element left and SHRINKS the sequence, so the no-op is wrong about EVERY index.
The DICT half correctly FAILS the analogous probe, which is what localises it.
REFUSED. Witness **0985**. Corpus byte-identical; `pycsl_lib` unchanged; the WL-05c dict
locks 0854-0857 keep their verdicts.

## ROUTE #18 — reassigning an array LOCAL is a no-op

    xs: List[int] = [1, 2]; xs = g(); return xs[0]     # g -> [9,9]; Python 9
    xs: List[int] = [1, 2]; xs = ys;  return xs[0]     # ys a PARAMETER; Python ys[0]

both `[+] Verification SUCCESS!` under `#@ ensures \result == 1`. The second is the sharper
one — an ALIASING reassignment from an unconstrained parameter, dropped, so the model
answers every later read from the old literal. REFUSED. Witnesses **0986**, **0987**.

## THREE ROUTES NOW NAME ONE REOPENING CAPABILITY

Route #13 (list mutators on a field) needs the length in the value model; route #17 (list
`del`) needs the length and a shift; route #18 needs the local to be REBINDABLE. One
capability — **a length-carrying, rebindable sequence local (`ref (array int)` plus its
length, or a real `seq`)** — retires all three refusals. That is the highest-leverage
value-model item in the backlog and is worth more than any of the three individually.

## WHAT THE FIDELITY AND VACUITY PLANES CAUGHT — read this before editing the live emitter

Routes #16 and #18 both edited a live method that is CONVERTED in the mirror.
`check-self-annotate-sync.sh` reported two NEW divergences; `check-emitted-vacuity --emit`
independently reported the SAME fault from the other side (the mirror's
`_emit_array_local_reassign` ignoring an input the live body had started using). One fault,
two planes, two vocabularies — lesson (bf) exactly.

THREE THINGS THE SYNC TAUGHT, all measured:
  1. `any(<genexp>)` over a `\trusted` predicate is an L3-tc
     `unbound function or predicate symbol` — the any/all bounded fold needs a pure symbol.
     Use an explicit loop.
  2. A SET-returning `\trusted` stub has no value-model type here. Route #16's two helpers
     became ONE boolean-returning helper (metric 454 -> 455 — an honest trusted stub for a
     call-graph worklist fixpoint).
  3. **A verbatim live->mirror copy CLOBBERS the mirror's stronger annotation.** The mirror
     declares `val_ir: "ExprIR"` where the live tree says `Dict[str, Any]`; copying the
     whole `def` replaced it and the file stopped type-checking.
     **Copy the BODY, keep the mirror's SIGNATURE.**

## THE PROOF BATTERY THAT IS OWED — the first thing to do next window

Only THREE mirror emissions moved across all of this relaunch's emitter work, plus the two
the route-#13 re-trusts moved and the three the route-#12 `raises` line moved. Compare
`scratchpad/w8/manifest_head_r14.md5` against a fresh sweep to re-derive it.

  IN FLIGHT (detached, `scratchpad/w7/pr2.sh`, 28800 s cap):
    module6_whyml/expressions.py   (a_expr)  — the array battery's 12th file
    frontend/pure_ast.py           (a_pure)  — the array battery's 13th, AND route #13
  NOT STARTED:
    audit_proof.py                 — route #13 re-trust
    frontend/Module3_Weaver.py     — route #12, one `raises` line on an UNCALLED val
    frontend/__init__.py           — route #12, same
    frontend/ir_resolve.py         — route #12, same
    frontend/desugar.py            — route #16 sync (16 goals, minutes)
    module6_whyml/statements.py    — route #18 sync (3886 goals)
    Module6_WhyMLTranspiler.py     — moved by the statements sync (862 goals)

**The array/map extension may be banked only when a_expr AND a_pure are both rc=0.**
Everything else about it is already gated: corpus byte-diff re-derived independently
(exactly the 26 files) and re-proved fresh (26/26), all non-proof planes green,
`frontend/Module5_IREmitter.py` (a_m5) rc=0 with 2088 Valid and zero bad goals.

# HANDOFF ADDENDUM 2 — #43, ROUTES #14, #15, #16. **Sixteen routes are now enumerated
# across #33/#34/#43; fifteen are closed.** Metric 451 -> 454, every +3 an HONEST re-trust.

## ROUTE #14 — the erasure of route #13 is not about `self`

The `self.<field>` restriction on route #13's guard was far too narrow. On a plain LOCAL
and on a PARAMETER, each printing SUCCESS under `#@ ensures \result == 0`:

    xs: List[int] = [0, 7]; xs.reverse();           return xs[0]    # Python 7
    xs: List[int] = [0, 7]; xs.sort(reverse=True);  return xs[0]    # Python 7
    xs: List[int] = [0, 7]; xs.insert(0, 9);        return xs[0]    # Python 9
    def driver(ys: List[int]) -> int: ys.reverse(); return ys[0]    # Python 7

The parameter form emits `let function driver` — Why3 was told the function is PURE,
because the only thing making it impure had been deleted. The guard is now keyed on the
CALL'S LOWERING (no receiver parameter AND no `writes` clause) rather than on the receiver.
Witnesses **0982**, **0983**. Corpus 820/820 byte-identical: `.append` has a faithful
array-local lowering and never reaches the fallback.

ONE HONEST REGRESSION: `src/pycsl_lib` L3-tc 92 -> 90. `warn.simplefilter`
(`_filter_actions.insert(0, action)` under `#@ assigns \nothing`) and `sysmod.path_insert`
are REAL victims that were compiling a model in which the insertion did not happen. They
are backlog items for the stdlib-stub policy, not silent successes.

## ROUTE #15 — a constructor's contract is silently discarded. FOUND, NOT CLOSED.

Found by a NEW GATE PLANE, `bin/check-clause-survival.py` (see below). `__init__` is never
emitted as a function — it is inlined at each allocation site — so its `#@ requires` and
`#@ ensures` go nowhere:

    #@ ensures self.x == 99      over a body `self.x = 0`
    [+] Verification SUCCESS! All contracts formally proven.

and `#@ requires 1 == 2` on `__init__` is discarded the same way. The inlining itself is
FAITHFUL (a caller-side claim relying on the false postcondition correctly FAILS,
single-file and cross-file), so this is a DISHONESTY, not a demonstrated unsoundness —
#33's category for the dangling-block finding.

**PRICED, and cheaper than it looks.** Of the 61 constructors carrying a
`#@ requires`/`#@ ensures`, only 34 carry a NON-TRIVIAL one, and **ZERO of those are in the
mirror** — 13 corpus files and 21 `pycsl_lib` stubs. A fix gated on a non-trivial
constructor contract is MIRROR-INERT, so the 53-file battery never arises. It needs TWO
additive IR fields, not one: `init_requires`, and `init_param_types` (the checking
function's signature needs WhyML types, and `init_params` is names only; `__init__` is
absent from `_module_method_param_whyml_types`). `init_body` is NOT a body model — it holds
only param-dependent stores — so the body must come from `_call_record_constructor`.
Cost: 2 IR fields + a Module 6 emitter + 38 front-end goldens under a machine-checked guard
+ 13 corpus re-proofs. **THE TOP LADDER ITEM.** Acceptance test: clause-survival 4 -> 0.

## ROUTE #16 — a Python `assert` is lowered to `()`, and inside a catching `try` that is unsound

`def f(n): assert n > 0; return n` emits `(); n`. Outside a handler that is CONSERVATIVE
and sound. Inside a `try` the handler branch is DEAD in the model and is the branch Python
takes. Four shapes proved `#@ ensures \result == 1` where Python returns 2 — lexical and
INTERPROCEDURAL, with `except AssertionError`, bare `except:` and `except Exception`.
CLOSED in `desugar.reject_unmodelled`, interprocedurally (a same-module callee that
transitively asserts counts), census **0** over 3565 files / 454 `try` / 1450 `assert`.
Witness **0984**. Corpus byte-identical; `pycsl_lib` L3-tc unchanged.
Callee exception propagation itself is FINE and was checked separately — `raise ValueError`
under `except ValueError` / `except Exception`, and `1 // 0` under `except ZeroDivisionError`,
all correctly FAIL. The leak is specific to `assert`.

## NEW GATE PLANE — `bin/check-clause-survival.py`

The plane that looks for what the emission is MISSING. Sound in one direction: the emitter
only ADDS clause lines, so `emitted < source` implies a clause did not survive. Tokenizes
the source side; returns rc 1 on an empty/stale `--emit-dir` with "that is a FALSE GREEN,
not a pass". Ratchet 4 — and all four are route #15, so it is that route's exact tracker.

**It was wrong twice before it was right**, and both fixes are the lesson: it first
anchored the emitted patterns at `^\s*` and missed the one-line
`requires { true } ensures { true }` form; then it counted `#@ requires True`, which is
legitimately normalized away. 25 -> 21 -> 4.

## SWEPT THIS RELAUNCH — do not re-derive

* Module-5 handler FIELD COVERAGE (transitive, depth 3): expression handlers 0 unmentioned
  fields; the 5 statement candidates all covered or not demonstrable.
* The Module-5 -> Module-6 IR-KEY boundary: 111 node tags, ZERO unread keys, under both a
  whole-Module-6 and a per-handler-closure form.
* Clause survival for `#@ loop invariant` / `loop variant` (90 files), `#@ class invariant`
  (83 files, 158 -> 178), `#@ assert` (13/13), `#@ check` (1/1) — all ZERO deficits.
* Argument binding: defaults, keywords and mixed calls all faithful (5 probes).
* STARRED-ARGUMENT FORWARDING is FAIL-CLOSED, not unsound — the backlog's wording implies
  otherwise and should be corrected. A multi-parameter callee is refused on arity; the
  single-parameter shape correctly FAILS a false postcondition.
* Inheritance: override dispatch, an inherited method, `super().m()`, and a polymorphic
  call through a base-typed parameter — all four correctly FAIL a false postcondition.
* Chained comparison, walrus, comprehension filters — correct.
* The `UnknownPyExpr -> 0` catch-all does NOT erase calls.

## THREE TIMES THIS RELAUNCH A FRESH INSTRUMENT'S FIRST FINDING WAS ITS OWN BUG

The line-based `#@` census reporting 95 docstring hits where the truth was 0; the
`^\s*ensures` anchor missing one-line contracts; the `#@ assume` prefix matching
`#@ assumes bounded_int(32)`. Each cost seconds to catch and would have cost a window to
act on. **Read the SOURCE LINE the census points at before believing the census.**

# HANDOFF ADDENDUM — #43, ROUTE #13: **the biggest find of the relaunch, and it DEFEATED
# the fix #34 built.** A mutating METHOD CALL on a `self.<field>` collection was erased
# from the model. 451 -> 454 markers, all three an HONEST RE-TRUST.

## THE ROUTE, REPRODUCED BEFORE ANYTHING WAS CHANGED

    #@ class invariant self.xs[0] == 0
    @mutable_state
    class C:
        #@ assigns self.xs
        def __init__(self) -> None:  self.xs: List[int] = [0, 7]
        #@ assigns \nothing
        def go(self) -> None:        self.xs.reverse()
        #@ ensures \result == 0                       <-- FALSE OF THE PROGRAM
        def run(self) -> int:        self.go(); return self.xs[0]

    [+] Verification SUCCESS! All contracts formally proven.        (Python: 7)

emitting `val self_xs_reverse_0 () : int` — **no `self`, no `writes`**. The mutation is
not under-claimed, it is ABSENT. A second shape: `self.xs.append(9)` emits a write into a
FRESH `Array.make 1024 0` with no write-back, and proves `#@ ensures \length(self.xs) == 2`
where Python gives 3. Witnesses **0980** and **0981**, both negative-tested.

**WHY IT MATTERS MORE THAN ROUTES 8/9/10: it defeats their fix.** #34's frame-preservation
`ensures { self.<f> = old self.<f> }` is checked by Why3 against the EMITTED body — and the
emitted body no longer contains the write. The clause is true of the model and false of the
program, and the class invariant is PROVED RE-ESTABLISHED by a method that reverses the list.

**WHY EVERY PLANE MISSED IT.** `check-dropped-mutation.py` classifies `Assign` / `AugAssign`
/ `AnnAssign` STATEMENTS; a bare `Expr(Call)` mutator is not in its population at all.
`check-trusted-frame-honesty.py` looks for a write the emitted body does not contain.
`check-avatar-frame-parity.py` sees a correctly-frameless avatar, because by the model it is.
The whole-file proof passes because the model is consistent — it is a model of a different
program. **A gate that reads the EMITTED body cannot see a mutation the emitter deleted.**

## CLOSED, and the refusals are byte-inert

Two refusals, each at the exact point where the mutation disappears:
`module6_whyml/expressions.py` (the generic abstract-op fallback, gated on
`not receiver_param and not writes_clause`) and `module6_whyml/statements.py` (the
array-local shadow arm of `.append`, gated on a `self.` receiver). Corpus **820/820
byte-identical**, zero refusals — the reference corpus's two `self.<f>.<mut>()` sites are
both modelled.

## THE THREE MIRROR VICTIMS, and the exact census that found them

`scratchpad/w8/census_selfmut3.py`. **Trust must be decided by the CONTIGUOUS `#@` block
above the def** — a fixed 10-line window missed `visit_Module` entirely.

  · `audit_proof.AuditReport.extend` — all THREE `self.<f>.extend(...)` absent from the model
  · `pure_ast._Unparser.write` — the unparser's OUTPUT BUFFER, `writes { }`, in a file
    proved at 3126 goals
  · `pure_ast._Unparser.visit_Module` — a trailing `.clear()` left the dict POPULATED.
    CHEAP REOPENING: the dict is alias-free there, so rewriting live+mirror to
    `self._type_ignores = {}` restores the conversion with no new capability.

`Module5_IREmitter._collect_final_registry` is NOT a victim — its appends take the faithful
`Seq.snoc` arm. That is what makes the refusals narrow rather than blanket.

## THE CERTIFIED BOUNDARY UNDER `_Unparser.write` — built, not argued

`#@ assigns self._source` was actually written, and the whole class re-framed from the LIVE
transitive write set (`scratchpad/w8/propagate_frame.py`; 58 mirror methods widened, 99 of
107 reach `self._source`). L3-tc then failed one layer out and not on a frame:

    self_interleave_3 (fun () -> (self_write_1 self ...))
    This function has side effects, it cannot be used as pure

`write` is passed to `interleave` as a FIRST-CLASS CALLBACK. 19 `_Unparser` methods build
such a lambda, so an honest `write` frame costs ~15 further re-trusts.
**REOPENING CAPABILITY: a lowering for an effectful higher-order callback.**
So `write` is `\trusted` with a KNOWN-FALSE `\nothing`, and the frame-honesty ratchets moved
**trusted total 0 -> 1, converted total 95 -> 94** — the same method relabelled from a
SILENT false frame to an EXPLICIT reviewed assumption. The dishonesty did not grow; it
became countable.

## A SEPARATE, LARGE, UNTAKEN LEVER FOUND ON THE WAY

Converting `_Unparser.__init__` (ONE marker, and its `#@ assigns` is already correct)
upgrades the entire class from the opaque `_pyobj_state` attribute store to a CONCRETE
RECORD — `type _unparser = { mutable _source: array int; mutable _precedences: ...; ... }` —
replacing `getattr__unparser self <hash>` with real field projections across 107 methods.
It currently costs ONE L3-tc error (`_for_helper`'s `writes` over-claims `self._source`,
because `fill`/`write` declare `\nothing`), i.e. it is blocked by the SAME
`_Unparser`-frame problem above. **Do this the moment the callback boundary is broken** —
it is the single largest model upgrade left in the mirror, and 20 of the 21 remaining
`_Unparser` `\trusted` stubs sit behind it.

# HANDOFF — #43 (2026-09-03, WINDOW 3, relaunch after the #34-#42 `529 Overloaded` outage):
# **the metric did not move (451) and that is again the right answer. This relaunch found
# and closed the TWELFTH demonstrated unsoundness, corrected THREE inherited claims that
# were false, and repaired FIVE gates that were printing their ratchet as if it were their
# measurement.**

## READ THIS FIRST — THREE INHERITED CLAIMS WERE FALSE, AND ALL THREE WERE CHEAP TO CHECK

1. **"A completed 13-file proof battery is waiting to be banked; verdict in
   `scratchpad/w7/verify_arr2.log`" — FALSE.** `verify_arr2.log` is the CORPUS plane. Its
   runner, `scratchpad/w7/verify_arr.sh`, iterates `changed_arr.txt`, which is 26 CORPUS
   TEST FILES, and proves each with `pycsl.py`. `ARR PROVE OK: 26` says nothing about any
   mirror. The mirror battery's verdicts live in `scratchpad/w7/proofs/a_*.rc`: TEN were
   0, `a_expr.rc` was **124** (killed by `pr.sh`'s 10800 s `timeout`, ZERO
   `Verification SUCCESS` lines in its 80514-line log), and `a_m5` / `a_pure` **did not
   exist** — Module5_IREmitter and pure_ast were never started. b952bef5's own commit
   message says so: "STILL OWED: the 13-mirror re-proof battery". The primary record was
   right and the summary of it was wrong. The tell was arithmetic: the count in the log
   line (26) does not match the battery's size (13).
2. **"#34 died mid-implementation of the `nonlocal_writes` IR field" — FALSE.** It is
   landed and witnessed: `Module5_IREmitter.py:5256-5279` builds it, `functions.py:5521`
   refuses on it, corpus **0977** is the witness. Settled by grepping the symbol
   (lesson (az)), in one command.
3. **"Route 6b of the `#@`-attachment audit is open; eight of eleven routes closed" —
   FALSE.** All eleven are closed; 6b is the row in #34's own table marked
   **CLOSED**, banked at 8396828e.

**The one item the #34 handoff named as genuinely unswept — its item 3,
`Module1_Ingestor._assign`'s `elif nxt is None: pass` — was real, and it is route #12
below.** The ladder handed down was stale in three places out of four and correct in the
fourth. Check each item against the disk before spending a minute on it.

## ROUTE #12 — a `#@` DIRECTIVE INSIDE A STATEMENT'S CONTINUATION LINES IS DISCARDED

Reproduced before anything was changed, five probes, every one printing SUCCESS:

    #@ ensures \result == 2
    def f() -> int:
        return (
    #@ assert 1 == 2                  <-- FALSE, AND NEVER CHECKED
            2)
    [+] Verification SUCCESS! All contracts formally proven.

The indented form, the module-level `y: int = (` form of both, and a `#@ ghost x = 99` +
`#@ assert x == 99` PAIR in that position all proved too.

MECHANISM. `_Harvester._assign` associates a comment with a target by `bisect` over the
targets' START lines, so a comment between a leaf statement's first and last line bisects
PAST it. When that statement is the file's last there is no `nxt` at all and the comment
takes `elif nxt is None: pass` or, indented, `prev.footer`. #33's and #34's END-OF-FILE
guards cannot see it: the block does not run to end-of-file — the statement's own
continuation lines follow it.

CLOSED by a refusal spelled INLINE in `Module1_Ingestor.process`, the one place holding
both the tree and the real comment tokens, and `\trusted` in the mirror.
Witness **0979_continuation_directive_refused**, NEGATIVE-TESTED (proves at 13c4860b,
refused at HEAD). Corpus 820/820 byte-identical; mirror L3-tc 53/53; metric unchanged.

**THE CENSUS IS THE PART TO REMEMBER.** A LINE-BASED scan of the 3663 annotated files
reports **95** hits. Every one is `#@` text inside a DOCSTRING — including the
doc-comments of routes 1-11's own witness tests. Tokenizing and keeping only real COMMENT
tokens gives **0**. A refusal built on the line-based number would have rejected 95
innocent files. When you census a SYNTAX, tokenize; a `grep` for `#@` finds the
documentation of the bug as readily as the bug.

## THE `#@`-ATTACHMENT VEIN IS NOW SWEPT

The compound-statement HEADER shapes were the last un-probed family and they are clean:
a directive inside a multi-line `def` signature, a multi-line `while` header and a
multi-line `class` header are all REFUSED by #34's `_reject_misplaced_directives`; one
inside a multi-line `if` condition attaches to the following statement, is CHECKED, and
correctly FAILS. Twelve routes found across #33/#34/#43, twelve closed.

## FIVE GATES WERE REPORTING THEIR RATCHET AS THEIR MEASUREMENT

`check-avatar-frame-parity.py`, `check-computed-rhs-erasure.py`, `check-dropped-mutation.py`,
`check-shadowed-selfcalls.py` and `check-trusted-frame-honesty.py` ended a green run with a
line formatting `args.max_*` — the CONSTANT — and nothing else. #34's closing baseline
copied one of those lines and so recorded "avatar-frame-parity 0 same-file / 7 inherited".
Measured (twice at HEAD, once at 13c4860b, all agreeing): **0 same-file / 1 inherited**.
`MAX_INHERITED` lowered **7 -> 1** — a real tightening, six units of unjustified slack
removed. All five OK lines now print measurement AND ratchet. Every other ratchet is
already AT its measurement, so nothing else could be lowered.

**Corollary for whoever reads a handoff number: a gate's green line is not necessarily a
census. Re-run the gate.**

## THE ARRAY/MAP FRAME EXTENSION — WHERE IT ACTUALLY STANDS

Landed as code at b952bef5 (the deletion of the scalar type filter in
`module6_whyml/functions.py`). Gating status as re-derived by this relaunch:

  · CORPUS byte-diff — **DONE, independently.** 820 emissions at HEAD vs 820 at 13c4860b,
    `diff -rq`: the changed set is EXACTLY the 26 recorded files and nothing else.
  · CORPUS proof — **DONE, freshly.** `43 ARR PROVE OK: 26 / 26`, FAIL empty
    (`scratchpad/w8/verify26.log`).
  · MIRROR battery — **10 / 13.** Green: struct_format, ConcurrencyChecker, audit_proof,
    audit_proof_reverify, proof2why3/parser, types, Module6_WhyMLTranspiler, Module2_Parser,
    stmt_control_flow, module6_whyml/statements. **OWED: `module6_whyml/expressions.py`,
    `frontend/Module5_IREmitter.py`, `frontend/pure_ast.py`.** expressions and
    Module5_IREmitter are IN FLIGHT under `scratchpad/w7/pr2.sh` (28800 s cap, detached
    via `setsid`); pure_ast has not been started.
  · Every NON-PROOF plane — **DONE, all green** (see the gate table below).

**DO NOT BANK THE EXTENSION UNTIL a_expr, a_m5 AND a_pure ARE ALL rc=0.**

## ALSO OWED, AND SMALL: THREE MIRROR RE-PROOFS FOR ROUTE #12

The route-#12 refusal adds exactly ONE line to three mirror emissions —
`raises { PyCSLParseError }` on `val module1_ingestor__process` in
`frontend/Module3_Weaver.mlw`, `frontend/__init__.mlw` and `frontend/ir_resolve.mlw`.
That val is DECLARED BUT NEVER CALLED in all three (grepped), so no goal can move; the
re-proofs are queued behind the array battery rather than skipped on that argument.

## INSTRUMENT FACTS #43 ADDS

18. **THE MIRROR IS `src/self-annotate/src/`, and `src/pycsl/` is the LIVE EMITTER.** Both
    trees carry a file at the same relative path. Proving the wrong one runs to completion
    and refuses *persuasively* — `src/pycsl/module6_whyml/expressions.py` dies with
    `in-place mutation of dict/set parameter 'free'`, a REAL recorded PyCSL boundary. Two
    things settle it, neither of them the error text: a control at an older commit shows
    the same refusal, and the HEAD of a previously-successful log names the file it parsed.
    Canonical invocation (`scratchpad/w2/sweep.sh`): FILE under `src/self-annotate/src/`,
    `--import-path src/pycsl`.
19. **A LIVE-TREE EDIT LEAKS INTO MIRROR EMISSION THROUGH `--import-path src/pycsl`.** The
    mirrors import the LIVE modules, so the live body is what the importer reads. Route
    #12's refusal was first spelled with `%` string formatting; the emitter reads `%` as
    MODULO and pulled the entire `pycsl_div` / `pycsl_mod` preamble into two mirror `.mlw`
    — ten lines of arithmetic helpers, out of a `raise` message. Rewritten with `str()`
    concatenation the delta vanished. "I only touched the live tree" is not an argument for
    emission inertness. Measure it.
20. `bin/check-emitted-vacuity.py` WITHOUT `--emit` does not merely under-report: it prints
    `8 known erasure(s) NO LONGER erased — remove from KNOWN_ERASURES`, i.e. it actively
    invites you to DELETE eight live gates. With `--emit` (11 s) the same eight are
    correctly still erased. Reproduced this window.

## SETTLED, DO NOT RE-DERIVE

* `computed-rhs-erasure`'s two residues are FAITHFULNESS gaps, **not** unsoundnesses.
  `expressions.py::_handle_field_get_expr`'s `_pg2` erases to `0` because
  `_property_getters` lives on `Module6_WhyMLTranspiler` and is read through the mixin, so
  it is not in `_all_record_fields`. The mirror method's contract is
  `requires True / ensures True`, so no false postcondition is provable, and the erased
  branch only RETURNS — it writes nothing, so the frame is over-claimed, which is safe.
  Reopening capability: a cross-class (mixin-owned) field model.
* `dropped-mutation`'s single DROPPED site is `pure_ast._merge_str_constants`'s
  `out[-1].value += v.value` — an augmented store through a non-Name base. The mirror
  method is `\trusted`, so it is a lowering gap, not a converted victim.
* The `UnknownPyExpr -> 0` catch-all is NOT the erasure hazard it looks like for CALLS:
  `xs.count(2)` emits `(xs_count_1 2)`, an opaque function, and three probes with false
  `ensures \result == 0` over an unrecognized local call, a `math.floor` call and a list
  method all correctly FAIL. The `-> 0` path is reached by genexps and yields, which have
  their own planes.

## THE GATE TABLE THIS RELAUNCH RE-RAN FRESH (all green, PATH exported)

    metric                    451 markers / 476 grep / offset 25 / unattached 0
    emitted-vacuity --emit    0 NEW erasure, 8 known gated
    yield-erasure             0 value-erasing, 2 suspension (ratchet 2)
    mirror-signature-drift    0 / 0
    computed-rhs-erasure      measured 2 rhs / 0 param
    dropped-mutation          measured 1 / 50 / 9 / 0
    mirror-field-parity       7 known, 0 NEW
    frame-honesty             trusted 0/0, converted 0 model-visible / 95 total
    untrusted-emitted         865 / 849 / 0 / 0
    shadowed-selfcalls        measured 14
    avatar-frame-parity       measured 0 same-file / 1 inherited (ratchet now 1)
    IR conformance            core-only 38/0, front-end 38/0, 10/10 hashseed-stable
    corpus byte-diff          820 / 820 byte-identical across the route-#12 refusal
    mirror L3-tc              53 / 53, TC_FAIL 0
    fidelity                  both scripts byte-identical to a freshly-built baseline
    doc-coherency             OK

## WHERE THE LADDER STANDS

0. **Finish the array/map battery** (a_expr, a_m5 in flight; a_pure not started), then bank
   the extension. Then the three route-#12 mirror re-proofs.
1. `proof2why3`'s `term` family — the named COST/SCALE residue, needing a general ADT-value
   lowering. Per §A.3 that is NOT a floor; a funded window pays it. It is now the largest
   remaining item.
2. The heterogeneous-list-literal 15.
3. The three formerly authorize-first builds (`find_assigned_vars` structural-variant
   robustification; const-dict global-type-inference model; `while` -> `for` rewrite) —
   pre-authorized since 2026-08-26 and untouched by #33/#34/#43.
4. Housekeeping done this relaunch: the stale worktrees `scratchpad/w3/wt`, `w4/base`,
   `w4/wt` are removed. w3/wt held two uncommitted `src/` edits — the ir_resolve
   qualified-method-name fix (verified LANDED) and an UNLANDED, unproven
   `_Unparser.__init__` conversion, archived to
   `getting-better/interrupted/2026-08-w3-unparser-init-spike.patch`.
   `scratchpad/w7/base` is KEPT: it is the byte-diff baseline.


# HANDOFF — #34 (2026-09-03, WINDOW 3): **the metric did not move (451) and that is the
# right answer. This window found ELEVEN demonstrated unsoundnesses — routes on which
# `[+] Verification SUCCESS! All contracts formally proven.` was printed over a contract
# that is FALSE OF THE PROGRAM — and CLOSED ALL ELEVEN, each one gated on every plane.**
# #33's ladder item 5, "Module 3's `#@` attachment", was the richest surface in the
# campaign so far, and the vein did not stop there: the last three are in the FRAME, and
# they are the biggest — an `#@ assigns` on a converted method was an UNCHECKED
# ASSUMPTION unless its class happened to carry `@mutable_state`.

## THE ELEVEN, EACH REPRODUCED BEFORE ANYTHING WAS CHANGED

Method, unchanged from #33: enumerate the dispatch mechanically, then probe END-TO-END
WITH A CONTRACT THAT IS FALSE OF THE PROGRAM. A true contract failing tells you nothing.
Every "Python returns N" below was obtained by RUNNING the probe.

| # | route | probe | status |
|---|---|---|---|
| 1 | `try ... except*` dropped ENTIRELY (`_PY_STMT_HANDLERS` has no `TryStar`, `_py_stmts_to_ir` has no `else`) | `ensures \result == 1`; Python returns 2 | **CLOSED** — refused in `desugar.reject_unmodelled` |
| 2 | a `#@` contract on an `async def` discarded; the coroutine never reaches the IR | `ensures \result == 1`; method returns 2; module emitted EMPTY | **CLOSED** — refused in `Module3_Weaver.process` |
| 3 | `#@` above `if`/`try`/`except*`/`match` never anchored (`_make` returned `mk(None, None)`) | `#@ assert 1 == 2` above an `if` proved SUCCESS | **CLOSED** — anchored as `SimpleStatement` |
| 4 | `#@` in decorator whitespace dropped ("invisible to libcst's leading_lines") | the mirror's `_heap_var` lost its whole contract | **CLOSED** — attached to the decorated def |
| 5 | a directive on an anchor that ignores it (every attachment site is an `if/elif` with no `else`) | `#@ assert 1 == 2` above a `def` and above a `class`; `#@ ensures 1 == 2` on a `while` | **CLOSED** — `_reject_misplaced_directives` |
| 6 | (same family) a `#@ class invariant` that lands on `__init__` | `pycsl_lib/re/_engine.py`: `ReMatch` had NO invariant in the model | **CLOSED** — moved above `class` |
| 6b | a statement-level `#@` at COLUMN 0 with nothing after it: `process`'s at-EOF refusal exempts `assert`/`ghost`/… because "a trailing `#@ assert` IS the last statement of a body" — true only INSIDE a body | `#@ assert 1 == 2` as the last line of a file proved SUCCESS | **CLOSED** — the exemption is now conditioned on the block being INDENTED |
| 7 | `nonlocal` dropped; the nested `def` is lifted and its write lands on a FRESH LOCAL | `ensures \result == 1`; Python returns 2 | **CLOSED** — refused in Module 6's GENERIC emission |
| 8 | an UNDER-CLAIMED `#@ assigns` on a converted method is never checked against the body | `ensures \result == 0`; Python returns 7 | **CLOSED** — frame-preservation `ensures` in Module 6 |
| 9 | `#@ assigns \nothing` on a mutating method (the avatar does not even take `self`) | same shape, same false proof | **CLOSED** — frame-preservation `ensures` in Module 6 |
| 10 | NO `#@ assigns` clause at all — callers still assume the method writes nothing | same shape, same false proof | **CLOSED** — frame-preservation `ensures` in Module 6 |

## LIVE VICTIMS FOUND — every one repaired

* **the mirror's own `pure_ast._Parser.import_from`**: TWO `#@ assert self.i > \old(self.i)`
  of its SIX staged monotonicity checkpoints sat above an `if` and were never anchored, in
  a file proved at 3103 goals. They are now real obligations and the file emits **3106** goals where it emitted 3103; the whole-file re-proof was still running when this was written — see the SEGMENT-CLOSE line in `getting-better/driver-progress.log` for its verdict.
* **`Module6_WhyMLTranspiler._heap_var`** (mirror): `#@ requires/ensures/assigns` under its
  `@property`, discarded; the method was verified as if uncontracted.
* **`pycsl_lib/re/_engine.py`**: two `#@ class invariant` below `__slots__`, landing on
  `__init__`. `ReMatch` carried NO invariant.
* **`pycsl_lib/os/UnixInodeFileSystem._pad_name`**: an `#@ assigns` and THREE `#@ ensures`
  after the docstring, with a source comment claiming they were "surfaced as top-level
  ensures so `_blit_dir_entry` can chain them". They were surfaced nowhere. (Redundant with
  the real block above the `def` — deleted.)
* **`pycsl_lib/csys`** (3) and **`UnixInodeFileSystem`** (1): four `#@ assert` above an `if`.
  `csys` re-proves at **4873 Valid vs 4866 before**, rc=0 SUCCESS, 0 Unknown either side.
* **corpus 0208**: `#@ ghost total += 1` above an `if`. This is EXACTLY why 0208 was
  `pycsl-expected: FAIL` — its `loop invariant total == i` could not hold when the ghost
  update did not exist. **It now PROVES**, and its one added line
  (`ghost total := !total + 1;`) is the ONLY change in the entire 819-file corpus emission.

## THE STRUCTURAL LESSON OF THIS WINDOW

**A `#@` DIRECTIVE HAS THREE PLACES TO DIE, AND ONLY THE THIRD HAD A GUARD.** Module 1 can
refuse to ANCHOR it; Module 3 can anchor it on a node whose attachment site IGNORES it;
Module 5/6 can drop the STATEMENT it was attached to. #33's `process()` guard covered
exactly one shape of the first (a block at end-of-file). Everything else printed
"All contracts formally proven" over a directive it had thrown away. When you audit a
directive surface, walk all three.

**AND THE FRAME IS A CLAIM WITH NO CHECK.** `_build_method_writes_map`'s docstring says the
avatar's `writes` is "derived from the SAME `contracts.assigns` the method's `let` is
verified against, so the abstract op's `writes {self.x}` cannot drift from the method's
frame." **That sentence is false.** The `let` carries no frame at all unless the class opts
in with `@mutable_state`; Why3 infers its effect from the body; nothing ties the two.
Lesson (az) again — settle a claim about a mechanism by RUNNING the mechanism.

## WHERE THE LADDER STANDS FOR #35

**0. THE FRAME-PRESERVATION FIX LANDED AND IS FULLY GATED — nothing is owed on it.**
Module 6 now emits, on the CONCRETE `let` of every method of a record-emitting class,
`ensures { self.<f> = old self.<f> }` for each SCALAR record label the method's
`#@ assigns` does not name. A preservation POSTCONDITION rather than a `writes` clause,
because Why3 rejects an OVER-claimed `writes` as hard as an under-claimed one and the
`writes` form breaks 14 corpus files whose `#@ assigns self.<array-field>` is spelled for
the field while the body writes `self.f[i]` (`self.f.elts`). Declaring more than you write
merely emits FEWER preservation clauses, so the form has no false-rejection mode at all.
  · **ALL SIXTEEN affected mirror re-proofs came back rc=0 `Verification SUCCESS` with
    ZERO bad goals** (pure_ast 3126, stmt_control_flow 6426, expressions 4315, statements
    3886, Module5_IREmitter 1650, Module6_WhyMLTranspiler 862, types 815, Module2_Parser
    738, proof2why3/parser 440, ir_inline 363, Module3_Weaver 284, proof2why3/ir 45,
    audit_proof_reverify 25, struct_format 22, proof2why3/crosscheck 10,
    ConcurrencyChecker 9). **THE VICTIM CENSUS CAME BACK EMPTY** beyond the one repaired
    before the battery.
  · THREE HONEST FRAME REPAIRS were needed and all three are genuine defects:
    `frontend/ConcurrencyChecker._walk_body` (declared `\nothing`, calls a callee that
    declares `#@ assigns self.warnings`), corpus 0721 `Bank.handle` (writes
    `self.session_authenticated`, the HAPPY capability flag its own call site relies on)
    and corpus 0723 `Ledger.transfer` (writes `self.balance`, `self.audit`,
    `self.audit_len`). Each had NO or an under-claimed `#@ assigns`.
  · `bin/check-trusted-frame-honesty.py`'s MODEL-VISIBLE predicate was WIDENED with it —
    the emitted record now answers the question whenever an emission is available, and
    `@mutable_state` is only the fallback for the source-heuristic path. Converted total
    ratchet 96 -> 95.
  · IR conformance: the FRONT-END corpus never moved (38 OK / 0 MISMATCH — this is a
    Module 6 emission change, the IR is untouched); the CORE-ONLY corpus went 8 MISMATCH
    and its goldens were refreshed under a MACHINE-CHECKED GUARD that aborts unless every
    diff line is exactly an added `ensures  { self.<f> = old self.<f> }`. It aborted on
    nothing.
  · Full suite re-run after the fix: **3021/3123, and the FAILURE SET IS BYTE-IDENTICAL**
    to the run before it. Zero new failures across 3123 tests.

**1. THE ONE THING THE FRAME WORK STILL OWES: the ARRAY/MAP extension.** The preservation
clauses are emitted for SCALAR record labels only, because an `array`/`map` field needs
element-wise preservation that scalar equality cannot express. So a method that declares
nothing and writes `self.disk[i] = v` is STILL unchecked. Corpus **0459** is exactly that
shape and is the ready-made driver; the `writes`-variant experiment named 0459 0460 0461
0720 0724 0725 as the population it reaches and the scalar form does not.

**2. `bin/check-trusted-frame-honesty.py`'s MODEL-VISIBLE predicate HAS BEEN WIDENED**
(it hard-gated on `@mutable_state` before its own `--emit-dir` refinement got a chance, so
it reported 0 over a set that excluded exactly the population routes 8/9/10 bite). It now
reports 0/0 and 0/95 on the HONEST set. Nothing owed.

**3. The `#@`-attachment vein has one unswept surface left**: `Module1_Ingestor._assign`'s
`elif nxt is None: pass` (a module-level trailing `#@` at indent 0 is ignored "as libcst").
The `process()` EOF guard covers the common shape; whether it covers all of them was not
measured.

**4. Unchanged from #33** and untouched by this window: avatar-frame INHERITED 7,
`computed-rhs-erasure` 2, the `dropped-mutation` residues (1/50/9/0),
`proof2why3`'s `term` family, the heterogeneous-list-literal 15.

## SWEPT AND CLEAN — do not re-derive

* the `match` surface: `_py_stmt_match` reads `subject` and every case's `pattern`, `guard`
  AND `body`. A MAPPING pattern (`case {"a": 1}`) is a LOUD `unsupported` in `pure_ast` and
  a KEYWORD class pattern (`case Ctor(x=0)`) is a LOUD syntax error, so
  `_match_pattern_to_ir`'s hard-coded `kwd_attrs=[]` can never silently drop a constraint.
* `global` is modelled (`module_collect` collects `written_via_global`). `import`,
  `import from`, `type X = ...`, a nested `class` and a nested `def` inside a body are
  dropped as STATEMENTS, but each was probed with a FALSE contract and each is INERT.
* the contract EXPRESSION grammar: five false contracts over `\forall`, `\exists`, `or`,
  `==>` and `\old` all correctly FAIL.

## INSTRUMENT FACTS #34 ADDS

1. **BOTH FIDELITY SCRIPTS EXIT 1, AND HAVE ALL WINDOW.** `check-self-annotate-sync.sh`
   (2 diverged un-trusted bodies: `expressions._handle_var_expr`,
   `stmt_control_flow._handle_for_stmt`) and `self-annotate-mirror-check.sh` (3 mirrors,
   4 mirror-only defs incl. `_materialize_bridge`) produce output that is BYTE-IDENTICAL
   at HEAD, at f408c9e3 and at the window-start e4d0a209. Long-standing, not a regression —
   but the honest reading of "fidelity green" is "no NEW divergence", and that is what can
   be verified. Baseline logs: `scratchpad/w7/sync_base.log`, `mirror_base.log`.
2. **`src/pycsl_lib` is 92 files L3-tc GREEN and 12 that do NOT type-check** — `dc`,
   `iomod`, `json/{__init__,decoder,encoder,scanner,tool}`, `os/UnixInodeFileSystem`,
   `proc`, `re/_engine`, `subproc`, `tmpf`. #33 named two of the twelve. The set is
   BYTE-IDENTICAL at f408c9e3 and after every #34 change
   (`scratchpad/w7/l3lib_{base,nl}.log`). `os/UnixInodeFileSystem.py`, the flagship
   body-verified stdlib file, fails on `unbound function or predicate symbol
   'dir_find_free_prefix'` and has been failing since before this window.
3. A REFUSAL is measurable on the byte-diff plane for free: a refused file emits no `.mlw`,
   so "819 of 819 present and byte-identical" also proves no corpus file was refused.
4. `scratchpad/w7/` layout: `base/` = worktree at f408c9e3 (window baseline), `wt/` =
   worktree at HEAD for measuring while the main tree proves (symlink `.venv` into it or
   `byte-diff-sweep.sh` emits 0 files), `proofs/` = every log + `.rc`, `probes/` = every
   false-contract probe, `pr.sh` = the detached whole-file proof driver.

## VERIFICATION BASELINE #34 LEAVES

**THE PROJECT'S OWN FULL SUITE, run as the closing integration check: 3021/3123.**
`pycsl-reference` **883/906** (695 PASS + 188 XFAIL, 23 FAIL) — **23 is exactly #33's
failure count** (it reported 877/900; the +6 are this window's witnesses 0973-0978, all
green), so that suite is unchanged. `python-reference` **2138/2217** (79 FAIL), a suite
#33 did not run at all: 1707 of its 2217 tests are the `stdlib` subtree, which is why the
denominators differ so much between the two windows' reports. **ZERO of the 102 failures
is caused by a #34 refusal** — `scratchpad/w7/check_fail_cause.sh` re-ran every one and
matched its output against all five refusal texts; 0 matched. Corpus 0208, previously
`pycsl-expected: FAIL`, now PASSES.

EIGHT WHOLE-FILE PROOFS, every one rc=0 `Verification SUCCESS` with 0 Unknown/Timeout/
Failure: `pure_ast` **3106** (3103 before — the two newly-anchored `#@ assert`), `csys`
**4873** (4866 before — three newly-anchored `#@ assert`), `ir_resolve` 793, transpiler
**708** (706 before — `_heap_var`'s recovered contract), mirror `pycsl.py` 735,
`frontend/__init__.py` 684, `ConcurrencyChecker` 5, `desugar` 16. The mirror `.mlw` set
was re-emitted afterwards and is BYTE-IDENTICAL to the set those proofs ran over, so every
verdict applies to HEAD. Mirror L3-tc 53/53.

Corpus byte-diff vs f408c9e3: **51 files** — 50 of them gaining the frame-preservation
`ensures` and 0208 its ghost line. Before the frame fix landed it was **1 file, 1 line** (0208's ghost update; everything else
byte-identical). Mirror L3-tc **53/53**. IR conformance BOTH corpora (38 OK / 0 MISMATCH,
10/10 drivers byte-stable across PYTHONHASHSEED). dropped-mutation 1/50/9/0 ·
shadowed-selfcalls 14 · yield-erasure 2 · computed-rhs-erasure 2/0 · frame-honesty 0/0 and
0/95 · mirror-signature-drift 0 · mirror-field-parity 7 known/0 new · avatar-frame-parity
0 same-file / 7 inherited · emitted-vacuity `--emit` 8 known / 0 input-blind ·
untrusted-emitted 849 emitted / 0 re-abstracted · doc-coherency OK. Witnesses added: **0973** (`except*` refused), **0974**
(async contract refused), **0975** (misplaced directive refused), **0976** (directive
anchoring — NEGATIVE-TESTED twice), **0977** (`nonlocal` refused). `python-reference/0111`
marked `pycsl-expected: FAIL`; `pycsl-reference/0208` un-marked because it now proves.

# HANDOFF — #33 (2026-09-02, WINDOW 3): **447 -> 451 markers, and the four extra markers
# bought THREE PROVED FALSE POSTCONDITIONS being made impossible, TWO NEW GATE PLANES, a
# DEAD CI GATE RESTORED, and both frame-honesty populations driven to zero.** The window's
# yield is not a count: it is a SYSTEMATIC AUDIT of one bug class — "a lowering reads some
# of a node's fields and silently drops the rest" — run mechanically over the dispatch
# table, and every candidate probed END-TO-END WITH A CONTRACT THAT IS FALSE OF THE PROGRAM.

## THE THREE FALSE PROOFS, EACH REPRODUCED BEFORE BEING FIXED

**1. `a = b = v` dropped every target but the first.**
```
    #@ ensures n <= 0 ==> \result == 0        <-- FALSE OF THE PROGRAM
    def f(n: int) -> int:
        a = b = 5
        if n > 0: b = 7
        return a * 0 + b
    [+] Verification SUCCESS! All contracts formally proven.
```
`f(0)` returns **5**. `_py_stmt_assign` opens `target = stmt.targets[0]`. Where it hides:
when nothing else assigns the extra target the file at least fails L3-tc (`unbound function
or predicate symbol 'b'`); the dangerous case is a LATER assignment declaring the local, so
the lost initialisation silently becomes the declaration DEFAULT.
**A live victim sat in a CONVERTED, PROVED method**: `pure_ast._Parser._subscript_item`'s
`lower = upper = step = None`, in a file proved at 3103 goals. It survived by COINCIDENCE —
the dropped value is `None` and the declaration default for an option-typed local is
`IrONone`, the same value.

**2. `x[lo:hi:step]` dropped the step.** `ys = xs[1:4:2]` emitted
`Array.sub xs 1 (4-1)`; `ensures \result == xs[1] + xs[2]` — false, `f` returns
`xs[1]+xs[3]` — proved SUCCESS. REFUSED (a strided copy is a value-model feature). Census
**0 corpus / 0 mirror / 0 pycsl_lib / 0 live**: the refusal is completely inert.

**3. A `finally:` block was dropped ENTIRELY.** `try: self.v = 1 finally: self.v = 2`
emitted `self.v <- 1; ()`, and `ensures self.v == 1` proved. Module 5 DOES carry `orelse`
and `finalbody` into the IR; **Module 6's `_handle_try_stmt` reads `stmt.body` and
`stmt.handlers` and neither of the other two** — so this one is a LOWERING drop, one stage
past the other two. **THREE CONVERTED, PROVED MIRROR METHODS were live victims**, every one
a save/restore whose RESTORE was absent from the model, so the model asserted the saved
state was still in place: `pure_ast.visit_Try`, `pure_ast.visit_TryStar`,
`functions._refine_tuple_return_type`.

## THE METHOD — reuse it, it is the whole reason the window paid

1. Enumerate the dispatch table MECHANICALLY: for each `ast.<Node>` in
   `_PY_EXPR_HANDLERS`/`_PY_STMT_HANDLERS`, diff the node type's `_fields` against the
   field names the handler's source mentions. Then one notch wider: "which handler reads
   only element `[0]` of a list-valued field without iterating it anywhere?"
2. Probe every candidate with a contract that is **FALSE of the program**. A true contract
   failing to prove tells you NOTHING — it is indistinguishable from incompleteness. This
   step is what turned three "maybe" shapes into demonstrated unsoundnesses and nine clean
   verdicts.

FULL RESULT, so it is not re-derived:

| shape | verdict | disposition |
|---|---|---|
| chained comparison `a<b<c` | **UNSOUND** | fixed (normalization) |
| extended slice `x[lo:hi:step]` | **UNSOUND** | refused |
| multi-target `a = b = v` | **UNSOUND** | fixed (normalization) |
| `try ... finally` | **UNSOUND** | safe case emitted, rest ratcheted |
| annotated non-Name store `self.x: T = v` | fail-OPEN | fixed (normalization) |
| `for/while ... else` | fail-OPEN | refused |
| `with ... as X` | fail-OPEN | ratcheted (CTXBIND 48) |
| augmented store through a non-Name base | fail-OPEN | ratcheted (DROPPED 1) |
| keyword args `g(3, b=4)` | CLEAN | `(g 3 4)` |
| starred list `[*a, 3]` · tuple-unpack to attributes | fail-CLOSED | L3-tc type error |
| dict `{**a, "y": 2}` | fail-CLOSED | and correctly modelled by the bespoke lowering at its one converted site |
| nested `def` · f-string spec · `in` | CLEAN / conservative | — |
| **floor `//` and `%` with a NEGATIVE divisor** | **CLEAN** | `7 // -2 = -4`, `7 % -2 = -1` both prove and the Euclidean answers are REJECTED |
| negative index `a[-1]` · `del d[k]` · `except ... as e` · list `+=` | CLEAN | — |
| `#@` ANNOTATION forms (`\forall`, `\exists`, `\old`, `\old(a[i])`, `\old(self.f)`, call-site preconditions, `\length` ranges) | CLEAN | every deliberately-VIOLATING body was REJECTED |

## THE STRUCTURAL FINDING THAT SHAPED EVERY FIX — CARRY IT FORWARD

**None of the Module 5 defects could be fixed in the handler.** `_py_expr_compare`,
`_py_stmt_assign` and `_py_stmt_annassign` are CONVERTED mirror methods, and their models
are not their bodies: they are HAND-SYNTHESIZED whole-body lowerings
(`functions._emit_py_expr_compare_bespoke` and siblings) keyed on the METHOD NAME. Change
the live body and **mirror-sync stays GREEN (the bodies still match), L3-tc stays green, the
whole-file proof stays green — and the model silently stops being the body.** No gate plane
detects that.

So every Module 5 fix normalizes the INPUT instead, in `frontend/desugar.py`, run from
`Module5_IREmitter.generate_json` — the single choke point BOTH Module 5 entry paths go
through (`pycsl.py`'s pipeline and `ir_resolve.resolve`'s dependency sub-pipeline) and a
method that is `\trusted` in the mirror, so no mirror body moves. That leaves every
bespoke-modelled handler byte-identical AND MAKES ITS MODEL'S IMPLICIT CLAIM TRUE, because
the shape it cannot express no longer reaches it.
**RULE: before fixing a Module 5 handler, `grep _emit_py_.*_bespoke`. If it has one, fix
the input.** (The `finally` fix is in Module 6's `_handle_try_stmt`, which has NO bespoke
lowering, so it was edited directly — check first, then choose.)

## TWO NEW GATE PLANES

**`bin/check-dropped-mutation.py`** — the fail-OPEN no other plane can see. Every other
plane inspects what WAS emitted; a statement never emitted leaves nothing to inspect. It
classifies every assignment-family statement in the four verified/mirrored populations as
HANDLED / NORMALIZED / REFUSED / **DROPPED** / **CTXBIND** / **TRYFINAL**, the last three
ratcheted. Pure AST, no `why3`, seconds to run — **run it after ANY Module 5 or Module 6
lowering change**. Now: 28254 statements — 28122 HANDLED, 70 NORMALIZED, 3 REFUSED,
**1 DROPPED, 48 CTXBIND, 10 TRYFINAL**, each residue named with its reopening capability.

**`bin/check-avatar-frame-parity.py`** — #32's avatar-frame rule is INTRA-FILE ONLY. Every
`self.<m>(...)` in a converted method is applied through an abstract avatar whose `writes`
clause is the ONLY thing a caller knows about the callee's effect; a frameless avatar lets
every caller declare `assigns \nothing` however much the callee writes. `_module_method_
writes` holds only the methods THIS file declares, so a mixin method DEFINED elsewhere and
merely INHERITED here is minted frameless. Measured: `stmt_control_flow.mlw` emitted
`val self__add_abstract_op_1 (x0: int) : int` while `statements.mlw` emitted the same
method with `writes { self._abstract_ops }`. **SAME-FILE 0 (a hard 0 — #32's rule must keep
covering it); INHERITED 11 -> 7.**

## A DEAD CI GATE, RESTORED

`bin/run-conformance.sh` is a LEADING gate in `bin/run-reference-tests.sh` and it reported
`front-end conformance: 0 OK / 38 MISMATCH`. **Measured at the window-start commit
`e4d0a209` in a clean worktree: identical.** It had been red before this window — and a
permanently-red gate is worth exactly what a falsely-green one is. Every diff was PURELY
ADDITIVE (`only-golden=[]` in all 38): `param_ast_node_types`, `set_value_types`, and
`method_deps[*].assigns` — the last being #32's own `depends_method` frame capability,
landed without refreshing these goldens. Refreshed with the repo's own
`bin/regen-ir-conformance-goldens.py`; **the `.expected.mlw` goldens did not move at all**,
which is the check that makes it a refresh and not a blessing. Both corpora now pass.

## A CERTIFIED BOUNDARY THAT WAS NOT ONE — AND THE LESSON

**`expressions._ifexpr_seq_arm` is CLOSED and both frame-honesty populations are at ZERO.**
#32 recorded it as a boundary ("Why3 requires the declared `writes` be EXACTLY the model's
effect while the live closure names ~20 fields the model erases") — but #32 had ALREADY
BUILT what closes it and did not connect the two: (a) a `requires_method`/`depends_method`
window may DECLARE THE DEPENDENCY'S FRAME, and (b) `_writes_filtered_to_labels` keeps only
the targets the record carries as a LABEL. (b) is the answer to the objection (a) was held
back for. The honest 22-field `#@ assigns` on both leaves the SIX the record labels; the
avatar declares exactly those; Why3 accepts. The `writes {  }` it replaces was **the false
claim**.
**LESSON (cg): a CERTIFIED BOUNDARY is a claim like any other and can be invalidated by a
capability landed later IN THE SAME WINDOW. Re-run its spike before inheriting it — this
one refuted in a single emission.**

## A THIRD KIND OF SILENT FRAME HOLE

#32 named two (a declared frame the label filter erases; one the record cannot label). #33
adds: **a `\trusted` stub that carries `#@ requires` and `#@ ensures` and NO `#@ assigns`
LINE AT ALL.** The stub exists, its signature is checked, it is believed — and it says
nothing about its frame, so `_module_method_writes` has no entry and the avatar is
frameless. THREE of the four avatar closures were exactly this, which is why they cost ZERO
markers. Census: 11 of 476 `\trusted` stubs have no `#@ assigns` (some genuinely pure).

## THE NUMBERS

| | markers | grep | offset | ledger |
|---|---|---|---|---|
| #33 start (`e4d0a209`) | 447 | 472 | 25 | 3 |
| **#33 (this section)** | **451** | **476** | **25** | **3** |

The FOUR new markers, every one honest: `desugar._ChainDesugarer.visit_Compare` and
`desugar.normalize_stores` (they CONSTRUCT `pure_ast` nodes; `normalize_stores` also reads
`getattr(node, field, None)` with `field` a LOOP VARIABLE — the dynamic-attribute-name
reason that made #32 re-trust `copy_location`), and the two cross-mixin protocol stubs
`stmt_control_flow._add_abstract_op` / `._is_string_expr`.

| plane | #33 start | now |
|---|---|---|
| trusted-frame-honesty (total / model-visible) | 0 / 0 | **0 / 0** |
| converted-frame-honesty (total / model-visible) | 99 / 1 | **96 / 0** |
| computed-rhs-erasure | 5 / 0 | **2 / 0** |
| **dropped-mutation (NEW)** | — | **1 / 48 / 10** |
| **avatar-frame-parity (NEW)** | — | **0 same-file / 7 inherited** |
| IR conformance (front-end) | **0 OK / 38 MISMATCH** | **38 OK / 0** |
| yield-erasure | 0/2/1 | 0/2/1 |
| mirror-signature-drift | 0 | 0 |
| shadowed-selfcalls | 14 / 121 | 14 / 121 |
| untrusted-emitted | 862/846/0/0 | 865/849/0/0 |
| corpus byte-diff | 0 | **0** (819 files, re-measured for EVERY increment) |
| fidelity (both scripts) | DIVERGED 2 | DIVERGED 2 (the baseline pair) |
| mirrors L3-tc | 52/52 | **53/53** |

## THE FRAME-HONESTY GATE EARNED ITS KEEP, IN REAL TIME

`_ChainDesugarer.visit_Compare` was first written with `#@ assigns \nothing` and
`check-trusted-frame-honesty` REJECTED IT the same hour — the live body writes `self._n`,
the deterministic temp counter. Declared honestly; the plane went back to 0/0. **A new false
frame, caught by a machine, minutes after it was written.**

## THE CORPUS WITNESSES, ALL NEGATIVE-TESTED

| file | witnesses | with the fix removed |
|---|---|---|
| `0969_chained_comparison.py` | plain chain, 3-comparator chain, pure-builtin middle (`len`), user-call middle (the walrus) | **8 non-Valid, FAILED** |
| `0970_annotated_field_store.py` | `self.v: int = 5` outside `__init__` | `set_to` emits an EMPTY body |
| `0971_multi_target_assign.py` | `a = b = 5` + conditional reassign; `p = q = three()` | L3-tc fails on unbound `q` |
| `0972_try_finally.py` | `try/finally` with no handlers | `ensures self.v == 2` Unknown |

## TWO DESIGN DECISIONS WORTH INHERITING

**THE WALRUS, NOT A REFUSAL.** The chain expansion mentions the middle operand twice while
Python evaluates it once. The first version REFUSED a non-repeatable middle and **broke four
reference-corpus files** (0836/0862/0865/0867 — all `assert 0 <= f() < 256` inside a
`main()` that is walked but not emitted, which is why no gate had ever fired on them). The
shipped version binds it with a WALRUS on its single evaluation:
`a <= (_pycsl_cmp_1 := f()) and _pycsl_cmp_1 <= b` — Python's own rule written in Python.
Same principle in `normalize_stores`: the RHS of `a = b = v` is re-mentioned only when it is
a `Constant` or a `Name` (both SHARE their object, so `a = b = []` binding ONE list is
preserved); anything else is bound to a temporary. **Temporaries are numbered from a
per-pass counter, never `id(...)`** — verified by emitting the whole corpus TWICE (diff 0).

**EMIT THE SAFE CASE, COUNT THE REST.** `finally` runs on every exit path and only the
normal one is expressible by appending the block, so it is appended exactly when no other
path exists: no handlers, and no `raise` anywhere in the LOWERED body. That single string
test is complete — every jump-out (`return`/`break`/`continue`/exception) lowers to a
`raise` — and it tests the EMITTED body, so it cannot miss a nested one.

## VERIFICATION STATE — COMPLETE, NOTHING PENDING

**FOURTEEN whole-file proofs, EVERY ONE `rc=0` and `Verification SUCCESS`, and NO PROVER
PROCESS LEFT RUNNING.** Logs and exit codes in `scratchpad/w6/proofs/` with `RC.txt`.

| mirror | goals | run |
|---|---|---|
| `frontend/pure_ast.py` | 3103 | SUCCESS (the `try/finally` + multi-target content) |
| `module6_whyml/stmt_control_flow.py` | 1874 | SUCCESS x2 (dict/set re-host; then `finally` + `try/else` + protocol stubs) |
| `Module6_WhyMLTranspiler.py` | 706 | SUCCESS x2 (`_ifexpr_seq_arm` frame; then protocol stubs) |
| `module6_whyml/functions.py` | 1199 | SUCCESS (poly reader + `finally`) |
| `module6_whyml/expressions.py` | 1069 | SUCCESS x2 (dict/set re-host; then the `_ifexpr_seq_arm` honest frame) |
| `module6_whyml/statements.py` | 923 | SUCCESS x2 (dict/set re-host; then protocol stubs) |
| `frontend/ir_resolve.py` | 793 | SUCCESS (the dangling refusal's `raises` line) |
| `frontend/__init__.py` | — | SUCCESS (same) |
| `module6_whyml/types.py` | — | SUCCESS (dict/set re-host) |
| `frontend/desugar.py` (NEW mirror) | — | SUCCESS |

One entry in `RC.txt` reads `rc=143 frontend_pure_ast`: that run was KILLED as SUPERSEDED
when the `try/finally` fix changed `pure_ast.mlw` under it. It is not a failure, and the
replacement (`frontend_pure_ast_tf33`) is the SUCCESS above.

**CORPUS BYTE-DIFF 0 ACROSS THE WHOLE WINDOW**, not just per increment: all 815 files that
existed at `e4d0a209` emit byte-identically at HEAD, re-measured from a worktree pinned at
that commit. The only new outputs are this window's four witnesses.

FULL BATTERY AT HEAD, `why3` on PATH:
  · markers **451**, stable over 3 samples · grep 476 · offset 25 · unattached 0 · ledger 3
  · 53/53 mirrors L3-tc GREEN · corpus byte-diff **0** (819 emitted = 815 + 4 witnesses)
  · fidelity DIVERGED **2** on both scripts (the documented baseline pair);
    mirror-check 3 drifts == the `e4d0a209` baseline, re-measured in a clean worktree
  · frame-honesty **0/0 trusted, 0/96 converted** — BOTH POPULATIONS AT ZERO MODEL-VISIBLE
  · avatar-frame-parity **0 same-file / 7 inherited** (NEW plane)
  · dropped-mutation **1 DROPPED / 50 CTXBIND / 9 TRYFINAL / 0 DANGLING** (NEW plane)
  · computed-rhs-erasure **2 / 0** · yield-erasure 0/2/1 · mirror-signature-drift 0
  · mirror-field-parity 0 NEW · untrusted-emitted 865/849/**0**/0 · shadowed-selfcalls 14/121
  · non-vacuity (`--emit`): no NEW erasure, 8 known gated, **0 input-blind**
  · **IR conformance: BOTH corpora pass** (was 0 OK / 38 MISMATCH at window start)
  · doc-coherency OK · tree clean · no prover process running

**THE PROJECT'S OWN FULL SUITE, run as a closing integration check: `877/900`.** All 23
failures are PRE-EXISTING and that is established two ways, not assumed: (a) corpus
byte-diff 0 means every one of those tests' `.mlw` is BYTE-IDENTICAL to the window-start
tree, so its verdict cannot have changed; and (b) the 0211-0226 block was re-run at
`e4d0a209` in a clean worktree and fails identically (5/16 passed there too). **All four of
this window's witnesses PASS**, as does #32's `0968`. Worth knowing for #34: at
`e4d0a209` the suite did not even reach the tests — it exited on the dead IR-conformance
gate, which this window restored.

A HARNESS BUG WAS FOUND BY THAT RUN AND FIXED: `run-reference-tests.sh` derived
`file_num` with `sed 's/^0*//'` alone, so a descriptively-named test left a non-numeric
token in an ARITHMETIC comparison — 46 lines of bash noise per run, and the comparison
ERRORS OUT rather than evaluating, so `--start-at`/`--stop-at` silently stopped filtering
exactly the tests whose names say what they test (everything from `0925` onward). One
`sed` stops at the first non-digit; `--start-at 968 --stop-at 972` now selects 5 tests,
5/5 pass, zero warnings.

## WHERE THE LADDER STANDS FOR #34

1. **`avatar-frame-parity` INHERITED 7 -> lower.** Three named routes, all measured:
   - `functions._is_string_expr` / `_is_emit_ir_expr` / `_collect_array_var_assigns`:
     **TYPE-MODEL boundary**, not a frame one. A local stub also RETYPES the avatar's
     parameter (int fallback -> `emit_ir`) and `functions.py` fails L3-tc at a call site
     whose local is a map. The frame and the type ride on the same declaration.
   - the three `_py_stmts_to_ir`: a **FOUR-FILE SEGMENT**. The coarse-declaration shape is
     right and needs no receiver, but the caller is `_py_stmt_match` in the IMPORTED
     `Module5_IREmitter.py`, so the source frame lands there and re-emits that mirror
     (1499 goals) plus all three importers.
   - `expressions._materialize_bridge`: newly surfaced, not yet triaged.
2. **`computed-rhs-erasure` 2, and the two causes are DIFFERENT**:
   `_handle_field_get_expr`'s `_pg2` (the class HAS a record but `_property_getters` is not
   one of its LABELS) and `unparse_inner`'s `unparser` (`type(self)(...)`, a DYNAMIC CLASS
   CONSTRUCTION — no capability named yet).
3. **`dropped-mutation` residues**: TRYFINAL 10 (run the block on handler arms and a
   `Return_t` re-raise arm), CTXBIND 48 (an `__enter__`/`__exit__` protocol), DROPPED 1
   (a sound write-back through a subscript — the same boundary `_py_stmt_assign` names).
4. **`proof2why3`'s `term` family (9 stubs)** — unchanged from #32: a COST/SCALE boundary
   needing a general ADT-value lowering. NOT a floor.
5. **THE AUDIT VEIN IS NOT EXHAUSTED.** Swept: the Module 5 assignment family, the Module 5
   expression dispatch table, Module 6's `_handle_try_stmt`, and the `#@` annotation forms.
   NOT yet swept the same way: **the rest of Module 6's `_handle_*` lowerings** (the same
   "reads some fields, drops the rest" question), and Module 3's `#@` attachment.

## INSTRUMENT FACTS #33 ADDS

1. **A census over the mirror is not a census over what the pipeline PARSES.** The `for/else`
   refusal measured "0 in the mirror" and then rejected `ir_resolve.py`: `--import-path
   src/pycsl` makes the LIVE modules import stubs whose helpers are lowered (214 from
   `Module5_IREmitter` alone). Two live `for ... else`-with-`break` loops had been silently
   dropped all along. **Scope every census over the LIVE tree too.**
2. **Probe a suspected drop with a contract that is FALSE of the program.** A true contract
   failing tells you nothing.
3. **`getattr(node, "<name>", None)` erases to the constant `0` in the model; `node.<name>`
   projects.** `reject_unmodelled`'s first draft used `getattr` and emitted `... && (0 <> 0)`
   — a check that can never fire. Reading the emitted WhyML is the only way to see it.
4. **THE LIVE EMITTER CARRIES NO `#@` CONTRACTS.** Every `#@ assigns` in `src/pycsl` is
   inside a comment or docstring. So no import-based cross-file contract lookup can ever
   work — the emitter resolves imports against the live tree. That is why the avatar-frame
   residue must be closed in mirror SOURCE, and it is a structural fact, not a gap.
5. **`src/pycsl_lib/json/scanner.py` and `encoder.py` do NOT type-check** — measured
   identically at `e4d0a209`, so pre-existing. The stdlib population is not uniformly
   verified; its 25 `\trusted` lines are outside this campaign's metric.
6. `bin/check-dropped-mutation.py` and `bin/check-avatar-frame-parity.py` are cheap; the
   latter needs `--emit-dir` and REFUSES to run without one.
7. `scratchpad/w6/` mirrors #32's `w5`: `wt/` is a worktree for measuring while the main
   tree proves, `base/` is pinned at the window-start commit for byte-diff baselines,
   `proofs/` holds every log plus `RC.txt`. `/tmp/framefix.py` and `/tmp/framefix2.py` drive
   the caller frame fixpoint against Why3's own error text (the second APPENDS to a
   non-`\nothing` `#@ assigns` instead of replacing `\nothing`).

# HANDOFF — #32 (2026-09-02, WINDOW 3): **446 -> 447 markers (ONE honest re-trust) and
# `check-trusted-frame-honesty` 82 -> 19 — because the probe reported only THREE CLEAN
# candidates in the whole tree, TWO of them were hollow in ways no marker could see, and
# the honest ladder turned out to be the FRAME plane, where a `\trusted` stub's
# `#@ assigns` was not merely assumed but UNOBSERVABLE.**

## THE LAST TWO INCREMENTS (and the one the FIDELITY plane refused)

- **FAITHFUL MAP TRUTHINESS, and it revived two DEAD BRANCHES.** `_to_bool` had been
  returning the CONSTANT `true` for an hval-map local, so `if not vinfo:` lowered to
  `not true` = false and the guarded path was UNREACHABLE IN THE MODEL — an
  under-approximation of the program's own behaviour, in two proved files. Python's
  `if <dict-or-set>:` is NON-EMPTINESS and a Why3 `map k (option v)` states it EXACTLY, so
  the fix is one `val function map_nonempty` with the DEFINITIONAL postcondition
  `result <-> (exists k. Map.get m k <> None)` — no over-approximation and NO AXIOM
  (ledger stays 3). `expressions.py` and `stmt_control_flow.py` both move.
- **THE `dict`/`set` HALF OF THE `getattr` CAPABILITY WAS BUILT, MEASURED GREEN, AND THEN
  REVERTED BY THE FIDELITY PLANE.** It works — 52/52 mirrors L3-tc, corpus byte-diff 0,
  `computed-rhs-erasure` 5 -> 3 — but one of its three rules has to live in
  `types._rhs_yields_map`, which is a CONVERTED mirror method, so the live change must be
  copied into the mirror verbatim, and the copied body does NOT type-check there (the
  mirror's refined `val_ir: "ExprIR"` signature reflects `.get("args")` to
  `args_of : array emit_ir`, so the element index yields an `emit_ir` where an `int` is
  wanted). DIVERGED went 2 -> 3, which is a FAILURE, not a ratchet. Reverted; the
  reopening capability is recorded beside the gate constant: **host the recognizer where
  the mirror can carry it — a `\trusted` helper, or a reflection-safe spelling.**
  This is lesson (cf): **a capability's cost includes WHICH FUNCTION it has to live in.**
  Check the host's trust status BEFORE writing the rule.

## VERIFICATION STATE AT WINDOW END — COMPLETE

**EVERY mirror `.mlw` that moved this window was re-proved, `Verification SUCCESS`, 0
non-Valid.** Fourteen whole-file proofs, all detached under `setsid`, all on the FINAL tree
content:

| mirror | goals | verdict |
|---|---|---|
| `frontend/pure_ast.py` | 3097 | SUCCESS |
| `module6_whyml/stmt_control_flow.py` (honest frames, then map truthiness) | 1874 | SUCCESS x2 |
| `frontend/Module5_IREmitter.py` | 1499 | SUCCESS |
| `module6_whyml/functions.py` | 1199 | SUCCESS |
| `module6_whyml/expressions.py` (getattr-scalar; then avatar frame + honest frames + drift + getattr-str + map truthiness) | 1069 | SUCCESS x2 |
| `module6_whyml/statements.py` (getattr-scalar; then honest frames + drift) | 922 / 923 | SUCCESS x2 |
| `frontend/ir_resolve.py` | 793 | SUCCESS |
| `Module6_WhyMLTranspiler.py` | 706 | SUCCESS |
| `module6_whyml/auto_trust.py` | 280 | SUCCESS |
| `module6_whyml/expr_ghost_spec_ops.py` (honest frames, then drift) | 123 | SUCCESS x2 |
| `module6_whyml/scc.py` | 50 | SUCCESS |
| `frontend/ConcurrencyChecker.py` | 5 | SUCCESS |

`module6_whyml/stmt_control_flow.py` is the one that mattered most: it proved WITH the
previously-dead branch made reachable by faithful map truthiness.
| `pycsl.py` | 735 | SUCCESS |

| `frontend/pure_ast.py` (again, the zero-frame pass) | 3103 | SUCCESS |
| `module6_whyml/functions.py` (again, the zero-frame pass) | 1199 | SUCCESS |

**SEVENTEEN whole-file runs, rc=0 and `Verification SUCCESS` on every single one, and NO
PROVER PROCESS LEFT RUNNING.** Nothing this window is banked on an unproved tree. Logs and exit codes are in `scratchpad/w5/proofs/`, and
`scratchpad/w5/proofs/superseded/` holds three runs that were KILLED (rc 137/15) because a
later increment superseded their content — those are not failures, and one of them
(`module6_whyml_statements_2.log`) had already reported SUCCESS before the kill.

THE FULL BATTERY, driver-verified fresh at window end, `why3` ON PATH:
  · markers **447**, stable over 3 samples · grep 472 · offset 25 · unattached 0
  · corpus byte-diff **0** — 814/814 identical to the window-start tree (the 815th file is
    this window's own new corpus test `0968`)
  · all **52/52** mirrors L3-tc GREEN
  · fidelity DIVERGED **2** on both scripts (the documented baseline pair)
  · non-vacuity (`--emit`): no NEW erasure, 8 known gated, **0 input-blind**
  · shadowed-selfcalls **14 / 121** (ratchet 14)
  · untrusted-emitted 862 un-trusted, 846 definitions, **0 re-abstracted**, 0 absent
  · frame-honesty **0/0 trusted (was 0/82 — THE PLANE IS AT ZERO), 1/99 converted
    (was 4/133)**
  · yield-erasure **0 value-erasing / 2 suspension (ratchet 2) / 1 modelled**
  · computed-rhs-erasure (NEW PLANE) **5 / 0**
  · mirror-signature-drift **0 (ratchet now a HARD 0, was 16)**
  · ledger **3** — no axiom added by any capability this window (`map_nonempty` is a
    `val function` with a DEFINITIONAL postcondition, not an axiom)
  · tree clean

## WHAT LANDED AFTER THE FIRST DRAFT OF THIS SECTION (same window, later)

| plane | at first draft | at window end |
|---|---|---|
| trusted-frame-honesty | 19 / 0 | **19 / 0** |
| converted-frame-honesty | 125 / 1 | **125 / 1** |
| **mirror-signature-drift** | 16 (ratchet 16) | **0 (ratchet now a HARD 0)** |

- **THE MIRROR-SIGNATURE-DRIFT PLANE IS AT ZERO.** All sixteen repaired: ten stubs MISSING
  a live parameter (`_handle_dotted_call` +`arg_irs`, `_handle_join_call`
  +`local_refs`/`invariant_ctx`/`subst`, `_handle_isinstance` +`local_refs`,
  `_call_record_constructor` +`kwargs_map`/`kwargs_ir`, `_emit_first_assign` +`local_refs`,
  `scc.sort_functions_by_scc` +`extra_concrete`, `ir_resolve.resolve` +`import_paths`,
  `auto_trust._build_witness_str` +`array_elem_witnesses`, and both Module5_IREmitter
  `dedup` stubs) and six pure RENAMES. The renames matter because they BLOCKED the
  signature-preserving port: those six stubs could not be MEASURED at all. They now can be,
  and the first measurement is recorded — all eight probe as L3TC-FAIL, four of them on
  `int` vs `emit_ir`, confirming #31's spike. Ratchet 16 -> 0 and 0 is a HARD FLOOR.
- **`getattr(self, "<str field>", …)` is STRING-TYPED** (`_is_string_expr`), fixing a third
  wrong lowering: an `int_to_string (if (0 <> 0) || …)` where the alias name belonged. The
  `dict`/`set` extension was MEASURED AND REFUSED in the same spike (breaks three files, on
  the two residues already named).
- **A `depends_method`/`requires_method` WINDOW MAY NOW DECLARE THE DEPENDENCY'S FRAME.**
  The window accepted `requires`/`ensures` only, so a declared dependency was FRAMELESS BY
  CONSTRUCTION and every method calling it could claim `assigns \nothing`. Wired through
  weaver -> Module5 IR -> `_mixin_dep_pseudo_functions`, three doc surfaces, and corpus
  witness `0968_requires_method_frame.py` with BOTH halves negative-tested.
  **It is deliberately NOT yet used by the mirror, and the reason is a CERTIFIED
  BOUNDARY:** annotating the `_seq_operand` requirement does give its avatar
  `writes { _pyobj_state }` and Why3 then correctly rejects `_ifexpr_seq_arm`'s `\nothing`
  — but the caller cannot then state an honest frame, because Why3 requires the declared
  `writes` to be EXACTLY the model's effect while the live closure names ~20 fields the
  model erases. Over-claim is rejected, under-claim is the direction #31 refused.
  **REOPENING CAPABILITY: lower a declared `#@ assigns` to `writes { _pyobj_state }` PLUS
  only the labels the model actually writes, decided as a FIXPOINT against Why3 rather
  than read off the declaration.** That single rule closes the last model-visible offender
  and is the natural successor to everything this window built.

## THE PLANE THAT WENT TO ZERO

**`check-trusted-frame-honesty` is at 0, from 82 at window start.** Every `\trusted` stub
in the mirror now declares a frame that is TRUE of its live body. A `\trusted` stub's
`assigns` is ASSUMED and never checked, so a false one is an unsoundness no proof plane can
see — that is the plane's whole reason to exist, and it is now at its floor. `82 -> 28 ->
19 -> 0`, and the converted population came with it: `133 -> 99`, model-visible `4 -> 1`.

Together with `mirror-signature-drift` `16 -> 0`, TWO WHOLE PLANES CLOSED this window.

The last step needed one more emitter rule, and its absence is exactly what had stalled the
`pure_ast.py` pass after three fixpoint iterations: **a CONCRETE callee's `_pyobj_state`
effect reaches its caller too.** `_obj_state_written` was set when a body registered a
`setattr_*` op or minted an avatar with the coarse cell, but a caller can inherit the effect
from an already-emitted concrete sibling (`let <callee> … writes { _pyobj_state }`) and that
route set no flag — so the caller emitted `writes { }` and Why3 rejected it with no
source-level knob to fix it. `_emit_function` now RECORDS every symbol it emits with the
cell in its frame and re-arms the flag when the emitted body applies one. Precise in both
directions, which matters: the cruder "always emit the coarse cell when the filtered set is
empty" rule was tried first and REFUSED, because Why3 then says *"variable `_pyobj_state`
does not occur in this expression"* for every method that really writes nothing.

**HONEST CAVEAT, written beside the constant: the closure can still UNDER-approximate (the
#31 `_walk_body` blind spot), so 0 means "nothing KNOWN false", not "every declaration
proven true".** Sharpening the closure again — as #31 did when it found `self.xs.append(v)`
— is the way to test that, and it should be expected to push the number back up. That would
be a better instrument, not a regression.

## THE HEADLINE, STATED PLAINLY
**There are no free conversions left.** The repaired whole-tree probe, re-run twice at
HEAD, reports **1 CLEAN out of 446** — and that one is `_ContractParser._err`, which #31
already refuted on the non-vacuity plane. Every remaining marker needs a NEW CAPABILITY;
none is one port away. That is the single most important state fact for the next relaunch,
and it is why this window's yield is honesty and capability rather than count.

## THE NUMBERS

| | markers | grep | offset | ledger |
|---|---|---|---|---|
| #32 start (`b2764659`) | 446 | 471 | 25 | 3 |
| **#32 (this section)** | **447** | **472** | **25** | **3** |

| plane | #32 start | now |
|---|---|---|
| trusted-frame-honesty (total / model-visible) | 82 / 0 | **19 / 0** |
| converted-frame-honesty (total / model-visible) | 133 / 4 | **125 / 1** |
| computed-rhs-erasure (NEW plane) | — | **5 / 0** |
| yield-erasure | 0 / 2 / 1 | 0 / 2 / 1 |
| mirror-signature-drift | 16 (0 converted) | 16 (0 converted) |
| corpus byte-diff | 0 | **0** (814/814, re-measured for EVERY increment) |
| fidelity (both scripts) | DIVERGED 2 | DIVERGED 2 (the baseline pair) |
| mirrors L3-tc | 52/52 | **52/52** |

+1 marker is the RIGHT direction here: `pure_ast.copy_location` was a hollow conversion and
is now honestly `\trusted`.

## FIVE INSTRUMENT FINDINGS, AND ONE IS ABOUT THE SHELL YOU RUN IN

### (bl) **`why3` IS NOT ON THE DEFAULT PATH, AND `pycsl.py` PRINTS `L3-tc ✓` WHEN IT IS ABSENT**
`_why3_typecheck` returns `(True, "(why3 not found — typecheck skipped)")` by design — a
missing prover must not be reported as a typecheck failure. The consequence is that **any
L3-tc sweep run from a shell without `/home/fabrice/.opam/framac-coq8/bin` on PATH is a
FALSE GREEN**, and this session wrote one and believed it for three increments. It was
caught only because `bin/probe-conversion-candidates.py` sets that PATH itself and
disagreed with a hand-rolled sweep on the same file.
**EVERY L3-tc sweep must `export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH`.**
`scratchpad/w5/l3sweep.sh` does; use it. Corollary: `--keep-mlw` keeps the `.mlw` even when
the run FAILS, so "a .mlw appeared" is not evidence of anything.

### (bm) The probe read the EMITTER'S OWN PROGRESS LINE as a why3 diagnosis
`_DIAG_RE` carries an `Unsupported` alternative; `proof2why3/ir.py` declares a class
literally NAMED `Unsupported`, so the emitter prints
`[*] Imported class from 'proof2why3.ir': Unsupported (record + 0 method stub(s) …)` above
every real message and `_idx[0]` picked it. **25 of 378 L3TC-FAIL verdicts — the ENTIRE
`proof2why3` subtree — recorded that line instead of a blocker.** The ranked census the
ladder navigates by was blind to that subtree, whose real shape is one homogeneous family
(`term` vs `int`, 9 stubs). Fixed: a line with a pipeline prefix is never a diagnosis.

### (bm2) The probe's FALLBACK read STDERR
`tail = _ls[-1:]` over stdout+stderr; `core_ir_semantic`'s C8 Union warning prints its own
SOURCE LINE to stderr and is physically last, so 8 candidates recorded `], union_vars,
fname)` as their blocker. Their real blocker is the pipeline's `[!] PIPELINE ERROR:` —
the HETEROGENEOUS LIST LITERAL refusal — which merges them into a 15-stub family.

### (bn) TWO NEW FACADE CLASSES the marker list could not see — and a new gate plane
Both were found on the same whole-tree census, both were reported **CLEAN**:
- **PARAM-FIELD MATERIALIZED AS A FRESH CONSTANT ARRAY.** `PyCSLWeaver._attach_loop_contracts`'s
  entire body is three `node.<listfield>.append(c)`; `node` is an int-typed parameter, so
  the emitter binds `let node_csl_invariants = Array.make 1024 0 in` and every read AND
  every append lands in that empty local. Reported CLEAN because the parameter name `node`
  DOES appear — inside the fresh local's own name.
- **COMPUTED RHS ERASED TO 0.** `Module3_Weaver._region_bound_str`'s
  `v = getattr(node, "value", None)` emitted `v := 0`, so `!v <> 0` is false on every path
  and the whole method collapses to `return "<expr>"`. Not abstracted to an opaque op —
  replaced by a LITERAL — which is why no marker fires.
Both are probe markers now (negative-tested), and both are a standing gate:
**`bin/check-computed-rhs-erasure.py`**, which audits the CONVERTED population the probe
never looks at. It found SIX there; one (`copy_location`) is re-trusted, ratchet is now 5/0.

## THE CAPABILITIES (every one corpus byte-diff 0)

1. **`getattr(self, "<field>", <default>)` reads the MODELLED FIELD for a SCALAR field.**
   `_lower_getattr` already did this — but only when the DEFAULT was a STRING literal, so
   `None` and `{}`, the two commonest spellings of the same idiom (1224 sites in the live
   emitter), fell through to "emit the default" and became the literal `0`. The license is
   carried by the `_all_record_fields` test that already guards the branch: a field the
   model DECLARES is present, so the default is unreachable. **Two WRONG LOWERINGS fixed:**
   `tmp_count := (0 + 1)` -> `tmp_count := (self._slice_set_tmp_counter + 1)` (a slice-temp
   counter restarting from 0 on every call) and `not (0 <> 0)` -> `not (self._scope_dyn_exec
   <> 0)` (a guard that was unconditionally TRUE). Both re-proved: statements.py 922 goals
   SUCCESS, expressions.py 1069 goals SUCCESS.
   **The BLANKET relaxation was MEASURED AND REFUSED** — fail-closed but blocking, with
   three named residues, each an ADJACENT mechanism that has not met this shape:
   local first-assign kind inference not seeing through `getattr`; map-typed field
   TRUTHINESS; string-typed field TRUTHINESS (`_to_bool` has the exact rule already).
2. **A list literal is `array string` when every element is STRING-TYPED**, not only when
   every element is a string LITERAL (`_is_string_expr` instead of `type == "String"`).
   Unblocks the 15-stub heterogeneous-list family and closes a LATENT UNSOUNDNESS: an
   all-VAR literal `[s1, s2]` carried no string literal, so the WL-04g guard let it through
   and the int-coercion fallback HASHED both elements into an `array int`.
3. **The TERM CARRIER reaches aliased locals and `Term`-annotated PARAMETERS.**
   `_term_alias_fixpoint` (a local bound from another term local is term-typed, iterated);
   and a `Term` parameter joins `_term_local_vars` so `t.body` projects through the
   inductive's arm instead of the opaque `get_body : int -> int`.
4. **THE AVATAR CARRIES THE CALLEE'S FRAME.** See below — the most consequential one.

## THE STRUCTURAL FINDING: A `\trusted` STUB'S `#@ assigns` WAS UNOBSERVABLE

`_writes_filtered_to_labels` keeps only `#@ assigns` targets the emitted record carries as
a field LABEL. When the filter empties the set, `field_spec` stayed None and the
caller-side avatar was minted as a bare `val self__<m>_<n> (x0: …) : unit` — no receiver,
no frame. **MEASURED EXACTLY:** giving `expressions.py`'s `_add_abstract_op` protocol stub
its honest `#@ assigns` left `module6_whyml_expressions.mlw` BYTE-IDENTICAL, while the same
edit in `statements.py` (where the label IS emitted) produced
```
val self__add_abstract_op_1 (self: statementemissionmixin) (x0: string) : unit
  writes { self._abstract_ops }
```
and forced six callers to tell the truth. So repairing the 82 declarations would have
changed NOTHING wherever the named field is not an emitted label.

**THE RULE BUILT (the caller-side twin of what `functions._emit_function` already applies
to a method's OWN definition — "the source names ANY assigns target -> add `_pyobj_state`
to the frame"): when the callee DECLARES a non-empty `#@ assigns` and the label filter
empties it, the avatar declares `writes { _pyobj_state }` and the caller's emission is
flagged `_obj_state_written`, so the caller's own definition inherits the cell.** The
coarse single cell over-approximates what may change and never claims a preservation the
source does not guarantee.
**BLAST RADIUS, MEASURED AND FAR SMALLER THAN THE FINDING SUGGESTED: 51 of 52 mirrors
byte-identical; only `expressions.py` rejected, with exactly the honest message.** The
fixpoint closed in 5 iterations.

With that in place the honest-frames pass became meaningful:
- **54 `\trusted` stubs given their honest `#@ assigns`**, derived PER STUB from the SAME
  live transitive closure `bin/check-trusted-frame-honesty.py` computes
  (`scratchpad/w5/honest_trusted_frames.py`), with the caller fixpoint closed by
  `scratchpad/w5/framefix3.py` (per-method derived field sets, NOT #31's blanket 17).
  **82 -> 28.**
- **Both label filters now FAIL CLOSED when the class has no record in the file**
  (`type functionemissionmixin = int` — `hasattr(self, "_emitted_record_field_labels")` is
  literally False). "Absent registry -> filter nothing" is safe only when the absence means
  "we did not build it"; here it means "there are NO labels", so every name is unbound.
  `functions._emit_function` fails closed AND sets a coarse flag so the effect is still
  SAID against `_pyobj_state`. **28 -> 19.**
**The entire residue 19 is `pure_ast.py`**, left alone only because its whole-file proof
was in flight. Finishing it is the first item for the next relaunch and needs no new idea.

**HONEST CAVEAT, recorded beside the ratchet:** the closure can still UNDER-approximate
(the #31 `_walk_body` blind spot), so 19 is a floor on what is KNOWN false, not a proof
that the other 271 are true.

## WHERE THE LADDER STANDS FOR #33

0. **Finish the frame-honesty pass on `pure_ast.py`** — 19 -> ~0, mechanical, tools written
   (`scratchpad/w5/honest_trusted_frames.py` + `scratchpad/w5/framefix3.py`), one pure_ast
   re-proof. Do it FIRST; it is the cheapest remaining honesty win in the tree. It was left
   out of #32's pass for one reason only: its whole-file proof was in flight.
0b. **Re-host the `dict`/`set` half of the `getattr` capability.** It is BUILT and MEASURED
   (52/52 L3-tc, corpus byte-diff 0, `computed-rhs-erasure` 5 -> 3); it was reverted purely
   because one rule lives in `types._rhs_yields_map`, a CONVERTED method whose mirrored body
   does not type-check. Move that one recognizer into a `\trusted` host or write it in a
   reflection-safe spelling and the increment lands as-is. The exact diff is recoverable
   from this window's REFUTED-AND-NARROWED commit.
1. **The last model-visible converted offender**, `expressions._ifexpr_seq_arm`: its
   callee's now-declared frame is still an UNDER-claim of the live closure. One level
   deeper than what this window fixed.
2. **The three named residues of capability 1** (map/string field truthiness in `_to_bool`;
   first-assign local kind inference seeing through `getattr`). Each is a one-rule addition
   with an ADJACENT mechanism that already exists, and together they close the remaining
   FIVE `computed-rhs-erasure` offenders.
3. **The `proof2why3` `term` family (9 stubs) is a genuine COST/SCALE boundary**, now
   correctly characterised for the first time. These are IMPERATIVE passes over the
   certified `term` inductive; converting them needs a GENERAL ADT-value lowering —
   constructor CALLS (`Forall(b, ty, body)` currently emits a RECORD LITERAL where a `term`
   is expected), `list term` locals, `Var(...)`-vs-`term` — not the spec-driven generator
   that produced the already-proved `_flip_comparisons`. Multi-session; NOT a floor.
4. **The heterogeneous-list-literal family, 15 stubs** — capability 2 moved its first
   blocker; the residue is literals genuinely mixing a string with a non-string.
5. `<x> or []` — **DEMOTED, and this is a measurement, not an opinion.** It IS a wrong
   lowering, but a fresh emission of all 52 mirrors contains **ZERO** occurrences of the
   boolean-collapse shape: all 56 converted methods containing `or []` already route
   through the pyval / emit_ir / closed-key recognizers. So it is a BLOCKER for 58 trusted
   stubs, NOT a live defect in the proved population — and #31's own note stands that the
   residue needs the empty-collection value-type inference anyway.
6. The 16 mirror-signature drifts and the `TypedDict`-view device — unchanged from #31.

## OPERATIONAL FACT #32 PAID FOR
**Do not run more than TWO whole-file mirror proofs concurrently on this machine.** Each
`pycsl.py --provers …` run ends with an internal VACUITY phase that re-proves every goal
individually at `--timelimit 5`, and that phase is itself parallel — so four concurrent
whole-file proofs put the 12-core box at load average 20 and every one of them slowed to a
crawl (`pure_ast.py` sat in its vacuity phase for over two hours). Queue them
sequentially in one detached `setsid` script, or at most two scripts.

## INSTRUMENT FACTS #32 ADDS
1. `scratchpad/w5/l3sweep.sh <outdir>` — the ONLY L3-tc sweep to use (it exports the opam
   PATH; see lesson (bl)). Writes every mirror `.mlw` into `<outdir>` for byte-diffing.
2. `scratchpad/w5/diag.sh <mirror-rel> <Class:name>` — port, emit with the right PATH,
   print the why3 error plus the surrounding emitted WhyML, restore the tree.
3. `scratchpad/w5/honest_trusted_frames.py` — rewrite every `\trusted` stub's
   `#@ assigns` from the live transitive closure. `scratchpad/w5/framefix3.py` — the
   caller fixpoint with PER-METHOD derived fields (env vars `FF_REL`, `FF_MAX`).
4. A git WORKTREE (`git worktree add`) is the right place to measure an emitter change
   while a whole-file proof is running in the main tree; symlink `.venv` into it so
   `bin/byte-diff-sweep.sh` works.
5. A backgrounded probe killed by a tool timeout does NOT run its `finally`: it leaves the
   ported mirror file DIRTY. Check `git status` after any interrupted sweep.

---

# HANDOFF — #31 (2026-09-02, WINDOW 3): **455 -> 446, seven emitter capabilities, two NEW
# GATE PLANES, and eleven conversions of which the GATES REVERTED TWO — but the findings
# that matter are that the CANDIDATE PROBE was measuring the wrong function for 40% of the
# tree, that a CONVERTED GENERATOR's `yield`ed values are dropped on the floor, and that
# `check-trusted-frame-honesty` could not see `self.xs.append(v)`.**

## VERIFICATION STATE — COMPLETE, NOTHING PENDING
**TWENTY mirror `.mlw` files moved this window and EVERY ONE was re-proved**, `Verification
SUCCESS` / 0 non-Valid: `pure_ast.py` (**3105 goals**) · `expressions.py` · `statements.py` ·
`stmt_control_flow.py` · `Module2_Parser.py` (proved three times as the gates walked it
back) · `pycsl.py` · `monomorphize.py` · `normalize.py` · `ConcurrencyChecker.py` ·
`audit_proof.py` · `audit_proof_reverify.py` · `frontend/__init__.py` ·
`import_classifier.py` · `ir_resolve.py` · `crosscheck.py` · `crosscheck_ir.py` ·
`extract.py` · `extract_lean_meta.py` · `sertop.py` · `Module6_WhyMLTranspiler.mlw`.

THE FULL BATTERY, driver-verified fresh at HEAD:
  · markers **446**, stable over 3 samples · grep 471 · offset 25 · unattached 0
  · corpus byte-diff **0** — 814/814 identical to the window-start tree
  · all **52/52** mirrors L3-tc GREEN (full sweep)
  · fidelity DIVERGED **2** on both scripts (the documented baseline pair)
  · non-vacuity (`--emit`): no NEW erasure, 8 known gated, **0 input-blind**
  · shadowed-selfcalls **14 / 121** (ratchet 14)
  · frame-honesty **0/82 trusted, 4/133 converted** — against the RE-BASELINED ratchets,
    see lesson (bk) below for why they rose and why that is not a regression
  · untrusted-emitted 863 un-trusted, **0 re-abstracted**, 0 unexpectedly absent
  · yield-erasure **0 value-erasing / 2 suspension (ratchet 2) / 1 genuinely modelled**
  · mirror-signature-drift **16 (ratchet 16), 0 converted**
  · ledger **3** — no axiom added by any of this window's seven capabilities
  · tree clean; **no prover process running**

## THE NUMBERS

| | markers | grep | offset | unattached | ledger |
|---|---|---|---|---|---|
| #31 start (`b3ad0507`) | 455 | 480 | 25 | 0 | 3 |
| **#31 end** | **446** | **471** | **25** | **0** | **3** |

Net -9 = ELEVEN conversions minus TWO gate-driven RE-TRUSTS (`iter_child_nodes`, refuted by
the NEW yield-erasure plane; `_ContractParser._err`, refuted by NON-VACUITY —
`erased=['msg'] of ['msg']`, its whole body being a `raise` whose payload is unmodelled).
**Both reverts are the right outcome and both were found by a plane, not by inspection.**

| # | commit | markers | what |
|---|---|---|---|
| 0 | `93dffbb0` | — | INSTRUMENT: probe recorded the CONTINUATION of a wrapped why3 diagnosis |
| 1 | `24a11bcc` | 455 -> 454 | `re.sub`/`re.escape` string model + `_strip_all_parens` |
| 2 | `a36de8ca` + `1639cd79` | 454 -> 452 | `pathlib.Path` model + `_default_lean_dir` / `_default_rocq_dir` |
| 3 | `a05185f6` | 452 -> 451 | EVERY-RHS-STRING local fixpoint + `_mangled_name` |
| 4 | `27ab0c3f` | — | STRING SUBSCRIPT `s[i]` |
| 5 | (yield gate) | 451 -> 452 | `iter_child_nodes` RE-TRUSTED — an honest +1 |
| 6 | (os.path) | 452 -> 450 | `os.path` model + `_proof_reference_mlw_name` / `_find_why3_coq_lib` |
| 7 | `9dec2e15` + `592c753f` | 450 -> 447 | probe SIGNATURE-PRESERVING port + `_err` / `_parse_mutex_expr_str` / `_walk_body` |
| 8 | `7121d1a7` | — | a REFLECTED NODE LIST is a real `array`, not an opaque iterable |
| 9 | `ec12c362` | 447 -> 445 | the CROSS-MIXIN PROTOCOL-STUB FRAME FIXPOINT + `_emit_array_local_reassign` / `_seq_operand` |
| 10 | `004f9ed7` | — | the SIBLING-CONCRETE route now carries the `-> NoReturn` divergence + a 32-method `#@ raises` fixpoint |
| 11 | `5dac35df` | 445 -> **446** | NON-VACUITY reverts `_err` — `erased=['msg'] of ['msg']` |

### THE `_err` SEQUENCE IS THE CLEANEST DEMONSTRATION OF LESSON (bf) THIS CAMPAIGN HAS
Five planes spoke on ONE method, each rejecting something the previous could not see:
1. the CANDIDATE PROBE (repaired, signature-preserving) said **CLEAN**;
2. SHADOWED-SELFCALLS said **14 -> 15**: all seven `self._err(...)` sites still routed
   through `val self__err_1`, so the converted body was invisible to every caller;
3. `#@ sibling_concrete` (the documented repair) then failed L3-tc — and the cause was a
   REAL EMITTER DEFECT: the concrete route never carried the `-> NoReturn` divergence
   wrapper that the abstract route has, so `if c then self._err(x) else 0` had a `unit` arm
   against an `int` one. `#@ sibling_concrete` and `-> NoReturn` had never met. **FIXED AND
   KEPT** (byte-inert: it fires only for a method that is both);
4. that exposed the unlisted `ContractSyntaxError` — exactly the reopening #30 recorded for
   `_write_fstring_inner`. BUILT with relaunch #19's device again, a fixpoint against Why3's
   own error text (`scratchpad/w4/raisesfix.py`): **converged in 32 iterations over 32
   methods**;
5. NON-VACUITY refuted the whole thing: `erased=['msg'] of ['msg']`. `_err`'s body is
   `raise _ContractSyntaxError(f"{msg} ...")`, the exception PAYLOAD is not modelled, so the
   emitted body ignores its only argument.
REVERTED to `\trusted` with the measurement written into the mirror in place of the old
guess. **REOPENING CAPABILITY: an exception payload in the model** — at which point the
raise consumes `msg` and every other piece this window built for it is already landed.

## THE TWO FINDINGS THAT MATTER

### 1. LESSON (bi): THE PROBE PORTED THE LIVE `def` LINE, DISCARDING THE MIRROR'S SIGNATURE

`bin/probe-conversion-candidates.py` spliced the live def AND body over the mirror stub.
The mirror's signature is not decoration: **188 of the 466 `\trusted` stubs that have a
live counterpart — 40% — carry a REFINED model annotation the live source does not have.**

    mirror  def _emit_array_local_reassign(..., val_ir: "ExprIR", ...)
    live    def _emit_array_local_reassign(..., val_ir: Dict[str, Any], ...)
    mirror  def statement(self) -> "List[ExprIR]"
    live    def statement(self)                       # no return annotation at all

Those annotations are what SELECT the emit_ir reflection (`val_ir.get("type")` ->
`kind_of val_ir`), the record projection, the pyval carrier and the typed return. A real
conversion KEEPS them — it deletes the `#@ \trusted` line and swaps the BODY. So the probe
was measuring the un-annotated, int-erased twin of each stub: systematically HARDER than
the thing a conversion actually produces.

**Whole-tree re-census after the repair: CLEAN 2 -> 8.** `Module2_Parser`, which #30
measured as **25 stubs / 25 L3TC-FAIL / 0 CLEAN** and recorded as REFUTED, yields two —
and one of them, `_parse_mutex_expr_str`, carried an explicit *CERTIFIED BOUNDARY
(parser-tokenstream-impl.md GAP #2)* comment in the mirror. Its stale comment is now
corrected in place (lesson (az)).

The repair is guarded on the two PARAMETER LISTS agreeing; when they do not it falls back
to the legacy port and FLAGS `PARAM-LIST DIVERGES`, which is how gate plane #2 below was
found.

### 2. LESSON (bj): A `yield` LOWERS TO `let _ = 0 in ()` — AND NO PLANE COULD SEE IT

Module 6 has no generator model. `yield <v>` emits `let _ = 0 in ()` and the `def` becomes
an ordinary function. `frontend/pure_ast.iter_child_nodes` was CONVERTED AND PROVED in
relaunch #30 in exactly that state:

    def iter_child_nodes(node):            let iter_child_nodes (node: int) : unit
        for _name, field in ...:      =>     ...
            if isinstance(field, AST):       if (py_isinstance_AST_int_op field) then
                yield field                    let _ = 0 in ()      <-- the whole method

Every plane was green: L3-tc passes (a `unit` body is well typed); `check-untrusted-emitted`
passes (it IS a definition); `check-emitted-vacuity` passes (the body still reads `node` via
`iter_fields node`, and that probe is documented as a LOWER BOUND); shadowed-selfcalls
passes; the mirror byte-diff and both fidelity scripts are indifferent. The proof was real
and it established **nothing about what the generator yields**, which is its entire meaning.

`iter_child_nodes` is RE-TRUSTED (451 -> 452, and the count going UP for this reason is the
right outcome). `bin/check-yield-erasure.py` now makes the class unbankable.

## THE TWO NEW GATE PLANES

### `bin/check-yield-erasure.py`
A converted mirror function whose body contains a VALUE-carrying `yield` must be emitted in
a form that can carry the values. Two mechanical symptoms, either of which fails: the
emitted definition returns `unit`, or its body contains `let _ = 0 in ()`.
State: **0 value-erasing · 2 suspension-dropping (ratchet 2) · 1 genuinely modelled.**
- MODELLED: `ir_inline._walk_dicts` — a real recognizer emits
  `let rec _walk_dicts (obj: pyval) : list pyval` with a genuine `Cons`.
- SUSPENSION (ratchet, not a failure): `_Unparser.block` / `_Unparser.delimit` are
  `@contextmanager`s whose VALUELESS `yield` drops no value but does drop the suspension —
  the emitted body runs the pre- and post-yield effects back to back with the caller's
  `with`-body nowhere. Lowering that ratchet needs a context-manager model.
NEGATIVE-TESTED (lesson (bg)): re-converting `iter_child_nodes` makes it exit 1.

### `bin/check-mirror-signature-drift.py`
The fidelity scripts compare the BODY of every UN-TRUSTED method. A `\trusted` stub has no
body — and its INTERFACE is its entire content. Nothing checked it.
**16 `\trusted` stubs disagree with the live parameter list; 0 converted methods do.**
- **10 MISSING a live parameter**: `_handle_dotted_call` declares `(self, func_name, args)`
  while the live signature has been `(self, func_name, args, arg_irs)` since #29 added
  `arg_irs`; `ir_resolve.resolve` is missing `import_paths`; `_m5_get_type_name` and
  `_normalize_union_annotation` are missing `dedup`; `_emit_first_assign` is missing
  `local_refs`; also `_handle_join_call`, `_handle_isinstance`, `_call_record_constructor`,
  `scc.sort_functions_by_scc`, `auto_trust._build_witness_str`.
- **6 pure RENAMES** (`expr` where the live binder is `node`): `_handle_binop`,
  `_handle_call_expr`, `_handle_subscript`, `_handle_attribute_expr`, `_handle_proj_expr`,
  `_handle_ctor_payload_expr`. Harmless to the model, but they BLOCK the
  signature-preserving port, so those six cannot be measured at all.
  **MEASURED (worktree spike, not landed): renaming all six makes them measurable and NONE
  of them becomes CLEAN** — the rename buys measurement, not markers. Their real blockers
  are `int` vs `PyCSL_Program.<record>` (three of them) and `_check_union_gt1`.
A CONVERTED method that drifts is a HARD failure, not a ratchet. Negative-tested.

## THE FIVE CAPABILITIES (all fail-closed; corpus byte-diff 0 for every one)

1. **`re.sub` / `re.escape` -> faithful `string` ops.** `re_sub_op` is a `val function`
   (deterministic — exactly what Python guarantees for default `count`/`flags`); NO content
   law. `re_escape_op` adds `length result >= length s` (escaping only inserts backslashes).
   Fail-closed on a keyword arg, a wrong arity, a compiled-pattern receiver, and — the
   important one — a CALLABLE `repl`, whose result is not a function of the argument values
   the model can see. Three of `normalize.py`'s own `re.sub` sites take a lambda and stay
   opaque BY DESIGN.
2. **The `pathlib.Path` value model.** `Path` (bare / dotted / quoted / `Optional[Path]`)
   resolves to the SAME `"str"` tag as `str` in Module5 (`_m5_path_ann_tag`), so every
   existing string mechanism applies for free. `p / q` -> `path_join_op`; `.parent`/`.stem`/
   `.name`/`.suffix` -> `path_*_op`. **Both rules are licensed by a fail-closed argument:
   `str / str` is a TypeError in Python and a Python `str` has none of those attributes, so
   a string-typed operand can only be a `Path`.** NO length or prefix law: an ABSOLUTE right
   operand discards the left (`Path("a") / "/b" == "/b"`).
   **This fixed a WRONG LOWERING**: path composition was going through the WL-02
   true-division rule and emitting `float_truediv_op (a b: int) : real`.
   Also landed here: the TYPING half of #30's capability 11 (an f-string in a function
   DECLARED `-> str` is string-typed in `_is_string_expr`, not only in the lowering).
3. **EVERY-RHS-STRING-TYPED local, as a FIXPOINT.** `_collect_string_literal_locals` marked
   a local `string` only when every assignment RHS was a plain `String` LITERAL. Generalised
   to `_is_string_expr`, iterated (marking one local makes another's RHS string-typed).
   Conservative in the same way: any non-string RHS anywhere excludes the local.
4. **STRING SUBSCRIPT.** `s[i]` on a string receiver is a one-character string
   (`str_sub_op s i 1`, the same op and law the `for c in <str>` element read already used).
   Fail-closed on a negative literal index.
5. **The `os.path` string model**, split by DETERMINISM, which is all that is claimed:
   `basename`/`dirname`/`normpath`/`relpath`/`join` are `val function`; `abspath`/`realpath`/
   `expanduser` read cwd/`$HOME` so they are plain `val` (equal arguments need not agree);
   `exists`/`isfile`/`isdir`/`islink`/`isabs` are filesystem predicates -> `int`. Plus a
   SLOT recognizer at the subscript for `os.path.splitext(p)[k]` / `split` / `splitdrive`
   (only a LITERAL 0/1 index).

## A FALSE `CLEAN` THE SIGNATURE REPAIR EXPOSED — and the marker that now catches it
With the mirror signature preserved, `proof2why3.from_sexp._find_construct_idx` scored
CLEAN. Its emitted body: `any_1 (Array.make 1 0)` — `any(<genexpr>)` has no lowering, so
the whole generator and every variable it reads are replaced by a FRESH CONSTANT ARRAY. It
also lowers `return None` to `raise (Return 0)`, conflating "not found" with index 0.
NOT CONVERTED. New probe marker: an ARITY-SUFFIXED abstract op applied to `(Array.make n 0)`
— keyed so the legitimate `let a = (Array.make 1024 0) in` initialiser is untouched.

### 3. LESSON (bk): `check-trusted-frame-honesty` SAW `self.x = ...` AND NOTHING ELSE

The gate whose whole purpose is to find `#@ assigns \nothing` frames that the live body
contradicts walked for an `ast.Attribute` in a STORE context. It did not see
`self.xs.append(v)`, `self.s.add(v)`, `self.d.update(m)`, `self.xs.sort()`,
`del self.d[k]`, or `self.d[k] = v` (a Subscript target, not an Attribute one) — which is
how the emitter mutates most of its state.

ON THE SAME TREE, sharper detector, nothing else changed:

| | before | after |
|---|---|---|
| trusted total | 63 | **82** (direct writers 23 -> 32) |
| converted total | 68 | **133** |
| converted MODEL-VISIBLE | 2 | **4** |

The four model-visible converted offenders — `expressions._ifexpr_seq_arm`,
`statements._materialize_bridge`, `._materialize_str_bridge`,
`._wrap_body_with_return_catch` — all reach `_add_abstract_op`, whose
`self._abstract_ops[k] = ...` is exactly the subscript store the old walk could not see.

**The most instructive offender is `pure_ast._Unparser.write`, the 97-call-site output
hub.** Its entire body is `self._source.extend(text)` and it emits as

    let _unparser__write (self: _unparser) (text: seq int) : unit
      writes {  }
    = let _ = (self__source_extend_1 text) in ()

a RECEIVER-LESS opaque op with no effect, under a frame saying the method changes nothing —
while a CONVERTED sibling reads that field through `getattr__unparser`, i.e. through
`_pyobj_state`, which `writes { }` asserts is unchanged. **CHECKED EXACTLY, not inferred:**
`stable_hash("_source") == 1975084088`, and the emitted `_unparser__maybe_newline` is

    let _unparser__maybe_newline (self: _unparser) : unit
      writes {  }
    = if ((getattr__unparser self 1975084088) <> 0) then
        let _ = (_unparser__write self (Seq.cons 1470490902 (Seq.empty: seq int))) in ()

so the model can prove `self._source` INVARIANT across any number of `write` calls, which is
false of the program. Both methods are CONVERTED and PROVED. **That is an
under-approximation of effects in the converted population.** Every plane was green on it. Ratchets re-baselined to 82/133/4 with the derivation written beside the
constants; raising a ratchet is legitimate ONLY when the analysis got sharper and the tree
did not get worse, the same condition under which shadowed-selfcalls went 13 -> 14 at #30.

**THE REPAIR IS ON THE LADDER AND OPTION (b) IS THE RIGHT ONE:**
  (a) re-trust `write` AND give it `#@ assigns self._source` — a trusted stub's frame is
      assumed, so the honest one costs nothing to discharge. +1 marker, one `pure_ast`
      re-proof. Available immediately.
  (b) **build the read-modify-write lowering**: under `@mutable_state`, an in-place
      collection mutation on a self field IS `self.f = <mutate>(self.f, args)`, i.e.
      `setattr__unparser self <f> (self__source_extend_1 (getattr__unparser self <f>) text)`.
      That makes the write MODEL-VISIBLE, lets the honest `#@ assigns self._source`
      DISCHARGE on the converted body, and fixes the whole 18-method class instead of one
      method. The emitter already owns both halves (`getattr__unparser` /
      `setattr__unparser ... writes { _pyobj_state }`).
  Do NOT simply re-trust without the honest `#@ assigns`: that only MOVES the false frame
  into the assumed population.

## THE FRAME FIXPOINT — a boundary found and broken in the same window

Why3 REJECTS an OVER-claimed `writes` ("this write effect does not happen in the
expression"). A converted method whose live body writes emitter state ONLY THROUGH a
`\trusted` cross-mixin protocol stub therefore could not state its honest frame: the stub's
`val` declared no writes, so the converted body wrote nothing in the MODEL while its
`#@ assigns` — correctly derived from the LIVE transitive closure — listed seventeen fields.
Measured on `statements._emit_array_local_reassign`, otherwise CLEAN.

Narrowing the CALLER to `#@ assigns \nothing` also makes it CLEAN — measured — and was
REFUSED: `assigns` is an upper bound on effects, so UNDER-claiming is the direction that
misleads a caller, and it would move an existing dishonesty out of the counted trusted-63
and into the converted population.

THE FIX went the other way. `StatementEmissionMixin._expr_to_whyml` /
`ControlFlowStmtMixin._expr_to_whyml` are cross-mixin PROTOCOL STUBS (`return ""`, no live
counterpart in that file) and carried NO `#@ assigns` clause at all — an IMPLICIT
`writes {}`, which is false. They now declare the frame. Every converted caller then has to
list it EXACTLY (Why3 rejects both directions), so this is a FIXPOINT — and relaunch #19
already built the device: drive `#@ assigns` against Why3's OWN ERROR TEXT as a LOOP rather
than an analysis. `scratchpad/w4/framefix_loop.py` does it; it **converged in ONE iteration
per file** across `statements.py` (6 callers), `stmt_control_flow.py` (1) and
`expressions.py` (3). Corpus byte-diff 0.

**MEASURED AND NOT LANDED:** doing the same for the OTHER TWELVE no-`#@ assigns` protocol
stubs converges too (2 more iterations) and yields **ZERO** additional conversions — an
honesty-only change at the price of three whole-file re-proofs, and the field set must then
be DERIVED PER STUB rather than the blanket 17 used for the spike.

## WHERE THE LADDER STANDS

0. **The FOURTEEN `\trusted` stubs with NO `#@ assigns` clause** — an implicit `writes {}`
   the frame-honesty counter cannot see (it counts stubs that declare `\nothing`
   explicitly). Twelve are cross-mixin protocol stubs. Method: the same fixpoint loop.
   Priced above: honesty-only, 0 markers, 3 re-proofs, per-stub derived frames.
1. **Repair the 16 mirror-signature drifts** (gate above). The 10 MISSING-parameter stubs
   are a live fidelity hole — `_handle_dotted_call`'s trusted interface is for a function
   that has not existed since #29. Each repair changes that mirror's emission and costs a
   whole-file re-proof. The 6 renames are measured to buy measurement only.
1b. **`<x> or []` IS A WRONG LOWERING, and it is the LARGEST identified family in the tree:
   54 `\trusted` stubs.** Python's `or` returns a VALUE; the emitter lowers it as a BOOLEAN.
   `for ens in (rec.get("ensures") or []):` emits
   `iter_length (if (rec_get_2 … <> 0) || ((Array.make 1024 0) <> 0) then 1 else 0)` — a
   `1` or `0` where a list belongs. The correct rule is
   `A or D` => `(if <truthy A> then A else D)` in a VALUE position, gated on a type
   agreement the emitter can DECIDE (both string / both array / both emit_ir) and failing
   closed to the boolean form otherwise. `_handle_binop` ALREADY carries a CLOSED-KEY
   special case of exactly this (`<emit_ir>.get(k) or []` for the seven node-list keys), so
   the emit_ir slice is already covered and the residue is the DICT slice, where `or []`
   has to be read as EVIDENCE that the map's value type is a list — i.e. it meets backlog
   item 1b-B (empty-collection-literal value-type inference). MEASURE THE CORPUS BYTE-DIFF
   FIRST: this touches a general operator, and a corpus `x or []` in a BOOLEAN position
   must stay byte-identical.
2. **The `int` <-> `string` boundary is still the biggest family** — 51 `int`-into-`string`
   and 30 `string`-into-`int` on the REPAIRED census. This window took five bites out of it
   (re, Path, os.path, string subscript, string locals) for 8 markers; the residue is
   dominated by opaque `\trusted`-callee returns and heterogeneous `Dict[str, Any]` reads.
3. **The heterogeneous `Dict[str, Any]` parameter.** ~13 emitter-mixin stubs whose first
   blocker is `match Map.get <ir> "type" ... None -> 0` compared with `str_eq_op`. The
   device that fixes it EXISTS and is used exactly twice: a closed-key `TypedDict` VIEW in
   the mirror (`ValIRBoolView`), which monomorphizes to a WhyML record. Untried at scale.
4. **The recursive node ADT / structural measure** — unchanged, still the reopening
   capability for `traverse`'s 88 shadowed call sites and `visit_If`.
5. `interleave` monomorphisation, `option string` record-field reads — unchanged from #30.

## A POSSIBLE BLIND SPOT IN `check-trusted-frame-honesty` (recorded, not acted on)
`ConcurrencyChecker._walk_body` was converted with `#@ assigns \nothing`. Live, it calls
`_walk_stmt` -> `_warn_if_unprotected` -> `self.warnings.append(...)`. The gate's transitive
closure follows DECLARED frames and `_walk_stmt`'s trusted stub declares `\nothing`, so the
write is invisible — and `_warn_if_unprotected` itself is not in the gate's 63 either. Two
readings: the closure stopping at a declared frame is by design (the falseness is counted at
the stub that declares it), or `<list-field>.append` is not recognised as a self-write.
**Check which, before trusting the 63.**

## THE DEFINITIVE RANKED CENSUS AT WINDOW END (repaired probe, all #31 capabilities)
Every census taken BEFORE the signature repair is unreliable; this is the first honest one.

    39  int -> string        28  int -> array        15  string -> int
    14  int -> emit_ir       10  () -> int            9  int -> map ('mu -> option int)
     8  array int -> int      7  array string -> int  5  syntax error / 5 py_classdef_node
     4  tuple pattern         4  ref 'mu @rho         4  PARAM-LIST DIVERGES

**`int` vs `emit_ir` (14) LOOKS cheapest and is NOT uniform** — SPIKED: `pure_ast._Parser.node`
needs a `**kw` dynamic-construction model, not an annotation (`_fin` gaining a truthful
`-> "ExprIR"` was measured byte-safe and did not move it). Check each member individually.
The family: `statements._handle_assign_stmt` `._typed_local_vars` · `expressions._e`
`._to_bool` `._match_pattern_cond` `._handle_sum_call` `._content_string_method` ·
`Module5_IREmitter._get_mutex_invariant_ir` `._csl_in` `._csl_list_to_ir` `._py_expr_fstring`
`._py_stmts_to_ir` `._normalize_union_annotation` · `Module3_Weaver._desugar_acts` ·
`pure_ast._Parser.node`.

## INSTRUMENT FACTS #31 ADDS
1. `scratchpad/w4/port_sig.py` — the SIGNATURE-PRESERVING port, matching the repaired probe.
   Use it, not the older `port*.py`, for any stub whose mirror signature is refined.
2. **Match the `#@ \trusted` marker ANCHORED (`^#@\s*\\trusted\b`).** A loose
   `"\trusted" in line` test also matches a PROSE comment that mentions the directive — the
   mirror has several — and then deletes the wrong line while leaving the marker in place,
   so the "conversion" silently does nothing. Cost: one wasted cycle on `_err`.
3. **Resolve an emitted WhyML name by `<class>__<method>`, never by a suffix match.**
   `_Unparser.block` matches `_fin_block` under `endswith("_block")`, and a gate that
   misidentifies its subject issues a clean bill of health.
4. `scratchpad/w4/diag_any.py <mirror-relpath> <Class:name>` prints the WhyML around the
   first type error and restores the tree. NOTE: it still ports the LIVE header — use the
   probe for a verdict, this only for reading the emitted text.

---

# HANDOFF — #30 FINAL (2026-09-02, WINDOW 3): **462 -> 455, seven markers, four verified
# increments — and the finding that matters most is that `check-shadowed-selfcalls.py`
# had been BLIND TO EVERY PUBLIC METHOD for the whole campaign.**

## THE NUMBERS

| | markers | grep | offset | unattached | ledger |
|---|---|---|---|---|---|
| #30 start | 462 | 487 | 25 | 0 | 3 |
| **#30 end** | **455** | **480** | **25** | **0** | **3** |

| increment | commit | markers | whole-file proof |
|---|---|---|---|
| 1 `@mutable_state` + 4 capabilities + `fill` | `d626dd39` | 462 -> 458 | pure_ast 3097/3097 Valid |
| 2 INSTRUMENT repair + 5 `sibling_concrete` hubs | `39c576c5` | — | (folded into 1's proof) |
| 3 `setattr`/`hasattr`/generator return type | `e37eca32` | 458 -> 456 | pure_ast 3118/3118 Valid |
| 4 four string-model capabilities + `_Inliner._fresh` | `c21486e7` | 456 -> 455 | ir_inline 358/358 Valid |
| 5 `_decl_arity` fix (byte-inert, no proof needed) | `cd223597` | — | emission unchanged |
| 6 trusted frame-honesty ratchet 68 -> 63 | `55b02c7a` | — | — |

**FINAL VERIFICATION at HEAD, run after every commit:** 52/52 mirrors L3-tc GREEN and
their `.mlw` md5s are IDENTICAL to the tree that proved 3118/358 — so both whole-file
proofs still stand. Corpus: exactly `0482`/`0483` differ from the window-start tree, both
re-verified `Verification SUCCESS`. No prover process left running; tree clean.

CONVERTED this window: `visit_FormattedValue`, `_function_helper`, `_type_params_helper`,
`fill`, `iter_child_nodes`, `copy_location`, `_Inliner._fresh`.

| plane | at #30 end |
|---|---|
| mirrors | **52/52 L3-tc GREEN**; only `pure_ast.mlw` and `ir_inline.mlw` differ from window start |
| corpus byte-diff | **812/814 identical**; `0482`/`0483` deliberate (see `str_repeat_op`), both re-verified `Verification SUCCESS` |
| fidelity | DIVERGED 2 (`_handle_var_expr`, `_handle_for_stmt` — the baseline pair) |
| shadowed-selfcalls | **14 / 121**, REPAIRED instrument (19 / 257 at window start, reported as 13 / 33) |
| non-vacuity (`--emit`) | no NEW erasure, 0 input-blind |
| frame-honesty | trusted **63/63** (ratchet LOWERED 68 -> 63) · converted 68/68 · model-visible 0 and 2 |
| ledger | 3, no axiom added |

## THE FIVE THINGS THE NEXT RELAUNCH MUST KNOW

### 1. LESSON (bg): AN INSTRUMENT'S BLIND SPOT IS SHAPED LIKE ITS REGEX
`check-shadowed-selfcalls.py` matched `^  val (self__([A-Za-z_0-9]+)_(\d+)) ` — **two
underscores**. The avatar mangling is `self_` + <name> + `_` + <arity>, so two underscores
occur only when the METHOD'S OWN NAME starts with `_`. Every PUBLIC-named method was
invisible — precisely what a visitor class is made of. On the window-start tree the
repaired regex reports **19 methods and 257 bypassing call sites, not 13 and 33**:
`self_write_1` (97 uses) and `self_traverse_1` (88) had been converted AND PROVED in
earlier windows with no caller able to see one thing their bodies compute.
Five of the six take `#@ sibling_concrete`; the ratchet is re-baselined to **14 / 121**.
**Before trusting a gate that reports a small number, feed it a case you KNOW is bad and
check that it fires.** The tell needed no domain knowledge: the mirror emits
`val self_fill_1` and the gate's own message says it looks for `val self__<m>_<n>`.

### 2. LESSON (bh): WHEN ONE GOAL IN A 3000-GOAL FILE WILL NOT DISCHARGE, READ THE CONTRACT
`val str_repeat_op` declared `requires { n >= 0 }`. Python has no such precondition —
`"ab" * -1` is `""`. It was an over-restriction of the model AND load-bearing: `fill`
lowers `"    " * self._indent + text` and `self._indent` is an opaque getattr read, so
`n >= 0` was unprovable at the call site and that ONE precondition was the only unproven
goal in two successive full proofs. Now a total contract (`n >= 0 -> length = n*|s|`,
`n < 0 -> length = 0`): strictly weaker as a requirement, strictly more informative as a
postcondition. **#29 reverted `fill` at the fourth link after three fixes to the CALLER.
The defect was one clause in a `val` declaration.**

### 3. A "DO NOT ATTEMPT AGAIN" RECORD IS A CLAIM — CHECK *WHICH* REPAIR WAS TRIED
`_function_helper`, `_type_params_helper`, `_write_fstring_inner` were refuted by
shadowed-selfcalls in #27, #28 and #29, and #29 wrote "do not attempt a fourth time". The
directive that fixes exactly that failure — `#@ sibling_concrete`, lesson (ay) — had never
been tried on them. Two of the three convert with the ratchet unchanged.

### 4. TWO NEW CERTIFIED BOUNDARIES, both found by the PROOF plane
- **`traverse` cannot be `#@ sibling_concrete`.** Concrete routing makes `traverse` /
  `visit` / every `visit_<Node>` ONE mutually recursive group and Why3 demands a measure
  the int model cannot supply. Measured: **124 unproven goals, every one `Sub-goal
  termination`**, over 30 visitors. REOPENING: a structural measure on the node handle,
  i.e. the recursive node ADT — now with a second independent reason to want it.
  **88 bypassing call sites ride on this one.** Do not retry without the measure.
- **`visit_If`** now TYPECHECKS under `@mutable_state` (it did not before) and is still
  not provable — its genuine `while` walks `node.orelse[0]` down the AST with no measure.
  **Type-checking is not provability; a green `tc.sh` is not a conversion.**

### 5. THE `int`/`string` MODEL BOUNDARY IS THE REAL REMAINING WALL — measured, not guessed
Four capabilities were built for it this window (below) and they are **completely
byte-inert**: corpus 814/814 identical AND all 52 mirror `.mlw` md5s unchanged. The
honest yield was ONE marker. Re-censused with them in place, the mirror-wide ranking
moved `string`-vs-`int` 46 -> 32 but `int`-vs-`string` 38 -> 56: **for most of that
population the blocker MOVED rather than cleared, because a body crosses the int/string
model boundary more than once.** Anyone attacking it should plan a model change, not more
per-site coercions.

## THE CAPABILITIES THIS WINDOW ADDED (11, all fail-closed, all corpus-audited)

**From `@mutable_state` on `_Unparser`** (ladder item 1, priced by #27 and untried by five
relaunches — its predicted cost, "~7 false frames flip to model-visible against a hard-0
ratchet", was WRONG: model-visible stayed 0/2):
1. a COMPUTED string into the int model at `_handle_call_expr`'s unannotated-callee arm;
2. a STRING actual into an int FORMAL in `_handle_dotted_call` — the same loop and the same
   `param_types[i] == "int"` gate as #29's bool-actual coercion;
3. #29's hoisted loop bound: its `@mutable_state` blast-radius gate now lifts **only when
   the length term's head is a PROGRAM `val`**, asked of the emitter's own `_abstract_ops`
   registry. `iter_length` is; the ADT's `let rec function irlen` is not, and stays
   byte-identical. Without the discriminator the hoist rewrote a `Module5_IREmitter`
   variant that already discharged;
4. `_coerce_str_arg` folds only a string LITERAL, so a COMPUTED string operand still met an
   int inside `val str_concat (x y: int) : int`. That gap was the whole of `fill`.

**Increment 3:**
5. DYNAMIC `setattr`. `setattr(o, <literal>, v)` is recognised by `_handle_fieldassign_stmt`;
   `setattr(o, <computed name>, v)` fell to the generic arm and minted a SECOND `setattr_3`
   with a different signature — two declarations of one Why3 symbol, module rejected. The
   generic arm now emits the recognised op.
6. A COMPUTED `hasattr` NAME (`hasattr(node, attr)` with `attr` a loop variable).
7. THE GENERATOR RETURN TYPE: `iter_fields` / `iter_child_nodes` / `walk` are Python
   generators; their stub is `pass` with no annotation so the `val` announced `: unit`.
   They now carry the MODEL annotation `-> int` — an iterable IS an opaque int handle here
   (it is what `iter_length`/`iter_get` consume), the same kind of model-truthful
   declaration as the `-> bool` stubs that emit `: int`. **Census: that was the LAST
   un-annotated generator stub in the tree bar `_Unparser.buffered`.**

**Increment 4 (the four byte-inert string-model capabilities):**
8. `_handle_call_expr` generic arm — hash from the ARGUMENT IR (`_is_string_expr`), not from
   the emitted text's head, so a string-typed VARIABLE is covered;
9. `_handle_dotted_call` int-formal loop — same generalisation (this reaches
   `re.sub(..., !s)` and `unicodedata.normalize`);
10. the INT-MODEL F-STRING JOINER — `f"{base}_{self.counter}"` put a `string` into
    `val str_concat (x y: int) : int`;
11. an f-string in a function DECLARED `-> str` now lowers in the STRING model. That branch
    was gated on `@mutable_state` membership, which a plain module function can never
    satisfy, so `_mangled_name` / `_fresh` / `_strip_all_parens` returned an int-hash from
    a `string`-typed function.

## THE STANDING DISCIPLINE THAT CAUGHT REAL BUGS THIS WINDOW

- **Lesson (be), three separate times.** `visit_If` and `_function_helper` (`with
  self.block():` -> `#@ assigns self._indent`), `copy_location` (`setattr` -> `#@ assigns
  new_node`), `_Inliner._fresh` (`self.counter += 1` -> `#@ assigns self.counter`). A port
  never inherits its stub's frame.
- **A converted method must not call `_add_abstract_op`.** It writes
  `self._obj_state_written`, so registering an operator from inside a CONVERTED method
  under `#@ assigns \nothing` makes that frame false and breaks the converted ratchet
  (measured). `val str_hash_op` is therefore recovered LATE, from the emitted text, in
  `abstract_ops._insert_abstract_val_block` — a `\trusted` mirror stub.
- **`_coerce_to_int` IS NOT THE PLACE for a string coercion.** It is called from positions
  whose formal is `string` (`whyml_ident`, a `seq string` element, an assignment); putting
  the coercion there moved FOUR already-typechecking mirrors off byte-identity. Coerce at
  the site that KNOWS the formal is `int`.

## MEASURED AND REFUTED — do not re-derive these

| target | verdict |
|---|---|
| `Module1_Ingestor` / `Module2_Parser` (#29's ranked next place to look) | **REFUTED.** Re-probed with the repaired harness AND all 11 new capabilities: Module2 25 stubs / 25 L3TC-FAIL / 0 CLEAN; Module1 12 stubs / 11 L3TC-FAIL + 1 ERASURE / 0 CLEAN. Twenty distinct blocker shapes, not one family. `_match_block_hdr` returns `(kw, name) \| None` over compiled regexes — a value-model build. |
| the whole tree outside `pure_ast.py` | **2 CLEAN candidates only** (`Module3_Weaver._attach_loop_contracts`, `_region_bound_str`), both still refuted by non-vacuity. Unchanged from #29 even with 11 new capabilities. |
| the 13 remaining shadowed methods | **ALL REFUTED for `#@ sibling_concrete`** — each fails L3-tc on a record/union/pyval type (`pyval`, `_union_*`, `boolwrapirview @rho`, `option string`). `_py_expr_to_ir` ALREADY carries the marker and is still shadowed at 17 of 45 sites. This seam is closed without a value-model change. |
| `walk` | ERASURE — `while todo:` emits `while true` (guard erased) and no variant |
| `iter_fields` | ERASURE — opaque attribute getter for `node._fields` |
| `NodeVisitor.generic_visit` | VAL — re-abstracted by the auto-trust valve |
| `fix_missing_locations` | nested `def _fix` — body-blocked |
| `_write_fstring_inner` + `sibling_concrete` | concrete routing exposes an unlisted `ValueError` at `_fstring_Constant`. Reopening: an exception clause on the callers. |
| mirror stubs missing their LIVE return annotation | **ZERO tree-wide** — that cheap seam does not exist. |

## A REAL EMITTER BUG, diagnosed and MEASURED, deliberately NOT landed — `_decl_arity`
`abstract_ops._add_abstract_op` disambiguates a same-name collision by arity and computes
arity as **`decl.count("(x")`** — parameter groups whose first binder is NAMED `x`. So
`val setattr_3 (x: int) (f: int) (v: int) : unit` reads as arity ONE. A correct
`_decl_arity` (count binder names per `(names : type)` group) is **corpus-byte-inert,
814/814** — but the tie-break underneath is wrong either way:
- with the existing "keep the LONGER": the `: int` mint of `setattr_3` survives and a
  statement-position call reads `type int, but is expected to have type ()`. One line in
  the statement emitter (`let _ = … in ()`) closes it.
- with "keep the FIRST": **REFUTED** — breaks `Module3_Weaver.mlw`
  (`unbound function or predicate symbol 'get_value'`) and moves `expressions.mlw` off
  byte-identity (`val str_eq_op (a: string) (b: string)` -> `(a b: string)`).
Increment 3's `setattr` unification removes its only known victim WITHOUT depending on it,
so the defect is now latent rather than blocking. Nothing is in the tree; re-derive here.

## WHERE THE LADDER STANDS

1. **The recursive node ADT / a structural measure on the node handle.** It is now the
   reopening capability for TWO independent boundaries (`traverse`'s 88 shadowed call
   sites, and the nine `iter_length` loop bodies #29 recorded). Biggest single item left.
2. **The `int`/`string` model boundary** (see §5) — a model change, not more coercions.
3. `_decl_arity` + the statement-position `let _ = … in ()` (above).
4. The closure FORMAL for `interleave` / `items_view` — #29's ladder item 2. **NO LONGER
   UNTRIED: spiked end-to-end at the close of #30 and RECORDED AS A CERTIFIED BOUNDARY.
   Every step below was measured; do not re-derive it.**
   - A `_prescan_callable_params` (formals APPLIED in the body -> their arity) plus one
     branch in `functions._param_type_str` rendering `int -> unit` / `unit -> unit` makes
     **`interleave` TYPECHECK and score CLEAN on the probe.** Corpus byte-inert (814/814);
     it moves exactly ONE line in two mirrors (`val _contractparser___try (fn: int)` ->
     `(fn: unit -> unit)`, which is the truthful type — `fn` is a thunk `_try` calls).
   - **But converting it is a LOST CONVERSION**: 11 call sites still route through
     `val self_interleave_3`, so shadowed-selfcalls goes 14 -> 15 and the gate rejects it.
   - `#@ sibling_concrete` on `interleave` then fails, because
     `self.interleave(lambda: …, self.traverse, node.elts)` passes a BOUND METHOD as a
     value and the attribute lowering emits the opaque `getattr__unparser self <hash>`.
   - A bound-method eta-expansion was built (`self.<m>` in a function-formal position ->
     `(fun x0 -> <cls>__<m> self x0)` when concrete, else onto the receiver-less avatar
     `self_<m>_<n>` the file already uses). It gets one level further and then hits the
     REAL obstacle: **the family is POLYMORPHIC in the argument type.** `interleave` is
     handed `self.traverse` (`int -> unit`) at one call site and `self._write_constant` /
     `self.write` (`seq int -> unit`) at another, so one avatar cannot carry both.
   - Typing the formal `'c0 -> unit` was tried and REFUTED: `interleave`'s own body
     applies `f` to `next(seq)`, an int, so the type variable cannot be universally
     quantified inside the definition (`This expression has type int, but is expected to
     have type 'c0`).
   **REOPENING CAPABILITY: per-call-site MONOMORPHISATION of a higher-order self-method
   (one avatar/definition per argument type), or a value model in which `traverse` and
   `write` share an argument type.** Nothing from this spike is in the tree.
5. `option string` record-field reads — still unbuilt, still priced (#29).

## HELPERS LEFT IN THE TREE (`scratchpad/`)
`tc.sh` · `port.py` / `port2.py` / **`port_any.py <Class:name|name>` (NEW, any mirror
file)** · `restub.py` · `tryport.sh` · `diag.sh` · **`sibcon.py add|del <names>` (NEW,
`_Unparser`)** · **`sibcon_any.py <mirror.py> <Class:name>` (NEW)** · `mirror_md5.sh`.

## INSTRUMENT FACTS #30 ADDS
1. **`bin/byte-diff-sweep.sh` needs `$ROOT/.venv`.** In a detached worktree it silently
   emits ZERO files and `diff -rq` then reports every file as "only in" — which looks like
   a catastrophic byte-diff. `ln -s /home/fabrice/git/pycsl/.venv <worktree>/.venv` first.
2. **The Bash tool caps at 600 s AND the background-task harness kills long jobs.** A
   `pure_ast.py` proof (up to ~1 h) was killed twice. Run it DETACHED —
   `setsid nohup <script> </dev/null >/dev/null 2>&1 &` writing a `.done` sentinel — and
   poll from the foreground. A proof is READ-ONLY, so this does not violate the
   ownerless-writer rule; a port/prove/REVERT sweep still does.
3. **Proof cost scales with what is concrete.** `pure_ast.py`: 9 min with the hubs
   abstract, >1 h with `write`/`traverse`/`fill` concrete, ~25 min with `traverse` reverted.
   Budget for it; a long Z3 phase is not a hang.
4. **Use a second detached worktree for all probing** (`git worktree add --detach`). It
   keeps the census completely off the main tree while a proof reads it, and it is the only
   way to run a port/emit sweep without becoming the ownerless writer the prompt forbids.

---

# HANDOFF — #30 (2026-09-02, WINDOW 3): **462 -> 458, and the more important number is
# 257 -> 33. `check-shadowed-selfcalls.py` was BLIND TO EVERY PUBLIC METHOD, and the
# `_Unparser` hubs `write` (97 call sites) and `traverse` (88) had been converted and
# proved in earlier windows with no caller able to see one thing their bodies compute.**

## THE NUMBERS

| | markers | grep | offset | unattached | ledger |
|---|---|---|---|---|---|
| window-3 relaunch start | 462 | 487 | 25 | 0 | 3 |
| **#30 end** | **458** | **483** | **25** | **0** | **3** |

**`pure_ast.py` whole-file proof: `Verification SUCCESS`, 3097 goals, 0 non-Valid.**

| plane | before | after |
|---|---|---|
| shadowed-selfcalls (methods / bypassing call sites) | 13 / 33 *as measured by a broken regex*; **19 / 257 under the repaired one** | **14 / 121**, repaired instrument, ratchet re-baselined 13 -> 14 |
| frame-honesty trusted total | 65 | 64 (ratchet 68) |
| frame-honesty converted total | 68 | 68 (ratchet 68) |
| corpus byte-diff | 0 | **812/814 identical**; 0482/0483 deliberate (see `str_repeat_op` below), both re-verified SUCCESS |
| mirrors L3-tc | 52/52 | **52/52**, and only `pure_ast.mlw` differs from the window start |
| fidelity DIVERGED | 2 | 2 (baseline) |

## THE THREE THINGS THAT MATTER

### 1. LADDER ITEM 1 IS DONE: `@mutable_state` on `_Unparser` LANDED

It was priced by #27 and left untried by five relaunches, with the warning "it will flip
~7 currently-false frames to MODEL-VISIBLE against a hard-0 ratchet". **That prediction
was wrong.** Measured: model-visible stayed at 0/trusted and 2/converted, and the
converted TOTAL moved only because two ported bodies use `with self.block():`
(re-declared `#@ assigns self._indent`, lesson (be) applied by hand).

The real cost was FOUR one-line emitter gaps, every one of them the adjacent case of a
mechanism the emitter already owned — **lesson (bb) for the third window running**:

1. a COMPUTED string into the int model at `_handle_call_expr`'s unannotated-callee arm;
2. a STRING actual into an `int` FORMAL in `_handle_dotted_call` — literally the same loop
   and the same `param_types[i] == "int"` gate as #29's bool-actual coercion;
3. #29's hoisted loop bound: its `@mutable_state` blast-radius gate now lifts **only when
   the length term's head is a PROGRAM `val`**, asked of the emitter's own `_abstract_ops`
   registry. `iter_length` is one; the IR-node ADT's `let rec function irlen` is not, and
   stays byte-identical. Without that discriminator the hoist rewrote a
   `Module5_IREmitter` variant that already discharged;
4. `_coerce_str_arg` folds only a string LITERAL, so a COMPUTED string operand still met an
   int inside `val str_concat (x y: int) : int`. That one gap was the whole of `fill`.

**AND ONE THING NOT TO DO, learned the expensive way.** The obvious home for (1)+(2) is
`_coerce_to_int`. Putting it there is WRONG TWICE: `_coerce_to_int` is called from
positions whose formal is `string` (`whyml_ident`, a `seq string` element, an assignment)
— it moved FOUR already-typechecking mirrors off byte-identity — and it must not call
`_add_abstract_op` at all, because that writes `self._obj_state_written` and
`_coerce_to_int` is a CONVERTED mirror method under `#@ assigns \nothing`; registering
from there breaks the converted frame-honesty ratchet (measured, not predicted).
The `val str_hash_op` declaration is therefore recovered LATE, from the emitted text, in
`abstract_ops._insert_abstract_val_block` — a `\trusted` mirror stub where no frame is claimed.

### 2. `#@ sibling_concrete` BREAKS A THRICE-REFUTED WALL

`_function_helper`, `_type_params_helper` and `_write_fstring_inner` were rejected by
shadowed-selfcalls in #27, #28 and #29, and #29's handoff wrote "do not attempt them a
fourth time". **The directive that fixes exactly that failure had never been tried on
them.** Two of the three convert with the ratchet unchanged. (`_write_fstring_inner`
still refuses: concrete routing exposes an unlisted `ValueError` at `_fstring_Constant`
— reopening is an exception clause on its callers.)

**A "do not attempt again" record is a claim like any other. Check WHICH repair was tried.**

### 3. THE INSTRUMENT FINDING — and it is the biggest thing in this window

`check-shadowed-selfcalls.py` matched `^  val (self__([A-Za-z_0-9]+)_(\d+)) ` — **two
underscores**. The avatar mangling is `self_` + <name> + `_` + <arity>, so two underscores
only occur when the METHOD'S OWN NAME starts with `_`. Every PUBLIC-named method was
invisible — which is precisely what a visitor class is made of.

On the same tree the repaired regex reports **19 shadowed methods and 257 bypassing call
sites, not 13 and 33**. In `frontend/pure_ast.mlw` alone it had been hiding
`self_write_1` (97 bypassing uses), `self_traverse_1` (88), `self_fill_1` (33),
`self_maybe_newline_0`, `self_do_visit_try_1` and `self_visit_FormattedValue_1`.
`write`, `traverse`, `maybe_newline` and `do_visit_try` were converted AND PROVED in
earlier windows while no caller could see a single thing their bodies computed.

All six take `#@ sibling_concrete`, and the count returns to 13 / 33 under the sharper
measurement — **224 call sites moved from an unconstrained abstract result to the real
body.** Two of the six (`fill`, `visit_FormattedValue`) were converted EARLIER IN THIS
WINDOW; without the repair this window would have banked two conversions no caller could see.

**LESSON (bg): an instrument's blind spot is shaped like its regex.** Before trusting a
gate that reports a small number, feed it a case you KNOW is bad and check it fires. The
tell here needed no domain knowledge: the mirror emits `val self_fill_1` and the gate's
own message says it looks for `val self__<m>_<n>`.

## WHAT THIS WINDOW MEASURED AND DID NOT ACT ON — all of it fresh, none of it inherited

### `Module1_Ingestor.py` and `Module2_Parser.py`: ladder item 3 is REFUTED as stated
#29 ranked these as the next place to look because their top two blocker families were
the ones it had just fixed twice. Re-probed with the repaired harness AND this window's
four new capabilities: **Module2_Parser 25 stubs, 25 L3TC-FAIL, 0 CLEAN. Module1_Ingestor
12 stubs, 11 L3TC-FAIL + 1 ERASURE, 0 CLEAN.** The blockers are not one family repeated;
they are twenty distinct shapes (`()` vs int, tuple patterns, `array int @rho`, regex
match objects, heterogeneous list literals, unlisted exceptions). `_match_block_hdr`,
the single module-level entry point, returns `(keyword, name) | None` over a list of
compiled regexes — a value-model build, not an inference.

### `pure_ast.py`'s remaining 63 markers, ranked by BLOCKER (full census in this window)
`()`-vs-`int` (**10**: `generic_visit`, `visit_Constant`, `_build_nodes`,
`_decode_fstring_middle`, `iter_child_nodes`, `walk`, `fix_missing_locations`,
`increment_lineno`, `_self_test`, `_fin_block`, `delimit_if`) · `int`-vs-`string` (6) ·
`array int @rho` (5) · tuple pattern (3, the `visit_Match*` family) · unbound symbol (4).

**THE `()`-vs-`int` FAMILY IS A GENERATOR-TYPING GAP, PRICED.** `iter_child_nodes` and
`walk` are Python GENERATORS. Their mirror stub is `pass` with no return annotation, so
`find_return_type` says `unit` and the `val` announces `: unit`; every caller that uses
the result is an L3-tc error. #29's `-> str` / `-> int` / `-> bool` disjuncts in
`_compute_return_type` are all gated on an ANNOTATION, and these stubs have none.
REOPENING, two shapes: (a) annotate the mirror stubs (a signature the live source does not
carry — decide whether that is a fidelity divergence before doing it), or (b) a
`generator -> int` (opaque iterable handle) inference. **NOTE BEFORE SPENDING ON IT:
`walk` is not convertible anyway — `while todo:` emits `while true`, the guard erased.
Check each member individually.**

### A REAL EMITTER BUG, found, diagnosed, NOT fixed — `_decl_arity`
`abstract_ops._add_abstract_op` disambiguates a same-name collision by arity, and computes
arity as **`decl.count("(x")`** — a count of parameter groups whose first binder is NAMED
`x`. So `val setattr_3 (x: int) (f: int) (v: int) : unit` reads as arity ONE and
`val setattr_3 (x0: int) (x1: int) (x2: int) : int` as arity THREE; they are filed under
different KEYS and **both are emitted under the same Why3 symbol** — "Symbol setattr_3 is
already defined in the current scope". That is the entire blocker for `copy_location` and
`NodeTransformer.generic_visit`.

A correct `_decl_arity` (count binder NAMES inside each `(names : type)` group) was written
and MEASURED in an isolated worktree. **The arity fix alone is CORPUS-BYTE-INERT — 814/814
identical.** What it exposes is the layer underneath, and both tie-breaks were measured:

- **`_decl_arity` + the existing "keep the LONGER" tie-break**: only the `: int` mint of
  `setattr_3` survives, and the statement-position call in `_Parser._fin_pos` then reads
  `This expression has type int, but is expected to have type ()`. The fix is one line in
  the statement emitter — wrap a non-`unit` call in statement position as `let _ = … in ()`,
  which it already does elsewhere.
- **`_decl_arity` + "keep the FIRST"**: REFUTED, do not take this route. It breaks
  `Module3_Weaver.mlw` outright (`unbound function or predicate symbol 'get_value'` — the
  longer decl was the one carrying the needed symbol) and it moves `expressions.mlw` off
  byte-identity (`val str_eq_op (a: string) (b: string)` -> `(a b: string)`, two spellings
  of the same signature that the OLD arity miscount had been resolving by length).
  With it, `copy_location` gets one level further and fails at
  `setattr_3 new_node !attr value` — `!attr` is a `string` from a `seq string` loop where
  the formal is `int`, i.e. this window's own string->int family, one call shape further out.

**Priced at three linked mechanical fixes; not started because the window'"'"'s proof was in
flight.** No part of it is in the tree — re-derive from this paragraph.

### `visit_If` — the ONE boundary #29 recorded, re-tested and CONFIRMED
It now TYPECHECKS under `@mutable_state` (it did not before). It is still not provable:
the emitted body carries `while <cond> do … done` with **no `variant`**, because the
source `while` walks `node.orelse[0]` down the AST and the int model has no measure for
that. **Type-checking is not provability — do not read a green `tc.sh` as a conversion.**

## THE HELPERS LEFT IN THE TREE (all under `scratchpad/`, all still current)
`tc.sh` (emit+typecheck pure_ast, 1.8 s) · `port.py` / `port2.py` (live body -> mirror) ·
`restub.py` · `tryport.sh` (port-test-KEEP) · `diag.sh` (port-test-REVERT-and-report) ·
**`sibcon.py add|del <names>` (NEW: add/remove `#@ sibling_concrete` on `_Unparser`
methods)** · `mirror_md5.sh`.

## INSTRUMENT FACTS #30 ADDS
1. **`bin/byte-diff-sweep.sh` needs `$ROOT/.venv`.** In a detached worktree it silently
   emits ZERO files and `diff -rq` then reports every file as "only in", which looks like
   a catastrophic byte-diff. `ln -s /home/fabrice/git/pycsl/.venv <worktree>/.venv` first.
2. **The Bash tool caps at 600 s.** The `pure_ast.py` whole-file proof does not fit;
   run it with `run_in_background` writing a `.done` sentinel and poll. A proof is
   READ-ONLY, so backgrounding it does not violate the ownerless-writer rule — a
   port/prove/REVERT sweep still does.
3. **The proof cost of `sibling_concrete` on the hubs is large.** `pure_ast.py` proved in
   **9 minutes** with the hubs abstract; with `write`/`traverse`/`fill` concrete the Z3
   phase alone ran past 30 minutes. That is lesson (bc)'s cost curve, and it is the price
   of the fidelity — budget for it, do not read it as a hang.

## THE PROOF PLANE DID ITS JOB TWICE, AND BOTH FINDINGS ARE LOAD-BEARING

### `traverse` CANNOT be `#@ sibling_concrete` — a REAL boundary, newly found
Routing `self.traverse(...)` concretely makes `traverse` / `visit` / every `visit_<Node>`
ONE MUTUALLY RECURSIVE GROUP, and Why3 then demands a termination measure for it. There
is none in the int model: `traverse` descends `AST | list[AST]` and the argument is an
opaque int. **Measured: 124 unproven goals, EVERY ONE of them `Sub-goal termination`**,
spread over 30 visitors. Reverted `traverse` alone; the other five hubs stay concrete.
REOPENING CAPABILITY: a structural measure on the node handle — i.e. the same recursive
node ADT the campaign has repeatedly declined, now with a second, independent reason to
want it. **Do not retry `sibling_concrete` on `traverse` without one.**

### `val str_repeat_op` carried a PRECONDITION PYTHON DOES NOT HAVE
It declared `requires { n >= 0 }`. In Python `"ab" * -1` is `""` — repetition by a
non-positive count is TOTAL. The guard was an over-restriction of the model AND it was
load-bearing: `_Unparser.fill` lowers `"    " * self._indent + text`, `self._indent` is an
opaque `getattr__unparser` read, so `n >= 0` is not provable at the call site — and that
single precondition was **the ONE unproven goal in the whole 3097-goal file**, in two
successive full proofs.

Replaced with the faithful total contract:
```
ensures { n >= 0 -> String.length result = n * String.length s }
ensures { n < 0  -> String.length result = 0 }
```
Strictly WEAKER as a requirement, strictly MORE INFORMATIVE as a postcondition, so nothing
that proved before can stop proving. Corpus cost: exactly 2 files (`0482`, `0483` — the
`s * n` / `n * s` reference tests), each diff exactly those three lines, both re-verified
`Verification SUCCESS`. **This is M1 discipline, not drift. Do not "fix" it back; the
byte-diff baseline for the next worker is HEAD.**

**LESSON (bh): when one goal in a 3000-goal file will not discharge, read the CONTRACT it
comes from before touching the code that calls it.** Two windows of effort had gone into
the caller (`fill` was reverted at the fourth link by #29). The defect was one clause in a
`val` declaration, and it was not modelling Python.

## WHERE THE LADDER STANDS FOR THE NEXT RELAUNCH

1. **The `_decl_arity` chain** (three linked mechanical fixes, fully diagnosed above,
   nothing in the tree). Buys `copy_location` and `NodeTransformer.generic_visit` directly
   and removes a duplicate-symbol emitter defect that can bite any file.
2. **The `()`-vs-`int` GENERATOR family in `pure_ast.py`** — the largest single blocker
   family left in the file (10 stubs). Decide the generator return-type question first;
   check each member individually, several are not convertible for other reasons.
3. **The remaining 14 shadowed methods / 121 bypassing sites.** `traverse` (88 sites) is
   now a recorded boundary. The other 13 are `_`-named, in `Module5_IREmitter`,
   `stmt_control_flow`, `auto_trust`, `expressions`, `functions`, `statements` — none has
   been tried with `#@ sibling_concrete`, and the directive has now worked on five hubs in
   one increment. **Cheapest remaining fidelity win in the tree.** It buys no markers.
4. `Module1_Ingestor` / `Module2_Parser`: refuted as a cheap-inference target (measured
   above). Do not re-rank them without new evidence.
5. `visit_If` (real boundary, re-confirmed), `_write_fstring_inner` (unlisted `ValueError`),
   `visit_MatchClass`/`visit_Dict`/`visit_MatchMapping` (tuple patterns),
   `visit_arguments`/`__init__`/`_str_literal_helper` (`array int @rho`),
   `interleave`/`items_view` (the closure FORMAL, still untried — #29's ladder item 2).

---

# HANDOFF — #29 FINAL ENTRY (2026-09-01, WINDOW 3): **491 -> 462. TWENTY-NINE MARKERS
# in one window — more than the previous three windows combined — and not one of them
# needed a new value model. Every unlock was a ONE-LINE gap in the emitter that an
# earlier relaunch had recorded as a value-model boundary.**

## THE NUMBER

| | markers | grep | offset | unattached | ledger |
|---|---|---|---|---|---|
| window start | 491 | 516 | 25 | 0 | 3 |
| **window end** | **462** | **487** | **25** | **0** | **3** |

Seven commits, every one gated on all planes, tree clean, no prover process left running.

| commit | markers | what unlocked it |
|---|---|---|
| `6f059995` | — | ITEM 0: the `csl_to_ir_op` "live unsoundness" REFUTED (a stale comment) |
| `772cad82` | — | the `_Unparser` boundary REOPENED (`_PURE_AST_FIELD_TABLE` already exists) |
| `e2a9a35b` | 491 | `visit_Name` record + `str_hash_op` for computed string vararg elements |
| `c633e7e1` | **488** | bool-actual coercion + the `-> int` trusted-stub disjunct, BOTH producers |
| `430f6ca5` | **477** | `unit -> unit` closure formal — the "higher-order formals" block |
| `8a5803e0` | — | INSTRUMENT: `probe-conversion-candidates.py` repaired (3 bugs, 38% of the tree) |
| `50c7bba6` | **469** | HOISTED loop bound — for-over-collection termination, with NO purity claim |
| `034227cf` | **464** | mixed string/int `+` was emitting a raw Why3 `+` |
| `abda560f` | **462** | `-> int` on a `unit` stub + the `s * n` string-repetition recognizer |

## THE SEVEN EMITTER CAPABILITIES THIS WINDOW ADDED — all fail-closed, all corpus-audited

1. `str_hash_op` coercion for a COMPUTED string actual packed into a `seq int` vararg
   (`expressions.py::_handle_dotted_call`, which now receives the source arg IRs). String
   LITERALS deliberately stay on `_coerce_to_int` so every existing literal write is
   byte-identical.
2. BOOL ACTUAL INTO AN INT FORMAL — reuses the emitter's own `_bool_ir_to_int_wrap`.
   Fires only where the formal is `int` AND the actual is a bool-source IR, i.e. only
   where the emitted file was ALREADY ill-typed: byte-inert by construction.
3. The `-> int` `\trusted`-stub return-type disjunct, in **both** producers
   (`_compute_return_type` AND `_build_method_return_type_map`).
4. `unit -> unit` inference for a ZERO-ARGUMENT closure actual (`(fun () -> …)`).
5. HOISTED PROGRAM LOOP BOUND: `let _len<idx> = <program length call> in` before the loop,
   used in the guard AND the variant. Two gates: **no mutable deref in the length term**
   (SOUNDNESS — hoisting freezes the bound) and not an `@mutable_state` class (blast radius).
6. MIXED STRING/INT `+` routed to the int-model `str_concat` the f-string path already uses.
7. `s * n` STRING-REPETITION recognized as string in `_is_string_expr` (the lowering
   already emitted `str_repeat_op … : string`).

## THE LESSONS — read these before touching anything

**(bb) In a mature emitter, "the value model cannot express this" is far more often a
MISSING ONE-LINE INFERENCE than a missing model.** Five separate boundaries recorded by
#23/#24/#27 were each one line. The discriminator is mechanical: **read the L3-tc error,
then grep the emitter for the mechanism that already handles the ADJACENT case.** The
`array int` inference sat three lines above the missing `unit -> unit` one. The `-> str`
disjunct sat one line above the missing `-> int` one. `_bool_ir_to_int_wrap` was already
imported into the same file.

**(bc) Re-prove the WHOLE file, never just the new goals.** A 20-port batch produced 20
non-Valid goals — ten were the new loop bodies and **ten were `get_docstring`, which had
been Valid at 0.00 s one increment earlier**. Unknown / Out-of-memory / Timeout, never
Invalid. Reverting the one genuinely-unprovable body restored it to 0.00 s. **A conversion
batch has a context cost that lands on goals it never mentions, and the cost is
proportional to how much UNPROVABLE material is in the file — so a failing goal elsewhere
is a signal to find and remove the one bad body, not to shrink the batch.**

**(bd) A MEASUREMENT INSTRUMENT IS A CLAIM LIKE ANY OTHER**, and its failure mode is the
worst kind: it reports a HARNESS bug in the vocabulary of a REAL boundary, so every reader
downstream inherits a fabricated wall. `probe-conversion-candidates.py` had three bugs; one
of them turned a Python `SyntaxError` (its own bad dedent of module-level bodies) into
`L3TC-FAIL ['expected an indented block']` for **133 of 352 verdicts, 38% of the tree**.
The tell needed no domain knowledge at all: 133 "type errors" that were word-for-word the
same SyntaxError. **Aggregate an instrument's output and look at the SHAPE of the
distribution before acting on any single verdict.**

**(be) A PORT DOES NOT INHERIT ITS STUB'S FRAME.** `#@ assigns \nothing` is harmless on a
`\trusted` stub (whose emitted `val` has no body) and becomes a FALSE FRAME the instant the
method enters the converted population, where `writes { }` is checked against an ERASURE of
the live body. Seven `_Unparser` ports used `with self.block():` (which writes
`self._indent`) and had to re-declare `#@ assigns self._indent`. Re-derive the frame on
every port.

**(bf) The gate planes are NOT redundant — each one caught a different bad port, three
separate times this window.** NON-VACUITY caught `get_type_comment` INPUT-BLIND (twice).
SHADOWED-SELFCALLS caught `_type_params_helper` / `_write_fstring_inner` / `_function_helper`
(three times — do not attempt them a fourth). FRAME-HONESTY caught the `block()` family.
The PROOF caught `visit_If`'s termination and the context blowup. **The candidate filter's
CLEAN verdict was refuted 2 out of 2 times by non-vacuity** (`Module3_Weaver`
`_attach_loop_contracts` / `_region_bound_str` — both erase an input). CLEAN is a filter,
never a gate.

## WHAT REMAINS ON `_Unparser` — every entry with its MEASURED reason

Reproduce any of these in ~4 seconds: `python3 scratchpad/port.py <name>` then
`./scratchpad/tc.sh`. Helpers left in the tree: `port.py` / `port2.py` (port a live body
into the mirror), `restub.py` (put it back as a `\trusted` stub), `tryport.sh` (port, test,
KEEP on green), `diag.sh` (port, test, REVERT and report), `tc.sh` (emit + typecheck, 1.8 s),
`mirror_md5.sh <root>` (52-mirror md5 sweep, 6.5 s).

| method | measured blocker |
|---|---|
| `visit_If` | `Sub-goal termination` — a genuine `while node.orelse and len(node.orelse)==1 and isinstance(…)`, not a for-over-collection, so no auto-variant applies and the source supplies no measure. **A REAL boundary.** |
| `_function_helper`, `_type_params_helper`, `_write_fstring_inner` | SHADOWED — call sites route through `val self__<m>_<n>`. Rejected three times. |
| `get_type_comment` | INPUT-BLIND (non-vacuity), twice. |
| `visit_BoolOp` | `This function is stateful, it cannot be used as pure` |
| `visit_Dict`, `visit_MatchMapping` | nested `def` (a local function) |
| `visit_MatchClass` | `This pattern has type ('mu, 'mu1)` — a tuple pattern |
| `visit_arguments`, `__init__` | `array int @rho` — a mutable list literal |
| `visit_MatchStar` | `string` vs `int` at an f-string over an optional name |
| `visit_JoinedStr`, `visit_FormattedValue` | nested `def` / `seq` clash |
| `interleave`, `items_view` | `This expression has type int, it cannot be applied` — a function-VALUED FORMAL (`f`, `traverser`) called inside the body. The dual of capability 4: that one types a closure ACTUAL, this needs a closure FORMAL. |
| `set_precedence` | `seq int` vs `int` — `self._precedences[node] = precedence`, a dict keyed by a NODE |
| `fill` | the string-literal TERNARY `"except*" if self._in_try_star else "except"` lowers to int hashes, because the `IfExpr`-is-string rule in `_is_string_expr` is gated on `@mutable_state` and `_Unparser` is not one |
| `buffered`, `delimit_if`, `_str_literal_helper`, `_write_docstring_and_traverse_body` | array/int clashes |

### THE TWO NAMED, PRICED, NOT-YET-TRIED CAPABILITIES

**(A) `@mutable_state` on `_Unparser`.** It genuinely has mutable state (`_source`,
`_indent`, `_precedences`), so the annotation is TRUE, and it turns on the whole typed-local
pre-decl family plus the `IfExpr`-is-string rule for the class at once — which is what
`fill` (a 14-use hub) needs. **WARNING, measured: it will also flip ~7 currently
"unmodelled" false frames to MODEL-VISIBLE, and the model-visible ratchet is a hard 0.**
Every one of those `#@ assigns` would have to become truthful first. That is the increment's
real cost and it is the honest one — those frames are false today either way.

**(B) A closure FORMAL.** `interleave(self, inter, f, seq)` and `items_view(self, traverser,
items)` take a function and CALL it. Capability 4 types a closure ACTUAL as `unit -> unit`;
the formal side needs the same treatment plus an effect story for the call. Two hub markers,
and it is what the whole `interleave` family's remaining depth rests on.

### `option string` RECORD-FIELD READS — still unbuilt, still priced
`MatchAs.name`, `ExceptHandler.name`, `keyword.arg`, `MatchStar.name` are `OptStr` ->
`option string` and the emitter has no read path for an option-typed record field.
REOPENING: a truthiness form (`<> None`) and a value form
(`match f with Some v -> v | None -> "" end`). Note `visit_alias` converted WITHOUT it, via
capability 6 — so the option path is now worth less than it was.

## THE REST OF THE TREE — probed, and it is genuinely harder

Every mirror was probed with the REPAIRED harness. Outside `pure_ast.py` there are exactly
**two** CLEAN candidates in the whole tree (`Module3_Weaver._attach_loop_contracts` and
`Module3_Weaver._region_bound_str`) and **both were refuted by non-vacuity** — each erases an
input. Everything else is L3TC-FAIL or ERASURE. The ranked blocker census across the tree,
now that the harness reports real reasons: `string`-actual-into-`int`-formal (50),
`unit`-returning-callee-used-as-a-value (20), `int`-actual-into-`string`-formal (17),
`array int @rho` (16), unbound symbol (12), array/int (7), tuple pattern (6). **The first
two are the SAME families this window already fixed twice** — they are the next place to
look, in `Module1_Ingestor.py` and `Module2_Parser.py`, which hold most of them.

## INSTRUMENT FACTS (carry forward)

1. **`export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH` ON EVERY GATE.**
   `_why3_typecheck` returns `(True, "(why3 not found — typecheck skipped)")` on
   `FileNotFoundError` and the caller prints `L3-tc ✓` + `Verification SUCCESS` without ever
   printing the skip reason. #29 hit this in its first hour on a file why3 rejects outright.
2. emit+typecheck `pure_ast.py`: **1.8 s**. 52-mirror md5 sweep: **6.5 s**. corpus
   byte-diff sweep: **31 s** per side. whole-file proof of `pure_ast.py`: **~50-60 min**.
3. **`check-self-annotate-sync.sh` is a LIVE PLANE FOR EMITTER EDITS.** Editing
   `module6_whyml/functions.py` took DIVERGED 2 -> 4 because `_compute_return_type` and
   `_build_method_return_type_map` are UN-trusted in the mirror. `_handle_dotted_call` needed
   nothing — it is a `\trusted` stub there. That asymmetry is the plane working.
4. The corpus byte-diff is **NOT 0** any more, by design and with M1 justification: exactly
   3 files (0418, 0884, 0886) carry the hoisted loop bound. 0418/0886 are `--no-proof` and
   re-emit L3-tc ✓; 0884 is `# pycsl-expected: FAIL` and still FAILS. **Use
   `scratchpad/corpus_head` semantics carefully: a future worker's "byte-diff 0" baseline is
   now HEAD, not the window-start tree.**
5. The trusted frame-honesty TOTAL ratchet was lowered **70 -> 68** this window.

---

# HANDOFF — #29 THIRD ENTRY (2026-09-01, WINDOW 3): **491 -> 477. FOURTEEN MARKERS.
# The `_Unparser` "CERTIFIED-BOUNDARY" was not a boundary at all — it was five separate
# ONE-LINE gaps in the emitter, each recorded by an earlier relaunch as a body block.**

## THE HEADLINE, AND THE LESSON UNDER IT

Three relaunches (#24, #25, #26, #27, #28) worked this wall and recorded it as a value-model
CERTIFIED-BOUNDARY needing a 76-arm recursive node ADT. What actually unblocked it:

| what #24/#27 recorded | what it actually was | size |
|---|---|---|
| "higher-order formals" body-block (8 of 13 leaves) | the emitter ALREADY lowers `lambda: self.write(", ")` to a real Why3 closure `(fun () -> …)`; only the FORMAL was missing, because an abstract self-call avatar default-types every parameter `int` | **one line** in `_handle_dotted_call`'s param-type loop |
| "a bool actual is a LOUD type error" (`require_parens`, #23) | the emitter already OWNS the coercion — `_bool_ir_to_int_wrap` in types.py, the same detector `return isinstance(...)` uses — it was just never applied at an argument position | **one loop** |
| "computed string element into `seq int`" (`visit_TypeVarTuple`/`ParamSpec`, #24) | `_coerce_to_int` hashes string LITERALS only; a computed string needed the same `str_hash_op` | **one branch** |
| "per-(node-type,field) projector typing = the pyx_view node ADT" (#27) | `_PURE_AST_FIELD_TABLE` + a `node: "<Class>"` param annotation, in production since #19 | **one table row** |
| a `\trusted` `-> int` stub's caller fails with `()` vs `int` | the `-> str` / `-> bool` disjunct already existed; `int` was simply missing, in BOTH producers | **two branches** |

**LESSON (bb): in a mature emitter, a "the value model cannot express this" verdict is far more
often a MISSING ONE-LINE INFERENCE than a missing model.** The five above were all recorded as
capability-level boundaries by workers who had just measured the failure. The discriminator is
cheap and mechanical, and it is the same one every time: **read the L3-tc error, then grep the
emitter for the mechanism that already handles the ADJACENT case.** `array int` inference sat
three lines above the missing `unit -> unit` inference. The `-> str` disjunct sat one line above
the missing `-> int` disjunct. `_bool_ir_to_int_wrap` was already imported into the same file.
None of it needed a new model; it needed someone to look at the line next door.

## WHAT LANDED (three commits, all gated on every plane, all clean)

| # | commit | markers | what |
|---|---|---|---|
| 1 | `e2a9a35b` | 491 (neutral) | `visit_Name(node: "Name")` — first per-node RECORD in the emitted mirror; `val get_id` GONE, payload is `str_hash_op node.id`. Plus the `str_hash_op` coercion for computed string vararg elements. |
| 2 | `c633e7e1` | 491 -> **488** | `visit_TypeVarTuple`, `visit_ParamSpec`, `require_parens`. Plus the bool-actual coercion and the `-> int` trusted-stub disjunct in BOTH producers. |
| 3 | `430f6ca5` | 488 -> **477** | eleven `interleave(lambda: …)` visitors. Plus the `unit -> unit` closure-formal inference. |

Final state, driver-verified fresh: **markers 477 · grep 502 · offset 25 · unattached 0 ·
ledger 3.** pure_ast.py 2873/2873 Valid SUCCESS; functions.py 1199/1199 Valid SUCCESS;
corpus byte-diff 0 (814/814); fidelity 2 DIVERGED / 3 drifted (baseline); non-vacuity no NEW
erasure; shadowed-selfcalls 13; frame-honesty trusted 0/68 + converted 2/68 (the trusted TOTAL
ratchet was LOWERED 70 -> 68 in commit 3). No prover process left running.

## THE THREE GATE PLANES EACH CAUGHT A DIFFERENT BAD PORT — keep every one of them

This batch is the clearest demonstration in the campaign that the planes are not redundant:

- **NON-VACUITY** caught `get_type_comment` as INPUT-BLIND (`erased=['node'] of ['node']`) — a
  conversion whose emitted body ignores its only argument. Nothing else would have seen it.
- **SHADOWED-SELFCALLS** caught `_type_params_helper` and `_write_fstring_inner` (15 > ratchet
  13): the call sites still route through `val self__<m>_1`, so the marker would have gone while
  the body stayed invisible to every caller.
- **FRAME-HONESTY** caught five ports at once and was fixed HONESTLY, not by reverting:
  `do_visit_try`/`visit_If`/`visit_With`/`visit_AsyncWith`/`visit_Match` use `with self.block():`,
  which writes `self._indent`. `#@ assigns \nothing` is harmless on a `\trusted` stub and becomes
  a FALSE FRAME the instant the method enters the converted population. They now declare
  `#@ assigns self._indent`. **A port must re-derive its own frame; it does not inherit the
  stub's.**
- **THE PROOF PLANE** caught the rest — see the next section, which is the finding to keep.

## THE PROOF FINDING — a batch can break a goal it does not touch

The first battery on the full 20-port batch FAILED: 2904 goals, 2884 Valid, **20 non-Valid**.
Ten were `Sub-goal termination` of the newly ported LOOP bodies. **The other ten were
`get_docstring` postcondition sub-goals that had been Valid at 2862/2862 one increment
earlier** — Unknown / Out-of-memory / Timeout, never Invalid. Reverting the nine loop-carrying
ports restored `get_docstring` to Valid in **0.00 s**, which is the proof that the cause was
those bodies and nothing else.

**LESSON (bc): re-prove the WHOLE file, never just the new goals — and read a previously-Valid
goal turning Unknown as a SIZE signal, not a correctness signal.** A conversion batch has a
context cost that lands on goals it never mentions.

## THE ONE REAL BOUNDARY THIS WINDOW HIT, and it was already written down

`for gen in node.generators:` lowers to `while !_idx_gen < (iter_length (get_generators node))`
with NO variant. `module6_whyml/stmt_control_flow.py:1166-1180` already documents why: the
auto-variant is admitted only when the length term is a pure LOGIC term (`Array.length` /
`Seq.length` / `String.length`), and `iter_length (get_generators node)` is a PROGRAM call,
which a Why3 `variant` term cannot mention at all.

**REOPENING CAPABILITY, PRICED, DELIBERATELY NOT TAKEN: promote `iter_length` and the node-field
projector in the length term to pure `val function`s.** NOT taken because it is a DETERMINISM
CLAIM on `iter_length` — `len` of an int-collapsed handle is constant only if the underlying list
is never mutated — and that is exactly the class of claim this campaign has twice caught as a
live unsoundness (see the `csl_to_ir` / `m5_current_class_present` repairs). It needs its own
increment with its own soundness argument, scoped to receivers that are provably immutable AST
nodes. **NINE markers ride on it**: `visit_Call`, `do_visit_try`, `visit_DictComp`,
`visit_GeneratorExp`, `visit_If`, `visit_ListComp`, `visit_Match`, `visit_SetComp`,
`visit_comprehension`.

## THE REMAINING `_Unparser` TRUSTED SURFACE — each with its MEASURED L3-tc error

Reproduce any of these in ~4 seconds: `python3 scratchpad/port.py <name>` then
`./scratchpad/tc.sh` (both left in the tree; `port.py` copies the LIVE body into the mirror and
drops the `#@ \trusted` line, `tc.sh` emits + typechecks with PATH set — 1.8 s per cycle).

| method | measured L3-tc error | shape of the fix |
|---|---|---|
| the 9 loop bodies above | `Sub-goal termination` (proof, not tc) | the `iter_length` variant capability |
| `visit_AugAssign`, `visit_Compare` | `has type string, but is expected to have type int` | `self.binop[<k>]` / `self.cmpops[<k>]` — a CLASS-level `str -> str` const dict, subscripted. `_is_string_expr` does not recognize `self.<table>[k]`, so `" " + <lookup> + "= "` emits a RAW Why3 `+` between two strings instead of `str_concat_op`. Same two-producer shape as the `s * n` repetition below. |
| `visit_BoolOp` | `This function is stateful, it cannot be used as pure` | a closure capturing mutable state used in a pure position |
| `visit_MatchClass` | `This pattern has type ('mu, 'mu1), but is expected to have type int` | a tuple pattern |
| `visit_Assign` | `has type (), but is expected to have type int` | another `unit`-returning trusted callee whose result is used |
| `visit_ImportFrom` | `seq int` vs `seq string` | the `"." * (node.level or 0)` repetition |
| `visit_alias`, `visit_MatchStar` | `option string` record-field READ | see below |
| `visit_Dict`, `visit_MatchMapping` | nested `def` (a local function) | body-blocked |
| `visit_arguments`, `__init__` | `array int @rho` (a mutable list literal) | |
| `visit_ClassDef`, `_function_helper` | `int` vs `array` | |
| `visit_JoinedStr`, `visit_FormattedValue` | nested `def` / `seq` clash | |
| `items_view`, `interleave`, `traverse`, `set_precedence`, `buffered`, `fill`, `_str_literal_helper` | hubs — see below | |

### `option string` RECORD-FIELD READS — priced, not built
`alias.asname`, `MatchAs.name`, `ExceptHandler.name`, `keyword.arg`, `MatchStar.name` are all
`OptStr` -> `option string`, and the emitter has NO read path for an option-typed record field:
`if node.asname:` emits the raw option against an int, and `" as " + node.asname` has no unwrap.
**REOPENING: a truthiness form (`<> None`) and a value form (`match f with Some v -> v | None ->
"" end`) for an option-typed record field.** Buys ~2 markers directly (`visit_alias`,
`visit_MatchStar`) plus real fidelity in three already-converted visitors.

### `fill` (a 14-use hub) — got THREE fixes deep and was reverted at the fourth
`text: str` annotation, `_for_helper(fill: str, …)` annotation, and a `_is_string_expr`
recognizer for the `s * n` repetition (whose LOWERING already emits
`str_repeat_op … : string` — a genuine two-producer disagreement, character-for-character the
same shape as the `binop[k]` one above). Its body then emitted correctly as
`str_hash_op (str_concat_op (str_repeat_op "    " indent) text)`. Reverted at the NEXT link:
`self.fill("except*" if self._in_try_star else "except")` — a string-literal TERNARY lowers to
int hashes because the `IfExpr`-is-string rule in `_is_string_expr` is gated on
`_current_self_type in _mutable_state_classes` and `_Unparser` is not a `@mutable_state` class.
**REOPENING, PRICED, NOT TRIED: put `@mutable_state` on `_Unparser`.** It genuinely has mutable
state (`_source`, `_indent`, `_precedences`), so the annotation is TRUE, and it would turn on the
whole typed-local pre-decl family for the class at once. It is a large single-step emission
change and needs its own increment.

### The `traverse` polymorphism — the reason the record model is not per-visitor incremental
`traverse(self, node)` is `if isinstance(node, list): for item in node: self.traverse(item) else:
super().visit(node)`, i.e. `AST | list[AST]`, so its formal is `(x0: int)`. The moment a
`_PURE_AST_FIELD_TABLE` row gives a field the `emit_ir` type, `self.traverse(node.<child>)` is a
type error, and `set_precedence`'s `seq int` vararg fails one line earlier. MEASURED on
`visit_Attribute`, `visit_arg` and `visit_TypeVar` — all three typecheck their own bodies and
fail at the first hub call. **Only visitors whose fields are ALL scalars can be annotated one at
a time** (which is exactly `Name`, `TypeVarTuple`, `ParamSpec`). NAMED CHEAP ROUTE, NOT TRIED:
tag every LIST-valued field as `ExprIR` (ONE opaque `emit_ir` standing for the whole list)
instead of `StmtIRList` — exactly as faithful as today's opaque `int`, and it makes `traverse`'s
formal uniform across the family.

## INSTRUMENT FACTS #29 ADDS

1. **`export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH` ON EVERY GATE.** `_why3_typecheck`
   (`src/pycsl/pycsl.py`) returns `(True, "(why3 not found — typecheck skipped)")` on
   `FileNotFoundError` and the caller prints `L3-tc ✓` and `Verification SUCCESS` WITHOUT ever
   printing the skip reason. #29 hit this in its first hour on a file why3 rejects outright.
2. **The emit+typecheck loop on `pure_ast.py` is 1.8 seconds.** `scratchpad/tc.sh` wraps it.
   Reach for it instead of reasoning about what the emitter will do.
3. **A full 52-mirror md5 sweep is 6.5 seconds** (`scratchpad/mirror_md5.sh <root>`); run it
   against a detached worktree at HEAD to get the sibling-emission set exactly.
4. **The corpus byte-diff sweep is 31 seconds** per side (`bin/byte-diff-sweep.sh <dir>`).
5. `scratchpad/port.py <names>` ports live bodies into the mirror; `scratchpad/restub.py <names>`
   puts them back as `\trusted` stubs; `scratchpad/tryport.sh` / `scratchpad/diag.sh` do
   port-test-keep and port-test-revert-and-report respectively.
6. **`check-self-annotate-sync.sh` is a LIVE PLANE FOR EMITTER EDITS.** Editing
   `module6_whyml/functions.py` took DIVERGED from 2 to 4 because `_compute_return_type` and
   `_build_method_return_type_map` are UN-trusted in the mirror; the hunks had to be copied into
   `src/self-annotate/src/module6_whyml/functions.py`. `_handle_dotted_call` needed nothing —
   it is a `\trusted` stub in the mirror. That asymmetry is the plane working.

---

# HANDOFF — #29 SECOND ENTRY (2026-09-01, WINDOW 3): **THE `_Unparser` CERTIFIED-BOUNDARY IS
# REOPENED. #27's named reopening capability — per-(receiver-node-type, field) projector typing —
# ALREADY EXISTS IN-TREE AND HAS SINCE RELAUNCH #19. It is `_PURE_AST_FIELD_TABLE` +
# a param annotation. PROVED BY BUILDING IT: `get_name`/`get_attr`/`get_id`/`get_arg` are GONE
# from four converted visitors and replaced by REAL `string` record fields.**

## WHAT WAS ACTUALLY TRIED (not scoped — run, with the emitted artifact inspected)

Probe, ~6 minutes, emission is **1.8 s** per cycle (`--no-proof --keep-mlw`), so this loop is
almost free — use it:

1. Added ONE entry to `_PURE_AST_FIELD_TABLE` (`src/pycsl/frontend/ir_resolve.py:688`):
   `"TypeVar": [("name", "string"), ("bound", "OptExprIR")]`.
2. Annotated ONE parameter: `def visit_TypeVar(self, node: "TypeVar")` (mirror AND live).

Emitted diff — 19 lines, and it is exactly the capability #27 declared missing:

```
+  type typevar = { mutable typevar_name: string; mutable typevar_bound: option emit_ir }
-  val get_bound (x: int) : int
-  let _unparser__visit_TypeVar (self: _unparser) (node: int) : unit
+  let _unparser__visit_TypeVar (self: _unparser) (node: typevar) : unit
-    self_write_1 (Seq.cons (get_name node) ...)
+    self_write_1 (Seq.cons node.typevar_name ...)      <-- a REAL `string`
-    if ((get_bound node) <> 0)         +    if (node.typevar_bound <> 0)
-    self_traverse_1 (get_bound node)   +    self_traverse_1 node.typevar_bound
```

Then `Attribute` / `Name` / `arg` — already IN the table, needing only the annotation — likewise
lost their `get_attr` / `get_id` / `get_arg` projectors for real `string` fields, AND their
`value` children became `emit_ir`, so `isinstance(node.value, Constant)` now lowers to the
ADT discriminant `py_isinstance_Constant_emit_ir_op node.attribute_value` instead of an int test.

## WHY FOUR WINDOWS MISSED IT — the lesson, and it is lesson (p) exactly

#27 traced `get_name` to its declaration site (`expressions.py:11918`), proved NO UNIFORM
per-attribute return type exists (correct, still correct), and named the reopening capability
"per-(receiver-node-type, field) projector typing = the node ADT (`pyx_view`)". #28 then SIZED
`pyx_view`. **Neither asked the census-FIRST question: does a mechanism for this already exist?**
It does, three of them, all in production:

| mechanism | where | keys on |
|---|---|---|
| `_PURE_AST_FIELD_TABLE` (28 entries) + `_harvest_node_spec_records` | `frontend/ir_resolve.py:688` | the node CLASS, per field: `string`/`int`/`ExprIR`/`OptStr`/`OptExprIR`/`ExprIRList`/`StmtIRList`/`RecList:R` |
| `_EMIT_IR_STR_ATTRS` / `_EMIT_IR_NODE_ATTRS` | `module6_whyml/expressions.py` | the ATTRIBUTE, on an `emit_ir` receiver |
| `_EMIT_IR_HANDLER_ATTR_PROJ` | same | the ENCLOSING HANDLER (`_current_emitting_func`) |

And `pure_ast.py:5010-5017` — the file's OWN comment, 20 lines above the `\trusted` stub — says
so in plain words: *"The node typing is FIXABLE and was fixed: annotate the parameter with the
harvested `_NODE_SPEC` record and the body emits ... reading the REAL fields."* Relaunch #19
wrote that. #24, #25, #26, #27 and #28 all worked inside this file and none of them applied it.

**LESSON (ba): `pyx_view` was never the blocker — it was the WRONG NAME for the blocker.** A
recorded reopening capability is a CLAIM, and the most expensive way for it to be wrong is to
name a capability you would have to BUILD when an equivalent one is already installed. #27's
refutation was sound and its conclusion ("no per-attribute type exists") is still true; only its
PRICE was wrong, by roughly two orders of magnitude — a 76-arm recursive ADT with a structural
variant, versus one table row and one `: "ClassName"` annotation. The campaign already has the
rule for this (lesson (p): census existing certified constructs BEFORE scoping a new one); what
this adds is **where to run that census: not over the model, over the EMITTER'S OWN TABLES.**
Corollary, and it is the sharper half: **the obstacle recorded against item 4 — "pure_ast's node
classes are synthesized at import by `type(name,(base,),body)`, so there is no static class
surface" — is TRUE AND IRRELEVANT.** The types never came from the classes. They come from the
`_NODE_SPEC` DICT LITERAL, harvested structurally from the source text, plus a hand-curated
per-field type table. A true obstacle guarding the wrong door blocks nothing.

## THE FULL PHASE-1 WORK LIST — MEASURED, NOT ESTIMATED

The record model and the `seq string` vararg must land TOGETHER (a `string` field cannot enter a
`seq int` write, and an int-sourced arg cannot enter a `seq string` write). With
`def write(self, *text: str)` the file has **74 write/fill call lines and exactly 16 non-literal
arguments**; every other write argument is already a real Why3 string literal. The 16, each with
its enclosing emitted function, its fix class, and whether it is TRIED:

| # | emitted line | function | argument | fix | status |
|---|---|---|---|---|---|
| 1 | 4318 | `visit_Attribute` | `get_attr node` | annotate param (`Attribute` already in table) | **DONE, works** |
| 2 | 4587 | `visit_Name` | `get_id node` | annotate param (`Name` already in table) | **DONE, works** |
| 3 | 4805 | `visit_arg` | `get_arg node` | annotate param (`arg` already in table) | **DONE, works** |
| 4 | — | `visit_TypeVar` | `get_name node` | table row + annotate | **DONE, works** |
| 5 | 4429 | `visit_ExceptHandler` | `get_name node` | NEW row `ExceptHandler: [type OptExprIR, name OptStr, body StmtIRList]` + annotate | not yet |
| 6,7 | 4534, 4538 | `visit_MatchAs` | `get_name node`, `str_concat 1174530543 (get_name node)` | NEW row `MatchAs: [pattern OptExprIR, name OptStr]` + annotate | not yet |
| 8 | 4821 | `visit_keyword` | `get_arg node` | NEW row `keyword: [arg OptStr, value ExprIR]` + annotate | not yet |
| 9 | 4155 | `block` | `extra` | annotate `def block(self, *, extra: str = None)` | not yet |
| 10,11 | 4169, 4171 | `delimit` | `start`, `py_end` | annotate `def delimit(self, start: str, end: str)` | not yet |
| 12 | 4504 | `visit_Lambda` | `buffer` | a buffered-list local — needs its source typed | not yet |
| 13,14 | 4746, 4349 | `visit_UnaryOp`, `visit_BinOp` | `!operator` | local from the `self.unop[...]` / `self.binop[...]` string-table lookup | not yet |
| 15 | 4126 | `_write_constant` | `repr_conv value` | `repr()` returns `str`; `repr_conv` is an int-returning abstract op | not yet |
| 16 | 4119 | `_write_str_avoiding_backslashes` | `str_concat (str_concat !quote_type !string) !quote_type` | needs `_str_literal_helper -> Tuple[str, List[str]]` | **TRIED, blocked — see below** |

### #16 is the only one with a MEASURED obstacle, and it is small and named

`def _write_str_avoiding_backslashes(self, string: str, ...)` works immediately — the param
retypes to `string`. The blocker is one slot type: `_str_literal_helper` (a `\trusted` stub, so
its DECLARED annotation is the only authority on its return) needs
`-> "Tuple[str, List[str]]"`, and `ir_resolve`'s per-slot table (the `_SLOT_WHYML` dict,
~line 1395) recognises `str`/`bool`/`int`/`PyConstVal`/`ExprIR`/`StmtIR`/`IRNode`/
`ContractExprIR` and `List[<node type>] -> seq emit_ir`, but **NOT `List[str]`**, so the whole
annotation is refused fail-closed and the return stays `(int, int)`.
**REOPENING CAPABILITY, PRICED: one row — `List[str] -> "seq string"` in `_SLOT_WHYML` — plus
whatever `subscript_get` needs to project a `seq string` element (`quote_types[0]`).** The table
is CLOSED and unrecognised slots already break out to the int-erased form, so widening it is
a pure widening. NOT YET TRIED — that is the next move.

## STATE OF THE TREE AT THIS ENTRY

The probe is IN FLIGHT and is NOT committed to `src/`. It is saved verbatim at
`getting-better/interrupted/2026-09-01-29-unparser-record-model.patch` (124 lines, 3 files:
`ir_resolve.py` table row, and the `pure_ast.py` annotations in BOTH the live and mirror copies).
It currently FAILS L3-tc at item #16 — that is expected and is the frontier, not a regression.
Metric unchanged: markers 491 · grep 516 · offset 25 · ledger 3.

## INSTRUMENT WARNING #29 PAID FOR — read this before you trust any `L3-tc ✓`

`_why3_typecheck` (`src/pycsl/pycsl.py`) does `subprocess.run(["why3", ...])` and, on
`FileNotFoundError`, **`return True, "(why3 not found — typecheck skipped)"`** — and the caller
prints `[level] L1 ✓ L2 ✓ L3-tc ✓` and `Verification SUCCESS`. The skip reason is returned but
NEVER PRINTED on the success path. `why3` is NOT on the default PATH here (it is only in
`/home/fabrice/.opam/framac-coq8/bin`, and there is no `default` opam switch, so
`bin/run-rocq-proofs.sh`'s `$HOME/.opam/default/bin` export points at a directory that does not
exist). #29 hit this within the first hour: a run reported `L3-tc ✓` on a file `why3` rejects
with a hard type error two lines long. `export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH`
on EVERY gate — the handoff's instrument-fact #1 has said so for windows and it is still the
easiest way to fabricate a green in this repo.

---

# HANDOFF — read this FIRST on relaunch (prepended 2026-09-01, RELAUNCH #29 worker — WINDOW 3 START)

## #29 ITEM 0 IN ONE LINE: **`csl_to_ir_op` is NOT a live unsoundness. It was FIXED in the same
## increment that fixed its sibling (#19), and the "KNOWN-LIVE" record was a STALE PYTHON COMMENT
## quoted forward through four relaunches. The #19 CLOSED entry is the true one.**

### THE EVIDENCE (source + all 53 emitted mirrors, read-only, ~3 minutes, zero prover time)

| check | command | result |
|---|---|---|
| pure symbol exists anywhere? | `grep -rn "val function csl_to_ir_op" src/` | **ZERO hits** |
| logic-level fold exists? | `grep -rn "function synth_overload_clauses\b" src/ \| grep -v _prog` | **ZERO code hits** (2 prose hits, both in `preamble.py` comments) |
| declaration as emitted | `src/pycsl/module6_whyml/preamble.py:6754` | `"  val csl_to_ir_op (e: emit_ir) : emit_ir"` — a **PROGRAM** `val` |
| the consuming fold | `preamble.py:6755-6765` | `let rec synth_overload_clauses_prog … variant { ens }` — **PROGRAM code**, structural descent on `list ens_node`, no `diverges`, no pinning `ensures` law |
| what actually landed in the mirrors | `grep -rn csl_to_ir_op --include=*.mlw` | 4 mirrors (`ir_resolve`, `pycsl`, `frontend/__init__`, `Module5_IREmitter`), 2 code lines each: the program `val` and its one program-context application |
| any spec-context use? | same grep filtered to `requires\|ensures\|invariant\|variant\|assert` | **NONE** |

So on both planes — the emitter source AND the emitted artifact — the symbol is a program `val`
applied only in program contexts. **There is no determinism claim to violate. The defect is CLOSED.**

### WHERE THE FALSE RECORD CAME FROM — this is the reusable finding

`preamble.py:6397-6409` is the SOUNDNESS comment for the *sibling* symbol `csl_to_ir`. Its last
three lines read (verbatim, before this commit):

> `# SIBLING csl_to_ir_op below CANNOT be demoted the same way — it is applied inside the`
> `# LOGIC-level function synth_overload_clauses fold, so removing its purity requires`
> `# redesigning that fold; recorded, not silently kept.`

That was TRUE when written and FALSE ~350 lines later in the same file, because the very same
increment (#19) then went and did the redesign: it rewrote the fold to `synth_overload_clauses_prog`
and demoted the symbol. **The comment outlived the fix by one edit.** Nobody re-read the code it
described; four consecutive handoffs quoted the comment's conclusion forward, each time with
*higher* confidence than the last ("recorded, not silently kept" -> "STILL OPEN, UNFIXED" ->
"KNOWN-LIVE UNSOUNDNESS"). Meanwhile `driver-backlog.md:5536` had the correct verdict the whole
time ("Two offenders were repaired: `csl_to_ir_op` … and `m5_current_class_present`") — the record
contradicted itself across two files and the LOUDER file won.

**The comment is now corrected in place** (`preamble.py`), and it carries the disconfirming
evidence with it so the next reader cannot re-derive the false claim. It is a Python `#` comment,
never emitted — grep confirms `"CANNOT be demoted"` appears in ZERO `.mlw`, so this edit is
byte-inert BY CONSTRUCTION, not merely by measurement. `_emit_exprir_theory` is absent from the
mirror's `preamble.py` (408 lines vs the live 9177), so the fidelity plane has nothing to say
about it either.

### LESSON (az) — THE ONE THIS BANKS

**A stale comment is more dangerous than a stale record, because it sits at the scene of the crime
and therefore reads as primary evidence.** The five lessons so far all say "re-derive the claim
from the source." This one adds the trap: a code comment *is* source, and a reader who dutifully
"checks the source" can land on the comment and stop, feeling rigorous. The discriminator is cheap
and mechanical: **a claim about a SYMBOL must be settled by grepping the SYMBOL, never by reading
prose that mentions it.** One `grep "val function csl_to_ir_op"` — four seconds — beat four
relaunches of careful documentation. Corollary: when two records disagree, the one that cites a
COMMAND beats the one that cites a NARRATIVE, regardless of which is more recent or more emphatic.

Corollary for this campaign specifically: whenever a comment says "X CANNOT be done, recorded not
silently kept", check whether a LATER hunk in the SAME FILE does X. That is exactly the edit
sequence that produces this failure.

### STATE AT #29 WINDOW START (verified fresh)

markers **491** · grep-substring 516 · offset 25 · attached 491 · unattached 0 · ledger 3 ·
tree clean (tracked) · HEAD was `b2c3a6d6`.

### LADDER FOR THE REST OF WINDOW 3 (unchanged below item 0)

1. Backlog item 4 — `pyx_view` node ADT / per-(receiver-node-type, field) projector typing.
   SIZED by #28: a `pure_ast`-LOCAL lever (144 of 172 `get_<attr>` use sites), not a campaign-wide
   unblocker. Obstacle: `pure_ast` node classes are synthesized at import by `type(name,(base,),body)`
   from `_NODE_SPEC`. Precedent: the `_optional_union_locals` / `_term_local_vars` carrier-field
   projections immediately above `expressions.py:11918`.
2. `ControlFlowStmtMixin._handle_return_stmt` (the converted-population frame residue).
3. `scratchpad/w3/fix_assigns.py` re-tests.

**Item 5 of #28's ladder ("STILL OPEN, UNFIXED: `val function csl_to_ir_op`") is DELETED, not
demoted. Do not re-open it. If you see it quoted again, the quote is from a pre-#29 handoff.**

---

# HANDOFF — read this FIRST on relaunch (prepended 2026-09-01, RELAUNCH #28 worker — WINDOW END)

## #28 IN ONE LINE: **the `pyx_view` node-ADT capability is now SIZED, and it is SMALLER than it
## reads: the generic `get_<attr>` fallback is declared in only 7 of 53 emitted mirrors, and
## 144 of its 172 use sites (84%) are in `pure_ast.mlw` alone. It is a pure_ast-LOCAL lever,
## not a campaign-wide unblocker.**

#28 got the final ~5 minutes of the 96h window (last relaunch). Per the supervisor it started no
prover run, attempted no port, made ZERO edits to `src/`. It spent the sliver on the read-only
census #27 queued: how much of the remaining 491 routes through the same generic `get_<attr>`
emitter fallback that #27 refuted a `string` return model for. Pure `python` over the 53 already-
emitted `.mlw` on disk (all mtime 2026-09-01, i.e. fresh), ~20 s, no emission needed.

Metric verified fresh at window end: **markers 491 · grep 516 · offset 25 · attached 491 ·
unattached 0 · ledger 3.** Tree clean (tracked), no prover process started. HEAD was `c9e08136`.

### THE SIZING (measured; do not re-derive)

Declarations matched as `val [function] get_<attr> (x: int) : int` — the fallback #27 traced to
`src/pycsl/module6_whyml/expressions.py:11918`. Use sites = occurrences of the symbol minus its
declaration.

| emitted mirror | use sites | distinct attrs declared | that file's `\trusted` markers |
|---|---|---|---|
| **`pure_ast.mlw`** | **144** | 45 | 96 |
| `Module3_Weaver.mlw` | 15 | 10 | 27 |
| `module_collect.mlw` | 5 | 6 | 3 |
| `exec_splice.mlw` | 3 | 7 | 2 |
| `audit_proof.mlw` | 3 | 3 | 12 |
| `Module5_IREmitter.mlw` | 1 | 14 | 30 |
| `pycsl.mlw` | 1 | 1 | 33 |
| **all other 46 mirrors** | **0** | **0** | — |
| TOTAL | **172** | 86 | 203 markers live in these 7 files |

Hottest attrs in `pure_ast.mlw`: `value`:34, `body`:13, `name`:7, `ATOM`:6, `orelse`:6, `target`:5.

### WHAT THIS CHANGES FOR THE LADDER

**Favourable read:** the node ADT is not a sprawling cross-mirror redesign. 84% of its demand is
one file, and that file is the one holding the 54-marker `_Unparser` lever. Build it *for*
`pure_ast` and you have essentially built all of today's demand.

**Unfavourable read, and it is the honest one:** the ADT therefore does NOT unblock a broad slice
of the remaining 491. Nothing outside these 7 files touches the fallback at all. Whoever prices
item 4 next must price it as "buys `pure_ast`'s residue", not "buys the value-model frontier".

### THE CAVEAT THAT MUST TRAVEL WITH THE NUMBER (lesson (ay), below)

**172 is a LOWER BOUND on post-port demand, not the true demand.** A `\trusted` stub has an
elided body, so it reads no attributes and generates no projector uses. The 144 uses in
`pure_ast.mlw` come from its ALREADY-CONVERTED methods; the 51 still-trusted `_Unparser` bodies
contribute zero today and will contribute more once ported. `Module5_IREmitter.mlw` is the visible
proof of the effect from the other side: it declares **14** distinct attr projectors but has only
**1** use site — declaration also happens in spec contexts, so declaration count and use count
measure different things. **Do not quote 172 as "the size of the ADT job." Quote it as "the size
of the demand the currently-converted surface already places on it."**

### THE LESSON #28 BANKS — (ay)

The three prior lessons were about not trusting a record. This one is about not trusting your own
fresh measurement's SCOPE: **a census of an emitted artifact measures the CONVERTED surface only.**
In a campaign whose entire purpose is converting stubs, every artifact-side census is systematically
biased toward zero on exactly the stubs still to be done. State the direction of the bias next to
the number, every time. Corollary: declaration counts and use counts are different instruments —
`Module5_IREmitter` reads 14 vs 1 depending which you pick.

### THE THREE LESSONS FROM THE PRIOR HOUR — carried forward verbatim, they are the campaign's core

- **A boundary that has not been TRIED is not a boundary**, even when the worker naming it had just
  measured the failure it predicts (#25 overturned #24's conditional floor in two minutes).
- **A re-measured number does not re-measure the mechanism** — when a census shrinks a residue,
  trace the SURVIVORS to their source; they are usually the hard core the easy cause was hiding
  (#26 overturned #25). Corollary: read the mirror's own comments near the failing construct —
  #20 had documented this exact failure at `pure_ast.py:5030-5044` and two later workers edited
  within 50 lines without reading it.
- **Trace survivors to the DECLARATION site, not the mirror source** (#27). #26 stopped at "an
  int-modelled projector," which made a string return look like a local choice; one
  `grep 'val get_'` showed it is a generic attr-keyed emitter fallback and the refutation followed
  with zero edits. **A symbol's type is a property of where it is DECLARED — in an emitter, that is
  a line of Python, not a line of the mirror.**

### WHERE THE LADDER STANDS FOR #29 (first worker of the NEXT window)

1. `_Unparser` (54 markers) is **CERTIFIED-BOUNDARY on the value model**. Both halves settled by
   trying: projector `string` return REFUTED with zero edits (#27); `_str_literal_helper` still
   body-blocked (#24). Do NOT re-open without the node ADT.
2. **Backlog item 4 — `pyx_view` node ADT / per-(receiver-node-type, field) projector typing** —
   is the named reopening capability, now SIZED by #28 (above). Its recorded obstacle stands:
   `pure_ast`'s node classes are synthesized at import by `type(name, (base,), body)` from
   `_NODE_SPEC`, so there is no static class surface to read a field type off. Existing in-tree
   precedent for the machinery: the `_optional_union_locals` / `_term_local_vars` carrier-field
   projections immediately ABOVE `expressions.py:11918` already bypass `get_<attr>` when the
   receiver's type is known. That is the shape to extend.
3. `ControlFlowStmtMixin._handle_return_stmt` (item 2) — the one non-constructor model-visible
   false frame left, ~1846 goals / ~45 min.
4. `scratchpad/w3/fix_assigns.py` re-tests of every "effect summary cannot be made exact" wall.
5. **[SUPERSEDED BY #29 — THIS ENTRY IS FALSE; SEE THE #29 SECTION AT THE TOP. The symbol is a
   PROGRAM `val` in the source and in all 53 mirrors; `grep "val function csl_to_ir_op"` returns
   zero hits. It was fixed by #19; this line quotes a stale code comment, not the code.]**
   ~~STILL OPEN, UNFIXED, HONESTLY RECORDED: `val function csl_to_ir_op`~~ — a KNOWN-LIVE
   unsoundness, a pure logic symbol standing for a state-dependent method, inside the logic-level
   `synth_overload_clauses` fold in `preamble.py`. (Note the conflict with the older "#19 CLOSED it"
   line further down this file: the live-unsoundness record is the current one.)

Reproduce #28's census in 20 s, no emission, no edits:
`python3` over `glob('src/self-annotate/**/*.mlw')`, match `^\s*val (?:function )?get_(\w+) \(x: int\) : int`,
count `\bget_<attr>\b` occurrences minus 1 per declaration.

---

# HANDOFF — read this FIRST on relaunch (prepended 2026-09-01, RELAUNCH #27 worker)

## #27 IN ONE LINE: **the projector probe is REFUTED — `get_name` is ONE global abstract symbol
## shared across ALL node types and it is used as a NODE, as a NONE-TEST and as a STRING in the
## SAME emitted file. A `string` return model is not merely ill-typed, it is semantically wrong.**

#27 got the final ~7 minutes and ran exactly the one probe #26 queued. NO edit was made to `src/`
(the probe is read-only: emit `pure_ast.mlw` at `--no-proof --keep-mlw`, 1.8 s, and census the
projector uses). Metric verified fresh at window end: **markers 491 · grep 516 · offset 25 ·
attached 491 · unattached 0 · ledger 3.** Tree clean, no prover process started.

### THE MECHANISM (measured, do not re-derive)

The projectors are NOT per-field emitter symbols. `src/pycsl/module6_whyml/expressions.py:11918`
is a single generic fallback for ANY attribute read off an int-modelled object:

```python
self._add_abstract_op(f"val get_{attr} (x: int) : int")     # or `val function …` in a spec ctx
```

So there is exactly ONE `val get_name (x: int) : int` per emitted file (`pure_ast.mlw:543`),
keyed on the ATTRIBUTE NAME ONLY — never on the receiver's node type. Its 7 uses in
`pure_ast.mlw` are mutually incompatible:

| line | use | required return type |
|---|---|---|
| 4425 | `self_traverse_1 (get_name node)` | **a NODE (int handle)** — `node.name` on this arm is an AST node, and it is fed to `traverse`'s `int` formal |
| 4426 | `if ((get_name node) <> 0)` | **int** — a lowered `is None` test |
| 4428 / 4533 / 4727 / 4586(`get_id`) / 4312(`get_attr`) / 4799,4820(`get_arg`) | `Seq.cons (get_name node) …` | element of the write vararg — string under `*text: str` |
| 4537 | `str_concat 1174530543 (get_name node)` | the #25/#26 clash site |
| 4817 | `if ((get_arg node) = 0)` | **int** — another `is None` test |

`get_arg` shows the same split by itself: two write-element uses and one `= 0` None-test.

**Therefore: no uniform per-attribute return type exists.** Giving `get_name` a `string` return
breaks the traverse feed and both None-tests; leaving it `int` keeps the clash. This is not a
lowering selection and not a signature tweak — it is the ABSENCE OF A TYPED NODE MODEL.

### VERDICT — CERTIFIED-BOUNDARY, and now it is a legitimately EARNED one

Both halves of #26's corrected capability are now settled:

1. **projectors -> `string`: REFUTED (this window, tried, not assumed).**
2. `_str_literal_helper`: still a body-blocked leaf (#24's classification, unchanged).

So the 54-marker `_Unparser` lever's residue is **not 1-2 sites reachable by a cheap move**. Its
reopening capability is now precise and it is the campaign's ALREADY-RECORDED value-model floor:

**REOPENING CAPABILITY: per-(receiver-node-type, field) projector typing — i.e. the node ADT /
record AST model (`pyx_view`, carried-forward item 4).** Only a typed node model can let
`ParamSpec.name : string` and `ClassDef.name : node` coexist. The `_optional_union_locals` /
`_term_local_vars` carrier-field projections right above line 11918 in `expressions.py` are the
EXISTING precedent for exactly this move — they bypass `get_<attr>` when the receiver's type is
known — so the capability is not novel, it is that machinery extended to `_Unparser`'s `node`
formals, which today are bare `(node: int)`.

This converges with the independently-recorded obstacle at item 4: `pure_ast`'s node classes are
SYNTHESIZED AT IMPORT by `type(name, (base,), body)` from `_NODE_SPEC`, so there is no static
class surface for the emitter to read a field type off. That is the same wall, reached from a
second direction — the third such convergence this campaign.

### THE LESSON #27 BANKS

#26's lesson said: when a census shrinks a residue, trace the SURVIVORS to their source. #27 adds
the next step: **trace them to the DECLARATION SITE, not just to the mirror source.** #26 traced
`get_name` back to "an int-modelled node-field projector" and stopped there, which made a string
return model look like a local choice. One `grep 'val get_'` (one command) shows it is a single
generic emitter fallback keyed on the attribute name alone — at which point the refutation is
immediate and needs no edit at all. **A symbol's TYPE is a property of where it is DECLARED, and
in an emitter that is a line of Python, not a line of the mirror.**

Corollary for the metric: the probe cost ~4 minutes and closed a question that had been open for
three windows, without touching `src/`. Read-only emit-and-census is the cheapest instrument in
this campaign — reach for it before any port probe.

### #27's #1 ITEM FOR #28

The `_Unparser` lever is CERTIFIED-BOUNDARY on the value model (node ADT). Do NOT re-open it
without that capability. The live ladder is unchanged below it:
`ControlFlowStmtMixin._handle_return_stmt` (item 2), then `scratchpad/w3/fix_assigns.py` re-tests
of "effect summary cannot be made exact" walls (item 3). [SUPERSEDED BY #29: the following
sentence is FALSE — `csl_to_ir_op` is a program `val`, closed by #19.] ~~`val function csl_to_ir_op` remains a
KNOWN-LIVE unsoundness in `synth_overload_clauses` (preamble.py) — still open, still unfixed.

---

# HANDOFF — read this FIRST on relaunch (prepended 2026-09-01, RELAUNCH #26 worker)

## #26 IN ONE LINE: **#25's 4-site "cost-shaped lowering selection" IS NOT ONE. Three of the four
## clash sites are INT-SOURCED, so `str_concat_op` cannot take them — the residue is a VALUE-MODEL
## capability (string-model the node-field projectors / `_str_literal_helper` returns), not a gate.**

#26 got the final ~10 minutes of the 96h window. Per the supervisor it started no prover run and
attempted no port. It spent the sliver locating the ROOT CAUSE of #25's four sites, and the answer
CORRECTS #25's reopening capability in the unfavourable direction (the first time in nine windows
that a re-pricing went the wrong way — record it as such, it is the counter-example to the streak).

### WHAT #25 CLAIMED, AND WHERE IT IS WRONG

#25 wrote: "under a `string` vararg element type, a computed string argument must lower through
`str_concat_op`/`+` rather than the hash-int `str_concat`; both symbols already exist; this is a
lowering SELECTION driven by `_vararg_elem_type`, COST-shaped." **The selection premise is false.**

`str_concat_op` has signature `(a: string) (b: string) : string`. Selecting it only helps if the
OPERANDS are Why3 `string`s. #26 read the four sites back to their mirror sources:

| emitted line | mirror source | operands |
|---|---|---|
| 4113 | `pure_ast.py:5087` `self.write(f"{quote_type}{string}{quote_type}")` | `quote_type`, `string` are **ints** — they are unpacked from `self._str_literal_helper(...)`, **which is still a `\trusted` stub returning ints** |
| 4120 | `_write_constant` inf/nan `repr` chain | `repr_conv`/`replace_3` results, int-modelled |
| 4348 | `(str_concat (str_concat 1376817993 !operator) 1376817993)` | `!operator` is an **int-typed local**; only the two literals are string-able |
| 4537 | `(str_concat 1174530543 (get_name node))` | `get_name` is one of the **int-modelled node-field projectors** |

So exactly ONE of the four (the literal halves of 4348) is a selection question. The other three are
int VALUES. Routing them through `str_concat_op` produces the *mirror-image* type error.

### THIS IS ALREADY RECORDED IN THE TREE, BY #20, AND IT WAS READ PAST TWICE

`src/self-annotate/src/frontend/pure_ast.py:5030-5044` (a comment #20 left in the mirror) states it
outright, and names the same first failure #25 rediscovered:

> "The remaining 16 come from INT-MODELLED sources — the `get_name` / `get_id` / `get_attr` /
> `get_arg` node-field projectors, `str_concat` over int-typed locals, and int-typed parameters
> (`extra`, `start`, `py_end`, `!operator`) … **L3-tc FAILS on the first one
> (`_write_str_avoiding_backslashes`, whose `quote_type`/`string` locals are ints because
> `_str_literal_helper` is still a stub returning ints)**. There is no int->string direction
> available: `str_hash_op` goes the other way and is not invertible, so no coercion can bridge it
> without a fiction."

#25 measured the residue as 4 sites (down from #20's 16 — that part of the re-pricing STANDS and is
a genuine gain: `seq string` really does clear 54 of 58) but attributed those 4 to the wrong
mechanism. **The count was re-measured; the CAUSE was not.**

### THE CORRECTED REOPENING CAPABILITY (for #27)

Not a lowering selection. It is: **the int-modelled node-field projectors (`get_name`/`get_id`/
`get_attr`/`get_arg`) and the tuple return of the still-`\trusted` `_str_literal_helper` must
produce Why3 `string`s.** Two independent sub-moves, either of which shrinks the 4:

1. **`_str_literal_helper` is one of #24's body-blocked leaves** (nested `def`, `map`, `lambda`,
   list comps, tuple return, `repr`). Porting it is what makes 4113 a string site. Body-blocked
   still, so this is NOT the cheap half.
2. **`get_name` & friends** are emitter-side projectors, not mirror bodies. Whether they can carry a
   `string` return model is UNMEASURED and is the ~2-minute probe #27 should open with. If they can,
   4537 (and the `!operator` half of 4348) go string and the residue may reach 1-2 sites.

**Per the standing lesson, #26 did NOT try either and therefore files NEITHER as a boundary.** What
is established here is only that the WORK IS NOT the work #25 named. `*text: str` still cannot land
until the residue is 0, because all 58 sites share the one `write` formal.

### THE LESSON — the streak's counter-example, and it is the more useful half

Eight windows re-priced a recorded boundary FAVOURABLY. #26 is the ninth and it went the other way:
**a re-measured NUMBER does not re-measure the MECHANISM.** #25 correctly recensused 16 -> 4 and then
inferred the cause of the 4 from the emitted symbol name (`str_concat` vs `str_concat_op`) instead of
from the operands' provenance. One `grep` back to the mirror source — 60 seconds — would have shown
that three of the four operands are values, not spellings. **When a census shrinks a residue, trace
the SURVIVORS to their source; do not assume they are small instances of the same cause as the ones
that went away.** They are usually the hard core that the easy cause was hiding.

Corollary, and it stings: **the answer was in a comment in the file under edit.** #20 wrote it, #24
and #25 both edited within 50 lines of it. Before pricing a blocker in a mirror, read the mirror's
own comments near the failing construct.

### #26 hygiene

No edit was made to `src/` at all — this window bought a diagnosis, not a build, so there was nothing
to revert. Metric verified fresh at window end: **markers 491 · grep 516 · offset 25 · attached 491 ·
unattached 0 · ledger 3.** No prover process started, none left running. Tracked `src/` clean.

### #27's #1 ITEM

Probe (2 min) whether the node-field projectors `get_name`/`get_id`/`get_attr`/`get_arg` can carry a
`string` return model. That is the cheap half of the corrected capability and it is the gate on the
54-marker `_Unparser` lever. If it clears, re-census the residue; if it refutes, the lever's residue
is `_str_literal_helper` alone and the question becomes whether that body-blocked leaf is portable —
which is the value-model floor, and THEN it may be recorded as one.

---

# HANDOFF — read this FIRST on relaunch (prepended 2026-09-01, RELAUNCH #25 worker)

## #25 IN ONE LINE: **`seq string` CLEARS #24's blocker. The 54-marker `_Unparser` lever is LIVE
## again — it is NOT a value-model boundary. Residue is FOUR int-model call sites, not fifty-eight.**

#25 got the final ~13 minutes and ran exactly the probe #24 queued: exercise degree of freedom 1
(`vararg_elem_type` as a PER-FUNCTION choice) on `_Unparser.write`, then re-run #24's port probe.

### HOW YOU SET IT (the mechanism, measured — do not re-derive)

`vararg_elem_type` is NOT a knob you pass; it is selected in
`src/pycsl/frontend/Module5_IREmitter.py:4979-5000` **from the vararg's own annotation**:
`*text: str` -> `"string"`, unannotated `*text` -> `"int"` (ladder 1a), star-forwarded -> dropped.
So the per-function choice is made **in the mirror source**, one annotation:

```python
def write(self, *text: str):      # was: def write(self, *text):
    self._source.extend(text)
```

`fill` needs nothing — its `text=''` is a plain default arg, not a vararg.

### RESULT — L3-tc gets MUCH further, and the two ported bodies are CORRECT

With `*text: str`, `let _unparser__write (self: _unparser) (text: seq string)` (line 4851), and
#24's two ported leaves lower exactly as wanted:

```
let _unparser__visit_ParamSpec   … = self_write_1 (Seq.cons ("**" + (get_name node)) (Seq.empty: seq string))
let _unparser__visit_TypeVarTuple… = self_write_1 (Seq.cons ("*"  + (get_name node)) (Seq.empty: seq string))
```

**A COMPUTED STRING IS NOW A FIRST-CLASS ELEMENT.** #24's decisive failure ("computed string cannot
be an element of `seq int`", old line 4605) is GONE. All 58 write/fill call sites re-materialize as
`seq string`, and the literals become REAL Why3 strings (`" in "`, `":"`, `"\n"`) instead of
`str_hash_op` ints — the fidelity gain #20 predicted.

### THE NEW BLOCKER IS SMALL AND IT IS IN THE *ALREADY-CONVERTED* BODIES, NOT THE PORT

L3-tc now fails at `pure_ast.mlw:4113`:

```
self_write_1 (Seq.cons (str_concat (str_concat !quote_type !string) !quote_type) (Seq.empty: seq string))
  This expression has type seq.Seq.seq string, but is expected to have type seq.Seq.seq int
```

because `val str_concat (x: int) (y: int) : int` (line 628) is the **hash-int** concat, while
`str_concat_op (a: string) (b: string) : string` (line 629) is the string one. The element is an
int, so `Seq.cons` fixes the sequence to `seq int` and the annotated `seq string` tail clashes.

**#25 CENSUSED THE WHOLE SURFACE (python over the emitted .mlw, not grep):**

| write/fill argument sites in `pure_ast.mlw` | **58** |
|---|---|
| already fine under `seq string` | **54** |
| int-model, would clash | **4** |

The four, with line numbers in the `seq string` emission:

```
4113  (str_concat (str_concat !quote_type !string) !quote_type)          _write_str_avoiding_backslashes
4120  (replace_3 (replace_3 (repr_conv value) …) … (str_concat …))       _write_constant (inf/nan repr)
4348  (str_concat (str_concat 1376817993 !operator) 1376817993)          visit_BinOp-family
4537  (str_concat 1174530543 (get_name node))                            a visit_* name write
```

### VERDICT — RE-PRICE, DO NOT RECORD A BOUNDARY

#24 asked for a two-way answer and this is the favourable one. **The 54-marker `_Unparser` lever is
NOT a value-model CERTIFIED-BOUNDARY.** It is gated on a bounded, named, 4-site capability:

**REOPENING CAPABILITY (precise, and it is a COST item, not a correctness one): under a `string`
vararg element type, a computed string argument must lower through the STRING concat
(`str_concat_op`/`+`) rather than the hash-int `str_concat`.** Both symbols already exist in the
preamble — this is a lowering *selection* in `module6_whyml/expressions.py`, driven by the same
`_vararg_elem_type` that already gates `seq_mem_str` (expressions.py:1088) and the abstract
self-call param typing (expressions.py:5675). It is the identical gating idiom, one call site over.

**#1 ITEM FOR THE NEXT WINDOW:** make those 4 sites string-model under `_vararg_elem_type ==
"string"`, land `*text: str` on the mirror's `write`, re-run L3-tc, then port the leaf batch —
which #24 showed is at most ~5 bodies (`fill`, `visit_TypeVarTuple`, `visit_ParamSpec`,
`visit_alias`, `visit_MatchStar`), all of them computed-string writes and hence all of them
unblocked by exactly this change. The other 8 of #24's 13 stay body-blocked (dict / generator /
higher-order / `super().visit`) — that finding stands unchanged.

### THE LESSON, NOW SEVEN TIMES IN SIX HOURS

**#24 wrote a conditional record ("if it does not clear, this is a value-model boundary"). The probe
cleared it. A boundary that has not been TRIED is not a boundary even when the worker who named it
had just measured the failure it predicts.** #24's measurement was correct *for `seq int`*; the axis
it did not measure was the element type it had itself identified as free. Two minutes bought back an
11.0%-of-campaign lever that was one sentence from being filed as a floor.

Corollary for the census habit: **census the emitted `.mlw`, not the plan.** "Computed writes break"
sounded like it covered most of 58 sites. It covered 4.

### #25 hygiene

Probe FULLY REVERTED (mirror byte-restored, 134 markers in file). Metric re-verified after revert:
**markers 491 · grep 516 · offset 25 · attached 491 · unattached 0 · ledger 3.** `src/` clean.
No prover process started, none left running. Nothing banked as a conversion — this window bought a
re-pricing, which is what the supervisor asked for.

---

# HANDOFF — read this FIRST on relaunch (prepended 2026-09-01, RELAUNCH #24 worker)

## #24 IN ONE LINE: **the 13-leaf batch is NOT 13 — the `seq int` element type of ladder 1a blocks
## every body that writes a COMPUTED string, and only ~3 of the 13 leaves are body-portable at all.**

#24 got the last ~16 minutes of the 96h window. Per the supervisor's instruction it did NOT start the
port batch; it ran ONE cheap probe against the port plan #23 wrote an hour earlier. The probe
corrected the plan again — the fifth consecutive window in which a record's claim failed on first
contact.

### FINDING 1 — LEAF-NESS IS A CALL-GRAPH PROPERTY. PORTABILITY NEEDS A SECOND, INDEPENDENT GATE.

#23's "13 leaves are portable now" was measured purely on the call graph (calls no still-trusted
sibling). #24 read the 13 LIVE BODIES (`src/pycsl/frontend/pure_ast.py`, `ast` census, 1 min) and
classified what each body actually needs. **Most of them are blocked by a body feature that has
nothing to do with the call graph:**

| leaf | live body needs | portable? |
|---|---|---|
| `set_precedence` | `self._precedences[node] = precedence` — **dict store keyed by an AST node** | NO — the object-identity / value-model floor |
| `__init__` | `{}` / `[]` dict+list field init | NO — dict model |
| `get_type_comment` | `dict.get` + dynamic `getattr` + f-string | NO |
| `interleave` | `iter()`/`next()`/`StopIteration` + **higher-order callable formals `f`, `inter`** | NO |
| `buffered` | `@contextmanager` with `yield` — a generator | NO |
| `delimit_if` | **returns a context-manager object** (`self.delimit(...)` / `_nullcontext()`) | NO |
| `traverse` | `isinstance(node, list)` + recursion + **`super().visit(node)`** | NO |
| `_str_literal_helper` | nested `def`, `map`, `lambda`, list comps, tuple return, `repr` | NO |
| `fill` | `self.write("    " * self._indent + text)` — computed string | see FINDING 2 |
| `visit_TypeVarTuple` | `self.write("*" + node.name)` | see FINDING 2 |
| `visit_ParamSpec` | `self.write("**" + node.name)` | see FINDING 2 |
| `visit_alias` | `self.write(node.name)` + `" as " + node.asname` | see FINDING 2 |
| `visit_MatchStar` | f-string `f"*{name}"` + None-default | see FINDING 2 |

**So the top hubs `traverse`, `interleave`, `set_precedence` — the three that #23 counted on to
unblock 23+18+8 dependents — are ALL body-blocked.** The DAG analysis is correct and still useful,
but it is a NECESSARY condition for porting, not a sufficient one. Batch 1 is at most the 5 rows in
the bottom group, and FINDING 2 cuts that further.

### FINDING 2 — THE `seq int` ELEMENT TYPE OF LADDER 1a IS A HARD BLOCKER FOR COMPUTED WRITES

#24 ported the two smallest candidate leaves (`visit_TypeVarTuple`, `visit_ParamSpec`, 1 line each)
into the mirror and emitted (`--no-proof --keep-mlw`, 134 -> 132 markers). **L3-tc FAILS:**

```
let _unparser__visit_ParamSpec (self: _unparser) (node: int) : unit =
  let _ = (self_write_1 (Seq.cons ("**" + (get_name node)) (Seq.empty: seq int))) in ()
File "…/pure_ast.mlw", line 4605: This expression has type string, but is expected to have type int
```

`write`'s formal is `let _unparser__write (self: _unparser) (text: seq int)` (line 4851). A **string
LITERAL** write lowers fine — it becomes a `str_hash_op` int (`self_fill_1 2128406761` in an
already-converted caller right below the failure). A **COMPUTED** string (`"**" + node.name`, `"    "
* self._indent + text`, an f-string) is a genuine Why3 `string` and cannot be an element of
`seq int`. The failure is again LOUD (a type error at L3-tc), never a silent mis-lowering.

**This is the decisive fact for the whole 54-marker lever.** Ladder 1a's uniform `seq int` was gated
on all four planes against the mirror AS IT STANDS — where every `_Unparser` body is an empty stub
and every live write call site passes a literal. The moment real bodies are ported, the overwhelming
majority of `_Unparser` writes are computed strings. **1a is proved, and 1a is still not the element
type the port needs.**

### CONSEQUENCE — THE #1 ITEM FOR THE NEXT WINDOW HAS CHANGED

Do **NOT** open the next window by porting leaves. Open it by exercising **degree of freedom 1,
which has now been sitting unused for four windows**: `vararg_elem_type` makes the element type a
PER-FUNCTION choice (#21's infrastructure carries it; #20 measured `seq string` turning 40 of 56
write sites into real Why3 string literals). Set `_Unparser.write` (and `fill`) to `seq string` and
re-run the probe above. That is the gate on batch 1, and it is a ~2-minute probe, not a scope.
If `seq string` clears it, re-price the batch; if it does not, the 54-marker lever is a
CERTIFIED-BOUNDARY on the value model and should be recorded as one.

The 3 starred-blocked bodies (`visit_Compare`, `visit_comprehension`, `visit_MatchOr`) are now moot
for batch 1 — their target `set_precedence` is body-blocked on the dict model anyway.

### #24 hygiene

Probe fully REVERTED; mirror byte-restored (134 markers, re-confirmed). Metric UNCHANGED:
**markers 491 · grep 516 · offset 25 · ledger 3.** No prover process left running. Tree clean.
Nothing was banked as an increment — this window bought a plan correction, which is what the
supervisor asked for.

### The method note #24 paid for

**A DEPENDENCY ANALYSIS IS A CLAIM ABOUT ONE AXIS ONLY.** #23's DAG was measured correctly and
answers "may I port X before Y?" It silently got read as "X is portable." Whenever a plan is built
on a structural census, ask which axis it measured and which axes it did NOT — then spend two
minutes reading the actual artifacts along the unmeasured axis. Here the unmeasured axis (what the
body's Python features require of the value model) knocked out 8 of 13 outright and the element-type
axis knocked out most of the rest.

---

## #23 IN ONE LINE: the vacuity plane on `pure_ast.py` is CLOSED, GREEN. Ladder 1a is fully paid for.

#23 got a ~20-minute window and the supervisor named exactly one job: finish the per-goal
NON-VACUITY gate that #22 had to kill at window end. It is done, and it did not need the slow
per-goal `why3 prove -g` loop at all — `bin/check-emitted-vacuity.py --emit` is the same plane
and it runs in well under a minute:

```
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
export TMPDIR=/home/fabrice/git/pycsl/scratchpad
python3 bin/check-emitted-vacuity.py --emit      # EXIT 0
```

**VERDICT: `[+] emitted-vacuity: no NEW erasure (8 known param-erasures gated; 0 input-blind).`**
Evidence: `scratchpad/r23/vacuity.log`.

Read the 8 gated rows carefully, because two of them are in this very file and they are NOT a
finding against 1a:

- `pure_ast.mlw::_parser___dict_rest` (erases `t`) and `pure_ast.mlw::_parser___sequence_pattern`
  (erases `t`) are **PRE-EXISTING, already in `KNOWN_ERASURES`, banked in commit `87f9cdb9` in an
  earlier window.** They sit in `_Parser`, not `_Unparser`. `bin/check-emitted-vacuity.py` is
  byte-unmodified in this tree — #23 added no entry to the ledger to make the gate pass.
- The other 6 are the long-standing `core_ir_semantic` / `Module3_Weaver` / `expr_ghost_spec_ops`
  / `statements` rows, unchanged.

### LADDER ITEM 1a IS NOW GATED ON ALL FOUR PLANES — nothing is left owing on it

| plane | verdict | who |
|---|---|---|
| fidelity (`check-self-annotate-sync.sh` + mirror-check) | green (2-DIVERGED baseline) | #21, inherited — tracked tree unchanged since `44150508` |
| whole-file proof | **2857 / 2857 Valid, 0 non-Valid** | #22, `scratchpad/r22/pure_ast_proof.log` |
| byte-inertness | 3/3 | #21, inherited |
| **non-vacuity** | **0 NEW erasures, 0 input-blind** | **#23, `scratchpad/r23/vacuity.log`** |

Plus: **`src/self-annotate/src/frontend/pure_ast.mlw` declares ZERO `axiom`s** (re-measured by #23
on the freshly emitted file). Ledger stays 3. `#22`'s caveat — "the vacuity plane is UNFINISHED,
not failed" — is now RESOLVED as FINISHED and GREEN. Do not re-run it as a precondition for step 3.

Metric re-verified fresh by #23, UNCHANGED by this window:
**markers 491 · grep-substring 516 · offset 25 · attached 491 · unattached 0 · ledger 3.**

### The instrument note #23 paid for

**Instrument fact 3 says `check-emitted-vacuity.py` is a false green without `--emit`. The
converse is the useful half: WITH `--emit` it is CHEAP.** It re-emits every mirror at
`-P 7 --no-proof --no-typecheck --keep-mlw` and finishes in under a minute — i.e. the whole
vacuity plane for the entire mirror surface costs less than one `--fun` probe. #22 spent its
window's tail inside pycsl.py's per-goal `why3 prove -g` vacuity loop, which was ~200 goals in
after many minutes. **Those are not two speeds of the same check to choose between on time
budget; the standalone probe is the one to reach for, and it covers all 52 mirrors, not one file.**
Generalization worth carrying: when a gate is embedded in a slow driver AND exists as a standalone
`bin/` probe, price the standalone one before assuming the plane is expensive.

---


## #23's SECOND FINDING — **PORT ORDER, not body length, is what gates step 3**

With the vacuity plane closed, #23 spent its remaining minutes on ONE cheap probe (2 min, fully
reverted, tree clean) rather than starting the port: it ported the single SHORTEST live body,
`_Unparser.require_parens` (1 line), into the mirror and emitted with `--no-proof --keep-mlw`.

**It FAILED L3-tc — and not for the starred reason.**

```
    (self_delimit_if_3 747334986 1226926668 ((_unparser__get_precedence self node) > precedence))
File "…/pure_ast.mlw", line 4242: This expression has type bool, but is expected to have type int
```

because the *callee is still a stub*:

```
val _unparser__delimit_if (self: _unparser) (start: int) (py_end: int) (condition: int) : unit
```

**A `\trusted` stub has a `pass` body, so its formals get the default `int` type. Port a CALLER
before its CALLEE and any non-int actual (here a `bool` comparison) is a hard type error.** As with
the starred residue, the failure is LOUD, never a silent mis-lowering — but it means the port is
not a flat batch.

### THE DEPENDENCY STRUCTURE (measured, `ast`, 30 s)

Of the 51 trusted `_Unparser` methods, counting `self.X(...)` calls in the LIVE body where `X` is
also still `\trusted`:

- **13 are LEAVES** — they call no still-trusted sibling: `__init__`, `_str_literal_helper`,
  `buffered`, `delimit_if`, `fill`, `get_type_comment`, `interleave`, `set_precedence`, `traverse`,
  `visit_MatchStar`, `visit_ParamSpec`, `visit_TypeVarTuple`, `visit_alias`.
- **38 depend on at least one** still-trusted sibling.
- The hubs are `traverse` (23 dependents), `interleave` (18), `fill` (14), `set_precedence` (8),
  `get_type_comment` (4), `require_parens` (3), `delimit_if` (2). **All the top hubs are themselves
  LEAVES**, so the 13-leaf batch is both portable now and unblocks nearly all of the 38.

**PORT ORDER FOR THE NEXT WINDOW: the 13 leaves first, then re-emit and take the 38 in topological
order.** This SUPERSEDES #22's "start with the 23 shortest bodies" — `require_parens` is the
shortest body in the class and it is *not* portable first. **Shortest != portable-first.** Note the
happy accident: `set_precedence` is a leaf, so it ports in batch 1; the 3 starred-blocked bodies
(`visit_Compare`, `visit_comprehension`, `visit_MatchOr`) are its CALLERS and stay deferred.

---

## WHAT #22 ESTABLISHED (all still valid; its vacuity caveat is now closed by #23 above)

A **~55-minute** window against the same deadline (`.driver-deadline` = 1788251064). The window was
too short to start a build, and the supervisor named exactly one job: **run a prover on ladder item
1a**, which #21 built and gated only to `L3-tc`. Lesson (hh) — *type-check success is not a
conversion criterion* — is the whole reason this had to happen before anything was banked on 1a.

## THE JOB: whole-file proof of `src/self-annotate/src/frontend/pure_ast.py`

Launched at T-53min, detached (`nohup`, so it survives a turn ending — instrument fact 8 is about
watchers, not about the proof process itself):

```
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
export TMPDIR=/home/fabrice/git/pycsl/scratchpad
PYTHONHASHSEED=0 python3 -u src/pycsl/pycsl.py \
  src/self-annotate/src/frontend/pure_ast.py \
  --import-path src/pycsl --provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,' \
  > scratchpad/r22/pure_ast_proof.log 2>&1 &
```

## PROOF VERDICT — **GREEN. 2857 / 2857 Valid, 0 non-Valid.**

**Ladder item 1a STANDS.** The unannotated-vararg -> `seq int` pyval lowering is not merely
type-checking; the whole of `pure_ast.py` proves under it.

| | |
|---|---|
| proof obligations | **2857** |
| `Valid` | **2857** |
| `Unknown` / `Timeout` / `Failure` / `Invalid` | **0** |
| provers | Alt-Ergo 2.6.3, Z3 4.13.3 (`--timelimit 5`, `-a split_vc`) |
| wall clock to full flush | ~13 min (the proof engine phase) |

Evidence: `scratchpad/r22/pure_ast_proof.log` (2857 `Prover result is: Valid` lines, zero
non-Valid; tally it with a python heredoc, NOT `grep` — instrument fact 14).

**This retires lesson (hh)'s open exposure on 1a.** #21 landed 1a on `L3-tc` alone and the campaign's
own rule is that a type-check is not a conversion criterion. It has now been paid: the criterion was
applied, and 1a passed it. Nothing built on top of 1a is resting on an unproved emitter change.

**Caveat, stated precisely so nobody over-reads the green.** The run had, at window end, moved past
the proof engine into pycsl.py's **per-goal non-vacuity phase** (one `why3 prove -g` per goal against
`scratchpad/.pycsl_vac_*.mlw`; it was ~200 goals in and still going). That phase is a SEPARATE gate
from the proof and it had NOT finished. **The proof plane is green; the vacuity plane is UNFINISHED,
not failed.** First action next window: re-run and let it finish, or run
`bin/check-emitted-vacuity.py --emit` (remember: a false green without `--emit`, instrument fact 3).

**One more fact worth having: the emitted `pure_ast.mlw` declares ZERO `axiom`s.** So those 2857
goals are discharged without the module contributing anything to the ledger. The campaign ledger
stays at 3 and this file adds nothing to it.

**The other two L-planes are INHERITED, not re-run.** The tracked tree has not changed since #21
gated them at `44150508` (this window's commits touch `getting-better/` only), so #21's fidelity
(2-DIVERGED baseline) and byte-inertness (3/3) results carry over unchanged. #22 re-verified the
metric itself fresh: **markers 491 · grep 516 · offset 25 · unattached 0 · ledger 3.**


## What #22 VERIFIED about 1a independently (all fresh, from the emitted `.mlw`)

`--no-proof --keep-mlw` on `pure_ast.py` (1.8 s, instrument fact 7) leaves
`src/self-annotate/src/frontend/pure_ast.mlw` on disk (gitignored, so it never dirties the tree).
In it, **the 1a capability is really present** — this is not a no-op emission:

- `let _unparser__write (self: _unparser) (text: seq int) : unit` at line 4847 — a **real
  parameterized `let`**, not a `val`, and not a zero-parameter facade.
- `val _unparser__set_precedence (self: _unparser) (precedence: int) (nodes: seq int) : unit`
  at line 4241 — the vararg is a formal here too.
- **58 `write` call sites**, every one materialized as `Seq.cons … (Seq.empty: seq int)`
  (266 `Seq.cons` occurrences file-wide). Element values are the same `str_hash_op` ints the
  drop-behaviour used: `self_write_1 (Seq.cons 260070937 (Seq.empty: seq int))`.
- `L1 ✓ L2 ✓ L3-tc ✓` reproduced independently of #21.

## THE RECORDED PRICE OF THE NEXT LEVER WAS WRONG (again) — and it is BIGGER, not smaller

Applying #21's own lesson (*a recorded price is a claim too*) to the price #21 itself recorded:

| record | recorded | **measured by #22** |
|---|---|---|
| markers in `pure_ast.py` | 96 | **95** |
| `_Unparser` family lever | 51 | **54 markers** (51 of them attach to `_Unparser` methods; 1 sits behind an `@_contextmanager` decorator; the rest are nested/decorated defs) |

Per-class marker census of `pure_ast.py` (95 total):
`_Unparser` **54** · `_Parser` 24 · `AST` 5 · `Comment` 3 · `NodeVisitor` 3 · `_Tok` 2 ·
`_ABC`/`Ellipsis`/`NodeTransformer`/`_Precedence` 1 each.

So `_Unparser` is **54 of 491 = 11.0%** of the whole campaign's remaining metric in ONE class in ONE
file. It is by a wide margin the largest single lever left, and the recorded figure understated it.

**Also measured, and it matters for how step 3 is planned:** all 51 trusted `_Unparser` methods are
`\trusted` *stubs with elided bodies* — an `ast.walk` over the mirror finds **zero** `self.write`
calls and **zero** starred forwarding inside them, because there is nothing inside them. The 58
`Seq.cons` call sites above are in the ALREADY-CONVERTED methods. Step 3 is therefore a *porting*
job (bring each real body into the mirror), not a *repair* job, and the `write` signature it must
target is the one now verified above.

## THE #1 ITEM FOR THE NEXT WINDOW

**Un-trust the `_Unparser.write` family — 54 of the 491 markers.** It is the campaign's largest
remaining single lever and, as of this window, the emitter capability under it is proved-or-refuted
(see the verdict) rather than merely type-checked.

Two live degrees of freedom, both opened in the last two windows and **neither one used yet**:

1. **`vararg_elem_type` makes the element type a PER-FUNCTION choice.** #20 measured that
   `seq string` turns **40 of 56** write call sites into real Why3 string literals (a fidelity gain)
   while 16 int-sourced sites are unbridgeable; #21's `seq int` is uniform and annotation-free.
   These were believed mutually exclusive. They are not, since #21's infrastructure carries the
   element type per function. Worth ONE probe, not a scope.
2. **STARRED-ARGUMENT FORWARDING (`g(*args)`) is deliberately still gated out** (Module5 `ast.walk`
   for `Starred(Name(vararg))`; a starred arg lowers to its bare inner value at
   `expressions._expr_to_whyml` `"Starred"` ~14613). It keeps the historical drop behaviour.
   Reopening capability: positional re-binding of an unknown-length sequence against the callee's
   arity. **It affects `_new` / `Ellipsis.__new__` / `Constant.__init__` ONLY — `_Unparser.write`
   and `set_precedence` are NOT affected, so the 54-marker lever is unblocked by it.**
   Per lesson (#20): the first move against this capability is to TRY it, not to scope it.

## STEP 3 IS FULLY SCOPED BY #22 — it is 503 lines of PORTING, and 48/51 are unblocked

`src/pycsl/frontend/pure_ast.py` is the live counterpart of the mirror (note the path: it is under
`frontend/`, NOT `src/pycsl/pure_ast.py`). Measured by AST diff against it:

- **All 51** trusted `_Unparser` stubs have a live body available. **Zero missing.**
- **Total live body lines to port: 503.** Size distribution: **23 bodies are <=5 lines**,
  19 are 6-15, only 9 are 16+. Largest five: `visit_arguments` 50, `_str_literal_helper` 38,
  `visit_JoinedStr` 32, `visit_ClassDef` 23, `visit_MatchClass` 22. Smallest are 2-3 lines
  (`require_parens`, `visit_ParamSpec`, `visit_TypeVarTuple`, `fill`, `set_precedence`,
  `visit_Delete`, `visit_Global`, `visit_Import`).
- **Start with the 23 <=5-line bodies.** They are a natural first batch and, at ~0.45 markers per
  line ported, the cheapest markers left anywhere in the campaign.

### THE STARRED BLOCKER IS REAL FOR THIS FAMILY — but it is NOT the shape the record names

The record (and `Module5_IREmitter.py:4986-4999`) says star-forwarding "affects `_new` /
`Ellipsis.__new__` / `Constant.__init__` only" and that "`_Unparser.write` and `set_precedence` are
NOT affected". **The first half is right about the GATE; the second half is wrong about the FAMILY.**

Read the gate: it walks the *defining* function and drops the vararg only when that function's OWN
vararg NAME is star-forwarded (`isinstance(_n.value, ast.Name) and _n.value.id == _va0.arg`).
`set_precedence`'s own 3-line body forwards nothing, so it correctly keeps its `seq int` formal —
confirmed in the `.mlw`. **But three of the 51 live bodies to be ported are CALLERS that pass a
starred actual INTO that vararg formal:**

```
visit_comprehension : self.set_precedence(_Precedence.TEST.next(), node.iter, *node.ifs)
visit_Compare       : self.set_precedence(_Precedence.CMP.next(),  node.left, *node.comparators)
visit_MatchOr       : self.set_precedence(_Precedence.BOR.next(),  *node.patterns)
```

This is a **different capability** from the recorded one: not `g(*args)` forwarding of an enclosing
vararg, but **MIXED positional-plus-starred packing at a call site into a `seq int` formal**
(`f(a, *b)` — concat a materialized prefix onto an existing sequence). Nothing in the tree gates it
today, so its behaviour on port is UNKNOWN and must be probed, not assumed. Two of the three even
have a non-starred positional *before* the star, which is the hard sub-case.

**#22 RAN THAT PROBE.** Isolated it in a 15-line standalone file (`scratchpad/r22/star_probe.py`,
a `sink(self, p, *nodes)` plus a star-only caller and a mixed caller) rather than editing the mirror
— zero risk, ~2 s. **The result is unambiguous, and it is the same for BOTH shapes:**

```
let p__caller_star_only (self: p) (xs: array int) : unit =
  let _ = (self_sink_2 1 (Seq.cons xs (Seq.empty: seq int))) in ()
let p__caller_mixed (self: p) (a: int) (xs: array int) : unit =
  let _ = (self_sink_2 1 (Seq.cons a (Seq.cons xs (Seq.empty: seq int)))) in ()
```

A `Starred` actual in a vararg position is packed **as a single ELEMENT** — `Seq.cons xs …` — so the
whole sequence lands where one element belongs. It does not splat. `L3-tc ✗`:

> `This expression has type seq.Seq.seq int, but is expected to have type seq.Seq.seq (array.Array.array int @rho)`

**Two things follow, and the second is the important one:**

1. The 3 bodies are genuinely blocked. Star-only (`visit_MatchOr`) is blocked exactly as hard as
   mixed (`visit_Compare`, `visit_comprehension`) — the prefix is not the hard part; the splat is.
2. **The failure is LOUD, not silent.** It is a Why3 TYPE error at L3-tc, not a mis-typed-but-
   accepted lowering. So this residue can never quietly produce a wrong proof — porting one of the
   3 by accident fails the gate immediately. That makes "port the 48 now" safe to do without first
   solving the 3.

**PRECISE REOPENING CAPABILITY (supersedes the vaguer `g(*args)` wording):** at a call site, a
`Starred` actual in a vararg position must lower to a sequence **CONCATENATION** of its inner value
(coerced to `seq elem`) onto the materialized prefix — `Seq.(++) (Seq.cons a Seq.empty) (to_seq xs)`
— instead of today's `Seq.cons xs`. That is a call-site packing change in the same materialization
code #21 added, not the "positional re-binding against the callee's arity" the record describes;
re-binding is only needed when a starred actual feeds NON-vararg formals, which is the
`_new`/`__new__`/`Constant.__init__` case, not this one. **These are two different capabilities and
the record conflates them.**

**Consequence for the plan: port the 48 unblocked bodies now — do not let the 3 hold up 94% of the
lever.** The 3 are a bounded, well-typed follow-on.

## Then, in this order (carried forward, still valid)

2. **`ControlFlowStmtMixin._handle_return_stmt`** — the ONE non-constructor model-visible false
   frame left (18 fields via-callee). `module6_whyml/stmt_control_flow` is 1846 goals, ~45 min.
3. **`scratchpad/w3/fix_assigns.py` IS THE REUSABLE TOOL.** It converges `#@ assigns` / `#@ raises`
   / `#@ \diverges` against Why3's own error text. Point its `MIR` constant at another mirror.
   **Every wall whose recorded reason is "the effect summary cannot be made exact" should be
   re-tested with it FIRST.**
4. **The `pyx_view` ADT redesign / record AST model** remains the soundness floor under the
   object-identity question. Obstacle: `pure_ast`'s node classes are SYNTHESIZED AT IMPORT by
   `type(name, (base,), body)` from `_NODE_SPEC`.
5. `val function csl_to_ir_op` is **CLOSED** (relaunch #19). Do not re-open it.

## Recorded boundaries carried forward — do not re-grind without the named capability

- `_csl_to_ir` is **BROKEN**; strike it from any ladder that still lists it.
- **The attribute-store third horn** works and is axiom-free; blocked on OBJECT-IDENTITY INJECTIVITY.
- **`crosscheck_ir.pairwise`** — spiked and working, demand NIL.
- **The shadowed TCFAIL residue — [PYVAL / ARRAY-INT MODEL SPLIT]** (33 sites / 13 methods).
  Same disease as the `_Unparser` finding, one type-family over.
- `_fin` / `_max_end` / `_fin_block` — [ERASURE-LEDGER]; `node(self, name, start_tok, **kw)` —
  [MODEL]; `_slice`; **`Module2_Parser`'s contract-expression cluster** (TERMINUS);
  `_decode_escapes` / `_decode_string`; `identifiers.whyml_ident` / `stable_hash`;
  `struct_format.parse_format` / `calcsize`; `proof2why3/normalize`'s whole file (regex).
- `pure_ast._Parser.error` / `.unsupported` — they DO convert (491→489) but
  `bin/check-emitted-vacuity.py --emit` reports 2 NEW erasures. **REOPENING: a modelled message
  payload on the raise** — the same decision `_fin` needs.
- **`exception_model.bases_closure`** — the wall is the VALUE MODEL, not termination.

## Instrument facts — unchanged and still load-bearing

1. **`why3` is NOT on the default PATH** (`/home/fabrice/.opam/framac-coq8/bin`). Without it
   `pycsl.py` errors AND EXITS 0. `export PATH=...` on every gate.
2. `--import-path src/pycsl` is the canonical mirror path.
3. `check-emitted-vacuity.py` is a false green without `--emit` — but WITH `--emit` it is CHEAP
   (re-emits all 52 mirrors `-P 7 --no-proof --no-typecheck --keep-mlw`, **under a minute**, and it
   IS the vacuity plane). Prefer it over pycsl.py's slow embedded per-goal `why3 prove -g` loop.
4. `.gitignore` has `*.mlw` — `git add -A` SILENTLY SKIPS evidence files.
5. `bin/check-untrusted-emitted.py` reports 0/0/0/0 — a FALSE GREEN — with no PATH export.
6. `python3 -u` on every proof. A run can sit at ZERO prover results for 50 minutes and then
   flush 1500 — do NOT conclude "stuck"; check for live `alt-ergo`/`z3` children.
   **#22 confirms this directly: `pure_ast.py` produced 0 `Prover result` lines for its entire
   first 20 minutes with exactly one live prover child throughout.**
7. A FAILING `pycsl.py` run is much FASTER than a passing one. **Emitting `pure_ast.py` alone
   with `--no-proof --keep-mlw` takes 1.8 SECONDS** — a vastly cheaper probe than a sweep.
8. BACKGROUND WATCHERS DO NOT SURVIVE YOUR TURN ENDING. **But a `nohup … &` proof process DOES**
   (#22 relied on this). `scratchpad/w3/prove.sh` / `prove_wt.sh` prove a list sequentially;
   `bin/byte-diff-sweep.sh` runs `--no-typecheck`.
9. `scratchpad/w2/sweep.sh <abs-root> <abs-outdir>` emits all 52 mirrors WITH L3-tc in ~35 s
   and writes an md5 manifest. **PASS ABSOLUTE PATHS.**
10. `--fun` CANNOT probe `Module5_IREmitter` at all — whole-file or nothing.
11. A git worktree is the right place for a spike. Sync with
    `git checkout --detach $(git -C <main> rev-parse HEAD)`.
12. A PROOF TRANSFERS BETWEEN TREES WHEN THE EMISSION MANIFEST IS IDENTICAL.
13. The Alt-Ergo pin at `pycsl.py:1318` is stale. Pass `--provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,'`
    EXPLICITLY; do NOT edit the pin.
14. `grep` here is ugrep and MISBEHAVES on `driver-progress.log`. Use python, via a
    `python3 - <<'PYEOF'` heredoc, never inline `-c`.
15. `cd` PERSISTS ACROSS A COMPOUND BASH COMMAND. Use absolute paths after any `cd`.
16. **NEVER put a `\trusted` marker LITERAL in a mirror comment** — it counts as a MARKER.
17. `TMPDIR=/home/fabrice/git/pycsl/scratchpad` for `bin/check-shadowed-selfcalls.py`.

## The method note THIS session paid for (#22)

**THE PRICE LESSON IS NOT A ONE-OFF — IT REPEATS ON THE VERY NEXT RECORD YOU READ.** #21 discovered
that a recorded price is a claim and corrected #20's. #22 then applied the same five-minute
`ast`-and-`grep` census to the price #21 itself had just written down, and it was wrong too — in the
*favourable* direction (54, not 51). Both directions matter: an overstated price stops a build that
should happen, and an understated one under-funds it. **The census that corrects a price costs
minutes; the record it corrects has stood for windows.** Run it as reflex on any figure you are
about to plan against, including one written an hour ago by the immediately preceding worker.

Corollary specific to this metric: **counting `\trusted` markers is not the same as counting
convertible methods.** In `pure_ast._Unparser` those numbers are 54 and 51 — the gap is markers on
decorated and nested defs. Quote the marker count for the metric, the method count for the plan,
and never silently substitute one for the other.

## The method notes #20 and #21 paid for (still the operating rule)

**A REOPENING CAPABILITY IS A CLAIM, AND SO IS A RECORDED PRICE.** This campaign has now found a
recorded boundary's *reason* wrong seven times, a recorded *price* wrong twice, and a named
*capability* already-built-and-working once. The standing rule: **verify every part of a record —
reason, capability, AND price — against the emitted `.mlw` and the actual tree**, before you spend
a window on it. `check-self-annotate-sync.sh` is a live plane for EMITTER edits too, not only
mirror edits; run it after ANY `src/pycsl/` change.
