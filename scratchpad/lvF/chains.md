# lvF (run #5, batch B): census near misses + two small emitter defects

Base b432460d6 (run5-int36). Probes: `scratchpad/lvF/probe.sh` (port the live body into a scratch copy of
the CANDIDATE mirror, apply a cv9 patch spec, `--no-proof` emit on QUICK). Results: `probe/results.tsv`.

## Defect fixes

### cap-trusted-val-unit-return (Module6_WhyMLTranspiler: transpile / _compute_shared_module_maps /
### _emit_prefunctions_infra / _shared_use_lines, all `\trusted` twins; functions._emit_function_block, live-only)
A `\trusted` stub whose body is a bare `pass` has `find_return_type -> "unit"`; only the scalar GAP #2
annotations (str / int / bool / ExprIR tags / PyConstVal) were promoted, every other annotation gave a
`val ... : unit` and a caller using the result failed L3-tc. Now the call-site map entry (and, adopted from
it, the stub's own `val`) is the WhyML type the emitter models the DECLARED annotation as: list/bytes ->
`array int` / `array string`, set/dict -> `map int (option int)`, float -> `real`, `#@ datatype` -> its
variant, record class -> record, anything else (Any, object, Optional/Union `_union_*`, unknown classes)
-> the erased `int` callers already test against `pycsl_none`. Not promoted: unannotated (a `pass` body
returns None in Python; retype the mirror def line instead), `-> None`, NoReturn, lemmas, `Tuple[...]`
(arity not in the IR annotation; tuple typing is emitter-wide). The array theory is pulled when such a
list stub exists. Soundness: the value is UNCONSTRAINED (no ensures added, plain program `val`, not a `val
function`: no determinism); the stub's contract is unchanged. Witnesses 9000 (PASS, L3-tc fails at base),
9001 / 9002 / 9003 (FAIL: value, determinism, length claims), 9004 (`-> None` control, PASS at both).
Control: a NON-trusted `-> List[str]` self-call with `return []` hits the same caller-local wall
(`ns = ref 0`, scratchpad/lvF/ur/ur3.py) -- the promoted val now behaves exactly like its converted twin.

### cap-return-exn-nonint (stmt_control_flow._handle_while_stmt, VERIFIED twin: re-ported verbatim)
lvA's spike, generalised from `string` to every non-int return type: the `while` arm wrapped a loop
holding a direct `return` in `try .. with Return r -> r end` even when the function-level wrap exists
(`_has_early_ret` is always set by an in-loop return); in a non-int function the int `Return` is the wrong
payload and is not even declared. Omitted there (the `for` arm's `not self._has_early_ret` guard). A
`while True:` with no `break` and nothing after it ends in `absurd` (a VC: the exit condition is false).
Int functions keep the inner catch (byte-identical). The guard reads the return type through a local
(`_wrt = self._func_return_type; ... not _wrt.startswith("int")`) so the verified mirror lowers it to the
modelled `str_startswith_op` (a direct `self._func_return_type.startswith(..)` lowered to an opaque
receiver-less call). Witnesses 9005 / 9006 / 9009 (PASS, L3-tc fails at
base: unbound exception `Return`), 9007 / 9008 (FAIL). NOT covered (each a separate carrier, emitter-wide):
early `return <set/dict>` (needs a map-payload Return), heterogeneous tuples (`Return_<arity>` is
`(int, ...)`), Optional[<record>] (mutable payload rejected by Why3), `-> Any` returning a str (s116).
OWED: whole-file `module6_whyml/stmt_control_flow.py` mirror proof (the DRIVER's batched slot).

## Conversions
- GhostSpecOpsMixin._handle_mktuple_expr (expr_ghost_spec_ops): live comprehension -> explicit loop
  (append each `self._e(e, lr)` in order, join), ported verbatim.
- _ContractParser.parse (Module2_Parser): ported verbatim; the `\trusted` callee `_parse_contract` mirror
  def line retyped `-> Any` (live is unannotated; Any is its faithful type) so its val returns the erased
  value. An honest delegating wrapper (call, at_eof check, diverging `_err`, return).

## Re-probed near misses (after both fixes)
| stub | probe | verdict |
|---|---|---|
| _ContractParser.parse (s031) | s031_f1 (spec cv9 s031_2: `_parse_contract -> Any`) | TC-OK, honest -> CONVERTED |
| _ContractParser._parse_inductive (s039) | s039_f1 (retypes only, no stand-in) | TC-OK but REFUSED for honesty: the record's `rules` / `members` fields are emitted `any_array ()` and each member tuple `any int` (input-blind; tuple element model) |
| _ContractParser._parse_inductive_rules (s040) | unchanged by these fixes | TC-OK-PARTIAL at base already; each appended (str, ExprIR) rule is `any int`: REFUSED (tuple element model) |
| _Harvester._normalize_leading (s025) | s025_f1 (cv9 s025_3) | the unit-return link CLEARS; next wall: `[ln.strip() for ln in raw_lines]` / `_fold_blocks` result (list_comp int vs array) |
| _Harvester._fold_blocks (s026) | s026_f1 (cv9 s026_3) | the unit-return link CLEARS; next wall: route #325 `str_concat` over erased operands |
| _rewrite_annotation_str (s116), parse_format (s141) | not completed | s116: `-> Any` returning str + re.Match; s141: Optional[StructFormat] early return (mutable payload) + re.Match |

re.Match model: NOT built. Each of its 8 chains has another wall it does not clear (s020 pair-unroll +
union, s116 Any-str, s141 record payload, s160 list/union, lvA/lvC chains tuple typing): it completes 0
stubs alone, below the brief's >= 2 bar.

## Gate record (candidate = /home/fabrice/git/pycsl-lvF-cand, base b432460d6)
- corpus root: 1 MOVED, 0 GONE, 0 APPEARED (+10 new witnesses): 2095_gen36_record_return_in_loop_stays_closed
  (expected FAIL): the while arm drops the inner `try .. with Return r -> r` around a loop in a RECORD-returning
  function; the in-loop `raise (Return {record})` is still rejected by Why3 (L3-tc: `p` vs `int`) -> still
  FAIL for the same reason (re-run on the candidate). Defect 2 moved NO corpus / pyref file.
- pyref: 0 MOVED / 0 GONE / 0 APPEARED.
- mirror: 7 MOVED (all type-check on the candidate, QUICK):
  * module6_whyml/expr_ghost_spec_ops (conversion), frontend/Module2_Parser (conversion + `_parse_contract -> Any` val),
    module6_whyml/stmt_control_flow (re-port of `_handle_while_stmt` + `irnode__to_dict` val type);
  * module6_whyml/expressions, module6_whyml/statements (`val irnode__to_dict : unit` -> `map int (option int)`),
    frontend/__init__, frontend/ir_resolve (six `pycslweaver__visit_* : unit` -> `int`): DECLARATION-ONLY
    moves of `\trusted` vals that no function of the file references (grep: each name occurs once / at its
    declaration only), so no goal of those files changes.
- witnesses (full proof): base 9004 PASS, all others FAIL (9000/9005/9006/9009 at L3-tc); candidate
  9000/9004/9005/9006/9009 PASS, 9001/9002/9003/9007/9008 FAIL at the postcondition (1 goal unproven each).
- `--fun controlflowstmtmixin___handle_while_stmt` (re-ported verified twin, candidate tree): 3443/3443
  Valid (3216 own sub-goals), rc 0, Verification SUCCESS (~2.2 h incl. the non-vacuity gate; a first try
  with a 50-min timeout ran out inside the vacuity phase with 0 non-Valid).
- fast planes 62/62 green (a first run was RED only on claim-vacuity: the witnesses' `requires True` /
  `ensures True` stub clauses; dropped, the stubs keep `assigns \nothing`).

OWED (driver's batched slots): whole-file `module6_whyml/stmt_control_flow.py` (~5 h) and
`frontend/Module2_Parser.py` mirror proofs. Residual: `--fun` on the Module2 mirror is broken AT BASE
(`unexpected 'variant' clause`: the --fun demotion keeps a `variant` on 3 vals); parse's own goals were
discharged with why3 on that emission minus the 3 val variant lines (5/5 Valid, Alt-Ergo and Z3).
