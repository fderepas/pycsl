# HANDOFF — read this FIRST on relaunch (rewritten 2026-08-30, RELAUNCH #15 worker)

## State, verified from the surface at end of session

- **Count: MARKERS 502 · grep-substring 527 · offset 25 · unattached 0.** Quote BOTH.
  From **`bin/count-trusted-directives.py`**, never a hand-rolled grep — 25 of the grep hits
  are one boilerplate module-docstring line repeated across 25 mirror files, so every
  historical absolute figure (the famous "687") is overstated by that 25.
  **Window #2 delta so far: markers 530 -> 502, grep 555 -> 527.**
  **This session (#15): 503 -> 502, ONE conversion — plus the big moves of the session,
  which were on the OTHER metrics: the shadowed-selfcall ratchet 27 -> 15 (sites 177 -> 154)
  and the mirror-wide input-blind `isinstance_op 0 0` count 26 -> 10.**
- **`bin/check-shadowed-selfcalls.py`: 15 CONVERTED methods / 154 bypassing call sites,
  ratchet 15** (was 27 / 177 at session start). Needs
  `TMPDIR=/home/fabrice/git/pycsl/scratchpad`; takes ~2 min; give Bash an explicit timeout.
  **The ratchet constant in the file was lowered 27 -> 26 -> 23 -> 15, each with its
  provenance comment.** 137 of the remaining 154 sites are the TWO recorded L2 dispatchers.
- Ledger **3**, untouched. Emitted axioms: **0**. Literal-guard grep: **0**.
- **PROOF COSTS. THREE NEW ONES THIS SESSION** (marked *new*):
  `frontend/pure_ast` **2798/2798**, ~55 min.
  `frontend/Module5_IREmitter` **1133/1133**, ~60 min.
  `module6_whyml/statements.py` **912/912**, ~30 min.
  *new* `module6_whyml/stmt_control_flow.py` **1846/1846**, ~45 min.
  *new* `module6_whyml/expressions.py` **1050/1050**, ~15 min.
  *new* `src/self-annotate/src/pycsl.py` **731/731**, ~20 min.
  A single corpus driver (`0447`) is **11 seconds**. A mirror EMISSION is ~2 s.
  **PROOF COST IS NOT PROPORTIONAL TO SOURCE SIZE** — `expressions.py` is the biggest source
  file in the mirror and proves in a quarter of `pure_ast`'s time.
- Fidelity at the standing baseline **2 DIVERGED** (`_handle_var_expr`, `_handle_for_stmt`).
  Field parity 335 / 7 known drift / 0 NEW. check-untrusted-emitted **808 / 791 / 0 / 0**.
  emitted-vacuity `--emit`: no NEW erasure, **8 known**, 0 input-blind.
  Corpus byte-diff **0 over 813/813** against HEAD (it was 1 of 813 BY DESIGN during
  increment 5 — driver 0603, which was re-proved; re-baseline against the CURRENT HEAD). `bin/self-annotate-mirror-check.sh`
  output byte-identical to the session-start HEAD baseline (3 mirrors drifted, exit 1 — that
  IS the baseline).
- Tree clean apart from the pre-existing user/build dirt (`session.txt`, untracked
  `scratchpad/`, `prompt`, `prompt.txt`). Leave it alone.
  `getting-better/.driver-deadline` intact (Sep 1 08:24 UTC). Commits unpushed by design.

## WHAT THIS SESSION LANDED (six gated increments)

1. **`Module5_IREmitter._py_stmt_raise` CONVERTED (503 -> 502)** — the CERTIFIED-BOUNDARY
   **[OPTIONAL NODE FIELD NOT UNWRAPPED] is BROKEN**, and all five recorded gaps fell.
   The previous session's refutation named ONE capability and was right that it subsumed
   three of the five; what it could not know is that the capability has a PLACE.
   **Unwrap at the BINDING, not at the read**: `exc = stmt.exc` in the LIVE body
   (runtime-identical) becomes an emit_ir local whose assignment is
   `(match stmt.py_raise_exc with Some _v -> _v | None -> IrOther "" end)`. Unwrapping the
   field READ instead would have broken the `x is None` presence guard, which reads the same
   field RAW. Plus three demand-gated extras: the TYPED `<emit_ir local>.args` attribute form
   in `_emit_ir_args_recv_ir` (so `exc.args[0]` -> `arg0_of` and `if exc.args:` ->
   `(nargs_of !exc) <> 0`, the MODELLED arity, instead of `Array.length` of the OPAQUE
   `val args_of` whose length is unconstrained); the `SRaise iropt_str iropt_ir` stmt_ir arm
   (FLAT, so `size_stmt`'s catch-all covers it); and the `optstr`/`optir` child kinds in
   `_lower_stmt_ir_node`. Proven inert on real inputs: 31 corpus files contain `raise`, and
   the corpus byte-diff is 0 of 813 WITH the live restructure in place.
2. **`_py_op_to_str` concrete at all six sites — ratchet 27 -> 26.** The marker alone took
   it 6 -> 1; the survivor lives in a SYNTHESIZED body (`functions.py::
   _emit_py_expr_compare_bespoke`) that had the avatar hard-coded in a string template.
   New `functions.py::_pyx_sibling_call` renders such a call the way the lowered route does.
3. **`stmt_ir` added to the concrete-route return-type allowlist — ratchet 26 -> 23.**
   `_process_for`/`_process_if`/`_process_while` are converted, proven `-> stmt_ir` node
   builders whose only call site is `ir_stmts.append(self._process_<k>(stmt))`; without the
   allowlist entry **the sub-body list of every emitted For/If/While was an ARBITRARY node.**
4. **The VOID sibling (`unit`), admitted OPT-IN ONLY — ratchet 23 -> 15, sites 168 -> 154.**
   A void mutator's avatar has no `writes`, so it is lesson (bq)'s NO-OP and its caller sees
   nothing it does. EIGHT methods went concrete. **Admitting `unit` on the shared
   `_record_array_fields` proxy BREAKS `pure_ast`** (`_Parser` passes that proxy, and its
   `-> NoReturn` `error` is `\trusted`, so the arm fires on a callee with no emitted
   definition to order: `unbound function or predicate symbol '_parser__error'`). Requiring
   the explicit `#@ sibling_concrete` marker is what let all eight land green.

5. **The RECEIVER-CARRYING `isinstance` — the SECOND deliberately NON-INERT change of this
   campaign.** `expressions._handle_isinstance`'s fallback, when `_tag_of_type(<class>)`
   yields no tag, was `(isinstance_op 0 0)` — BOTH arguments erased, so the test was
   independent of the value AND of the class. It now emits a per-(class, receiver-type)
   uninterpreted predicate APPLIED TO THE RECEIVER,
   `val py_isinstance_<Cls>_<ty>_op (x: <ty>) : bool`. **Monomorphic by construction** — the
   receiver's Why3 type is part of the op NAME, which is the design question the census had
   flagged. Two receiver shapes admitted (a plain `Var` whose symtype is a known RECORD or a
   scalar `_symtype_to_whyml` resolves; and a RECORD-FIELD read), everything else DECLINES to
   the historical constant. `_csl_proj`'s `if not isinstance(node.index, CSLNumber): raise
   PyCSLSemanticError` now READS ITS INPUT, and `val isinstance_op` is gone from
   `Module5_IREmitter` entirely. Blast radius measured first and it is 2 mirrors + **corpus
   0603**, the reference driver for this very feature, re-proved in 1 s. Mirror-wide
   input-blind `isinstance_op 0 0`: **26 -> 24**.
6. **The isinstance receiver oracle WIDENED — input-blind `isinstance_op 0 0` 24 -> 10, and
   this one is CORPUS-INERT (0 of 813).** The residue was diagnosed by INSTRUMENTING THE
   DECLINE (lesson (bp)) — a one-line stderr print at the fallback, run over all 52 mirrors,
   printing the enclosing function, the class name and the receiver SHAPE — and it named two
   blockers the census had not guessed. **(a) `cls=None` on ELEVEN of the 24**: the class is
   written DOTTED (`isinstance(node, ast.Expr)`), so `args_ir[1]["name"]` is None and the
   class could not even be NAMED; take the ATTRIBUTE. **(b) `symtype=Any` on most of the
   rest**: an untyped receiver lowers to the INT default — but "untyped in the symbol table"
   is NOT "int in the emission", because a dozen inference passes retype a local AFTER the
   symbol table is built. Admit the int default only when the name is in NONE of them
   (nineteen sets, six maps). That is fail-closed by EXCLUSION rather than inclusion, which
   is weaker, and acceptable HERE only because the failure mode is LOUD: a wrong type is an
   ill-typed application L3-tc rejects in 35 s on the sweep.

## TWO CERTIFIED-BOUNDARIES RECORDED THIS SESSION (measured, spikes reverted)

- **`module6_whyml/struct_format.arity` — [UNEMITTABLE @property].** The previously recorded
  capability (a string-element list field + the preamble noticing an array-typed record
  field) is REAL — spiked: `slots: List[str]` gives `mutable slots: array int` (elements INT,
  not string) and the file's preamble has no `use array.Array`, so even the one-line body is
  an L3-tc `unbound type symbol 'array'` — but it is NOT SUFFICIENT. `arity` is an
  `@property`, and `Module5_IREmitter._should_skip_method` drops every `@property` outright.
  The evidence needs no argument: the trusted sibling `slot_id` emits as
  `val structformat__slot_id`, while `structformat__arity` appears in the emitted theory
  NEITHER as a `let` NOR as a `val`. Converting it is lesson (bd)'s COUNT THEATRE, and
  `check-untrusted-emitted.py` would correctly report it "unexpectedly absent".
  **REOPENING CAPABILITY, RENAMED: `@property` support in Module 5** — emit the getter as a
  nullary method and route `self.<prop>` reads to it. Cost/scale, but it is a LANGUAGE-SURFACE
  change: `docs/pycsl-translational-reference.md` documents "`@property`, `@staticmethod` |
  Not supported", and corpus driver **0962_crosscheck_selfstate_registry_skipped.py** exists
  to PIN the skip. Owes the full `pycsl-audit-pycsl-language` gate, five doc surfaces, and a
  re-spec of 0962. **Yield: FOUR markers** (`struct_format.arity`, `audit_proof_reverify.ok`,
  and the `@property` stubs in `proof2why3/crosscheck_ir.py` and `proof2why3/crosscheck.py`).
- **The shadowed residue's TCFAILs — [PYVAL / ARRAY-INT MODEL SPLIT], co-blocked by the
  value-model frontier.** All 25 non-dispatcher shadowed methods were tried with
  `#@ sibling_concrete` on the 2-second oracle. The failures are ARGUMENT-type mismatches, not
  return-type ones: `_returns_string_seq` and `_has_set_op_on_map` both `array int` vs
  `pyval`, `_first_tuple_return_elts` `int` vs `list pyval`, `_field_type_for` `int` vs
  `string`. The CALLEE has already been converted onto the certified `pyval` value model
  while the CALLER's same-named parameter is still the untyped `array int`. **That is not a
  coercion gap — an `array int` genuinely is not a `pyval`, and a coercion would be a lie.**
  The reopening capability is caller-side: the caller's `body_stmts`-shaped parameter must
  itself be `pyval`-typed. Do NOT re-grind these as coercion work.

## Pick up here — in this order

1. **`frontend/pure_ast.strings` — CERTIFIED-BOUNDARY [HETEROGENEOUS TUPLE ELEMENT TYPE].**
   `parts` is a seq of 4-TUPLES that collapses to a HASH CONSTANT; its three consumers each
   need their own capability; the `kinds` SET is NOT a gap (it models as
   `map string (option int)`). NOTE it now carries a SECOND trusted clause
   (`ensures self.i > \old(self.i)`, added and consumed with `small_stmt` in relaunch #14),
   so converting it also DISCHARGES that TCB — read lesson (bs) §1 before scoping it.
   `pure_ast` proves 2798/2798 in ~55 min; budget accordingly.
2. **`@property` support in Module 5 — FOUR markers, language-surface.** See above. This is
   the biggest single named marker yield left that is not a recorded fundamental wall. It is
   cost/scale, so the funded window pays it — but it must go through
   `pycsl-audit-pycsl-language` (grammar -> validate -> IR -> WhyML), the five normative doc
   surfaces via `bin/doc-coherency.py --check`, and a re-specification of corpus 0962.
   A CHEAPER alternative exists and is NOT recommended without measurement: turn the live
   `@property` into a plain method and update its call sites (runtime-equivalent, but an API
   change to live emitter code the corpus exercises).
3. **The two Module5 dispatchers — 137 of the 154 remaining shadowed sites**
   (`_csl_to_ir` 92, `_py_expr_to_ir` 45). Already CONVERTED, so this is a SHADOWED-metric
   item. The recorded L2 TYPE-UNIFICATION wall; marking them `#@ sibling_concrete` makes them
   real recursion needing a structural variant (lesson (bi)). Everything else in the residue
   is co-blocked by the value-model frontier (see above), so this is now the ONLY large
   shadowed lever left.
4. **THE `isinstance_op 0 0` FACADE — TAKEN FROM 26 TO 10 THIS SESSION; the last TEN are
   three receiver SHAPES and the machinery is in place for each.**
   `expressions._isinstance_recv_whyml_type` / `_isinstance_recv_field_whyml_type` name the
   receiver's Why3 type for a plain `Var` (typed, untyped-by-exclusion, or a known record)
   and a RECORD-FIELD read. **The ten that remain decline on the receiver SHAPE: an Attribute
   read (`value.value`), a Subscript (`node.body[0]`), and a Call result.** Add one shape at
   a time and re-measure; each is fail-closed (return None and the historical constant
   stands), each is independently provable, and the diagnostic that finds them is a one-line
   stderr print at the isinstance fallback in `expressions.py` — re-add it in a minute rather
   than guessing. The original per-function census, still accurate for the residue: ONE producer (`expressions.py:~8383`: when
   `_tag_of_type(<class>)` yields no tag, the term is `(isinstance_op 0 0)` with BOTH
   arguments erased, so the test is independent of the value AND of the class). **26 sites**,
   by enclosing emitted function: `Module3_Weaver` 4 (`_target_dotted_path` 3, `_const_int`
   1); `pure_ast` 10 (`_get_raw_docstring` 3, `get_docstring` 3, `_write_constant` 1,
   `_is_non_empty_tuple` 1, `visit_Attribute` 1, `visit_Constant` 1); `module_collect` 4;
   `proof2why3/sertop` 3; `exec_splice` 3; `Module5_IREmitter` 1 (`_csl_proj`);
   `statements` 1 (`_handle_critical_section_stmt`). This is a FAITHFULNESS increment, not a
   count one — the same class as relaunch #14's `ch_isalpha_0 ()` and this session's
   `nargs_of` repair, both of which were worth their own increment.
   **THE CORPUS BLAST RADIUS IS ALREADY MEASURED AND IT IS EXACTLY ONE FILE: 0603**, the
   reference driver for "isinstance on a class-typed value", whose contract is
   `ensures ((result = 1) || (result = 0))` — 0/1-ness, precisely what a receiver-carrying
   repair preserves. Same situation and same justification as relaunch #14's `is*` repair
   and its driver 0447, so the precedent for a deliberate NON-INERT increment stands.
   **ANSWER THIS DESIGN QUESTION FIRST — it is what stopped the build today:**
   `isinstance_op` is MONOMORPHIC (`x: int`) and the receivers are not all ints (0603's
   `isinstance(x, Box)` has a RECORD receiver; `_csl_proj`'s `node.index` is an int hash).
   The honest op is therefore per-(class, receiver-type) — `val isinstance_Box_op (x: box)
   : bool` — and the emitter must be able to name the receiver's Why3 type at the call site.
   **Do NOT half-fix it** by passing the receiver where it happens to be an int and `0`
   elsewhere: that leaves one op name with two meanings. A CORPUS-INERT STAGING exists if you
   want the faithfulness gain before settling the type question — gate on `_uses_stmt_ir()` /
   `_uses_pyast_parser()`, which covers `_csl_proj` and `_handle_critical_section_stmt` and
   leaves 0603 byte-identical, exactly how relaunch #14 staged its increment 5 before
   un-gating it.
5. **`module6_whyml/struct_format.slot_id`** — a run-length encoder over `self.slots`; it
   needs the `array string` record field and the `use array.Array` preamble scan FIRST (both
   spiked and measured this session, see the boundary above), and unlike `arity` it is a
   PLAIN METHOD, so it is NOT blocked on `@property` support.

## RECORDED BOUNDARIES — do not re-grind without the named capability

- **`strings` — [HETEROGENEOUS TUPLE ELEMENT TYPE]** (see ladder item 1).
- **`struct_format.arity` — [UNEMITTABLE @property]** (see above). `slot_id` in the same file
  is a run-length encoder over a string list and needs the `array string` field FIRST.
  `parse_format`/`calcsize` stay on the regex categorical boundary.
- **The shadowed TCFAIL residue — [PYVAL / ARRAY-INT MODEL SPLIT]** (see above).
- **`_fin`, `_max_end`, `_fin_block` — [ERASURE-LEDGER]** (lesson (bd)). Reopening: an
  `emit_ir` that CARRIES the four ASDL location attrs.
- **`node(self, name, start_tok, **kw)` — [MODEL]**, a `**kw` SPLAT with a run-time class name.
- **`_slice`** — needs `self._lines`, a `List[str]` field the mirror's `__init__` does not model.
- **`_py_stmts_to_ir` / `_csl_to_ir` / `_py_expr_to_ir` — [L2 TYPE UNIFICATION]**;
  `_py_stmts_to_ir` additionally refuted by a measured four-erasure probe (SIX features for
  ONE stub, banked at `getting-better/pyast-expr/py-stmts-to-ir-erasure-probe.mlw`).
- **`for`-over-array termination** — the SOURCE cannot supply a variant.
- The **`_Unparser` family (~50 stubs)** — `self.interleave(lambda: …)` and
  `with self.delimit(…)`. A fundamental modelling boundary. (Three of its VOID WRITERS did go
  concrete this session — that is the shadowed metric, not the marker count.)
- **`Module2_Parser`'s contract-expression cluster** — recorded TERMINUS.
- `_decode_escapes` / `_decode_string` — `str|bytes` return, `chr(int(d, 8))`,
  `_unicodedata.lookup`. `_decode_fstring_middle` is blocked on it and splitting is NET ZERO.
- **`identifiers.whyml_ident`** — `unicodedata.normalize('NFD', ch)`, the same boundary;
  `identifiers.stable_hash` is a SHA-256 digest, irreducibly opaque.
- **`error` / `unsupported`** stay `\trusted` by design; count-neutral.
- **`_py_stmt_assign` reads `stmt.targets[0]` only** — chained-assignment targets silently
  dropped; the repair is corpus-byte-inert and was reverted (lesson (bk) §2).
- Dropping the `_record_array_fields` PROXY disjunct changes 6 of 813 corpus files (lesson (bc)).

## Instrument facts (re-verified this session)

1. **`why3` is NOT on the default PATH** (`/home/fabrice/.opam/framac-coq8/bin`). Without it
   `pycsl.py` errors AND EXITS 0. `export PATH=...` on every gate.
2. **`--import-path src/pycsl`** is the canonical mirror path.
3. `check-emitted-vacuity.py` is a false green without `--emit`.
4. **`.gitignore` has `*.mlw`** — `git add -A` SILENTLY SKIPS evidence files.
5. `bin/check-untrusted-emitted.py` reports 0/0/0/0 — a FALSE GREEN — with no PATH export.
6. `python3 -u` on every proof, or the log stays empty until the run ends.
7. **A `pycsl.py` run has TWO phases and the second (non-vacuity) dominates.
   A FAILING run is much FASTER than a passing one.** Never read a quick finish as good news.
8. **BACKGROUND WATCHERS DO NOT SURVIVE YOUR TURN ENDING.** `nohup` the proof, then wait in
   the FOREGROUND with `timeout 580 bash -c 'until grep -q ALLDONE …; do sleep 20; done'`
   AND pass the Bash tool's own `timeout` parameter (default 120 s will background you).
9. **`scratchpad/w2/sweep.sh <repo-root> <outdir>`** emits all 52 mirrors WITH L3-tc and
   writes `manifest.md5` in ~35 s. `bin/byte-diff-sweep.sh <out>` does the 813 corpus files
   in ~32 s. Keep a HEAD worktree at `…/8f7f6044-…/scratchpad/head-wt`; refresh with
   `git fetch /home/fabrice/git/pycsl <branch> && git checkout -q FETCH_HEAD`.
   **USE IT AS A SPIKE SANDBOX** — the whole `_py_stmt_raise` build and the entire
   sibling-concrete triage were priced there before a single proof minute was spent.
   Careful: a `cd` into the worktree persists for the whole compound Bash command, so
   `git apply` after a `cd` lands in the WRONG tree (it happened twice this session).
   **RE-BASELINE the sweeps after every landed increment** or the next diff reads the
   previous increment as collateral.
10. **`--fun` CANNOT probe `Module5_IREmitter` at all** — the filtered emission puts a
    `variant` clause on a plain `let`. Whole-file or nothing.
11. **`bin/check-shadowed-selfcalls.py --emit-dir <dir> --verbose`** gives the per-method
    breakdown and takes seconds when you already have the emitted `.mlw` files; without
    `--emit-dir` it re-emits everything (~2 min).
12. The **Alt-Ergo pin at `pycsl.py:1318` is stale** (2.6.2 vs installed 2.6.3). Keep passing
    `--provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,'` EXPLICITLY; do NOT edit the pin.

## Method notes this session paid for (full text in wall-lessons.md, (bt)-(bu))

- **(bt)** the capability the refutation names has a PLACE — prefer the home the existing
  recognizers do not already read; an OPAQUE `val`'s `Array.length` is NOT a length; and
  before arguing about a suspicious lowering, grep the emitted theory for the same shape
  somewhere already gated.
- **(bu)** the concrete-route RETURN-TYPE allowlist is a recurring silent floor (four times
  now) — add a new certified ADT to it in the same increment; the VOID sibling must be
  opt-in or `pure_ast` breaks on its trusted `-> NoReturn` `error`; a SYNTHESIZED body is a
  second producer of every call it contains; a "SKIP" in your own triage is a finding about
  your triage (`@staticmethod` puts a decorator between the `#@` block and the `def`); and
  proof cost is not proportional to source size.
- Still live: **(am)** ASSUME TWO PRODUCERS; **(ai)** never stack whole-file proofs;
  **(bd)** a conversion into an UNCOUNTED register is count theatre — decline it;
  **(bl)** grep the emitted body for `if true then` / `&& false` after ANY slot-type change;
  **(bn)/(br)** a table ADDITION is cross-cutting — after adding an entry, diff the emitted
  bodies of every OTHER site that reads it (done this session: the `SRaise` ADT arm moved
  four collateral mirrors by EXACTLY the two expected lines and nothing else);
  **(bp)** instrument the decision when a source bisection convicts an innocent;
  **(bq)** a returnless mutator is modelled as a NO-OP, and the fix is a RETURN INTERFACE —
  or, for a void SIBLING, the concrete application;
  **(bs)** state LESS when the support is not there, and read a dispatcher's `ensures` list
  before its return type.
