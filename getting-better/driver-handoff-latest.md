# HANDOFF — read this FIRST on relaunch (rewritten 2026-08-30, RELAUNCH #16 worker)

## State, verified from the surface at end of session

- **Count: MARKERS 496 · grep-substring 521 · offset 25 · unattached 0.** Quote BOTH.
  From **`bin/count-trusted-directives.py`**, never a hand-rolled grep — 25 of the grep hits
  are one boilerplate module-docstring line repeated across 25 mirror files, so every
  historical absolute figure (the famous "687") is overstated by that 25.
  **Window #2 delta so far: markers 530 -> 496, grep 555 -> 521.**
  **This session (#16): 502 -> 496, SIX conversions across four increments, plus TWO
  increments that are pure faithfulness/capability.**
- **`bin/check-shadowed-selfcalls.py`: 15 CONVERTED methods / 154 bypassing call sites,
  ratchet 15** — UNCHANGED this session. Needs `TMPDIR=/home/fabrice/git/pycsl/scratchpad`;
  ~2 min; give Bash an explicit timeout. 137 of the 154 are the TWO recorded L2 dispatchers.
- **Mirror-wide input-blind `isinstance_op 0 0`: 10 -> 1.** The one survivor is
  `exec_splice._is_constant_exec`'s `getattr(call, "func", None)` CALL result.
- Ledger **3**, untouched. Emitted axioms: **0**. Literal-guard grep: **0**.
- Fidelity at the standing baseline **2 DIVERGED** (`_handle_var_expr`, `_handle_for_stmt`).
  Field parity 335 / 7 known drift / 0 NEW. check-untrusted-emitted **813 / 797 / 0 / 0**.
  emitted-vacuity `--emit`: no NEW erasure, **8 known**, 0 input-blind.
  **Corpus byte-diff 0 over 814/814** — note the corpus is now **814**, not 813: this
  session added `0967_property_getter_supported.py`. `bin/self-annotate-mirror-check.sh`
  output byte-identical to the session-start HEAD baseline (3 mirrors drifted, exit 1 —
  that IS the baseline).
- **PROOF COSTS** (re-measured this session unless noted):
  `frontend/pure_ast` **2848** (was 2798), ~55 min.
  `frontend/Module5_IREmitter` **1133**, ~60 min.
  `frontend/ir_resolve` **792**. `frontend/__init__` **683**.
  `module6_whyml/statements` **912**, ~30 min. `module6_whyml/stmt_control_flow` **1846**, ~45 min.
  `module6_whyml/expressions` **1050**, ~15 min. `module6_whyml/functions` **1185**.
  `Module6_WhyMLTranspiler` **706**. `src/self-annotate/src/pycsl.py` **731**, ~20 min.
  `frontend/exec_splice` **45**, `proof2why3/crosscheck_ir` **41**, `audit_proof` **40**,
  `audit_proof_reverify` **11**, `module6_whyml/struct_format` **5**, `crosscheck` **2**,
  `Module1_Ingestor` **2**. A corpus driver is 1–11 s.
  **PROOF COST IS NOT PROPORTIONAL TO SOURCE SIZE.**
- Tree clean apart from the pre-existing user/build dirt (`session.txt`, untracked
  `scratchpad/`, `prompt`, `prompt.txt`). Leave it alone.
  `getting-better/.driver-deadline` intact (Sep 1 08:24 UTC). Commits unpushed by design.

## WHAT THIS SESSION LANDED (six gated increments)

1. **`frontend/pure_ast.strings` CONVERTED (502 -> 501)** — the CERTIFIED-BOUNDARY
   **[HETEROGENEOUS TUPLE ELEMENT TYPE] is BROKEN**, and with it a SECOND, sharper wall the
   spike uncovered: **[VARIANT-RANK LADDER EXHAUSTION]**. NET-NEGATIVE ON TCB: the two
   cursor clauses this stub used to ASSUME (`self.i >= \old(self.i)` from #13 and the STRICT
   `self.i > \old(self.i)` from #14) are now discharged proof obligations.
   The recorded value-model blockers were all real and all DECLINABLE — the contract that
   mattered is about the CURSOR, not the node. What actually stopped it: converting a stub
   MERGES SCCs (a `\trusted` `val` CUTS the call graph, and `strings` sat on the edge
   `atom -> strings -> _fstring`), and the group measure `16 * (len - i) + offset` has only
   16 slots, with `atom` at offset 1 and THREE members needing slots below it. Rescaled
   16 -> 64, all 32 offsets x4 — a MIRROR-SOURCE-ONLY change with provably zero corpus blast
   radius. Plus three TOKEN-KIND preconditions on the `atom_paren` precedent, each
   discharged at every call site from `cur`/`at_op`'s existing postconditions.
   FOUR fail-closed emitter capabilities, each measured before the next was written:
   an any/all `let function` FOLD that applies an abstract `val` sorting AFTER it in the one
   alphabetically-sorted abstract-op block DECLINES (Why3 rejects the forward reference);
   `ir_resolve`'s `Tuple[...]` return-annotation recorder widened from the single
   `Tuple[List[ExprIR], List[ExprIR]]` literal to a CLOSED per-slot table; a declined
   PYTHON-AST NODE CTOR FAMILY construction gets an `emit_ir`-TYPED nullary `val` instead of
   the int-typed generic fallback; and an UNHANDLED for-loop tuple target binds each
   component the body actually READS to a nondeterministic `any int` instead of leaving it a
   FREE VARIABLE. Plus a typed decline for `.extend` of an opaque-int read (HAVOC the
   accumulator, never a silent no-op).
2. **`@property` SUPPORT — the [UNEMITTABLE @property] boundary BROKEN, 501 -> 498.**
   **THE RECORDED GATE CLAIM WAS FALSE** (lesson (bz)): the handoff said corpus driver
   `0962` "exists to PIN the skip"; read from disk, 0962 has NO `@property` decorator — it is
   a plain 0-arg method MODELLING one, and its docstring says so. `@property` appears in ZERO
   corpus decorators, so un-skipping is corpus-inert by construction. TWO halves, both
   needed: the EMIT half (delete the decorator disjunct from `_should_skip_method` in BOTH
   producers — the source AND the SYNTHESIZED bespoke body in `functions.py`) and the READ
   half (`is_property` on the function IR -> `_property_getters` -> `<recv>.<prop>` becomes
   `(<cls>__<prop> <recv>)`). THREE properties converted: `struct_format.arity`,
   `audit_proof_reverify.ok`, `Module6_WhyMLTranspiler._heap_var`. Three more capabilities
   made `arity` FAITHFUL: `List[str]` -> `array string` in EVERY module, `use array.Array` /
   `use seq.Seq` pulled from the FIELD, and `len(self.<string-list field>)` -> `Array.length`.
   New corpus driver **0967_property_getter_supported.py**, PROVEN.
   `docs/pycsl-translational-reference.md` §T.11.3 updated; `bin/doc-coherency.py --check` GREEN.
3. **`module6_whyml/struct_format.slot_id` CONVERTED (498 -> 497) with a FULLY FAITHFUL
   body.** The content is the SLICE ITERATION: `for t in self.<f>[k:]` now reads the real
   array (`<f>[!idx + k]`, bound `(Array.length <f>) - k`) instead of erasing wholesale to
   `iter_length 0` / `iter_get 0 !idx` — an int-typed oracle applied to the LITERAL ZERO.
   Plus string-typed element locals, and the loop carries its OWN invariant+variant (the
   first proof attempt returned exactly the two goals that predicts).
4. **The `isinstance_op 0 0` facade: 10 -> 1, and CORPUS-INERT (0 of 814).** Three widenings,
   all found by INSTRUMENTING THE DECLINE, and the census corrected the handoff twice.
   The recorded "three receiver SHAPES" is the wrong axis — what those receivers share is a
   TYPE, so ONE `_is_emit_ir_expr` test replaces three shape rules. The handoff had not
   noticed the TUPLE-OF-CLASSES form at all (3 of the 10): Python defines it as the
   disjunction over the tuple, so it lowers as one. And the residual receivers lower to an
   application of an abstract op the SAME emission already declared, so **the op's declared
   return type IS the receiver's Why3 type** — evidence rather than inference.

5. **`proof2why3/crosscheck.pairwise` CONVERTED (497 -> 496)** — the
   [DICT-LITERAL RETURN DECLINES TO THE EMPTY MAP] boundary recorded EARLIER IN THIS SAME
   SESSION, broken by its own named reopening capability (lesson (cb)). A non-empty dict
   literal in a `map <K> (option <V>)`-returning function lowers to the `map_update_some`
   CHAIN instead of `(const (None: option int))`; the op was already declared with
   `ensures result = Map.set m k (Some v)`, so NO axiom. Retires a standing `TODO` in
   `expressions.py`. Triple-gated: the literal must HAVE keys (every `d = {}` byte-identical),
   the return type must be a nameable `map`, every key/value must coerce. A second capability
   fell out of the L3-tc iteration: **`bool(<string>)` was lowering to `bool_conv (x: int)`
   applied to a STRING** — now the faithful `(if str_eq_op s "" then 0 else 1)`.
6. **UNION IDENTITY AT THE PARAM SEAM — a capability increment, count unchanged.**
   `dedup=True` at the parameter-annotation seam, so two parameters of one function with the
   structurally identical `Optional[τ]` share ONE synthesized union type (Why3 sum types are
   NOMINAL). The mechanism already existed — `tool-feature-5` applies it at the LOCAL and
   RETURN seams for exactly this reason; only the param seam was left per-site. The FIELD
   seam stays per-site deliberately. 2 mirrors moved (`audit_proof`,
   `module6_whyml/expressions`), both re-proved; corpus byte-diff 0 of 814.

## CERTIFIED-BOUNDARIES RECORDED THIS SESSION

- **`crosscheck_ir.pairwise` — [DEGENERATE SYNTHESIZED UNION].** RE-MEASURED THREE TIMES
  in one session, and the first two readings were both BROKEN on the way here (lesson (cc)).
  It is no longer a dict-literal wall (increment 5) and no longer a union-IDENTITY wall
  (increment 6). The real cause: `Term` is an OPAQUE MARKER CLASS (`class Term: pass`), so
  the `Optional[Term]` union DROPS its payload arm and collapses to
  `type _union_cmp_6 = Arm_6_None` — ONE inhabitant. `a is None` therefore lowers to a test
  that is ALWAYS TRUE (lesson (bl)), the else-branch is unreachable, and the converted `cmp`
  would return `None` on every path — the `let` would CLAIM all three `pairwise` values are
  `None`. DECLINED under lesson (ca). REOPENING CAPABILITY: give a synthesized `Optional[X]`
  union a `Some` arm carrying an OPAQUE payload when `X` is an unmodelled class, instead of
  dropping the arm. **This is now the top of the ladder.**
- *(HISTORICAL, both BROKEN this session)* `crosscheck.pairwise`'s
  [DICT-LITERAL RETURN DECLINES TO THE EMPTY MAP] Both now EMIT (the `@property` boundary is gone) and both bodies port and
  type-check — and both were DECLINED ANYWAY. A `map`-returning dict LITERAL declines to
  `(const (None: option int))`, so the `let` would CLAIM the property has no keys: a positive
  FALSE statement, where the `val` it replaces is an unconstrained havoc that claims nothing.
  **A conversion that trades a havoc for a wrong definite value is a faithfulness
  REGRESSION** (lesson (ca)). REOPENING CAPABILITY: lower a string-keyed dict literal to the
  `map_update_some` chain — that op is already declared with `ensures result = Map.set m k v`,
  so NO axiom is involved. Blast radius is CORPUS-WIDE (every `(const (None: option int))`
  decline in an 814-file emission), so it owes its own gated increment and its own byte-diff.
  `crosscheck_ir.pairwise` additionally carries a NESTED `def cmp(a, b)`.
- **The last `isinstance_op 0 0` — `exec_splice._is_constant_exec`'s
  `getattr(call, "func", None)`.** A CALL result whose head symbol is not a declared abstract
  op, so the read-the-type-off-the-lowering rule has nothing to read.

## Pick up here — in this order

1. **THE OPAQUE `Some`-ARM PAYLOAD for a synthesized `Optional[X]` union — SPIKED,
   MEASURED AND PRICED THIS SESSION, then reverted for lack of a live consumer.**
   THE EDIT IS THREE LINES: in `Module5_IREmitter._union_arm_tag` (~3538) a CLASS-shaped
   `ast.Name` arm with no record `type_decl` returns `"Any"` and is DROPPED; return
   `elt.id` instead (gate on a leading capital + a typing-alias exclusion set). Module 6
   resolves an unknown payload tag to the `int` default, so NO Module 6 change is needed.
   **MEASURED BLAST RADIUS: corpus 4 of 814** (`0962`–`0965`, and in each the diff is
   exactly three DEAD type declarations becoming inhabited — nothing those drivers prove
   changes), **mirrors 4 of 52 with TC_FAIL 0** (`audit_proof`, `Module2_Parser`,
   `crosscheck_ir`, `sertop`), PLUS a mirror sync of `_union_arm_tag` itself which drags
   `Module5_IREmitter` (1133 goals, ~60 min) into the battery.
   **IT DOES NOT FINISH `crosscheck_ir.pairwise` ON ITS OWN** — measured: with it, the
   union identity is fixed and the presence test becomes real, and the NEXT L3-tc error is
   `Arm_7_0 (a = b)`, a Why3 `bool` where the `Optional[bool]` arm's payload is `int` (a
   bool->int coercion missing at the union-arm RETURN wrap), with a program-level ADT
   equality question behind that. So take it WITH the bool->int wrap, or take it for its
   own sake: at least one degenerate union is LIVE — `audit_proof`'s
   `val audit_rocq (…) (proofs_dir: _union_audit_rocq_1) …` is an `Optional[Path]`
   PARAMETER whose type today has ONE inhabitant, i.e. the signature says the argument is
   always absent. It is a deliberate NON-INERT increment; say so plainly and re-prove the
   four corpus drivers.

   *(original note, still accurate)* **THE OPAQUE `Some`-ARM PAYLOAD.** One marker
   directly (`crosscheck_ir.pairwise`) and it removes a whole class of modelled-away
   optionals — a union that drops its payload arm makes every `x is None` guard a literal
   `true` (lesson (bl)), which is a positive false claim wherever such a union is a
   parameter. The two cheaper walls in front of it were both broken this session, so the
   spike is now three lines from a verdict: give `_normalize_union_annotation`'s
   `lowered` list a `Some` arm with an opaque payload when the arm tag is an unmodelled
   class instead of dropping it as `Any` (see the `any_dropped` / GT1 path at
   `Module5_IREmitter.py:~3710`), and MEASURE — this one has a real corpus blast radius,
   unlike the last three capabilities.
2. **The remaining half of `@property`: route a `self.<prop>` READ.**
   `_handle_attribute_expr` is the NON-self path (its own docstring says so), so the
   `self.` receiver goes elsewhere and is NOT yet routed. Concretely: the mirror models
   `Module6_WhyMLTranspiler._heap_var` as a MUTABLE STRING RECORD FIELD, so `self._heap_var`
   still projects that field while the newly proven getter sits beside it unused — two
   symbols for one thing. Blast radius: `_heap_var` is a field on FOUR mirrors
   (Module6_WhyMLTranspiler + the expressions/statements/stmt_control_flow mixins), but the
   `_property_getters` map is per-module so only the module that DEFINES the getter can
   route. Expect 1 mirror to move, ~20 min to re-prove.
3. **The two Module5 dispatchers — 137 of the 154 remaining shadowed sites**
   (`_csl_to_ir` 92, `_py_expr_to_ir` 45). Already CONVERTED, so this is a SHADOWED-metric
   item. The recorded L2 TYPE-UNIFICATION wall; marking them `#@ sibling_concrete` makes them
   real recursion needing a structural variant (lesson (bi)). Everything else in the shadowed
   residue is co-blocked by the value-model frontier. This is the ONLY large shadowed lever
   left — and note that lesson (bw) now gives a NEW angle on it: a merged SCC needs a
   COMMON measure with enough rank capacity, and the multiplier can be rescaled at zero
   corpus cost.
4. **`pure_ast`'s remaining 97 markers.** ~60 are the `_Unparser` family (recorded
   fundamental). The rest is the `_N`/node-builder infrastructure plus the public `ast` API
   surface (`iter_fields`, `iter_child_nodes`, `walk`, `copy_location`,
   `fix_missing_locations`, `increment_lineno`, `dump`, `_splitlines_no_ff`,
   `get_source_segment`, `parse`, `literal_eval`). `_splitlines_no_ff` is a pure
   string -> list-of-strings function and is the most promising of them; `walk` and anything
   reached through it are GENERATORS and are blocked.
