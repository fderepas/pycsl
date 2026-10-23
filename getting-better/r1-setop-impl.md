# r1-setop-impl.md — the string-keyed set-op lowering pass (item-7 R1, user-funded 18h)

Goal: make `Set[str]` lower to a STRING-keyed map (`map string (option int)`) everywhere — param,
field, local, set-ops — so `.add(str)`/`x in s`/`|`/`.copy()`/`.discard` typecheck and prove
faithfully. Fixes a real all-users faithfulness bug (currently `Set[str]` is int-keyed via
`str_hash_op`, an erasure), de-vacuifies `_emit_new_ghost_ref`, and unblocks item-2's F4.

## Banked seed (item-7 spike, PROVEN standalone — `def add_it(s: Set[str], x): s.add(x)` L3-tc ✓ + proves)
4 emitter edits: (a) `functions.py::_emit_param` set branch consults `_dict_key_types` (was hard-coded
`map int (option int)`); (b)+(c) `_build_method_param_types_map` + `_build_method_param_whyml_types_by_name`
pin `dict_key_types[arg]="string"` from a `Set[str]` annotation via `_m5_get_set_elem_type`; (d) Module5
`_build_function_symbol_table` pins it from the annotation.

## Measured cascade (item-7 boundary — each step revealed the next; this is the work)
1. **set-union `|`** (`expressions.py` L3660) `str_hash_op`-hashes the string element — needs a raw
   string-key branch, incl. the `<set>.copy()` LEFT-operand variant.
2. **`#@ requires_method` grammar** can't parse `Set[str]` (`Module2_Parser`) — falls back to `int`
   (worse). Extend the requires_method param-type grammar for `Set[str]`.
3. **membership `in` + `.add`/`.discard`** write sites all `str_hash_op`-hash — same raw-key fix.
4. **mirror inconsistent annotations** — 60 `local_refs: Set[str]` vs 15 `local_refs: int` vs 1 bare
   `set`. Reconcile to `Set[str]` where the live type is a str-name set.
5. **cross-file self-method bridges** default the callee set param to `map int` — infer string-key.
6. **de-vacuify `_emit_new_ghost_ref`**: `_seed_mutated_collection_params` (`functions.py` L4143)
   EXCLUDES methods from by-ref promotion, so `.add(target)` emits `()` → `target` erased. Lift the
   method exclusion (guardedly) so the ghost-ref add is caller-visible → removes it from KNOWN_ERASURES.

## Discipline — INCREMENTAL, byte-diff/M1-gated (this touches shared emission = corpus risk)
Each increment its own gate battery. Corpus byte-diff is the make-or-break: a `Set[str]` corpus program
that was int-keyed-and-WRONG will now emit differently — that is an **M1 SANCTIONED RESET** (§10.10) ONLY
if the diff is EXACTLY the string-key correction AND every affected program still PROVES. Any corpus
program that BREAKS (relied on the int-keyed lowering) is a STOP-and-report, not a force. Assert the
emitted population (786) on both sides (lesson k). Whole-file proofs uncapped (driver). Ledger 3.
Count MUST NOT rise; the payoff is de-vacuify (`_emit_new_ghost_ref` out of KNOWN_ERASURES) + the
faithfulness fix + any stubs a string-keyed-set census unblocks.

## Increment order (spike-gated; refutation-exit per increment)
- **I0 SPIKE (re-verify the seed):** reproduce `add_it` proving with the 4-edit seed. If it no longer
  proves, STOP — the seed regressed.
- **I1 — Set[str] type-plane (the seed, byte-inert):** param/field/local `Set[str]` → `map string
  (option int)`, gated on the `str` element type (Set[int] stays int-keyed). Byte-diff: any corpus
  Set[str] program changes are the M1 correction (verify re-proof); Set[int] unchanged.
- **I2 — set-op lowering string-key-aware:** union `|` (+`.copy()` left), membership `in`, `.add`,
  `.discard` — raw string key, retire `str_hash_op` for str-sets. Byte-diff/M1 per op.
- **I3 — requires_method grammar** for `Set[str]` (Module2_Parser). Byte-inert on corpus (no corpus
  program uses cross-mixin requires_method with a set param); fixes the mirror fallback.
