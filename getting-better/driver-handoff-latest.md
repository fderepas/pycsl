# HANDOFF — read this FIRST on relaunch (rewritten 2026-08-30, RELAUNCH #17 worker)

## State, verified from the surface at end of session

- **Count: MARKERS 492 · grep-substring 517 · offset 25 · unattached 0.** Quote BOTH.
  From **`bin/count-trusted-directives.py`**, never a hand-rolled grep — 25 of the grep hits
  are one boilerplate module-docstring line repeated across 25 mirror files, so every
  historical absolute figure (the famous "687") is overstated by that 25.
  **Window #2 delta so far: markers 530 -> 492, grep 555 -> 517.**
  **This session (#17): 496 -> 492, FOUR conversions across SEVEN gated increments (three
  of the seven are pure capability/faithfulness), plus FIVE certified-boundary records,
  plus a COMPREHENSIVE cheap-win census.**
- **`bin/check-shadowed-selfcalls.py`: 14 CONVERTED methods / 153 bypassing call sites,
  ratchet 14** (was 15/154; the ratchet constant in the script is now 14). Needs
  `TMPDIR=/home/fabrice/git/pycsl/scratchpad`; ~2 min; give Bash an explicit timeout.
  **137 of the 153 are the TWO recorded L2 dispatchers** — see the boundary below, which
  this session RE-CLASSIFIED.
- Ledger **3**, untouched. Emitted axioms: **0**. Corpus is **814** files.
- Fidelity at the standing baseline **2 DIVERGED** (`_handle_var_expr`, `_handle_for_stmt`).
  `bin/self-annotate-mirror-check.sh`: **3 mirrors drifted, exit 1 — that IS the baseline.**
  check-untrusted-emitted **817 / 801 / 0 / 0** (was 813/797).
  emitted-vacuity `--emit`: no NEW erasure, **8 known**, 0 input-blind. doc-coherency GREEN.
- **Corpus byte-diff deliberately SPENT twice this session, 6 files of 814 in total** —
  increment 1 (`0962`–`0965`, three dead type declarations each) and increment 6
  (`0406`, `0407`, two lines each). All six re-proved. Everything else was 0 of 814.
- **PROOF COSTS** (re-measured this session unless noted; NOT proportional to source size):
  `frontend/pure_ast` **2857**, ~50 min. `frontend/Module5_IREmitter` **1134**, ~50 min.
  `module6_whyml/stmt_control_flow` **1846**, ~45 min. `module6_whyml/functions` **1187**,
  ~30-45 min. `module6_whyml/expressions` **1069**, ~16 min.
  `frontend/Module2_Parser` **720**, ~10 min (NEW). `src/self-annotate/src/pycsl.py` **731**, ~20 min.
  `Module6_WhyMLTranspiler` **706**, ~20 min (NEW). `frontend/ir_resolve` **792**.
  `frontend/__init__` **683**. `proof2why3/parser` **438**, minutes (NEW).
  `frontend/Module3_Weaver` **259** (**270** converted), ~8 min.
  **`module6_whyml/preamble` 216, ~5 min (NEW — startlingly cheap for an 8000-line mixin)**.
  `proof2why3/from_lean_json` **56** (NEW). `proof2why3/canonical` **48** (NEW, was 38).
  `frontend/exec_splice` **45**, `proof2why3/crosscheck_ir` **41**, `audit_proof` **40**,
  `audit_proof_reverify` **11**, `proof2why3/sertop` **11**,
  `module6_whyml/struct_format` **5**, `proof2why3/crosscheck` **2**. Corpus driver 1–11 s.
