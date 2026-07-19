# emit_ir / AST-lowering conversion — hard-won lessons (2026-07 campaign)

Companion to `leaf-conversion-recognizers.md`. Distilled from converting the ENTIRE Module5 AST→IR
lowering surface (`frontend/Module5_IREmitter.py`: all `_py_expr_*`/`_py_stmt_*` handlers + `_csl_*` +
bool-recognizers, ~1176→1043) plus breaking the list-append-mutation wall. These are the techniques,
the gate discipline, the boundary-diagnosis lessons, and the traps. HEED THEM.

## 1. THE GATE — whole-file proof is authoritative; `--fun` and the monolith both lie

- **The WHOLE-FILE proof is the soundness gate** (`python3 src/pycsl/pycsl.py <mirror-file>
  --import-path src/pycsl`). NOT `--fun`. On heavy mutual-recursion VCs (stmt_ir/handler_list/etc.),
  **`--fun <method>` spuriously reports "FAILED or INCOMPLETE"** while the whole-file proof SUCCEEDS —
  the `--fun` val-stub trusting of the other ~200 methods changes the proof context. Confirmed
  repeatedly (try/match/delete/assign). If `--fun` fails, DO NOT revert — run the whole-file proof.
- **The monolithic `bin/run-self-annotation-suite.sh` WEDGES on `stmt_control_flow`/heavy mirrors under
  load** (observed 50+ min hangs, and it dirties `test-suite/corpus/*.proofs/*.aux` proof-caches).
  Do NOT use it as the per-batch gate. Use **DECOMPOSITION**: (a) the changed mirror file's whole-file
  proof SUCCESS; (b) inertness — the new machinery is gated (see §2) so only the changed mirror(s)
  differ, and EACH differing mirror proves standalone; (c) `bin/byte-diff-sweep.sh` + `diff -rq` for
  corpus byte-diff 0. This is sound because mirror files are proved independently.
- **Whole-file proof time CLIMBS as the emit_ir theory grows** (measured 545s → 843s over ~10 ctors).
  A soft ceiling: each new emit_ir ctor makes every future proof of that file slower. Budget ~10-15min
  per proof late in a campaign; batch conversions to amortize; prefer recognizers that add NO ctor.

## 2. THE GATED-EMIT_IR-CTOR PATTERN (validated — reuse for any new emit_ir ctor)

`emit_ir` is the CORE type and **real corpus files emit `type emit_ir`** (0746 etc.) — so adding a ctor
UNCONDITIONALLY breaks corpus byte-diff. Gate it: add the ctor + its `kind_of` arm INSIDE the
monolithic emit_ir type string via `+` concatenation, keeping the `with` clauses INLINE (a list-splat
that moves `with` to a new line breaks implicit-concat and fails byte-diff — caught the hard way),
guarded on the per-file signal (`_uses_stmt_ir`/`_uses_pyconst_val` — True iff the file harvested the
relevant record). `size`'s `_ -> 1` catch-all covers a flat ctor. Result: only the consuming mirror
emits it → corpus + other mirrors byte-identical. For stmt_ir (a SEPARATE gated theory block) the whole
block is gated; for emit_ir (the core type) gate the ctor inline.

## 3. BOUNDARY DIAGNOSIS — test by building; opaque abstract readers are the workhorse

**My "leave-trusted" boundary predictions were WRONG repeatedly.** Things that LOOK like walls but MODEL
FAITHFULLY under the type-safety-only contract, via an OPAQUE ABSTRACT READER/PREDICATE at the same
trust level as the certified sub-dispatchers (`_py_stmts_to_ir`, `_csl_to_ir`, `_get_mutex_invariant_ir`):

- **Custom exception construction** — `raise PyCSLSemanticError(f"...{type(x).__name__}...", stage=, code=)`
  → a real Why3 `raise` + an auto-added `raises {}` clause; the f-string/`type().__name__`/kwargs are
  DROPPED (a raise takes only the exception NAME); the raise path doesn't reach `ensures` so it proves.
  isinstance_op=0. NOT a boundary.
- **Weave-injected attributes** — `getattr(stmt, 'csl_critical_mutex', None)` (attrs the weaver adds,
  not in pure_ast `_NODE_SPEC`) → an opaque `csl_mutex_ast : ... -> iropt_str` reader. Both branches
  reachable, non-vacuous. NOT a boundary.