- **I4 — mirror annotation reconcile** (`local_refs`/`declared_refs` → consistent `Set[str]`) +
  cross-file bridge string-key inference. Mirror-only where possible (byte-inert).
- **I5 — de-vacuify `_emit_new_ghost_ref`:** lift the method by-ref-promotion exclusion (guarded);
  confirm `.add(target)` is caller-visible, `target` referenced, remove from KNOWN_ERASURES.
- **I6 — census:** any other `\trusted` stubs now convertible via string-keyed sets? Convert (count DOWN).

Refutation exit at any increment that cascades unboundably or breaks a corpus program unfixably →
record the exact blocker + how far it got, revert THAT increment clean, keep the landed ones.

## RESULTS — run 1 (2026-07-24): I0 ✓, I1 LANDED (352576ae), I2 LANDED (0e2c5ab9). count 942, drift 2, ledger 3.

**I0 SPIKE — seed reproduces.** `def add_it(s: Set[str], x: str): s.add(x)` `#@ ensures x in s` →
`ref (map string (option int))`, L3-tc ✓, proof **Valid / SUCCESS**. Ground-truth finding: the set-ops
were ALREADY string-key-aware — Module5's usage-based κ inference (`_tag_str_keyed`, on `.add`/membership
with a provably-`str` key) tags the param κ=string, and the `.add`/membership handlers (cleared-hash S5)
already emit the RAW string key. The ONLY bug was the TYPE PLANE (`_emit_param` hard-coded `map int`), a
`map int` vs raw-string-key mismatch. So I1 = ONE edit (`_emit_param`), not four.

**I1 LANDED (byte-inert, fixture 0940).** `_emit_param` set branch consults `_dict_key_types`;
**GATED ON `_mut_coll`** → only a BY-REF set param → `ref (map string (option int))`.
- Seed edits (b),(c),(d) REFUTED:
  - **(d) annotation-pin BREAKS 0884** — the `\nothing` frame-negative's `acc.add(node["target"])` adds an
    `Any`-erased (int) value; pinning κ=string from the `Set[str]` annotation would put an `int` into a
    `map string` → 0884 fails to typecheck instead of staying unproven. Usage-inference (only tags a
    provably-`str` key) is the correct, safe signal; the annotation over-approximates.
  - **`_mut_coll` gate is REQUIRED, not optional.** A METHOD's set param is excluded from by-ref promotion
    (`_seed_mutated_collection_params` skips methods), so its `.add` lowers to the sound `()` NO-OP (this is
    exactly why `_emit_new_ghost_ref` is the I5 de-vacuify target). But usage-inference STILL tags its params
    κ=string. Un-gated, `_emit_param` emitted `map string` for `_emit_new_ghost_ref`'s `local_refs`/`declared_refs`,
    which forward to the sibling `val` bridge `_stmts_to_whyml` (still `map int`) → **statements.py whole-file
    L3-tc: base GREEN → head RED** (measured WITH `--import-path`; the standalone run masks this behind a
    missing-import artifact). Gating on `_mut_coll` keeps method set params `map int` → statements.py stays green.
  - (b),(c) [cross-method param maps] dropped: a method set-param's abstract `val` (map string) would then
    mismatch its own `let` definition (map int, `_mut_coll`-gated) — same coupling.
- **Result: fully byte-inert (corpus 786/786 diff 0, mirror 52/52 diff 0).** The by-ref-`Set[str]` capability
  has no existing corpus/mirror consumer (all corpus set params are `Set[int]` or `Any`-erased; mirror set
  params are method params) → witnessed by fixture 0940 (string twin of 0833).