- **FULL REFERENCE SUITE, run end-to-end on the final tree AND on the session-start commit:
  `Results: 3010/3112 passed` BOTH TIMES, and the 102 failing names are IDENTICAL (the diff
  of the two failure lists is EMPTY).** Zero regressions from this session. TWO PRE-EXISTING
  BASELINES, now measured so nobody mistakes them for their own damage: (1)
  `bin/run-reference-tests.sh` ABORTS on its leading IR-conformance gate with **40 MISMATCH**
  (`only-derived=['param_ast_node_types','set_value_types']` — the front-end emits two IR keys
  the goldens predate; verified identical at the session-start commit). Run it with
  `PYCSL_SKIP_CONFORMANCE_CHECK=1`; the goldens need an IR_VERSION-gated refresh that is
  nobody's current work item. (2) The suite's standing **102/3112** failures — 23 in
  pycsl-reference (0211-0220, 0226, 0484, 0540, 0700, 0701, 0714, 0766, 0932, 0938, 0943,
  0944, 0948, 0949) and 79 in python-reference. `run-reference-tests.sh` line 176 also emits a
  cosmetic `[[: value too great for base` for every non-numeric corpus name.
- Tree clean apart from the pre-existing user/build dirt (`session.txt`, untracked
  `scratchpad/`, `prompt`, `prompt.txt`, `style.css` — the last dated Aug 26, leave it).
  `getting-better/.driver-deadline` intact (Sep 1 08:24 UTC, untouched).
- **NOTE, observed not caused: THE BRANCH HAS BEEN PUSHED TO `origin` BY SOMETHING OUTSIDE
  THIS WORKER.** `git reflog show origin/ghost-assign-bc6` carries a run of `update by push`
  entries, the most recent landing on `4a4f0e66` (a commit of THIS session, ~1 h before its
  end). This worker never ran `git push` — the gate was honoured. At end of session only the
  last FOUR commits are local-only (`5d546c2d`, `274caa87`, `6bed3044`, `3e4bdc62`). The
  previous handoff's line "commits unpushed by design" is therefore NO LONGER TRUE of the
  repository; whoever owns the outer supervisor should confirm that push is intended, and a
  future worker should not be surprised to find `@{u}..HEAD` small.

## WHAT THIS SESSION LANDED (seven gated increments)

1. **THE OPAQUE `Some`-ARM PAYLOAD — a FAITHFULNESS increment, count unchanged.**
   A CLASS-shaped `Optional[X]` arm with no WhyML record type is no longer DROPPED as
   `Any`; it carries the class name as its payload tag, which Module6 resolves to the
   OPAQUE `int` default. The single-inhabitant `type _union_… = Arm_i_None` collapse is
   gone, so `x is None` is a real two-valued test (lesson (bl)) and an `Optional[X]`
   PARAMETER no longer declares that its argument is ALWAYS ABSENT —
   `audit_proof.audit_rocq`'s `proofs_dir` was exactly that positive false claim.
   Census-first by INSTRUMENTING THE DECLINE: exactly 46 declines mirror-wide over three
   class names, 12 corpus-wide. NON-INERT: corpus 4 of 814, all re-proved; mirrors 5 of 52,
   TC_FAIL 0 (`Module2_Parser` **714/714** newly measured; `Module5_IREmitter` **1134/1134**).
2. **`frontend/pure_ast._splitlines_no_ff` CONVERTED (496 -> 495), fully faithful.**
   The `val` erased BOTH the string input and the list result. **THE BLOCKER WAS AN
   ANNOTATION SPELLING, not a value model**: `pure_ast` may not import `typing` (lesson
   (ss)), so its only legal return spelling is the QUOTED `-> "List[str]"`, which Module5
   sees as an unrecognised string Constant. `ir_resolve` now records `list` + element
   `string` for the quoted form — the STRING TWIN of the existing `-> "List[ExprIR]"`
   route. Byte-inert by construction (a repo-wide census found ZERO pre-existing
   `-> "List[str]"`). pure_ast **2857/2857**.