5. **The last `isinstance_op 0 0`** (see the boundary above) — one site, low value, but it
   would close the facade completely.

## RECORDED BOUNDARIES — do not re-grind without the named capability

- **`crosscheck.pairwise` / `crosscheck_ir.pairwise` — [DICT-LITERAL EMPTY MAP]** (above).
- **The shadowed TCFAIL residue — [PYVAL / ARRAY-INT MODEL SPLIT]**, co-blocked by the
  value-model frontier. The CALLEE is on the certified `pyval` model while the CALLER's
  same-named parameter is still the untyped `array int`. **That is not a coercion gap** — an
  `array int` genuinely is not a `pyval`. The reopening capability is caller-side.
- **`_fin`, `_max_end`, `_fin_block` — [ERASURE-LEDGER]** (lesson (bd)). Reopening: an
  `emit_ir` that CARRIES the four ASDL location attrs.
- **`node(self, name, start_tok, **kw)` — [MODEL]**, a `**kw` SPLAT with a run-time class name.
- **`_slice`** — needs `self._lines`, a `List[str]` field the mirror's `__init__` does not model.
- **`_py_stmts_to_ir` / `_csl_to_ir` / `_py_expr_to_ir` — [L2 TYPE UNIFICATION]**;
  `_py_stmts_to_ir` additionally refuted by a measured four-erasure probe (SIX features for
  ONE stub, banked at `getting-better/pyast-expr/py-stmts-to-ir-erasure-probe.mlw`).
