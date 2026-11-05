# lvD cause census: the str value-model seam (cv8 cap-vm-unerase-str), run #5

Base 07fe9acc3 (run5-int33 = main + u25 + lvA). Method (lvA pattern): verbatim port of the LIVE
body into a scratch copy of the mirror (`bin/port-one-mirror-body.py --convert [--replace]`),
`--no-proof --keep-mlw` on QUICK (`survey.sh`, `runsurvey.sh`), the generated `.mlw` read at the
Why3 error position; then the link hand-patched in the scratch copy (`runp.sh` + `subs/*.py`) or
the candidate capability built in the emitter and the VERBATIM body re-emitted, down to TC-OK +
`--fun` + an honesty read. Probe outputs: `r1/` (first links at base, all 12 probed stubs; same
positions as cv8), `r2/` (hand-patched second links), `r3/` `r4/` (verbatim bodies on the lvD
emitter).

The 14 cv8 stubs share one Why3 symptom (`string` vs `int`) but NOT one cause: the census finds
NINE distinct erasing constructs, and no cause covers more than two stubs.

## Cause table (first link = the construct whose value is erased)

| stub | file | erased construct at the error position (r1) | cause id | rest of the chain (r2/r3/r4) | end state |
|---|---|---|---|---|---|
| `CrossCheckResult.diagnostic` | proof2why3/crosscheck | `f"  {label}: {'PASS' if ok else 'FAIL'}"` -- the both-arms-string ternary segment wrapped `int_to_string (<string>)` (the str-return f-string joiner treats every non-`_is_string_expr` part as int; the IfExpr string rule is @mutable_state-gated) | **C1** f-string string-ternary segment | hand-patched segment -> TC-OK (r2); the `self.pairwise.items()` loop is the generic havoc (`iter_length/iter_get (self_pairwise_items_0 ())`, plain `val`s, targets `any int`): a sound over-approximation, not a law | **CONVERTED** (C1) |
| `_Unparser.visit_MatchStar` | frontend/pure_ast | `name = "_"` into `name`, pre-declared `ref 0` (first bound by the int-model `node.name`): a raw Why3 string into an int-HASH slot | **C2** str literal into an int-hash local | hand-patched -> TC-OK (r2); the rest (`self.write(f"*{name}")`) is the same int-model shape as the VERIFIED twin `visit_MatchAs` | **CONVERTED** (C2) |
| `_make_temp_mlw_path` | pycsl | `fd, path = tempfile.mkstemp(..)`: the generic tuple unpack types every slot `int` (`val tempfile_mkstemp_0 () : (int, int)`), so `path` is `ref 0` against `-> str` | **C3** stdlib `(int, str)` pair (mkstemp) | TC-OK after C3 (r4) | **CONVERTED** (C3) |
| `_synthesize_legacy_text` | pycsl | `"\n\n".join(_synthesize_block(r) for r in records)` -> `join_1 (any int)`; `records: "List[dict]"` (quoted) -> `int` | C4 join over a MAPPED genexp + List[dict] element erasure | unquoting the annotation (r2) gives `records: array int` -- a `List[dict]` element is erased to `int` while `_synthesize_block` takes `map string (option int)`: an honest fold would need the list-of-dict element model | REFUSED (two value-model links: list-of-dict elements, mapped-genexp join) |
| `_to_cache_payload` | audit_proof_reverify | `-> dict` literal with HETEROGENEOUS values (bool / str / str / float / list): `map_update_some .. report.compile_stdout` into a `map int (option int)` | C5 heterogeneous dict value | needs a universal (`hval`-style) dict value for an unannotated `dict` return | REFUSED (value-model: heterogeneous dict) |
| `calcsize` | module6_whyml/struct_format | `char in sizes` -- `char` from `m.group(2)` (`m_group_1 2`, int, ignores `m`) against a str-keyed map; `int(count_str)` lowered as the identity on the int | C6 `re.Match.group` (lvC scope) | then `int(<str>)`, `_TOKEN_RE.match(fmt, pos)` (module-constant compiled pattern), `m.end()`; mirror `-> int` for live `Optional[int]` | REFUSED here (lvC builds Match.group / module constants) |
| `_lex_contract` | frontend/Module2_Parser | `m.group(0)` into a `str` record field (`_tok_string`) | C6 `re.Match.group` (lvC scope) | -- | REFUSED here (lvC) |
| `ExpressionEmissionMixin._handle_sum_call` | module6_whyml/expressions | `known_sizes[vname]`: `known_sizes = getattr(self, "_known_collection_sizes", {})` is the opaque int (R325 getattr), subscripted by a `string` | C7 getattr-with-default (lvC scope) | then `str(elems[i]).lstrip("-").isdigit()` over an int-erased map | REFUSED here (lvC getattr; expressions home) |
| `ExpressionEmissionMixin._call_bytes_methods` | module6_whyml/expressions | `st = a.strip()` -> `a_strip_0 ()`: the `for a in args` target over `args: List[str]` (`array string`) is not a string local, so `.strip()` / `.lstrip("!")` / `.replace` take the generic opaque path | C8 for-target over a `List[str]` | then `getattr(self, "_array_locals", set())` (lvC), `any(st.startswith(p) for p in _ARR)` over a local str tuple (`any_1 (any (array int))`), `" ".join(f".." for i, t in enumerate(ptypes))` (`join_1 (any int)`), `ptypes[0] == "int"` hashed against a `seq string`: 5+ links | REFUSED (5+ links, expressions home) |
| `PyCSLToJSONEmitter._field_type_from_annotation_inst` | frontend/Module5_IREmitter | `self._m5_tuple_record_name(_tup_tags)` -> opaque int: the callee (and `_m5_tuple_slot_tags`, `_irnode_ann_name`) has NO mirror twin, so the generic method call is int-typed | C9 missing mirror twins | r5: with the three live methods (+ the `_M5_TUPLE_SLOT_TAGS` class constant) added verbatim to the scratch mirror, Module 4 REFUSES the file: `e.id in PyCSLToJSONEmitter._M5_TUPLE_SLOT_TAGS` reads a class constant through the class name, classified as an enum-member use (ir-semantic). Further links: `type(a).__name__` / `getattr` duck-typing in `_irnode_ann_name`, the `ast.*` isinstance chain; side finding: live `_irnode_ann_name` carries a DOUBLE `@staticmethod` (Module5_IREmitter.py:3007-3008) | REFUSED (3 missing twins, a class-constant-through-class-name refusal, then lvC getattr; Module5 home) |
| `_load_axiom_registry` | proof2why3/crosscheck | `_REPO_ROOT / "src" / ..` -> `float_truediv_op` (no `Path` model) | C10 `pathlib.Path` `/` | then `Path.read_text`, `ast.parse` / `ast.walk` (lvC) / `literal_eval`, a dict comprehension; lvA: the converted body would be input-blind | REFUSED (honesty, lvA) |
| `_load_axiom_registry` | proof2why3/crosscheck_ir | same as above | C10 | same | REFUSED (honesty, lvA) |
| `normalize_surface` | proof2why3/parser | (lvA) needs `#@ \diverges` | -- | -- | skipped per brief |
| `_nat_to_int_with_sidecond` | proof2why3/normalize | (lvA) honesty: lifted `repl` def input-blind | -- | -- | skipped per brief |