3. **THE MAP-KEY MODEL SPLIT — shadowed ratchet 15 -> 14, count unchanged.**
   `name in self._module_binding_names()` emitted
   `Map.get (self__module_binding_names_0 ()) (str_hash_op !name)` — an UNCONSTRAINED,
   INT-KEYED map indexed by a HASH — while the CONVERTED method is emitted as the faithful
   StrSet `map string bool`. Three one-line policies: `map ` admitted to the concrete-route
   allowlist (its FIFTH silent floor, lesson (bu)); a PER-CALLEE StrSet retype of
   `_build_method_return_type_map`; and a StrSet membership arm reading the RAW string key.
   **THE GATE IS THE POINT**: this is backlog 1b(A)'s `Set[str]` retype, whose ATTEMPT #1
   was rejected for being GLOBAL — the `#@ sibling_concrete` marker is the per-CONSUMER
   gate that attempt lacked. expressions **1069/1069**, M6T **706/706**, functions **1185/1185**.
4. **THE MODULE-LEVEL TERM CARRIER — `proof2why3/canonical.canonicalize` CONVERTED
   (495 -> 494), fully faithful.** `val canonicalize (t: int) : int` in a file that ALREADY
   carries the certified 9-constructor `term` inductive. THE BLOCKER WAS A GATE: the
   `-> Term` carrier was TRIPLE-gated and one gate was `@mutable_state` CLASS membership,
   which a module-level function can never satisfy. Four fail-closed widenings (return
   carrier, PARAM carrier — there was none at all, the `isinstance` REAL constructor
   discriminant, `Return_term` + `term` local pre-decl). Corpus 0 of 814; two of the four
   changed mirrors are pure faithfulness gains elsewhere (`from_lean_json.project_to_ir`
   and `parser.parse_type_expr` now declare `: term`, not `: int`).
5. **`module6_whyml/preamble._emit_preamble_helpers` CONVERTED (494 -> 493)** — the ONE
   genuine find of the ~230-stub census. The `val` collapsed the whole `needs` dictionary
   to an int; the `let` reads it as a real `map string (option int)` with NATIVE string
   keys and snocs the REAL preamble line literals. Measured: zero `str_hash_op`, zero
   argument-less oracles, zero `getattr_*`. preamble **216/216**. Mirror-source-only.
6. **THE FOR-OVER-COLLECTION VARIANT UN-GATED — `Module2_Parser.parse_node_contracts`
   CONVERTED (493 -> 492).** The recorded [`for`-over-array termination] boundary is HALF
   BROKEN and its cause is located exactly: the emitter ALREADY auto-emits
   `invariant { 0 <= !idx } / variant { <len> - !idx }`, but that arm was
   **`@mutable_state`-ONLY**. The variant is SOUND BY CONSTRUCTION, so it now fires for any
   loop whose length term is already pure LOGIC. TWO measured fail-closed guards: never for
   a PROGRAM length call (`iter_length (get_clauses !c)` — Why3 rejects it in a variant),
   and it STANDS DOWN when the source supplies `#@ loop variant` (corpus **0208** breaks
   otherwise). The @mutable_state arm is preserved verbatim beside it — dropping it silently
   removed variants from Module5_IREmitter, caught by the sweep. Corpus 2 of 814, both
   re-proved. Module2_Parser **720/720**.
7. **THE RECEIVER-CARRYING UNANNOTATED CALL — a faithfulness increment, corpus-INERT.**
   The generic unannotated-call fallback still DROPPED a COMPUTED receiver, so
   `float(node.value).is_integer()` lowered to `(is_integer_0 ())` — a test independent of
   the value tested AND of everything else. Same defect the previous window repaired twice
   (`ch_isalpha_0 ()`, `isinstance_op 0 0`); only the generic fallback still had it. Now
   `is_integer_1 (py_float_1 (get_value node))`, and pure_ast's chained
   `repr(value).replace(a,b)` goes `replace_2` -> `replace_3 (repr_conv value) …`. The op
   stays EXACTLY as uninterpreted — what is restored is the LINK to the value. THREE
   fail-closed refinements, each found by measuring after the previous cut looked clean:
   a RECORD-literal receiver is a Why3 SYNTAX error as an argument; a COLLECTION-shaped
   receiver is an L3-tc TYPE error (`_coerce_to_int` collapses a bare `(Array.make …)` but
   NOT the let-bound array-literal form); and lowering a receiver REGISTERS abstract ops as
   a side effect, so a DECLINED receiver left DEAD `val` declarations behind — snapshot and
   restore `_abstract_ops`. Module3_Weaver **259/259**, pure_ast **2857/2857**, corpus 0 of 814.
   The mirror-wide ARGUMENT-LESS ORACLE census is now 22 applications over 6 names, and
   every survivor is a genuinely 0-argument method or the dotted `x.next()` form.