- **Instance-state dict membership** — `x in self._cur_func_symtab` → an opaque `symtab_mem` abstract
  bool predicate. Non-vacuous (both branches observed by the fixture). NOT a boundary.
- **getattr-with-default** — `getattr(tgt,'slice',None)` folds into the discriminant guard
  (`if is_sub tgt then IrOSome (sindex_of tgt) else IrONone`); often no recognizer needed.

**Diagnosis rule:** a runtime/stateful/reflective value that the handler only *reads* (never needs to
compute faithfully — the contract is type-safety + frame, not value-faithfulness) → model it as an
opaque abstract reader/predicate. Whether it's non-vacuous is decided by the OBSERVATIONAL fixture
(both branches reachable + evil-twin unprovable), not by the reader being concrete. **Spike the
suspected-hardest branch FIRST (Gate 0)** before building the rest of a multi-branch handler.

**GENUINE boundaries (confirmed):**
- **`isinstance(x.func, ast.Name)` on an `IrCall`** — `IrCall string emit_ir int` stores the callee as
  a func-STRING, so `Foo()` and `mod.Foo()` are indistinguishable at the ctor level; a guard that needs
  the Name-vs-Attribute-callee distinction cannot be modeled (isinstance_op forced). (`_py_stmt_raise`.)
- **String reflection of a value** — `str(v.value)` (arbitrary Constant → its repr), `.lower()`,
  `.endswith(".decode")` — the value-model / string-op wall. (`_py_expr_fstring`, `_overload_type_name`,
  `_is_decode_call`.)
- **Chain-walk giants** — `while isinstance(node, ast.Attribute): node = node.value` + `.join` +
  multi-branch. (`_py_expr_call`.) And the **class-synthesis / visitor giants** (body-walk over
  ClassDef + recursive annotation-reader + `program_ir` record-list mutation + stateful `self.*`):
  `_build_function_ir`, `visit_*`, `_emit_typeddict/namedtuple/protocol_record`.
- **Generic `Dict[str,Any]` walkers / annotation-readers** — the type-system value-model wall (census E).

## 4. VACUITY TRAP — child-list ops MUST be concrete, never abstract length-only

When a handler maps/filters/folds over a child-list (`[x.id for x in elts if isinstance(x,Name)]`,
`for v in values[1:]: acc = BinOp(acc, disp(v))`, `"|".join(...)`), the naive lowering to an ABSTRACT
`val function` with a LENGTH-ONLY content law is **VACUOUS** — an empty-result model satisfies the
length bound and vacuously satisfies the per-index `forall`, so the projected content is unobservable.
A fable review PROVED this (a driver observing a specific element goes unprovable). **`--check-vacuity`
does NOT catch it** (an assumed-but-false caller postcondition poisons the SMT context — it proved
`result=1` while returning `0`).
- **Fix:** a CONCRETE recursive `function` (`var_names_of`/`pipe_join`/`boolop_fold`/`dict_keys_of`
  compaction/existence-fold) — no opaque `val`, definitional, terminating. The filter/None-guard
  becomes a real per-element branch.