**I2 LANDED (byte-inert, fixture 0941).** Real, all-users bug (measured): a `Set[str]` FIELD is `map string`
(field_key_types), its `.add`/membership use the raw key, but set-UNION `self.s | {x}` `str_hash_op`-hashed
the element (`int`) → type error indexing the `map string` field. Fix: `_set_union_left_is_strfield` gates the
raw-string union key on the left operand being a κ=string dict/set FIELD; a Var (method set param/local, `map
int`) keeps `str_hash_op` (byte-identical: mirror `local_refs | {target}` / `declared_refs.copy() | {target}`).
Membership/`.add`/`.discard` needed NO change (already raw-string, S5). Fixture 0941 (union presence + DISTINCT
"c" absence — needs the injective key str_hash can't give) proves Valid; anti-facade mutation test PASS.

## RESULTS — run 2 (2026-07-24): I3 LANDED. count 942, drift 2, ledger 3.

**I3 — parametric-`Set[str]` lowering in a cross-mixin `requires_method` sig. LANDED, byte-inert.**
GROUND-TRUTH CORRECTION: the Module2_Parser GRAMMAR **already parses `Set[str]` fine** (spike:
`_ContractParser._parse_depends_method` round-trips `(self, val_ir: ExprIR, local_refs: Set[str]) -> str`
verbatim, brackets intact; even `Dict[str, int]` parses). The "falls back to int" is NOT in the parser —
it is in the TYPE-LOWERING consumer `_symtype_to_whyml` (`functions.py`), which had no branch for the
bracketed form and hit the `int` default (WORSE than bare `set`→`map int`). Measured directly: flipping
the mirror annotation to `Set[str]` emitted `val self__seq_operand_2 (x0: emit_ir) (x1: int)` (the bug).
- **Fix (one function, LIVE + mirror):** `_symtype_to_whyml` recognizes `Set[str]`/`FrozenSet[str]` →
  `map string (option int)` and `Set[int]`/`FrozenSet[int]`/`Set`/`FrozenSet` → `map int (option int)`,
  by simple string equality (identical shape to the existing `symtype in ("set","dict","frozenset")`
  branch — trivially provable, no string-parsing). NO Module2_Parser change needed.
- **Spike confirms capability:** with the branch, flipping the annotation to `Set[str]` emits
  `val self__seq_operand_2 (x0: emit_ir) (x1: map string (option int))` (was `int`). Annotation kept `set`.
- **Byte-inert (verified, not assumed):** corpus byte-diff **0** (population 788/788 both sides, detached-
  HEAD worktree). No `Set[`/`FrozenSet[` param appears in ANY mixin sig (mirror or LIVE) → the new branches
  are unreachable for every current emission. Mirror `functions.py` (the changed converted body) whole-file
  proof **SUCCESS, 0 unproven**; mirror-check 52/52; vacuity exit 0; count 942; drift 2; no axiom; allowlist
  untouched.
- **I3 is the type-recognition PREREQUISITE for I4** (the fixpoint will flip the annotation to `Set[str]` and
  needs this branch). It is a correct latent-bug fix on its own (the `int` fallback was wrong).

## I4 — CROSS-METHOD κ=string BRIDGE FIXPOINT: **CERTIFIED-BOUNDARY (SESSION-SCALE/cyclic/unsound-signal). NOT built.**

Spiked the fixpoint FIRST (lesson q) — MEASURED the `local_refs`/`declared_refs` cluster before any build.
Three INDEPENDENT walls, each individually sufficient to refuse the build:

1. **Size + cyclicity (not a localizable cluster).** `local_refs`/`declared_refs` is the AMBIENT "set of
   local ghost-ref names" threaded through **44 distinct methods** (LIVE statements.py + expressions.py),
   plus the mirror threads it through stmt_control_flow.py and functions.py (`_build_param_list`) — 4 files.
   **81 distinct forwarding call sites** pass it to siblings. The graph is MUTUALLY RECURSIVE: `_stmts_to_whyml`
   (stmt) → `_expr_to_whyml`/`_e` → `_handle_*_expr` → nested `_stmts_to_whyml`. `_emit_new_ghost_ref` (the I5
   target) → `_stmts_to_whyml` → the ENTIRE emission recursion. There is no small cut; the fixpoint IS the
   whole expr↔stmt pipeline.

2. **No CONSISTENT κ=string signal exists with current machinery (the decisive wall).** The SAFE signal is
   Module5 usage-inference (`_dict_key_types` tags a param κ=string ONLY when THAT method's OWN body has a
   provably-`str` `.add`/membership). But the 81 forwarding sites just PASS `local_refs` through with no local
   str `.add` → usage-inference does NOT tag them → they stay `map int`. The UNSOUND alternative
   (annotation-pin κ=string from a `Set[str]` annotation) was already REFUTED at I1 — it breaks 0884 (an
   `Any`-erased value `.add`ed into a `map string` fails to typecheck). WORSE: `statements.py:793` does
   `local_refs.add(st)` where `st` is a STATEMENT-IR node, not a string — so `local_refs` is not even
   semantically a string-set on every path; κ=string is ACTIVELY WRONG there. So no uniform, sound κ=string
   assignment across the cluster exists; the fixpoint has no consistent solution.

3. **`_mut_coll` no-op-model collision (I5's own precondition).** `_emit_new_ghost_ref` does
   `local_refs.add(target)` / `declared_refs.add(target)` which today emit `()` NO-OPS (method excluded from
   by-ref promotion → `_mut_coll` False → `target` erased = the KNOWN_ERASURE). Making them caller-visible
   (I5) requires LIFTING the method by-ref exclusion — but that turns the ~7 `.add` sites into real
   `map_update_some` writes and forces by-ref (`ref (map …)` + `writes {p}`) promotion to propagate
   TRANSITIVELY through the cyclic 44-method graph (the `_build_func_mutated_collection_params` fixpoint,
   currently GATED to standalone functions with methods explicitly excluded PRECISELY to avoid this cascade).

**Verdict → keep I1+I2+I3; do NOT build I4; STOP (no grind).** I3 (the type-recognition prerequisite) is the
only part of the κ=string chain that lands cleanly and byte-inert. **I5's de-vacuify of `_emit_new_ghost_ref`
is UNREACHABLE without I4** — `_emit_new_ghost_ref` STAYS in `check-emitted-vacuity.py` KNOWN_ERASURES (its
`target` erasure is a true consequence of the sound method-`.add`-is-`()` no-op model, not a facade). I6 census
not attempted (depends on I4). R1 final = I1 (Set[str] type-plane) + I2 (string-key set-union) + I3
(parametric-Set[str] requires_method lowering) = the faithfulness fix; de-vacuify deferred behind this fixpoint.

## I6 — census RESULT (2026-07-24): **ZERO conversions.** count 942, drift 2, ledger 3. R1 CLOSED.

Measure-before-build census (§10.1) over the genuinely-new I1/I2/I3 unblock surface (Set[str] **FIELD**
str-key + str-field union `<field> | {x}` + requires_method Set[str] sig — NOT method Set[str] params,
which I4 left `map int`). Coarse "131 Set[str]-touching stubs" refined by cross-referencing each `\trusted`
stub's LIVE body against the actual Set[str] FIELD ops.

**Refined candidate count: 19** `\trusted` stubs whose live body does a Set[str]-field op (`in`/`.add`/
`.discard`/`|`/`.copy()`). Per-candidate verdict — **0 convertible:**

1. **17 are field membership/`.add`/`.discard` (NOT newly unblocked).** I2 established these already used the
   raw string key (S5) pre-R1 — I2 changed nothing for them; only str-field UNION was fixed. So they were
   never blocked by the string-key bug. Empirically spiked the cleanest one, `_resolve_effective_ghost_type`
   (types.py, `TypeInferenceMixin`, all-`str` params, reads 4 ghost `Set[str]` fields): ported verbatim →
   `--no-proof --keep-mlw` → membership emits `contains_check (str_hash_op target)
   (getattr_typeinferencemixin self 732187999)` — an **int-hashed OPAQUE CROSS-MIXIN self-getattr**, NOT the
   fixed string-keyed map. STRUCTURAL ROOT: every `Set[str]` field (`_ghost_*_vars`, `_dict_locals`, …) is
   declared in `functions.py`/`Module6_WhyMLTranspiler.py`'s `__init__`, but these stubs live in OTHER mixins
   (types.py/statements.py/expressions.py/preamble.py) where the field is an unrecognized cross-mixin
   getattr → I2's `field_key_types` κ=string recognition NEVER fires. Plus each carries independent walls
   (here: `_ghost_tuple_vars[target]` Dict[str,int] subscript + `f"tuple{…}"` — the actual L3-tc error).
   Reverted clean.
2. **2 are set-field "union" — but the WRONG shape.** `_reset_function_state` (functions.py, 290L):
   `self._dict_locals |= self._mutated_collection_params` — augmented union of two SET FIELDS, not the
   I2-fixed `<str-field> | {x}` single-element-literal union. `_emit_type_decls` (preamble.py, 540L):
   `self._ambiguous_fields |= (_rec_fields & _local_names)` — set-INTERSECTION union, further still from the
   fixed shape. Both are GIANT multi-blocker methods (getattr reflection, Dict[str,Any] IR reads throughout);
   the `|=` is one incidental line among hundreds. Not consumers of the new capability; not convertible.
3. **requires_method Set[str] sig (I3): zero consumers.** No mixin sig (mirror or live) has a `Set[`/
   `FrozenSet[` param (re-confirmed) — I3's branch is a correct latent-bug fix with no converting stub.

**Verdict.** A well-evidenced ZERO, exactly as the honest expectation predicted. The string-key fix's reach
is FIELDS-declared-in-the-owning-mixin only; the Set[str]-touching stubs all sit in sibling mixins (opaque
cross-mixin getattr, κ=string unrecognized) and/or carry unrelated value-model walls. **R1 CLOSES: I1
(Set[str] type-plane) + I2 (string-key set-union) + I3 (parametric Set[str] requires_method lowering) = the
faithfulness fix, count-neutral; I4 CERTIFIED-BOUNDARY; I5 de-vacuify unreachable behind I4; I6 no count
movement.** No stub converted, tree clean, count 942, drift 2, ledger 3.

## RESULTS — run 3 (2026-07-24): I4 REOPENED + BUILT. count 942 → **941** (1 conversion). drift 2, ledger 3.

The driver reopened I4 (cross-mixin field-key propagation) as a Full-authorized COST/SCALE item.
**GATE S spike PASSED** (branch: build the reachable subset). The build is NOT the session-scale
`local_refs`/`declared_refs` fixpoint I4 originally scoped — that stays CERTIFIED-BOUNDARY. The
reachable cross-mixin case is realized **MIRROR-ONLY, no src/pycsl edit**:

- **The propagation mechanism ALREADY EXISTS.** `_self_field_dict_kappa` (expressions.py) reads
  `field_key_types` from `_record_types[self._current_self_type]`, and the membership handler
  (expressions.py L985) consults it. A cross-mixin field lowers string-keyed as soon as the SIBLING
  mixin class DECLARES it — the exact pattern the mirror already uses for `_array_locals`/`_dict_locals`
  (`_array_locals: Set[str] = None`). I6 missed this: it ported the body WITHOUT the class annotations,
  so the field stayed an opaque `getattr_typeinferencemixin self <hash>` (int-hash, vacuous).
- **I6's "f-string-of-int wall" does NOT exist.** `f"tuple{self._ghost_tuple_vars[target]}"` lowers
  faithfully to `str_concat_op "tuple" (int_to_string (Map.get self._ghost_tuple_vars target …))`.
  `int_to_string` is a `val` abstract op (uninterpreted, ledger-neutral), already used across the mirror.

**CONVERTED: `_resolve_effective_ghost_type` (types.py, `TypeInferenceMixin`).** Added five class-level
annotations (`_ghost_{list,set,dict,string}_vars: Set[str]`, `_ghost_tuple_vars: Dict[str,int]`) +
ported the body VERBATIM. Emission: every membership `target in self._ghost_*_vars` →
`match Map.get (self._ghost_*_vars) (target) with Some _ -> true | None -> false end` (RAW string key,
non-vacuous); all three params referenced. GATES (fresh): `--fun` SUCCESS; whole-file `types.py` proof
SUCCESS 0-unproven (uncapped, ~4min); mirror-check 52/52; vacuity `--emit` exit 0 (no new erasure);
sync drift 2 (unchanged — verbatim port, the 2 known residuals only); corpus byte-inert (mirror-only);
ledger 3. **commit ef753230.**

**REACHABLE SUBSET = 1 of 19.** The other 18 carry walls ORTHOGONAL to the mixin boundary (so the
propagation alone does not free them) — classify each `[CORRECTNESS]`:
- `_expr_to_whyml_string_ctx` (expressions.py) — recursive `Dict[str,Any]` expr-walker + `_expr_to_whyml`
  sibling recursion (generic-Any tree-transform wall, §10.3).
- `_field_type_for`/`_field_type_of`/`_call_return_whyml_type` (types.py) — `_record_types.values()`
  `Dict[str,Any]` iteration + nested `.get("field_types",{}).get(field)` reads, plus `rpartition(".")`/
  `.lower()` string ops. The Dict[str,Any] `.values()` walker wall + runtime-string-ops wall.
- `_maybe_emit_no_exception_assert`/`_wrap_call_with_callee_raises_assert` (Module6_WhyMLTranspiler.py) —
  in-body `from exception_model import …`, `.format(*operands)`, list-of-dict `raises` iteration, sibling
  `_render_callee_condition`.
- `_emit_uncited_axiom_func_decls` (preamble.py) — `.split()`, `List[str]` accumulate/return, dict iter.
- `.add`/`.discard` writers (`_handle_ghost_assign_stmt` 97L, `_reset_function_state` 290L, stmt_control_flow
  `_pyast_stmt_locals`/`_tparam_locals` writers) — giant handlers needing real (non-`\nothing`) frames.

**Verdict.** SPIKE PASSED for the 1 clean stub (the mixin boundary WAS its only blocker); the remaining 18
are `[CORRECTNESS]` value-model boundaries (Dict[str,Any] walker / string-op / mutator-frame), not the
`[COST/SCALE]` mixin boundary. R1 I4 partially opened: the cross-mixin field-key recognition is a real,
byte-inert, count-moving capability — but its reach is stubs whose ONLY wall is the missing field
declaration, and there is exactly one such stub. count 941, drift 2, ledger 3.

### Backlog (what an authorized I4 build would need, in order)
- A SOUND cluster-wide κ inference that tags a FORWARDED param κ=string from the callee's tagged slot
  (propagate κ backward across the 81 call edges), REPLACING annotation-pinning — must handle the
  `local_refs.add(st)` non-string path (either prove those paths never reach a string-keyed consumer, or
  split `local_refs` into a string-set vs a stmt-holder). Session-scale, new inference pass.
- Then lift I1's `_mut_coll` gate for the now-consistent cluster AND extend
  `_build_func_mutated_collection_params` to promote method params transitively (drop the `kind == "method"`
  exclusion) without breaking the abstract-`val`/`let` agreement — a second fixpoint over the same cyclic graph.
- Only then is I5 (`_emit_new_ghost_ref` de-vacuify) reachable.

## BLOCKERS carried forward (for I3–I6)
- **I4 (cross-method κ=string bridge fixpoint) is a PREREQUISITE, not a follow-on.** I1's `_mut_coll` gate is a
  WORKAROUND: a method's `Set[str]` param cannot become `map string` until every sibling `val` bridge it is
  forwarded to (`_stmts_to_whyml`, …) also becomes `map string`, propagated as a FIXPOINT over the self-method
  call graph (the `_build_func_mutated_collection_params` shape). Until then, method set params stay `map int`
  and the de-vacuify (I5) of `_emit_new_ghost_ref` (whose `.add` is a no-op precisely because it is a non-by-ref
  method param) is UNREACHABLE — I5 depends on I4 lifting the method by-ref exclusion AND the bridge fixpoint.
- **I2 residual:** `.copy()`-of-a-string-FIELD union (`self.s.copy() | {x}`) is blocked upstream on `.copy()`
  field-read modeling (`get_s self` mistypes independently of the string key) — NOT a string-key gap.
- **A by-ref `Set[str]` param union `| {x}`** is unreachable: the union branch is `@mutable_state`-gated and
  standalone functions (where by-ref params live) are not `@mutable_state`. Needs I5 (method by-ref promotion).