## CERTIFIED-BOUNDARIES RECORDED THIS SESSION (all with a PRICED reopening capability)

- **THE TWO L2 DISPATCHERS — RE-CLASSIFIED. The recorded cause [L2 TYPE UNIFICATION] IS
  WRONG.** `#@ sibling_concrete` on `_py_expr_to_ir` TYPE-CHECKS FINE. The historical
  `unbound function or predicate symbol` came from NINE BESPOKE group-emitters in
  functions.py HARD-CODING their opening keyword as `let`, breaking the `let rec … with`
  chain FROM THE INSIDE of a 20-member SCC (verified by instrumenting `compute_sccs`) —
  lesson (am) in a new place: a SYNTHESIZED body is a second producer OF THE GROUP KEYWORD.
  ONE post-process in `_emit_function` fixes all nine; MEASURED: L3-tc passes, shadowed
  sites **153 -> 125**, corpus byte-diff 0 of 814, mirrors 2 of 52. Patch kept at
  `scratchpad/w2/l2_dispatcher_scc.spike.patch`.
  **THE REAL BLOCKER IS TERMINATION, AND IT IS A SOUNDNESS FLOOR.** The 20-member mutual
  recursion has no common variant: 1198 Valid / **86 TIMEOUT**, 43 of them `termination`.
  And the measure CANNOT BE DERIVED — checked against the emitted `.mlw`: the dispatch goes
  through `val function pyx_view (e: emit_ir) : pyast_expr`, an UNINTERPRETED view whose
  only law is a KIND law, over a datatype the preamble itself documents as "NOT recursive
  at this stage". So `size_<T> (payload_of e) < size e` would be a NEW AXIOM and the ledger
  would exceed 3. **REOPENING CAPABILITY: make `pyx_view` STRUCTURAL** — a recursive
  `pyast_expr` that is a defined projection of `emit_ir`, so the size law holds by
  construction. An ADT redesign co-landing with Phase2l_PyAstExpr.v / PyAstExpr.lean.
  `_csl_to_ir` (92 sites) does not even reach that point: its group fails L3-tc with
  `this expression produces an unlisted write effect` — members of a `let rec … with` group
  must agree on their EFFECT SUMMARY. That is a SECOND, additional wall.
- **`crosscheck_ir.pairwise` — RE-CLASSIFIED, and the recorded reopening capability was
  WRONG.** #16 recorded "`Term` is an OPAQUE MARKER CLASS" and named the opaque `Some`-arm
  payload as the fix. That capability is real and landed as increment 1 — but READ FROM
  DISK the premise is FALSE for this file: `Term` is a CERTIFIED 9-constructor Why3
  inductive with a structural `term_eq`, the `Optional[Term]` FIELDS already lower to
  `option term`, and the SIBLINGS `all_agree`/`provers_agree` already use `term_eq`. The
  opaque-int arm would have been a faithfulness REGRESSION relative to its own siblings.
  The FAITHFUL route was SPIKED AND WORKS (~15 lines,
  `scratchpad/w2/opt_term_param.spike.patch`): `Optional[Term]` at the PARAM seam through
  the same `opaque_term` -> `option term` path the FIELD seam takes, an option-presence
  `is None` branch, and `a == b` lowered to `(match a, b with Some x, Some y -> term_eq x y
  | _, _ -> false end)` AT THE INT TYPE THE UNION ARM EXPECTS — which SUBSUMES the
  "bool->int union-arm return wrap" the previous handoff predicted as a separate capability.
  TWO gaps remain: (1) a call to a LIFTED NESTED `def` does not resolve to the hoisted
  symbol (it lowers to an abstract `cmp_2` with int-coerced args; this codebase handles
  every nested-def shape with a BESPOKE outer+lifted recognizer); (2)
  `Dict[str, Optional[bool]]` IS NOT EXPRESSIBLE — the dict model already spends `option`
  on KEY PRESENCE, so a Python `None` VALUE is indistinguishable from an ABSENT KEY.
  DEMAND is nil (the only reader of `.pairwise` is the `\trusted` `diagnostic()`).