## Set cover

Built (all emitter-local, no op law beyond the existing ones, no axiom, every edited live method has
a `\trusted` mirror twin, so no re-port is owed by rule 13):

- **C1** (`_handle_fstring_expr`, `\trusted` twin; `_fstring_str_part`'s VERIFIED twin untouched):
  in the str-typed f-string joiner a segment that is an `IfExpr` whose BOTH arms are string-typed is
  lowered by `_expr_to_whyml` itself -- `(if t then a else b)`, an exact Why3 `string` -- instead of
  `int_to_string (<string>)`. The replaced emission was always ill-typed, so every f-string that
  type-checked at base is byte-identical. Covers `diagnostic`.
- **C2** (`_emit_body_code` + `_handle_assign_stmt`, both `\trusted` twins; frame of the
  `_emit_body_code` stub names the new field `_lvd_int_predecl`): a bare string LITERAL assigned to a
  local that the pre-decl chain declares with the INT `ref 0` (no typed carrier, not a formal) is the
  literal's `stable_hash` -- the documented A7 int-hash string collapse, the same text
  `_coerce_to_int` folds the literal to at every call / comparison site. The replaced `x := "lit"`
  against `ref 0` was always ill-typed. Covers `visit_MatchStar`.
- **C3** (`_typed_local_vars` + `_handle_tuple_unpack_stmt`, both `\trusted` twins): a TOP-LEVEL
  `fd, path = tempfile.mkstemp(..)` (stdlib-resolved by the route #323 import test, `path` bound
  nowhere else, not a formal) types the generic plain `val tempfile_mkstemp_0 () : (int, string)`
  (non-deterministic: no `function`, no content law) and let-binds `path` from the string slot. No
  corpus program uses `mkstemp`. Covers `_make_temp_mlw_path`.

3 conversions. The remaining causes are each a single-stub value-model link (C4, C5, C9, C10) or in
lvC's scope (C6, C7) or 5+ links deep (C8).

## Side findings

- `mirror-int-annotations.tsv` (`mirror-int-annotations.py`): 242 mirror def-line annotations say
  `int` / `List[int]` where the live def says something else (args and returns, 20 files). This is
  the mirror's systematic int-erasure, not a handful of typos; the two cv8 rows it touches are
  `_load_axiom_registry -> int` (live `Dict[str, str]`, crosscheck + crosscheck_ir) and
  `calcsize -> int` (live `Optional[int]`: a `None` result is erased into `int`, a genuinely false
  claim for any caller that reasons about the value). Not fixed here (their stubs stay `\trusted`;
  correcting the annotation moves every caller's emission).

## C3 extension (after the first gate round)

The admitted mkstemp path target is also added to `_string_local_vars` (already written by
`_typed_local_vars`, so no frame moves), so `path + ".x"` / `path == q` lower through the string
ops; in a @mutable_state body that pre-declares it `ref ""` the unpack assigns into it, elsewhere it
is let-bound at its only binding. Found because the first PASS witness (`ensures True`) tripped the
claim-vacuity ratchet; the reworked 8926 proves `path + "" == path`.

## Gates (final snapshot cand3 = stash 74e1404c1 of run5-lvD over 07fe9acc3)

| gate | result |
|---|---|
| `--fun crosscheckresult__diagnostic` | 12/12 Valid, 0 non-Valid |
| `--fun _make_temp_mlw_path` | 735/735 Valid, 0 non-Valid |
| `visit_MatchStar` | `--fun` is refused on pure_ast (each `--fun`-stubbed `_parser__funcdef` / `_parser__classdef` trips the list-length guard); its VC `_unparser__visit_MatchStar'vc` proved directly in the full emitted module: 2/2 Valid (Alt-Ergo 2.6.3 and Z3 4.13.3). Whole-file pure_ast OWED. |
| mutations | `_make_temp_mlw_path` `return fd` -> Why3 type error (int vs string); `diagnostic` hidden `self.qualname = ..` write -> rejected (immutable field); `visit_MatchStar` `name = ["_"]` -> type error. NOT caught: a hidden `self._indent = 7` write in `visit_MatchStar` -- the `_Unparser` frame is synthesized `writes { _pyobj_state }` from the body, so `#@ assigns self._source` is not enforced for ANY `_Unparser` method (pre-existing; the verified twin `visit_MatchAs` has the same shape) |
| corpus root + pyref vs base | 0 MOVED / 0 GONE (rc 0); APPEARED = the 9 witnesses only |
| mirror vs base | exactly 3 declared movers (rc 0): frontend/pure_ast, proof2why3/crosscheck, pycsl -- each diff confined to the converted function + its abstract-op decls; statements.mlw unchanged (the `_emit_body_code` frame edit does not move it) |
| fidelity | check-self-annotate-sync rc 0, self-annotate-mirror-check rc 0, doc-coherency --check rc 0 |
| fast planes (cand3) | 62/62 green (incl. mirror-coverage, vacuous-drivers, claim-vacuity, trusted-reasons, yield-erasure, emitted-vacuity, stable-hash-fold-injectivity) |
| witnesses 8920-8928 | candidate: 8920 / 8923 / 8926 PASS, the 6 others FAIL by non-Valid goals (0 type errors); base: all 9 FAIL (8920 / 8923 type errors, 8926 unprovable) |
| `\trusted` grep | 413 -> 410 |
| ledger | 3 (no axiom, no proof-axiom file touched) |