- **`for`-over-array termination** — the SOURCE cannot supply a variant.
- The **`_Unparser` family (~50 stubs)** — `self.interleave(lambda: …)` and
  `with self.delimit(…)`. A fundamental modelling boundary.
- **`Module2_Parser`'s contract-expression cluster** — recorded TERMINUS.
- `_decode_escapes` / `_decode_string` — `str|bytes` return, `chr(int(d, 8))`,
  `_unicodedata.lookup`. (NOTE: `_decode_string`'s mirror now carries the annotation
  `-> "Tuple[PyConstVal, str, bool]"`, which is what let `strings` convert around it.)
- **`identifiers.whyml_ident`** — `unicodedata.normalize('NFD', ch)`;
  `identifiers.stable_hash` is a SHA-256 digest, irreducibly opaque.
- **`error` / `unsupported`** stay `\trusted` by design; count-neutral.
- **`_py_stmt_assign` reads `stmt.targets[0]` only** — the repair is corpus-byte-inert and
  was reverted (lesson (bk) §2).
- Dropping the `_record_array_fields` PROXY disjunct changes 6 of 813 corpus files (lesson (bc)).
- `struct_format.parse_format` / `calcsize` stay on the regex categorical boundary.

## Instrument facts (re-verified this session)

1. **`why3` is NOT on the default PATH** (`/home/fabrice/.opam/framac-coq8/bin`). Without it
   `pycsl.py` errors AND EXITS 0. `export PATH=...` on every gate.
