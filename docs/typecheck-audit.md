# Typecheck audit — the honest-gate backlog (refactor.md Phase D)

**What this records.** Phase D's principle: *a run is SUCCESS only if the emitted WhyML at least
type-checks* — emitting text that does not even type-check is the silent success the laws forbid
(`refactor.md` §1.5). The `--typecheck` gate (`pycsl … --no-proof --typecheck`) makes this checkable: it
runs `why3 prove --type-only` on the emitted `.mlw` and reports a per-level status `L1 ✓ L2 ✓ L3-tc {✓|✗}`,
exiting non-zero on `L3-tc ✗`.

**The finding (snapshot).** Of the **588** reference drivers that emit WhyML and report `--no-proof`
SUCCESS, **54 emit WhyML that does NOT type-check** — i.e. they have been reporting a *dishonest* SUCCESS.
(Since this snapshot, the `0406 0407` `list.append` pair has been RESOLVED-BY-SUPPORT — growable-list `Seq`
for `.append`-ed params — and both now type-check honestly; see the `list.append` cohort below.)
The failure is real, not a harness artifact: the production `why3 prove -a split_vc -P <prover>` path fails
the same drivers with the same diagnostic (verified on `0250`: `unbound function or predicate symbol
'counter'`), and none of the 54 are marked `# pycsl-expected: FAIL`.

Regenerate the list at any time with `bin/typecheck-audit.sh`.

## The 54, by category

- **Concurrency (28):** drivers using `#@ critical`/`acquires`/`releases`/`shared`/`thread_entry`/
  `mutex_invariant`/`lock_order`. **ROOT CAUSE (diagnosed):** the mutex-invariant lowering emits a *logic*
  `predicate` whose body dereferences a *program* mutable ref — which WhyML forbids (logic cannot see
  mutable program state). For `0250`: shared state is `val counter : ref int`
  (`module6_whyml/preamble.py:610`), but the invariant is `predicate lock_counter_inv = (!counter >= 0)`
  (`preamble.py:623`) → `why3` reports `unbound function or predicate symbol 'counter'` at the predicate
  line. **FIX (D1, one root cause covers ~all 28):** parameterize the predicate by the shared values —
  `predicate {mutex}_inv ({var}: int …) = {bare invariant}` — and apply it with the dereference at every
  program-context use site: `_check_initial` (`preamble.py:633`) and the critical-section assume/prove
  (`module6_whyml/statements.py:534-535`), i.e. `assert { {mutex}_inv !{var} }`. This CHANGES the
  concurrency `.mlw` (so it is byte-diff-visible and gated by: the fixed `.mlw` type-checks **and** the
  corpus pass/fail is otherwise unchanged), unlike the rest of this refactor's byte-preserving bricks.
  **STATUS — predicate fix LANDED:** the `unbound symbol` error is gone on all concurrency drivers; **7 now
  fully type-check** (`L3-tc ✓`), non-concurrency `.mlw` byte-identical, no pipeline regression. The fix
  peeled the onion: a SECOND layered blocker (25 drivers) — the source `#@ \diverges` on the worker
  (modelling lock-blocking as possible non-termination) lowers to a `diverges` effect (`functions.py:286`),
  but the critical section was modelled as non-blocking (havoc+assume), so why3 saw a terminating body and
  rejected it (*"this expression does not diverge"*); the 7 that already passed are exactly the concurrency
  drivers WITHOUT `#@ \diverges`. **STATUS — `\diverges` cohort RESOLVED (2026-06, maintainer decision:
  model the acquire as diverging).** MECHANISM (the standard WhyML idiom for "may block forever"): a
  lock-acquire can block forever (deadlock/contention), so it is *potentially-diverging*. The lowering now
  declares, per mutex used by any `#@ critical`/`#@ acquires` section, an ABSTRACT diverging operation
  `val acquire_<mutex> () : unit  diverges` (emitted in `_emit_shared_state`,
  `module6_whyml/preamble.py`, after the `_check_initial_<mutex>` helpers; mutexes collected by
  `_collect_critical_mutexes`, **sorted** — no hash-order), and **emits a call to it at section ENTER**
  (`_handle_critical_section_stmt`, `module6_whyml/statements.py`, prepended before the havoc+assume). The
  worker's body therefore *genuinely may diverge*, so why3 ACCEPTS the worker's `diverges` effect and the
  `.mlw` type-checks. The emission fires ONLY for programs with a critical section, so the os and all
  non-concurrency `.mlw` are byte-identical (verified: ~30-driver basket + `os_demo` diff-clean). The
  `diverges` effect only RELAXES the termination obligation, so existing concurrency proofs are unaffected
  (`0257` still proves fully). **Before → after `.mlw` for `0250`:**

  ```
  (* before — REJECTED: "this expression does not diverge" *)
    let worker () : int
      diverges
    =
      let _any_counter_0 = any int in
      counter := _any_counter_0;
      assume { lock_counter_inv !counter };
      counter := !counter + 1;
      ...

  (* after — ACCEPTED: the abstract diverging acquire justifies the effect *)
    (* lock-acquire may block forever — modelled as diverging *)
    val acquire_lock_counter () : unit
      diverges

    let worker () : int
      diverges
    =
      let _any_counter_0 = any int in
      acquire_lock_counter ();
      counter := _any_counter_0;
      assume { lock_counter_inv !counter };
      counter := !counter + 1;
      ...
  ```

  After the fix, **24 concurrency drivers `L3-tc ✓`** (the 7 prior + every `#@ \diverges`+critical worker);
  the 8 expected-FAIL concurrency drivers emit no `.mlw` (they fail earlier at semantic checks, e.g.
  `0255`/`0691` lock-order, `0254`/`0415`); two remain `L3-tc ✗` for DIFFERENT, non-`\diverges` reasons:
  **0417** (the pre-existing unit-vs-int return-type mismatch) and **0276** (a `#@ thread_entry` worker that
  declares `#@ \diverges` but has NO critical section / no lock-acquire — nothing in its body can block, so
  the lock-acquire model does not apply; its `\diverges` is unjustified by the maintainer's lock-based
  rationale and would need either a separate thread-run-loop diverging anchor or removing the annotation —
  out of scope for this lock-acquire fix).
