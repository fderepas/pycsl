# lvI (run #5, batch D): census sec. 1 conversions + sec. 2 emitter rows

Base run5-int40 693e20184. Census: getting-better/run5-hot-chain-census.md (e9d51d13a), probes scratchpad/cv10.

## Conversions

### ExpressionEmissionMixin._e (expressions.py)
- mirror def `ir: Dict` -> `ir: "ExprIR"` [T]; LIVE + mirror body
  `_sub: Dict[str, str] = {}` / `return self._expr_to_whyml(ir, lr, False, _sub)`.
- Behaviour identity: every `subst` consumer in src/pycsl is in module6_whyml/expressions.py (the
  name occurs nowhere else but Transpiler's own local), and reads it only by truthiness
  (`if subst and ..`, `subst.get(..) if subst else ..`), `subst or {}` / `dict(subst or {})`, or
  forwards it to another expressions.py method with the same discipline; 0 `subst is None` tests.
  `invariant_ctx=False` is the default. A fresh `{}` per call: no aliasing.
- Honesty: emitted body reads `ir`, `lr` (one-line delegation to the `_expr_to_whyml` val).

### StatementEmissionMixin._resolve_dotted_signature (statements.py declaration)
- expressions.py trusted definition retyped `-> Tuple[str, List[str], int, int]` [T];
  statements.py stub `\trusted` -> `#@ declared_in module6_whyml/expressions.py::ExpressionEmissionMixin._resolve_dotted_signature`;
  KNOWN_NONCONFORMING / KNOWN_FAILURES entries dropped (FAIL_RATCHET 5 -> 4).
- check-declaration-conformance: OK, 22/26 conform; `declared_in` 20 -> 21 (all 21 conform).

### ExpressionEmissionMixin._emit_bitwise_or_power (expressions.py): REFUSED (reverted, stays `\trusted`)
- Applied as the census specified (live if-chains for `_BITWISE_FOLD_OPS` / `_BITWISE_FN_NAMES`,
  `raise KeyError(op_char)` default, mirror port, def retype `expr: Dict[str, Any]`): TC-OK, but
  `--fun expressionemissionmixin___emit_bitwise_or_power` (fun/bw1.log): 1 goal Timeout, the route #259
  precondition `y >= 0` of `py_pow !_fa !_fb` in the constant-FOLD arm. The census's "honesty residue" is
  exactly what this goal needs: the guard `not (op_char == "**" and right_ir["value"] < 0)` compares an
  ERASED value (the child dict read is `Dict[str, Any]`, route #251: `pycsl_py_lt` with no order law) and
  `_fb` is a second, non-deterministic `subscript_get` read. Equivalent rewrites tried: `elif op_char ==
  "**" and _fb >= 0` (still `pycsl_py_ge`, `_fb` is in route #249/#251's erased set), `_fa: int` / `_fb: int`
  annotations (unchanged: the erased judgement follows the source, not the annotation). The only remaining
  route, `int(right_ir["value"])`, is behaviour-identical only if no IR `Number` node ever carries a bool
  (`str(True & True)` is "True", `str(int(True) & int(True))` is "1"): not provable here -> REFUSED rather
  than approximated. Capability needed: an int view of the IR `Number` payload under the `type == "Number"`
  + `isinstance(.., int)` guard (the IR-node value seam).

### StatementEmissionMixin._handle_augassign_stmt (statements.py)
- LIVE: 4 value-position `x or d` -> `x if x else d` (x = `getattr(self, "_formal_params", [])`,
  `getattr(self, "_r249_scope", None)`: plain instance attributes, no property / __getattr__ in
  module6_whyml or the Transpiler, so the double read is the same value); `op_fn: str` annotation.
  Mirror ported verbatim.

## Emitter rows (sec. 2)

### Comment.__init__ (pure_ast): emitter defect FIXED + converted
- Defect (statements.py `_handle_fieldassign_stmt`, live + its VERIFIED mirror twin, re-ported
  verbatim): the record-store arm tested `field in self._all_record_fields`, a NAME test. Once
  `Comment.__init__` is ported, record `comment` declares `lineno` / `col_offset`, and every pure_ast
  location stamp on a NON-record object took the record store: `tup.lineno <- ..` on an emit_ir local
  (`_subscript_list`, ...), `node.lineno <- ..` on the int-erased `node` of `_Parser._fin_pos` -> L3-tc
  (Why3 resolves the label to `comment`). The census saw only the first shape; the second appeared
  after fixing it.
- Fix (inline, no def): under the existing pure_ast gate `_uses_pyast_parser()`, a store to one of the
  four ASDL location attributes on `obj != "self"` that is NOT a known record variable (`_rec_lower ==
  ""`: not in `_current_record_var_classes`) skips the record arm and keeps the non-record lowering below
  (emit_ir local -> the unit no-op; anything else -> `setattr_3`, which `writes { _pyobj_state }`) --
  exactly the base lowering of a file with no record field of that name. `self` and record-typed
  variables keep the record store. Soundness: no new modelling, the record store is just not chosen for
  a value that is not a record (it was ill-typed, i.e. fail-closed); corpus-inert by the gate.
- Port: body verbatim; [T] def `(self, lineno: int, col_offset: int, text: str, own_line: bool, indent:
  int)`. As for the verified `_Tok.__init__`, a record `__init__` emits NO WhyML function (it is the
  record's field derivation): no own goal. Emission effect (mirror diff, 20 lines): `type comment = int`
  -> `{ mutable lineno: int; mutable col_offset: int; mutable comment_text: string; mutable own_line:
  int; mutable indent: int }`, and the VERIFIED `Comment.__repr__` now reads the real fields
  (`self.lineno`, `self.own_line`, `self.indent`, `str_repr_op self.comment_text`) instead of 4 opaque
  `getattr_comment self <hash>` reads. Honesty: fully input-reading (5 field stores).
- Gate: `--fun` is refused on pure_ast (lvD); `comment____repr__'vc` proved directly in the full emitted
  module (sw/mir_cand/frontend__pure_ast.mlw): 6/6 split goals Valid, Alt-Ergo 2.6.3 AND Z3 4.13.3
  (fun/repr1.log). `--fun statementemissionmixin___handle_fieldassign_stmt` (re-ported twin, st tree):
  3820/3820 Valid (3714 own sub-goals), rc 0, 100 min (fun/fa1.log). Emission of the new guard reads
  `field`, `obj`, `_rec_lower`.
- Witnesses: 9100 (PASS), 9101 / 9102 (FAIL). Base: all three FAIL at L3-tc (`node.lineno <- 3`: int vs
  pos). Candidate: 9100 PASS; 9101 (`\result == a`, the elided-store claim) and 9102 (`a + 3`) FAIL on
  `restamp`'s postcondition only.

### StatementEmissionMixin._expr_to_whyml (declaration): REFUSED
- The fill is `{"string": '""', "real": "0.0"}.get(_pwt, "0")` (expressions.py `_handle_dotted_call`
  self-call default fill, and `_handle_call_expr`): a `None` default on a map-typed param gets `0`.
  The model has NO None for a map-typed `Optional[Dict]` slot: an explicit `f(3, None)` lowers
  `pycsl_none` (int) and fails L3-tc too, and so does `subst is None` / `subst == {}` / `str(subst)` in
  the callee (nd/nd1, nd4, nd6). A fill would have to put a real dict (the empty map) where Python has
  None, i.e. "None == empty", which is not Python (`len` / `in` / `.get` / iteration raise on None).
  Measured with the fill simulated in a scratch emitter (st2: map-typed param -> `(const None)`), each
  probe also at base: `is None` (nd1), `== {}` (nd4), `str(subst)` (nd6), `len` / `.get` / iteration under
  `try/except` (nd7 / nd8 / nd9): ALL fail closed (L3-tc) at both; `isinstance(subst, dict)` (nd5) is
  opaque (g's claim not proved). Under `#@ no_exception` the None-unsafe ops are refused from the
  annotation (route #441 / R527: nd2 / nd3). So no unsoundness was measured; the refusal is on the
  modelling ground alone: the fill would put a value Python does not have into the slot, and its safety
  rests on every None-observing channel staying fail-closed, which nothing gates. Status quo `0` is
  fail-closed. Needs an Optional-map representation (option (map ..)), not a small emitter fix.

## Gate record (candidate = run5-lvI working tree, base 693e20184)
| gate | result |
|---|---|
| `--fun expressionemissionmixin___e` | 226/226 Valid (33 own sub-goals), rc 0 (fun/e1.log) |
| `--fun statementemissionmixin___handle_augassign_stmt` | first run 4362/4362 Valid (4144 own), rc 0, 88 min (fun/aug1.log); RE-RUN on the final tree (after the shadowed-selfcall opt-ins): 4371/4371 Valid (4153 own), rc 0, 90 min (fun/aug2.log) |
| `--fun statementemissionmixin___handle_fieldassign_stmt` (re-ported VERIFIED twin) | 3820/3820 Valid (3714 own), rc 0, 100 min (fun/fa1.log) |
| `comment____repr__'vc` (pure_ast, full emitted module; `--fun` refused on pure_ast) | 6/6 Valid, Alt-Ergo 2.6.3 and Z3 4.13.3 (fun/repr1.log) |
| Transpiler `module6_whymltranspiler___e_refines_statementemissionmixin` (binder type moved) | Valid, Z3 (fun/tr_e2.log) |
| `--fun expressionemissionmixin___emit_bitwise_or_power` | 1 Timeout (route #259 `py_pow` pre) -> REFUSED, reverted (fun/bw1.log) |
| mutations (frame: a hidden write of a field outside the `assigns`) | `_e` (`self._scope_dyn_exec`), `_handle_augassign_stmt` (`self._heap_var`): both REJECTED ("unlisted write effect") (fun/m_e.log, m_aug.log) |
| corpus root + pyref vs base | root 0 MOVED / 0 GONE / 0 APPEARED (+3 new witness sources 9100-9102); pyref 0 / 0 / 0 (sw/cmp-corpus.txt, cmp-pyref.txt) |
| mirror vs base (sw/cmp-mirror2.txt) | exactly 4 movers: `module6_whyml/expressions` (`_e` converted; `_resolve_dotted_signature` val typed), `module6_whyml/statements` (augassign converted, fieldassign re-port, declared_in swap, 2 `sibling_concrete` opt-ins; `opaquestmt.raw` label qualified to `opaquestmt_raw` because the new `_opaqueexpr375` record also has `raw`), `frontend/pure_ast` (record `comment` + `__repr__`), `Module6_WhyMLTranspiler` (DECLARATION-ONLY: `_e` val param type, augassign val `raises`, val order; its one moved refines goal is `(true -> true) /\ (true -> true)`, proved). All 4 type-check (QUICK). |
| honesty planes on the new emissions | yield-erasure rc 0, computed-rhs-erasure rc 0, emitted-vacuity rc 0 (no NEW erasure) |
| check-shadowed-selfcalls | first RED 16 > 14 (augassign's calls to the verified `_seq_operand` / `_call_returns_string_collection` went through receiver-less vals); repaired with the lesson (ay) `#@ sibling_concrete` opt-in on both -> 14 (ratchet 14) |
| fidelity | check-self-annotate-sync rc 0, self-annotate-mirror-check rc 0, doc-coherency --check rc 0 |
| check-declaration-conformance | OK 22/26; `declared_in` 20 -> 21, all conform; FAIL_RATCHET 5 -> 4 |
| fast planes | 62/62 green (sw/planes4.txt; an earlier run was RED on claim-vacuity / contract-truth-args from a wrong first draft of witness 9100, fixed) |
| `\trusted` (count-trusted-directives grep-substring) | 406 -> 402 (markers 378 -> 374) |
| ledger | 3 (no axiom, no `#@ proof` line, no proof-axiom file touched) |

OWED (driver-batched, NOT run): whole-file `module6_whyml/expressions.py`, `module6_whyml/statements.py`,
`frontend/pure_ast.py`; `Module6_WhyMLTranspiler.py` moved by declaration only (type-checks; its single
moved goal is trivially true and proved).