2. **`--import-path src/pycsl`** is the canonical mirror path.
3. `check-emitted-vacuity.py` is a false green without `--emit`.
4. **`.gitignore` has `*.mlw`** — `git add -A` SILENTLY SKIPS evidence files.
5. `bin/check-untrusted-emitted.py` reports 0/0/0/0 — a FALSE GREEN — with no PATH export.
6. `python3 -u` on every proof, or the log stays empty until the run ends.
7. **A `pycsl.py` run has TWO phases and the second (non-vacuity) dominates.
   A FAILING run is much FASTER than a passing one.**
8. **BACKGROUND WATCHERS DO NOT SURVIVE YOUR TURN ENDING.** `nohup` the proof, then wait in
   the FOREGROUND with `timeout 580 bash -c 'until grep -q ALLDONE …; do sleep 25; done'`
   AND pass the Bash tool's own `timeout` parameter.
   **`scratchpad/w2/r17prove.sh <file> …`** proves a LIST of mirrors SEQUENTIALLY (lesson
   (ai)) and appends `OK`/`FAIL` + goal count to `scratchpad/w2/r17proofs/RESULTS`, ending
   with `ALLDONE`. It `cd`s to the repo root itself, so it is safe to launch from anywhere.
9. **`scratchpad/w2/sweep.sh <repo-root> <outdir>`** emits all 52 mirrors WITH L3-tc and
   writes `manifest.md5` in ~35 s. **`scratchpad/w2/keepsweep.sh <repo-root> <outdir>`** (new
   this session) does the same but KEEPS the `.mlw` files, which is what you need for any
   emitted-text census (`isinstance_op 0 0`, `const (None: option int)`, …).
   `bin/byte-diff-sweep.sh <out>` does the 814 corpus files in ~32 s and needs a `.venv` —
   in a worktree, `ln -sfn /home/fabrice/git/pycsl/.venv .venv` first.
   Keep a HEAD worktree at `…/8f7f6044-…/scratchpad/head-wt`; refresh with
   `git checkout -q -- . && git fetch /home/fabrice/git/pycsl <branch> && git checkout -q FETCH_HEAD`.
   **RE-BASELINE the sweeps after every landed increment.**
   **A `cd` into the worktree persists for the whole compound Bash command, so a `git apply`
   after a `cd` lands in the WRONG tree — it happened AGAIN this session (third time).**