- **`PyCSLWeaver._desugar_for` — [FOR-OVER-OPAQUE-ITERABLE TERMINATION]. BUILT, PROVEN
  GREEN, AND DECLINED ON A SOUNDNESS PRICE.** The four-step chain works and the file proves
  **270/270, 0 non-Valid**, with an AFFORDABLE blast radius (corpus 6/814, mirrors 8/52,
  TC_FAIL 0): `val function iter_length` + `val function get_<attr>` + admitting
  `iter_length`/RANGE to the variant gate + suppressing the `0 <= !idx` invariant for a
  RANGE loop. **Reverted anyway** (patch + proof log in `scratchpad/w2/opaque_iterable_
  variant.*`): `val function get_<attr>` asserts ATTRIBUTE READS ARE DETERMINISTIC, and
  because this model already treats `setattr` as a NO-OP (lesson (bq)), pure projectors
  would let a mutate-then-read body PROVE `node.x == \old(node.x)` right after
  `node.x = 1`. Global assumption, ONE marker of consumer. **The two SOUND halves are
  separable and stay available**: `iter_length` purity (a length query on a collection
  VALUE) and the range-loop variant. What would make it sound: relate `setattr` to the
  projectors (a real object-state model), or emit projectors pure only in a setattr-free file.
- **THE COMPREHENSIVE CHEAP-WIN CENSUS — ZERO faithful cheap wins.** Ladder rung 1, re-run
  with all FOUR of this session's new capabilities in place, over ~230 `\trusted` stubs in
  22 mirror files, by PORTING THE LIVE BODY VERBATIM and re-emitting on the seconds-scale
  L3-tc oracle (always restoring). **34 stubs pass L3-tc; every one examined is a DECLINE**
  — an int-erased FACADE (`_region_bound_str` lowers to `v := 0; if !v <> 0`, so it returns
  the CONSTANT `"<expr>"`; `_Harvester._build` appends to a FRESH LOCAL `Array.make 1024 0`
  instead of the object's field; `visit_Module` is a row of `setattr_3 node <hash> 0`;
  `_Unparser.set_precedence` references an UNBOUND `nodes`; `_Unparser.traverse` branches on
  `typeof_op 422`, an oracle applied to a LITERAL), or a GENERATOR, or a DUNDER Module5
  skips, or an `error`/`unsupported` trusted by design. **Trap (hh) confirmed at scale:
  34 of 34.** The prober is at `scratchpad/w2/probe_all.py` (and `show_conv.py` prints one
  converted body); re-run it after any capability lands.

- **A MEASURED HONESTY GAP IN ALREADY-BANKED CONVERSIONS — the FRAME plane, quantified for
  the first time.** A mirror-wide census of `setattr*` INSIDE CONVERTED (`let`) bodies found
  **11 methods across 4 mirrors** whose emitted body performs a mutation the model DISCARDS
  (lesson (bq)), and **8 of the 11 declare NO `writes` at all**. Worst:
  `PyCSLWeaver._init_function_csl_fields` — CONVERTED, PROVEN, and its body is **31**
  applications of `setattr_3 node <hashed-attr> 0` under `#@ assigns \nothing`, a frame claim
  TRUE OF THE MODEL and FALSE OF THE SOURCE. Also `_Parser._fin_pos` (4),
  `_Unparser.block/visit/visit_Module/visit_Try/visit_TryStar` (1-2 each),
  `FunctionEmissionMixin._refine_tuple_return_type` (4) / `_build_param_list` (2), and
  `StatementEmissionMixin._handle_fieldassign_stmt`/`_handle_fieldaugassign_stmt` (2 each —
  these DO declare a large `writes` set, so their frame is real, just not for the setattr'd
  attribute). NOT an argument to revert them: the bodies are otherwise faithful and only the
  FRAME claim overstates. It is the SAME missing capability the `_desugar_for` decline names.
  **Until an object-state model exists, an `assigns \nothing` on a method that setattrs is a
  MODEL statement, not a source guarantee — read every one that way.**

