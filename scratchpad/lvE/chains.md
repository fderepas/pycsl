# lvE chain census: route #327 IDENT-COLLISION (generated binder namespace) as first blocker (run #5)

Base b432460d6 (run5-int36 = main + u25 + lvA + u26 + u27 + lvC). Method = lvA / lvC's: port the VERBATIM live
body into a scratch copy of the mirror (`bin/port-one-mirror-body.py --convert [--replace]`), SIMULATE the
hygiene by renaming the colliding user names in the PORTED scratch body only (`rename.py`: NAME tokens inside the
def's line span, e.g. `_ri` -> `lve_ri`, `C` -> `C_up`), emit `--no-proof` on QUICK (`HEAVY_QUICK=1 heavy.sh
batchN.sh`), read the next blocker. Probe sources / logs: `probe/` (not committed, scratch).

## 1. Why #327 refuses instead of renaming (history)

Route #327 (gen #37, `getting-better/open-routes/route327-identifier-collision.md`) and its extension route #333
(`route333-generated-name-and-exception-collisions.md`, which added the `_rsv333` generated-namespace regex that
these 12 stubs hit) both PRICED the renaming alternative first and rejected it on BLAST RADIUS, not on soundness:

- #327: an injective encoding of every name (case-marked `N`, collision-free keyword prefix) re-emits ~1962 / 48 / 48
  (root / pyref / mirror) files; refusal moves 1 / 0 / 0.
- #333: renaming every GENERATED binder into a namespace no Python name reaches re-emits 586 / 12 / 37 files (every
  moved mirror re-OWES a whole-file proof); refusal moves 0 / 0 / 0.

No soundness reason is recorded against a renaming. Both options were "rename EVERYTHING". The lvE candidate is
different: it renames only a USER name that is refused today, so by construction it changes only programs that
#327 / #333 refuse at base. It is corpus-inert by construction, but this was not measured: no build, see §3.
Soundness obligations that a hygiene build would have to discharge. They are all about consistency; none is a known
counterexample:
(a) every occurrence must be renamed: IR `Var`, `target(s)`, `var(s)`, `formal_params`, contract nodes incl.
`\at` / `\old` / labels, `assigns` paths, loop annotations, and any name-keyed side tables (local type maps,
`_string_local_vars`-style sets). A missed site leaves a PARTIAL renaming, which is itself the collision.
(b) module-level names (`val constant`, read by every function) need a module-wide renaming, not a per-function one.
(c) the fresh name must lie outside every `_rsv333` prefix and outside the image of `whyml_ident` over Python
identifiers. Example: a character no Python identifier has. It must also pass `whyml_ident` unchanged.
(d) the inlined-callee case (#333 residual 4) must not be renamed twice.
(e) keep the refusal for the case-fold and keyword-prefix collisions (n40, n24, n09, n27, n14 ...), unless the
renaming is shown injective there too.

The emitter's own stubs do not need the hygiene. Renaming the locals in the LIVE source (`_ri` -> `ri_`, `C` ->
`cls_c` ...) removes the #327 refusal for all 13 stubs with no emitter change. Every twin is `\trusted`, so no mirror
emission moves. It is a pure refactor of live code. This is the cheaper route once link 2 is solved (below).

## 2. Chain table (link 1 = cv8's first blocker; link 2/3 measured with the rename simulated)

| stub | file | body lines | colliding names (link 1) | link 2 (after simulated hygiene) | link 3 | end state |
|---|---|---|---|---|---|---|
| `_emit_preamble_uses` | preamble | 166 | `_u` | R542 NON-CONTAINER-OPERAND: `needs` is int-erased in the mirror (`needs: int`), `sorted(needs["bounded_sizes"])` | (hand-patched `needs: Dict[str,bool]`, list dropped, scratch only) R325 opaque `str_concat` used as int | **WALL** (heterogeneous `Dict[str, Any]` needs-dict: value-model unerase) |
| `_insert_abstract_val_block` | abstract_ops | 177 | `_cc_parts _cc_q _cc_sub` | route #314: `_cc_q.format(body=...)` keyword arg of a str method discarded | (hand-patched positional, scratch only) `out.insert(...)` in-place receiver mutator, no certified lowering (cv7's known wall); further `self._abstract_ops[k] = ..`, `getattr(self, .., set())` | **WALL** (in-place list mutator on a param) |
| `_track_collection_metadata` | types | 226 | `_u_el _u_sz` | dict/set value into field `self._rebound_collections` while aliased (`_pycsl_multi_1`) | -- | **WALL** (collection alias model) |
| `apply_composition` | ir_resolve | 259 | `C`/`c`, `M`/`m` (case fold) | nested closure `walk` lift unfaithful (reads `written` from the enclosing scope) | -- | **WALL** (closure lift, known cost-scale) |
| `_handle_array_set_stmt` | statements | 340 | `_fk _idx_ir` | and/or used as a VALUE on non-bool operands (cap-boolop-value) | -- | **WALL** |
| `_handle_attribute_expr` | expressions | 326 | `_ri` | route #301: nested tuple target in the generator `next(i for i, (fn, _w) in enumerate(_flds) if ..)` | -- | **WALL** |
| `_emit_body_code` | statements | 710 | `_ri _union_predecl` | dict/set value into field `self._current_append_targets` while aliased | -- | **WALL** (alias model) |
| `_handle_call_expr` | expressions | 1611 | `_ci _ri` | mutating a collection aliased by a tuple-unpacking assignment (14 names) | -- | **WALL** (alias model) |
| `_handle_subscript` | expressions | 787 | `_idx_ir` | `_w170.pop(...)` in-place receiver mutator | -- | **WALL** |
| `_handle_binop` | expressions | 2240 | 13 `_r230_*` / `_r251_*` | route #498: identity test on a freshly computed value (`None`-built operand) | -- | **WALL** (cap-identity-vs-literal) |
| `visit_ClassDef` | Module5_IREmitter | 641 | `_class_ssc _class_tsc` | mutating a collection aliased by a tuple-unpacking assignment (`fields`, `init_body` ...) | -- | **WALL** (alias model) |
| `_build_function_ir` | Module5_IREmitter | 1310 | 7 `_r230_*` | route #498: identity test on a loop-bound local `_r526_n` | -- | **WALL** (cap-identity-vs-literal) |
| `Module3_Weaver.process` | Module3_Weaver | 2218 | 19 `_cc_*` + 27 `_lf_*` | route #504: identity test on a FIELD value (`.value: CSLNode`) | -- | **WALL** (cap-identity-vs-literal) |

## 3. Set cover / decision

No stub reaches TC-OK with the hygiene alone. All 13 chains stop at link 2 on an existing, known capability gap:
- identity tests, 3 stubs (cap-identity-vs-literal / #498 / #504);
- collection alias / in-place mutator models, 6 stubs (`_track_collection_metadata`, `_emit_body_code`,
  `_handle_call_expr`, `visit_ClassDef`, `_handle_subscript` `.pop`, and `_insert_abstract_val_block` `.insert` at
  link 3);
- the remaining four, one each: and/or value (cap-boolop-value), nested tuple target (#301), closure lift, and the
  int-erased `needs` dict.
The two smallest bodies (preamble, abstract_ops) were pushed one link further by hand, scratch only, and wall again
on a known gap. The brief's STOP rule applies (fewer than 2 stubs convert cleanly). Nothing was built: no emitter
change, no conversion, no witnesses, no sweeps, no whole-file proof owed.

Ranking hint for the driver: #327 is not the binding constraint for any of these 13 stubs. When one of the link-2
capabilities lands (the alias model covers 6), clear #327 for its stubs by renaming the colliding locals in the LIVE
source (`\trusted` twins, 0 mirror movers, 0 corpus movers). That is cheaper and safer than building the IR hygiene.