10. **`--fun` CANNOT probe `Module5_IREmitter` at all** — whole-file or nothing.
11. **`bin/check-shadowed-selfcalls.py --emit-dir <dir> --verbose`** gives the per-method
    breakdown in seconds when you already have the emitted `.mlw` files.
12. The **Alt-Ergo pin at `pycsl.py:1318` is stale**. Keep passing
    `--provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,'` EXPLICITLY; do NOT edit the pin.
13. **`grep` MISBEHAVES on `driver-progress.log`** — the file has 2700-character lines and
    `grep -c` returned "no match" for text that is demonstrably present. Use
    `python3 -c "print('…' in open(f).read())"` to verify that file's content.
14. **A `#@`-block heredoc in a Bash `-m` commit message gets MANGLED by backtick command
    substitution.** Write long commit messages to a file and use `git commit -F`.

## Method notes this session paid for (full text in wall-lessons.md, (bw)-(ca))

- **(bw)** a conversion's real blocker may be the TERMINATION LADDER, not the value model;
  converting a stub MERGES SCCs because a `val` CUTS the call graph; a rank ladder has a
  CAPACITY and rescaling the multiplier is a mirror-source-only change with zero corpus cost;
  strict progress ALWAYS needs a precondition, and the invariant that carries it is
  "either the cursor moved, or it is still on the token the precondition named".