## RECORDED BOUNDARIES CARRIED FORWARD — do not re-grind without the named capability

- The five above.
- **The shadowed TCFAIL residue — [PYVAL / ARRAY-INT MODEL SPLIT]**, RE-CONFIRMED this
  session by re-running the `#@ sibling_concrete` triage over all 13 non-dispatcher
  shadowed methods: 11 TC_FAIL with exactly that signature, 2 NOEFFECT (which turned out
  to be the MAP-KEY split and one of them, `_module_binding_names`, was broken as
  increment 3; `_collect_map_typed_locals` remains, co-blocked by the pyval/array-int split).
- **`_fin`, `_max_end`, `_fin_block` — [ERASURE-LEDGER]** (lesson (bd)).
- **`node(self, name, start_tok, **kw)` — [MODEL]**, a `**kw` SPLAT with a run-time class name.
- **`_slice`** — needs `self._lines`, a `List[str]` field the mirror's `__init__` does not model.
- The **`_Unparser` family (~50 stubs)** — `self.interleave(lambda: …)` / `with self.delimit(…)`.
  RE-CONFIRMED by the census: 13 of them pass L3-tc and every one is a facade.
- **`Module2_Parser`'s contract-expression cluster** — recorded TERMINUS.
- `_decode_escapes` / `_decode_string`; `identifiers.whyml_ident` / `stable_hash`;
  `struct_format.parse_format` / `calcsize` (regex categorical boundary);
  `proof2why3/normalize`'s whole file (regex).
- **`error` / `unsupported`** stay `\trusted` by design; count-neutral.
- Dropping the `_record_array_fields` PROXY disjunct changes 6 of 813 corpus files.

## Pick up here — in this order

1. **THE VALUE-MODEL FRONTIER, backlog item 1b(A) — and it now has a PROVEN-SAFE PATTERN.**
   ATTEMPT #1 was rejected because the `Set[str]` retype was GLOBAL and cascaded into every
   verified caller. Increment 3 of this session did the same retype PER-CALLEE, gated on the
   opt-in `#@ sibling_concrete` marker, and it landed with corpus byte-diff 0 and three
   mirrors re-proved. **That gate is the reopening the backlog asks for.** Next consumer to
   try: `_collect_map_typed_locals` (blocked additionally by the pyval/array-int param
   split), then the `Set[str]`-returning surface listed in the backlog.
2. **`crosscheck_ir.pairwise`'s three capabilities** — (a) the `Optional[Term]` PARAM route
   is SPIKED AND WORKING (patch in scratchpad); (b) generic lifted-nested-def call
   resolution, or a bespoke `recognize_crosscheck_pairwise` beside the existing
   `recognize_crosscheck_*` family; (c) a dict value model that distinguishes an ABSENT key
   from a present `None`. Note (c) is the same shape as backlog 1b(B).
3. **The L2 dispatcher ADT redesign** — make `pyx_view` STRUCTURAL. This is the only route
   to the 137-site shadowed residue that does not spend an axiom. Large, and it touches the
   Rocq/Lean certificate; but the SCC-keyword half is already built and byte-inert (patch
   in scratchpad), so the redesign is the whole remaining cost.