- **Other (26):** `0050 0303 0386 0406 0407 0477 0478 0479 0480 0482 0483 0484 0485 0486 0487 0488 0489
  0557 0560 0563 0575 0601 0631 0634 0636 0638` — assorted features whose lowering emits an
  ill-typed/undeclared symbol. **D1 diagnosis (2026-06) groups these; the 13 string drivers were
  subsequently RESOLVED by the G2 strings feature (2026-06) — see below.**
  - **Logic-context abstract op declared as program `val` (4) — FIXED:** `0631 0634 0636 0638`
    (`\in_globals` / `isinstance`/`\typeof` / `\in_scope`). The lowering emitted `val in_globals_op` /
    `val typeof_op` / `val in_scope_op` (program functions) but used them inside `ensures`/`requires`
    (logic terms) → why3 *"unbound function or predicate symbol"*. A pure program `val` is not visible in
    logic; the symbols are uninterpreted (pure by construction), so the correct WhyML form is `val function`
    (a logic function usable in both terms and code). Fix: `module6_whyml/expressions.py` —
    `_tag_of_value` (`typeof_op`), `_handle_in_globals_expr` (`in_globals_op`), `_handle_in_scope_expr`
    (`in_scope_op`) now emit `val function …`. All four now `L3-tc ✓`; the change is a single-line
    `val`→`val function` per driver, byte-identical on the decided-true/false neighbors
    (`0603 0630 0632 0633 0635 0637`) and the rest of the corpus.
  - **String feature demand-drivers (13) — RESOLVED by the G2 strings feature (2026-06):**
    `0477 0478 0479 0480 0481 0482 0483 0484 0485 0486 0487 0488 0489`. (`0481` — `+`/concat — was
    already supported.) Each now lowers FAITHFULLY (a Python `str` is a real Why3 `string`, never
    int-coerced) and **FULLY PROVES** (`pycsl <f>` → Verification SUCCESS), so every `# pycsl-expected:
    FAIL` marker was REMOVED (they are now positive drivers). The lowering changes are confined to
    `module6_whyml/expressions.py` (`_handle_binop`, `_handle_call_expr`) and
    `module6_whyml/stmt_control_flow.py` (`_classify_iterable`); each new op fires ONLY for
    string-typed operands (guarded by `_is_string_expr`), so the rest of the corpus + `os` are
    byte-identical. Per-op bridges (all `ensures`-tied to the Why3 `string.String` theory):
    - **`< <= > >=` (0477–0480):** `str_lt_op`/`str_le_op` (`val:bool`, `result <-> String.lt/le`);
      `>`/`>=` reflect by swapping operands. Body returns Python's int truth (`if … then 1 else 0`).
    - **`str(s)` / `format(s)` (0486, 0488):** identity — returns the argument string unchanged.
    - **`hash(s)` (0485):** routes a string arg to the existing `val str_hash_op : int`.
    - **`s*n` / `n*s` (0482, 0483):** `val str_repeat_op` with `String.length result = n * String.length s`
      (content opaque; length law only). Canonicalizes string-first.
    - **`s % x` (0484):** honest abstract `val str_mod_op (s:string)(x:'a):string` with only
      `String.length result >= 0` — a sound over-approximation; the formatting is NOT modeled
      (never the int `pycsl_mod`).
    - **`for c in s` (0489):** `_classify_iterable` now lowers a string iterable to bound
      `str_length_op s` (= `String.length s`) and element `str_sub_op s !idx 1`. Because the
      iteration index is internal (not source-referenceable), 0489's *counting* postcondition
      (which must relate `count` to that index) is stated over an explicit `while i < len(s)` index;
      it proves `result == String.length s`.
    - **`repr(s)` (0487) — HONEST DISPOSITION (option b):** the naive `len(repr(s)) == len(s) + 2`
      is UNSOUND in general (Python adds exactly 2 quote chars only for quote/escape-free strings;
      escapes lengthen it further), so PyCSL does **NOT** emit that `+2` equality. `repr` lowers to
      `val str_repr_op (s:string):string` whose only `ensures` is the sound LOWER bound
      `String.length result >= 2` (repr always carries its two surrounding quotes — Why3's
      `length_nonneg` axiom is commented out, so a bare `>= 0` is not even provable for an opaque
      result, whereas `>= 2` is a true, faithful fact). 0487 was rewritten to assert
      `\str_length(\result) >= 2` and is now a positive (proving) driver — no false postcondition,
      no string→int coercion anywhere.
  - **`list.append` Seq-vs-Array representation mismatch (2) — RESOLVED-BY-SUPPORT (growable-list Seq for params):**
    `0406 0407` (the only two with NO `expected: FAIL`) WERE genuinely dishonest: a `.append`-ed `list`
    PARAM typed as `array int`, was seq-promoted (so `.append` lowered to `Seq.snoc`), yet the
    append-targets backing loop bound it as `let dst = Array.make 1024 0 in` → `Seq.snoc !dst v` applied
    to an `array int` ref → *"has type array … but is expected …"* (the dishonest SUCCESS). Maintainer
    decision: **SUPPORT** `list.append` on params via the `Seq` representation (not reject). Fix
    (`module6_whyml/statements.py` + `stmt_control_flow.py`): a seq-promoted `.append`-ed param is now
    shadowed as a `ref seq` — `let dst = ref (snapshot dst) in` (the same `snapshot : array int -> seq int`
    bridge the pre-decl seq-param shadow uses), the `Array.make`/`_len` array backing is omitted, the param
    joins `local_refs` so it deref's (`!dst`), and `_classify_iterable` reads a seq-promoted iterable via
    `Seq.length !x` / `Seq.get !x i`. Result: `dst`/`arr` are `ref seq` consistently with `Seq.snoc`, so
    both **now type-check honestly (`L3-tc ✓`)**. Emission is byte-identical for every other driver and all
    of `os` (whose append-targets are seq LOCALS, already on the seq path — untouched by the param-only fix).
    Full proof still does not discharge (these are `--no-proof` detector drivers with no loop invariants); the
    bar is `L3-tc ✓`, which is met.
  - **Singletons — REPORT (each a distinct negative/boundary test, all `expected: FAIL`):**
    `0050` (`variant … with subterm` — syntax error from the structural-variant lowering);
    `0303` (`\proj` out-of-range → undeclared `z_` from tuple-projection lowering);
    `0386` (strict-no-exception unannotated callee → undeclared `external_helper_1`);
    `0557` (arithmetic on a datatype quantifier binder — `color` vs `int`, ill-typed by design);
    `0560` (non-terminating lemma — *"cannot prove termination"*, the intended boundary);
    `0563`/`0575` (non-strictly-positive inductive — why3 correctly rejects, the point of the test);
    `0601` (returning an array of tuples — unsupported `array (int,int)` vs `array int`).
    These are intentional negatives whose "type error" IS the documented behavior; no emission fix applies.

