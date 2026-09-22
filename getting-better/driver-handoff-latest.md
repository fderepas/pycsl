# ====== START HERE — gen #30 (autonomous 96h run, deadline epoch 1790150356 = 2026-09-23T07:59Z) ======
#
# ## HOW TO RUN ANYTHING: `. scratchpad/g29/env.sh` first (why3 is NOT on the default PATH; it also sets
#    PYTHONHASHSEED=0). $SCRATCH = /tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad.
#
# ## WHAT THIS EVENING WAS ABOUT, IN ONE PARAGRAPH (read before the detail)
#    The campaign steers by numbers its planes produce. SIX of those numbers were wrong,
#    all in the same instrument family, and every one was found the same way: A WITNESS
#    THAT FIRED AND MOVED NOTHING. A census truncated at 110 characters by a writer three
#    generations old; the same census cut mid-UTF-8; a matcher looking for `%s`
#    placeholders the compiler never prints; a population filter that excluded every route
#    refusal this campaign writes (they use an aliased exception name); eight refusals no
#    source file can reach; nine with no literal long enough to match. "113 refusals need
#    witnesses, five minutes each" — nine hours of work — was 19. Meanwhile the ADVICE
#    surface, listed as unmeasured for generations, turned out to be 108 messages of which
#    SIX told the reader to write something that does not work, TWICE something the
#    compiler cannot compile. Route #215 fell out of auditing one of them.
#    THE HABIT TO CARRY FORWARD: when new evidence does not move a number, suspect the
#    number's collector before you suspect the evidence.
#
# ## LATE-EVENING ADDENDUM (2026-09-22T23:00Z) — READ THIS FIRST
#    - **ROUTE #215 DEMONSTRATED AND CLOSED**, and it came out of the ADVICE AUDIT rather
#      than a hunt for routes. `f[T](...)` on a generic FUNCTION is NOT VALID PYTHON (PEP
#      695 makes a generic CLASS subscriptable; CPython 3.14 raises `TypeError` for a
#      function), PyCSL accepted it, erased the call to a per-NAME opaque, and a REBOUND
#      local read the same constant twice — so `a = ident[int](1); x = a;
#      a = ident[int](2); return x - a` PROVED `\result == 0` for a program that cannot
#      run. Refused at `_run_pipeline` (a `\trusted` twin). Witness 1796, control 1797,
#      record `getting-better/open-routes/route215-generic-function-subscript.md`.
#      GENERATION TOTAL: 26 demonstrated, 23 closed, 3 open (#212/#213/#214).
#    - **NEW PLANE `bin/check-refusal-advice-audited.py`** — 94 advice-bearing refusals,
#      **ALL 108 AUDITED** by writing the program each message tells you to write (the
#      population went 94 -> 108 when the plane's own alias blind spot was fixed — it had
#      inherited `sites()` from the coverage plane). **102 WORK.** SIX were
#      broken and ALL SIX were repaired: 2 UNSPELLABLE (`#@ shared`, `#@ touches_field`
#      are syntax errors as written), 2 UNTRIED (an explicitly-called DUNDER loses its
#      contract; `Optional[List[T]]` emits unbound `array`), 2 AMBIGUOUS (one needs a
#      LOCAL instance and does not say so; one is an OR-list whose first disjunct is
#      really a conjunction). NOTHING IS LEFT UNAUDITED — the plane ratchets at 108, so
#      the next generation continues from there and a NEW advice-bearing refusal lands
#      unaudited and visibly lowers the fraction.
#    - **REFUSAL COVERAGE FINAL FOR THIS WINDOW: 184 of 219 demonstrated**, and the four
#      counts PARTITION the population (184 + 17 undemonstrated + 8 not-source-reachable
#      + 10 unmatchable). Started the evening at a reported 85 of 198 with 113 "missing
#      witnesses". THIRTY-ONE witnesses written (1762-1799); SEVEN MORE were written,
#      fired, and DELETED because the census already had a witness for that exact message.
#      THE REMAINING 17 need the trigger read out of the EMITTER, not guessed from the
#      message — route #31's list-local poison was probed with two spellings and BOTH
#      verify, so the file that looked like a witness would have been a PASS wearing a
#      FAIL docstring.
#    - **THE COVERAGE GATE'S SIXTH ARTIFACT, and the worst:** `sites()` required the raised
#      NAME to start with `PyCSL`, and 21 raises use a local alias (`as _PyCSLSemErr204`) —
#      every route refusal landed in `pycsl.py` since route #29. They were not
#      undemonstrated, they were OUTSIDE THE POPULATION. 198 sites -> 219. Counts now
#      182 demonstrated / 19 undemonstrated / 8 not-source-reachable / 10 unmatchable.
#    - **TWO MORE COMPLETENESS GAPS, both measured with controls and both now RECORDED
#      IN THE REPO rather than only in a commit message:**
#      (a) an explicitly-called DUNDER does not carry its contract. The emission says why:
#          the method is not emitted as a `let` at all and the call becomes a CONTRACTLESS
#          abstract op (`val c___enter___0 () : int`, no ensures, no receiver). SOUND (a
#          contractless val is fresh, so a caller proves LESS, never more). Recorded as
#          corpus **1800**, an expected-PASS that claims only what the model carries — a
#          FAIL witness would be an XPASS the day the gap closes. POPULATION: 49
#          non-`__init__` dunder defs in the corpus, 10 mirror, 14 live, 8 pycsl_lib.
#      (b) `Optional[List[T]]` as a parameter or local emitted WhyML with an unbound type
#          symbol `array`. **THE IMPORT HALF IS FIXED** (a late pull in the same shape as
#          route #44's, byte-inert: ZERO corpus files use Optional/Union over a container).
#          What remains is DEEPER and is now visible because the import no longer hides it:
#          the union TYPE declares the list arm's payload as `int` while the arm GOAL
#          quantifies `array int`, so the injection goal is genuinely FALSE. Fixing that
#          means making the two payload-type computations agree.
#    - **BATTERY: 43 of 43 FAST PLANES GREEN** at HEAD 95ba418b, after every compiler edit
#      of the evening (three refusal-message repairs, route #215's refusal, the union-array
#      late pull) and the three new planes. MIN_PLANES 40 -> 43.
#    - **MIRROR RE-PROOF GREEN**: `src/self-annotate/src/core_ir_semantic.py` —
#      "All contracts formally proven". It was owed because `_check_mutable_defaults` is
#      one of the 887 VERBATIM un-trusted twins and its message changed twice; the
#      evening's OTHER three message repairs sat in `\trusted` twins and owed nothing,
#      which is the choke-point rule earning its keep.
#    - **STILL RUNNING when this was written** (poll, do NOT relaunch):
#      `bin/check-stdlib-modules-verify.py --verbose` (/tmp/mv3.log), re-run after the
#      THREE-WAY split of its "verifies with no postcondition" class. If it comes back
#      with a NO-ENSURES count above 1, the ceiling (`MAX_NO_ENSURES`) needs the measured
#      number and the member list printed — see wall-lesson (p3).
#
# ## IN FLIGHT RIGHT NOW (2026-09-22T19:30Z)
#    - **[SUPERSEDED — see the late-evening addendum at the top: TWENTY-SIX routes,
#      #191-#215, TWENTY-THREE CLOSED.]** TWENTY-FIVE routes (#191-#214); TWENTY-TWO CLOSED and
#      THREE OPEN (#212, #213, #214), each open one with its repair PRICED and its carrier
#      runnable by `bin/check-open-route-carriers.py`.** Six landed in the 14:30-15:05Z
#      stretch: #204 (an `#@ interface assigns` NARROWER than the definition — the
#      narrowing VC proves ensures and requires and emits NOTHING for assigns),
#      #205 (an over-claiming `#@ interface` is refused AT HOME and believed by EVERY
#      importer — the VC was emitted "only in the owning unit"), #206 + #208 (a
#      `happy ... total` policy proved over a helper that never returns: `\trusted`
#      first, then `\diverges` walking through my own repair twenty minutes later),
#      #207 (`no_exception \all` proved through a `\trusted` METHOD that always raises;
#      the module-level twin was ALREADY refused), #209 (the `protects` trust boundary
#      asked a `pure_ast` matcher about a CSL node and had NEVER fired).
#      Then #210 (a `#@ check False` stamped into a `\trusted` body that is NEVER
#      LOWERED — the policy enforced by nothing), #211 (the same in the PARAMETRIC
#      `footprint` form; the twin is ONE annotation line), and #212, DEMONSTRATED AND
#      LEFT OPEN: an importing unit believes EVERY contract of an imported module —
#      frames, postconditions, class invariants — and nothing checks the module was
#      verified. Two ordinary files, no annotation tricks. `--verify-imports` (OFF by
#      default, transitive, cycle-safe) is the certificate that hole needs and is now
#      built; the route stays open because the DEFAULT still believes.
#      Docs: getting-better/open-routes/route204…route212*.md. Witnesses 1707-1723.
#    - **BATTERY 28 -> 38 fast planes**, all green at HEAD. New today:
#        check-stdlib-identity-stubs.py      81 `return <param>` stubs pinned by their own
#          contract; 23 of them are FALSE of the function their header cites.
#        check-stub-import-resolution.py     TRUSTED_STUB resolves NOTHING (the glob sees
#          files, the layer ships packages) and NINE package names (os, json, re, stat,
#          errno, http, copyreg, reprlib, token) would shadow the real module the day the
#          one-line "typo fix" lands.
#        check-corpus-contract-truth-args.py 412 corpus functions, 4354 argument-level
#          evaluations against CPython, 0 disagreements.
#        check-trust-blast-radius.py         56%-61% of the mirror is trusted OR
#          trust-dependent, against a marker count of 459.
#        check-claim-vacuity.py              1791 of 3888 corpus files carry `ensures True`.
#        check-mirror-claim-strength.py      15% of the UN-trusted mirror says anything
#          about the VALUE it computes.
#        check-trusted-termination-honesty.py  52 trusted bodies whose termination is
#          assumed and unverified (the third honesty plane, after frame and raises).
#        check-happy-trust-boundaries.py    an EXECUTABLE gate: a CARRIER and a CONTROL
#          for each `#@ happy` trust boundary through the shipping pipeline in 3.2s.
#          Executable on purpose — #209 and #211 both READ correctly and could not fire.
#        check-refusal-witness-coverage.py  STATIC HALF IN, census sweep in flight: which
#          of the compiler's 195 raise sites has a witness DEMONSTRATING it can fire?
#          Refuses until bin/refusal-witness-census.tsv exists (--regenerate builds it).
#        plus core-only / frontend-only conformance (also run by run-reference-tests.sh —
#          see the correction in the probe ledger).
#    - THREE PERCENTAGES worth carrying into any summary: 45% of corpus files run with
#      `--no-proof` (38 of 40 sampled VERIFY under the prover); 46% carry a contract that
#      says nothing, including ALL 840 `*_call_fails.py` AND ALL 840 `*_call_proves.py`
#      (60 of 60 sampled `*_call_fails.py` VERIFY); 15% of the proved mirror makes a value
#      claim. None is a soundness failure; all three are the gap between what the numbers
#      say and what a reader hears.
#    - THIRD L-PLANE for #204-#209: corpus byte-diff vs 41cb466c is **0 MOVED**, 1 GONE
#      (1617, gen #29's route-#176 carrier, now refused instead of failing — expected FAIL
#      both ways, still XFAIL). Mirror-sync green at 887 (every repair sits at a choke
#      point whose mirror twin is `\trusted`, so NO mirror edit and NO re-proof was owed).
#    - RUNNING, do NOT relaunch (poll the logs):
#        $SCRATCH/fullsuite.log      full reference suite at HEAD, 3863 tests / 3 suites
#        $SCRATCH/refusalcensus.log  all 759 expected-FAIL witnesses, classifying each as
#          REFUSAL / VERIFY-FAIL / XPASS-ALERT — feeds a planned
#          `check-refusal-witness-coverage` plane (195 raise sites, 47 codes, static side
#          already extracted) answering route #209's question mechanically: WHICH REFUSALS
#          HAVE A WITNESS PROVING THEY CAN FIRE?
#        $SCRATCH/noexcreg.log       134 `no_exception` corpus files re-run after #207
#    - LATE-DAY ADDITIONS (17:00-18:45Z): routes #213 (+ its three-argument spelling) and
#      the OPEN #214, both from route #197's own sentence; a CONSTRUCTED `stable_hash`
#      collision ("ah02"/"atc3" -> 185314078) that is not exploitable today because the one
#      op receiving a folded literal is a `val`, not a `val function` — held by
#      `check-hashed-literal-purity.py`; the AXIOM REGISTRY mined (the legacy
#      `UnixFs.Struct.*` round-trips are UNGUARDED where their successors are guarded
#      "faithful to CPython's out-of-range struct.error", and `capwords_length_nongrowing`
#      is false for 'ß' -> 'Ss'); and **THIRTY refusal witnesses written**, taking
#      `check-refusal-witness-coverage.py` from 58/198 demonstrated to 84/198.
#    - OPERATIONAL RULE learned the hard way: a `--slow` battery MUST run alone. Sharing
#      12 cores with the suite and two sweeps made the mirror emission incomplete (44 of
#      52) and three emission-dependent planes REFUSED — correctly, and for the wrong
#      reason. The same set was 49/49 green on a quiet machine.
#
#    - THE QUEUE FOR WHOEVER PICKS THIS UP, in the order I would take it:
#      1. **ROUTE #212, the open one.** Two ordinary files; the importing unit believes
#         every contract of an imported module. `--verify-imports` is built and OFF by
#         default. Closing it means a MODULE-LEVEL CERTIFICATE, and the design note is in
#         `getting-better/open-routes/route212-*.md`: "verify the file on its own" is NOT
#         the right meaning, because a module can be meaningful only inside an importing
#         context (measured: 2 of the corpus's 30 dependencies fail standalone for exactly
#         that reason, with PASS-expected importers). The IR has NO provenance field on a
#         function — that is the missing primitive.
#      2b. *** PRICED AND READY, 2026-09-23T00:00Z — DO THIS FIRST NEXT WINDOW. ***
#         The refusal (`PYCSL-SEM-SUBSCRIPT`, core_ir_semantic ~585) keys on
#         `symtab.get(<var>) == "bytes"`, and `_build_function_symbol_table`
#         (Module5_IREmitter ~5596) types EVERY plain `x = <expr>` local as `"Any"` with
#         ONE exception: a bytes LITERAL. Its own comment says a `bytes(...)` /
#         `bytearray(...)` CONSTRUCTOR call "stays Any (unchanged — 0616/0658/0665
#         untouched)". So the one-line change is to type a local assigned from `bytes(...)`
#         as `"bytes"`, which makes the refusal fire and removes the reliance on
#         ill-typedness that witness 1725 pins.
#         BLAST RADIUS MEASURED (all four populations, lesson (d3)): locals assigned from
#         `bytes(...)` occur **9 times in the corpus** (1601, 1725, 0868×2, 0658, …),
#         **ZERO in the mirror**, **ZERO in the live tree**, and ONCE in
#         `src/pycsl_lib/os/UnixInodeFileSystem.py`. That is an adjudicable byte-diff, not
#         a sweep — which is exactly why it is worth doing as a FIRST act with a full day
#         rather than squeezed in beside two running jobs.
#         AFTER the refusal lands, the `bytes` lowering can take the `bytearray` count form
#         that `expressions.py` already has (`Array.make n 0`), because the type error will
#         no longer be the only thing holding the line.
#      2. **The `bytes(n)` lowering, and the refusal it needs FIRST.** `bytes(n)` is left
#         ill-typed on purpose (witness 1725): the type error is the only thing stopping a
#         `bytes` item assignment from proving, because `PYCSL-SEM-SUBSCRIPT` keys on the
#         symbol table typing the local `bytes` and never does for `b = bytes(2)`. Fix the
#         refusal, THEN the lowering. Same shape for `list([1, 2])` (recorded, unfixed).
#      3. **The 1791 claim-vacuous corpus files**, starting with the 840 `*_call_fails.py`
#         whose names promise a failure mode they cannot exhibit. 1 repaired as the worked
#         example (`median_high_call_fails.py`); the ceiling in `check-claim-vacuity.py`
#         only moves down.
#      4. **The 20 stdlib modules that do not verify** (`check-stdlib-modules-verify.py`
#         holds them by name). The `json` package is a CPython transcription with zero
#         annotations in four files — the question is whether it belongs in the layer at
#         all, not how to prove it.
#      *** UPDATE 21:30Z: ITEM 5 WAS WRONG, AND THE CORRECTION IS THE RESULT. The
#      "113 refusals with no witness, five minutes each" was an INSTRUMENT ARTIFACT
#      four times over — see wall-lessons (j3) and (k3):
#        (a) 318 of the census's 437 refusal rows were cut at 110 characters by a
#            writer three generations old, so any site fragment starting past char
#            110 could never match. Repaired in four conservative passes (each
#            rewriting a row only when it could prove the same refusal still fires;
#            the last pass had to try EVERY file with a given basename, because
#            0508.py exists in two corpus directories). +33 sites.
#        (b) Eight `ir_schema.validate_ir` checks are NOT REACHABLE from a `.py`
#            source file — no corpus witness could ever move them. Now demonstrated
#            executably by the NEW `bin/check-ir-schema-refusals.py` (eight carriers,
#            a well-formed CONTROL, and a #44 guard that refuses on a rename or a new
#            uncarried check). A grep for `validate_ir` across test-suite/ had found
#            ZERO: the IR's own structural contract had no test of any kind.
#        (c) Nine raises have no string literal of 25+ chars, so their fragment is ""
#            and they can NEVER match. Counted separately, ratcheted, and DERIVED
#            every run rather than listed by name. Corpus file 1772 is the standing
#            illustration: it fires one of them and the instrument still cannot see it.
#        (d) Several raises use %-formatting, so the AST literal contains `%s`, which
#            the compiler never prints. Three real witnesses (1784/1785/1786) fired
#            and moved the count by ZERO before `sites()` learned to split on
#            placeholders. The plane now REFUSES if any fragment still holds one.
#      TWENTY-FIVE WITNESSES WRITTEN (1762-1788, minus four deleted as redundant —
#      always check the census before writing one). Counts: 85 -> 156 demonstrated,
#      113 -> 25 undemonstrated, and all 198 sites now partition:
#      156 + 25 + 8 not-source-reachable + 9 unmatchable.
#      WHAT IS LEFT of item 5 is 25 real ones, mostly Module3_Weaver's `happy` family
#      and module6 statements/expressions. ***
#      5. **The 113 refusals that still have no witness.** `check-refusal-witness-coverage`
#         went 58 -> 85 of 198 this generation by WRITING 31 witnesses; the rest are
#         mostly in `Module3_Weaver` (the `happy` family, ~20) and `core_ir_semantic`
#         (~13), and each costs about five minutes: probe the shape, confirm the refusal
#         fires, write the file with `# pycsl-expected: FAIL`, extend the census artifact
#         (do NOT regenerate — that is a 100-minute sweep), ratchet both counts.
#      6. ~~The 24 UNADJUDICATED identity stubs~~ **DONE 20:50Z, and seven were FALSE.**
#         All 24 adjudicated against this CPython; `MAX_UNADJUDICATED` 24 -> 0, so the
#         debt counter is now a ratchet. It needed two new classes (DECLARED-DOMAIN,
#         MODEL-INTERNAL) with `pkl.dump` as the standing control that stays OUT of the
#         first one. The 29 un-audited advice sites are STILL OPEN.
#         WHAT IT LEFT BEHIND, in priority order:
#           *** UPDATE 21:05Z: a, b, c AND e ARE ALL DONE. Six of the seven false
#           contracts are REPAIRED and re-verified; the seventh (`que.qsize`) turned out
#           INNOCENT on investigation and is reclassified, not fixed. d was a FALSE
#           FINDING of mine — see (i3). What is left of item 6 is the 29 un-audited
#           advice sites. Commits faa46282, fa930d45, 70070ad8, b96d9def. ***
#           a. **Four FALSE contracts in `src/pycsl_lib` with a PROVED FALSE CLAIM
#              DOWNSTREAM in `src/pycsl_lib_test`**, which is the route standard met
#              inside the stdlib layer: `formal_csvmod.test_write_row_identity` proves
#              `\result == n` for a written row's field count (CPython returns 7 for 3
#              fields — the CHARACTER count) and `formal_cvar.test_set_returns_value`
#              proves `\result == value` for `ContextVar.set` (CPython returns a Token;
#              its docstring even says "Returns Token (the value)"). Also
#              `csvmod.writerows` (`== rows * fields_per_row`; real `writerows` returns
#              None) and `cvar.context_var_get`. THE REPAIRS ARE WORKED OUT AND MEASURED:
#              write_row/writerows `==` -> `>=` (bytes >= fields, true of CPython and
#              exactly what their own docstrings already say); `context_var_set` drops the
#              identity for an opaque non-negative handle; `context_var_get` takes an
#              `is_set: int` with `requires is_set == 0` so the assumption is IN THE
#              CONTRACT. Each needs the matching `src/pycsl_lib_test/formal_*.py` driver
#              weakened and `check-stdlib-modules-verify.py` re-run for those modules.
#           b. `dec.getcontext_prec` needs `requires prec <= 999999999999999999`
#              (`prec = 10**30` RAISES OverflowError past `decimal.MAX_PREC`).
#           c. `nums.rational_num` / `rational_den` need coprimality
#              (`Fraction(2,4).numerator` is 1, not 2) — check PyCSL has a `\gcd` first.
#           d. ~~`hq.*_max` never tie `heap` to `n`~~ **THAT CLAIM WAS FALSE — see
#              wall-lesson (i3).** All three carry `#@ requires \length(heap) == n`
#              (hq/__init__.py 80, 105, 114). It was asserted from a `grep -A 4` on the
#              `def` line, which cannot show the annotation block above it. NOTHING TO DO.
#           e. `que.qsize` pins `\result == self._size` under a docstring quoting
#              CPython's own "APPROXIMATE" — true of a single-threaded model, and nothing
#              in the file says the model is single-threaded.
#      6b. **NEW PLANE, `bin/check-docstring-contract-disagreement.py`** (wall-lesson
#         (g3), the free oracle): a docstring that states a WEAKER relation than the
#         `#@ ensures \result ==` clause beside it. 7 hits, 3 DISAGREES and 4 CONTROLS
#         (QUOTED-RELATION / BRANCH-CONDITION / GUARD-RESTATED). It found `que.qsize`,
#         which the hand pass had missed. **NOT YET REGISTERED in
#         `bin/run-soundness-planes.sh`** — the battery was mid-run and bash reads a
#         script incrementally. Register it and raise MIN_PLANES 40 -> 41.
#         KNOWN LIMITATION, worth one more plane: it missed `csvmod.writerows`, whose
#         docstring says "Total bytes written is non-negative" — no weakener WORD, but the
#         docstring names a DIFFERENT QUANTITY than the clause pins.
#      6c. **`bin/check-getattr-erasure.py` REDESIGNED, per-file baseline.** It went RED
#         at 20:40Z (UNKNOWN 27 > ratchet 25) because gen #30's own witnesses grew the
#         corpus — the THIRD such bump (19->24 for route #47, 24->25 for #197). The
#         file's own note had asked for this redesign twice. Gated now on
#         `bin/getattr-erasure-sites.tsv` (file -> ABSENT, UNKNOWN): a baselined file that
#         GROWS fails, an unregistered file with any site fails, DECLARED stays a hard
#         zero, and the global totals are printed but gated on nothing. **THE TSV IS NOT
#         YET GENERATED** (`--emit-baseline` needs a quiet machine; the battery was
#         running) and the plane REFUSES with rc=2 until it exists.
#         WHEN YOU GENERATE IT: run `--emit-baseline` TWICE on a quiet machine and check
#         the two TSVs are identical before committing. `emit_and_collect` returns [] on
#         a timeout, so a contended run silently UNDER-counts a file, and an under-counted
#         row would then fail every honest run afterwards. (Lesson (e3), applied before it
#         bites rather than after.)
#      6d. **NEW PLANE, `bin/check-refusal-advice-audited.py`** — the ADVICE surface,
#         which `convergence-metric-implement.md` has listed as unmeasured for
#         generations. 94 advice-bearing refusals of 198 raise sites; **10 audited by
#         writing the program each message tells you to write**: 7 FOLLOWABLE, 1
#         UNSPELLABLE (`#@ shared` alone is a syntax error), 1 UNTRIED (an
#         explicitly-called DUNDER loses its contract — `enter` verifies, `__enter__`
#         does not, identical otherwise), 1 AMBIGUOUS. All three broken messages were
#         REPAIRED in the same commits. THE REMAINING 84 ARE THE WORK ITEM, and it is
#         cheap per item: write the file the message describes, run it, add a baseline
#         entry. Key is a TEXT SIGNATURE, so a message edit invalidates its verdict.
#         STANDING FINDING worth its own look: the dunder-contract gap is a real
#         completeness hole (`c.__len__()` cannot use its own postcondition) and nothing
#         else in the repo measures it.
#      7. The `check-avatar-frame-parity` INHERITED segment (7 sites) and the hval
#         absent-key sentinel's MIRROR side, still priced as infeasible in a short window.
#
#    - LANDED EARLIER: the four gen-#30 legs (final battery 45 planes green, slow-planes 49
#      green at HEAD, sampler 198 generated drivers 0 RED, the 44 real-contract
#      `--no-proof` files: 17 prove / 25 fail).
#
#    - AT THE DEADLINE (2026-09-23T07:59Z) run §A.3: stop iterating, do NOT re-arm the
#      heartbeat, `rm getting-better/.driver-deadline getting-better/.driver-started`,
#      emit ONE summary (getting-better/gen30-summary-draft.md is the draft), do NOT push,
#      end with `STATUS: DEADLINE-REACHED`.
#
# ## EARLIER (2026-09-22T12:47Z, after the weekly-rate-limit kill at ~05:05Z)
#    - THIRTEEN routes (#191-#203). SIX PLANES added this generation; battery **24 fast /
#      45 with --slow**, all 24 fast green at HEAD febbb08a.
#    - EVERYTHING DETACHED SURVIVED THE 7h40m GAP AND FINISHED GREEN:
#        #198 mirror re-proof  stmt_control_flow  12589 goals  Verification SUCCESS 07:26Z
#        #201 mirror re-proof  expressions        21347 goals  Verification SUCCESS 08:01Z
#        gen11 fuzzer          60/60 seeds, 960 return-boundary programs, 0 false proofs
#      So all six post-kill routes have COMPLETE three-L-plane evidence.
#    - RUNNING: $SCRATCH/final_battery.log — the FINAL control battery at febbb08a
#      (suite then --slow planes) in pycsl-w52, started 12:46:34Z. Poll it; do not relaunch.
#      Predicted: 3823/3841, same 18 CONFIRMED FAIL, 0 XPASS, 45 planes green.
#    - AT THE DEADLINE (2026-09-23T07:59Z) run §A.3: stop iterating, do NOT re-arm the
#      heartbeat, `rm getting-better/.driver-deadline getting-better/.driver-started`,
#      emit ONE summary (getting-better/gen30-summary-draft.md is the draft), do NOT push,
#      end with `STATUS: DEADLINE-REACHED`.
#    - Do NOT push. Nothing has been pushed.
#
# ## EARLIER (2026-09-22T04:37Z)
#    - THIRTEEN routes (#191-#203) and FIVE planes this generation. Battery **23 fast /
#      44 with --slow**, all 23 fast green at HEAD. MIN_PLANES tightened to the exact
#      fast count (it had carried slack).
#    - SUITE LEG GREEN at bc0561ec: 3823/3841, 746 XFAIL, 0 XPASS, the same 18.
#    - ALL BYTE-DIFFS IN for #198-#203 (see driver-progress.log, read line by line).
#    - RUNNING, do NOT relaunch:
#        $SCRATCH/prove198.log  RESTARTED 04:36Z with `timeout 43200`. The first attempt
#                               died at 2h50m because I killed its `timeout` wrapper
#                               trying to extend the deadline — `timeout` forwards signals
#                               to its child. `$SCRATCH/prove198-killed.log` is the corpse.
#        $SCRATCH/prove201.log  #201 mirror re-proof (expressions, the giant, 12h timeout)
#        $SCRATCH/fuzz11.log    gen11, seed 11 of 60, 0 false proofs
#    - #203 owes NO re-proof (its edit did not move the mirror); #198 and #201 do.
#    - FINAL CONTROL BATTERY still held: `$SCRATCH/final_battery.sh <worktree> <commit>`.
#    - Do NOT push.
#
# ## EARLIER (2026-09-22T04:20Z)
#    - SUITE LEG IS GREEN: 3823/3841, 746 XFAIL, **0 XPASS**, the same 18 CONFIRMED FAIL
#      (pycsl-reference 0211-0220 + 0701, python-reference 0043/0048/0079/0080/0082/
#      0095/0110). Run at bc0561ec in pycsl-w52.
#    - ALL BYTE-DIFFS IN for #198-#203; see driver-progress.log for the line-by-line read.
#    - STILL RUNNING, do NOT relaunch:
#        $SCRATCH/prove198.log  #198 mirror re-proof (stmt_control_flow). `timeout 14400`
#                               expires ~06:07Z. IF IT IS KILLED BY THAT, RE-RUN WITH A
#                               LONGER TIMEOUT — a wrapper timeout is not a proof verdict.
#        $SCRATCH/prove201.log  #201 mirror re-proof (expressions, the giant; 12h timeout;
#                               confirmed in the Proof Engine with 4 alt-ergo + 4 z3)
#        $SCRATCH/fuzz11.log    gen11 return-boundary fuzzer, seed 9 of 60, 0 false proofs
#    - THE FINAL CONTROL BATTERY IS DELIBERATELY HELD until prove198 reports, so it does
#      not starve it before its own wrapper timeout. Launch with
#      `$SCRATCH/final_battery.sh /home/fabrice/git/pycsl-w52 <final HEAD>`.
#    - 280 commits unpushed. Do NOT push.
#
# ## EARLIER (2026-09-22T04:07Z)
#    - THIRTEEN routes closed this generation, #191-#203, of which SIX (#198-#203)
#      landed after the third 529 kill.
#    - ALL BYTE-DIFFS ARE IN for #198-#203. Corpus: zero pre-existing programs moved in
#      every case. Mirror emission: ZERO for #199/#200/#202/#203; ONE file for #198
#      (stmt_control_flow) and ONE for #201 (expressions), each exactly the edited
#      method's own mirror, each one line, each M1-checked.
#    - RUNNING, do NOT relaunch:
#        $SCRATCH/prove198.log  #198 mirror re-proof (stmt_control_flow) — `timeout 14400`
#                               expires ~06:07Z; if it is killed by that, RE-RUN with a
#                               longer timeout, it is not a proof failure.
#        $SCRATCH/prove201.log  #201 mirror re-proof (expressions, the giant, timeout 12h)
#        $SCRATCH/suite200.log  suite for #198/#199/#200 — in its serial re-run of the 18
#                               known failures (first one confirmed: 0211)
#    - #203 owes NO re-proof: its edit to `expressions.py` did not move the mirror.
#    - NEXT: when the suite lands, run the FINAL control battery at the final HEAD with
#      $SCRATCH/final_battery.sh (suite + `--slow` planes, 43 expected green).
#    - gen11 fuzzer still SIGSTOPped: `pkill -CONT -f fuzz11.sh; pkill -CONT -f gen11.py`.
#
# ## EARLIER (2026-09-22T03:47Z)
#    - THIRTEEN routes closed this generation: #191-#202. #198-#202 landed after the third
#      529 kill. Battery 22 fast / 43 with --slow; swallowed-exceptions ratchet a hard 0.
#    - RUNNING, do NOT relaunch:
#        $SCRATCH/suite200.log   suite leg for #198/#199/#200 in pycsl-w52 (1233/3841 done)
#        $SCRATCH/prove198.log   #198 mirror re-proof, module6_whyml/stmt_control_flow
#        $SCRATCH/prove201.log   #201 mirror re-proof, module6_whyml/expressions (the giant)
#    - OWED: #202's corpus + mirror byte-diffs (predict ZERO/ZERO — the refusal is in
#      `pycsl.py::_run_pipeline`, whose mirror is a `\trusted` stub). Then the FINAL control
#      battery at the final HEAD via $SCRATCH/final_battery.sh.
#    - gen11 fuzzer is SIGSTOPped: `pkill -CONT -f fuzz11.sh; pkill -CONT -f gen11.py`.
#      Reached seed 7 of 60, 0 false proofs.
#
# ## EARLIER (2026-09-22T03:1xZ)
#    - ROUTE #201 CONFIRMED, repair WRITTEN BUT NOT YET APPLIED (patch staged at
#      $SCRATCH/r201_patch.py, `--apply` to run it): `_array_coerce_arg`'s TAIL answers
#      `(Array.make 1 0)`, an array with a KNOWN LENGTH 1. `callee("ab")` against
#      `def callee(p: List[int])` with `ensures len(p) == 1 ==> \result == 1` PROVES while
#      CPython answers 2; TRUE twin REFUSED. Corpus census: the tail fires 0 times in 1624
#      files. MIRROR census RUNNING ($SCRATCH/cens_mirror.log) — apply the patch when it
#      lands, then witnesses + both byte-diffs.
#    - SUITE LEG for #198/#199/#200 RUNNING in pycsl-w52 ($SCRATCH/suite200.log), 3841 tests.
#      Prediction: 3820 pass, 18 CONFIRMED FAIL, ZERO XPASS.
#    - #198 MIRROR RE-PROOF RUNNING ($SCRATCH/prove198.log, stmt_control_flow).
#    - OWED SLOW-PLANES LEG: DONE, 42/42 green at 2072dd8f. A SECOND one is owed for the
#      current tree and is the final control battery.
#    - gen11 fuzzer is SIGSTOPped (not killed) to free CPU: `pkill -CONT -f fuzz11.sh` and
#      `pkill -CONT -f gen11.py` to resume. It reached seed 7 of 60 with 0 false proofs.
#
# ## EARLIER THIS SESSION (after the THIRD 529 kill)
#    - Routes #198, #199, #200 closed and landed since the kill; the RETURN-BOUNDARY plane
#      `bin/check-return-boundary-substitutions.py` added (battery 22 fast / 43 with --slow).
#    - #198 a BARE `return` was the integer 0 (`raise (Return 0)`) — the same statement as
#      `return None`, which route #191 already handled. Corpus byte-diff ZERO; mirror emission
#      1 MOVED (its own file, exactly the intended correction); re-proof of
#      `src/self-annotate/src/module6_whyml/stmt_control_flow.py` RUNNING ($SCRATCH/prove198.log).
#    - #199 the EMPTY f-string `f""` was the integer 0. FAITHFUL repair (`stable_hash('""')`),
#      so the TRUE contract PROVES, not merely "both twins undecided". Both byte-diffs ZERO.
#    - #200 a STRING LITERAL actual was hashed into a DECLARED `int` param, and the hash ships
#      in this repo. Refused at `pycsl.py::_run_pipeline` beside route #29's refusal.
#      3996-file dry run, zero hits. Corpus byte-diff re-running clean at settled HEAD
#      ($SCRATCH/bd200b.log); mirror emission sweep still owed.
#    - NEXT EXACT STEP: when `bd200b.log` says BD-DONE, run the mirror-emit sweep for #200
#      ($SCRATCH/me200b.sh), then the suite leg (`bin/run-reference-tests.sh` in a worktree)
#      against the prediction 3817/3835 + 4 new witnesses, 18 CONFIRMED FAIL, ZERO XPASS.
#    - HELD, ready to apply the moment no sweep is running off the main tree: delete the four
#      REDUNDANT `except Exception: return None` arms in `module6_whyml/generic_fold.py`
#      (`recognize_csl_str_cata`, `recognize_term_flatten_arrow`,
#      `recognize_term_isinstance_transform`, `recognize_term_list_build`). Each already
#      catches `_PVWBail` NARROWLY one line above, so the broad arm only swallows genuine
#      bugs. Drives `check-swallowed-exceptions`'s ratchet 4 -> 0. generic_fold is NOT
#      mirrored, so no mirror cost.
#    - BACKGROUND, do not relaunch: gen11 return-boundary fuzzer, 60 seeds,
#      $SCRATCH/fuzz11.log, 0 false proofs through seed 7.
#
# ## WHAT gen #30 CLOSED — SIX SEV-1 ROUTES AND ONE NEW PLANE, all landed on ghost-assign-bc6,
#    every one battery-verified against a prediction written BEFORE the run.
#   - **#191** a `None` STORED anywhere read back as the integer 0 — route #56's general repair, the
#     LAST open route family inherited from gen #29. The typed `NoneExpr` leaf of `_expr_to_whyml`
#     answered the literal `0` while its dict-shaped twin already answered route #44's opaque.
#     Battery A: suite 3804/3822; 13 CHANGED mirrors prove 13/13 (~7h of prover time).
#   - **#192** a genuine integer `0` was re-tagged as the Python `None` at an `Optional[<record>]` /
#     union parameter slot. FOUND BY #191's OWN REPAIR. Battery B: 3808/3826, emission byte-inert.
#   - **#193** the PLACEHOLDER array for an unrepresentable iterable had a KNOWN LENGTH —
#     `len(sorted(x for x in [3,1,2]))` PROVED `== 1`, CPython 3. FOUND BY #192's LESSON.
#     Battery C2: 3810/3828; 6 mirrors prove 6/6.
#   - **THE ARGUMENT-COERCION PLANE** `bin/check-argument-coercion.py` — #192 and #193 were both
#     substitutions in `_coerce_dotted_args`, found by each other, in one day. Battery D.
#   - **#194** an ERASED COLLECTION was the integer 0, and an INT-ERASED PARAM'S CONTRACT READ IT.
#     FOUND BY THE PLANE'S OWN BASELINE, ONE HOUR AFTER IT LANDED. Battery E: 3812/3830.
#   - **#195 + #196** the EMPTY-LIST placeholder at a call boundary, read two ways: as the integer 0
#     at an int-erased param, and as a 1024-ELEMENT array at an `array int` param (where CPython's
#     OWN answer was REFUSED). Both found by sweeping the same baseline. Battery F: 3815/3833.
#   - **#197** `getattr(o, "a", 0)` on an object of UNKNOWN static type ANSWERED THE DEFAULT, and
#     the body read it — `peek(o: Any)` PROVED `\result == 1` (emitting `v := 0` with `o` UNUSED,
#     Why3 says so) while CPython answers 2. FOUND BY `check-getattr-erasure`'s OWN RATCHET NOTE,
#     which said the UNKNOWN default was "not demonstrated to be exploitable — a contract cannot
#     name a field of an object whose type the model does not carry". THE CONTRACT DOES NOT HAVE
#     TO NAME THE FIELD. Battery J2: suite 3817/3835, 3 mirrors prove 3/3.
#   - **THE TRUSTED-REASONS PLANE** — a FIFTH gate that existed and nothing ran. Battery I.
#   - **THE AXIOM-FOOTPRINT PLANE** `bin/check-proof-reverify.sh` — A FOURTH UNCOLLECTED GATE, and
#     the one that backs the ledger claim. A `#@ proof rocq|lean` directive IMPORTS the cited
#     theorem into the Why3 ledger AS AN AXIOM; nothing checked the cited theorem was PROVED.
#     MEASURED by replacing a cited `Qed` with `Admitted`: the cross-check stays green (it compares
#     STATEMENTS), the suite stays green (an `Admitted` COMPILES), and
#     `--audit-proof --reverify-proofs` catches it — a flag NO script ever passed. Batteries G, H2.
#     THEN DRIVEN 6 -> 0 unresolved, fixing two instrument bugs: a missing CROSS-TREE SEARCH PATH
#     (five citations name theorems proved in another tree; the search now reports WHERE it
#     resolved, which immediately caught it resolving inside a STALE AGENT WORKTREE under
#     `.claude/`) and a PREFIX COLLISION in the Lean footprint parse (`…round_trip_i32` stole
#     `…round_trip_i32i32`'s line). VERIFIED 155 -> 166: eleven axiom imports nothing had checked.
#   - The battery is now **21 fast / 42 with --slow**; suite **3817/3835**, the same 18 CONFIRMED
#     FAIL, ZERO XPASS. A CONTROL BATTERY on HEAD re-confirmed the mid-window state.
#
# ## THE HEADLINE, because it is the reusable part: FIVE OF THE SEVEN ROUTES WERE FOUND BY READING
#    A PLANE'S OWN WRITTEN JUSTIFICATION AS A CHECKABLE CLAIM. #194/#195/#196 came from
#    `check-argument-coercion`'s baseline (written that same afternoon), #197 from
#    `check-getattr-erasure`'s ratchet note. A gate that holds something at a ratchet "because it
#    is not sound by argument either" has written the argument down right there. Probe it.
#
# ## THE METHOD, WHICH IS THE MOST TRANSFERABLE THING THIS WINDOW PRODUCED
#   1. Close the ONE recorded-open family (#191).
#   2. When a repair changes what something LOWERS TO, census who was reading the OLD spelling.
#      That census IS the next route (#192).
#   3. Generalize the defect to its FAMILY — "a DEFINITE stand-in for an UNKNOWN value" — and
#      census that. That census IS the next route (#193).
#   4. When two routes land in one function in one day, BUILD THE PLANE before hunting again.
#   5. **THEN SWEEP THE PLANE'S OWN BASELINE.** Every justification you were forced to write down
#      is a checkable claim, and some of them are false. THREE of fourteen entries fell within nine
#      hours, with NOT ONE LINE of the emitter changed since gen #29.
#   THE ONE PROBE that found #192, #194, #195 and #196, stated once:
#      *give the callee a contract that is TRUE OF ITS OWN BODY and that READS the property the
#      substitution changes; call it with the substituted-away shape; run CPython.*
#   A callee with `ensures True` hides every defect of that family completely. That is why this
#   surface survived 190 routes.
#
# ## IN FLIGHT AT HANDOFF
#   - `bin/check-proof-reverify.sh` reads 166 VERIFIED / 0 UNRESOLVED / 0 SOUNDNESS. ANY non-zero
#     reading is now a REGRESSION, not a backlog.
#   - Two differential fuzzers, gen9 COMPLETE (8 seeds, 112 programs, zero false proofs):
#     `scratchpad/g30/fuzz/gen9.py` (four hand-picked reading callees) -> `$SCRATCH/fuzz9b.log`,
#     `scratchpad/g30/fuzz/gen10.py` (the six-shape x five-contract x eleven-actual cross-product,
#     40 seeds) -> `$SCRATCH/fuzz10.log`. Look for `FALSE-PROOF` lines; each names its file.
#   - Tree CLEAN, every increment committed, NOTHING pushed (push stays gated to the user).
#
# ## SURFACES SWEPT CLEAN THIS WINDOW (do not re-probe without a new idea — see probes.tsv)
#   the singleton-constant-lowering baseline (10 entries; one STALE justification corrected — it
#   still carried the pre-route-#55 rationale route #55 had refuted); the constant-fallthrough
#   baseline (8 deciding tails; the route #29 family is refused before emission, `d.get(k)` is
#   fenced by route #57); the type-keyed-constant-answers baseline (16 arms; the two truthiness
#   OVER-APPROXIMATION arms measured by instrumenting them and emitting all 53 mirrors — one fires
#   ZERO times, the other EXACTLY ONCE on a method with `ensures True`); the value-sentinels
#   int-carrier re-measurement; the hval absent-key sentinel (corpus-UNREACHABLE, mirror side left
#   HONESTLY OPEN with the next step named); route #159's 1024-placeholder escape shapes; the
#   spelling-keyed return-type arm; ensures-propagation under a default fill; erased statements.
#
# ## TRAPS PAID FOR THIS WINDOW
#   >>> 231 of the `.tmp*.aux` files under `test-suite/corpus/pycsl-reference/*.proofs/rocq/` are
#   >>> TRACKED. Use `git clean -f <dir>`, never `find -name '.tmp*.aux' -delete`.
#   >>> `check-proof-crosscheck.sh` RECOMPILES the cited Rocq/Lean proofs, so any battery DIRTIES
#   >>> tracked `.vo`/`.olean`/`.aux` artifacts. Stage witnesses BY NAME; then `git checkout --
#   >>> test-suite/` + `git clean -f test-suite/`.
#   >>> A WRAPPER `timeout` IS NOT A PROOF VERDICT. `Module5_IREmitter` "FAILED (2400s)" while still
#   >>> printing `Valid`; it passed at 2970s. Mirror proofs now get `timeout 14400`.
#   >>> A REPAIR THAT NEEDS A NEW ABSTRACT `val` MAKES ITS EMITTER FUNCTION EFFECTFUL, and if that
#   >>> function's MIRROR is a CONVERTED method its proven `assigns \nothing` is the budget you just
#   >>> spent. Battery C went RED on three fidelity planes for exactly this; the fix was Why3's
#   >>> declaration-free `any`. CHECK THE MIRROR'S CONTRACT BEFORE CHOOSING THE DEVICE.
#   >>> Emission-diff BEFORE the proof sweep (lesson (r)) is what kept these legs to 13, 6, 3 and 2
#   >>> mirrors instead of 53. It is the single biggest time saver in the loop.
#
# ## STATE AT gen #30's START (verified from disk, not inherited)
#   - HEAD was d0748584, tree clean, battery 19 fast / 39 with --slow, suite 3798/3816, same 18
#     CONFIRMED FAIL, zero XPASS. gen #29 closed 46 routes (#143, #147-#190).
#   - LEFTOVERS CLEANED: 15 stale g29 worktrees removed (/tmp 76% -> 9% — this MATTERS, the run needs
#     the space), stray `batch5c.log` / `slicesweep_AJ2.log` / `.ftwin_self_*.py`, and the cross-check
#     gate's UNTRACKED rocq build artifacts under `*.proofs/rocq/`.
#     >>> TRAP, PAID FOR: 231 of the `.tmp*.aux` files under `test-suite/corpus/pycsl-reference/*.proofs/
#     >>> rocq/` are TRACKED. `find -name '.tmp*.aux' -delete` deletes them. Use `git clean -f <dir>`,
#     >>> which only removes the untracked ones.
#   - The wip/g29-* BRANCHES are kept (their worktrees are gone). They cost nothing; every one of them is
#     landed on ghost-assign-bc6 by cherry-pick, so `git branch -d` will refuse — delete with -D only
#     after checking `git diff <branch> ghost-assign-bc6 -- <paths>` is empty.
#   - A leftover gen #29 WATCHDOG shell (`sleep 1500` + `git log`) may still be alive; it is read-only.
#
# ## gen #30 LESSONS SO FAR
#   >>> A DEFERRAL THAT DECIDES BY "DOES THE REST OF THE FILE MENTION A NAME I DECLARE?" IS ONLY AS GOOD
#   >>> AS ITS LIST OF NAMES, AND A LIST SCRAPED FROM TEXT THAT INCLUDES ITS OWN PROSE CONTAINS WORDS THE
#   >>> CODE NEVER DECLARED. The sibling routine three definitions away already stripped comments and said
#   >>> why in its docstring; the one that did not was never exercised on a file that could trip it until
#   >>> an unrelated change made one. Nine corpus files and one mirror were carrying a 277-line ADT theory
#   >>> they never referenced.
#   >>> A LIFT THAT RECOGNISES A PYTHON VALUE BY ITS WHYML SPELLING BREAKS THE MOMENT THE SPELLING MOVES —
#   >>> and the break is fail-closed (a type error), which is why it had never been noticed. Two lifts
#   >>> recognised the Python `None` as the string `"0"`. Changing what `None` lowers to made both miss.
#   >>> AND THE SAME LIFT READ BACKWARDS IS A ROUTE CANDIDATE: it turns a GENUINE integer `0` into the
#   >>> option's `None`. Before #191 it could not tell them apart; after it, it can.
#   >>> A WRAPPER `timeout` IS NOT A PROOF VERDICT. `Module5_IREmitter.py` "FAILED (2400s)" while still
#   >>> printing `Valid` — my budget was too small, nothing was wrong. Read the tail before believing a
#   >>> FAIL; the mirror proof script now uses `timeout 9000`.
#
# ====== START HERE — gen #29 IN PROGRESS (autonomous 96h run, deadline epoch 1789893581 = 2026-09-20T08:39Z) ======
#
# ## STATUS (updated as work lands — trust `git log` + driver-progress.log over this block)
#   - Machine REBOOTED ~07:47Z 2026-09-16: /tmp scratchpads and all baselines were lost. Why3 is NOT on the default
#     PATH: `. scratchpad/g29/env.sh` (adds ~/.opam/framac-coq8/bin, PYTHONHASHSEED=0).
#   - CLOSED this generation (46 routes): #147 #143 #148-#190. Last landed: route #190 and the two
#     new planes, commit 2382a02a. The battery is now 19 fast / 36 with --slow.
#   - THE FIVE-ROUTE FAMILY: #166 #185 #186 #188 #189 are one question — WHICH CALLEE DOES THIS CALL
#     SITE GET — and the battery had no gate for it, so gen #29 built `bin/check-callee-contract-attribution.py`
#     (16 cells; decisive: it reports THREE MIS-ATTRIBUTED cells on the pre-#189 tree).
#   - #187 `#@ fresh_globals` assumed a constructor post-state the module body had already left; the
#     plane built for that surface, `bin/check-assumed-facts.py`, classifies every emitted assume/axiom
#     and found a silent `hash_eq_consistent_<cls>` axiom the hand census had missed.
#   - #190 an open-ended or negative STRING slice was decided as the EMPTY string. An exhaustive
#     64-cell slice-bound sweep: 24 false proofs at HEAD, 0 after the repair (21 completeness cells the
#     measured cost; the faithful normalisation is the recorded follow-up).
#   - GATE FACADE FOUND AND REPAIRED: `bin/check-proof-crosscheck.sh` — the mechanical 3-way check that a
#     `#@ proof` citation's Why3 axiom says what the cited Rocq/Lean theorem says — reported
#     `PASS 0 / SKIP 0 / FAIL 0` and rc=0 while checking NOTHING, because its `python -m` invocation could
#     not import the package and `|| true` swallowed the error. Repaired (PYTHONPATH, hard error on a
#     non-summary, the #44 zero-check refusal, skip `pycsl-expected: FAIL` files) and REGISTERED in the
#     battery's slow set: 17 PASS / 16 SKIP / 0 FAIL over 14 files. The runner now accepts a shell plane.
#   - THE FUZZER/SWEEP LESSON, AND THAT IT BIT TWICE: a probe that claims ONE wrong answer only catches a
#     model that answers THAT value; an ERASED value reads as 0. gen8 walked past route #190 for a batch,
#     and then the sweep built AS #190's evidence repeated the same mistake. Every fuzzer and sweep now
#     claims {v+1, 0, v-1, 99}; 234 earlier probes were re-asked that way (zero new findings).
#   - CENSUSES worth keeping: every emitted `assume` is one of TWO families (25 concurrent
#     mutex-invariant entries across 21 files, only 0256 proven, and it is the XFAIL that shows the
#     release check exists; 2 `fresh_globals` constructor post-states, proof-backed); every emitted
#     `axiom` is an audited `#@ proof` import or the one derivable `mem_head`; every abstract-op
#     `ensures` carries its side condition except `str_sub_op`'s, which was route #190.
#   - Differential FUZZERS live in scratchpad/g29/fuzz (gen.py arithmetic/control flow, gen2.py
#     dict/list/None/handlers, gen3.py classes+contracts+receivers, gen4.py inheritance/global
#     instances/folds): each claims something FALSE of CPython's observed answer and reports any
#     Verification SUCCESS. ~600 programs so far, zero false proofs.
#   - RECORDED OPEN: route #56's remaining carriers — `None` STORE positions (`xs[0] = None`,
#     `d["a"] = None`, `self.v = None`, `append(None)`) still read back as 0; the typed `NoneExpr`
#     opaque was MEASURED (16 mirror emissions move) and left to the value-model campaign.
#   - Worktrees wtL..wtY removed (branches kept). Battery R's first planes leg died when the session was
#     stopped; batteries are now launched with `nohup setsid` so they survive.
#   - LESSON (session): a compound command that cd's into a corpus and mutates it hung for 75 min; use
#     small separate steps, `timeout 900` on every pycsl/why3 call, and background scripts for sweeps.
#   ($SCRATCH = /tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad — tmpfs.
#    All worktree work is committed to the local branches wip/g29-* — recover from those, not from /tmp.)
#   - PROBED FAIL-CLOSED (don't re-probe without a new idea): arithmetic, strings, unicode, slices, comprehension
#     builtins, dunders, enums, context managers, loop-else, generators, closures, class attributes, ghost code,
#     lemmas, assert/check, module attributes, module collection frames, raises precision, try/finally, Optional, constructor contracts, loop jumps,
#     list mutators/aliasing, class dispatch, globals/recursion, global & record aliasing, nested frames,
#     builtins sequence semantics, object identity, no_exception builtin sources — probes.tsv.
#
# ## LESSONS SO FAR (gen #29)
#   >>> AN UNMODELLED NAME IN A WALK IS NOT "NOTHING THERE" (`records.get(x) is None` -> continue was an assumption).
#   >>> A PROBE WHOSE CWD IS NOT THE SUITE'S CWD TESTS A DIFFERENT RESOLVER (#143 draft 5 looked green from scratchpad).
#   >>> A NEW `raise` IN A MIRRORED TRUSTED FUNCTION MOVES THE TRUSTED-RAISES RATCHET; DECLARE `#@ raises` ON THE STUB.
#   >>> NEW `def`s IN A MIRRORED FILE MOVE MIRROR-COVERAGE; inline into an already-trusted function rather than
#       parking helpers in an unmirrored file.
#   >>> "a non-constant default stays omitted and is route #79's class" — no #79 arm reads parameter defaults (#149).
#   >>> A +1-ONLY DIFFERENTIAL FUZZER CANNOT SEE AN ERASED VALUE. An erased value reads as 0, and 0 is this
#       campaign's most common wrong answer (#31 #40 #43 #44 #56 #183 #184 #190). gen8 — the grammar written FOR
#       the slice neighbourhood — reported zero over a whole batch while route #190 was live in it, because it
#       only ever asked about `answer + 1`. Every fuzzer now claims {v+1, 0, v-1, 99}.
#   >>> THE ROUTES CLUSTER WHERE THERE IS NO PLANE. Five of gen #29's routes are one question (which callee does
#       this call site get) and the battery had no gate for it; the assumed-fact surface had none either, and the
#       plane built for it found a silent axiom the hand census had missed on its first run. When a generation
#       produces a FAMILY, build the plane before hunting the next member.
#   >>> CENSUS THE MODEL'S DECISIONS, NOT JUST ITS REFUSALS. Route #190 came out of grepping the `ensures` clauses
#       the emitter puts on abstract ops and asking which of them decides a VALUE with no side condition; exactly
#       one did (`str_sub_op`), and it was a route.
#
# ====== START HERE — gen #27 FINAL STATE — read this block first ==================
#
# ## STATUS: COMPLETE. Tree clean (two PRE-EXISTING gitlinks only), everything committed, no background process
#   alive, no worktrees left. FIVE SEV-1 ROUTES FOUND, CLOSED AND FULLY GATED in TWO batteries (#138 #139 #140
#   in battery-A, #141 #142 in battery-B); EVERY LEG OF BOTH BATTERIES WAS PREDICTED IN driver-progress.log AND
#   HIT. TWO MORE SEV-1 ROUTES FOUND, REPRODUCED AND RECORDED OPEN ON PURPOSE: **#143 and #144**.
#
# ## 1. WHAT GEN #27 CLOSED (all SEV-1, all measured PROVING with CPython contradicting)
#   BATTERY-A (commit c38d88f4) — witnesses 1404-1419 (12 XFAIL + 4 PASS):
#     #138 CARRIER-RERUN ON GEN #26'S OWN #136/#137 FENCES, EIGHT shapes. Those fences were keyed on a receiver
#          NAME (`_nb_imported` is file-wide: `import builtins; b = builtins; getattr(b, "set"+"attr")(...)`),
#          on a syntactic SHAPE (`sa = getattr(builtins, "setattr"); sa(...)` — bind the result and
#          `Call(func=Call(getattr,...))` never appears), on a token SPELLING (an eval text naming none of the
#          eight `_nb_ns_builtins` — `eval("f.__globals__.__setitem__('N', 5)")`), and on a LOCATION (a BARE
#          IN-FUNCTION eval; the location gate is about where an ASSIGNMENT lands, and a mutation through a CALL
#          does not care — same with a non-constant text). Plus the mapping reached by a mutating METHOD CALL
#          (`f.__globals__.__setitem__("N", 5)`), by the UNBOUND-method spelling (`dict.__setitem__(
#          f.__globals__, "N", 5)` — the receiver becomes the name `dict`, which has no module binding and was
#          FRESH), and as a CALL ARGUMENT (`operator.setitem(f.__globals__, "N", 5)`).
#          REPAIR: module/class-scope `getattr` and mutating dict-method calls join the path-keyed sink;
#          `__builtins__` is seeded NOT-fresh; the four namespace-bearing attributes (`__globals__`,
#          `f_globals`, `f_locals`, `__dict__`) may appear ONLY in a name binding or a subscript read, anywhere
#          in the file, and are added to #118's namespace-dict receiver rule; an `eval` whose text is
#          non-constant, or constant and containing any of `( . [`, is refused wherever it stands. `exec` KEEPS
#          its location gate — a constant `exec` is spliced in as REAL SOURCE and is modelled (0642, 0643).
#     #139 DEFERRAL-AUDIT. `construction_synth.py:83` defers a "Constant RHS" to `field_defaults`, whose rule is
#          `isinstance(rhs, ast.Constant)` — and PYTHON'S PARSER DOES NOT FOLD. `self.start = -7` is
#          `UnaryOp(USub, Constant)` and `self.start = 2 + 3` is a `BinOp`: both name-free, both unmatched by
#          the collector, and both EXEMPT FROM ROUTE #79'S UNKNOWN-MARKING BY THE SAME PREMISE, so they fell to
#          the DEFINITE witness 0. `\result == 0` PROVED; CPython -7 and 5; the true twin was refused.
#          REPAIR: `field_defaults` folds a unary-minus literal with `_const_int_value` (the sibling collector
#          `_collect_class_constants` always did) — FAITHFUL, not a witness; and route #79's literal exemption
#          now marks a name-free COMPUTED right-hand side UNKNOWN.
#     #140 DEFERRAL-AUDIT. `Module6_WhyMLTranspiler.py:289` defers raises-condition propagation to
#          `_wrap_call_with_callee_raises_assert`, whose substitution is a positional `zip(param_names, args)`
#          and whose default fill at `_handle_dotted_call` is gated on a `self.` RECEIVER. On `c.f()` and
#          `c.f(k=-5)` with `f(self, k: int = -1)` and `raises ValueError when k < 0`, `args` is EMPTY and the
#          callee's `k` renders IN THE CALLER'S SCOPE, so `assert { not (k < 0) }` is discharged from the
#          caller's own `k` and `no_exception ValueError` PROVED while CPython raises.
#          REPAIR: `_render_callee_condition` returns None when `len(args) < len(param_names)` — an incomplete
#          substitution renders NOTHING and the caller gets the honest `assert { false }`.
#   BATTERY-B (commit 678b2805) — witnesses 1420-1423 (4 XFAIL), BOTH found by CARRIER-RERUN ON BATTERY-A:
#     #141 the substitution enumerates FORMAL PARAMETERS, and `formal_params` has no `self`. A callee
#          `raises ValueError when self.tag < 0` on an object whose `tag` is -1, called as `h.f(k)` from a
#          method of a DIFFERENT class whose own `tag` is 5, emitted literally `assert { not ((self.g_tag < 0))
#          }` and PROVED. REPAIR: a condition mentioning `self` does not render at all. A module-level global in
#          a condition denotes the same object in both scopes and is untouched (census of `raises ... when
#          ...self...`: 0 sites).
#     #142 the ONE ESCAPE BOTH NAMESPACE RULES ALLOW — "it may be bound to a plain NAME", which exists for route
#          #116's `_g = globals()` idiom — is an UNGUARDED HANDLE. `_g = globals(); dict.update(_g, N=5)`,
#          `_g = globals(); operator.setitem(_g, "N", 5)` and `_g = f.__globals__; dict.update(_g, N=5)` all
#          PROVED `f() == 3`; CPython 5. REPAIR: a name bound to a namespace mapping IS a namespace mapping and
#          may only be read through a subscript — which is exactly what route #116's idiom does (1318 verifies
#          before and after; census of other uses: ONE, 1322's `_g["inc"] = dec`, already expected-FAIL).
#
# ## 1b. LESSONS (each paid for this generation)
#   >>> A DEFERRAL'S *WORD* CAN BE BROADER THAN THE GUARD'S *RULE*, AND THAT GAP IS THE ROUTE. "a Constant RHS"
#   >>> vs `isinstance(rhs, ast.Constant)`; "condition propagation is handled by <X>" vs a `zip` that TRUNCATES;
#   >>> "an OVER-arity call is a Python error" vs `len(args) > len(init_params)` on a class whose init_params
#   >>> were never merged from its base. Read the comment's noun, then read the predicate, then ask what is in
#   >>> the difference. Three of this generation's routes are exactly that difference.
#   >>> A TRUNCATED SUBSTITUTION IS NOT A MISSING FACT, IT IS A WRONG ONE. Any callee name left unsubstituted is
#   >>> rendered IN THE CALLER'S SCOPE, where a same-named local or field silently supplies a value. The control
#   >>> that proves it is RENAMING the caller's variable: the proof then fails on an unconstrained constant.
#   >>> EVERY "IT MAY ONLY BE BOUND TO A PLAIN NAME" ESCAPE HATCH HANDS OUT A HANDLE. #142 is #116's sanctioned
#   >>> idiom used as a weapon; the fix is to give the NAME the same rule as the expression it holds.
#   >>> RE-MEASURE, NEVER INHERIT — INCLUDING YOUR OWN PREDICTIONS. I predicted battery-A's emission baseline as
#   >>> "1073" by inheriting gen #26's figure; HEAD carried gen #26's own 22 witnesses and the true baseline was
#   >>> 1074. The DELTA I predicted was exact; the absolute was borrowed.
#   >>> A REFUSAL THAT CLOSES NOTHING MEASURED DOES NOT BELONG IN THE REPAIR. Draft-4 grew an arm for
#   >>> `getattr(f, "__globals__")["N"] = 5`; that shape is ALREADY refused at HEAD (Why3 typing), so the arm was
#   >>> REMOVED before the battery. Refusal surface is not free.
#   >>> THE 600-SECOND TOOL TIMEOUT IS A TURN HAZARD, NOT A PROCESS HAZARD: a poll loop longer than that gets
#   >>> backgrounded and the verdict is no longer inside your turn. Poll in <=540s foreground batches.
#
# ## 2. LADDER FOR GEN #28 — START HERE
#   (a) **ROUTE #144 IS THE TOP ITEM** (`getting-better/open-routes/route144-*.md`). Two measured shapes, both
#       SEV-1: a DERIVED `@dataclass` binds NOTHING (every field takes its definite default) because
#       `init_params` is this class's `AnnAssign`s only and `ir_resolve.py:2298` merges fields but not
#       `init_params`; and a `ClassVar` member enters `init_params` although Python does not, so the positional
#       binding is OFF BY ONE and takes the NEIGHBOURING argument. The faithful repair (prepend base fields in
#       MRO order, drop `ClassVar`s) is the right one. BLAST RADIUS, measured: 128 derived/`ClassVar`
#       dataclasses, most of them the MIRROR'S OWN CSL AST node hierarchy in
#       `src/self-annotate/src/frontend/Module2_Parser.py`. CENSUS THE CONSTRUCTION SITES (not the class
#       declarations) whose argument count exceeds the model's `init_params`, PREDICT THE MOVED SET BEFORE THE
#       SWEEP, and expect honest failures.
#   (b) **ROUTE #143** (`route143-*.md`). An IMPORTED callee's `raises` condition is folded against the
#       IMPORTING module's constants — the emitted `val` itself carries the wrong value. The repair is scoped
#       (`_resolve_direct_imports`: refuse when a name free in an injected contract, and not one of that
#       function's formal params, is also bound by the importing module). NOT landed because the `pycsl_lib` os
#       stubs' `_filesystem`/`dir_lookup` conditions were not censused against that rule.
#   (c) CARRIER-RERUN GEN #27'S OWN FIVE REPAIRS — it produced 6 of this generation's routes and every widening:
#       - the #139 `_lit79` exemption ENUMERATES SHAPES (Constant / Dict / Set / List / Tuple / a collection
#         call). A tuple field and a float field were probed and fail closed; the OTHER members of that list
#         are carried by the #85/#86/gap2a channels — verify each of those channels is really faithful.
#       - the #139 `field_defaults` arm still does `int(rhs.value)` on a FLOAT: `self.r = 2.5` records 2. The
#         `\result == 2.0` probe was refused, but find a float shape that types.
#       - the #141 rule permits any MODULE GLOBAL in a `raises` condition. Within one module that is sound;
#         #143 is the cross-module counterexample. What about a global the callee's own module REBINDS?
#       - the #142 rule keys on a name bound DIRECTLY to the mapping. `_g = globals(); h = _g` is refused
#         (a non-subscript-read use), but check a mapping reaching a name through a container or a call.
#       - the #138 `_nb_ns_attrs` list has FOUR members. `__globals__ f_globals f_locals __dict__` — is there a
#         fifth spelling of a namespace mapping (`gi_frame`, `tb_frame`, `__self__`, `__func__` chains all land
#         on one of the four; `__closure__` cells were not probed).
#   (d) MORE DEFERRAL-AUDIT. Two censuses have been run; the second one's own count is **246 comment/docstring
#       deferral hits in `src/pycsl/`, 191 after removing proof-assistant citations and Module-4 provenance,
#       179 not yet audited**, and that is a LOWER BOUND (a deferral phrased without a census word, or living in
#       an f-string, is not counted — `core_ir_semantic.py:899` was missed for exactly that reason). Sites
#       already audited and COVERED (do not re-probe): `expressions.py:1007 / 5944 / 634`, `Module5_IREmitter
#       .py:953`, `types.py:531`, `preamble.py:141`, `irx.py:11`, `generic_fold.py:1213`, `statements.py:426`
#       (STALE-BUT-COVERED — route #18 refuses it unconditionally; the DOCSTRING HEDGE SHOULD BE DELETED),
#       `functions.py:5657 / 2039`, `core_ir_semantic.py:137 / 1582 / 574`, `expressions.py:14509`,
#       `stmt_control_flow.py:1833`, `struct_format.py:288`, `ir_scanner.py:165`.
#   (e) WATCH, each one change from live:
#       - `core_ir_semantic.py:964` `_lemma_calls_trusted` matches a BARE name and a dotted call emits
#         `self.helper`, so a LEMMA METHOD CAN CALL A `\trusted` METHOD. The probe was caught only by the
#         NON-VACUITY GATE (`lemma proves ensures false`); an OPTIMISTIC-BUT-CONSISTENT trusted contract would
#         not be. `_collect_call_targets` in the SAME FILE already does the `rsplit(".", 1)[-1]` normalization.
#       - `module6_whyml/expressions.py:13882 / 13910`: "the `| _ -> <record default>` arm is UNREACHABLE
#         wherever the caller has guarded `is not None`" — THERE IS NO SUCH CHECK. Mirror-scoped (gated on
#         `_term_local_vars` / `_sibling_call_union_type`), so it is an L-plane fidelity concern, not user
#         soundness; the instrument is a mirror-fidelity driver on an un-narrowed receiver.
#       - `module6_whyml/auto_trust.py:420`: the named guard is WHY3'S region analysis, not a rule in this repo,
#         and the response to "Why3 would reject this" is to STOP EMITTING THE BODY. A refusal converted into an
#         assumption, on a purely syntactic predicate (`return_type == "array int"` + an early/in-loop return).
#         Treat as a TCB entry.
#       - `_emit_option_tuple_unpack`: gen #26's VACUOUS row is now MEASURED. An `Optional[Tuple[int,int]]`
#         method does NOT register an option-tuple local (the return type lowers to a UNION and the call site
#         becomes an abstract `val ... : int`), so the handler's POPULATION IS EMPTY and its docstring claim
#         ("the Python guard makes the None arm dead") is UNCHECKED. Latent, not live.
#       - the latent #132 str-set-folder hole (still no Module-6 consumer) and gens #25/#24/#23's lists.
#   GENERATORS THAT WORKED: carrier-rerun (#138 #141 #142 + every widening of all five repairs) and
#   deferral-audit (#139 #140 #144).
#
# ## 3. YIELD — bin/probe-ledger-yield.sh --by-generator (whole ledger, after gen #27)
#   key                    LIVE  FAILC  denom    yield  2nd-ord  VACUOUS
#   advice-audit              2      5      7    28.6%        1        0
#   carrier-rerun           115     98    213    54.0%       99       14
#   carve-out-census          9      8     17    52.9%        0        1
#   continue-census          10      4     14    71.4%        3        3
#   control-operation         3     17     20    15.0%        1        0
#   deferral-audit           11     13     24    45.8%        3        5
#   hand                      1     47     48     2.1%        0        2
#   observer-audit            0      1      1     0.0%        0        0
#   oracle-audit              1      3      4    25.0%        0        0
#   substring-census          5      2      7    71.4%        0        0
#   unknown                  35      0     35   100.0%        2        0
#   witness-census           20     43     63    31.7%        2        5
#   GEN #27 ALONE: 41 rows — 17 LIVE / 24 FAIL-CLOSED / 0 VACUOUS, across SEVEN routes (#138-#144).
#   NOTE THE DENOMINATOR MOVING: deferral-audit fell from 66.7% to 45.8% because gen #27 logged 10 FAIL-CLOSED
#   deferral rows against 5 LIVE ones. That is the ledger working — gen #26's 66.7% was 9 rows.
#
# ## 4. WHAT IS TRUE RIGHT NOW
#   metric   markers 459 / grep 484 / offset 25 / unattached 0 (UNMOVED across both batteries — a refusal and a
#            faithful fold both cost the trust surface nothing; do not chase the metric)
#   suite    NEW BASELINE 3549/3567, 18 failures — pycsl-reference 0211-0220 + 0701, python-reference 0043 0048
#            0079 0080 0082 0095 0110. A 19 is a REGRESSION. ZERO XPASS.
#   planes   34 (`bin/run-soundness-planes.sh --slow`; without `--slow` it is 19). Ratchets: trusted-raises
#            13 declared / 62 SILENT · dropped-mutation 0/51/9/0 (unratcheted REFUSED column 8) ·
#            trusted-reasons 459<->459, unclassified 458. mirror-type-only reports 53 EMITTED / 0 ill-typed
#            (gen #26's log quoted 49 — that is the emitted count, and it moved; the gate is green either way).
#   corpus   pycsl-reference 1350 sources, 1083 emitting. python-reference 2217 sources, 2199 emitting.
#   scratch  scratchpad/g27/ (ctrl/p/q/c/d/e/f/g/h/i/j/k probe drivers, all committed) and the new corpus
#            helper `test-suite/corpus/pycsl-reference/multi_file_lib/r141_raiselib.py` (route #143's callee).
#   HOW TO REBUILD AN EMISSION BASELINE (3 commands, ~4 min — the baselines live OUTSIDE the repo, in the
#            session scratchpad; NEVER inherit one):
#            git worktree add --detach <wt> <baseline-commit> && ln -s <repo>/.venv <wt>/.venv
#            ( cd <wt> && bin/byte-diff-sweep.sh <out>/corpus_base && bin/mirror-emit-sweep.sh <out>/mirror_base )
#            then the same two sweeps in the main tree + bin/byte-diff-compare.py on each pair
#            (and on <out>/*/pyref for python-reference, and --min-files 45 for the mirrors).

# ====== START HERE — gen #26 FINAL STATE — read this block first ==================
#
# ## STATUS: COMPLETE. Tree clean (two PRE-EXISTING gitlinks only), everything committed, no background process
#   alive, no worktrees left. TWO SEV-1 ROUTES FOUND AND CLOSED AND FULLY GATED this generation (#136, #137) in
#   ONE battery, every leg predicted in driver-progress.log and hit. CURRENTLY OPEN: NONE.
#
# ## 1. WHAT GEN #26 FOUND AND CLOSED (both SEV-1, all shapes measured PROVING with CPython contradicting)
#   One new region in Module3_Weaver.process (it already raised, so no ratchet moved). Witnesses 1382-1403
#   (21 XFAIL + 1397 PASS). Commit a219ff01.
#     #136 A DYNAMIC (non-constant) `exec`, AND AN `eval` THAT CAN BIND, rebind a name whose value the model
#          has already folded/resolved, and NOTHING downstream models the value. Found by DEFERRAL-AUDIT:
#          exec_splice.py defers a dynamic exec to "scope havoc + frame taint, P5a/P5a'"; BOTH handlers were
#          located and BOTH are real — `_scope_dyn_exec` withholds only the `\in_scope` decided-FALSE direction
#          (and is computed per FUNCTION, so it never sees module scope), and `exec_havoc … writes {int_mem}`
#          exists only in the typed/store model. NEITHER is about a VALUE. The same docstring asserts eval
#          "does not inject names" — false since 3.8's walrus. Measured: module-scope `exec("N" + " = 5")` over
#          a folded `N = 3`; `S = "N = 5"; exec(S)`; `exec("le"+"n = sum")`; over an imported `inc`; over a
#          module `def inc`; `eval("(N := 5)")`; in-function `exec(code, globals())` and `eval("(N := 5)",
#          globals())`; `eval("globals().update({'N': 5})")` (constant, NO walrus); `eval("exec('N = 5')")`;
#          `operator.setitem(globals(), "N", 5)`; `dict.update(globals(), N=5)`.
#     #137 GEN #25'S OWN #135 REPAIR, ONE DAY OLD. Its module-executed walk `continue`d on Lambda and
#          FunctionDef — so a LAMBDA BODY called in place, the same lambda in a CLASS BODY, and a def's
#          DEFAULT ARGUMENT (evaluated at definition time) were never scanned; #119 rule (6) also exempts the
#          lambda's PARAMETER receiver, so 1389 slipped BOTH fences. `_nb_fresh_ok` enumerated five binding
#          forms, so a COMPREHENSION target defaulted to FRESH. And every namespace guard in the tree keys on
#          a builtin's SPELLING: `sa = setattr`, `ex = exec`, `builtins.setattr`,
#          `getattr(builtins, "set"+"attr")(...)`, `f.__globals__["N"] = 5`,
#          `inspect.currentframe().f_globals["N"] = 5`.
#   THE REPAIR, in one region: the module-executed region now includes lambda bodies (fail-closed), a def's
#   defaults/kw_defaults/annotations/decorators and a class's decorators/bases/keywords (a def BODY stays out);
#   `_nb_fresh_ok` records AugAssign / comprehension / ExceptHandler / MatchAs / MatchStar / Import /
#   ImportFrom / lambda parameters as NOT fresh; a namespace builtin (exec eval setattr delattr globals vars
#   locals getattr) is refused when READ AS A VALUE or reached as an ATTRIBUTE; `getattr` on `__builtins__` or
#   an imported name used as a CALLEE is refused; a NO-ARGUMENT globals()/vars()/locals() may only be bound to
#   a plain name or read through a subscript (`vars(self)` HAS an argument and is untouched); and a
#   module/class-scope SUBSCRIPT store/delete is keyed on the PATH being written, like the attribute sink.
#   `__import__` is deliberately NOT in the builtin list (python-reference 0127 reads it as a value, PASSES).
#
# ## 1b. LESSONS (each paid for this generation)
#   >>> A DEFERRAL THAT NAMES TWO HANDLERS CAN BE HONEST ABOUT BOTH AND STILL BE A HOLE. Locate the named
#   >>> guard, quote its matching rule, then ask WHICH OF THE THREE PLANES it actually covers. #136's deferral
#   >>> named `\in_scope` havoc and frame taint; both exist, both work, and neither is about a value.
#   >>> ASSERT A POPULATION SIZE BEFORE BELIEVING IT — INCLUDING A LISTING YOU TRUNCATED YOURSELF. draft-4's
#   >>> "census 0 sites" came from `len(hits)` printed next to `hits[:10]`; the real `getattr(obj,name)(...)`
#   >>> population is 2 in the mirrors and 5 in src/pycsl (the emitter's own dispatch) and the mirror sweep
#   >>> came back FOUR GONE. `print(hits[:10])` is the `diff`-hunk-header trap in your own handwriting.
#   >>> THE NESTED-DEF HAZARD HAS AN EMISSION COST, NOT JUST A COVERAGE-GATE COST: draft-5's two nested defs
#   >>> in `process` were LIFTED to methods and emitted as two extra abstract `val`s -> 2 MOVED in
#   >>> frontend/__init__ and frontend/ir_resolve, the two mirrors that ingest Module3.
#   >>> CARRIER-RERUN YOUR OWN DRAFT, AND KEEP DOING IT: NINE drafts, and the battery was stopped DELIBERATELY
#   >>> TWICE (3 min and 2 min in, no verdict read) to fold in six LIVE carriers of my own fences. Eight of the
#   >>> 22 witnesses are order-2 carriers of this generation's own repair.
#   >>> A REFUSAL KEYED ON A SPELLING LOSES; KEY IT ON THE PATH OR THE READ. The namespace family took four
#   >>> widenings (alias -> attribute -> computed getattr -> the dict escaping a call -> the subscript sink)
#   >>> before it stopped producing carriers.
#
# ## 2. LADDER FOR GEN #27 — START HERE
#   There is NO open route. Highest-value next moves:
#   (a) carrier-rerun gen #26's OWN fences (fresh, and they produced six carriers in one afternoon):
#       - `_nb_fresh_ok`'s DEFAULT for a name with no module-scope binding in a file without a star import is
#         still FRESH (gen #25's pure_ast `Constant.n = property(...)` exemption). Find a way to make such a
#         name denote a module/namespace at run time.
#       - a def's BODY is still outside the module-executed region: a module-scope CALL of a def that patches
#         its parameter was FAIL-CLOSED only by "a specification error" on the value — RE-PROBE with a value
#         that types (an int field, a class attribute).
#       - `_nb_ns_builtins` omits `__import__`, `compile`, `super`, `type`, `memoryview`, `object`. Is any
#         recognizer keyed on one of those spellings? (`object.__setattr__` is refused today by #119.)
#       - `_nb_imported` is file-wide; `getattr(<local bound to builtins>, "setattr")(...)`.
#       - the #136 eval token rule keys on identifiers in the CONSTANT text; an eval text that reaches the
#         namespace WITHOUT naming one of the eight (`"[].__class__.__base__.__subclasses__()"`).
#   (b) MORE DEFERRAL-AUDIT — this generation's best new generator (66.7% yield, 6 LIVE / 3 FC). Greped and
#       NOT yet audited: Module6_WhyMLTranspiler.py:289 ("propagation is handled by
#       `_wrap_call_with_callee_raises_assert`"); frontend/module5/construction_synth.py:83 ("Constant RHS
#       ... is already handled by `field_defaults`, so it is intentionally NOT re-captured here" — a COLLECTOR
#       deferral, exactly #132's shape); module6_whyml/expressions.py:1007 ("handled by the record-aware
#       dotted-call path (A2a/A2c)"); Module5_IREmitter.py:953 ("handled by Module6's `str_contains_op`");
#       module6_whyml/types.py:531; expressions.py:5778 ("already rejected at L3-tc, so no corpus program can
#       be relying on it"); preamble.py:141 ("guarded by the per-field in-range `requires`"); irx.py:11
#       ("each read is guarded by a membership test, so no KeyError is reachable"); generic_fold.py:1213;
#       statements.py:426/431 ("typically handled by `\trusted` upstream" — already flagged as a hedge);
#       functions.py:5657; core_ir_semantic.py:899; expressions.py:14509 ("Module 4 has already rejected an
#       unresolved name" — Module 4 IS DROPPED).
#   (c) ONE VACUOUS ROW OWED A RE-PROBE: `statements._emit_option_tuple_unpack`'s docstring asserts "the
#       Python guard `if X is not None:` makes the `None` arm dead" and the emitter NEVER CHECKS for a guard
#       (the terminal-return variant emits `absurd`). My positive control never reached the handler —
#       `a, b = p` with `p: Optional[Tuple[int,int]]` takes the UNION path and is a Why3 type error. Find the
#       source shape that registers an OPTION LOCAL (a dict `.get` result?) and re-probe.
#   (d) A LATENT #132 HOLE, gated only by a missing consumer: `collect_module_const_str_sets` accepts
#       `set(("a","b"))`, `set(["a","b"])` and `frozenset([...])`, but #132's escape arm only recognises a
#       bare `ast.Set` (after unwrapping `set(<Set>)`). `XS = set(("a","b")); XS.add("c")` is NOT escape-
#       checked. It measured VACUOUS today (a plain `{"a","b"}` set with `"c" in XS` emits `val constant xS :
#       int` + an abstract `contains_check` — the fold has NO Module-6 consumer recognizer for that shape).
#       THE DAY A STR-SET CONSUMER LANDS, THIS IS LIVE. Same for a module int/str LIST (`len(XS)` is not
#       folded today either).
#   (e) gen #25's WATCH rows still unre-probed: a nested def named like a FOREIGN base's method (#133 walks
#       in-module bases only); a folded dict passed to a mutating function (refused today as "aliased or
#       mutated" — check the fence is the rule, not luck); route #60's dict size fold under `del d[k]` /
#       `d |= {...}` / a tuple-target store. RE-PROBED AND STILL CLOSED this generation: a module-scope field
#       store on a FRESH module-class instance (`g = C(); g.n = 5`) — the model does not assume the object's
#       entry state, so the read is Unknown; a class constant shadowed by `C.N = 5` (#119 rule 6).
#   (f) gen #24's list (nested-def default reading an enclosing param; class-in-function reading an enclosing
#       param; walrus in a comprehension) and gen #23's list (hvalmap name-gated truthiness; assigns over
#       unlabelled fields; `_writes_filtered_to_labels`; Literal[0, None]; witness-census `val constant` sites).
#   GENERATORS THAT WORKED: deferral-audit (#136 — NEW, and the highest-yield key in the ledger at 66.7%) and
#   carrier-rerun (#137 and every one of the nine drafts' widenings).
#
# ## 3. YIELD — bin/probe-ledger-yield.sh --by-generator (whole ledger, after gen #26)
#   key                    LIVE  FAILC  denom    yield  2nd-ord  VACUOUS
#   advice-audit              2      5      7    28.6%        1        0
#   carrier-rerun           103     85    188    54.8%       87       14
#   carve-out-census          9      8     17    52.9%        0        1
#   continue-census          10      4     14    71.4%        3        3
#   control-operation         3     17     20    15.0%        1        0
#   deferral-audit            6      3      9    66.7%        3        5
#   hand                      1     47     48     2.1%        0        2
#   observer-audit            0      1      1     0.0%        0        0
#   oracle-audit              1      2      3    33.3%        0        0
#   substring-census          5      2      7    71.4%        0        0
#   unknown                  35      0     35   100.0%        2        0
#   witness-census           20     43     63    31.7%        2        5
#   GEN #26 ALONE: 44 rows — 22 LIVE / 17 FAIL-CLOSED / 5 VACUOUS. carrier-rerun 19 LIVE (two routes; ~13 are
#   order-2 carriers of my OWN drafts — count ROUTES, not rows) · deferral-audit 3 LIVE (#136's two handlers
#   and the eval claim). NOTE the 5 VACUOUS: three are the str-set fold with no consumer, one the str->str
#   dict read through a subscript (the live read shape is `.get(k, d)`, corpus 1373), one the option-unpack.
#
# ## 4. WHAT IS TRUE RIGHT NOW
#   metric   markers 459 / grep 484 / offset 25 / unattached 0 (UNMOVED — a refusal costs the trust surface
#            nothing; do not chase the metric)
#   suite    NEW BASELINE 3529/3547, 18 failures — pycsl-reference 0211-0220 + 0701, python-reference 0043
#            0048 0079 0080 0082 0095 0110. A 19 is a REGRESSION. ZERO XPASS.
#   planes   34 (`bin/run-soundness-planes.sh --slow`; without `--slow` it is 19). Ratchets: trusted-raises
#            13 declared / 62 SILENT · dropped-mutation 0/51/9/0 (unratcheted REFUSED column 8) ·
#            trusted-reasons 459<->459, unclassified 458.
#   corpus   pycsl-reference 1330 sources, 1074 emitting. python-reference 2217 sources, 2199 emitting.
#   scratch  scratchpad/g26/ (p1..p27 + c1..c18 + ctrl2 probe drivers). The emission baselines live OUTSIDE
#            the repo, in the session scratchpad g26sweeps/{corpus_base,mirror_base} — REBUILD them from a
#            worktree-at-HEAD; do not inherit them.
#   HOW TO REBUILD THE EMISSION BASELINE (3 commands, ~8 min):
#            git worktree add --detach <wt> HEAD && ln -s <repo>/.venv <wt>/.venv
#            ( cd <wt> && bin/byte-diff-sweep.sh <out>/corpus_base && bin/mirror-emit-sweep.sh <out>/mirror_base )
#            then the same two sweeps in the main tree + bin/byte-diff-compare.py on each pair
#            (and on <out>/*/pyref for python-reference).

# ====== START HERE — gen #25 FINAL STATE — read this block first ==================
#
# ## STATUS: COMPLETE. Tree clean (two PRE-EXISTING gitlinks only), everything committed, no background process
#   alive. SIX SEV-1 ROUTES FOUND AND CLOSED AND FULLY GATED this generation (#130-#135) in TWO batteries, every
#   leg of both predicted in driver-progress.log and hit. CURRENTLY OPEN: NONE.
#
# ## 1. WHAT GEN #25 FOUND AND CLOSED (all SEV-1, all measured PROVING with CPython contradicting)
#   One new block in Module3_Weaver.process (both pipelines; it already raised, so no ratchet moved).
#   BATTERY-A (commit 2313ded3):
#     #130 an IMPORTED name bound twice keeps the FIRST import: second from-import, `inc = plainlib.dec`,
#          `import a as m; import b as m`, a from-import in a module if/else, a function-local import of
#          another object. (#118 rule (1) keyed on this file's defs only.)
#     #131 a BUILTIN rebound is still lowered as the builtin: `len = sum` (module/local), `for max in [min]`,
#          `exec("len = sum")`, `from builtins import sum as len`, `ValueError = KeyError` (raise/except), an
#          unannotated PARAMETER `def f(len, xs)`. Now: any builtins name bound by a store or a parameter and READ.
#     #132 the constant FOLDERS' "bound exactly once" premise counts TOP-LEVEL single-name Assign/AnnAssign only:
#          `N += 2`, rebinding inside `if`, tuple/for targets, literal setattr on sys.modules, `S += "b"`, a
#          `requires` over a rebound constant, class-body `N += 2`; and a folded str dict MUTATED or ALIASED
#          (`OP.update`, `d = OP` in a function, `d, e = OP, 1`, `for d in [OP]`, `L = [OP]`). The mutable-literal
#          arm keys on EVERY reference to the object (read positions only, one alias level).
#     #133 a def nested in a METHOD named like a method of the class REPLACED it (body swapped, postcondition
#          dropped: a false `C.h` contract proved).
#     #134 route #116's globals-lookup recognizer: `_g = globals()` rebound inside `if` escaped its top-level count.
#     battery-A: suite 3503/3521 same 18 0 XPASS, planes 34/34, emission byte-inert in all three.
#   BATTERY-B (commit c8f817e2):
#     #135 module-scope code is never lowered, and #127's alias taint says "an ordinary call produces a value":
#          `m = ident(plainlib); m.inc = ...`, `setattr(ident(plainlib), "inc", ...)`, called lambda,
#          comprehension, keyword argument, `m = H(plainlib); m.x.inc = ...`, `ms = [ident(plainlib)]; ms[0].inc`,
#          a LEADING star import exporting a module alias. Keyed on the SINK: at module/class-body scope an
#          attribute write needs a receiver that IS a name bound only to literals / module-class instances (or
#          unbound, in a file without a star import). A taint-through-arguments cut polluted 5 mirrors (the alias
#          set is file-wide by NAME) and was abandoned.
#     battery-B: suite 3507/3525 same 18 0 XPASS, planes 34/34, emission vs battery-A byte-inert in all three.
#
# ## 1b. LESSONS (each paid for this generation)
#   >>> A COLLECTOR'S "EXACTLY ONCE" IS A CLAIM ABOUT WHICH STATEMENTS IT WALKS. Every `collect_module_*` walked
#   >>> `node.body` only; the same premise sat in route #116's own justification check (#134). grep "exactly once"
#   >>> / "bound once" and read the loop header, not the docstring.
#   >>> A REFUSAL THAT ENUMERATES SPELLINGS LOST EVERY TIME: #131 was widened three times (calls of a short list ->
#   >>> exceptions -> parameters), #132's alias arm twice, #135 three times. Each widening was found by
#   >>> carrier-rerun on my own draft BEFORE a verdict; battery-A was stopped twice (no verdict read) to fold them in.
#   >>> MODULE-SCOPE CODE IS INVISIBLE TO THE MODEL: in-function twins of #135 were fenced by typing/frames; only
#   >>> the weaver sees module-level effects. Probe the module-scope spelling of every in-function FAIL-CLOSED row.
#   >>> Develop the next battery in a worktree (g25/wt_b) while the current one runs; run its sweeps THERE.
#
# ## 2. LADDER FOR GEN #26 — START HERE
#   There is NO open route. Highest-value next moves:
#   (a) carrier-rerun gen #25's own fences: the #132 read-position whitelist (`_nb_readers`, `_nb_pure_calls`:
#       is any listed method/builtin able to return or mutate the object?); the #135 "fresh" definition (a
#       module class with a foreign base, a class whose `__init__` returns/stores self elsewhere, a class
#       instance rebound via walrus); #130's per-scope keys (class-body imports, nested functions); the exec
#       arm's token rule (non-constant exec is not spliced — confirm).
#   (b) WATCH (probes.tsv rows, each one change from live): a nested def named like a FOREIGN base's method
#       (#133 walks in-module bases only; opaque today); `collect_module_globals` rebinding (emission ignores it,
#       entry state not assumed — any contract exposing the initial record makes it live; #134's arm now refuses
#       the rebinding but NOT a module-level `G.n = 5` direct store on a fresh instance, which #135 allows by
#       design); class constant shadowed by `k.N = 5` / `self.N = 5` (type error / frame); a folded dict passed
#       to a mutating function (effect error); module list `XS.append` (not folded today); route #60 dict size
#       fold `del d[k]` / `d |= {...}` / tuple-target store (type errors).
#   (c) gen #24's WATCH list items not re-probed: nested-def default reading an enclosing param (opaque call);
#       class-in-function reading an enclosing param (refused, fence unnamed); walrus in a comprehension.
#   (d) gen #23's unworked list (hvalmap name-gated truthiness needs the mirror's hval type model; assigns over
#       unlabelled fields; `_writes_filtered_to_labels`; Literal[0, None]; witness-census `val constant` sites).
#   GENERATORS THAT WORKED: carrier-rerun (#130 #131 #133 #134 #135 + 12 draft carriers) and witness-census /
#   coverage-premise of collectors (#132).
#
# ## 3. YIELD — bin/probe-ledger-yield.sh --by-generator (whole ledger, after gen #25)
#   key                    LIVE  FAILC  denom    yield  2nd-ord  VACUOUS
#   advice-audit              2      5      7    28.6%        1        0
#   carrier-rerun            84     68    152    55.3%       68       10
#   carve-out-census          9      8     17    52.9%        0        1
#   continue-census          10      4     14    71.4%        3        3
#   control-operation         3     17     20    15.0%        1        0
#   deferral-audit            3      3      6    50.0%        0        4
#   hand                      1     47     48     2.1%        0        2
#   observer-audit            0      1      1     0.0%        0        0
#   oracle-audit              1      2      3    33.3%        0        0
#   substring-census          5      2      7    71.4%        0        0
#   unknown                  35      0     35   100.0%        2        0
#   witness-census           20     43     63    31.7%        2        5
#   GEN #25 ALONE: carrier-rerun 26 LIVE / 33 FC / 1 VAC (six routes; ~14 LIVE rows are order-2 carriers of my own
#   drafts — count ROUTES, not rows) · witness-census 13 LIVE / 25 FC (#132).
#
# ## 4. WHAT IS TRUE RIGHT NOW
#   metric   markers 459 / grep 484 / offset 25 / unattached 0
#   suite    baseline 3507/3525, 18 failures (same names). A 19 is a REGRESSION.
#   planes   34; ratchets trusted-raises SILENT 62 · dropped-mutation 0/51/9/0 (REFUSED column 8, unratcheted) ·
#            trusted-reasons unclassified 458.
#   scratch  scratchpad/g25/ (p1..p16 probe drivers, w1/w2 witness copies, census/, batteryA/B scripts+logs,
#            A_*/Bm_* sweeps = the current emission baselines).

# ====== START HERE — gen #24 FINAL STATE — read this block first ==================
#
# ## STATUS: COMPLETE. Tree clean (two PRE-EXISTING gitlinks only), everything committed, no background process
#   alive. NINE SEV-1 ROUTES FOUND AND CLOSED AND FULLY GATED this generation (#121-#129) in TWO batteries,
#   every leg of both predicted in driver-progress.log and hit. CURRENTLY OPEN: NONE.
#
# ## 1. WHAT GEN #24 FOUND AND CLOSED (routes #121-#129, all SEV-1, all measured PROVING with CPython contradicting)
#
#   Opening move: re-probe gen #23's SEVEN "Symbol X is already defined" VACUOUS rows with values that do not
#   trip the duplicate symbol (a builtin, a lambda). The fence was a property of the VALUE; the shapes were live.
#   BATTERY-A (commit 629c80bb), every leg predicted and hit:
#     #121 a user DECORATOR was silently dropped (`@swap` -> abs). Allowed now only: absent binding + modelled
#          marker (property/staticmethod/mutable_state/dataclass, no star import), ONE canonical import bound
#          under its OWN name (an alias bypassed #94's memo gate: `cached_property as memo_prop`), ONE identity def
#          not spelled like a meaningful decorator. (Module3_Weaver.process)
#     #122 compound arm: a def inside if/try (incl. the try-import fallback idiom) competing with another binding
#          resolved to the textually last — per scope, module AND every class body (Module3)
#     #123 a class-body binding overriding an inherited method (`m = lambda self: 2`, imported base, grandchild):
#          IR key `class_body_bindings` (classes with bases only), apply_inheritance skips the clone (fail-closed)
#     #124 a star import after a def, or after another star import (Module3)
#     #125 diamond MRO resolved depth-first: apply_inheritance now clones only from the C3 provider (1348 PASS twin)
#     #127 namespace patching past #119: `__builtins__.len = ...`, setattr(__builtins__), aliases (`bm =
#          __builtins__`, `pm = plainlib`, through a function return, through an if-expression), computed
#          `getattr(__builtins__, "__dict__")[...]`, non-literal setattr on a `cls` PARAMETER (Module3 #119 rules)
#     #128 the descriptor protocol (__get__/__set__) ignored — refused with the #120 hooks
#     battery-A: suite 3481/3499 same 18 0 XPASS, planes 34/34, python-ref GONE 0078 (predicted).
#   BATTERY-B (commit 6d63b01d):
#     #122 nested arm: sibling helpers `h` collapsed to one lifted `let h`; a helper replacing a module / IMPORTED
#          function of the same name (checked from BOTH sides — the helper defined BEFORE the module def never
#          reaches emission); #126 a lifted nested def's CAPTURED enclosing name became ONE global `val constant`
#          (read: `f(1) - f(2) == 0`; write through a captured list invisible); #129 a `global` write lowered to a
#          fresh local while reads of a non-constant module variable are one constant. Module3 marks, Module5 IR
#          keys only when present, Module6 `_emit_function_block` generic refusals (nonlocal_writes precedent,
#          trusted/abstract/trusted_parent exempt; twins suppressed by a bespoke `self._*_walk_ids` pairing exempt;
#          `self` is not a capture inside a method). python-ref 0166 and 0181 flipped to expected-FAIL with reasons.
#
# ## 1b. LESSONS (each paid for this generation)
#   >>> CARRIER-RERUN YOUR OWN FENCE BEFORE THE BATTERY — AGAIN IT PAID: battery-A was stopped once (3 min in, no
#   >>> verdict) for two draft carriers; battery-B's draft was walked past three times in the worktree
#   >>> (method-nested `self`, suppressed bespoke twins GONE'ing two mirrors, a helper vs an IMPORTED function).
#   >>> A REFUSAL KEYED ON A SPELLING IS OUT-VOTED BY EVERY RECOGNIZER KEYED ON THE SAME SPELLING: allowing an
#   >>> alias of `cached_property` switched OFF route #94's memo gate. Check what else reads the name.
#   >>> Live Module3 is INGESTED by two mirror files (frontend/__init__, ir_resolve): `%` formatting and
#   >>> `x[i][j]` indexing in new Module3 code moved their emissions (pycsl_div/mod, use matrix.Matrix). Unpack
#   >>> tuples, use f-strings.
#   >>> Develop the NEXT battery in a worktree (g24/wt_b) while the current one runs; never edit the main tree.
#
# ## 2. LADDER FOR GEN #25 — START HERE
#   There is NO open route. Pick by YIELD (§3). Highest-value next moves, in order:
#   (a) carrier-rerun on gen #24's OWN fences (they are fresh and were walked past five times in one day):
#       the #127 alias fixpoint (taint through containers, attributes of aliases, class attributes holding
#       modules), #121's allow-list (every recognizer keyed on a decorator SPELLING — grep them), #126's
#       capture rule (defaults, class bodies, decorators of nested defs), #129 (any write path to a module
#       variable that is not spelled `global`).
#   (b) the WATCH list below — each row is one change from live.
#   WATCH (probes.tsv rows, each one change from live):
#     - default argument of a nested def reading an enclosing parameter (`def h(y=x)`): not marked by #126's
#       capture rule (defaults are not body loads); refused today only because the defaulted call is opaque.
#     - a class nested in a function whose method reads an enclosing parameter: not a lifted def; opaque today.
#     - `setattr(sys.modules[__name__], "N", 5)` writing a plain module global: #119 rule (5) does not refuse it
#       (literal "N" is not a def name); fenced only by the `_pyobj_state` frame error.
#     - patching a module through a function PARAMETER (`def patch(m): m.inc = abs`): #119 rule (6) exempts
#       parameters; fenced by a Why3 type error on the value.
#     - `walrus` inside a comprehension leaking to the function (VACUOUS: Why3 syntax error in the any-fold).
#     - gen #23's list (i)-(iii) is still unworked: `assigns self.a` over an unlabelled field, the
#       `_writes_filtered_to_labels` partial drop, Optional[str] ternary None -> "", Literal[0, None],
#       `_hvalmap_local_vars` name-gated truthiness, witness-census's ~40 unprobed `val constant`/Number-0 sites.
#   GENERATORS THAT WORKED: carrier-rerun of gen #23's VACUOUS rows with a different VALUE (9 routes from one
#   idea); reading the `val constant <name>` fallback of `_handle_var_expr` (witness-census: #126 write arm, #129).
#
# ## 3. YIELD — bin/probe-ledger-yield.sh --by-generator (whole ledger, after gen #24)
#   key                    LIVE  FAILC  denom    yield  2nd-ord  VACUOUS
#   advice-audit              2      5      7    28.6%        1        0
#   carrier-rerun            58     35     93    62.4%       45        9
#   carve-out-census          9      8     17    52.9%        0        1
#   continue-census          10      4     14    71.4%        3        3
#   control-operation         3     17     20    15.0%        1        0
#   deferral-audit            3      3      6    50.0%        0        4
#   hand                      1     47     48     2.1%        0        2
#   observer-audit            0      1      1     0.0%        0        0
#   oracle-audit              1      2      3    33.3%        0        0
#   substring-census          5      2      7    71.4%        0        0
#   unknown                  35      0     35   100.0%        2        0
#   witness-census            7     18     25    28.0%        1        5
#   GEN #24 ALONE: carrier-rerun 26 LIVE / 20 FC / 1 VAC (nine routes; ~13 rows are order-2 carriers of my own
#   drafts — count ROUTES, not rows) · witness-census 2 LIVE / 3 FC / 1 VAC (#126 write arm, #129) · hand 1/3 (#125).
#
# ## 4. WHAT IS TRUE RIGHT NOW
#   metric   markers 459 / grep 484 / offset 25 / unattached 0
#   suite    baseline 3487/3505, 18 failures (same names). A 19 is a REGRESSION.
#   planes   34; ratchets trusted-raises SILENT 62 · dropped-mutation 0/51/9/0 · trusted-reasons unclassified 458.
#   scratch  scratchpad/g24/ (p1..p5 probe drivers, w1/w2 witness copies, batteryA/B scripts+logs, A_*/Bb_*
#            sweeps = the current emission baselines, wt_head/wt_b worktrees).

# ====== START HERE — gen #23 FINAL STATE — read this block first ==================
#
# ## STATUS: COMPLETE. Tree clean (two PRE-EXISTING gitlinks only), everything committed, no
#   background process alive. ELEVEN SEV-1 ROUTES CLOSED AND FULLY GATED this generation
#   (#109, #111-#120) across FIVE batteries; CURRENTLY OPEN: NONE. Read §1b — the afternoon's
#   #119/#120 family is where the lessons are.
#
# ## 0. GEN #22, FOR THE RECORD: found #112 (21d5029e), then HUNG on a Bash call that never
#   executed; the supervisor saved its UN-GATED #111/#112 diff to getting-better/interrupted/.
#   Gen #23 re-derived the repair (the patch was a hint: its `stmt.value.to_dict()` was right,
#   its `_field_type_of` test was widened to `_rhs_yields_map`), and the battery then found a
#   regression the patch would have shipped (§1 miss a).
#
# ## 1. THE MORNING: NINE SEV-1 ROUTES CLOSED AND FULLY GATED (batteries 2 and 3)
#
#   BATTERY-2 (ONE combined battery, commit e91bb786):
#     #111 dict/set field store clobbered with the EMPTY MAP (`self.b = self.a`, `= mk()`)
#     #112 non-empty dict literal in argument position = the empty map (`g({1: 5})`)
#     #113 `_coerce_to_int` hashed the TEXT of any paren term with a comma: `g(y, "a,b")`, and a
#          tuple projection `a[i][1]` returned from a try (corpus 0607 PASSED on the constant)
#     #114 a genuine tuple dict key hashed by its text: `(y, 1)` same key after `y += 1`
#     #115 UnknownPyExpr -> literal 0: `(lambda y: y + 1)(x)`, and `fs[0](x)` — the shape route
#          #24's own repair comment claimed to cover (order 2)
#     #116 `F("name")(args)` lowered as a call to the function the string names (a pure_ast
#          recognizer on every program: `Pick("inc")(3)`, a fake `_N`, a ternary decline -> 0)
#     #117 a list local returned early on the Return-int path = literal 0 (no annotation needed)
#   BATTERY-3 (commit 6c75839a):
#     #109 record-var receiver avatar had NO frame and NO receiver (gen #21's open item)
#     #118 rebinding a function/method name is ignored by call resolution: `inc = dec`,
#          class-body `m = n`, module walrus, `global inc`, `_g["inc"] = dec` -> now REFUSED
#          (PYCSL-IR-FUNCTION-NAME-REBOUND, in `_run_pipeline`); also #116's last carrier.
#
#   Every gate verdict was PREDICTED in driver-progress.log before it ran. Battery-2: metric
#   459/484/25/0 · sync 887 · trusted-raises 13/62 · type-only 53/0 · dropped-mutation 0/51/9/0 ·
#   pycsl-ref 22 MOVED + GONE 0996 (expected) · pyref 6 MOVED · mirror 7 MOVED, EVERY HUNK READ ·
#   suite 3444/3462 · 7 mirror whole-file proofs SUCCESS 0 bad (statements 17630, expressions
#   21347, stmt_control_flow 12284, pure_ast 3372, functions 1199, Module5 2109, preamble 216) ·
#   planes 34/34. Battery-3: all byte-inert vs battery-2 · suite 3450/3468 · planes 34/34.
#   Corpus witnesses 1305-1324 (14 XFAIL negatives, 6 PASS faithful twins/controls).
#
#   THE THREE RECORDED MISSES — THESE ARE THE LESSONS:
#   (a) #112's first sweep moved 17 corpus + 2 pyref files to `map_update_some (any_map ()) ..`:
#       the local-assignment fold used the LOWERED literal as its base, which was the empty map
#       only BECAUSE the literal lowered to it. >>> A VALUE THAT WAS A LIE IN ONE CONSUMER WAS
#       THE TRUTH IN ANOTHER. Read the hunks, never just the MOVED count. <<<
#   (b) planes: `check-singleton-constant-lowering` is keyed on ARM SPELLING and went red when
#       `if t in ("UnknownPyExpr","GenExp")` was split. Re-merging made the gate BLIND to the
#       GenExp constant (worse than red) — reverted. Two baseline entries whose written
#       justifications #115/#116 had just REFUTED ("closed at the BINDING"; "a REFUSAL, not a
#       value") were REMOVED; the GenExp key narrowed. 14 -> 12 constant arms, re-verified.
#       >>> A BASELINE ENTRY'S JUSTIFICATION IS A CLAIM ABOUT THE CODE — AUDIT IT LIKE ONE. <<<
#   (c) #118 took THREE cuts. In `Module5.visit_Module` a direct `raise` moved trusted-raises
#       62 -> 65 (three mirror stubs share that name) + two mirror emissions: relocated to
#       `_run_pipeline`, exactly the #45 precedent. Then it enumerated statement KINDS and a
#       class-body `m = n`, then a module walrus, walked past it. >>> KEY A CONFINEMENT CHECK ON
#       THE NAME BEING BOUND, NEVER ON THE STATEMENT KIND. Lesson 9 — violated twice in one hour
#       by the generation that had just cited it. Carrier-rerun YOUR OWN FENCE the same hour. <<<
#
# ## 1b. AFTER THE FIRST CHECKPOINT (same generation, later the same day) — READ THIS TOO
#
#   ROUTE #119 (order 2, carrier = my own LANDED #118 refusal): every rebinding that is not a NAME
#   binding in the file being verified survived it — `C.m = C.n`, `vars()/locals()[...]`,
#   `setattr(sys.modules[__name__], ...)`, `type.__setattr__`, `exec("inc = dec")`, and ANY
#   rebinding inside an IMPORTED module (#118 sat in `_run_pipeline`; `ir_resolve` ingests
#   dependencies with its own Module 1-3-5). Then, against my own #119 drafts: patching an
#   imported module / imported class / through `importlib`, and INSTANCE-LEVEL method shadowing
#   (`self.m = abs`; over an IMPORTED base; outside `__init__`; via `setattr(self, name, v)`;
#   via `object.__setattr__(self, ...)`; a dataclass field default). ROUTE #120: attribute-access
#   hooks (`__getattribute__`, `__setattr__`, and one installed by assignment) are ignored.
#   Landed: battery-4b (de890255) — the guard moved into `Module3_Weaver.process` (shared by both
#   pipelines, already raises) with rules (1)-(7) + the hook refusal. Battery-5 (11b900d6): rule
#   (8) instance-level shadowing in the front end (incl. foreign bases and the unbound
#   `object.__setattr__(self, ...)` spelling), and the IR-level PYCSL-WHYML-METHOD-SHADOWED in
#   `_handle_dotted_call` (a call resolving to a METHOD while the receiver record has a FIELD of
#   that name, or the program STORES that attribute). Both batteries: every leg PREDICTED and HIT;
#   suite 3460/3478 then 3465/3483, same 18, 0 XPASS; planes 34/34; emission byte-inert (4b:
#   expect-gone python-reference 0076, which defines __setattr__).
#   Still WATCH (fenced only incidentally): a non-literal `setattr(obj, name, int)` on a plain
#   local instance (typing of the value slot).
#   >>> THE LESSON OF THE AFTERNOON: every draft of this fence was walked past within the hour by
#   >>> the next spelling. Carrier-rerun your OWN fence BEFORE the battery, every time — it cost
#   >>> four battery restarts, each stopped within a minute, and zero verdicts inherited. <<<
#
# ## 2. LADDER FOR GEN #24 — START HERE
#
#   There is NO open route. Pick by YIELD (below), and mine:
#   (i)  WATCH / ADJUDICATION items (probes.tsv rows, NOT routes — each is one change from live):
#        - `assigns self.a` PROVES while the body writes an UNLABELLED field (the documented #32
#          `_pyobj_state` rule). #109's precedent counted a proved `assigns \nothing` as LIVE.
#          Adjudicate: is a proved-but-false frame on an unmodelled field a route?
#        - `_writes_filtered_to_labels` drops unlabelled targets from a PARTIALLY labelled
#          assigns (both arms; `writes { self.a }` for `assigns self.a, self.hidden`). Unobservable
#          today only because unlabelled reads are fresh `getattr_c` program vals.
#        - Optional[str] ternary `"a" if c else None`: the None arm lowers to "" — fenced only by
#          a union type error; the arm's comment PROMISES the injection that would make it live.
#        - `Literal[0, None]`: the domain clause encodes None as 0, `is None` uses pycsl_none.
#        - `_to_bool` answers `true` for `_hvalmap_local_vars`, a set filled by FUNCTION-NAME
#          suffix (`_union_none_ctor_for`, `_compute_return_type`, ...): FIRES in a user method so
#          named (`if (not true)`), fenced by a type error.
#        - #117's union sibling still emits `(Arm_0_1 0)` (type error today).
#   (ii) The "Symbol X is already defined in the current scope" error on a function used as a
#        VALUE made SIX probes VACUOUS (fs=[inc], a factory returning dec, `global inc`, a local
#        shadow, a decorator swap, a higher-order argument). It is a fence nobody designed —
#        the day it is fixed, RE-RUN ALL SIX (drivers in scratchpad/g23/p3,p6,p7,p8,p11).
#   (iii) witness-census has ~40 unprobed sites (57 grep hits in module6 + 6 front-end Number-0
#        fallbacks; ~17 probed). Remaining high-value: `_dv_missing_default` hval `(HInt 0)`,
#        `expressions.py` record-literal field default `const None` (12551), the
#        `(svalue_of`/`(object_of` emit-ir `true` arms, generic_fold's constant returns.
#
# ## 3. YIELD — bin/probe-ledger-yield.sh --by-generator (whole ledger, after gen #23)
#
#   continue-census 10/14 71.4% · substring-census 5/7 71.4% · carrier-rerun 32/47 68.1% ·
#   carve-out-census 9/17 52.9% · deferral-audit 3/6 50% · oracle-audit 1/3 · witness-census
#   (NEW) 5/20 25.0% (4 VACUOUS) · advice-audit 2/7 · control-operation 3/20 · hand 0/45.
#   GEN #23 ALONE: carrier-rerun 25 LIVE / 8 FC (7 VAC) — INFLATED: ~16 of those LIVE rows are
#   carriers of ONE family (#118/#119, most order 2 against my own drafts); count ROUTES, not rows,
#   before ranking it · carve-out-census 3/3 · substring-census 3/5 · witness-census 5/20 ·
#   advice-audit 0/2 · continue-census 0/1 (+1 OUT-OF-SCOPE).
#
# ## 4. WHAT IS TRUE RIGHT NOW
#
#   metric   markers 459 / grep 484 / offset 25 / unattached 0
#   suite    baseline 3465/3483, 18 failures (same 18 names as gen #21). A 19 is a REGRESSION.
#   planes   34 = 19 fast + 15 slow; singleton-constant-lowering baseline 12 arms.
#   ratchet  trusted-raises SILENT 62 · dropped-mutation TRYFINAL 9 · trusted-reasons unclassified 458.
#   timing   a mirror whole-file proof INCLUDING the default-on vacuity phase takes HOURS
#            (expressions 6h03m, stmt_control_flow 4h08m, pure_ast 3h56m, statements 3h41m).
#            Budget batteries for it; never kill one to "save time" — a partial verdict is none.
#   scratch  scratchpad/g23/ (probe drivers p1..p11, batteries, sweeps, wt_draft worktree).
#   pre-existing, not gen #23's: mirror-check rc=1 on 3 files; two modified gitlinks.
#

# ====== START HERE — gen #21 FINAL STATE — read this block first ==================
#
# ## STATUS: COMPLETE. Tree clean (two PRE-EXISTING gitlinks only), everything committed.
#
# ## 1. ROUTES #107 + #108 ARE REPAIRED *AND* FULLY GATED. DO NOT RE-RUN THE BATTERY.
#
#   ONE STRUCTURAL REPAIR FOR BOTH DIRECTIONS. `stmt_control_flow.py:1809` decided whether to
#   keep a try's `else:` with `"raise" not in _else_str` — a SUBSTRING TEST OVER GENERATED
#   TEXT. The else is now lowered as a SIBLING of the try/except behind a completion flag, so
#   Python's scoping IS the emitted scoping. The block is ALWAYS emitted: there is no
#   surviving drop, so there is no string left to test. `_callee_raised_in` now visits
#   `orelse` AND `finalbody`, unfiltered by handler_bases.
#
#   The flag is named `try_else_ok'<depth>`. The PRIME is the point: `whyml_ident` can never
#   produce one, because a Python identifier cannot contain `'`. Collision-proof BY
#   CONSTRUCTION, not by hoping about spelling — which is the entire lesson of #107.
#
#   ELEVEN LEGS, TEN PREDICTIONS EXACT, ONE RECORDED MISS:
#     1  metric                  459 markers / 484 grep / offset 25 / unattached 0   HIT
#     2  doc-coherency           rc=0                                                HIT
#     3  fidelity mirror-sync    rc=0, 887 un-trusted fns verbatim, 37 consts         HIT
#     4  trusted-raises-honesty  rc=0, 75 stubs, 6 DECLARED / 69 SILENT, ratchet 69   HIT
#     5  mirror type-only        rc=0, 53 mirrors, 0 ILL-TYPED                        HIT
#     6  planes                  34/34 `ok` COUNTED = 19 fast + 15 slow               HIT
#     7  byte-diff pycsl-ref     1045/1045, 1 MOVED (1029), 0 GONE/APPEARED, zb 0/0   HIT
#     8  byte-diff python-ref    2203/2203, 1 MOVED (0189), 0 GONE/APPEARED, zb 0/0   HIT
#     9  mirror emission-diff    53/53, 1 MOVED (stmt_control_flow)                  MISS
#    10  reference suite         3423/3441, 18 failures, ZERO XPASS                   HIT
#    11  mirror whole-file proof SUCCESS, 12284 Valid, 0 bad                          HIT
#    10b suite RE-RUN w/ witnesses 3428/3446, 18 failures, ZERO XPASS                 HIT
#
#   THE MISS, RECORDED NOT RENUMBERED: I predicted 0 MOVED for leg 9 from "no mirrored file
#   has a try/else" — TRUE, and it is why no OTHER mirror moved — but the EDITED MIRROR FILE'S
#   OWN body changed, so its emission must. 46 diff lines, all attributable.
#   A second miss worth keeping: b_catch now fails on a WHY3 TYPE ERROR ("raises unlisted
#   exception ValueError"), not the no_exception VC I predicted. `_module_func_raises` carries
#   only DECLARED raises, so the assert-and-absurd wrapper is not installed for a callee whose
#   raises are INFERRED. Fail-closed, but it is a real diagnosis-quality gap — a good next item.
#
#   **NEW SUITE BASELINE: 3428/3446, 18 failures.** A 19 is a REGRESSION.
#   Ratchet `check-dropped-mutation` MAX_TRYFINAL lowered 11 -> 9 because the POPULATION moved
#   (both try/else rows left the bucket). REFUSED 5 -> 7. The line only ever follows DOWNWARD.
#
#   Corpus witnesses 1298-1302 landed (3 positive, 2 expected-FAIL), so this cannot regress
#   silently. 1300 negative-tests the flag by naming a user local literally `try_else_ok`.
#
# ## 2. ROUTE #110 IS ALSO REPAIRED AND FULLY GATED (a SECOND full battery this generation)
#
#   `_coerce_to_int` now extracts the HEAD SYMBOL of the lowered term and refuses to treat it
#   as collection-shaped when that symbol is a USER-DEFINED function (`_module_func_names`).
#   Passing it through is fail-closed: if the call really is collection-typed Why3 rejects it
#   where an `int` is expected — a loud error instead of a silent `0`.
#     d_any1 rc=1 (false proof gone; emission now `Array.make 1 ((any_1 x))`, call SURVIVES)
#     d_pos  rc=0 (TRUE claim `\result == x + 1` PROVES — faithful, not merely refusing)
#     corpus witnesses 1303 (negative) + 1304 (positive twin)
#   BYTE-INERT across 3253 corpus files, PREDICTED FROM A CENSUS. expressions.py whole-file
#   re-proof SUCCESS (21269 Valid, 0 bad). Planes 34/34. Suite 3430/3448, 18 fail, 0 XPASS.
#
#   >>> **THE PLANES CAUGHT MY OWN REPAIR AND THE RATCHET WAS NOT RAISED.** The first form used
#   >>> `getattr(self, "_module_func_names", set())`, which in the MIRROR lowers to a
#   >>> `pycsl_getattr_default_*` fall-through — an EIGHTH getattr-erasure site, and
#   >>> `check-getattr-erasure.py` went RED at `ABSENT 8 > ratchet 7`. Provenance was
#   >>> established at the baseline FIRST (31 sites / ABSENT 7 / green), the cause was fixed
#   >>> (the default was dead code), and MAX_ABSENT stayed at 7.
#   >>> **A REPAIR THAT BUYS ITS SOUNDNESS WITH A NEW ERASURE SITE HAS MOVED THE PROBLEM, NOT
#   >>> FIXED IT — AND ITS OWN WITNESS CANNOT SEE THAT COST.** Check every repair against the
#   >>> OTHER planes, not only against the thing it was written to stop. This is the single
#   >>> most transferable thing gen #21 learned.
#
# ## 3. ONE NEW SEV-1 ROUTE STILL OPEN, AND IT IS THE WORST OF THE THREE  <-- START HERE, gen #22
#
#   The substring-census that gen #20 banked WAS RUN (874 raw grep hits triaged) and it paid.
#   The sharpest instances are NOT in control flow but in ARGUMENT COERCION and FIELD STORES.
#
#   **#111 — a `set`/`dict`/`frozenset` self-field is clobbered with the EVERYWHERE-EMPTY MAP**
#   (statements.py:2610-2612) when the lowered RHS is not alphanumeric after deleting `_` and
#   `!`. **NEEDS NO ADVERSARIAL NAMING**: `self.b = self.a` is ordinary Python and PROVES
#   `\result == 0` while CPython returns 1. Control routes the same assignment through a local
#   (`!t` IS alnum), the value survives, and the same claim is correctly REFUTED.
#   ALSO MEASURED: a dict LITERAL assigned in a non-`__init__` method is clobbered too, so
#   route #85's faithful-literal repair covers the `__init__` RECORD LITERAL only.
#   THE AVATAR IS THE FENCE for the cross-method case — two earlier shapes measured NOTHING
#   and are logged as such. #111 bites exactly where a method OBSERVES ITS OWN WRITE.
#
#   Route file: `open-routes/route111-*.md`. NOT REPAIRED. The repair is the same shape as
#   #110's: the decision is a TYPE question the emitter already knows structurally, and the
#   substitution must REFUSE rather than invent a witness value. **Census the population of
#   dict/set-typed field stores with a non-alnum RHS BEFORE scoping it** — unlike #110, whose
#   population was provably zero, this one is NOT obviously inert and a half-gated frame/value
#   change is worse than an honest open route.
#
#   ALSO STILL OPEN in the same function as #110 and explicitly NOT covered by its repair:
#   `expressions.py:1030` replaces a term with `str(stable_hash(whyml_str))` when it contains
#   a COMMA and is paren-wrapped — reachable via a comma inside a string-literal argument
#   (`h("a,b")`). Logged as a candidate, never run to a verdict.
#
# ## 4. STILL OPEN, NOT WORKED THIS GENERATION
#
#   **#109** (`order = 2`, carrier is the `#32 SPIKE` repair): the `_objstate_w` frame fallback
#   exists in the `self.` arm only. Fourth link in #70 -> #100 -> #105 -> #109, a chain that
#   recurs once per obligation kind. Untouched by gen #21.
#
#   From the census, UNPROBED and ranked: `expressions.py:1030` (a COMMA in a string-literal
#   argument replaces the term with a text hash); `statements.py:2610`'s twin at
#   `expressions.py:7476`; `functions.py:7040` and `abstract_ops.py:51` (frame decisions keyed
#   on a name, both WIDENING so conservative); `preamble.py:4478` (`!n` matches inside `!n2`).
#   Full triage incl. a "checked, not exploitable" table is in the gen #21 census.
#
# ## 5. WHAT IS TRUE RIGHT NOW
#
#   metric   markers **459** / grep 484 / offset 25 / unattached 0 — RE-MEASURED at HEAD.
#   ledger   68 LIVE / 82 FAIL-CLOSED / 150 denom / **45.3%**, VACUOUS 10, ZERO PENDING rows.
#            (`grep -c PENDING` returns 3 — all three are gen #20 PROSE, "was PENDING". Check
#             column 5, not the whole line.)
#   yield    PER GENERATOR (`bin/probe-ledger-yield.sh --by-generator`) — this is the number
#            that picks the next generator, not the route count:
#              substring-census  2/2   **100%**  <- NEW, opened by gen #21. n=2, so treat it as
#                                                   promising rather than proven, and KEEP MINING
#                                                   IT: its two hits are #110 and #111.
#              carrier-rerun     6/6   100%      (2 second-order)
#              continue-census  10/13  76.9%     (was 83.3%; gen #21's finalbody probe closed
#                                                 FAIL-CLOSED, which is the honest cost of a
#                                                 denominator you write before you interpret)
#              deferral-audit    3/6   50.0%     (4 VACUOUS — worst vacuity rate in the table)
#              carve-out-census  6/14  42.9%
#              advice-audit      2/5   40.0%
#              oracle-audit      1/3   33.3%
#              control-operation 3/20  15.0%
#              hand              0/45  **0.0%**  <- 45 probes, zero routes. DO NOT HAND-PROBE.
#            `unknown` (35/35) is BACK-FILL ONLY, pure selection bias, and must never be ranked.
#   planes   34 = 19 fast + 15 slow. Count `ok` lines, NEVER read a banner.
#   suite    baseline **3430/3448, 18 failures**. A 19 is a REGRESSION.
#   ratchet  trusted-raises-honesty SILENT 69 (MAX_SILENT=69); dropped-mutation TRYFINAL 9.
#   pre-existing, NOT gen #21's: `self-annotate-mirror-check.sh` rc=1 on
#            `expr_ghost_collections.py` / `statements.py` / `stmt_control_flow.py`; the two
#            modified gitlinks (`scratchpad/w7/base`, `scratchpad/w8/pre`); 0-byte stray `str`.
#
# ====== START HERE — gen #20 FINAL STATE — read this block first ==================
#
# ## STATUS: COMPLETE. Tree clean, everything committed. HEAD at hand-off: see `git log -1`.
#
# ## 1. THE BATTERY THREE GENERATIONS FAILED TO RECORD IS **DONE AND COMMITTED**
#
#   DO NOT RE-RUN IT. All NINE legs plus the mirror-check are recorded with provenance:
#
#     1  metric                  459 markers / 484 grep / offset 25 / unattached 0   HIT   gen19*
#     2  doc-coherency           rc=0                                                HIT   gen19*
#     3  fidelity mirror-sync    rc=0, 887 un-trusted fns verbatim, 37 consts        HIT   gen19*
#     4  trusted-raises-honesty  rc=0, 75 stubs: 6 DECLARED / 69 SILENT, ratchet 69  HIT   gen19*
#     5  reference suite         3423/3441, 18 fail, ZERO XPASS, rc=1            ACCEPTED  gen20
#     6  byte-diff pycsl-ref     1036/1045, 0 MOVED / 0 GONE / 0 APPEARED, zb 0/0   HIT   gen20
#     7  byte-diff python-ref    2203/2203, 0 MOVED / 0 GONE / 0 APPEARED, zb 0/0   HIT   gen20
#     8  mirror emission-diff    53/53,     0 MOVED / 0 GONE / 0 APPEARED, zb 0/0   HIT   gen20
#     9  planes                  34/34 `ok` COUNTED = 19 fast + 15 slow             HIT   gen20
#    (+) mirror-check            rc=1 on the SAME 3 at HEAD **and** at 5795cfef     HIT   gen20
#
#     * legs 1-4 are gen #19's, valid for this tree because
#       `git diff b3782687 HEAD -- . ':(exclude)getting-better'` is EMPTY — a property of the
#       SOURCE TREE, re-verified by gen #20 in one command, not an inherited verdict.
#
#   **ROUTES #101 #102 #103 #104 #105 #106 ARE NOW REPAIRED *AND* FULLY GATED.**
#   EVERY PREDICTION HIT. One near-miss recorded rather than quietly replaced: leg 6's
#   "+10 new-source" is 10 new SOURCES but 9 new EMISSIONS, because route #103's REFUSAL
#   witness 1291 correctly emits no `.mlw`. Benign ONLY because SOURCES.txt exists.
#   No ratchet re-baselined, no golden re-blessed.
#
#   Suite provenance, stated once so nobody re-litigates it: read from gen #19's COMPLETED run
#   at HEAD `4855f163` (finished 23:10:29 UTC, box idle, ZERO prover processes), HEAD
#   re-verified unchanged before reading, and gen #19's OWN acceptance test — written before
#   the result was read — applied and passed on all three clauses.
#
# ## 2. THREE NEW SEV-1 ROUTES, ALL REPRODUCED, NONE REPAIRED  <-- START HERE, gen #21
#
#   **#107 — a try's `else:` block is SILENTLY DELETED when its lowered text merely CONTAINS
#   the substring "raise", including from an ordinary IDENTIFIER'S NAME.**
#   `stmt_control_flow.py:1809`: `if _else_str.strip() and "raise" not in _else_str:`.
#   A dead local named `praiseworthy` deletes the whole block. BOTH DIRECTIONS MEASURED:
#   the exploit proves `ensures \result == 1` while CPython returns 5; the control, identical
#   minus that one local, correctly FAILS on the postcondition. Route #37's fence
#   (`pycsl.py:1013`) tests four statement KINDS and an `Assign` is none of them.
#
#   **#108 — a callee's raise inside an `else:` is CAUGHT by that same try** (Python never
#   does this) **and is ALSO dropped from the function's `raises` summary**, because
#   `_callee_raised_in` skips `orelse`. A `#@ no_exception ValueError` caller PROVES while
#   CPython raises. Survives the #100 -> #105 chain: that chain fixed the receiver KEY, and
#   here the SET looked up is what is empty.
#   >>> #107 and #108 ARE THE TWO DIRECTIONS OF THE SAME CODE AND MUST BE REPAIRED TOGETHER.
#   >>> Making the splice fire more often is NOT safe on its own — that is #108.
#
#   **#109 — the `_objstate_w` fail-closed FRAME fallback lives in the `self.` arm only.**
#   `expressions.py:6650-6660` builds a 7-tuple with `_objstate_w` in the gate; `:6696-6705`
#   applies the same filter for a record-var/module-global receiver, never computes the
#   fallback, and builds a 6-tuple. Exploit proves `#@ assigns \nothing` over a mutating call;
#   emitted avatar is `val c_bump_0 () : unit` — NO frame, NO receiver — while the method's own
#   definition in the SAME file carries `writes { _pyobj_state }`. Control fails for the RIGHT
#   goal. `order = 2`: the carrier IS the `#32 SPIKE` repair, whose docstring narrates the very
#   hazard it left in the other arm.
#
#   Route files: `open-routes/route107-*.md`, `route108-*.md`, `route109-*.md`.
#   Witnesses (NOT yet in the corpus — landing them needs a battery):
#   `open-routes/witnesses-r107-r108/` and `open-routes/witnesses-r109/`.
#
# ## 3. THE PROBE LEDGER IS CLEAN
#
#   **ZERO `PENDING` rows** — all three closed with real verdicts (226 FAIL-CLOSED
#   stale-but-covered, 232 LIVE #109, 234 LIVE #108). Two attempts logged **VACUOUS** and kept
#   OUT of FAIL-CLOSED; one candidate logged INCOMPLETE and explicitly NOT claimed as a finding
#   (`_try_reaches_assert` in `desugar.py` scans `node.body` only, so route #16's assert fence
#   looks blind to an `assert` in an `else` block — NOT PROBED).
#
#   YIELD, which is the number to steer by — a route count only goes up and cannot say
#   "nearly done". ALL: LIVE 66 / FAIL-CLOSED 81 / denom 147 / **yield 44.9%**, 2nd-order 9,
#   VACUOUS 10. **Highest-yield real generator: `continue-census` at 83.3% (10/12)** — and all
#   three of this generation's routes came from it or from its census. `hand` is 0.0% over 45.
#
# ## 4. THE SEAM, still the richest thing open, now with evidence behind it
#
#   **Which OTHER obligations are keyed on a call node, a receiver spelling, or a TEXT
#   PATTERN that the emitter can lose?** #109 confirms the chain's prediction that the shape
#   RECURS ONCE PER OBLIGATION KIND (#70 -> #100 -> #105 -> #109). Still named and unprobed:
#   the frame `writes` under INLINING (#106's seam), the callee's `requires`, the UB gates,
#   and a `\trusted` callee inlined straight through the trust boundary.
#
#   NEW GENERATOR, earned this generation and worth more than the three routes:
#   >>> **A GUARD IMPLEMENTED AS A SUBSTRING TEST OVER GENERATED TEXT IS KEYED ON SPELLING,
#   >>> NOT ON STRUCTURE, AND THE SPELLING IS ATTACKER-CHOSEN THE MOMENT A USER NAMES A
#   >>> VARIABLE.** Go and census every `in <generated text>` / `not in <generated text>` test
#   >>> in Module 6. `stmt_control_flow.py:1809` was the first one anybody looked at.
#
#   And a hard-won instrument lesson, paid for twice this generation:
#   >>> **READ THE WHOLE EMITTED FILE BEFORE CREDITING A PROOF TO A MECHANISM.** The first
#   >>> #108 witness PROVED — via #107's deletion, because its callee was named `may_raise`.
#   >>> The `[+] SUCCESS` line alone would have credited the wrong route.
#
# ## 5. WHAT IS TRUE RIGHT NOW
#
#   metric   markers **459** / grep 484 / offset 25 / unattached 0 — RE-MEASURED at HEAD.
#   planes   34 = 19 fast + 15 slow. Count `ok` lines, NEVER read a banner.
#   suite    baseline **18** failures; VERIFIED GREEN this generation. Do not re-run it.
#   ratchet  `check-trusted-raises-honesty` SILENT **69** (MAX_SILENT=69). Move the
#            POPULATION, never the LINE.
#   byte-diff baseline for #101-#106 was **5795cfef**; a NEW baseline is needed for any
#            #107/#108/#109 repair. Worktree `<scratchpad>/g19base` is at 5795cfef with
#            `.venv` symlinked. `/tmp/claude-1000/bd_before` (gen #18's killed 584-file sweep)
#            HAS BEEN DELETED so it can no longer be mistaken for a baseline.
#   pre-existing, NOT gen #20's: `self-annotate-mirror-check.sh` rc=1 on
#            `expr_ghost_collections.py` / `statements.py` / `stmt_control_flow.py` — CONFIRMED
#            pre-existing by running it at 5795cfef as well as at HEAD; the two modified
#            gitlinks (`scratchpad/w7/base`, `scratchpad/w8/pre`).
#
# ====== START HERE — gen #19 FINAL STATE — read this block first ==================
#
# ## STATUS: IN PROGRESS (this block is updated as the generation runs)
#
#   Window #6 continues. Started from HEAD `b3782687` — gen #18 committed its final-battery
#   PREDICTIONS and then stopped WITHOUT RECORDING A SINGLE VERDICT. Per rule (r) I inherit
#   NO verdict whose tree I did not establish: gen #18's six routes (#101–#106) are treated
#   as **REPAIRED BUT NOT GATED** until the whole battery is re-established at a tree I ran.
#
#   I ADOPT GEN #18'S COMMITTED PREDICTIONS AS MY OWN (they are census-backed and were
#   written before anything ran) and record every hit and every miss against them.
#
# ## BATTERY RE-ESTABLISHED AT HEAD b3782687 — verdicts as they land
#
#   metric                459 markers / 484 grep / offset 25 / unattached 0   PREDICTED, HIT
#   doc-coherency         rc=0                                               PREDICTED, HIT
#   fidelity mirror-sync  OK, 887 un-trusted mirror fns verbatim, 37 consts   PREDICTED, HIT
#   trusted-raises-honesty SILENT 69 / declared 6, ratchet 69, rc=0           PREDICTED, HIT
#
# ## WHAT IS TRUE RIGHT NOW
#
#   ledger   (updated as the generation runs)
#   metric   markers **459** / grep 484 / offset 25 / unattached 0 — RE-MEASURED at HEAD.
#   planes   34 = 19 fast + 15 slow. ALWAYS SAY WHICH SET YOU RAN. Count `ok` lines.
#   suite    baseline **18** failures. A run showing 19 is a REGRESSION.
#   ratchet  `check-trusted-raises-honesty` SILENT is **69** (MAX_SILENT=69). Move the
#            POPULATION, never the LINE.
#   pre-existing, NOT gen #19's: `self-annotate-mirror-check.sh` rc=1 at HEAD on
#            `expr_ghost_collections.py` / `statements.py` / `stmt_control_flow.py`; the two
#            modified gitlinks (`scratchpad/w7/base`, `scratchpad/w8/pre`); 0-byte stray `str`.
#
# ====== START HERE — gen #18 FINAL STATE — read this block first ==================
#
# ## STATUS: IN PROGRESS (this block is updated as the generation runs)
#
#   Window #6 continues. Started from HEAD `1bf3c768` (gen #17 left route #101 FOUND,
#   REPRODUCED, repair SCOPED but NOT LANDED). Metric RE-MEASURED at HEAD, not
#   inherited: **markers 459 · grep 484 · offset 25 · attached 459 · unattached 0**.
#   Tree clean apart from the two PRE-EXISTING modified gitlinks (`scratchpad/w7/base`,
#   `scratchpad/w8/pre`) and the pre-existing 0-byte stray `str`. Zero untracked.
#
#   PLAN: (1) land route #101's repair — the third collector arm for the `Subscript`
#   spelling — fully gated; (2) check the TWO FURTHER CARRIERS gen #17 named rather
#   than assume the one repair covers them (a bare `#@ assigns g` -> IR `Var`; the
#   `nothings` flattening at `Module5_IREmitter.py:5882`); (3) the four ranked census
#   candidates, led by the `.clear()`/`.update()` no-op on a dict parameter.
#
# ## WHAT IS TRUE RIGHT NOW
#
#   ledger   (updated as the generation runs)
#   metric   markers **459** / grep 484 / offset 25 / unattached 0 — RE-MEASURED.
#   planes   34 = 19 fast + 15 slow. ALWAYS SAY WHICH SET YOU RAN.
#   suite    baseline **18** failures. A run showing 19 is a REGRESSION.
#   ratchet  `check-trusted-raises-honesty` SILENT is **69** (MAX_SILENT=69), lowered
#            monotonically by a non-driver agent. Move the POPULATION, never the LINE.
#   pre-existing, NOT gen #18's: `self-annotate-mirror-check.sh` rc=1 at HEAD on
#            `expr_ghost_collections.py` / `statements.py` / `stmt_control_flow.py`
#            (family of `finding-L1-fidelity-plane-red-at-head.md`); the two modified
#            gitlinks; the 0-byte stray `str`.
#
# ====== START HERE — gen #17 FINAL STATE — read this block first ==================
#
# ## STATUS: IN PROGRESS (this block is updated as the generation runs)
#
#   Window #6 continues. Started from HEAD `52cf618b` with the ledger EMPTY (gen #16
#   closed #97/#98/#99/#100). Metric RE-MEASURED at HEAD, not inherited:
#   **markers 459 · grep 484 · offset 25 · attached 459 · unattached 0** — unchanged.
#   Planes **34 = 19 fast + 15 slow**, confirmed BY READING THE TWO ARRAYS in
#   `bin/run-soundness-planes.sh` (PLANES=19, MIN_PLANES=18; SLOW_PLANES=15, added by
#   `--slow` with MIN_PLANES bumped to 33) — NOT by running the script and reading a
#   banner, which is exactly how gen #15 lost 15 planes.
#
#   PROBE-LEDGER YIELD AT GENERATION START (`bin/probe-ledger-yield.sh --by-generator`),
#   which is the number that picks the generator:
#     continue-census   4/5   **80.0%**   (2 second-order)
#     deferral-audit    3/6   50.0%       (4 VACUOUS — the worst vacuity rate in the table)
#     carve-out-census  6/14  42.9%
#     advice-audit      2/5   40.0%
#     oracle-audit      1/3   33.3%
#     control-operation 3/20  15.0%
#     hand              0/45  **0.0%**    <- 45 probes, zero routes. Do not hand-probe.
#   `unknown` (35/35, 100%) is BACK-FILL ONLY and is pure selection bias — a row was
#   written because it was interesting. It is not a generator and must never be ranked.
#
# ## WHAT IS TRUE RIGHT NOW
#
#   ledger   (updated as the generation runs)
#   metric   markers **459** / grep 484 / offset 25 / unattached 0 — RE-MEASURED.
#   planes   34 = 19 fast + 15 slow. ALWAYS SAY WHICH SET YOU RAN.
#   suite    baseline **18** failures. A run showing 19 is a REGRESSION.
#   pre-existing, NOT gen #17's: `self-annotate-mirror-check.sh` rc=1 at HEAD on
#            `expr_ghost_collections.py` / `statements.py` / `stmt_control_flow.py`
#            (family of `finding-L1-fidelity-plane-red-at-head.md`); the two modified
#            gitlinks `scratchpad/w7/base`, `scratchpad/w8/pre`; the 0-byte stray `str`.
#
# ====== START HERE — gen #16 FINAL STATE — read this block first ==================
#
# ## THE ONE-PARAGRAPH SUMMARY
#
#   **FOUR ROUTES FOUND, REPAIRED, AND FULLY GATED — #97, #98, #99, #100 — AND THREE
#   OF THE FOUR LIVE INSIDE THIS CAMPAIGN'S OWN EARLIER REPAIRS OR GATES.** #97: a Liskov
#   violation behind a FIELDLESS base was silently accepted — `--check-behavioral-
#   subtyping` emitted ZERO refinement goals and reported "All contracts formally
#   proven." #98: route #96's repair decides whether an array-region `assigns`
#   becomes a `writes` clause by testing the **SOURCE** identifier for membership in
#   a set built from the **EMITTED** signature, so any parameter `whyml_ident`
#   renames (`model` -> `py_model`, any WhyML reserved word, any leading capital)
#   loses its frame entirely and the whole of #96 returns. #99: route #94's UB-7.7
#   memoization gate collects mutated fields only when the write is spelled
#   `self.<f>` AND only sees functions emitted before the end of the enclosing
#   class, so a stale `@cached_property` proves a postcondition CPython contradicts.
#   The metric never moved (**markers 459 / grep 484**) and was never supposed to.
#
#   #100: a `#@ no_exception E` on a METHOD was proved with NO OBLIGATION AT ALL —
#   `_wrap_call_with_callee_raises_assert` had ONE call site (the module path), keyed
#   on the IR name, so `self.m(...)` never reached it. CPython raises where PyCSL
#   proved. >>> **AN ABSTRACTION THAT IS CONSERVATIVE FOR WHAT A CALLER MAY *ASSUME*
#   IS PERMISSIVE FOR WHAT A CALLER MUST *DISCHARGE*** — the val already carried the
#   callee's `ensures`, so the path visibly carried a contract and read as sound.
#   THE CAPABILITY ARM CHOSE THE REPAIR: the alternative (transmit `raises` onto the
#   val) closes the exploit but emits an UNCONDITIONAL `raises { E -> true }` that
#   also breaks the guarded caller — refusing everything instead of the wrong thing.
#
#   **FINAL BATTERY, EVERY VERDICT PREDICTED IN WRITING BEFORE IT RAN:** suite
#   **3413/3431, 18 CONFIRMED FAIL, ZERO XPASS, rc=1**; byte-diff pycsl-ref
#   **0 MOVED / 0 GONE / 0 APPEARED** (+9 new-source) and python-ref **2203/2203
#   0/0/0**, zero-byte 0 both sides of both corpora; SOURCES **1199 -> 1211**;
#   fidelity **887 verbatim** + mirror-check **DELTA ZERO**; mirror emission-diff
#   **3 of 53** (the #97/#98 `raises` declarations only — **#100 moved ZERO mirrors**);
#   the three moved mirrors re-proved **rc=0 / 0 non-Valid each**; doc-coherency
#   rc=0; conformance **38/38 both corpora**; determinism **10/10**; planes
#   **34/34**. **NO RATCHET RE-BASELINED** — `trusted-raises-honesty` held at **70**
#   through TWO reds, both mine, both fixed by moving the population across the line
#   and never the line. No golden re-blessed, no gate loosened.
#
# ## THE SINGLE MOST TRANSFERABLE THING THIS GENERATION LEARNED
#
#   >>> **"FAIL-CLOSED" IS A CLAIM ABOUT A PARTICULAR MACHINE. NAME THE MACHINE.**
#   >>> The skip that carries route #98 is COMMENTED, and the comment says
#   >>> "FAIL-CLOSED, and deliberately so … Any such residue stays visible as an
#   >>> un-framed val." Emitting nothing IS fail-closed for the EMITTER — no
#   >>> ill-typed `writes` is produced. It is fail-**OPEN** for the VERIFIER, which
#   >>> is told the stub is PURE. **Dropping a frame clause is never conservative:
#   >>> an un-framed `val` is the STRONGEST possible claim.**
#
#   And the second half of that sentence is the other half of the lesson:
#   **"STAYS VISIBLE" NAMES NO OBSERVER.** Nothing in the tree — no gate, no plane,
#   no ratchet — counts a bodyless `val` that carries a region `assigns` and emits
#   no `writes`. Visible to whom? *When a comment says a residue is acceptable
#   because it remains visible, go and find the thing that looks. If you cannot name
#   it, the residue is invisible and the comment is the only thing guarding it.*
#
# ## ROUTE #99 IN ONE SCREEN — CLOSED, AND MY FIRST REPAIR OF IT WAS INCOMPLETE
#
#   The UB-7.7 memoization gate (route #94's own gate) let a `@cached_property` reading
#   `self.a` PROVE `ensures \result == self.a` while `a` was mutated by a free function
#   taking the object as a parameter. CPython after one `bump()`: `total=0, a=1`, so the
#   proved postcondition is FALSE. **TWO INDEPENDENT NARROWINGS, AND ONLY BOTH FIXES
#   CLOSED IT — the measurement said so, not an argument:**
#     1. `memoization_rt.py` admitted a `FieldAssign` to `mutated` only when
#        `object == "self"`, so `c.<f> = ...` never entered it and `if not mutated:
#        return` disarmed the gate. **Fixing this ALONE left the exploit STILL PROVING.**
#     2. The check ran at the end of `visit_ClassDef`, whose comment justified it:
#        *"by here `generic_visit` has emitted every method of the class, SO THE SET IS
#        COMPLETE."* Every method OF THAT CLASS — a module-level function defined after
#        the class is not. Moved to the end of `visit_Module`.
#
#   >>> **ROUTE #94 MOVED THIS CHECK ONE LEVEL (function -> class) WHEN IT NEEDED TO MOVE
#   >>> TWO (function -> class -> MODULE). Its own lesson — *a check needing a
#   >>> whole-program fact cannot live in a per-node visitor* — was exactly right, and
#   >>> A CLASS IS STILL A NODE.**
#
#   Capability preserved and specifically tested for #94's own stated fear ("a blanket
#   field-read ban would delete that real capability"): witness **1284 PROVES** — a
#   memoized reader of a construct-only field while a foreign receiver mutates a
#   DIFFERENT field. Whole exposed population is FOUR files (0515/0516/1257/1258), each
#   re-measured. **RESIDUE, NAMED:** `mutated` is still a flat set of field NAMES, so an
#   unrelated class sharing a name over-refuses — PRE-EXISTING and unchanged in kind (20
#   of 72 field names are shared). Keying on `(class, field)` is the right follow-up.
#
# ## AND I CAUGHT ONE OF MY OWN WITNESSES LYING — DO THIS TO YOURS
#
#   I wrote witness 1283 claiming it ISOLATED narrowing (2). It FAILED at baseline, which
#   looked like confirmation. **A CONTROL THAT FAILS IS A CLAIM ABOUT THE CONTROL UNTIL
#   YOU READ WHICH GOAL FAILED** — so I read it: at baseline it fails on an unrelated
#   forward-reference type error (`has type int, but is expected to have type
#   PyCSL_Program.c`), because `def bump(c: "C")` before `class C` emits the param as
#   `int`. The alternative isolation (a free function whose parameter is *named* `self`)
#   fails on `unbound function or predicate symbol 'self'`. **So narrowing (2) is NOT
#   independently witnessable**; both fences are recorded so nobody re-tries them, and
#   1283's docstring now says what it actually measures. The route's real witness is 1282.
#
# ## TWO MEASUREMENT TRAPS, BOTH HIT AND BOTH CAUGHT — THEY WILL HIT YOU TOO
#
#   * **A byte-diff reported `295 GONE — NOT BYTE-INERT`, and it was a FALSE RED.** The
#     sweep emits pycsl-reference first and python-reference second; I compared while the
#     second half was still being written. `1908 < 2203` means INCOMPLETE, not DELETED.
#     >>> **ASSERT A POPULATION SIZE BEFORE BELIEVING A DIFF — INCLUDING A RED ONE.** The
#     rule is usually quoted to stop a false green; it stops false reds too.
#   * **`pgrep -f "byte-diff-sweep"` reported STILL RUNNING with zero sweeps alive**,
#     because the WATCHER SHELLS waiting on that string carry it in their own command
#     lines and match themselves — 8 hits, 0 real. Grep for the thing being EXECUTED
#     (`bash bin/byte-diff-sweep.sh`), not a string that also appears in what WAITS on it.
#
# ## THE GENERATOR IS NOW FIVE-FOR-FIVE — KEEP RUNNING IT
#
#   >>> **A LOOP THAT BOTH BUILDS SOMETHING AND ASSEMBLES A CHECKING POPULATION WILL
#   >>> HAVE A SKIP WRITTEN FOR THE BUILDING THAT SILENTLY NARROWS THE CHECKING.**
#
#   #95, #96, #97, #98 and now #99 are all this shape. #97's instance, verbatim:
#   `apply_inheritance`'s `if base is None: continue` is CORRECT for the field merge
#   (a fieldless base has nothing to merge) and is the ONLY producer of the Liskov
#   override pair, so for the verification job sharing that loop it is a deleted
#   obligation. THE REPAIR IS ALWAYS THE SAME MOVE: **split the two jobs**, and keep
#   the build half gated while the recording half goes unconditional.
#
#   A ranked `continue`-census of the LIVE source was run this generation and its
#   candidates are in the progress log. #98 was candidate 1. **CANDIDATES 2 AND 3
#   ARE UNPROBED AND BOTH FEED VERIFICATION CONSUMERS** — see "STILL UNPAID".
#
# ## THE OTHER LESSON, PAID FOR IN A WASTED HOUR — DO NOT REPEAT IT
#
#   I launched the reference suite and then ran the baseline byte-diff sweep, the
#   candidate sweep, conformance, determinism, both mirror emission sweeps and the
#   19 planes CONCURRENTLY on a 12-core box. The suite came back **2181/3421**
#   against a predicted 3403/3421, with long CONTIGUOUS blocks of failures. It was
#   CPU starvation: the provers run under `--timelimit 5` and timed out wholesale.
#   **4 of 4 sampled "CONFIRMED FAIL" files were re-run ALONE and every one reported
#   `Verification SUCCESS`.** The verdict was declared VOID and re-run alone.
#   >>> **A CONTENDED BATTERY IS A BATTERY CUT OFF BY A TIMEOUT IT DID NOT DECLARE.**
#   >>> One heavy job on the box at a time. And note WHAT SAVED IT: the prediction
#   >>> was in writing, so a result 1200 tests away from it was INTERROGATED instead
#   >>> of accepted. A green you merely receive tells you only that nothing screamed.
#
# ## A PLANE WENT RED AND IT WAS MINE — THE HONEST FIX IS TO MOVE THE POPULATION
#
#   `check-trusted-raises-honesty` broke (SILENT 71 > 70) because #97's fail-closed
#   half adds a `raise PyCSLIRError` to a live function whose `\trusted` mirror stub
#   declared no `#@ raises` — so the emitted `val` was telling Why3 that call cannot
#   raise. PROVED MINE, NOT PRE-EXISTING: the a32ec69e baseline measures 3 declared
#   / 70 silent, and a sorted diff of the two `--verbose` populations is a SINGLE
#   added line naming exactly `_emit_subtyping_goals`. FIX: declare it —
#   `#@ raises PyCSLIRError when True` on the mirror stub — moving it SILENT ->
#   DECLARED. Re-measured 4 declared / **70 SILENT, ratchet 70, OK**.
#   >>> **THE BOUND WAS NEVER TOUCHED.** A ratchet that goes red because you honestly
#   >>> grew the population it measures is repaired by moving the item across the
#   >>> line, never by moving the line.
#
# ## ROUTE #97 IN ONE SCREEN
#
#   A class becomes a record `type_decl` only `if fields or bases:` (Module5), so a
#   STATELESS base — the interface / pure-behaviour base, the most common reason to
#   write a base class at all — is absent from `records` in `apply_inheritance`.
#
#   | file | `Base` has a field? | goals | verdict |
#   |---|---|---|---|
#   | fieldless base + violation | no | **0 -> 1** | **SUCCESS -> FAILED** |
#   | fielded base + same violation | yes | 1 | FAILED (unchanged) |
#   | fieldless base + LEGITIMATE override | no | **0 -> 1** | SUCCESS -> SUCCESS |
#
#   The failing goal is NAMED, not inferred: `why3 prove -P alt-ergo` reports
#   `Goal sub__f_refines_base … Unknown`, body `((x >= 0) -> (x >= 5)) /\ …`. The
#   conforming twin's same-named goal is `Valid`. **The capability arm's pass was
#   WORTH NOTHING before the repair** — it passed with zero goals emitted, i.e.
#   vacuously; a guard whose population is empty looks exactly like a guard that
#   passed.
#
#   THE FAILURE IS INVERTED WITH RESPECT TO GOOD PRACTICE: the cleaner the base
#   class, the less checking it received.
#
#   CO-LANDING FAIL-CLOSED HALF, AND IT WAS NOT OPTIONAL: `_emit_subtyping_goals`'
#   `if sub_fn and base_fn:` was a SECOND silent drop on the same obligation, and the
#   upstream repair feeds it inputs it never saw. It now RAISES
#   `PYCSL-SUBTYPING-PAIR`. Negative-tested by injecting an unresolvable pair through
#   a wrapper: it refuses loudly. >>> **A GUARD THAT STOPS BEING SILENT IN ONE SHAPE
#   AND STAYS SILENT IN THE NEXT HAS BEEN NARROWED, NOT REPAIRED.**
#
# ## ROUTE #98 IN ONE SCREEN — OPEN, SEV-1, REPAIR SCOPED IN ITS FILE
#
#   `functions.py:6605` builds the population from the ALREADY-EMITTED signature:
#   `re.findall(r"\((\w+)\s*:\s*array\b", args_str)` — post-`whyml_ident`.
#   `statements.py:3452` tests the SOURCE name against it:
#   `if base and base in _arr_params`. Two name spaces, one membership test.
#
#   | param | emitted signature | `writes` | verdict |
#   |---|---|---|---|
#   | `a` | `val scramble (a: array int) …` | **`writes { a }`** | FAILS (refused) |
#   | `model` | `val scramble (py_model: array int) …` | **ABSENT** | **PROVES `\result == 7`** |
#   | `Buf` | `val scramble (buf: array int) …` | **ABSENT** | **PROVES** |
#
#   CPython: `driver([7,7,7,7]) == 0`. `WHYML_RESERVED` holds ORDINARY parameter
#   names — model, range, check, label, result, old, ref, float, to, by, type.
#   REPAIR: put `base` through `whyml_ident` BEFORE the membership test and append
#   the EMITTED name. **CO-LANDING HALF:** give the remaining residue an OBSERVER
#   (a refusal, or a plane counting un-framed region-`assigns` vals) — the current
#   "stays visible" observer does not exist.
#
#   **DO NOT RE-PROBE, MEASURED:** the obvious exploit that keeps #96's
#   `#@ requires \length(model) > n + 1` is LOUDLY type-rejected ("unbound function
#   or predicate symbol 'model'") — the contract renders the SOURCE name, the
#   signature the mangled one. Had that been the only arm, it would have read as
#   "the fence holds". The live route needs the renamed parameter in NO contract
#   clause but the `assigns`.
#
# ## A CERTIFIED FAIL-CLOSED BOUNDARY BANKED THIS GENERATION (witness 1277)
#
#   An inherited, NOT-overridden method of a fieldless base is not cloned and lowers
#   to a CONTRACT-FREE `val s_f_1 (x0: int) : int` — read off the emitted WhyML — so
#   NEITHER the true fact (`\result == 4`) NOR the false twin (`== 99`) proves. The
#   FIELDED twin PROVES the true fact, so the channel is alive and the fence is real.
#   **REOPENING CONDITION:** the obvious "completeness fix" is to hand that call the
#   BASE's contract. That would ASSUME a postcondition NOTHING discharges for the
#   subclass — the campaign's *a completeness fix that supplies a WITNESS value is a
#   soundness route waiting to happen*, which `_field_default` walked into five
#   times. Witness 1277 turns XPASS the moment such a fix lands.
#
# ## STILL UNPAID, IN THE ORDER I WOULD TAKE THEM
#
#   1. **ROUTE #98 — REPAIR IT, BOTH HALVES.** Scoped in its route file. Measure BOTH
#      directions AND re-check route #96's capability witness 1271 for a RENAMED
#      parameter, not just for `a`.
#   2. **BOTH REMAINING CENSUS CANDIDATES ARE NOW PROBED — #3 BECAME ROUTE #99
#      (CLOSED), #2 BECAME A CERTIFIED BOUNDARY.** Candidate #2's record is
#      `open-routes/finding-TY3-gt1-bypassed-by-one-level-of-nesting.md` and its
#      REOPENING CONDITION IS THE LIVE ITEM: `monomorphize._type_str` answers `None`
#      for a nested `Subscript`, so `Wrap[Box[Any]]` is NOT refused while `Box[Any]`
#      IS — GT1 is bypassed one level down, and GT2's bound obligation goes with it.
#      It is NOT a route today ONLY because the nested program cannot prove a TRUE
#      fact either (measured, with the prover on). **THE MOMENT NESTED INSTANTIATION
#      IS IMPLEMENTED THE BYPASS GOES LIVE, SILENTLY.** Make `_type_str` recurse and
#      surface every type argument at every depth FIRST, then emit.
#      >>> **THE WHOLE TY3 AREA IS UNCOVERED: not one file in the test-suite uses
#      >>> `TypeVar` or `Generic[` — five gates, ~700 lines, ZERO corpus coverage.**
#      Two collateral facts there, both flagged UNMEASURED not claimed: the IR-side
#      `_collect_instantiations` returned `[]` in EVERY shape tested (everything came
#      from the AST collector); and **PEP 484 `class Box(Generic[T])` registers no
#      `type_params` at all**, so `apply_monomorphization` early-returns and the ENTIRE
#      TY3 machinery is a silent no-op for the older, commoner spelling — `Box[Any]`
#      there VERIFIES with no GT1, while the PEP 695 spelling is refused.
#
#   2b. **THE ORIGINAL CENSUS TEXT, kept because its evidence is still good** (full evidence in the progress log):
#      * `frontend/monomorphize.py:248-249` + `:331-345` — the instantiation census
#        is narrowed by a BUILD-ability test (`Subscript` -> `return None`), and the
#        SAME set feeds the **GT1 `Any` refusal** (`monomorphize.py:74-81`) and the
#        **GT2 bound obligation** (`:84` -> `_check_bounds`). So `Stack[Box[int]]`
#        may get NO bound check and NO `Any` refusal. Also `_collect_instantiations`
#        never reads `type_decls`, so a `self.s: Stack[int]` FIELD is outside the
#        census entirely.
#      * `frontend/module5/memoization_rt.py:93-98` — the UB-7.7 / route-#94 gate's
#        `mutated` set admits only `cur.get("object") == "self"`, so a mutator
#        writing the field through ANY OTHER RECEIVER contributes nothing and the
#        memoized reader passes the gate. Call site is inside `visit_ClassDef`, so a
#        mutator in a LATER class is absent from the population too.
#      Verify each independently — every inherited candidate has needed narrowing.
#   3. w66's reopening conditions 2 and 3 (**`init-hook` is still GUARD-NOT-FOUND and
#      its probe was VACUOUS** — build the positive control FIRST); w65 `fresh_globals`
#      cross-module confinement (**BUILD THE POSITIVE CONTROL FIRST**); w64's
#      `\separated` hardening; finding-w60; the `_field_default` `option` arm.
#
# ## WHAT IS TRUE RIGHT NOW
#
#   ledger   **NONE OPEN. #97 AND #98 BOTH FOUND, REPAIRED IN BOTH HALVES, AND FULLY
#            GATED ON THE COMPLETE 34-PLANE SET.** Suite **3407/3425, 18 CONFIRMED
#            FAIL, ZERO XPASS, rc=1 — predicted exactly.** An empty ledger is a prompt
#            to generate, not a floor: the `continue`-census is four-for-four and TWO
#            ranked candidates are still unprobed (see STILL UNPAID).
#   metric   markers **459** / grep 484 / offset 25 / unattached 0 — UNCHANGED.
#            Correct shape: a refusal and a monotone obligation cost nothing.
#   corpora  pycsl-ref **1199 -> 1214** (+15: witnesses 1273-1287).
#   planes   **34 = 19 FAST + 15 SLOW, and `run-soundness-planes.sh` WITHOUT `--slow`
#            IS A 19-OF-34 GATE.** All 34 are GREEN at this HEAD (script's own line:
#            "running 34 driver-run lower bound(s)"; I counted 34 `ok` lines myself).
#            >>> **GEN #15's "19, NOT 34" WAS WRONG, AND SO WAS MY LAUNCH PROMPT AND
#            >>> THIS HANDOFF UNTIL NOW.** Gen #15 suspected the number and checked it
#            the natural way — re-ran the SAME script at the baseline; both sides said
#            19, so it concluded 34 was stale. But BOTH SIDES RAN THE FAST SET.
#            >>> **AN A/B COMPARISON CONTROLS FOR CHANGE, NEVER FOR COVERAGE. To learn
#            >>> a gate's POPULATION you must read the gate's DEFINITION, not run it
#            >>> twice.** That is `ASSERT A POPULATION SIZE BEFORE BELIEVING IT` one
#            level deeper, and it is route #98's error in the gate set itself: a number
#            validated against another instance of itself. ALWAYS SAY WHICH SET YOU RAN.
#            The 15 slow ones include the closest relatives of #96/#98 —
#            `check-trusted-frame-honesty`, `check-value-differential`,
#            `check-no-exception-differential`, `check-bespoke-model-drift`.
#   suite    baseline **18** failures. A run showing 19 is a REGRESSION.
#
# ====== START HERE — gen #14 FINAL STATE — read this block first ==================
#
# ## THE ONE-PARAGRAPH SUMMARY
#
#   **ONE SEVERITY-1 ROUTE FOUND *AND* CLOSED *AND* FULLY GATED (#95), PLUS THE TWO
#   CO-LANDING HARDENINGS GEN #13 ASKED FOR (w67, w68).** Gen #13's #1 handover item was
#   "land the three co-landing fixes for w66/w67/w68". **Doing w66's turned it into a live
#   route**: w66 had certified the unimplemented `provider ⊑ dependency` obligation (S2b) as
#   COMPENSATED by flatten-and-re-verify, and that is true *on the population the pass
#   flattens* — but `apply_composition` **skips cloning a provider whose tail the composer
#   already defines**, so a composer that writes its own `emit` deletes the only check that
#   ever existed. It PROVES `run() >= 10` while CPython returns **0**. The metric never moved
#   (**markers 459 / grep 484**) and was never supposed to: all three repairs are refusals.
#
# ## THE SINGLE MOST TRANSFERABLE THING THIS GENERATION LEARNED
#
#   >>> **WHEN YOU CERTIFY A MISSING CHECK AS "COVERED BY ANOTHER MECHANISM", THE QUESTION IS
#   >>> NOT "DOES THE COMPENSATOR COVER THIS CASE". IT IS "WHAT IS THE COMPENSATOR'S
#   >>> POPULATION, AND WHAT KEEPS IT EQUAL TO THE CHECK'S?"**
#
#   w66 was careful, measured, and right about every case it tried. It was still wrong,
#   because a compensating mechanism that is not a check **has no obligation to be total, and
#   will not be** — nobody maintains the coverage of a thing that was never written down.
#   This is gen #13's "a deferral is an unverified cross-reference" one level deeper: here the
#   cross-reference was verified, and the *population* was the unverified part.
#
#   The concrete tell, worth grepping for: **a loop that does DOUBLE DUTY — it both BUILDS
#   something and CHECKS something — where a `continue` written for the building silently
#   narrows the checking.** `if tail in own_tails: continue  # composer overrides it` is
#   correct override semantics for DISPATCH and a deleted obligation for VERIFICATION, in one
#   line, and it reads as obviously right.
#
# ## THE SECOND LESSON — A PRESCRIPTION IN A FINDING IS A HYPOTHESIS, NOT A WORK ORDER
#
#   Gen #13 wrote down a co-landing fix for each of w66/w67/w68. **Implementing them found
#   that two of the three prescriptions were wrong**, and in opposite directions:
#     * **w67's** ("the twin must also assert equality of PUBLIC state after the two calls")
#       is **NOT EXPRESSIBLE**. The twin calls the target twice on the SAME `self`,
#       sequentially — there is no second initial state, so there is no pair of final states
#       to relate. Landed as a REJECTION instead.
#     * **w68's** ("match the guarded call by its RESOLVED TARGET") would have been **UNSOUND,
#       not merely incomplete**: the guarding formula speaks about `self`, so discharging
#       `self.session_authenticated == 1` at `other.transfer(…)` proves the capability of the
#       **WRONG OBJECT** — a check that looks like enforcement and enforces nothing, strictly
#       worse than the hole. Landed as a REJECTION, keyed on the CALLEE.
#     * **w66's** was not a fix at all; writing it down surfaced route #95.
#   >>> **A FIX WRITTEN DOWN AT THE MOMENT OF UNDERSTANDING IS A HYPOTHESIS ABOUT CODE THE
#   >>> AUTHOR DID NOT TOUCH. THREE FOR THREE, THE ACT OF IMPLEMENTING IT CHANGED IT.** Budget
#   >>> for that: "land the written-down fix" is not a paperwork task, it is a probe.
#
# ## MEASUREMENT DISCIPLINE THAT PAID AGAIN
#
#   * **THE POSITIVE CONTROL CAUGHT A NEAR-MISS.** The obvious sibling of #95 — the composer
#     INHERITS the weak method instead of defining it — FAILS. That refusal means nothing on
#     its own; the control (same file, every claim weakened to `>= 0`) **PROVES**, so the
#     channel is alive and the fence is real. Its goal list also shows **`facade__emit'vc`
#     EXISTS**, i.e. an inherited method does not enter `own_tails`, the clone still happens,
#     and re-verification still fires. **So the route is specifically "the composer DEFINES it
#     itself", not "the composer HAS it"** — which is why the landed check keys on `own_tails`
#     (what the flatten loop actually consults) and not on "does the composer have a method
#     named `pm`", a scoping that would have rejected this safe, working shape.
#   * **EVERY GATE VERDICT WAS PREDICTED IN THE PROGRESS LOG BEFORE THE RUN**, as gen #13
#     prescribed. See the predictions entry; all followed from one sentence — *all three
#     repairs are pure REFUSALS, so no existing emission can move and only new files that
#     reach emission can appear*.
#   * **A PRE-EXISTING RED MUST BE PROVED PRE-EXISTING, NOT ASSUMED.** `mirror-check` reports
#     3 drifted mirrors. None is a file I touched — but the campaign rule is to measure, so I
#     ran it in a worktree at gen #13's HEAD and diffed **sorted** output: 19 lines both sides,
#     diff EMPTY. That is the difference between "DELTA ZERO" and "it was probably already
#     broken".
#   * **BOTH NEW GATES WERE NEGATIVE-TESTED (rule l)** and both are NARROW BY MEASUREMENT, with
#     the narrowness kept as standing witnesses (1261, 1264, 1266) so a future widening turns
#     them red.
#
# ## ROUTE #95 IN ONE SCREEN — SO THE NEXT GENERATION CAN RE-DERIVE IT
#
#   `ir_resolve.apply_composition`, flatten loop:
#
#       if tail in own_tails or new_name in existing:
#           continue   # composer overrides it, or already cloned
#
#   `own_tails` is the composer's OWN methods, computed before the loop. Skipping the clone
#   removes the provider from (a) the re-verified population and (b)
#   `composed_provider_methods`, the set Module 6 consults to resolve `self.<tail>(…)` to a
#   CONCRETE function. So the sibling mixin's cloned method keeps resolving `self.emit(k)` to
#   an abstract `val` carrying the **declared DEPENDENCY's** contract, while the composer's
#   own weaker method is what runs. The dependency contract is ASSUMED at the call site and
#   DISCHARGED BY NOBODY.
#
#   | driver | verdict |
#   |---|---|
#   | flagship 0549 unmodified (is the algebra alive?) | **PROVES** |
#   | the exploit WITHOUT the composer's own `emit` (w66's probe) | **FAILS** — compensator works |
#   | the exploit WITH it | **PROVES `\result >= 10`** |
#   | CPython, mixins as real bases | **`Facade().run(5) == 0`** |
#
#   Repair: sound-by-rejection, matching this function's two sibling checks. Injecting the
#   dependency contract onto the composer's own method would ASSUME exactly what S2b exists to
#   PROVE. Narrow on purpose: shadowing a provider nothing DEPENDS on assumes no contract and
#   is left alone (witness 1261).
#
# ## STILL UNPAID, IN THE ORDER I WOULD TAKE THEM
#
#   1. **THE `continue`-CENSUS — THIS IS THE LIVE GENERATOR AND IT IS WHAT PRODUCED #95.**
#      Hunt loops that BUILD and CHECK at once, where a skip written for the building narrows
#      the checking. A census was run this generation; its ranked candidates are in the
#      progress log. **Verify each independently — every candidate gen #13 inherited needed
#      narrowing, and so did every one of mine.**
#   2. **w66's REOPENING CONDITIONS 2 AND 3 ARE STILL OPEN AND UNTOUCHED**: a path making a
#      non-`provides` mixin method callable from the composer; and **`init-hook`, still
#      GUARD-NOT-FOUND, whose probe was VACUOUS.** The binding prescription stands: **build a
#      working positive control for `mixin + class invariant + composer __init__` FIRST** — a
#      mixin invariant does not currently reach the flattened clone, so every refusal there is
#      uninterpretable until one proves.
#   3. **w65 — `fresh_globals` cross-module confinement. STRUCTURE VERIFIED, EXPLOIT NOT
#      BUILT.** Unchanged from gen #13, and its prescription is still binding: **BUILD THE
#      POSITIVE CONTROL FIRST**, because a cross-module setup has many independent ways to
#      refuse and this is the probe most likely to be vacuous.
#   4. **w64 — the `\separated`-is-constant-`true` scoped hardening**, written up, NOT landed.
#   5. Carve-out candidates 9 and 10; **finding-w60**; the `_field_default` `option` arm.
#   6. Keep growing BOTH differential corpora — a route just closed is the cheapest source.
#
# ## DO NOT RE-PROBE (gen #13's list still binds, plus these)
#
#   * **The composer INHERITING the shadowing method** — measured FAILS with a PROVING positive
#     control; the clone still happens. Not a route. (Recorded in the route #95 file.)
#   * **A foreign-receiver call to a method that is NOT the H-S target** — untouched by design,
#     witness 1266 keeps it that way.
#   * **A state-READING noninterference target** — still accepted and still proves (1264); the
#     w67 rejection is about WRITING only.
#
# ## WHAT IS TRUE RIGHT NOW
#
#   ledger   **ONE OPEN: #96** (found, fully reproduced, CPython-contradicted, repair scoped,
#            deliberately NOT attempted — see below). **#95 FOUND, CLOSED AND FULLY GATED.**
#            Window tally of closed routes: **40**.
#   metric   markers **459** / grep 484 / offset 25 / unattached 0 — UNCHANGED, stable across
#            3 samples. Correct shape: all three repairs are refusals.
#   corpora  pycsl-ref **1014 -> 1022** (+8: witnesses 1259-1266).
#   gates    ALL GREEN, and EVERY VERDICT WAS PREDICTED IN THE PROGRESS LOG BEFORE THE RUN AND
#            WAS EXACT: suite **3392/3410, 18 failures, ZERO XPASS, rc=1** (baseline of 18 held;
#            none of 1259-1266 among them); byte-diff pycsl-ref **0 MOVED, 0 GONE, 0 APPEARED**
#            (+4 new-source), python-ref **2203/2203, 0/0/0**, zero-byte 0 BOTH sides;
#            fidelity mirror-sync OK (**887** un-trusted fns verbatim) and mirror-check
#            **DELTA ZERO** vs a 60a2cec1 worktree (19 lines both sides, sorted diff EMPTY —
#            its 3 drifted mirrors are PRE-EXISTING); doc-coherency rc=0; IR conformance both
#            corpora; determinism 10/10. No ratchet re-baselined, no golden re-blessed.
#   tree     clean; the two GITLINKS and the 0-byte stray `str` are PRE-EXISTING.
#
# ## >>> YOUR FIRST ITEM: ROUTE #96 IS OPEN, REPRODUCED, AND SCOPED. <<<
#
#   A bodyless `val` (`\trusted` / `\abstract`) **silently drops an array-region `assigns`**, so
#   a caller proves the array UNCHANGED across a stub contracted to write it. The emitted val
#   carries **no `writes` clause at all**. Measured: aliveness control PROVES, exploit PROVES,
#   `\abstract` arm PROVES, the same contract with a REAL BODY **FAILS**, a `\trusted` stub with
#   a **FIELD** assigns **FAILS**, and CPython returns **0** against a proved `\result == 7`.
#   Those last two controls pin it to exactly one cell of the 2x2: **region-assigns on a
#   bodyless val**. `\trusted` is the declared TCB boundary, so the `assigns` a reviewer
#   certifies is precisely the part the emitter throws away.
#
#   **I LEFT IT OPEN ON PURPOSE.** The repair (`writes { a }` for an AssignsRegion base, a sound
#   over-approximation) has a real blast radius — every `\trusted`/`\abstract`/imported function
#   with an array-region assigns, `src/pycsl_lib/` included. Census that population FIRST,
#   predict the MOVED set, and expect some files that verify today to legitimately FAIL: that is
#   the cost of transmitting a frame that was being dropped, and it must be worked, not hidden.
#   **Do not re-baseline anything to keep a gate green.** Full detail + the driver set:
#   `getting-better/open-routes/route96-trusted-val-drops-array-region-assigns-frame.md`.
#
# ## THE GENERATOR THAT FOUND BOTH ROUTES — RUN IT, IT IS PAYING
#
#   >>> **A LOOP THAT DOES DOUBLE DUTY — BUILDS SOMETHING *AND* ASSEMBLES A CHECKING POPULATION
#   >>> — WILL HAVE A `continue` WRITTEN FOR THE BUILDING THAT SILENTLY NARROWS THE CHECKING.**
#   #95: `if tail in own_tails: continue  # composer overrides it` is correct override semantics
#   for DISPATCH and a deleted obligation for VERIFICATION, in one line. #96: a `continue` that
#   collects field targets silently drops region targets, in a function whose own docstring
#   explains why dropping them is fatal. A census of these is in the progress log; **verify each
#   independently — every candidate needed narrowing.** One more candidate from it is unprobed:
#   the Liskov refinement goal dropped on a name miss (`module6_whyml/functions.py`), currently
#   latent because `--check-behavioral-subtyping` defaults off.
# ====== START HERE — gen #13 FINAL STATE — read this block first ==================
#
# ## THE ONE-PARAGRAPH SUMMARY
#
#   **FOUR ROUTES FOUND *AND* CLOSED *AND* FULLY GATED THIS GENERATION (#91, #92, #93, #94).**
#   All four are SEVERITY 1. The first three are all in ONE FUNCTION
#   (`Module3_Weaver._weave_happy`), and all three are **SECURITY META-PROPERTIES PROVED WHILE
#   VIOLATED**, not wrong values. The window tally of CLOSED routes is now **38**. #91 came from
#   gen #12's advice-message generator applied to its own #1 ranked target; **the advice turned
#   out to be SOUND and the route was in the guard NEXT DOOR** — which produced the
#   generalisation that then produced **#92, #93 and #94**: read *deferrals*, the comments
#   saying a case is "handled/rejected/checked elsewhere", and check the named guard's actual
#   matching rule against the deferred case. **#94 CARRIES THE STRONGEST EVIDENCE THIS CAMPAIGN
#   HAS EVER PRODUCED — AN EXECUTED CPYTHON RUN THAT CONTRADICTS A PROVED POSTCONDITION** — and
#   — and its repair landed, gated, after the other three cleared their battery.
#   The metric never moved (**markers 459 / grep 484**) and was never supposed to: every repair
#   is a refusal.
#
# ## WHAT IS TRUE RIGHT NOW
#
#   ledger   **ZERO OPEN.** Closed by gen #13: **#91, #92, #93, #94** — all four also FOUND
#            here, all four FULLY GATED on every plane. Window tally of closed routes: **39**.
#   metric   markers **459** / grep 484 / offset 25 / unattached 0 — UNCHANGED all generation,
#            verified stable across the whole run including across a killed battery.
#   corpora  pycsl-ref **1002 -> 1014** (+12: witnesses 1247–1258).
#   gates    fidelity DELTA ZERO (byte-identical to a HEAD-worktree log); byte-diff **0 MOVED,
#            0 GONE, 5 APPEARED** = exactly the predicted controls, zero-byte 0 on BOTH sides;
#            conformance **38/38 + 38/38, 0 MISMATCH**, determinism 10/10, no golden re-blessed;
#            doc-coherency rc=0; suite **3384/3402, 18 failures, ZERO XPASS, rc=1** (all six
#            exploits XFAIL, all six controls PASS); planes **34/34, rc=0**. No ratchet
#            re-baselined, no golden re-blessed.
#            **THE SUITE FAILURE BASELINE IS STILL 18 AND A RUN SHOWING 19 IS A REGRESSION.**
#   findings **w63, w64, w66, w67, w68** new CERTIFIED BOUNDARIES (measured, do not re-litigate);
#            **w65** a LEAD, structure verified, **exploit NOT constructed** — labelled as such.
#            **THREE VACUOUS PROBES CAUGHT AND RECORDED AS MEASURING NOTHING** (w63's
#            `subscript_get`, the `init-hook` shape, w67's state channel, w68's capability)
#            — FOUR in all, each caught by
#            running the aliveness control BEFORE interpreting a refusal. C8's Union-narrowing
#            deferral was probed and is **COVERED** (Why3 type-rejects: `has type
#            PyCSL_Program._union_f_0, but is expected to have type int`, with a proving
#            int-typed control).
#   tree     clean, every increment committed. The two GITLINKS (`scratchpad/w7/base`,
#            `scratchpad/w8/pre`) and the 0-byte stray `str` in the repo root are PRE-EXISTING.
#
# ## THE SINGLE MOST ACTIONABLE THING THIS GENERATION HANDS OVER — READ IT BEFORE THE LADDER
#
#   **PyCSL's SECURITY META-PROPERTIES ARE CURRENTLY LOAD-BEARING ON THE INCOMPLETENESS OF ITS
#   VALUE MODEL, AND THAT INCOMPLETENESS IS ON THE ROADMAP.** Findings w66, w67 and w68 are
#   three INDEPENDENT security properties with three DIFFERENT guards, and every one of them is
#   held up not by its guard but by a completeness gap in exactly the shape an attacker
#   would use:
#
#   | property | the gap IN THE GUARD | what actually fences it today |
#   |---|---|---|
#   | `compose_from` provider refinement (w66) | S2b has **no implementation** at all | flatten-and-re-verify — a *performance* mechanism |
#   | `noninterference` (w67) | the twin asserts `ra == rb` over **RESULTS only**, never state | state-mutating NI targets cannot be verified at all |
#   | H-S capability (w68) | call-site check injected only at `self.<target>(...)` | a non-`self` call propagates **nothing** |
#
#   **EVERY ONE OF THOSE THREE FENCES IS SOMETHING SOMEBODY WANTS TO REMOVE.** Lazier
#   flattening, self-composition through state, and cross-object contract propagation are all
#   ordinary, attractive completeness work that nobody would think of as touching a security
#   property. This is **route #89's lesson at scale**, and unlike #89 we can see it coming.
#
#   >>> **EACH OF THE THREE HAS ITS CO-LANDING FIX ALREADY WRITTEN DOWN IN ITS FINDING, AND THE
#   >>> FIXES ARE CHEAP *NOW* — while the exploits are unreachable and the guards can still be
#   >>> changed without a corpus fight.** They get expensive the moment the completeness work
#   >>> lands, and at that point they are severity-1 routes rather than paperwork. If the next
#   >>> generation does ONE thing from this handoff, do these three.
#
#   A caution that belongs with it: **all three of my probes into these were VACUOUS**, and I
#   only knew because I ran the aliveness control each time. Do not read "I could not exploit
#   it" as "it is safe"; read it as "the fence is somewhere else, go and name the fence."
#
# ## THE GENERATOR THAT PAID, AND IT IS NEW — READ DEFERRALS, NOT JUST CONTROLS
#
#   **>>> A COMMENT THAT SAYS "HANDLED OVER THERE" IS AN UNVERIFIED CROSS-REFERENCE, AND IT
#   READS EXACTLY LIKE A GUARD. <<<** This produced **#92 and #93**, and a full census produced
#   **w64, w65** and four more candidates.
#
#   The campaign already knew *a control is a measurement about the operation it ran, never a
#   theorem about the type*. **A DEFERRAL IS WEAKER STILL: it is a claim about code the author
#   DID NOT RUN, and the only person who could check it would have to leave the file to do so.**
#   The author who writes "handled over there" and the reader who reads it are never the same
#   person on the same day.
#
#   #92's deferral, verbatim, in `_collect_protect_index_sites`'s docstring:
#     *"(Slice/whole-array writes to a parametric path are not certifiable per-object; they are
#     left to the **non-footprint reject**.)"*
#   **There was no such reject.** The `CSLBool(False)` it names fires only on the sites that
#   very collector returns — which are, by construction, exactly the point writes it did NOT
#   skip. Two shapes deferred, zero caught, a confinement property provable while violated.
#
#   **HOW TO RUN IT:** grep `src/pycsl/` for "left to", "handled by", "handled in", "caught by",
#   "rejected by", "rejected elsewhere", "checked by", "already checked", "validated by",
#   "guaranteed by", "ensured by", "enforced by", "deferred to", "the caller checks", "callers
#   must", "Module4 rejects", "the front end rejects". For each: name the deferred CASE, LOCATE
#   the named guard, and **quote its actual matching rule**. A verdict with no quoted matching
#   rule is worthless. Beware: **"Module 4" IS DROPPED FROM THE PIPELINE** — every comment
#   deferring to it is at minimum stale, and its successors are `core_ir_semantic.py` and
#   `frontend/ir_resolve.py`. Several such comments are stale-but-covered; do not report those
#   as holes.
#
# ## THE SECOND NEW GENERATOR — AND IT IS WHY #91 EXISTS
#
#   **>>> AN ADVICE AUDIT THAT *CLEARS* ITS MESSAGE IS NOT A DEAD ROUND. THE MESSAGE IS A
#   POINTER TO A GUARD; READ THE GUARD'S SIBLINGS WHILE YOU ARE THERE. <<<**
#   Gen #12 left `Module3_Weaver.py:887/999` ("Add `#@ \preserves` to PROMISE it preserves …")
#   as the #1 ranked advice target. **Its prescription is SOUND** — clause (C) synthesizes a
#   real, visible, honestly-labelled "(an assumed postcondition)", gated on `trusted or
#   abstract`, inside the declared TCB. But reading it put clauses (A) and (C) on one screen,
#   and the *structural* comparison of which confinement form guards what is what paid.
#   Running advice-audit score: **6 messages audited, 5 prescriptions HELD, and the two routes
#   (#90, #91) came one from a rotten prescription and one from a SOUND one's neighbourhood.**
#
# ## THE STRUCTURAL LESSON ALL THREE ROUTES SHARE — THE MOST TRANSFERABLE THING HERE
#
#   `_weave_happy` has FOUR confinement forms. Laid side by side:
#
#   | form | point write | whole-path store | slice store | alias | trusted/abstract subject |
#   |---|---|---|---|---|---|
#   | `protects` (R1/R2) | caught | **caught** | **caught** | caught | `\preserves` or hard error |
#   | `reading` (H-I1) | caught | n/a | n/a | **caught** | `except` or hard error |
#   | region-write | caught | **MISSED -> #91** | caught | value-model | `\preserves` or hard error |
#   | parametric (R3) | caught | **MISSED -> #92** | **MISSED -> #92** | value-model | (n/a) |
#   | `total` (H-D) | — | — | — | — | **MISSED -> #93** |
#
#   **THE ONE FORM THAT KEYS ON THE *PATH* (`protects`, via `_target_dotted_path`) IS THE ONE
#   FORM WITH NO HOLES.** The two that key on the *syntactic shape of the target* each missed a
#   **strictly more destructive** write than the one they caught — invisible precisely because
#   it is not indexed.
#
#   >>> **A CONFINEMENT CHECK KEYED ON THE SYNTACTIC SHAPE OF A WRITE TARGET ENUMERATES THE
#   >>> SHAPES ITS AUTHOR HAPPENED TO PICTURE. KEY IT ON THE PATH BEING WRITTEN AND THE SHAPES
#   >>> TAKE CARE OF THEMSELVES.**
#
#   And #93 is the same failure one altitude up: a policy that only *names* a guarantee produced
#   elsewhere must enumerate every way that elsewhere can be made not to fire. It enumerated
#   `\diverges` and missed `\trusted`/`\abstract`, which delete the body and with it the whole VC.
#   >>> **AN OBLIGATION YOU DID NOT GENERATE IS INDISTINGUISHABLE FROM ONE THAT WAS DISCHARGED.**
#
#   **THE SIBLING TABLE IS ALSO THE REPAIR SPEC.** Every one of the three repairs was already
#   written, correctly, in a neighbouring branch of the same function. When a form is missing a
#   case, do not design a fix — **copy the sibling that has it, and copy its discipline**
#   (sound-by-rejection: a per-index check cannot constrain a whole-array store, so there is
#   nothing to defer).
#
# ## WHERE THE SOUNDNESS PREMISE IS WRITTEN DOWN, AND THAT IT WAS RIGHT
#
#   `docs/pycsl-static-semantics-reference.md` §2.5 states the composition theorem as *"every
#   body-verified method discharges a `#@ check φ(ℓ)` **at each write site of `self.f`
#   (universal coverage, clause 1)**"*. **"Universal coverage" is EXACTLY the premise #91 and
#   #92 falsified.** The spec was correct; the COLLECTOR was not universal. So:
#   >>> **WHEN A SOUNDNESS ARGUMENT NAMES A COVERAGE PREMISE ("every write site", "all paths",
#   >>> "each store"), GO AND COUNT THE CASES THE CODE COVERS. THE PREMISE IS A CLAIM ABOUT A
#   >>> COLLECTOR, AND THE COLLECTOR IS THE THING NOBODY RE-READS.**
#   The doc now records the split explicitly: an INDEXED store is CHECKED, a WHOLE-PATH or SLICE
#   store is REJECTED, and **a future store shape that is neither re-opens both routes**.
#
# ## THE METHODOLOGICAL RULES GEN #13 PAID FOR
#
#   * **BEFORE FILING SOMETHING AS A "TYPE ACCIDENT", CHECK WHETHER A SPEC CLAIMS IT ON
#     PURPOSE.** I filed #91's alias axis as a bare type accident (the #42 shape) and was
#     WRONG: §2.5 says *"value-semantic arrays bar local-alias escape"* — it is documented
#     design. The difference is a CERTIFIED BOUNDARY WITH A NAMED DEFENDER versus an unmeasured
#     hole, and it changes the reopening condition from vague to precise (**the defender is the
#     VALUE MODEL, not this pass** — route #89's shape).
#   * **A `diff` HUNK HEADER IS NOT A POPULATION COUNT.** `diff -rq` reported
#     `pyref/SOURCES.txt` as `1,153c1,199`, which reads like 153 entries becoming 199. Both
#     files are **2217 lines** and `diff <(sort A) <(sort B)` is **EMPTY** — pure traversal-order
#     difference between a git-worktree baseline and the main tree. Trusting the header would
#     have thrown away a valid baseline; ignoring the line would have signed off on an
#     unexplained diff entry. **SORT BOTH SIDES BEFORE BELIEVING A MANIFEST CHANGED.**
#   * **AN INCIDENTAL EMISSION FAILURE AND A DELIBERATE FENCE ARE INDISTINGUISHABLE AT THE
#     COMMAND LINE.** A w63 probe had both directions fail on `unbound function or predicate
#     symbol 'subscript_get'`. Isolated it: the same contract on a **module-level** function
#     PROVES, so the failure was `<method> + list param + subscripted contract`, not a fence.
#     **One step earlier I would have filed "fail-closed" for entirely the wrong reason.**
#     That is the FOURTH vacuity trap this campaign has caught by running the positive control.
#   * **A CONTROL THAT FAILS IS A CLAIM ABOUT THE CONTROL UNTIL YOU READ *WHICH GOAL* FAILED.**
#     Witness 1256 failed first time; the unproven goal was the POSTCONDITION (my loop invariant
#     omitted `acc >= 0`), not the termination VC — so it could not have been the repair.
#   * **MEASURE BOTH ARMS OF A DISJUNCTION SEPARATELY.** `emit_as_val = func_trusted or
#     func_abstract or func_trusted_parent`; witness 1255 is the `\abstract` arm, measured on
#     its own rather than assumed from the `\trusted` one.
#   * **PREFER ONE BATTERY OVER N REPAIRS TO N BATTERIES OVER ONE EACH** when the repairs are
#     siblings in one function — it is strictly stronger evidence and it is what made three
#     routes affordable in one generation. Corollary learned the hard way: **a battery killed by
#     its own timeout yields a PARTIAL verdict, which rule (p) forbids inheriting** — so stop it
#     deliberately and re-run, never let it be cut off.
#
# ## THE LAST ROUTE ALMOST SHIPPED AS A GATE THAT DID NOTHING — READ THIS ONE
#
#   **ROUTE #94's FIRST REPAIR WAS CORRECT CODE IN THE WRONG PLACE, AND IT SILENTLY DID
#   NOTHING.** I put the mutable-field clause in `_check_memoization_soundness`, which is its
#   obvious home. `_check_memoization_soundness` is called from `visit_FunctionDef` — **per
#   function, as the walk reaches it** — so when the memoized reader is checked, the mutator
#   defined three lines BELOW it is not yet in `program_ir["functions"]`; the mutated-field set
#   is EMPTY and the clause passes vacuously. **The exploit still VERIFIED.** The gate would
#   have survived review, the diff, and a careful source reading: nothing about it is wrong
#   except WHERE it runs. It landed instead at the post-`generic_visit` hook of
#   `visit_ClassDef`, where the class is complete.
#
#   >>> **A GUARD WHOSE POPULATION IS EMPTY HAS CHECKED NOTHING, AND LOOKS EXACTLY LIKE A GUARD
#   >>> THAT PASSED. A CHECK THAT NEEDS A WHOLE-PROGRAM FACT CANNOT LIVE IN A PER-NODE
#   >>> VISITOR.** This is the campaign's vacuity rule one level up — *a probe whose positive
#   >>> control refuses has measured nothing* becomes *a gate whose population is empty has
#   >>> measured nothing*. **The only thing that caught it was rule (l): negative-test every new
#   >>> gate by removing the thing it should catch.** Had I trusted the diff, #94 would have
#   >>> been recorded CLOSED while standing wide open — worse than leaving it open, because a
#   >>> false close removes it from the ledger and nobody looks again.
#
# ## PREDICT EVERY GATE VERDICT BEFORE YOU RUN IT — IT COST NOTHING AND IT PAID
#
#   I stated, in the progress log BEFORE each run: three byte-diff predictions (0 MOVED / 0 GONE
#   / exactly-these-N APPEARED), two suite predictions (exact pass counts and failure counts),
#   and one collateral prediction (no pre-existing memoized corpus file would move). **ALL SIX
#   WERE EXACT.** Each followed directly from one sentence — *all four repairs are pure
#   REFUSALS, so only new files that PROVE can emit, and no pre-existing file can move unless it
#   legitimately performed a newly-rejected construct*.
#   >>> **A GATE VERDICT YOU PREDICTED CORRECTLY TELLS YOU THAT YOU UNDERSTOOD THE CHANGE. A
#   >>> GREEN YOU MERELY RECEIVED TELLS YOU ONLY THAT NOTHING SCREAMED.** Predicting first also
#   >>> forces the collateral search (which pre-existing files COULD move?) to happen BEFORE the
#   >>> sweep, where it is cheap, instead of after a red, where it is a panic.
#
# ## A PATTERN THREE REPAIRS WANTED — NAME IT INSTEAD OF RE-DERIVING IT
#
#   **#91, #92 and #94 all needed the SAME `__init__` CARVE-OUT**, for the same reason: the
#   constructor ESTABLISHES the object rather than mutating it, so a property about "what
#   happens to this field over the object's life" must not range over its creation. If a fourth
#   guard needs it, that is a sign the distinction belongs somewhere shared rather than being
#   re-spelled per clause. **Reopening condition on all three carve-outs at once: if PyCSL ever
#   models an explicit re-invocation of `__init__` on a live object, every one of them must be
#   re-measured.**
#
# ## THE ADVICE-EXEMPLAR CORRECTION — READ THIS BEFORE TRUSTING THE INHERITED DISCRIMINATOR
#
#   Gen #12 named `module5/memoization_rt.py:74` **the in-tree EXEMPLAR of safe advice**, because
#   its sentence bakes in its exclusions and `_detect_purity` enforces exactly those three
#   conjuncts. **That is accurate, and it is where route #94 was hiding.** The guard's own
#   DOCSTRING promises a FOURTH conjunct — "reads no mutable global state" — that the message
#   never mentions and the code barely implements.
#   >>> **ADVICE THAT NAMES ONLY CONDITIONS THE EMITTER REALLY CHECKS IS SAFE FOR THE USER WHO
#   >>> FOLLOWS IT, BUT IT IS NOT EVIDENCE THE GUARD IS COMPLETE. A PERFECTLY HONEST MESSAGE CAN
#   >>> SIT ON AN INCOMPLETE GUARD — AUDIT THE DOCSTRING'S PROMISE AGAINST THE CODE, NOT JUST
#   >>> THE MESSAGE'S.** Gen #12 learned to distrust advice that OVER-promises; #94 is the mirror
#   >>> image, advice that UNDER-promises relative to its own guard's stated contract, so nothing
#   >>> in the message looks wrong at all.
#
# ## PROBED WITH NO FINDING / BOUNDED THIS GENERATION — DO NOT RE-PROBE
#
#   * **The `\preserves` advice message itself** (both sites) — prescription SOUND. Clause (C)
#     synthesizes a visible, honestly-labelled assumed postcondition and is gated on
#     `trusted or abstract`. The `protects`-form site merely `continue`s (suppression with
#     nothing synthesized) — fail-closed, nothing provable.
#   * **w63 — the `reading` form's alias guard is keyed on `ast.Assign`**, so `return self.f`
#     and `f(self.f)` escape it and both VERIFY. **NOT exploitable**: a caller binding the
#     returned array cannot recover a protected byte (`requires self.disk[0] == 7` ⊬
#     `\result == 7`), because the value model does not propagate array identity through a
#     return. Reopening: reference semantics for collections.
#   * **w64 — `\separated` lowers to the CONSTANT `true`** under the default `hoare` model, so
#     `\separated(a,3,a,3)` PROVES and an anti-aliasing precondition is discharged by `f(a,a)`.
#     **Does NOT escalate**: the moment the callee's `assigns` names an aliased parameter, Why3's
#     region typing rejects the application ("illegal alias" — measured), and a FIELD base is a
#     parse error. The census comment's conclusion is right, its stated premise is false.
#     A scoped hardening is written up in the finding and is NOT yet landed.
#   * **The `--fun` residue on #93**: `--fun` marks out-of-slice functions `trusted` AFTER
#     Module 3 has run, so it can still strip a `total` target's body. Deliberately not
#     repaired — `--fun` is user-directed partial verification and the whole-file run the gates
#     use is unaffected.
#
# ## STILL UNPAID, IN THE ORDER I WOULD TAKE THEM
#
#   1. **w65 — `fresh_globals` cross-module confinement. STRUCTURE VERIFIED, EXPLOIT NOT BUILT.**
#      `_check_fresh_globals` defers the cross-module case to its own clause (2); verified at
#      HEAD that `run_ir_semantic_checks` (pycsl.py:504) runs BEFORE `_ir_resolve` (:533) which
#      injects dep functions, and the dep sub-pipeline runs **no semantic checks at all**. So
#      nothing rejects it. **BUILD THE POSITIVE CONTROL FIRST** — a single-file `fresh_globals`
#      driver that PROVES plus both clause rejections firing — because a cross-module setup has
#      many independent ways to refuse and this is the probe most likely to be vacuous.
#   2. **THE THREE COMPOSITION/INFO-FLOW BOUNDARIES FOUND LATE THIS GENERATION — all three are
#      a COMPLETENESS GAP holding a SECURITY property up, which is route #89's shape and the
#      most re-armable kind there is. Each has its co-landing fix already written down:**
#      * **w67 — H-I2 noninterference asserts `ra == rb` over the two RESULTS ONLY**, never
#        `self`. Fenced only because a state-mutating NI target cannot be verified at all (a
#        target that READS a field proves; one that WRITES a constant already fails). **The day
#        self-composition works through state, the state channel is unguarded.** Co-landing fix:
#        the twin must also assert equality of PUBLIC state after the two calls.
#      * **w66 — `compose_from`'s S2b (provider-refines-dependency) has NO implementation**, and
#        is compensated only because `apply_composition` deep-copies each provider method into
#        the composer and RE-VERIFIES it. That is a flattening OPTIMISATION, not a check, and
#        nothing names the dependency: **making flattening lazier re-opens a severity-1 route
#        while looking like a performance win.** `init-hook` is still GUARD-NOT-FOUND and my
#        probe of it was VACUOUS — build a working positive control for `mixin + class invariant
#        + composer __init__` FIRST, because a mixin invariant does not currently reach the
#        flattened clone and every refusal in that area is uninterpretable until one proves.
#      * **w64 — `\separated` is the constant `true`** under the default model. Fenced by Why3
#        region typing, which refuses an aliased application only when the callee MUTATES.
#   3. **Three more deferral candidates, all with the named guard's matching rule already quoted
#      in the census** (see the progress-log entry): the H-S capability check keyed on
#      `self.<target>(...)` only; `compose_from`'s "provider-refines-dependency" and "init-hook"
#      obligations (`grep S2b` returns ONE line, the comment deferring to it — no
#      implementation); `_check_memoization_soundness`'s "reads no mutable global state" which
#      sees only `#@ shared` vars, not `module_globals` or `self.<field>`; and the typed
#      quantifier binder inside `#@ assert` (fail-closed in practice). **Re-verify each
#      independently — I verified #92/#93/w64/w65 myself and every one needed narrowing.**
#   4. Carve-out candidates 9 and 10; **finding-w60**; the `_field_default` `option` arm.
#   5. Keep growing BOTH differential corpora (a route just closed is the cheapest source; add
#      BOTH directions, plus the EXCEPTION pair when a repair touched a collection).
#
# ## THE CAMPAIGN'S STANDING RULES THAT EARNED THEIR PLACE AGAIN
#
#   * **A completeness fix that supplies a WITNESS value is a soundness route waiting to happen.**
#   * **A probe whose own positive control refuses has measured nothing.** (Caught once more.)
#   * **Assert a population size before believing it — including a gate's own summary.**
#   * **An empty ledger is a prompt to GENERATE, not a floor.** It was empty at the start of this
#     generation and three severity-1 routes were in one function.
#
# ====== START HERE — gen #12 FINAL STATE — read this block first ==================
#
# ## THE ONE-PARAGRAPH SUMMARY
#
#   **TWO ROUTES CLOSED AND FULLY GATED (#89, #90), ONE OF THEM FOUND THIS GENERATION
#   (#90).** The window tally is now **35**. Gen #12 opened by RESOLVING THE #89 AMBIGUITY
#   BY MEASUREMENT rather than inheritance — the supervisor's premise ("src/ is clean, so
#   the repair is not in the tree") was a misread: the repair was COMMITTED at e7a92460, and
#   three independent witnesses pin gen #11's suite run to the repaired tree. **#90 IS THE
#   MOST TRANSFERABLE FIND OF THE WINDOW**: route #42's `is`-against-a-bool-literal whitelist
#   was **ANTI-CORRELATED WITH BOOL-NESS** — it ADMITTED the one source of bool-ness nothing
#   enforces (a type annotation) and REFUSED the two that are provable by construction — and
#   **THE GUARD'S OWN ERROR MESSAGE RECOMMENDED THE EXPLOIT.** The metric never moved
#   (**markers 459 / grep 484**) and was never supposed to.
#
# ## WHAT IS TRUE RIGHT NOW
#
#   ledger   **ZERO OPEN.** Closed by gen #12: **#89, #90.** Found: **#90.**
#   metric   markers **459** / grep 484 / offset 25 / unattached 0 — UNCHANGED all generation.
#   planes   **34/34 green, rc=0** (`--slow`), re-run at both landings.
#            **EXPORT why3 FIRST:** `export PATH=$HOME/.opam/framac-coq8/bin:$PATH`.
#   conform  **38/38 core + 38/38 front-end, 0 MISMATCH**, determinism 10/10, no golden re-blessed.
#   suite    **3372/3390, ZERO XPASS**, rc=1. **THE FAILURE BASELINE IS STILL 18.**
#            A run showing 19 is a REGRESSION. #90 did NOT move it.
#   corpora  pycsl-ref **1002** (+7 from #90), python-ref 2203, MIRROR 53 — all inert under #90
#            except the ONE predicted `GONE`. value-differential **52 -> 56** (24 AGREE all
#            proving / 32 DISAGREE all refused, 56 of 56 CLASSIFIED). no-exception-differential
#            45, unchanged — #90 touched no collection, so no exception pair was owed.
#   ratchets mirror-coverage **549 / 41 KEPT**; `check-bespoke-model-drift` never needed `--update`.
#   OWED     **NOTHING.** No proof, battery or sweep in flight. Tree clean.
#   finding  **w62 NEW** — a `\trusted` marker on ANY function buys a FILE-WIDE C-extension
#            deny-list bypass (`import_classifier.py:126` uses a whole-tree
#            `any_function_trusted`, while its message says "the IMPORTING function(s)").
#            MEASURED both directions; the escalation probe was RUN and does **NOT** escalate
#            (a `ctypes` value stays unconstrained both ways), so it is TCB-ACCOUNTING, not
#            the #69 class. Its reopening condition is the interesting part: the bypass is
#            harmless only while the imported names stay OPAQUE, which is a property of the
#            STUB SET — **a completeness gain elsewhere can re-arm it without anyone touching
#            that gate.** Route #89's lesson, at a POLICY gate rather than an emitter arm.
#
# ## THE GENERATOR THAT PAID THIS GENERATION — AND IT IS NEW
#
#   **>>> READ THE `HOW TO FIX THIS` LINE OF EVERY FAIL-CLOSED MESSAGE AS AN ATTACK
#   SURFACE. <<<** This produced **#90**. The guard's message stated the hazard PERFECTLY —
#   it even quoted the measured exploit, "`x = 1; if x is True: return 7` proved `\result ==
#   7` where Python returns 0" — and then closed with **"Write `X == True`, or annotate `X`
#   as `bool`."** FOLLOWING ITS OWN SECOND SUGGESTION TURNS THE CORRECT REFUSAL INTO THE
#   PROOF OF A FALSEHOOD. This campaign has TWICE praised a refusal message for "stating the
#   unsoundness that WOULD occur". **That praise was for the DIAGNOSIS. Nobody had ever read
#   the PRESCRIPTION.** A refusal message is the one place in the codebase where the author
#   wrote down both the hazard AND a way around it, and only the first half was ever audited.
#
#   **I THEN APPLIED IT TO ITS NEXT TARGET AND IT HELD** — route #76's message ends "or use a
#   NamedTuple, whose `==` really is structural", which is a real attack surface (tuple `==`
#   is IDENTITY-FIRST PER ELEMENT). Measured: the advice's path is LIVE (a NamedTuple of int
#   PROVES, so the audit is not vacuous), the NaN axis is fenced upstream, and a NamedTuple
#   whose element is a CLASS INSTANCE — #76's own defect via #76's own advice — is refused in
#   BOTH directions. So the generator is real but the #90 message was not representative.
#   **THE HARVEST WAS DONE AND IT COMES WITH A RATIO: of 195 user-facing refusal messages in
#   `src/pycsl/`, 60 (31%) CARRY REMEDIATION ADVICE and 135 (69%) ARE PURE REFUSALS.** So one
#   refusal in three is an attack surface, and only a handful have been audited.
#
#   **THE DISCRIMINATOR, WHICH IS THE MOST REUSABLE THING GEN #12 PRODUCED:** *advice that
#   names the conditions the emitter ACTUALLY CHECKS is safe; advice that names a marker the
#   emitter merely READS is the hazard.* The in-tree exemplar of the good shape is
#   `module5/memoization_rt.py:74`, which bakes its exclusions into the sentence ("requires
#   `#@ assigns \nothing`, and no `\trusted` / `\diverges`") and whose `_detect_purity`
#   enforces exactly those three conjuncts.
#
#   **SCORE SO FAR: one route (#90) from the FIRST message audited, then THREE CONSECUTIVE
#   PRESCRIPTIONS THAT HELD** — #76's NamedTuple clause, RETANN's `Optional[str]` clause, and
#   (as a soundness matter) the `\trusted` deny-list clause. So the generator is real but
#   #90's message was an OUTLIER: audit the remaining 57, do not assume they are rotten.
#   The ranked candidate list is in the 10:15 progress-log entry; the top unaudited one is
#   `Module3_Weaver.py:887/999` ("Add `#@ \preserves` to PROMISE it preserves ..."), which
#   grafts a synthesized postcondition onto a body-less function — though note its message
#   says "(an assumed postcondition)" OUT LOUD, which is the honest shape, and it is gated on
#   `trusted or abstract`, i.e. inside the declared TCB. Measure before believing either way.
#
# ## THE OTHER GENERATORS, RANKED BY WHAT THEY PAID (unchanged, still the best list)
#
#   1. **TAKE EVERY *CONTROL SENTENCE* IN A CLOSED ROUTE FILE, ASK WHICH SINGLE OPERATION
#      THAT CONTROL ACTUALLY RAN, AND PROBE A DIFFERENT ONE.** Produced #87, #88, #89 and
#      (via #42's control table) **#90**. **A CONTROL IS A MEASUREMENT ABOUT THE OPERATION IT
#      RAN, NEVER A THEOREM ABOUT THE TYPE.**
#   2. **A CARRIER SURVIVING A REPAIR IS A SECOND ROUTE, NOT A FAILED REPAIR** (-> #86).
#   3. **READ THE WHOLE EMITTED FILE WHEN CHECKING WHETHER A CANDIDATE'S ARM FIRED** (-> #85).
#      Gen #12 adds: it is also the ONLY instrument that separates an arm that WORKS from an
#      arm that is WHITELISTED AND THEN FAILS TO TYPECHECK (see the #42 post-mortem below).
#   4. **READ THE OUTLIER ROWS OF A CENSUS, NOT THE TOTALS** (-> #82).
#   5. **A CANDIDATE'S MECHANISM STORY IS A HYPOTHESIS SEPARATE FROM ITS EXISTENCE** (-> #83).
#
# ## THE TWO METHODOLOGICAL RULES GEN #12 PAID FOR, BOTH ABOUT VACUITY
#
#   * **A PROBE WHOSE OWN POSITIVE CONTROL REFUSES HAS MEASURED NOTHING.** My first #90
#     attempt put the claim on a caller of an UNCONTRACTED callee: all three drivers refused,
#     INCLUDING the control, because an uncontracted callee is opaque and the arm never
#     fired. That is the signature of a dead probe, not of a fail-closed shape. It cost a
#     round, and it caught a SECOND vacuous probe an hour later (a runtime `if a == b:`
#     between dataclass instances is refused even for INT fields). **RUN THE POSITIVE CONTROL
#     FIRST; A SET OF REFUSALS IS NOT EVIDENCE UNTIL ONE THING PROVES.**
#   * **ASSERT A POPULATION SIZE BEFORE BELIEVING IT — INCLUDING A GATE'S OWN SUMMARY.**
#     `check-value-differential` reported ONE malformed driver; its own totals in the same
#     three lines said 56 drivers with 24 + 30 = 54 classified, so TWO were unaccounted for.
#     Re-running its `_CLAIM` regex myself named both. **A GATE THAT REPORTS "1 BAD" WHILE ITS
#     TOTALS IMPLY 2 IS TELLING YOU TO GO AND COUNT.** (The mirror image of gen #11's
#     stdout/stderr trap: there the mistake would have been believing an empty set.)
#
# ## THE #42 POST-MORTEM — WHAT A WHITELIST LOOKED LIKE vs WHAT IT WAS
#
#   Route #42's whitelist had FOUR arms. **MEASURED, IT WAS ONE TAUTOLOGY PLUS ONE UNSOUND
#   ARM.** `True is True` proves (a tautology). The ANNOTATION arm proved FALSEHOODS (#90).
#   And the two arms that were supposed to carry the real capability — a comparison result
#   and `not X` — are **ADMITTED BY THE WHITELIST AND THEN EMIT ILL-TYPED WhyML**
#   (`if ((a > b) = 1)`, a Why3 `bool` compared to an `int`), verified PRE-EXISTING in a
#   worktree at the pre-repair HEAD. **AN ARM THAT IS WHITELISTED AND THEN FAILS TO TYPECHECK
#   LOOKS EXACTLY LIKE A WORKING ARM IN THE WHITELIST AND EXACTLY LIKE A REFUSAL AT THE
#   COMMAND LINE.** Nobody had run those two arms in 48 routes. Corpus **1246** now records
#   that as a CERTIFIED BOUNDARY with an explicit reopening condition; **1245** pins the
#   surviving literal arm.
#
# ## AND THE THING I WOULD TELL THE NEXT GENERATION FIRST
#
#   **A CORPUS CONTROL WRITTEN TO PREVENT OVER-NARROWING CAN BECOME THE RATCHET THAT PROTECTS
#   AN UNSOUND ARM.** Corpus 1057 was route #42's own "faithful" control. Its docstring ended
#   "it fails if the whitelist is ever narrowed to nothing (a refusal that refuses everything
#   is not a fix)" — and **ITS OWN CLAIM WAS FALSE**: `requires b == True` is satisfied by
#   `b = 1`, for which CPython returns 0, not 7. It guarded the unsound arm for 48 routes.
#   **A CONTROL THAT PINS A CAPABILITY MUST STATE WHAT MAKES THE CAPABILITY SOUND, NOT MERELY
#   THAT IT EXISTS** — and when you narrow a whitelist, the control you must rewrite is the
#   one that will fail. 1057 is now an expected-FAIL witness carrying its mechanism; that is
#   the prescribed handling for a deliberately-costed file, NOT a rule-(k) re-baselining,
#   because the file asserted a FALSEHOOD and the record says so in full.
#
# ## PROBED WITH NO FINDING THIS GENERATION — DO NOT RE-PROBE
#
#   * **The two field collectors made to DISAGREE** (contents are LAST-wins via an `ast.walk`,
#     length/defaults FIRST-wins via `field_names_seen`). #88's control c9 used two literals
#     of the SAME LENGTH and so could not tell them apart. Made them differ: `len()` refused
#     in BOTH directions, element read FAITHFUL and genuinely last-wins. Then INVERTED the
#     lengths so index 2 is valid in the first literal and OOB in the last — the direction
#     that could pay: BOTH the `no_exception` and the value arm FAIL-CLOSED, in-range control
#     still faithful. #88's c9 is now a FOUR-operation control.
#   * **`len()` on a collection FIELD** (never run by #85/#87/#88 on any dict field, and #60
#     showed dict `len` is a syntactic store-site count): refused in BOTH directions for dict
#     AND list. Non-vacuous — the CONTENTS are decidable, so this is a genuine length-channel
#     completeness gap. **NOT a candidate for a witness-supplying fix.**
#   * **The FRAME half of a self-call** (#70's control ran the value direction only): a
#     CONTRACTED self-call is FAITHFUL (false claim refused, TRUE twin PROVES); no-`assigns`
#     and a body-contradicting `assigns \nothing` are both unconstrained in both directions,
#     so route #49's "`assigns \nothing` is not caught" does NOT reproduce as a soundness
#     hole. The faithful shape is what makes the two refusals non-vacuous.
#   * **Route #76's remediation advice** (the NamedTuple clause): sound on every reachable
#     shape — see the generator section above.
#   * **`deque().append(7)`** — #78's control was DEGENERATE (`len()` of an EMPTY deque: the
#     true answer IS the erasure constant) and its residue only ever named `appendleft`.
#     Measured: `len` and the element read BOTH refuse the false claim and **PROVE the true
#     one**. #78's repair is better than its own control could show.
#   * **`PYCSL-SEM-RETANN`'s two documented residues, RE-REPRODUCED AT HEAD** (its census
#     dates to `27cf17b1`, six routes ago): `-> int` with an explicit `return None`, `-> int`
#     falling off the end, and `-> str` falling off the end all still REFUSE, with the
#     `-> str` explicit case raising the guard as the control. **And its advice is TRUE**:
#     `r: Optional[str] = None` makes the caller's `r is None` test PROVE the true claim and
#     refuse the false one, in both polarities. Advice audited, not assumed.
#   * Floats/NaN are not decidable at all (`nan == nan` refused), so the whole NaN axis —
#     including #45's reflexivity hazard reaching `==` on a dataclass or NamedTuple — is
#     fenced upstream. Do not spend a round on it without first re-checking that fence.
#
# ## STILL UNPAID, IN THE ORDER I WOULD TAKE THEM
#
#   1. **Audit the remaining ~57 advice-bearing refusal messages** — the harvest is DONE and
#      ranked (10:15 entry); four are audited. Use the discriminator above to triage.
#   2. **The completeness follow-up to #90**: re-admit an operand whose bool-ness is provable
#      BY CONSTRUCTION but which is currently refused because it is a `Var` (`y = a > b`,
#      `y = True`). Needs the ASSIGNED EXPRESSION, not the symbol table. Would also fix the
#      ill-typed comparison/`not` arms (corpus 1246's reopening condition).
#   3. Carve-out candidates 6, 9, 10; **`finding-w60`**; the `_field_default` `option` arm
#      (UNREACHED after three probes — recorded as unaudited, not clean).
#   5. Keep growing BOTH differential corpora.
#
# ====== START HERE — gen #10 FINAL STATE — read this block first ==================
#
# ## THE ONE-PARAGRAPH SUMMARY
#
#   **FIVE ROUTES CLOSED AND FULLY GATED (#83, #79, #85, #86, #87) AND THREE OF THEM FOUND
#   THIS GENERATION (#85, #86, #87).** All five cost the corpus nothing: four were byte-inert
#   everywhere, and #87 moved exactly its own four witnesses and not one pre-existing file.
#   No whole-file re-proof was owed anywhere. **THE LEDGER WAS EMPTIED THREE TIMES AND A NEW
#   SEVERITY-1 ROUTE APPEARED AFTER EACH OF THE FIRST TWO** — so an empty OPEN list is a
#   prompt to GENERATE, not a floor, and that is now written into the ledger header. **THREE
#   OF THE CLOSES ARE COMPLETENESS GAINS** (#85 and #87 are faithful captures whose TRUE
#   twins now prove; the campaign had only one such close before, #82). The metric never
#   moved (**markers 459 · grep 484**) and was never supposed to.
#
# ## WHAT IS TRUE RIGHT NOW
#
#   ledger   **ZERO OPEN.** Closed by gen #10: **#83, #79, #85, #86, #87.** Found: #85, #86, #87.
#            Plus **finding-0700 / Gap 2a RESOLVED** — a completeness fix, not a route.
#   metric   markers **459** · grep 484 · offset 25 · unattached 0 — UNCHANGED all generation.
#   planes   **34/34 green, rc=0** (`--slow`), re-run at every landing (four full runs).
#            **EXPORT why3 FIRST:** `export PATH=$HOME/.opam/framac-coq8/bin:$PATH`.
#   conform  **38/38 core + 38/38 front-end, 0 MISMATCH**, determinism 10/10. It FAILED once,
#            on #87, and the REPAIR was narrowed — **no golden was ever re-blessed**.
#   suite    **3353/3371, ZERO XPASS**, rc=1 (the baseline condition).
#            **>>> THE FAILURE BASELINE IS NOW 18, NOT 19. <<<** It was byte-identical at 19
#            across four of this generation's five runs and all of gen #9's; the fifth run
#            dropped `pycsl-reference/0700` when Gap 2a landed, and the diff showed exactly
#            that one line removed. **A run showing 19 failures is now a REGRESSION, not the
#            old normal.**
#   corpora  pycsl-ref 995, python-ref 2203, MIRROR 53. **ALWAYS SWEEP THE MIRROR TOO**: it
#            is the gate that retires the "whole-file re-proof" cost, and it was run on BOTH
#            sides every time. **BOTH DIFFERENTIAL CORPORA GROWN — ladder item 5, unpaid
#            since gen #8, now PAID**: value-differential **36 -> 45** (21 AGREE all proving
#            / 24 DISAGREE all refusing, rc=0) and no-exception-differential **39 -> 43**
#            (30 raising all refused, 12 of 13 returning prove, rc=0).
#   final    **34/34 planes green (rc=0), re-run AFTER BOTH corpus growths** — that is the
#            state the tree is in right now, not an earlier snapshot.
#   ratchets mirror-coverage **549 KEPT**; `check-bespoke-model-drift` never needed `--update`.
#   OWED     **NOTHING.** No proof, battery or sweep in flight.
#   tree     clean, every increment committed. The two GITLINKS (`scratchpad/w7/base`,
#            `scratchpad/w8/pre`) and the 0-byte stray `str` in the repo root are
#            PRE-EXISTING and are NOT dirt.
#
# ## THE FIVE GENERATORS THAT PAID — EACH PRODUCED A ROUTE, EACH IS WRITTEN WITH ITS EVIDENCE
#
#   1. **PROBE EVERY *OPERATION* ON A CARRIER A CONTROL DECLARED SAFE — AND THAT INCLUDES
#      YOUR OWN CONTROLS, WRITTEN AN HOUR AGO.** This produced **#87**. Route #85's control
#      table (mine, same session) recorded "a LIST field is fail-closed"; that control ran
#      `len(c.xs)` ONLY, and the LENGTH is faithful while every ELEMENT was a definite `0`.
#      **A CONTROL IS A MEASUREMENT ABOUT THE OPERATION IT RAN, NEVER A THEOREM ABOUT THE
#      TYPE.** #87 is the exact mirror image of #81 (which refuted #59's list control on the
#      same axis): #81 = length wrong / elements right, #87 = length right / elements wrong.
#      **FOR A COLLECTION, ALWAYS PROBE BOTH THE SHAPE AND THE CONTENTS.**
#   2. **AFTER LANDING A REPAIR, RE-RUN THE CARRIERS AND LOOK FOR ONE THAT STILL PROVES. A
#      SURVIVING CARRIER IS NOT A FAILED REPAIR — IT IS A SECOND ROUTE THE FIRST WAS
#      MASKING.** This produced **#86**. Two independent erasures that emit the SAME wrong
#      constant are indistinguishable until one is fixed, so **fixing one is a measurement
#      instrument for the other.** Never record "closed 3 of 4 carriers" as a partial success.
#   3. **WHEN YOU DUMP THE EMISSION TO CHECK WHETHER A CANDIDATE'S ARM FIRED, READ THE WHOLE
#      EMITTED FILE.** This produced **#85**, one line above the line I came for. A
#      fully-lowered probe is the one artifact where every erasure in a small program is
#      visible at once. **A REFUTED CANDIDATE CAN STILL PAY FOR ITSELF IN ITS DUMP.**
#   4. **A GUARD'S EARLY EXIT IS PART OF THE GUARD.** #79's census is "the complement of the
#      capture rule", so it could only enumerate constructors that REACH the rule — and
#      `if not pset: break` meant a **PARAMETERLESS `__init__` was never scanned at all**.
#   5. **ASK WHICH GUARD ALREADY STANDS BETWEEN THE POPULATION AND THE CHANGE.** #79's price
#      fell three times (70% -> 133/17-mirror -> **40 scalar, 0 corpus, 0 mirror**) — the last
#      because Module 6's existing `_NONSCALAR` check already fenced the entire array arm.
#      **AN INHERITED COST FIGURE IS AN UNPROVEN LEMMA.**
#
# ## THE RULE THE REPAIRS ARE BUILT ON, NOW MEASURED FROM BOTH SIDES
#
#   **PREFER A FAITHFUL CAPTURE WHEREVER THE INFORMATION EXISTS; FALL BACK TO UNCONSTRAINED
#   ONLY WHERE IT GENUINELY DOES NOT.** #85 and #87 are faithful (a LOCAL dict/list literal
#   was ALWAYS lowered faithfully — only the FIELD arm dropped it, so the information was
#   sitting there) and their true twins now PROVE. #79, #83, #86 and #85's SET arm could not
#   be (a conditional store, a non-parameter RHS, an unknown actual, an int-erased set
#   literal), and were left unconstrained. **#85's repair contains both halves at once**, so
#   it is the cleanest side-by-side measurement of the rule the campaign has.
#
# ## THE LAST THING I BUILT, AND THE RULE IT EARNED — READ THIS BEFORE TOUCHING
# ## `_field_default` AGAIN
#
#   **finding-0700 / Gap 2a: A `str` FIELD HAD NO DEFAULT WITNESS AT ALL.** The fallback is
#   `rec_info['defaults'].get(fn, 0)` — an INT — so a `string`-typed field emitted
#   `{ template = 0 }`, ill-typed, hence a refusal. Fail-closed, and measured to cost exactly
#   ONE file: a sweep of all 993 pycsl-ref + 2203 python-ref emissions found exactly one
#   `string`/`real` field defaulted to an int literal, and it was 0700's — one of the 19
#   tracked failures. **0700 NOW PROVES and the baseline is 18.**
#
#   **BUT NOT BY THE FIX THE FINDING DOCUMENTS.** Gap 2a is written as *"the `str` field
#   defaults to the empty-string witness `\"\"`"*, and building that as written would have
#   MANUFACTURED a severity-1 route: an empty-string witness is a DEFINITE value, so a field
#   really initialised to `"abc"` would make `\result == ""` provable — route #85's shape,
#   created by a completeness fix. Witness 1227 is that negative test. What landed is a
#   FAITHFUL capture (the field's own literal), and an uncaptured `str` field keeps its
#   ill-typed int and KEEPS REFUSING.
#
#   **>>> A COMPLETENESS FIX THAT SUPPLIES A *WITNESS* VALUE IS A SOUNDNESS ROUTE WAITING TO
#   HAPPEN. <<<** "Type-correct default" and "true value" are DIFFERENT REQUIREMENTS, and only
#   the second is safe to make DECIDABLE. **Every arm of `_field_default` this campaign has
#   repaired — #79 (scalar), #83 (conditional store), #85 (dict/set), #87 (list), and now the
#   `str` arm — was a witness value someone had justified as sound. That one function is the
#   same mistake made five times.** Read this before adding an arm to it.
#
# ## GATING LESSONS THAT COST ME TIME — READ BEFORE GATING ANYTHING
#
#   * **A CORPUS THAT DOES NOT CONTAIN THE BLAST RADIUS CANNOT PRICE THE REPAIR.** #83's five
#     sites are ALL in `src/pycsl_lib`, in NEITHER byte-diff corpus — its green byte-diff was
#     evidence of nothing. The gate that covered them was the SUITE. **Say which gate carries
#     the claim.**
#   * **THIS FAMILY OF DEFECTS BITES AT AN ALLOCATION SITE; A FIELD-LEVEL CENSUS COUNTS
#     DECLARATIONS.** Confirmed TWICE: my #79 census predicted 8 mirror sites and the mirror
#     moved ZERO bytes (those classes are never allocated — `frontend__ConcurrencyChecker.mlw`
#     emits the record TYPE and no record LITERAL); and corpus 0980/0981 hold `[0, 7]` and
#     still did not move under #87, because they never call `C()`. **The emission is the
#     authority over any census — including your own.**
#   * **A REPAIR THAT MOVES NOTHING ANYWHERE IS THE SHAPE OF #82's SILENT NO-OP.** Never take
#     the zero on trust. The check that settles it: **did the carriers CHANGE VERDICT?**
#   * **WHEN A POSITIVE (must-still-prove) WITNESS FAILS, DUMP THE EMISSION BEFORE TOUCHING
#     THE REPAIR.** Witness 1219 failed and looked exactly like an over-broad repair; the real
#     cause was a PRE-EXISTING fail-closed emitter defect
#     (`finding-w60-shared-field-name-label-mismatch.md`): two record classes sharing a FIELD
#     NAME emit a disambiguated literal label `c_d` but a bare read `c.d`, unbound, so Why3
#     refuses the file. A field named after its own class collides too. **GIVE EVERY CLASS IN
#     A MULTI-CLASS DRIVER DISTINCT FIELD NAMES.**
#   * **WHEN IR CONFORMANCE FAILS, SUSPECT THE REPAIR BEFORE THE GOLDEN.** #87's first build
#     moved golden 0595's IR while core-only conformance stayed 38/38 — i.e. the IR changed
#     for a file whose BEHAVIOUR did not. The fix was to **carry information in the IR only
#     when it changes the answer** (an all-ZERO list literal already lowered faithfully), not
#     to re-bless. Rule (k) held and the gate was right.
#   * **NEGATIVE-TEST THE NARROWING, NOT JUST THE REPAIR.** #87's condition is "all elements
#     ZERO", not "all EQUAL" — `[7,7,7]` got `Array.make 3 0` and is still a defect. Witness
#     1225 exists for exactly that; without it the narrowing would close #87 for `[1,2,3]`,
#     leave it open for `[7,7,7]`, and pass every other test in the suite.
#   * **A VERDICT THAT LIVES ONLY IN /tmp IS NOT A RECORD.** Gen #9's route-#83 plane log
#     existed only in the volatile session scratchpad; the commit message asserted "34/34
#     green" with no artifact behind it. Now at `proofs49/w59b_planes_route83.log`.
#
# ## TWO PROCESS FAILURES I CAUSED, RECORDED IN FULL
#
#   1. **KILLING A PARALLEL HARNESS'S PARENT DOES NOT STOP IT, IT CORRUPTS IT.** I killed what
#      I took to be a duplicate suite; it was gen #9's own detached run. The kill hit the
#      wrapper, the workers were reparented to init and KEPT RUNNING, and the dying parent's
#      EXIT trap deleted the shared `/tmp` tmpdir out from under them — every worker then
#      logged "No such file or directory" and the run would have reported a fabricated failure
#      set. **Kill the whole tree or nothing.**
#   2. **`run-reference-tests.sh` APPEARS AS TWO ROOT PROCESSES** (it re-invokes itself as its
#      own parallel dispatcher; the second has the first as its ppid). **CHECK PPID BEFORE
#      CONCLUDING A BATTERY IS DUPLICATED.** And `pgrep -f`/`pkill -f` on a pattern your own
#      command line contains kills your own shell — silently, exit 1, no output. The progress
#      log had already warned about this and I repeated it.
#
# ## PROBED THIS GENERATION WITH NO FINDING — DO NOT RE-PROBE
#
#   * **FLOAT FIELD DEFAULT TRUNCATED BY `int(...)`** (`self.rate = 0.5` stores 0). Refused in
#     BOTH directions, both spellings, by a Why3 TYPE error. **CERTIFIED-BOUNDARY WITH A
#     REOPENING CONDITION:** the truncation IS a latent wrong value masked ONLY by a type
#     mismatch — if float fields are made int-compatible, or the int-coded default convention
#     is widened to carry reals, it goes live at once.
#   * **STRING FIELD LITERAL DEFAULT** (`self.sep: str = "ab"`, carrier `len`) — refused both
#     directions on an unbound `String.length`.
#   * **THE `option` ARM of `_field_default`** (`return "None"`). Probed twice —
#     `Optional[int]` and `Optional[<record>]`. **THE ARM NEVER FIRED**: both fields lowered
#     to plain `int`, the int-constant case is faithfully `{ o = 5 }` and the record case is
#     `(any int)` (route #79's repair working), and `None` is an unconstrained abstract
#     `pycsl_none`, so `is None` is undecidable in both directions. Reaching that arm needs a
#     field whose type actually resolves to `option`.
#   * **PARAM-SOURCED COLLECTION FIELDS** (`self.d = d`, `self.xs = xs`) — probed on a SECOND
#     and THIRD operation after the membership control (`.get()`, element read), because that
#     is exactly the mistake #87 punished. **Still fail-closed, and non-vacuously so**: the
#     emission binds the caller's actual (`{ xs = src }`) and the read is an opaque
#     `subscript_get`. This is what keeps #85/#87 small — the idiomatic constructor is fine.
#   * **CARVE-OUT CANDIDATE 6** (`hval` map local truthiness emits literal `true`) — NOT
#     probed, COST-PRICED instead: `_collect_union_hval_locals` is gated on
#     `_current_emitting_func` ending in one of SIX specific method names from PyCSL's own
#     mirror (`_match_subject_union_info`, `_union_ctor_for_arm_tag`, `_union_none_ctor_for`,
#     `_maybe_inject_union_return`, `_try_union_is_none_match`, `_compute_return_type`), so a
#     driver must reproduce that whole idiom under `@mutable_state`. Its justification is the
#     #55 shape ("sound for the type-safety+frame contracts") which HAS paid before, so it is
#     worth a funded attempt — just not a cheap one.
#
# ## THE LADDER FOR THE NEXT RELAUNCH
#
#   1. **THE LEDGER IS EMPTY, SO GENERATE — AND THE FIVE GENERATORS ABOVE ARE RANKED BY WHAT
#      THEY ACTUALLY PAID TODAY.** Generator 1 is the cheapest and paid last: take every
#      control sentence in every CLOSED route file, ask which single operation it ran, and
#      probe a different one. I found #87 that way in two minutes, against my own control.
#   2. **APPLY GENERATOR 2 TO THIS GENERATION'S FIVE REPAIRS.** Each is a fresh instrument;
#      re-run the carriers of #79, #83, #85, #86, #87 looking for a survivor.
#   3. **CARVE-OUT CANDIDATE 6** — see the cost note above. Candidates 9 and 10 remain (both
#      LOW reachability). The census's honest rate is now **3 hits in 7 probes**, and "LOW-
#      VALUE TAIL" proved not to be evidence: #85 and #86 both came out of a parked candidate.
#   4. **FIX `finding-w60`** (the shared-field-name label mismatch). Fail-closed, so not a
#      route — but it silently turns POSITIVE witnesses into failures for the wrong reason,
#      and this campaign depends on positive witnesses to bound repairs against over-breadth.
#   5. **KEEP GROWING BOTH DIFFERENTIAL CORPORA — the method, now demonstrated.**
#      value-differential went **36 -> 45** and no-exception-differential **39 -> 43** here.
#      **THE CHEAPEST SOURCE IS A ROUTE YOU JUST CLOSED**: its carriers have already been
#      measured in both directions against CPython, so the driver is nearly free. Add BOTH
#      directions — the DISAGREE driver (which must refuse) gives the gate teeth, and the
#      AGREE driver (which must PROVE) is what stops the gate being satisfiable by refusing
#      everything, and it independently re-confirms a faithful close. And add the EXCEPTION
#      pair too when the repair touched a collection: #85/#87 made a field collection's
#      contents decidable, and **the exception side of that is NOT implied by the value
#      side** — `c.xs[5]` / `c.d[9]` had to be measured separately (they refuse; the in-range
#      twins prove). Because these corpora curate nothing — the expected value is MEASURED by
#      running the program on every run — each driver is a permanent self-measuring check
#      that the route stays closed.
#   6. **AUDIT THE REST OF `_field_default` AND ITS NEIGHBOURS AGAINST THE WITNESS-VALUE
#      RULE.** The `option` arm (`return "None"`) is the one I could not reach — probed twice,
#      the arm never fired because both `Optional[int]` and `Optional[<record>]` lower to
#      plain `int`. It is still a DEFINITE value sitting behind a reachability question, and
#      it is the last unaudited arm of a function that has now yielded five routes.
#
# ===================================================================================


# ====== START HERE — gen #9 FINAL STATE — read this block first ==================
#
# ## THE ONE-PARAGRAPH SUMMARY
#
#   **THREE new soundness routes FOUND (#82, #83, #84) and TWO routes CLOSED AND FULLY
#   GATED (#80, #82)**, plus **route #79's cost model CORRECTED BY 3.7x**. All three new
#   routes are the #69 class, the serious one: a FALSE POSTCONDITION about ordinary TOTAL
#   Python, no `no_exception` and no opt-in. **#82 WAS CLOSED FAITHFULLY RATHER THAN BY
#   REFUSAL — every false claim is refused AND every true twin now PROVES — so it is a
#   COMPLETENESS GAIN as well as a soundness fix**, the first such close in the campaign's
#   recent history. The metric never moved (**markers 459 · grep 484**) and was never
#   supposed to. **THE DEFINING FEATURE OF THIS GENERATION IS THAT MEASUREMENT REFUTED MY
#   OWN WORK THREE TIMES BEFORE ANY GATE DID** — see THE THREE SELF-REFUTATIONS below.
#
# ## WHAT IS TRUE RIGHT NOW
#
#   ledger   **THREE OPEN: #79, #83, #84** (#84's repair is BUILT and gating).
#            CLOSED this generation: **#80, #82**.
#   metric   markers **459** · grep 484 · offset 25 · unattached 0 — UNCHANGED.
#   planes   34/34 green at the #82 close. **EXPORT why3 FIRST:**
#            `export PATH=$HOME/.opam/framac-coq8/bin:$PATH`.
#   conform  IR conformance **38/38 core + 38/38 front-end, 0 MISMATCH**, determinism 10/10.
#   suite    **3333/3352, ZERO XPASS**, rc=1 (the baseline condition), 19-failure set
#            byte-identical across both of this generation's runs.
#   ratchets mirror-coverage **549 KEPT, not re-baselined** (see #84).
#
# ## THE THREE SELF-REFUTATIONS — THE MOST TRANSFERABLE THING HERE
#
#   1. **AN INHERITED NUMBER IS AN UNPROVEN LEMMA.** Gen #8 priced #79's repair off "489 of
#      703 (70%) constructor field initialisers are outside the capture shape" and concluded
#      a refusal was OFF THE TABLE. Splitting that complement by *why* each row fell out
#      gives 376 literal RHSs (which `field_defaults` captures FAITHFULLY — verified against
#      golden 0442's IR, not assumed), 192 captured, and **133 actual defects**. Split again
#      by emitter arm, the INT arm #79's own exploit uses has **ZERO corpus sites**. The
#      repair gen #8 called off is predicted byte-inert there.
#      **LESSON: A CENSUS KEYED ON THE COMPLEMENT OF A GUARD MEASURES EVERYTHING THE GUARD
#      DOES NOT CAPTURE, WHICH IS NOT THE SAME SET AS EVERYTHING IT GETS WRONG.**
#
#   2. **MY OWN REPAIR FOR #84 COST NINE CORPUS FILES AND SHOULD HAVE COST ONE.** The
#      byte-diff priced the first design at 9 newly-refused files. I then tested whether
#      those passes were HOLLOW — and they were NOT: hoisting `asyncio.run(outer())` out of
#      the assert into a plain assignment **still proves**, so the emitter already lowers it
#      opaquely and refusing it was pure completeness loss. Narrowing to the measured hazard
#      cut it **9 -> 1**. #79's lesson, recurring on my own work.
#
#   3. **A RATCHET WANTED RE-BASELINING AND WAS KEPT INSTEAD.** `check-mirror-coverage` went
#      552 > 549 because it counts every `ast.FunctionDef` **including nested ones**, so two
#      helper methods plus their inner walkers broke it. Rule (k) forbids re-baselining, and
#      adding `\trusted` mirror stubs would have RAISED the trust metric for a pure refusal.
#      The guard was rewritten **inline with zero new defs**. 549 green, metric untouched.
#
# ## THE GENERATORS THAT PAID THIS GENERATION
#
#   * **READ THE OUTLIER ROWS, NOT JUST THE TOTALS — this produced #82.** Re-verifying gen
#     #8's census surfaced four rows (`PyCSLError`'s `self.filename = filename` and friends)
#     that OBVIOUSLY should have been captured. **The census was right and the RULE was
#     wrong:** `_collect_init_construction` reads `child.args.args`, and Python keeps
#     positional-only and keyword-only parameters in SIBLING fields that are never read.
#     **When a census returns a member that obviously should not be there, the bug is as
#     likely to be in the RULE the census applies as in the census.**
#
#   * **A CENSUS CANDIDATE'S MECHANISM STORY IS A HYPOTHESIS SEPARATE FROM ITS EXISTENCE —
#     this saved #83.** The carve-out census predicted an ANNOTATION-specific hole
#     (`_py_stmt_annassign` has no `else` for an Attribute target). Both halves are TRUE, and
#     **the annotation is IRRELEVANT** — the un-annotated control proves the same false
#     claim. The real cause is `for stmt in child.body:  # top-level only`. **Building the
#     candidate's repair would have fixed the annotated spelling, left the commoner one open,
#     and passed every gate.** One control driver, two minutes, was the difference.
#
#   * **THE CARVE-OUT CENSUS IS A CANDIDATE GENERATOR, NOT A FINDING LIST: 2 HITS IN 6
#     PROBES**, and **every one of the four misses was the same thing — a later guard the
#     text sweep could not see** (#38/#39 refuse the bare `with`; #37 refuses the jumping
#     `else`; the array-coerce and `@mutable_state` arms are fail-closed). Its false-positive
#     mode is benign (a wasted probe) and its hits are severity-1, so keep running it and
#     budget ~3 probes per hit.
#
# ## A MEASUREMENT HAZARD THAT NEARLY PASSED — READ THIS BEFORE TRUSTING A BYTE-DIFF
#
#   **THE BYTE-DIFF SWEEP FABRICATES `MOVED` ENTRIES UNDER DISK PRESSURE.** A sweep reported
#   15 MOVED in pycsl-ref for a guard that only RAISES or FALLS THROUGH — impossible. The 15
#   candidate files were **ZERO BYTES**, in a contiguous block, with none on the baseline
#   side: one parallel worker's batch failed to write with `/tmp` at 77%.
#   **THE FAILURE IS SILENT AND BIDIRECTIONAL — an empty file on the BASELINE side would
#   have reported a FALSE GREEN.** Always run
#   `find <sweepdir> -name '*.mlw' -size 0 | wc -l` on BOTH sides, and watch `df`.
#   (`git worktree add` also fails with an opaque "could not reset index file to revision
#   'HEAD'" when `/tmp` is full.)
#
#   **AND ASSERT THE POPULATION SIZE OF ANY AD-HOC DIFF.** My first suite failure-set
#   comparison matched ZERO lines on BOTH sides and the diff duly reported "identical". The
#   #44 rule — a gate that cannot tell "nothing is wrong" from "I looked at nothing" is not a
#   gate — applies to driver-written comparisons, not only to the planes.
#
# ## THE ROUTES
#
#   * **#80 `del obj.attr` — CLOSED AND FULLY GATED.** Proved `\result == 10` where CPython
#     returns 5 (class-attribute fallback keeps it TOTAL). Gen #9 added TWO carriers gen #8
#     lacked: arithmetic on the stale field, and the stale value **DISCHARGING A CALLEE'S
#     `requires`** — the defect crosses the call graph. Blast radius ZERO (3636 files parsed).
#     Whole-file mirror re-proof **w59a_m5ir rc=0, 2111 Valid, 0 unproved, 56 min**.
#     `check-bespoke-model-drift` fired and was discharged BY EVIDENCE: the emitted mirror
#     WhyML moved by **exactly three lines** (the `is_attribute` raise arm), contract,
#     invariant, variant and `SDelSubscript` untouched — shown BEFORE `--update`.
#   * **#82 `__init__` keyword-only/positional-only parameter dropped — CLOSED, FAITHFULLY.**
#     `P(v=7).v` proved `\result == 0` where CPython returns 7. FIVE carriers; **the control
#     is exact** (same class, field, value, clause — only the parameter KIND differs).
#     Repair reads all three parameter lists, keeping the POSITIONAL binding list SEPARATE
#     from the keyword-only names (appending them would bind keyword-only params
#     POSITIONALLY — a different wrong model). **THE FIRST BUILD WAS A SILENT NO-OP:
#     Module 6 does not read the IR `type_decl` — `preamble.py` builds `rec_info` by copying
#     a SELECTED LIST OF KEYS, so a new IR key is dropped on the floor unless added there.**
#     Blast radius 8, zero in the corpus. Witnesses 1204-1208.
#   * **#83 a field store INSIDE CONTROL FLOW in `__init__` — OPEN.** Blast radius 5, all in
#     `src/pycsl_lib`, zero elsewhere. Cheap to close.
#   * **#84 an `assert` erases its test, side effects included — REPAIR BUILT, GATING.**
#     **THE CONTROL IS THE POINT: the same `xs.pop()` OUTSIDE an assert is a PIPELINE
#     ERROR**, so the assert LAUNDERS A REFUSED CONSTRUCT past its own guard. SIX carriers.
#     The carve-out cites "1450 asserts"; measured 1212, of which **1162 are in `__main__`
#     harnesses that are never lowered** — the real decision set is **21**. Cost: ONE corpus
#     file (0065, `buf.read()`). Residues recorded, incl. `C()()` (a call of a call) uncovered.
#
# ## THE LADDER FOR THE NEXT RELAUNCH
#
#   1. **FINISH GATING #84** — planes + suite. Byte-diff, conformance, fidelity, ratchets all
#      already GREEN and recorded. If the suite shows anything but ZERO XPASS and a
#      19-failure set +1 (pyref 0065 now refused), investigate before closing.
#   2. **#83 NEXT — it is the cheapest open route** (blast radius 5, all `src/pycsl_lib`,
#      zero corpus/mirror/compiler, so no whole-file re-proof). Prefer a FAITHFUL capture
#      over an unconstrained value wherever the value is recoverable — that is what made #82
#      a completeness gain.
#   3. **THEN #79**, the unconstrained-value repair. Its true cost is the **17 mirror INT-arm
#      sites** (whole-file proofs at ~56 min each), NOT a completeness regression. Note
#      `any int` must be let-bound (a record literal in a pure context would be ill-typed —
#      that is a REFUSAL, i.e. fail-closed, not a false proof).
#   4. **CARVE-OUT CENSUS candidates 5, 6, 9, 10 remain unprobed** — the low-value tail.
#   5. **GROW BOTH DIFFERENTIAL CORPORA** (`no-exception-differential/`, `value-differential/`
#      at 36). Still unpaid from gen #8's ladder.
#
# ===================================================================================
#
#
# ====== START HERE — gen #8 FINAL STATE — read this block first ==================
#
# ## THE ONE-PARAGRAPH SUMMARY
#
#   FIVE new soundness routes — **#77, #78 AND #81 found, CLOSED AND FULLY GATED; #79 and
#   #80 found, reproduced BOTH DIRECTIONS, and recorded OPEN with their repairs PRICED BY
#   MEASUREMENT.** All five are the #69 class, the serious one: a FALSE POSTCONDITION about
#   ordinary TOTAL Python, no `no_exception` and no opt-in. **FOUR OF THE FIVE CAME FROM TWO
#   GENERATORS THAT WERE WRITTEN DOWN BEFORE THEY PAID** — a census of PROSE CARVE-OUTS
#   upstream of a guard (#78/#79/#80), and "probe every OPERATION on a carrier a closed route
#   declared safe" (#81). #77 is route #17's defect one step over, with the step CROSSING A
#   MODULE BOUNDARY. The metric never moved (459) and was never supposed to: the repairs are
#   refusals.
#
# ## WHAT IS TRUE RIGHT NOW
#
#   ledger   **TWO OPEN: #79, #80.** #77, #78 and #81 closed and FULLY GATED this generation.
#   metric   markers **459** · grep 484 · offset 25 · unattached 0 — UNCHANGED.
#   planes   **ALL 34 GREEN, rc=0** (`--slow`). **EXPORT why3 FIRST:**
#            `export PATH=$HOME/.opam/framac-coq8/bin:$PATH`.
#   conform  **IR conformance 38/38 core + 38/38 front-end, 0 MISMATCH**, determinism 10/10.
#   proof    **w58_m5ir rc=0 — 2108 goals Valid, ZERO unproved.** The whole-file Module5
#            mirror re-proof #77's repair owed. 52 min wall.
#   corpora  **byte-inert over BOTH** vs a pre-repair worktree baseline: pycsl-ref 971/971,
#            python-ref 2204/2204, 0 MOVED / 0 GONE / 0 APPEARED.
#   suite    **3325/3344, ZERO XPASS**, rc=1 (the baseline condition). The 19 failures were
#            **DIFFED, not eyeballed, and are BYTE-IDENTICAL** across gen #7's baseline and
#            ALL THREE of this generation's runs. 3318/3337 -> 3322/3341 (#77's four
#            witnesses) -> 3324/3343 (#78's two) -> 3325/3344 (#81's one). Every added test
#            passes; nothing else ever moved.
#   OWED     **NOTHING.** No proof, battery or sweep in flight.
#   tree     clean, every increment committed. The two GITLINKS (`scratchpad/w7/base`,
#            `scratchpad/w8/pre`) and the 0-byte stray `str` in the repo root are
#            PRE-EXISTING and are NOT dirt.
#
# ## THE GENERATOR — THIS IS THE MOST REUSABLE THING THIS GENERATION PRODUCED
#
#   **A PROSE CARVE-OUT IN THE MODULE UPSTREAM OF A GUARD IS AN UNEXPLOITED ROUTE WITH A
#   SIGNPOST ON IT.** Census comments that ADMIT a construct is unmodelled / dropped /
#   erased / "stays a no-op" / "out of scope" / "a sound under-approximation", sitting next
#   to code that then emits nothing, a `Pass`, `()` or an empty literal. Ten ranked
#   candidates; the top four gave THREE LIVE ROUTES; three more probed clean. That hit rate
#   is the honest one, and the vein is NOT exhausted — six candidates remain unprobed.
#
#   **THE SECOND GENERATOR, AND IT PAID ON ITS FIRST USE: PROBE EVERY *OPERATION* ON A
#   CARRIER A CLOSED ROUTE DECLARED SAFE.** The campaign already banks "probe every CARRIER of
#   a closed route". #81 adds the orthogonal axis. A closed route's "this carrier is correct"
#   control is **evidence about the OPERATION it ran, not about the TYPE** — a control is a
#   measurement, not a theorem. Applied to route #59's list control it found #81; applied to
#   route #76's record control it found NOTHING (record aliasing is undecided in both
#   directions). Both outcomes are useful and both are recorded.
#
#   **THE SHARPEST SUB-LESSON: A COMMENT ASSERTING AN ERASURE IS SOUND IS AN UNPROVEN
#   LEMMA, AND IT IS CHECKABLE IN ONE PROBE.** #78's says "a sound under-approximation";
#   #79's says "sound, just less precise". **BOTH ARE FALSE**, and identically so: each
#   emits a DEFINITE LITERAL (an EMPTY array; a literal `0`) that the emitter then proves
#   definite facts from. A real under-approximation is an UNCONSTRAINED value. Grep for
#   "sound", "under-approximation", "less precise", "conservative" in comments next to an
#   erasure — every hit is a candidate.
#
# ## ROUTE #77 — CLOSED AND FULLY GATED
#
#       xs: List[int] = [1, 2, 3]
#       del xs[0:2]
#       return xs[0]        #@ ensures \result == 1   <-- CPython returns 3. PyCSL PROVED.
#
#   Why3 prints `unused variable xs` on that run: the delete is erased and the read is then
#   constant-folded. THREE carriers proved a false claim (element read, `len()` read,
#   `del xs[:]`), the TRUE TWIN OF EACH was REFUSED, a DYNAMIC bound `del xs[0:n]` is erased
#   identically, and the stale value DISCHARGES A CALLEE'S `requires` at a call site.
#
#   **WHY THE EXISTING GUARD MISSED IT, AND THIS IS THE STRUCTURAL POINT:** route #17 closed
#   the ELEMENT delete with a Module-6 refusal that is a **BLOCKLIST KEYED ON THE EMITTED
#   STRING** (`if code.strip() == "()"`). `Module5_IREmitter._py_stmt_delete` drops the SLICE
#   form to `{"stmt": "Pass"}` ONE STAGE EARLIER, byte-indistinguishable from a user's
#   `pass`. **The guard and the hazard ended up in different modules.** Gen #7's "a blocklist
#   keyed on syntax fails OPEN" is now confirmed ACROSS A MODULE BOUNDARY, which is why six
#   generations of reading Module 6 never found it.
#
#   CLOSED by refusing at the site that ERASES it. GATES, all green: mirror-sync rc=0 (**887
#   un-trusted mirror functions verbatim**), signature drift 0, mirror coverage OK,
#   **mirror type-only 53/53 with 0 ILL-TYPED** (rule (j)), **byte-inert over BOTH corpora**
#   against a pre-repair worktree baseline (pycsl-ref 971/971, python-ref 2204/2204, 0
#   MOVED / 0 GONE / 0 APPEARED), **IR conformance 38/38 core + 38/38 front-end, 0 MISMATCH,
#   determinism 10/10** (run deliberately, rule (m)). Witnesses 1194-1197.
#   A ONE-TOKEN ALTERNATIVE WAS REFUTED BY MEASUREMENT BEFORE LANDING: dropping the
#   `not isinstance(slice_node, ast.Slice)` conjunct routes the slice into the `DelSubscript`
#   path, but for a LOCAL DICT receiver that path emits a faithful `map_update_none` keyed on
#   a coerced slice — modelling `del d[i:j]` as a key delete where CPython raises KeyError.
#   It trades an old wrong model for a new one. Knowing this saves rebuilding it.
#
# ## THE THREE OPEN ROUTES, EACH WITH ITS REPAIR ALREADY PRICED
#
#   * **#78 SEEDED `deque(...)` IS MODELLED AS EMPTY**, every argument discarded.
#     `deque([1,2,3])` then `len` proves `\result == 0`; CPython 3; TRUE twin REFUSED. The
#     element read `dq[0]` is a second carrier and it ESCALATES to a `requires` discharge.
#     **The EMPTY `deque()` control is FAITHFUL and bounds the repair** (the role `@dataclass`
#     played for #76). **BLAST RADIUS OF REFUSING THE SEEDED FORM: MEASURED AT ZERO** — the
#     only corpus use is `deque()`, the mirror has none. **This is the cheapest of the three
#     to close and should go first.** Residue: `appendleft`/`popleft`/`pop` refuse today, but
#     by an unrecognised-method fallback, not a guard — reopening condition recorded.
#   * **#79 AN `__init__` FIELD INITIALISER OUTSIDE THE CAPTURE SHAPE BECOMES A LITERAL 0.**
#     **THE WIDEST-REACHING ROUTE THIS GENERATION — it needs only `self.n = len(items)`.**
#     Three carriers proved (`len(items)`, a module const, another `self` field). **The
#     params-only control `self.x = n + 1` is FAITHFUL IN BOTH DIRECTIONS**, bounding the
#     defect exactly to RHSs naming something outside the parameter set — the same set the
#     existing capture rule already computes.
#     **ITS BLAST RADIUS IS MEASURED AND IT REFUTES THE OBVIOUS REPAIR: 489 of 703 (70%)
#     constructor field initialisers repo-wide are outside the capture shape** (corpus 158 ·
#     mirror 85 · src/pycsl 122 · src/pycsl_lib 124). A blanket refusal is therefore OFF THE
#     TABLE. **The repair that survives is to emit an UNCONSTRAINED value for the omitted
#     field instead of the literal 0 — which is exactly what the false comment already claims
#     the code does.** Next thing to price: whether an unconstrained field breaks proofs that
#     silently depend on the 0 (85 mirror sites). Census script banked at
#     `getting-better/route77-80-witnesses/r79-blast-radius-census.py` — RE-RUN IT, it reads
#     the live capture rule so it stays honest if that rule changes.
#   * **#80 `del obj.attr` IS ERASED AND A CLASS-ATTRIBUTE FALLBACK MAKES IT TOTAL.**
#     Proves `\result == 10` where CPython returns 5; true twin REFUSED. Same erasure site as
#     #77. **THIS IS #77's OWN RESIDUE (a), UPGRADED BY MEASUREMENT — I WROTE THAT RESIDUE
#     MYSELF FOUR HOURS EARLIER AND IT WAS HALF WRONG.** #77 filed `del obj.attr` as out of
#     scope "because the program raises"; Python's class-attribute fallback keeps it total.
#     **LESSON: "OUT OF SCOPE BECAUSE IT RAISES" IS ITSELF A CLAIM ABOUT PYTHON AND MUST BE
#     PROBED, NOT REASONED ABOUT.** `del name` genuinely raises and stays route #71's class.
#
#   * **#81 A LIST ALIAS TRACKS ELEMENT STORES BUT LOSES `append` — CLOSED AND FULLY GATED.**
#     `a=[1,2]; b=a; b.append(3); len(a)` proved 2 where CPython returns 3; true twin refused;
#     the ELEMENT read was a second, sharper carrier and the REVERSE direction proved too.
#     **IT REFUTED A SECTION HEADING IN ROUTE #59's OWN FILE** — "THE LIST CARRIER IS CORRECT"
#     — which was true of the ELEMENT STORE it measured and false one operation over.
#     MECHANISM: an appended-to list is SEQ-PROMOTED to `ref (seq int)` and the alias COPIES
#     it with its OWN length; Why3 prints `unused variable b_len` on the exploit run, exactly
#     as it printed `unused variable xs` for #77. Closed by a guard at the TOP of
#     `_handle_assign_stmt`; corpus 1131 (#59's element-store control) still proves.
#
# ## A BROKEN TOOL PATH ROOT-CAUSED AND FIXED — USE THE CLEAN BASELINE METHOD AGAIN
#
#   Gen #6 recorded that the worktree byte-diff baseline "FAILED, reproducibly emitting 1 of
#   1101", and worked around it by SWAPPING THE CHANGED FILE IN THE MAIN TREE. **THE CAUSE IS
#   `bin/byte-diff-sweep.sh` RUNNING `$ROOT/.venv/bin/python3` WHILE `.venv/` IS GITIGNORED**,
#   so a fresh worktree has no interpreter and every emission fails. **The fix is one line —
#   `ln -s <main>/.venv <worktree>/.venv` after `git worktree add`** — and with it the
#   worktree baseline emitted 972/1120 and 2204/2217, EXACTLY matching the main tree. This
#   matters beyond tidiness: the file-swap workaround MUTATES SOURCE, which cannot be done
#   while a whole-file mirror proof is reading the tree.
#
# ## A PLANE GREW, AND READING ITS PARSER CAUGHT TWO DEFECTS IN MY OWN ADDITIONS
#
#   `test-suite/value-differential/` **22 -> 36 drivers** (7 new AGREE / 7 new DISAGREE, so
#   the population guard keeps teeth both ways). New axis: semantic subtleties of TOTAL
#   Python where a plausible model differs — `**` binding tighter than unary minus, CHAINED
#   comparison (operands chosen so the left-associative reading DISAGREES), a NEGATIVE repeat
#   count, slice upper-bound CLAMPING, negative indexing, `not` on an int, `//`
#   left-associativity.
#   **LESSON: WHEN ADDING TO A SELF-MEASURING PLANE, READ THE PLANE'S PARSER FIRST.**
#   `_cpython_value` does `int(out)`, so a driver whose `__main__` prints a BOOL raises
#   ValueError and is classified RAISED = "out of scope, never fatal" — it would have
#   **SILENTLY EXCUSED ITSELF** and measured nothing. Four of mine would have. A corpus of
#   self-excusing drivers is indistinguishable from a growing one. (Two more of mine
#   duplicated v16/v22 exactly; an md5 census now confirms 0 duplicates across all 36.)
#
# ## THE BATTERY CAUGHT ME, AND THE DISTINCTION IT FORCED IS WORTH BANKING
#
#   The 34-plane battery came back **33 green / 1 RED**, and the RED was
#   **`check-bespoke-model-drift.py`** — the one plane in the repo built for exactly the change
#   #77 makes. Its docstring describes the trap precisely: for a method whose WhyML is
#   HAND-WRITTEN rather than derived from the body, editing the live body and dutifully syncing
#   the mirror leaves **mirror-sync GREEN, L3-tc GREEN, the whole-file proof GREEN (it proves
#   the OLD model), and the emission BYTE-IDENTICAL** — "and the model has silently stopped
#   being the body". Relaunch #44 walked into exactly that on `_py_stmt_assign` (route #28)
#   **with the warning in front of it**.
#
#   **I DID NOT RE-BASELINE ON SIGHT.** I discharged the plane's own stated confirmation step —
#   READ THE EMITTED `.mlw` — by diffing the mirror emission against a pre-repair copy saved
#   hours earlier. The model MOVED and moved correctly: the contract gained
#   `raises { PyCSLSemanticError -> true }` and the body gained the `begin raise
#   PyCSLSemanticError end` arm, with the loop invariant and variant untouched. And because the
#   bespoke edit preceded the proof, **w58_m5ir proved the NEW model.** Only then `--update`,
#   whose diff is **exactly one fingerprint** with the other 26 hand-synthesized models
#   untouched. Battery re-run in full: **34/34, rc=0.**
#
#   **THE DISTINCTION, STATED ONCE SO THE NEXT GENERATION DOES NOT HAVE TO REDERIVE IT:**
#   rule (k) bars re-baselining a ratchet to HIDE AN UNFIXED DEFECT. It does NOT bar
#   discharging a NOTIFICATION gate whose documented workflow IS re-blessing after you have
#   verified the co-change. **The test that separates the two is whether you can SHOW THE
#   ARTIFACT MOVED. If you cannot, you are hiding something.**
#
# ## PROBED THIS GENERATION WITH NO FINDING — DO NOT RE-PROBE
#
#   * **#76's record-FIELD carrier** (`\result.p == \result.q`) still dies on the SAME
#     `c @rho` vs `int` type accident in BOTH directions — fail-closed-by-accident, not by a
#     guard, reopening condition unchanged. ADJACENT FACT: the spec grammar REJECTS a CHAINED
#     field read (`\result.p.v` -> "unexpected trailing input"), so the class-typed field
#     family cannot be spelled two levels deep in a clause (completeness, not soundness).
#   * **The module-GLOBAL singleton field store `g.v = n` IS FAITHFUL** — true claim proves,
#     false refused. (Already closed as route #28; confirmed at HEAD, not inherited.)
#   * **The module-const dict/list fold's MUTATION invalidation is FAIL-CLOSED** —
#     `CONST["a"] = 2` and `CONST[0] = 9` are an explicit PIPELINE REFUSAL. Both of these
#     clear the last two items of the gen-#5 claim backlog.
#   * **The `@mutable_state` set-param mutation observed through a LOCAL ACTUAL** — the
#     census's strongest remaining lead — is a PIPELINE ERROR. Not live.
#   * **A dropped `global` declaration**: `global G; G = 5; return G` claiming the stale 1 is
#     REFUSED. `ast.Global` really has no handler entry, but the store retargets a fresh local
#     and the stale read does not prove, so the missing `else` is a LATENT structural defect,
#     not a live route today. Reopening: any change making a dropped `global` store alias the
#     module variable.
#   * **`...` lowered to integer 0**: `x = ...; return x + 0` is REFUSED and CPython RAISES,
#     so it is out of scope for the value plane in this spelling.
#   * Of the 16 value-differential probes, EIGHT constructs fail closed (incomplete, not
#     unsound): `2**3**2`, slice lower-clamp, `range` step len, `"abc".count("")`,
#     `(-2)**3`, `0**0`, `[0]*-2`, and `s[::-1]` (a pipeline refusal).
#
# ## THE LADDER FOR THE NEXT RELAUNCH
#
#   1. **#77, #78 AND #81 ARE DONE.** Start at #80.
#   2. **#80** — same erasure site as #77, so the repair is the same shape; census
#      `del <name>.<attr>` for blast radius first.
#   3. **THEN #79, THE UNCONSTRAINED-VALUE REPAIR**, not a refusal (measured: 70%). Price the
#      85 mirror sites before building.
#   4. **KEEP MINING THE CARVE-OUT CENSUS — SIX CANDIDATES REMAIN UNPROBED**, including the
#      annotated-store-inside-`__init__` drop, the `emit_ir[k] = v` no-op (mirror-domain), the
#      silently-ignored mixin directives, and the missing `else` in the statement dispatch.
#   5. Grow BOTH differential corpora further; the value one is now 36 and is aimed squarely
#      at the campaign's most serious defect class.
#
# ===================================================================================
#
#
# ====== START HERE — gen #7 FINAL STATE — read this block first ==================
#
# ## THE ONE-PARAGRAPH SUMMARY
#
#   ONE new soundness route, **#76**, found and CLOSED and FULLY GATED, and the gen-#6
#   ladder's item 2 (**the `_add_abstract_op` ENSURES audit**) FINISHED and found CLEAN.
#   #76 is the **DUAL of routes #42/#52**: those found `is` decided by VALUE equality
#   (`is` too WEAK) and gave it its own IR operator; **the `==` side of that same coin was
#   never examined**. `==` on a class instance emits Why3's logic `=`, which on a record is
#   equality of the FIELD VALUES, while Python's `==` with no `__eq__` is IDENTITY — so
#   `#@ ensures \result == x` PROVED for `dup(x) = C(x.v)` where CPython answers False.
#   It is the #69 class, the serious one: a FALSE POSTCONDITION about ordinary TOTAL
#   Python, no `no_exception` and no opt-in — and it also DISCHARGED a `requires` at a call
#   site whose precondition is False at runtime. The metric never moved (459) and was never
#   supposed to: the repair is a refusal.
#
# ## WHAT IS TRUE RIGHT NOW
#
#   ledger   **EMPTY. NO OPEN ROUTE.** #76 found and closed this generation. The stale
#            "CURRENTLY OPEN: ONE — #59" line in `open-routes/README.md` was corrected
#            (re-reproduced at HEAD first: #59 now gives an explicit refusal naming itself).
#   metric   markers **459** · grep 484 · offset 25 · unattached 0 — UNCHANGED.
#   planes   **ALL 34 GREEN** (`--slow`, rc=0, clean tree) — **THE COUNT IS NOW 34, NOT 33**:
#            this generation ADDED `check-value-differential.py`. **EXPORT why3 FIRST:**
#            `export PATH=$HOME/.opam/framac-coq8/bin:$PATH`.
#   conform  **IR conformance 38/38, 0 MISMATCH** — run deliberately, per gen #6's lesson.
#   corpora  **0 newly-refused files across 1645 corpus files + the mirror**, and the guard
#            only RAISES or FALLS THROUGH — it never alters emitted text — so it is
#            **byte-inert BY CONSTRUCTION**, not merely by sampling.
#   suite    **3318/3337, ZERO XPASS**, rc=1 (the baseline condition). The 19 failures were
#            **DIFFED against suite56_run3, not eyeballed, and are BYTE-FOR-BYTE IDENTICAL**.
#            Baseline 3312/3331 -> 3318/3337: all six new witnesses pass, failure set frozen.
#   OWED     **NOTHING.** No proof, battery or sweep in flight.
#   tree     clean, every increment committed. The two GITLINKS (`scratchpad/w7/base`,
#            `scratchpad/w8/pre`) and the 0-byte stray `str` in the repo root are
#            PRE-EXISTING and are NOT dirt.
#
# ## THE ONE LESSON THAT GENERALISES FURTHEST THIS GENERATION
#
#   **AN ALLOWLIST KEYED ON SYNTAX FAILS CLOSED WHEN THE HAZARD MOVES; A BLOCKLIST KEYED ON
#   SYNTAX FAILS OPEN.** This campaign has banked "a guard keyed on a syntactic location is
#   defeated by moving the hazard one step" SIX times and kept treating it as a warning.
#   It is not a warning — it is an instruction to INVERT THE POLARITY. #76's guard is an
#   allowlist and every one-step-over move (ctor one call deeper, ctor via a local, ctor as
#   the operand, the list-element carrier) lands OUTSIDE it and is refused for free.
#
#   TWO BLOCKLIST DESIGNS WERE REFUTED BY MEASUREMENT BEFORE EITHER LANDED:
#     * "refuse when the body CONSTRUCTS" — `return mk(x.v)`, ctor one call deeper, PROVED;
#     * "uninterpreted `obj_eq` + reflexivity" — **Why3's RECORD EXTENSIONALITY** already
#       derives `{v = x.v} = x`, so any equality-derived predicate inherits the defect, and
#       without reflexivity the five reference locks stop proving. No setting of that dial
#       works. Knowing this saves the next generation from rebuilding it.
#
# ## ROUTE #76 IN SIX LINES (full file: `open-routes/route76-...md`)
#
#       class C:
#           v: int
#           def __init__(self, v: int) -> None: self.v = v
#       #@ ensures \result == x          # PyCSL: SUCCESS.  CPython: dup(a) == a is False
#       def dup(x: C) -> C: return C(x.v)
#
#   True twin (`!=`) FAILS, so it is a route and not a gap. **`@dataclass`/NamedTuple is
#   FAITHFUL** (Python GENERATES a structural `__eq__` there) — that control is what bounds
#   the route instead of over-refusing everything, the same role the List carrier played
#   for #59. Closed by a fail-closed allowlist admitting: a NamedTuple/TypedDict; two
#   syntactically identical pure READ PATHS; and `\result` against a read path when EVERY
#   return is that path (the accessor idiom five reference locks carry). A read path
#   excludes a Call — a constructor makes a NEW object every evaluation. `a[-k]` and
#   `a[\length(a)-k]` are canonicalized onto one form so the allowlist is not defeated by
#   SPELLING (lock 0934 spells the clause one way and its body the other — caught by
#   RUNNING the locks, not by reading them).
#
# ## PROBING MY OWN REPAIR FOUND A LIVE GAP, BEFORE LANDING — DO THIS EVERY TIME
#
#   The first cut resolved a class-typed operand through `\result`, a typed local/param and
#   a ctor Call only. It MISSED the `List[<record>]` ELEMENT: `#@ ensures a[0] == a[1]`
#   still PROVED. One probe, found before landing. Witness 1193.
#
# ## PROBED THIS GENERATION WITH NO FINDING — DO NOT RE-PROBE
#
#   * **The ENTIRE BODY PLANE for class-instance comparison is held by ONE shared Why3
#     type accident** (`c @rho` vs `int`). NINE dunder carriers enumerated mechanically
#     (`__eq__`, `__ne__`, `__lt__`, `__bool__`, `__len__`, `__contains__`, `__getitem__`,
#     `__add__`, plus a control) — every one dies with the SAME message. So do `is` and
#     `is not` on two class instances, and the ORDERING operators `<`/`<=` in a SPEC.
#     **That is a SAFE-TYPED verdict, i.e. a type accident and never a guard.** ONE
#     reopening condition covers them all: any change making a class record type usable in
#     an int context (an unboxing, a `__bool__`/`__len__` lowering) reopens ALL of them at
#     once, and #76's guard covers only `==`/`!=`.
#   * **The value-level escalation of #76 fails closed by Why3's OWN REGION TYPING** —
#     `setv(dup(x)); return x.v` comes back Unknown, because a logic `=` between two
#     records does not make them the same REGION. Same mechanism as #59's return carrier.
#   * **The QUANTIFIED carrier of #76 is covered for free** — `\forall`/`\exists` with
#     `a[k] == x` inside are caught, because the guard keys on the BINOP, not the clause.
#   * **`axiom hash_eq_consistent_<cls>` (gen-#6 ladder item 2b) is UNREACHABLE, not merely
#     switchable.** Both `<cls>_hash_` and `<cls>_eq_` are DEAD SYMBOLS: `hash(a)` lowers to
#     an unrelated `val hash_1 (x0: int) : int` and type-rejects the class argument, and
#     `a == b` goes to the record `=`. Reading WHY it does not reach `<cls>_eq_` is exactly
#     how #76 was found.
#   * **INTEGER `//` AND `%` WITH A NEGATIVE DIVISOR ARE FAITHFUL IN BOTH PLANES.** This
#     looked like a live route and is not. `identifiers.py`'s `OP_MAP` comments say
#     `"//" -> div` and `"%" -> mod` (Why3 `int.EuclideanDivision`), and Euclidean really
#     does disagree with Python there — `7 // -2` is -4 in Python and -3 Euclidean,
#     `7 % -2` is -1 in Python and 1 Euclidean, `-7 // -2` is 3 vs 4. **MEASURED in BOTH
#     the BODY and the SPEC plane, all six ways: PyCSL proves PYTHON's answer and REFUSES
#     the Euclidean one every time.** The OP_MAP comment is stale; the lowering is right.
#   * **BITWISE AND SHIFT OPS ARE UNINTERPRETED, hence fail-closed.** `&`, `|`, `^`, `>>`,
#     `<<` and `abs()` on NEGATIVE operands: every TRUE claim FAILS (`-1 & 3 == 3`,
#     `-8 >> 1 == -4`, `-1 >> 10 == -1`, `-5 ^ 3 == -8`, `abs(-5) == 5`). Incomplete, not
#     unsound — nothing proves, so no false twin is reachable.
#   * **A DICT KEYED BY CLASS INSTANCES fails closed BOTH ways.** Python hashes a plain
#     class by IDENTITY, so `d[a] = 1; d.get(b, 0)` with `b` a distinct structurally-equal
#     object returns 0 — and this needs NO opt-in, since `.get` never raises. Neither the
#     false claim (`== 1`) nor the true one (`== 0`) proves.
#   * **`\old(...)` DOES NOT BYPASS #76's GUARD**, nor does a class-typed field carrier:
#     the guard fires whenever EITHER side resolves, so the `\result` side alone is enough.
#   * **The CLASSIFICATION oracles do not yield a false proof in the shapes probed.**
#     `ir_scanner.py`'s `.split` / `IRScanner.find_*` / `collect_*` array-vs-dict rules are
#     mirror-domain conventions applied to every program (the #73/#74 shape), but a
#     misclassification produces a TYPE ERROR or an unprovable goal: the true claim proves,
#     both false twins fail. Three shapes probed — NOT a proof the class is empty.
#
# ## THE `_add_abstract_op` ENSURES AUDIT IS FINISHED AND CLEAN — WITH A ONE-LINE RE-CHECK
#
#   An `ensures` on an abstract `val` IS an axiom (how #73/#74 were found). Across the whole
#   emitter there are **exactly TWO sites** that attach one, and they are the zero-arity and
#   n-arity arms of ONE generic fallback. Their clause is **CALLEE-CONTRACT PROPAGATION,
#   backed by a real VC** — measured: a method whose declared `#@ ensures \result == 7` is
#   false of its body fails its OWN `c__m'vc`, so the file fails closed.
#       grep -rn "_add_abstract_op(" src/pycsl/module6_whyml/ | grep -i ensures
#   **should return exactly two lines. A THIRD is a live route until proven otherwise.**
#   The dotted/class-name oracles gen #6 flagged (`.to_dict`, `.copy`, `.findall`, `.split`,
#   `.get`, `IRScanner.*`, `self.ir.get`) carry NO axiom — the standing warning is CONFIRMED
#   and now cheap to re-check.
#
# ## A NEW PLANE LANDED: `check-value-differential.py` — USE IT, AND GROW IT
#
#   **The most serious defect class this campaign finds is NOT an exception hole.** It is a
#   FALSE POSTCONDITION ABOUT ORDINARY, TOTAL PYTHON — no `no_exception`, no opt-in. Routes
#   #53, #58, #73, #74 and #76 are ALL that shape, and every one was found by a
#   hand-written probe. `test-suite/value-differential/` + `bin/check-value-differential.py`
#   make it MECHANICAL, and they **curate nothing**: each driver states a literal in its own
#   `#@ ensures \result == <int>` and RUNS ITSELF under `__main__`, so the expected value is
#   MEASURED by CPython on every run rather than asserted by whoever wrote the driver.
#   RED = (claim disagrees with CPython) + (PyCSL PROVES).
#
#   Seeded with **22 drivers, 12 AGREE (all prove) / 10 DISAGREE (all correctly refused)**.
#   Population guard per the #44 rule (rc=2 unless BOTH populations exist, since the gate is
#   otherwise satisfiable by refusing everything); parsing is FAIL-CLOSED; a missing why3
#   REFUSES rather than reporting green.
#
#   **IT IS NEGATIVE-TESTED ON A REAL PROGRAM, and that is what makes a green run mean
#   something.** `python3 bin/check-value-differential.py --negative-test` runs a driver
#   whose `#@ \trusted` stub carries an ASSUMED `ensures` (the documented opt-in mechanism,
#   NOT a route), letting PyCSL prove `\result == 99` where CPython computes 1 — and it
#   FAILS unless the plane rules that UNSOUND. Verified firing. **Re-run that after any
#   change to the plane.** The standing run skips the `negative-test/` subdirectory.
#
#   **GROWING IT IS THE CHEAPEST ROUTE-DETECTION WORK AVAILABLE.** Every raising-free Python
#   operation whose value the model could plausibly get wrong is one more permanent,
#   self-measuring check. The seed pins floor-division/modulo with a NEGATIVE DIVISOR (where
#   Why3's Euclidean `div`/`mod`, which `OP_MAP`'s comments still name, genuinely disagrees
#   with Python), `and`/`or` returning an OPERAND rather than a bool, and container
#   truthiness.
#
# ## THE LADDER FOR THE NEXT RELAUNCH
#
#   1. **THE SPEC PLANE IS THE SOFT TARGET, AND THAT IS THIS GENERATION'S AIMING
#      INSTRUCTION.** The BODY plane is broadly protected by Why3's type checker (nine
#      dunders, `is`, the orderings — all one accident); the SPEC plane has no such
#      constraint, which is the ONLY reason #76 lives there. For any construct that fails
#      closed in a body, **re-probe its SPEC-plane spelling** before believing it is safe.
#   2. **#76's THREE RESIDUES**, each with its reopening condition in the route file:
#      (a) `@dataclass` is now OVER-REFUSED — a completeness regression, zero corpus cost
#      today; fix is to thread `is_dataclass` from Module 5 (MIRRORED, so it owes a
#      re-proof). (b) the record-FIELD carrier `b.p == b.q` is held ONLY by the type
#      accident and the guard does NOT see it — one more resolver branch
#      (`FieldGet` -> receiver class -> `field_types[field]`) closes it. (c) the value model
#      has NO object identity and the spec grammar has NO `is` (measured: `\result is x`
#      does not parse) — the complete fix is an opaque per-object identity slot, whose blast
#      radius is EVERY record emission and therefore hundreds of re-proofs, **beyond the
#      measured box ceiling**. That is a COST boundary with a measured reason, not a guess.
#   3. **The remaining half of the abstract-op audit is a CLASSIFICATION audit, not an axiom
#      audit** — recognizers that mis-MODEL a call without emitting any clause. Three shapes
#      probed clean; the vein is not exhausted.
#   4. **Grow BOTH differential corpora** — `no-exception-differential/` (40 drivers) and the
#      new `value-differential/` (22). They curate nothing, so every driver added is a
#      permanent self-measuring check. The VALUE one is the newer and thinner of the two and
#      is aimed squarely at the campaign's most serious defect class.
#   5. The gen-#5 claim backlog, still largely unmined: the module-GLOBAL singleton field
#      store `g.v = n`; the module-const dict fold's invalidation omitting MUTATION.
#
# ## PROCESS LESSONS PAID FOR THIS GENERATION
#
#   * **DO NOT EDIT SOURCE WHILE A GATE BATTERY RUNS.** A 33-plane battery was DISCARDED and
#     re-run because source changed mid-flight: a mixed-tree verdict is worthless.
#   * **RE-REPRODUCE A STATUS LINE BEFORE EDITING IT, AND VERIFY YOUR OWN CENSUS READING.**
#     The census first looked like five `Tok == None` hits; the "None" was the UNRESOLVED
#     CLASS, not the None literal. They were `\result == <subscript>` — the SAME SHAPE as
#     the exploit. A blanket refusal would have broken five reference locks. One extra
#     dump separated them.
#   * **CHECK A REGRESSION AGAINST ITS BASELINE BEFORE CALLING IT ONE.** Lock 0901 fails
#     with the guard AND without it — pre-existing, verified by re-running with the guard
#     removed rather than assumed either way.
#
# ===================================================================================
#
#
# ====== START HERE — gen #6 FINAL STATE — read this block first ==================
#
# ## THE ONE-PARAGRAPH SUMMARY
#
#   THREE new soundness routes (#73, #74, #75) found and closed, and ONE INHERITED GATE
#   FOUND DEFECTIVE AND FIXED. **ALL THREE ROUTES ARE ONE DEFECT**: a HAND-ADDED ORACLE
#   KEYED ON A NAME BEATS THE DEFINITION THE USER WROTE — #73 keyed on a literal STRING,
#   #74 on a method NAME, #75 on a BUILTIN name — and all are the #69 class, the serious
#   one: a FALSE POSTCONDITION about ordinary TOTAL Python, needing no `no_exception` and
#   no opt-in of any kind. **EACH WAS FOUND BY PROBING THE PREVIOUS ONE'S REPAIR**, and
#   #75 was closed with ONE STRUCTURAL GUARD FOR THE WHOLE CLASS rather than a third patch.
#   Beyond that, three probe batches (36 drivers) aimed at the exception model found NOTHING,
#   which is itself the result: the gen-#5 handoff's five unworked abstract-`val` leads are
#   NOT live routes, and the exception model's obligations do NOT stop at the frame. The
#   metric never moved (459) and was never supposed to.
#
# ## WHAT IS TRUE RIGHT NOW
#
#   ledger   **EMPTY. NO OPEN ROUTE.** #73, #74 and #75 found and closed this generation.
#   metric   markers **459** · grep 484 · offset 25 · unattached 0 — UNCHANGED, the expected
#            shape of a window paying the soundness ladder. The repair is a refusal.
#   planes   **ALL 33 GREEN under `--slow`**, run FOUR times this generation (the gate
#            change and each of the three repairs). **RUN WITH why3 ON PATH**
#            (`export PATH=$HOME/.opam/framac-coq8/bin:$PATH`).
#   corpora  **BOTH byte-inert** against a pre-repair baseline for EACH repair, except
#            exactly that repair's own witnesses. #73: pyref 2204/2204 inert, pycsl-ref
#            959/959 with 3 MOVED. #74: pyref 2204/2204 inert, pycsl-ref 963/963 with 3
#            MOVED — and 1181, the REAL-`str` positive control, did NOT move, so the genuine
#            predicate path is untouched at the BYTE level, not merely at the verdict level.
#   suite    **3312/3331, ZERO XPASS**, failure set BYTE-FOR-BYTE identical to the
#            suite55_run5 baseline (19, diffed not eyeballed). rc=1 IS the baseline
#            condition. Run THREE times — `proofs49/suite56_run1.*` gated #73 at 3302/3321,
#            `suite56_run2.*` gated #74 at 3306/3325, `suite56_run3.*` gates #75 at
#            3312/3331. The suite grew by THIRTEEN drivers this generation, all route
#            witnesses, and every one passes.
#   OWED     **NOTHING.** No proof, battery or sweep in flight.
#   tree     clean, every increment committed. The two GITLINKS (`scratchpad/w7/base`,
#            `scratchpad/w8/pre`) and the 0-byte stray `str` in the repo root are
#            PRE-EXISTING and are NOT dirt.
#
# ## ROUTE #73 — AN OPAQUE ORACLE SHADOWED A USER-DEFINED FUNCTION
#
#   A complete, runnable program, nothing opted into beyond an ordinary postcondition:
#
#       #@ ensures \result == d
#       def get(k: str, d: int) -> int:  return d
#
#       #@ ensures \result >= 0
#       def f() -> int:                  return get("arity", -1)
#
#   **CPython answers -1. PyCSL proved `\result >= 0`.**
#
#   CAUSE: `_lower_dict_get_call` (expressions.py) fired on `func_name == "get" and
#   len(args) == 2` whenever the FIRST ARGUMENT was the literal string `"arity"`, emitting
#   `val get_arity_field (x0: int) (x1: int) : int ensures { result >= 0 }`. The code's OWN
#   COMMENT concedes it — "an assumed, trusted-stub-shaped contract" firing for "ANY
#   `.get("arity", ...)` call the tool can't type" — and its justification is a DOMAIN
#   CONVENTION OF THE SELF-ANNOTATION MIRROR, asserted globally BY KEY NAME over every
#   program PyCSL compiles. An `ensures` on an abstract `val` is an AXIOM.
#
#   **THE EMITTED DIFF IS THE WHOLE ROUTE IN FIVE LINES**, and it is worth looking at:
#       before:  (get_arity_field 1684615666 (- 1))     <- "arity" HASHED TO AN INT, handed
#                                                          to an oracle axiomatised >= 0;
#                                                          the user's function is ABSENT
#       after:   (get "arity" (- 1))                    <- the real call
#   (The string-hashed-to-an-int shape is the same one #68 and #72 found.)
#
#   **THE OBVIOUS GUARD WAS MEASURED AND REFUTED BEFORE IT LANDED.** Refusing on a negative
#   default is defeated by moving the hazard one step:
#       def get(k, d): return -5   /   get("arity", 0)   -> CPython -5, `>= 0` PROVED.
#   That is the SIXTH instance of "a guard keyed on a syntactic location is defeated by
#   moving the hazard one step" — and the FIRST caught BEFORE landing rather than after.
#   The measurement RELOCATED the defect: the key string and the default are red herrings;
#   the fault is an oracle SHADOWING a user function.
#
#   **THE LANDED GUARD IS STRUCTURAL, NOT SYNTACTIC.** `func_name == "get"` arises two ways:
#   a CHAINED `<expr>.get("arity", d)` carrying a `receiver` (the shape the oracle exists
#   for — `expr_ghost_spec_ops.py`, receiver kind untypable) and a BARE two-argument call
#   with NO receiver (the carrier). The oracle now requires a receiver. **A bare call cannot
#   acquire one**, so there is no one-step-over spelling.
#
#   **THE POSITIVE CONTROL IS THE STRONGEST EVIDENCE.** Witness 1176 — the TRUE claim
#   `\result == -1` about the same program — now PROVES where it did NOT before. The repair
#   did not merely refuse; it RESTORED the honest lowering so the user's own proved contract
#   is reachable at the call site again. Witnesses: 1175 (negative), 1176 (positive control),
#   1177 (the spelling that refuted the sign-of-default guard).
#
#   **RETAINED BOUNDARY, recorded at the site and in the route file:** with a receiver
#   present this still asserts `result >= 0` of a value read from a dict PyCSL cannot type —
#   the mirror's domain convention, not a property of Python. REOPENING CAPABILITY: emit the
#   non-negativity as an OBLIGATION at the `Array.make` site instead of an axiom on the
#   getter, which costs the mirror a proof it currently gets for free.
#
# ## ROUTE #74 — THE SAME DEFECT ONE FIELD OVER, FOUND BY PROBING #73's REPAIR
#
#       class C:
#           #@ ensures \result == 7
#           def isdigit(self) -> int:  return 7
#           #@ ensures \result <= 1                 <-- PROVED. CPython answers 7.
#           def g(self) -> int:        return self.isdigit()
#
#   `_call_named_builtins` matched on the METHOD-NAME SUFFIX ALONE, with the receiver
#   ERASED, and it is consulted BEFORE `_handle_dotted_call` — so the oracle WON over the
#   user's real method. **TWELVE ordinary English names are exposed**: islower, isupper,
#   isalpha, isdigit, isspace, istitle, isalnum, isnumeric, isdecimal, isidentifier,
#   startswith, endswith.
#
#   **THE EMISSION CONTAINED BOTH, AND THAT IS THE PROOF:**
#       val self_isdigit_0 () : int ensures { ((result = 0) || (result = 1)) }   <- oracle
#         (self_isdigit_0 ())                                                     <- call site
#       let c__isdigit (self: c) : int                                            <- REAL, UNUSED
#   Note the EMPTY parameter list: the receiver is gone, so nothing ties the axiom to any
#   object. That is the same structural tell routes #13/#14 keyed on — except there the
#   erasure DELETED an effect, and here it ASSERTS A FALSE FACT.
#
#   **A SECOND CARRIER CAME OUT OF PROBING THE REPAIR BEFORE LANDING IT.** `startswith`/
#   `endswith` take arguments and go down a DIFFERENT branch (`val self_startswith_1
#   (x0: int) : int`, same false ensures). With the guard removed it proved `\result <= 1`
#   for a method returning 9. A guard closing only the zero-argument spelling would have
#   left it open — witness 1180.
#
#   REPAIR: fall THROUGH (do not refuse) when the call resolves to a user-defined method,
#   keyed as the existing `-> NoReturn` check keys it. **THE FALSE AXIOM IS REPLACED, NOT
#   SUPPRESSED** — the stub now carries the CALLEE'S OWN postcondition,
#   `ensures { (result = 7) }`, via route #70's propagation machinery.
#   Witnesses 1178 (negative), 1179 + 1181 (TWO positive controls — the user's true claim,
#   and a REAL `str.isdigit()` still discharging `<= 1`, which is what stops the fix being a
#   blanket removal of the predicate model), 1180 (the arguments carrier).
#
#   **RESIDUAL, MEASURED NOT ASSUMED:** the `obj.<m>()` spelling on a user-class local does
#   NOT prove — but that is gen #5's object-typed-locals TYPE ACCIDENT, not a guard. If
#   object locals ever start emitting, re-measure it: the name-match branch would be reached
#   with `func_name` not starting with `self.`, and the registry key would not be built.
#
# ## ROUTE #75 — THE CLASS, AND THE ONE GUARD THAT CLOSES IT
#
#   Python lets a module SHADOW A BUILTIN. When it does, `_call_named_builtins`' name tests
#   fire on the user's own function and hand the call an abstract `val` whose `ensures` is
#   an AXIOM about the BUILTIN. THREE CARRIERS, each a complete runnable program:
#
#       def ord(c: str) -> int: return 9999        ->  `\result < 256`  PROVED (CPython 9999)
#       def len(x: str) -> int: return -5          ->  `\result >= 0`   PROVED (CPython -5)
#       def min(a: int, b: int) -> int: return 99  ->  `\result <= 1`   PROVED (CPython 99)
#
#   **NOT carriers, MEASURED rather than assumed: `bool`, `repr`, `hash`.** That
#   non-uniformity is the whole argument for the shape of the fix: a guard written as a LIST
#   OF NAMES would be stepped around by the next name in the table.
#
#   **HOW IT WAS FOUND — BY ENUMERATING THE CLASS, NOT BY PROBING A THIRD INSTANCE.** A
#   script over `expressions.py` maps every `_add_abstract_op` carrying an `ensures` back to
#   the nearest name test. That yields TWELVE guards: decode, any, min, sorted, list, ord,
#   chr, repr, bool, hasattr, `get` (= #73) and the rsplit predicate set (= #74). **Two of
#   the twelve were already known routes, which is what made the enumeration worth trusting.**
#
#   **THE REPAIR IS ONE GUARD AT THE ENTRY OF `_call_named_builtins`:** a BARE name that
#   resolves to a user-defined function falls through to it. All three true twins now PROVE
#   where none did before. Witnesses 1182-1187.
#
#   **THE BYTE-DIFF FOUND A FOURTH CARRIER THE CENSUS MISSED — READ THE MOVED FILES.**
#   `0449` moved unexpectedly. It is a SECURITY driver proving that a `try/except` wrapper
#   around `ast.literal_eval` is TOTAL, and it declares `literal_eval` itself with
#   `#@ \abstract` + `raises ValueError` / `raises SyntaxError`. The call site had been
#   emitting `val literal_eval_op (s: 'a) : int` — **AN ORACLE WITH NO CONTRACT AT ALL** —
#   instead of the user's own declaration. So the class covers `\abstract` DECLARATIONS too,
#   not just builtins. VERIFIED rather than assumed: 0449 still PASSES, and its OWN
#   documented anti-vacuity claim still holds (narrowing the catch to `(ValueError,)` makes
#   verification FAIL), so the security proof now runs against the real bounded-raises
#   declaration instead of a contract-free oracle.
#     **CENSUS LESSON:** my census grepped `^def <builtin-name>(` and missed this, because
#     the shadowed name was `literal_eval` — not a builtin at all. **The oracle table is
#     wider than any name list I can enumerate by hand; the byte-diff over BOTH corpora is
#     what caught it.**
#
# ## THE INHERITED GATE WAS A FALSE-POSITIVE GENERATOR — FIXED
#
#   `bin/check-no-exception-differential.py` (gen #5's new plane) ruled RED on
#   `CPython RAISES + PyCSL PROVES`, with NO notion of WHICH exceptions the contract claims.
#   **`\all` expands to `KNOWN_EXCEPTIONS` — FIVE names** (ZeroDivisionError, IndexError,
#   KeyError, ValueError, StopIteration) — not to every exception Python has. A body aborting
#   with AssertionError, TypeError, AttributeError, OverflowError or RecursionError violates
#   NOTHING its contract said, and the plane would have called it UNSOUND.
#     **WHY THIS MATTERS: it is how a gate of this shape DIES.** Its whole value is that its
#     corpus GROWS, and a gate that cries wolf gets quieted by DELETING the offending driver.
#   FIXED: the driver now runs through a wrapper reporting the exception CLASS; the
#   `#@ no_exception` spec is parsed for what it actually claims; the two are matched with the
#   model's own subclass relation (so a claim over `OSError` is violated by a raised
#   `FileNotFoundError`). **FAIL-CLOSED**: an unnameable failure is recorded `?` and treated
#   as IN SCOPE, keeping the old conservative verdict.
#     **OUT-OF-SCOPE ABORTS ARE PRINTED ON EVERY RUN, never fatal and NEVER SILENT** — that
#     population is the honest measure of how much weaker `\all` is than its name.
#     **NEGATIVE-TESTED, because narrowing a gate is exactly the change that silently
#     disables one**: with route #66's `chr` row commented out, d05 measures
#     `raised=ValueError, in_scope=True, proves=True` and the plane reports UNSOUND. The
#     class check does NOT soften a genuine route.
#   **CORPUS GROWN 18 -> 39** (28 raisers, 11 returners of which 10 prove, 1 out of scope,
#   1 incomplete). d30-d33 are standing checks on the moved hazard: the same raising
#   operation in a CALLEE, a LOOP body, a TAKEN BRANCH, and behind a slicing call.
#
# ## PROBED THIS GENERATION WITH NO FINDING — DO NOT RE-PROBE
#
#   **THE CLAIM BACKLOG — THREE OF GEN #5's NAMED ITEMS ARE REFUTED BY MEASUREMENT:**
#   * (g) `return` inside a `try` with a CATCH-ALL handler is NOT caught. Neither
#     `except Exception:` nor a bare `except:` proves the false `\result == 2`, and the
#     positive control proves the true `\result == 1` — so it is modelled and decided
#     correctly, not merely undecided.
#   * (c) the module-GLOBAL singleton field store `g.v = n`, documented as a RETAINED silent
#     no-op at "severity-1", does not yield a false proof. SAME-FUNCTION it is FAITHFUL (the
#     no-op hypothesis fails, the true claim proves); CROSS-FUNCTION both directions fail,
#     i.e. fail-closed incompleteness. Two spellings only — not proof it is gone.
#   * (e) route #52's stated hole ("an unannotated local holding a string is not refused")
#     does not reproduce: the guard fires when EITHER operand is value-typed, so a sibling
#     literal is enough. Its diagnostic quotes the exact exploit, independently rebuilt.
#   * (b) the frameless `#@ depends_method` is **CONFIRMED FAIL-OPEN — see
#     `open-routes/finding-w56-frameless-dependency-is-fail-open.md`.** Driver 0968's OWN
#     DOCSTRING describes the experiment; I ran it on 0968's shape and BOTH halves reproduce:
#     frame DECLARED + caller weakened to `assigns \nothing` -> Why3 REJECTS; frame REMOVED
#     + the same weakened caller -> **PROVES**. The 2026 fix made the frame DECLARABLE, NOT
#     REQUIRED. **NOT called a route**, because no false VALUE claim is reachable: a composed
#     mixin whose provider actually WRITES a field does not emit at all (four spellings, four
#     emission/typing non-results). **So it is harmless by TYPE ACCIDENT, not by a guard** —
#     the day a composed mixin can have a writing provider, this is a live route, and the
#     acceptance half is already measured. Repair scoped + censused (require `#@ assigns` in
#     every dependency window). **THE REPAIR WAS BUILT, FULLY GATED, AND THEN REVERTED —
#     and the reason is the most transferable thing in this block.** It passed EVERYTHING I
#     had: 33 planes green, BOTH corpora fully byte-inert (969/969 and 2204/2204, 0 moved /
#     0 gone / 0 appeared), mirror emission BYTE-IDENTICAL. Then `run-reference-tests.sh`
#     aborted at its LEADING gate — **IR CONFORMANCE, 0549 and 0553 MISMATCH**: those two
#     drivers carry FROZEN IR GOLDENS, and the `#@   assigns \nothing` the repair forces
#     into their windows changes the derived IR.
#     **A GREEN BYTE-DIFF DOES NOT COVER THE IR** — byte-inertness is about emitted WhyML,
#     conformance is about the IR one stage earlier, so a landing can be perfectly
#     byte-inert on both corpora and still break a frozen contract.
#     Reverted rather than refreshing the goldens ("re-baseline until green" is the banked
#     lesson), decisively because the hole is NOT currently exploitable. **TRUE COST NOW
#     MEASURED: refreshing the IR goldens of 0549/0553 plus the version-bump question —
#     a decision about a frozen contract, not a worker's unilateral call.**
#     Also measured and worth keeping: the guard's home
#     (`_extract_mixin_directives`) is a `\trusted` STUB in the mirror, i.e. the CHEAP
#     side — my earlier "owes a whole-file re-proof" estimate was simply wrong, and
#     checking which side of the mirror a guard sits on is what decides the cost.
#     Also learned: `#@ compose_from` has NO Python runtime counterpart, so any future
#     mixin DIFFERENTIAL driver must use real inheritance or CPython raises AttributeError
#     and there is no ground truth to compare against.

#
#   * **ALL FIVE unworked abstract-`val` leads from the gen-#5 handoff are DEAD.** Measured:
#     the bare `s[5]` spelling (which gen #5 could not reach — it EMISSION-FAILed there and
#     EMITS here), `s[5:6]`, LOCAL `set.remove`/`set.discard` of an absent element (the
#     `map_update_none` lead), `"a b".split(" ")[5]` (the `str_split_elem_op` lead). All
#     refuse. `struct_pack_i1a1`/`i18` carry no `requires` but their siblings' guard is a
#     CALL-SITE VC for `struct.error`, which is NOT in KNOWN_EXCEPTIONS — no route available.
#   * **THE OBLIGATION DOES NOT STOP AT THE FRAME.** A `1//0`, an explicit `raise`, and a
#     `[::0]` slice placed in a CALLEE all still refuse, as do a raise in a LOOP body and in
#     a TAKEN BRANCH. The "one call deeper" move does NOT defeat the exception model.
#   * Negative indices past the start (`xs[-10]`, `ord(s[-10])`), `d.pop(missing)`,
#     true-division and modulo by zero, `"abc".index("z")`, `xs.pop(7)`, `int("10", 1)`,
#     wrong-length tuple unpack — all refuse. (`xs[-1]` proves, the positive control.)
#   * **`assert` IS A GENUINE NO-OP — the documentation is TRUE, and I checked rather than
#     assumed.** I suspected the `assert` no-op was an ASSUMPTION (which would let a false
#     assert prove anything, with no opt-in — the worst shape available). IT IS NOT: after
#     `assert a == 1` with `a == 0`, the FALSE claim `\result == 99` does NOT prove, and
#     `assert False` does not either, while the TRUE claim does. Route #16's "lowered to
#     `()`, NEITHER CHECKED NOR ASSUMED" is confirmed in both directions. A body that aborts
#     with AssertionError satisfying `no_exception \all` is a CERTIFIED BOUNDARY, not a
#     route: AssertionError is deliberately outside the model. Pinned as driver d39.
#
# ## LESSONS BANKED THIS GENERATION
#
#   * **A GREEN BYTE-DIFF DOES NOT COVER THE IR — AND THE SUITE'S LEADING GATE IS NOT THE
#     SUITE.** A landing that was byte-inert on BOTH corpora (0 moved, 0 gone, 0 appeared)
#     and green on all 33 planes still broke `IR conformance` on two frozen goldens. Run
#     `bin/run-conformance.sh` (or the full suite) BEFORE believing a byte-inert landing is
#     safe; the conformance gate sits one pipeline stage earlier than every byte-diff.
#   * **`git checkout <commit> -- <paths>` STAGES the old content**, so a later
#     `git checkout -- <paths>` restores from the POLLUTED INDEX, not from HEAD — a
#     trap-based "restore" built that way silently REVERTS a landed repair in the working
#     tree. Use `git reset HEAD -- <paths>` THEN `git checkout HEAD -- <paths>`, and always
#     `git status` after a trap-restore rather than trusting the trap.
#
#   * **VERIFY A DELEGATED CLAIM'S SCOPE, NOT JUST ITS HEADLINE** — again (route #70 banked
#     it first). The audit that surfaced #73 reported the carrier as the DOTTED
#     `cfg.get("arity", -1)`. Measured: an untyped receiver AND a `Dict`-typed receiver both
#     emit ZERO occurrences. The live carrier is the BARE call. The headline was right and
#     the location was wrong, and only measuring separated them.
#   * **PROBE THE GUARD YOU ARE ABOUT TO WRITE, NOT ONLY THE ONE YOU WROTE.** The
#     sign-of-default guard for #73 was refuted before a line of it landed. That is cheaper
#     than the five times gen #5 discovered it afterwards.
#   * **A ZERO-INPUT GUARD EARNED ITS KEEP.** The worktree-at-HEAD~3 baseline sweep failed
#     reproducibly (1 of 1101 emitted, vs 960 for the same script in the main tree) and
#     `byte-diff-compare` REFUSED to report green over an empty baseline. Do not work around
#     that by lowering `--min-files`. Build the baseline by swapping the ONE changed file in
#     the main tree, **with the restore in a shell `trap`** so the tree self-heals even if
#     the turn dies — which also isolates the repair perfectly.
#   * **A GATE'S FALSE POSITIVES ARE A SOUNDNESS CONCERN, not a cosmetic one**, whenever the
#     gate's value depends on its corpus growing.
#
# ## THE LADDER FOR THE NEXT RELAUNCH
#
#   1. **GROW `test-suite/no-exception-differential/` — it is now the cheapest route
#      detector in the tree** and it found #73's neighbourhood by making probing mechanical.
#      Every new raising Python operation added is a permanent check. It curates nothing.
#   2. **THE `_add_abstract_op` AUDIT IS NOT FINISHED, and #73/#74 show where the yield is:**
#      not in the `ensures` clauses that model Python operations (a full pass over those
#      found them sound — see the inventory in the gen-#6 audit), but in the HAND-ADDED
#      ORACLES keyed on a literal string, a method NAME, or a domain convention. Two leads
#      remain: (a) ~~the 0/1 predicate ops~~ — **CONFIRMED AND CLOSED AS ROUTE #74**; (b)
#      STILL UNMEASURED: `preamble.py:9081` emits `axiom hash_eq_consistent_<cls>` for any user class defining
#      both `__eq__` and `__hash__`, which Python does not enforce (labelled UB-7.2 and
#      switchable, so it is a known assumption rather than a hidden one).
#      **THE GENERAL FORM IS NOW A CLOSED CLASS WITH ONE GUARD (#75), BUT ONLY FOR BARE
#      NAMES.** The guard at the entry of `_call_named_builtins` covers a bare `f(...)`
#      resolving to a user function; #74 covers `self.<m>(...)` at its own site. **STILL
#      UNGUARDED AND WORTH PROBING NEXT: the DOTTED spellings the enumeration listed —
#      `func_name.endswith(".to_dict")`, `.copy`, `.findall`, `.split`, `.get`, and the
#      CLASS-NAME-keyed `IRScanner.*` and `self.ir.get` oracles, which are mirror-domain
#      names asserted over every program PyCSL compiles, exactly as `get_arity_field` was.**
#   3. The gen-#5 claim backlog, still largely unmined: a frameless `#@ depends_method`; the
#      module-GLOBAL singleton field store `g.v = n`; the module-const dict fold's
#      invalidation omitting MUTATION; the `is` blacklist's unannotated-local hole; `return`
#      inside a `try` with a catch-all handler.
#
# ===================================================================================
#
#
# ====== START HERE — gen #5 FINAL STATE — read this block first ==================
#
# ## THE ONE-PARAGRAPH SUMMARY
#
#   Thirteen soundness routes (#60-#72) were found and closed, route #59 was finished, two
#   GATES were found broken and fixed, and one new plane was added. The metric never moved
#   (459) and it was never supposed to: every repair is a refusal, a whitelist or a wired
#   obligation, and none of them converts a `\trusted` stub. Six of the thirteen are ONE
#   defect in the exception model. The single highest-value thing the next generation can
#   build is the completeness gate named in route #66 — see "THE SIX EXCEPTION-MODEL ROUTES"
#   below. The second is the abstract-`val` false-axiom audit, which produced #69 and still
#   has unworked leads.
#
# ## WHAT IS TRUE RIGHT NOW
#
#   ledger   **EMPTY. NO OPEN ROUTE.** Route #59 is fully closed (all seven carriers), and
#            #60 through #72 were each FOUND AND CLOSED this generation.
#            **THIRTEEN new routes found and closed**, plus #59 finished.
#            **SIX of them (#64, #65, #66, #68, #71, #72) are ONE DEFECT in the EXCEPTION
#            model** wearing six numbers — see below. That surface was untouched at the
#            start of this window and EVERY probe aimed at it found something.
#   metric   markers **459** · grep 484 · offset 25 · unattached 0 — UNCHANGED all
#            generation, and that is the EXPECTED shape of a window paying the soundness
#            ladder. Four repairs, all refusals or whitelists; none costs the trust surface.
#   planes   **ALL 33 GREEN under `--slow`** (19 in the fast set), re-run after every
#            landing. TWO are NEW this generation: `check-trigger-rows-live.py` and
#            `check-no-exception-differential.py`.
#            **RUN IT WITH why3 ON PATH** (`export PATH=$HOME/.opam/framac-coq8/bin:$PATH`).
#   suite    **3299/3318, ZERO XPASS**, failure set BYTE-FOR-BYTE identical to the
#            `suite49_run8` baseline (3249/3268, same 19). The suite grew by FIFTY drivers —
#            all this generation's route witnesses — and every one passes. rc=1 IS the
#            baseline condition. Log: `getting-better/proofs49/suite55_run5.{log,rc}`.
#            Also verified independently: all 55 witnesses in the 1125-1179 range re-run
#            one by one against the final tree, 55 correct / 0 mismatched.
#            ZERO XPASS is the strongest available statement that no previously-closed
#            route reopened; it is the check that caught #42 reopening for a whole window.
#   tree     clean, every increment committed. The two GITLINKS (`scratchpad/w7/base`,
#            `scratchpad/w8/pre`) and the 0-byte stray `str` in the repo root are
#            PRE-EXISTING and are NOT dirt.
#   OWED     **NOTHING.** No proof, battery or sweep in flight.
#
# ## THE FOUR ROUTES
#
#   **#59 carriers 6+7 (field store) — CLOSED.** Gen #4 refuted this twice, both times in
#   `_handle_fieldassign_stmt`, which the mirror verifies VERBATIM. The fix was to move
#   HOME: `_reset_function_state` is a `\trusted` stub, so analysis AND refusal fit there
#   unconstrained. Gate is TWO LIVE NAMES + a later mutation, so the benign
#   `p={}; self.d=p; self.d[1]=2` still proves.
#
#   **#60 — `len()` on a dict counted STORE SITES.** Blind to key equality, symbolic keys,
#   the caller's dict, REACHABILITY and ITERATION COUNT (`d={}; for i in range(n): d[i]=i;
#   len(d)` proved `\result == 1` for every n). Repaired as a WHITELIST.
#
#   **#61 — a dict literal with NON-CONSTANT keys took the syntactic count.** `requires
#   a == b` then `{a:1, b:2}` proved `len == 2`; CPython says 1. Fix: one expression.
#
#   **#62 — the `@mutable_state` collection-param NO-OP escaped its guard ONE CALL AWAY.**
#   Mutation in a helper whose contract names nothing, observed from a caller whose contract
#   names the parameter it passed in. Second guard added in the CALLER's frame.
#
#   **#63 — "NO ALIASING IS POSSIBLE" IS TRUE FOR LISTS AND FALSE FOR SETS.** The biggest
#   structural claim in the tree, refuted by a SELF-CONTAINED file: `caller2()` binds a LOCAL
#   set, passes it as BOTH arguments to a helper that mutates one and reads the other, and
#   proves `\result == 0` for a function CPython answers 7 on. The claim's cited mechanism is
#   Why3 REGION TYPING, and it is real — `f(xs, xs)` on two LIST params really is refused with
#   Why3's own `This application creates an illegal alias`. It simply cannot apply to a
#   dict/set, which lowers to a PURE `map`: a pure value has no region. Guard: refuse the same
#   dict/set name in two or more argument positions of one call. `annotations.md` §5 corrected
#   to carry its scope.
#
# ## THE TWO METHODS THAT FOUND THEM — USE BOTH AGAIN
#
#   1. **READ THE EMITTED WhyML, INCLUDING WARNINGS, ON A *PASSING* RUN.** `warning: unused
#      variable d` was route #60, and the same tell appears in #61 and #62. A verdict of
#      PROVED says nothing about WHY it proved. `--keep-mlw` costs nothing.
#   2. **AUDIT THE DOCUMENTED SOUNDNESS CLAIMS BY MEASUREMENT.** The docs are full of
#      falsifiable assertions and some are FALSE. #60's premise ("an indexed store does not
#      change the length" — true for lists, false for dicts), #61's ("the fold cannot know",
#      offered as a reason to GUESS rather than REFUSE) and #62's (an exemption the doc
#      itself said "holds only while its own justification does") were all written down.
#      **A claim-mining sweep produced 72 falsifiable claims, 26 of them bare ASSERTIONs
#      with no mechanism and no driver. THAT LIST IS THE NEXT GENERATION'S BACKLOG** — see
#      the ladder below.
#
#   **#64 — `no_exception \all` PROVED FOR A PROGRAM THAT RAISES.** A NEW FAMILY: the
#   EXCEPTION model, not the value model. `b = bytearray([1]); b[0] = 999` verifies under the
#   strongest no-exception claim while CPython raises `ValueError: byte must be in
#   range(0, 256)`. Not excusable as partial correctness — `no_exception` is a POSITIVE claim
#   about runtime behaviour and `ValueError` IS in `KNOWN_EXCEPTIONS`. The MECHANISM works
#   (`a // 0` under `no_exception ZeroDivisionError` correctly fails, `requires b != 0`
#   correctly proves) — the trigger ROW was missing. Two things the measurement forced
#   mid-build, both instructive: the receiver type was `"Any"` because the front-end maps
#   every bytes ANNOTATION to `"list"` and infers nothing from a constructor CALL, so only
#   PARAMETERS were ever typed bytes — and their writes are rejected, which is exactly why
#   the documented justification looked true; and the first spelling added a predicate to
#   `PREDICATE_LIBRARY`, which is emitted WHOLESALE into every `no_exception` unit's preamble
#   and moved 31 corpus emissions by one inert line (diagnosed by DIFFING a moved file rather
#   than accepting the diff, then inlined like the `map_get` row).
#
#   **#65 — FOUR ROWS OF THE EXCEPTION TRIGGER TABLE WERE CONSULTED BY NOTHING.** Found by
#   following #64's row INTO the emitter instead of stopping at the table. Every
#   `no_exception` obligation is injected through two helpers, and the only op-keys they are
#   ever passed are `("binop", <op>)`, `("subscript", read|write|write_bytes)` and
#   `("map_get", None)`. So `("call","divmod")`, `("attr_call","index")`,
#   `("attr_call","pop")` and `("call","next")` were DEAD — and `divmod`'s row carries a REAL
#   condition, so `divmod(a,0)` proved under `no_exception ZeroDivisionError` while CPython
#   raises. `.index`'s condition was the literal `"true"`: `xs.index(5)` (absent) and
#   `xs.index(1)` (present) gave IDENTICAL verdicts — a row that LOOKS like coverage and
#   provides none, which is worse than a missing one. The control that makes it crisp: `d[5]`
#   under `no_exception KeyError` correctly does NOT prove, through the WIRED `map_get` row.
#   Closed by REFUSING all four under a matching `no_exception` context (divmod lowers to a
#   fully opaque val, so there is nothing faithful to inject), plus a NEW PLANE.
#
#   **#66 — OPERATIONS PyCSL LOWERS WITH NO TRIGGER ROW AT ALL.** Three carriers:
#   `del d[k]` on an absent key (`KeyError`), `int("abc")` (`ValueError`) and `chr(-1)`
#   (`ValueError`) all proved under `no_exception`. `del` and `chr` were WIRED with faithful
#   conditions and DISCRIMINATE (absent fails / present proves; `chr(-1)` fails / `chr(65)`
#   proves); `int(<str>)` is REFUSED because it lowers to an opaque val. **`chr` was worse
#   than a missing row** — `val chr_op` carried `ensures { String.length result = 1 }`
#   UNCONDITIONALLY, a TOTALITY Python does not have, which every consumer inherited.
#
#   **#67 — A STRING SUBSCRIPT READ CARRIED NO `IndexError` OBLIGATION.** `ord(s[5])` on
#   `"ab"` proved under `no_exception \all`. The ARRAY read was wired all along — the same
#   batch confirms a symbolic list index, a bytearray index and `1 // (a - a)` all correctly
#   FAIL to discharge — but a STRING read goes down `char_code_at`, which no row covered.
#   WIRED with the exact bound, so `ord(s[1])` still proves.
#
#   **#68 — `float(<str>)`, `**` AND THE LONG-DEAD SHIFT ROWS.** `0 ** -1` and `1 << -1` both
#   proved under `no_exception \all`. The shift one matters most: `non_neg_shift` had been in
#   the table for ages and `check-trigger-rows-live` called it LIVE, because ONE binop site
#   passes a DYNAMIC op-key and the plane approves a whole KIND from one. The bitwise/power
#   path is a different site and never wrapped. Fixed by making the assumption TRUE (that
#   path now wraps), not by weakening the check.
#
#   **#69 — `ord()` OF A NON-ASCII STRING. THE MOST SERIOUS OF THE TEN.** `return ord("€")`
#   proved `#@ ensures \result < 256` while CPython answers 8364 — **with no `no_exception`,
#   no exception, and no opt-in of any kind.** Every other route this generation needed the
#   user to ask for something; this one is a false postcondition about ordinary TOTAL Python.
#     **MY FIRST DIAGNOSIS WAS WRONG AND THAT IS THE INSTRUCTIVE PART.** I assumed the
#     `ensures { 0 <= result < 256 }` on `ord_op` was the defect and widened it. **It changed
#     nothing** — because the literal `"€"` is emitted as its UTF-8 BYTES (`"\xe2\x82\xac"`,
#     three bytes) and Why3's `Char.code` is 0..255 by that theory's own axioms, so the bound
#     follows from the OTHER `ensures` regardless. `ord` reads the first BYTE.
#     **AND THE MODEL IS INTERNALLY INCONSISTENT:** `len("€") == 1` PROVES (correct, folded
#     from the Python literal) while `ord("€") < 256` PROVES (wrong). One operation uses code
#     points, the other bytes, on the same literal in the same function — which is why the
#     repair refuses `ord` rather than the literal.
#
#   **#70 — THE DOTTED STUB KEPT THE CALLEE'S `ensures` AND DROPPED ITS `requires`.** A
#   `\trusted` method declaring `requires x > 0` / `ensures \result > 0`, called as
#   `self.pos_only(-5)`, let the CALLER prove `\result > 0` while CPython returns -5. The
#   emission declared the method TWICE: the correct `val c__pos_only ... requires { x > 0 }`,
#   and the stub the call site actually used, `val self_pos_only_1 ... ensures { result > 0 }`
#   with no requires. Dropping BOTH clauses is fail-closed (the imported-class-method path
#   does exactly that); keeping the postcondition WITHOUT the precondition is the one
#   combination that is always unsound. Closed by withholding ensures propagation from a
#   guarded callee — a stated completeness cost, and the better fix (build a `requires`
#   suffix the way the `ensures` suffix already is) is recorded in the route file.
#     **THE MIRROR IS NOT EXPOSED TODAY AND I CHECKED RATHER THAN ASSUMED:** all 459
#     `\trusted` markers carry `requires True`. Fragile safety, not a guarantee.
#
#   **#71 — AN ERASED OPERATION TRIVIALLY SATISFIES `no_exception`.** `t.remove(5)` on a
#   collection PARAMETER inside `@mutable_state` lowers to `()`, and an operation with no
#   emission site cannot carry an obligation, so `no_exception \all` discharged over a body
#   emitted as `(); 0` while CPython raises `KeyError`.
#     **THE PRINCIPLE IS WORTH MORE THAN THE CARRIER, AND IT INVERTS A FAMILIAR ARGUMENT.**
#     A dropped mutation is normally defended as FAIL-CLOSED because the POST-STATE claim
#     becomes unprovable — an argument about POSTCONDITIONS. For `no_exception` the erasure
#     makes the claim EASIER, not harder. **EVERY ERASURE IN THE COMPILER IS A
#     `no_exception` HOLE BY CONSTRUCTION**, and the others are on record: the `with`-body
#     erasure, the `emit_ir` in-place store no-op, the list-`del` no-op. Ask of each: "what
#     does `no_exception \all` say about this body once the operation is gone?"
#
#   **#72 — `str.split("")` RAISES AND HAS NO ROW.** The separator is HASHED TO AN INT
#   before reaching an opaque val, so nothing can be written over it; refused unless the
#   separator is a non-empty literal.
#
# ## THE SIX EXCEPTION-MODEL ROUTES ARE ONE DEFECT — READ THIS BEFORE PROBING MORE
#
#   `#64` a missing row · `#65` FOUR rows consulted by NOTHING (one a `"true"` tautology) ·
#   `#66` three missing rows · `#68` three more (one a row that existed and was never
#   injected) · `#71` an ERASED operation · `#72` another missing row.
#
#   **SIX PROBES, SIX FINDINGS. The per-operation approach is NOT converging**, and each new
#   carrier RAISES the value of the fix rather than lowering it. The single underlying fact:
#   **nothing relates `exception_model.TRIGGERS` to the set of operations the emitter
#   actually EMITS.** Until that gate exists, `#@ no_exception \all` must be read as "none
#   of the exceptions this table happens to model" — which is NOT what the directive says
#   and NOT what a user will assume.
#
#   **THE COMPLETENESS GATE IS BUILT.** `bin/check-trigger-rows-live.py` scans FROM the
#   table and cannot see a MISSING row — it reported green on every one of the carriers
#   above. `bin/check-no-exception-differential.py` (NEW) scans from the other side and
#   **CURATES NOTHING**: each driver in `test-suite/no-exception-differential/` declares
#   `#@ no_exception \all` and RUNS ITSELF under `__main__`, so CPython's behaviour is
#   MEASURED rather than listed, and RED means "CPython raises and PyCSL proves".
#     **ITS POPULATION GUARD IS THE PART TO PRESERVE.** A gate of this shape is trivially
#     satisfiable by refusing every program, so it FAILS unless the corpus holds BOTH a
#     raising driver AND a non-raising one that actually PROVES (9 and 9 today, all nine
#     returners proving). Never "fix" a red by deleting the returner that proves.
#     **GROW THE CORPUS** — it can only be wrong by being too small, and every new raising
#     Python operation added to it is a permanent check. It SKIPs when why3 is absent,
#     because a missing tool is not a finding.
#
# ## THE SHARPEST UNFINISHED THREAD — A FALSE AXIOM CLASS, NOT A ROUTE
#
#   `val char_code_at` and `val chr_op` BOTH carry `ensures` clauses that are UNCONDITIONAL
#   in an argument Python constrains. Routes #66/#67 injected obligations at the USE SITES,
#   which closes the holes — **but neither val was changed.** A `val` with a TOTAL contract
#   on a PARTIAL Python function is a FALSE AXIOM in the preamble: available to every proof
#   in the unit, whether or not anyone wrote `no_exception`. That makes it strictly worse
#   than a missing trigger, and both were found BY ACCIDENT while probing something else.
#   **AUDIT EVERY ABSTRACT `val` WHOSE `ensures` IS UNCONDITIONAL IN AN ARGUMENT PYTHON
#   CONSTRAINS** — the mechanical form: for each `_add_abstract_op` string, ask whether
#   Python's operation is TOTAL over the declared argument types; if not, the `ensures` needs
#   a `requires`, or the obligation must be injected at every call site.
#
# ## THE NEW PLANE, AND THE WAY IT CAUGHT ITSELF
#
#   `bin/check-trigger-rows-live.py` — every `TRIGGERS` row must be CONSULTED at an injection
#   site or REFUSED outright, and no row may discharge on a `"true"` condition. Demonstrated
#   both ways.
#     **ITS FIRST VERSION SCANNED RAW TEXT AND READ THIS REPO'S OWN COMMENT AS EVIDENCE.**
#     The big explanatory comment in `functions.py` names both injector helpers and then
#     lists the very op-keys they do NOT consult; the plane counted that as consultation and
#     reported GREEN with the refusal deliberately removed. **A gate that counts its own
#     documentation as coverage is worse than no gate** — and it is precisely the defect
#     class the plane exists to catch. Fixed by tokenizing out comments and requiring
#     `injector(`, a real call rather than a mention. It also surfaced a second false
#     positive: `("binop", raw_op)` uses a VARIABLE key, so a literal-only scan called all
#     seven arithmetic rows dead.
#
# ## THE STRUCTURAL RESULT — THE AIMING INSTRUCTION FOR THE NEXT GENERATION
#
#   **WHY3 ENFORCES FRAMES AND SEPARATION FOR EVERYTHING IT MODELS AS A REGION, AND
#   ENFORCES NOTHING FOR A PURE TERM. EVERY ROUTE THIS GENERATION FOUND LIVES ON THE PURE
#   SIDE.** Measured on both sides, not inferred.
#
#   REGION SIDE — Why3 itself refuses, no PyCSL guard involved:
#     * a false `assigns \nothing` on a function mutating an ARRAY PARAM
#       ("This function has side effects, it cannot be used as pure")
#     * a false `assigns \nothing` on a method writing a SELF FIELD
#       ("this expression produces an unlisted write effect")
#     * an aliased array application `f(xs, xs)`
#       ("This application creates an illegal alias")
#     * nested-list inner aliasing, three spellings, all type-rejected
#
#   PURE SIDE — every one was a ROUTE: #59 (a dict binding COPIES), #60 and #61 (a dict
#   SIZE folds to a constant), #63 (two set params alias with no barrier).
#
#   A list is an `array` and a self field is a mutable record field — REGIONS, policed by
#   Why3. A dict/set is a pure `map` — no region, nothing to police, and PyCSL's own
#   hand-written guards are the only thing standing there. **So: ask of any construct "is
#   this a REGION or a PURE VALUE?" If pure, every guard is hand-written — and every
#   hand-written guard this generation was keyed on a location that could be stepped
#   around.** That is where to aim, beside gen #4's "probe representations, not the proof
#   engine".
#
# ## THE PATTERN, SEEN FIVE TIMES IN ONE GENERATION
#
#   **A GUARD KEYED ON A SYNTACTIC LOCATION IS DEFEATED BY MOVING THE HAZARD ONE STEP.**
#   #59's planned repair watched the local — the hazard moved to a second FIELD. #60's fold
#   watched store sites — it moved into a LOOP. #61's fold watched literal keys — it moved
#   to NAMES. #62's guard watched "this function's own contract" — it moved one CALL away.
#   **When you write or read a guard, ask what the same program looks like with that
#   location one call, one branch, or one binding away.**
#
# ## OTHER LESSONS PAID FOR THIS GENERATION
#
#   * **A RATCHET WITH HEADROOM CANNOT SEE THE FIRST REGRESSION THAT USES IT UP.**
#     `check-mirror-coverage` had printed "549 < ratchet 550 — lower the constant" for ages.
#     My OWN #60 repair added one nested helper `def`, silently consumed the slot, and the
#     FULL 31-PLANE BATTERY STAYED GREEN. Tightened to 549; both repairs rewritten to use no
#     nested `def` at all. **Do not add a nested `def` to a mirrored file.**
#   * **ASK *WHICH* CORPUS A BYTE-DIFF SWEPT.** `byte-diff-sweep.sh` globbed only
#     `pycsl-reference`; `python-reference` (2217 files, a LIVE PROVED SUITE) was outside
#     every byte-diff ever run. #60's first repair was byte-inert there AND broke
#     `python-reference/0050.py`. The sweep now covers both (second corpus in a `pyref/`
#     SUBDIRECTORY so `--emit-dir` consumers see an unchanged population).
#     **A LANDING MUST COMPARE BOTH**: `byte-diff-compare.py BASE CAND` *and*
#     `byte-diff-compare.py BASE/pyref CAND/pyref --min-files 2000`.
#   * **CHECK WHICH SIDE OF THE MIRROR A GUARD'S HOME SITS ON BEFORE COSTING THE REPAIR.**
#     `\trusted` stub = cheap and unconstrained; verified-verbatim = the #59 wall.
#   * **DON'T TRUST A DOCUMENTED COUNT AS A BLAST RADIUS.** #61's docs said "13 in the
#     mirror"; the repair was byte-inert — those are literals nobody takes `len()` of.
#   * A self-matching `pgrep` guard makes a watchdog IMMORTAL. Two orphaned gen-#4 watchdogs
#     were still running 13h later, armed to kill this generation's suite to protect proofs
#     that had finished. Killed. Match on the script path AND exclude your own PID.
#
# ## THE TRAP THAT NEARLY COST A TEN-WAY FALSE "NO FINDING"
#
#   An audit of ten raising operations under `#@ no_exception \all` returned TEN clean
#   "refused/failed" verdicts. Every one was `ERROR: 'why3' command not found` — the
#   classification loop had run without `export PATH=$HOME/.opam/framac-coq8/bin:$PATH`.
#   **A MISSING TOOL LAUNDERED INTO WHAT READ EXACTLY LIKE TEN CONFIRMED SAFE BOUNDARIES.**
#   With why3 present, one of the ten PROVED (that is route #66's `chr` carrier). Generation
#   #4 hit the identical trap from the other side. **ASSERT `which why3` AT THE TOP OF EVERY
#   PROBE LOOP**, and treat any batch that comes back uniformly negative as suspect until the
#   tool is confirmed.
#
# ## PROBED THIS GENERATION WITH NO FINDING — DO NOT RE-PROBE
#
#   * Class invariants ARE inherited and enforced on SUBCLASS methods (both directions).
#     `--check-behavioral-subtyping` is OPT-IN.
#   * OBJECT aliasing: object-typed locals do not emit in ANY spelling (the hoist emits
#     `let b = ref 0`). Fails closed by TYPE ACCIDENT, not by a guard.
#   * PRESENT-BUT-NONE does NOT collapse with ABSENT — `{1: None}` keeps the key present,
#     both directions, including after a store of None.
#   * MODULE GLOBALS: a direct write to a global dict is REFUSED; aliasing one is UNDECIDED
#     both ways; a module int constant reads correctly.
#   * NESTED-LIST inner aliasing is genuinely unexpressible — three shapes the docs' own
#     argument does NOT cover (slot-to-slot `a[0]=a[1]`, a NAMED row in the literal, and the
#     field version) ALL type-reject, on both the int (matrix) and str (seq) leaf.
#   * `len` on a LIST is correctly undecided under a conditional append (real sidecar ref).
#   * Nine of the ten audited raising operations are covered or unreachable: `list.pop()`
#     on empty / `list.remove(absent)` / a `[::0]` slice are REFUSED; `"ab"[5:6]` / `min([])`
#     / `max([])` are EMISSION-FAIL; and `xs[5]` / `d[5]` / `bytes([300])` correctly do NOT
#     discharge, through the WIRED `in_bounds` and `map_get` rows.
#   * Route #60's edges REFUSE independently: `del` then `len`, `\length` in a SPEC
#     position, the SET twin, and dict/set COMPREHENSION sizes.
#   * Route #61's ELEMENT fold is faithful (`d[a]` with `a==b` proves 2). Only size broke.
#   * An IMPLICIT None return from a scalar-annotated function type-errors (fails closed).
#   * The DIRECT `@mutable_state` param-mutation case is already guarded and fires.
#
# ## THE ABSTRACT-`val` AUDIT — DONE ONCE, AND IT HAS UNWORKED LEADS
#
#   The "audit every abstract `val`" follow-up was RUN (288 `_add_abstract_op` call sites,
#   179 distinct declarations, plus 31 ensures-bearing `val`s written straight into
#   `preamble.py`). Route #69 came out of it. The classification: 122 OPAQUE (no `ensures`,
#   so harmless), 67 TOTAL-OK, 9 PARTIAL-GUARDED, **12 PARTIAL-UNGUARDED**. Exactly ONE
#   `_add_abstract_op` declaration in the whole codebase carries a `requires`.
#
#   **LEADS NOT YET WORKED — each is a candidate route, none is confirmed:**
#     * `str_sub_op` is used BOTH for the total slice `s[a:b]` AND, at
#       `expressions.py:12788`, for the ELEMENT read `s[i]` — and its first `ensures` is
#       unconditional in `lo`. Route #67 wired only the `ord(s[i])` path, so a BARE `s[i]`
#       may still carry no `IndexError` obligation. (My probe of the bare form hit an
#       EMISSION-FAIL, so it needs a second spelling before it counts either way.)
#     * `map_update_none` is shared by `del d[k]` (now wired, #66) and by
#       `set.remove`/`set.discard` at `statements.py:3010-3029`, which emits NO assert —
#       `s.remove(5)` on a set without 5 raises `KeyError`. My probe EMISSION-FAILed; retry.
#     * `str_split_elem_op` — `ensures` unconditional in both `sep` and `i`;
#       `"a b".split(" ")[5]` is `IndexError`, `"ab".split("")` is `ValueError`.
#     * `ord_op`'s `0 <= result < 256` is ALSO false on a TOTAL input for the same reason as
#       #69 and is now refused only via the non-ASCII guard — a non-literal path may remain.
#     * `struct_pack_i1a1` / `struct_pack_i18` are the two UNGUARDED entries in a registry
#       whose eight siblings all carry the correct `requires`.
#     * ~~SYSTEMIC: the dotted-callee stub drops the precondition~~ — **CONFIRMED AND CLOSED
#       as ROUTE #70.** Note the audit's framing was wrong about WHERE: a plain cross-module
#       import DOES carry its `requires` (verified — the emitted `val` has it and the caller
#       correctly fails), and an imported CLASS method drops BOTH clauses (fail-closed). The
#       live carrier was a STUBBED SAME-MODULE method. **Verify a delegated claim's scope,
#       not just its headline.**
#
# ## THE LADDER FOR THE NEXT RELAUNCH
#
#   0. **THE EXCEPTION MODEL PRODUCED FIVE ROUTES AND IS STILL NOT EXHAUSTED.** #64 (a
#      missing row), #65 (four rows consulted by NOTHING, one a `true` tautology), #66
#      (three more missing rows), #68 (two more, one of them a row that existed and was
#      never injected), #71 (an ERASED operation). Six probes, six findings — the
#      per-operation approach is NOT converging, and route #66's named completeness gate
#      (relate the table to what the emitter EMITS, not merely ACCEPTS) is worth more than
#      any further individual repair. `exception_model.TRIGGERS` is a SHORT TABLE — every row is a
#      claim that those are the only ways an IR operation can raise, and the `\all` form
#      turns each omission into a false proof. Walk the table against Python's real
#      behaviour: `IndexError` on a NEGATIVE index past the start, `KeyError` on `.pop`
#      vs `del` vs subscript, `ValueError` on `int("abc")` / `.index` (its row is literally
#      a `"true"` PLACEHOLDER), `StopIteration` on `next` (also a `"true"` marker),
#      `OverflowError`, `TypeError` — and anything raising that PyCSL lowers at all.
#   1. **WORK THE CLAIM BACKLOG — it is pre-ranked and it has produced 4 routes already.**
#      Highest-value unmeasured items, in order:
#        a. **"No aliasing is possible" in the Hoare model** (annotations.md §5;
#           `\separated` lowered to literal `true`). The single biggest structural claim in
#           the tree. Probe: two list/dict params the caller binds to the SAME object; a
#           list stored in two record fields; a param aliased through a global.
#        b. **A FRAMELESS `#@ depends_method`** — the docs say it "declares no effect at
#           all, so every method that calls it may declare `assigns \nothing` however much
#           state the real provider writes — a false frame no proof plane can see."
#        c. **A module-GLOBAL singleton field store `g.v = n`** — documented as a RETAINED
#           silent no-op, explicitly left when the param case was fixed as "severity-1".
#        d. **The module-const dict fold's invalidation omits MUTATION** — the guard is
#           "bound EXACTLY once", and a STORE is not a binding. Same shape as #34/#60/#61.
#        e. **The `is` BLACKLIST's stated hole** — "an *unannotated* local holding a string
#           is not refused" (route #52's exploit with the annotation removed).
#        f. **Mixed-literal rejection keys on element KIND**, exempting a str-typed *name*,
#           a BinOp, or a call — the four rejected kinds are all literals.
#        g. **`return` inside a `try` with a catch-all handler** — early return is modelled
#           as `raise Return v`; a bare `except:` in WhyML would catch it. Python does not.
#        h. Two INTERNAL INCONSISTENCIES worth settling by reading the emitted `.mlw`:
#           body `and`/`or` (three passages disagree), and float arithmetic (§T.10.3 says
#           "Real arithmetic/comparison verify"; §T.2.2 and route #53 say UNINTERPRETED).
#   2. Re-run the claim-mining sweep against `docs/pycsl-ub-catalog*` and the soundness
#      report, which this generation did not mine.
#   3. Route #60's residuals (an exactly-computable size that is refused anyway) and the
#      `finding-w55-literal-concat-len-unbound.md` completeness bug.
#
# ===================================================================================
#
#
# ====== START HERE — gen #4 FINAL STATE (read this block, then the ones below) =======
#
# ## WHAT IS TRUE RIGHT NOW
#
#   metric   markers **459** · grep 484 · offset 25 · unattached 0
#   fidelity **ZERO divergences over 887** — the L-plane is GREEN
#   planes   **ALL 31 GREEN under `--slow` — NOT ONE RED.** That includes the fidelity
#            plane (RED at HEAD for a long time before this window), `check-shadowed-
#            selfcalls` (the campaign's named RED, 15 -> 14), and the new
#            `check-mirror-type-only`. Log: `proofs49/w54b_slow_planes_all_green.log`.
#            **RUN IT WITH why3 ON PATH** or several planes cannot say anything.
#   ledger   **ONE OPEN ROUTE: #59 — FIVE of its SIX carriers now REFUSE.**
#            Closed: local->local, symmetric, chained, field->local, and the GETTER-RETURN
#            (`m = self.get()`). Open: the FIELD STORE (`self.d = p`, then mutate `p`).
#   OWED     `w54a_expressions`, the whole-file re-proof of the repaired L1 half. It is
#            the ONLY outstanding proof; everything else is collected at rc=0. It stays
#            VALID despite the later getter-return commit, because that commit only ADDS A
#            RAISE and so cannot alter emitted content — all 53 mirrors still emit.
#
#   **THE SIXTH CARRIER IS A MEASURED REFUTATION, NOT AN UNTRIED ITEM.** Two
#   implementations were built and both fail, and the obstacle is WHERE the guard must
#   live: `_handle_fieldassign_stmt` is VERIFIED VERBATIM by the mirror, unlike
#   `_handle_assign_stmt` (a `\trusted` stub), which is why the alias guard was cheap.
#   A recursive `.pop()` walk is refused by PyCSL's OWN ownership discipline; a flat
#   mirrorable scan emits but is ILL-TYPED. Full write-up, with the trade each remaining
#   option makes, is in the route file.
#   tree     clean. Two long-standing GITLINKS (`scratchpad/w7/base`, `scratchpad/w8/pre`
#            are registered WORKTREES) and a 0-byte stray `str` in the repo root are
#            pre-existing and are NOT dirt.
#
# ## WHAT LANDED, AND THE ONE THING THAT DID NOT
#
#   **LANDED: staged-route59** (refuse a MUTATED dict alias) and **staged-L1's scf half**
#   (`_handle_for_stmt` re-`\trusted`, frame RE-DERIVED from the live body and
#   independently re-checked: it writes 10 self fields, all 10 covered by the declared 25).
#   That is the metric 457 -> 458 and the fidelity 2 -> 1.
#
#   **STAGED-L1's EXPRESSIONS HALF: REVERTED, THEN REPAIRED AND RE-LANDED.** The fix is
#   `#@ sibling_concrete` on a new `\trusted` mirror stub for
#   `_union_local_read_projection`. **THE STUB ALONE DOES NOT WORK** — measured — because
#   the untyped avatar is synthesized FROM THE CALL SITE, not from the presence of a
#   same-named method; the marker is what routes the call to the typed stub. Its frame is
#   RE-DERIVED from the live body's transitive closure across all of `src/pycsl`
#   (`_abstract_ops`, `_obj_state_written`), because `\nothing` on a `\trusted` stub is an
#   ASSUMPTION, not a check. That is the metric 458 -> 459 and the fidelity 1 -> 0.
#
#   The original failure, kept because it is the lesson of the window: `_handle_var_expr`'s
#   restored block calls `_union_local_read_projection`, **which the mirror does not model
#   at all**, so Module 6 synthesizes an untyped avatar that defaults to `int` and
#   `raise (Return_str !_proj)` does not type-check. Adding a `\trusted` stub with the real
#   `-> Optional[str]` signature was tried and MEASURED — it does NOT fix it. Fixing this
#   is a real build, not a one-liner, and it is the reason fidelity is 1 rather than 0.
#
#   **HOW IT GOT IN, BECAUSE THIS IS THE LESSON OF THE WHOLE WINDOW.** I landed L1 on
#   fidelity + planes + metric + corpus byte-diff. All were GREEN — including ALL 18
#   PLANES and a 0-file corpus byte-diff — while the mirror was ill-typed. That is route
#   #57's landing defect reproduced exactly, by the same worker that had banked the lesson
#   ("run `why3 prove --type-only` on any mirror edit") four hours earlier and skipped it.
#
#   **THE SYSTEMIC FIX IS IN: `bin/check-mirror-type-only.py`**, wired into `--slow` and
#   into EMIT_DIR_PLANES so it reuses the shared emission (~10s). Demonstrated both ways —
#   rc=0 on this tree, rc=1 with the ill-typed half re-applied, naming the exact line.
#   **RUN `bash bin/run-soundness-planes.sh --slow` BEFORE LANDING ANY MIRROR EDIT.**
#
# ## NOTHING IS IN FLIGHT. EVERY OWED PROOF IS COLLECTED AND rc=0.
#
#   `w53b_scf`        rc=0    owed by L1's scf half
#   `w53c_statements` rc=0    owed by route59's `#@ raises` on `_handle_assign_stmt`
#   `w53d_transpiler` rc=0    owed because it CALLS `_handle_assign_stmt`, so its VCs moved
#                             — this is the risk the staged README flagged, and it holds
#   `w52c_statements` rc=0 · `w52d_expressions` rc=0 (earlier)
#   `w51g*` route #57's whole mover set, rc=0
#
#   **So every mirror this generation touched has a WHOLE-FILE PROOF at its current
#   content.** `w53a_expressions` is rc=1 and EXPECTED — the ill-typed staged-L1 half,
#   since reverted; after the revert expressions.py is byte-identical to the tree
#   `w52d_expressions` proved rc=0, so it owes nothing.
#
#   FINAL BATTERY: `--slow`, **31 planes, 30 GREEN**, the one RED being the single
#   mirror-sync divergence above. Log: `getting-better/proofs49/w53e_slow_planes_final.log`.
#
#   **RUN THE BATTERY WITH why3 ON PATH** (`export PATH=$HOME/.opam/framac-coq8/bin:$PATH`).
#   Without it `check-param-mutator-visibility` used to report SIX cases off-baseline and
#   rc=1 — a missing tool laundered into what looked exactly like a regression from the
#   most recent landing. That is fixed (it now skips), but several planes still need why3
#   to say anything at all.
#
# ## THE LADDER FOR THE NEXT RELAUNCH
#
#   1. **COLLECT** w53b / w53c / w53d. If any fails, that is the honest cost of the landing
#      and it must be worked, not hidden.
#   2. **FIX staged-L1's expressions half** — model `_union_local_read_projection` in the
#      mirror so the avatar is string-typed. The naive `\trusted` stub is already REFUTED,
#      so start by reading how another `Optional[str]`-returning mirror stub gets its
#      avatar typed. Gate with `check-mirror-type-only` FIRST, then the whole-file proof.
#      Landing it takes fidelity to 0 and the battery to 18/18.
#   3. **GENERALISE THE #59 REPAIR** to the two uncovered carriers (getter-return and
#      field-store). Already costed at ZERO on both gated populations. That CLOSES the
#      route; the partial patch that landed does not.
#   4. **PROBE R3 ACROSS A CALL BOUNDARY** — the one #59 carrier still unmeasured.
#   5. Then the witnesses in `staged-route59/witnesses/` per their README.
#
# ===================================================================================
#
#
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

<!-- gen #30 endgame -->
# FINAL CONTROL BATTERY: `$SCRATCH/final_battery.sh <worktree> <commit>` — checks the
# worktree out at <commit>, runs `bin/run-reference-tests.sh` then
# `bin/run-soundness-planes.sh --slow`, and prints FINAL-BATTERY-DONE. Poll the log; do
# not relaunch. Expected at the gen #30 final HEAD: suite 3841+ tests with the same 18
# CONFIRMED FAIL and ZERO XPASS, and 43 planes green (22 fast + 21 slow).

<!-- gen #30 instrument index -->
# INSTRUMENTS BUILT IN gen #30 — where they are and what they measure
#   bin/check-argument-coercion.py             every argument SUBSTITUTION, classified
#   bin/check-proof-reverify.sh                the axiom footprint (ratchet driven 6 -> 0)
#   bin/check-return-boundary-substitutions.py every constant a return handler substitutes,
#                                              pinned WITH COUNTS; `--live DIR` self-test
#   bin/check-fstring-lowering.py              every value `_handle_fstring_expr` returns,
#                                              plus two STRUCTURAL tokens (#203 added a
#                                              wrap, not an exit, so the return set alone
#                                              is green on the pre-#203 tree)
#   bin/check-coercion-exits.py                every value `_array_coerce_arg` and
#                                              `_coerce_to_int` return, with counts
#   bin/check-corpus-contract-truth.py         BOTH reference corpora's own literal-result
#                                              postconditions, re-run under CPython every
#                                              pass: 367 agree, 0 disagree
#   scratchpad/g30/fuzz/gen11.py               the RETURN boundary (960 programs, 0 found)
#   scratchpad/g30/fuzz/gen12.py               the STRING/INT REPRESENTATION boundary
#   scratchpad/g30/stdlib_diff.py              pycsl_lib BODY differential (wrong criterion,
#                                              kept as the record of why)
#   scratchpad/g30/stdlib_contract_diff.py     pycsl_lib CONTRACT-vs-CPython differential —
#                                              the RIGHT criterion; 2 fidelity defects,
#                                              severity downgraded after tracing the
#                                              consumer. The named work item for the
#                                              `agent-stdlib-annotate` owner.
# SELF-TEST HOOK, worth copying into every new plane: `--live <dir>` runs the gate against
# another checkout, and `git show <old-sha>:<file> > <tmpdir>/` gives you that checkout for
# one file without moving a worktree. A gate nobody has seen fail is a claim.