4. **EXTEND THE TYPED-RECORD AST MODEL to the node classes the mutators touch — the single
   highest-leverage item left, with THREE measured consumers and a REFUTED cheaper
   alternative.** Consumers: it unblocks `_desugar_for` (already proven green under the
   unsound projector-purity version); it unblocks every `visit_*`/`_attach_*` mutator the
   census declined (a large family across Module3_Weaver and Module5_IREmitter); and it makes
   the FRAME claims of the 11 already-banked setattr-ing conversions true of the SOURCE and
   not only of the model. **DO NOT reach for a global attribute store — it was spiked
   directly on the emitted `.mlw` and is structurally impossible in Why3**: a `ref (map …)`
   store is inherently GHOST (`map.Map` is a logic type) so attribute values cannot flow into
   the non-ghost computation the bodies do with them, and an `array int` store makes
   `get_<attr>` non-pure ("depends on external variables, cannot be used as pure") and
   therefore illegal in EVERY contract clause. The horns are exclusive and exhaustive. The
   emitter ALREADY has the right machinery — `py_with_node` / `py_match_node` /
   `py_ghost_node` in the Module5 handler family, where `node.<attr>` is a native mutable
   field and the frame is a native `writes { node.<field> }`. And the cost is favourable:
   the corpus uses `setattr` in **0 of 814** files, declares exactly **1** `get_<attr>`
   projector, and only **2** contract clauses mirror-wide mention one — a MIRROR-ONLY build.
5. `pure_ast`'s residue is now CENSUSED and is the `_Unparser` family plus generators plus
   dunders. Do not re-probe it without a new capability.

## Instrument facts (re-verified this session)

1. **`why3` is NOT on the default PATH** (`/home/fabrice/.opam/framac-coq8/bin`). Without it
   `pycsl.py` errors AND EXITS 0. `export PATH=...` on every gate.
2. **`--import-path src/pycsl`** is the canonical mirror path.
3. `check-emitted-vacuity.py` is a false green without `--emit`.
4. **`.gitignore` has `*.mlw`** — `git add -A` SILENTLY SKIPS evidence files.
5. `bin/check-untrusted-emitted.py` reports 0/0/0/0 — a FALSE GREEN — with no PATH export.
6. `python3 -u` on every proof, or the log stays empty until the run ends. A `grep -c
   "Prover result"` on a running log can read 0 for 40 minutes and then jump — the log
   flushes in batches. Do not conclude "stuck" from it.
7. **A `pycsl.py` run has TWO phases and the second (non-vacuity) dominates. A FAILING run
   is much FASTER than a passing one.**
8. **BACKGROUND WATCHERS DO NOT SURVIVE YOUR TURN ENDING.** `nohup` the proof, then wait in
   the FOREGROUND with `timeout 580 bash -c 'until grep -q ALLDONE …; do sleep 25; done'`
   AND pass the Bash tool's own `timeout` parameter.
   **`scratchpad/w2/r17prove.sh <file> …`** proves a LIST of mirrors SEQUENTIALLY.
   A SECOND proof runner for a worktree is at `…/scratchpad/spikeprove.sh` (its own TMPDIR)
   — running one battery in the main tree and one in the spike worktree concurrently works
   and roughly halves the wall clock, at some per-proof slowdown.
8b. **`bin/byte-diff-sweep.sh` RUNS WITH `--no-typecheck`.** A corpus byte-diff of 0 is
    therefore NOT evidence that the corpus still TYPE-CHECKS. Measured this session: a
    receiver widening left corpus 0425 byte-clean and proof-RED. After any emitter change,
    PROVE at least the corpus files the sweep flags — and if the sweep flags none but the
    change could retype an operand, spot-prove one file that exercises it.
9. **`scratchpad/w2/sweep.sh <repo-root> <outdir>`** emits all 52 mirrors WITH L3-tc in ~35 s;
   **`keepsweep.sh`** keeps the `.mlw`. `bin/byte-diff-sweep.sh <out>` does the 814 corpus
   files in ~32 s and needs a `.venv` — in a worktree, `ln -sfn …/pycsl/.venv .venv` first.
   **RE-BASELINE the sweeps after every landed increment.**
   **A `cd` into the worktree persists for the whole compound Bash command — a `git apply`
   after a `cd` lands in the WRONG tree. It happened AGAIN this session (fourth time).**