- **(bx)** A DECLINE HAS A TYPE. Three of the five capabilities were declines that were
  already correct but emitted at the wrong type. Produce a decline at the type the CONSUMER
  expects and produce it NONDETERMINISTICALLY; and bind only what is READ.
- **(by)** ITERATE THE TYPE-CHECKER, NOT THE PROVER. Five of the six blockers were found in
  ~10 s each by re-emitting with `--no-proof` and reading the FIRST L3-tc error. Price a
  spike by "how many L3-tc errors deep is this".
- **(bz)** VERIFY THE HANDOFF'S GATE CLAIM AGAINST DISK. The recorded corpus pin did not
  exist, and that one wrong sentence had kept a five-marker, one-line capability parked as a
  language-surface project. Cost is what decides whether an item gets worked at all.
- **(ca)** A CONVERSION CAN MAKE THE MODEL WORSE. The acceptance test is not "does it prove"
  and not even "is the body faithful" — it is "does the `let` claim anything the `val` did
  not, and is everything it claims true?" A decline that lands on a HAVOC is fine; a decline
  that lands on a CONSTANT is an assertion.
- Still live: **(am)** ASSUME TWO PRODUCERS (a SYNTHESIZED body is a second producer — it bit
  again this session on `_should_skip_method`); **(ai)** prove sequentially;
  **(bd)** a conversion into an UNCOUNTED register is count theatre; **(bl)** grep the
  emitted body for `if true then` / `&& false` after ANY slot-type change;
  **(bn)/(br)** a table ADDITION is cross-cutting; **(bp)** INSTRUMENT THE DECISION — it paid
  twice this session and corrected the handoff's own census both times;
  **(bq)** a returnless mutator is modelled as a NO-OP; **(bs)** state LESS when the support
  is not there.