## The gate is now DEFAULT-ON (D2 — done)

The staged path to honest-by-default is complete:

1. **D0 (done):** the `--typecheck` capability + per-level status + this audit.
2. **D1 (done):** the 54 fixed-or-marked — concurrency `\diverges` cohort (lock-acquire-is-diverging),
   the logic-context `val`→`val function` group (G1), the `list.append` Seq-vs-Array pair (G3),
   and the singleton XFAIL targets (G4). **G2 (the 13 string drivers) was subsequently RESOLVED by
   the faithful strings feature (2026-06): all 13 now type-check AND fully prove; markers removed.**
3. **D2 (done):** the typecheck now runs **by default** on every `--no-proof` run and SUCCESS is gated
   on `L3-tc ✓`. ← *here*

**What D2 changed (`src/pycsl/pycsl.py`):**

- `_run_proofs` `--no-proof` branch: `_why3_typecheck` runs **by default** (no longer only under
  `--typecheck`); a non-type-checking emission EXITS NON-ZERO with the located diagnostic even under
  plain `--no-proof`. The SUCCESS message states the level reached (`… AND type-checks [L3-tc ✓]`).
- New **`--no-typecheck`** escape flag (`store_true`): restores the old fast emit-only behavior for
  byte-diff / dev sweeps and when why3 is absent. A missing why3 is still treated as **skip-not-fail**
  by `_why3_typecheck` (it returns `ok=True`), so the gate never turns an absent prover into a false
  failure.