10. **`--fun` CANNOT probe `Module5_IREmitter` at all** — whole-file or nothing.
11. **`bin/check-shadowed-selfcalls.py --emit-dir <dir> --verbose`** gives the per-method
    breakdown in seconds when you already have the emitted `.mlw` files.
12. The **Alt-Ergo pin at `pycsl.py:1318` is stale**. Keep passing
    `--provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,'` EXPLICITLY; do NOT edit the pin.
13. **`grep` MISBEHAVES on `driver-progress.log`** — the file has very long lines. Use
    `python3 -c "print('…' in open(f).read())"` to verify that file's content.
    NOTE the shell `grep` here is **ugrep**; `grep -cF '\trusted'` is the campaign's rule.
14. **A `#@`-block heredoc in a Bash `-m` commit message gets MANGLED by backtick command
    substitution.** Write long commit messages to a file or use `git commit -F -` with a
    quoted heredoc.
15. **Check `ps -eo cmd | grep -c '[p]ycsl.py'` BEFORE launching a battery, not after.**
    Note the pattern also matches the `r17prove.sh` command line itself, so a healthy single
    battery reads as 2.
16. **NEVER put a `\trusted` marker LITERAL in a mirror comment** — `count-trusted-
    directives.py` counts it as a MARKER, and a 5-marker conversion showed as 0.

## Method notes this session paid for

- **VERIFY THE MODELLING PREMISE, NOT ONLY THE GATE PREMISE.** Lesson (bz) said to check a
  recorded GATE claim against disk. This session the same failure appeared one level up: a
  recorded REOPENING CAPABILITY was precisely wrong because the record's claim about the
  MODEL (`Term` is opaque) was false in the emitted `.mlw`. Read the `.mlw`, not the note.
- **AN `elif` SPLICED INTO THE MIDDLE OF A LONG `if <gate>:` BLOCK SILENTLY TERMINATES IT**,
  so every branch below the splice starts running UNGATED. Measured as 3 changed corpus
  files and 6 TC_FAIL mirrors, and it read exactly like a value-model over-reach.
- **DETECT A DIRECTIVE BY ITS LINE PREFIX, NEVER BY SUBSTRING.** The census tool's first
  version matched PROSE mentions of the marker inside comment blocks and both invented FIVE
  false-positive wins on ALREADY-CONVERTED methods and deleted the WRONG line. Assert that
  the marker count drops by exactly one per probe.
- **A DECLINE CAN BE MADE ON SOUNDNESS AFTER THE PROOF IS ALREADY GREEN.** `_desugar_for`
  proved 270/270 and was reverted anyway. "It proves" is not the acceptance test; "does the
  model claim anything false" is (lesson (ca)).
- **THE BLOCKER IS OFTEN A GATE, NOT A MODEL.** Four of this session's six increments were
  un-gatings of machinery that already existed and was scoped to `@mutable_state` or to a
  class: the `-> Term` carrier, the for-over-collection variant, the concrete-route
  return-type allowlist, and the `Set[str]` return retype. Before scoping a new value model,
  grep for the capability and read its GATE.
- Still live: **(am)** ASSUME TWO PRODUCERS — it bit again, this time as a second producer
  of a `let rec … with` GROUP KEYWORD; **(ai)** prove sequentially; **(bl)** grep the
  emitted body for `if true then` after ANY slot-type change; **(bp)** INSTRUMENT THE
  DECISION; **(bq)** a returnless mutator is modelled as a NO-OP — it is the single largest
  source of census facades; **(bu)** the concrete-route allowlist is a serial silent floor
  (fifth time); **(bw)** a merged SCC needs a COMMON measure with rank capacity;
  **(bx)** produce a lowering at the type the CONSUMER expects; **(hh)** L3-tc passing is
  NOT a conversion criterion — now measured at 34 of 34.