- **The load-bearing gate is an OBSERVATIONAL fixture** (a hand `.mlw` in `test-suite/corpus/
  pycsl-reference/`, `git add -f`, GROUNDED in the tool's VERBATIM emitted theory + handler body): a
  driver that constructs via the handler, reads back a SPECIFIC value/tag, proves it Valid, PLUS an
  EVIL-TWIN asserting the wrong value that MUST stay UNPROVEN. Both are mandatory; the evil-twin is what
  refutes the false-green. best-of-N matters: Alt-Ergo often proves compaction read-backs Z3 misses.

## 5. NEW VALUE SHAPES — coupling rule + the ADT encoding constraints

- **Every new WhyML value shape co-lands an AXIOM-FREE `src/formal-semantics/` certificate** (Rocq
  `Phase2*.v` + Lean `PyCSL/*.lean`): size measure, decidable-eq, ctor tag distinctness, per-field
  observability, `abs` surjectivity, + the concrete-compaction correctness section. Verify axiom-free:
  Rocq `Print Assumptions` all "Closed under the global context"; Lean `#print axioms` = standard kernel
  only (propext/Quot.sound/Classical.choice), NO 4th. **The 3-axiom ledger (`proof_axiom_allowlist.py`)
  stays 3.** Watch for ctor-name clashes across certificate sections (StrList vs strl — rename).
- **Recursive ADT encoding:** Why3's positivity checker REJECTS a recursive occurrence inside the
  abstract `seq` (`SWhile emit_ir (seq stmt_ir)` → "non strictly positive"). The library `list` TYPE
  is unbound + pulling `list.List` into scope EXPLODES the emit_ir `size_*_dec` lemmas (27-34M steps).
  Use a **bespoke MUTUAL-CONS ADT** (`stmt_list = SLNil | SLCons stmt_ir stmt_list`, the `irlist`
  precedent), disjoint from emit_ir's mutual block (one-directional reference). To materialize a `seq`
  accumulator into the cons field, a `seq_to_sl` function with `variant { Seq.length s }` + a bridge
  lemma `sl_len (seq_to_sl s) = Seq.length s`. The bridge lemma often proves ONLY via Alt-Ergo (Z3
  E-matching explodes in the big emit_ir context) — best-of-N is essential, not optional.
- **GATE 0 for a recursive ctor:** measure the size-lemma discharge at FULL theory scale with a LIVE
  recursive handler present (a single flat handler's SUCCESS is not proof) before the family build.

## 6. LIST-MUTATION-THROUGH-A-PARAMETER (the wall that unlocked the stmt family)

PyCSL modeled a passed `list` as an IMMUTABLE snapshot (`let xs = ref (snapshot xs)`; `.append` →
`Seq.snoc` on a LOCAL copy) — so a callee's append to a passed `ir_stmts` was INVISIBLE to the caller,
and a verbatim port was a FALSE GREEN (tag erased, `writes {}` vacuous frame, distinct handlers
byte-identical). Fable-adjudicated BREAKABLE + Why3-proven sound: an **`ir_stmts : ref (seq stmt_ir)`
parameter with a real `writes { ir_stmts }` frame**; `.append` → `ir_stmts := Seq.snoc !ir_stmts v` on
the PARAMETER's ref. Keyed on the shape "returns None + `#@ assigns <list-param>`" so the existing
build-and-RETURN-a-list snapshot path (and its corpus byte-diff) is untouched — two conventions coexist.
Variants built on it: **loop-append-to-OUTER** (`for x in node.<list>: ir_stmts.append(...)` → a real
`for i in 0..len` loop with invariant `0<=i<=len` + variant `len-i`, per-element snoc onto the ref),
**record-list emission** (`acc=[]; for x in node.<list>: acc.append({record})` → `ref (seq <rec>)` +
real record construction + `seq_to_*`), **seq-concat extend** (`ir_stmts.extend(body)` → `!ir_stmts ++
body` under writes). This is a FRONTEND-emitter capability: the tool must emit the loop faithfully, not
int-erase it to `Seq.snoc 0`.

## 7. WALL-ESCALATION (fable) — when cheap is drained

Use the report → INDEPENDENT fable review → impl → spike cycle (SKILL.md §4) ONLY when the cheap
frontier is drained. The fable review MUST produce an ORACLE ARTIFACT (a hand `.mlw` it proved, a
byte-diff it ran) — a prose-only "response" is a rubber stamp, reject it. Fable twice adjudicated walls
BREAKABLE that looked terminal (list-append-mutation; the ast-node-list filtered-map — breakable via
CONCRETE compaction, NOT the vacuous abstract law). But note: a wall-break that is NECESSARY but not
SUFFICIENT (each handler needs several interdependent builds) is a "deliberate multi-build campaign,
authorize-first", not a cheap-drain — don't grind it silently.

## 8. HYGIENE

- COMMIT: stage ONLY the conversion files EXPLICITLY (never `git add -A`); `git add -f` the observational
  `.mlw` fixtures (gitignored); NEVER stage `test-suite/corpus/*.proofs/`/`*.aux` (transient proof-cache)
  or `TODO`/`session.txt` (pre-existing user content).
- The mirror sync gate compares method BODIES + signatures modulo `#@`; a deliberate `-> int` model
  retype of the return annotation (vs the live `-> Dict[str,Any]`) is the accepted stub convention and
  shows as a byte-level signature diff — the structural `self-annotate-mirror-check.sh` stays green.
- Count via the precise marker: `grep -rhF '#@ \trusted' src/self-annotate/src --include='*.py' | wc -l`
  (a `wc -l` on a broader grep over-counts — reconcile discrepancies with THIS).