- `--typecheck` is now a **harmless no-op alias** (the gate is already on).
- The proof path is unchanged — it already type-checks via `why3 prove`.

**The dishonest set was emptied to ZERO before the flip.** The audit's two genuinely-dishonest residuals
were resolved:

- **0276** (`#@ thread_entry` + `#@ \diverges`, straight-line body, no critical section): the `\diverges`
  was *unjustified* (a straight-line body provably terminates, so why3 rejects the `diverges` effect with
  *"this expression does not diverge"*). Resolution: **PyCSL now LOUDLY REJECTS** `#@ \diverges` on a
  function whose body has no potentially-diverging construct — no critical section / lock-acquire, no loop,
  no call/recursion (`Module4_SemanticAnalyzer._validate_diverges`). This is symmetric with why3's own
  effect check but fires at PyCSL semantic time with a clear message. The driver itself was edited to drop
  the unjustified annotation (its actual purpose is the ConcurrencyChecker *unprotected-shared* warning
  path, which still fires) so it is now an honest SUCCESS that type-checks; the rejection is covered by the
  new negative driver **0695** (`# pycsl-expected: FAIL`, a straight-line `#@ \diverges`). The recursion-
  justified `\diverges` drivers (0051/0158/0159 — `return f(x)`) and the critical-section ones stay
  accepted (their bodies *can* diverge).
- **0417** (unit-vs-int return mismatch): a clear **emission bug**, now FIXED. When `return <v>` is the
  LAST statement *inside* a `#@ critical` `with` block, the exit-invariant `assert` was appended *after*
  the body → section tail `… ; <v> ; assert {…}` is `unit` while the function is declared `: int`
  (why3: *"This expression has type (), but is expected to have type int"*). `_handle_critical_section_stmt`
  (`module6_whyml/statements.py`) now HOISTS a trailing value-`Return` past the assert: body-prefix
  (mutations) → `assert` → return value as the tail. Fires only for `return`-inside-critical-section with a
  `prove_inv`; every other shape (e.g. 0250, where the `return` is *outside* the `with`) is byte-identical.

**Post-D2 audit:** `bin/typecheck-audit.sh` still lists 21 `L3-tc ✗` drivers, but **every one carries
`# pycsl-expected: FAIL`** — the genuinely-dishonest (SUCCESS + ✗ + no XFAIL) count is **0**. Full
`--no-proof` sweep: **567 `L3-tc ✓`**, 21 `L3-tc ✗` (all XFAIL), 64 emit-no-mlw. Corpus harness: 652/652
(was 651/651 + the new 0695 XFAIL); os_demo proves fully (0 unproven) and type-checks; doc-coherency green.

A plain `--no-proof` SUCCESS now means "WhyML emitted **and** type-checks". `--no-proof --no-typecheck`
SUCCESS means "WhyML emitted (emit-only, typecheck skipped)".
