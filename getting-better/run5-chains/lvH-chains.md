# lvH chain walk: mutator-bundle batch (driver run #5)

Tree `run5-lvH` = run5-int40 693e20184 + merge of run5-lvB (7b462e09c 18d4ddca7, clean merge, faae82431).
Scratch tree `scratchpad/lvH/st` (copy of the merged src/pycsl + mirror + bin; NOT committed). Method as cv9:
verbatim port of the live body (`bin/port-one-mirror-body.py --convert [--replace]`), cumulative patch
specs (`spec/<tag>.json`, applied by cv9's `patch.py`), `--no-proof --keep-mlw` on QUICK (`probe.sh`,
`batch.sh`, HEAVY_QUICK=1). 38 emissions, `probe/results.tsv`, `probe/<tag>.{src.py,log,patchlog}`.

Simulation of the brief's capabilities (scratch only):
- (a) exact `pop()`: source stand-in `x = s[len(s) - 1]; s = s[:len(s) - 1]` (a seq local; probe t1 shows
  the emitter accepts the worklist `while s:` with no variant and lowers it to `Seq.get` + `seq_sub`).
- (b) set `add` / dict `setdefault` on fresh locals: lvB's lowering as merged (admitted where its rules hold).
- (c) set ctor shapes: `set(seed) if seed else set()` rewritten into two fresh bindings; `|=` -> `= .. | ..`.
- also simulated (NOT in the brief, to look further): lvC's unlanded cap-r325-typepos patch
  (`scratchpad/lvC/typepos.patch`, applied to st/src/pycsl/pycsl.py only).

Legend: [R] equivalent rewrite (live refactor of the `\trusted` twin possible), [T] mirror retype,
[S] stand-in (capability NOT built), [a]/[b]/[c] = the brief's capability (simulated).

## Chain table

| # | stub | first mutator link (receiver shape) | links walked | terminal | reachable by (a)-(c)? |
|---|---|---|---|---|---|
| h01 | `ExpressionEmissionMixin._handle_struct_call` (expressions) | `_STRUCT_FMT_FOLDS.setdefault(k, v)` on a MODULE GLOBAL dict, result USED (`_p228 != args[0]`) | [S] setdefault dropped | R325 `ret_type` from `str_concat` (opaque-int string build of the struct return type) | NO: a global receiver is outside lvB's admission (and outside (b)); the result is used, so (b) must refuse |
| h02 | `ExpressionEmissionMixin._content_string_method` (expressions) | `_fs_work.pop()` fresh `list(..)` local under `while _fs_ok and _fs_work:` | [a] exact pop; [S] `extend([..get..])` -> `+` (lvB refuses call-valued extend args); [R] 4x `x or []` as a value (cap-boolop-value); [R] 2x R274 comprehension/genexp over the WRITING `_expr_to_whyml` / `_is_string_expr` -> loops | R542 `expr["args"][0]`: a subscript of the int-erased `expr` (vm-unerase-irnode); 5 sites | NO: 6 links walked, 4 of them outside (a)-(c), and the terminal is the IR-node value-model seam |
| h03 | `PyCSLToJSONEmitter._populate_protocol_conformance` (Module5) | `self.program_ir.setdefault("overrides", []).append({..})`: COMPUTED receiver inside a self FIELD | [S] dropped | R325 `getattr(node, 'csl_conforms_to', [])` (getattr-dynamic on a pyast node) | NO: self-field / computed receiver (lvB residual: inter-procedural alias) |
| h04 | `PyCSLToJSONEmitter._collect_union_arms` (Module5) | `stack.pop()` fresh list under `while stack:` | [a] exact pop | R325 `ast.Attribute(..)` constructor result into an array (pyast-ctor-model; the quoted-arm rewrite builds pure_ast nodes) | NO: the next wall is the pure_ast constructor model; honesty: 3 of the 4 return arms build `ast.Attribute` / `ast.Constant` nodes that would be opaque ints |
| h05 | `PreambleEmissionMixin._precompute_axiom_logic_funcs` (preamble) | `self._axiom_logic_funcs.add(fn)` (SELF FIELD set) in a `while changed` fixpoint | not walked further (self field) | + 2 nested closures (`_names_of`, recursive `_walk`), `|=` on locals | NO: self-field receiver |
| h06 | `PreambleEmissionMixin._emit_module_globals` (preamble) | `self._module_global_classes.pop("result", None)` (SELF FIELD dict) | [S] dropped | element store `self._module_global_classes["result"] = ..` through an opaque self-field dict | NO: self-field receiver (both the store and the pop) |
| h07 | `Module6_WhyMLTranspiler._render_callee_condition` (Transpiler) | `_r141.pop()` fresh worklist | [a] exact pop; [S] `_ops.pop(k, None)` dropped (`_ops = getattr(self, "_abstract_ops", None)` is an ALIAS of a self field: not fresh) | route #175: `except Exception` meant to catch the user `PyCSLIRError` raised by `_expr_to_whyml` (handler matching knows only builtin classes); fixing it changes the live code's behaviour, not an equivalent rewrite | NO: self-field alias + exception-hierarchy model |
| h08 | `audit_proof_reverify._sha256_file` | `h.update(path.read_bytes())`, `h = hashlib.sha256()` (not a builtin collection ctor: lvB refuses) | not walked | HONESTY-WALL: even with `update` havocked, `h.hexdigest()` of an opaque hash object over an unmodelled `Path.read_bytes()` is input-blind: a converted body would be a FACADE (no hashlib / FS model; cv9 s145 same verdict) | NO (honesty) |
| h09 | `FunctionEmissionMixin._emit_contracts` (functions) | `_s60.pop()` fresh worklist | [a] exact pop + `extend` -> appends [S]; `declared_exc` / `covered_raw` = `set()` + `.add(str)` ADMITTED by lvB [b,c]; [T] `func_exceptions: Set[str]`; [S] cap-r325-typepos (lvC patch) for the `isinstance(_n60, list)` `pv_size` false positive | R325 `str_concat` into `Seq.snoc !lines`: functions.py's mirror DECLARES NONE of `_expr_to_whyml` / `_emit_frame_condition` / `_is_linear_vc` (cross-mixin `#@ declared_in` stubs needed, each with the callee's full `assigns`), so every rendered clause is an opaque int | NO: >= 2 more links (declared_in stubs + the `self._in_spec` / callee-assigns frame) outside (a)-(c), plus typepos |
| h10 | `FunctionEmissionMixin._emit_function` (functions) | `_nd.add(_n)`: `_nd = _ndp[1]`, an alias into the SELF FIELD tuple `self._r242_nondet` | [S] dropped (+ `getattr(..).discard` computed receiver) | R490 `_tk & _nd`: a set operand typed int | NO: self-field alias (the method's whole effect is the self-held nondet set) |
| h11 | `TypeInferenceMixin._collect_array_var_assigns` (types) | route #301 nested unpack `for tgt, (_a, _o) in ..` | [R] unpack flattened; [R][c] `set(seed) if seed else set()` -> two fresh bindings, `found |= X` -> `found = found | X`; [T] `seed: Optional[Set[str]]`, `-> Set[str]`; [T] `stmts: List[Dict[str, Any]]`; [S] `str(fn)` for the erased `fn` into `_call_return_whyml_type(fn: str)` (route #252) | method-recursion-cycle: `self._collect_array_var_assigns(s[k])` self-recursion through a method stub (needs `#@ \diverges`, which would propagate, or a structural measure). The VERIFIED sibling `_collect_tuple_array_locals` is converted ONLY through a bespoke pyval structural-recursion recognizer (`let rec .. (stmts: list pyval) : sdict`), not by the generic lowering | NO: recursion + vm-seam beyond (a)-(c) |

## Verdict

**0 of 11 stubs reach TC-OK** (honest or not) with (a)-(c) simulated, even with lvC's typepos patch also
simulated. The brief's stop rule (fewer than 2 honest TC-OKs) holds: **nothing built, no conversion.**

Why cv9's "known walls are all mutator links" did not hold: the merged.json rows for these 11 stubs came
from lvB's FIRST-blocker census (a chain of length 1, "DEPTH-STOP"); their links were never walked past the
mutator site. Walked:
- 6 / 11 (h01 h03 h05 h06 h07 h10) have a mutator on a self FIELD, an alias of a self field, or a module
  GLOBAL: lvB's documented residual (inter-procedural alias analysis), outside (a)-(c).
- 1 / 11 (h08) is a facade at any depth (hashlib + filesystem).
- 4 / 11 (h02 h04 h09 h11) pass the mutator links with (a)-(c) and stop 1-5 links later on the value-model
  seam (int-erased IR / pure_ast nodes: R542, pyast ctor), cross-mixin declarations (`declared_in`), a
  method-recursion cycle, and two small emitter defects (cap-r325-typepos; route #175 user-exception
  hierarchy).

What (a) would still buy: the exact pop is needed by h02 h04 h07 h09 (all `while stack:` worklists over
int-erased IR, so `pop` is always guarded by the loop test and its IndexError VC is dischargeable), but in
none of them is it the last wall. Probe t1 (`scratchpad/lvH/t/t1.py`) shows the existing lowering of the
source-level equivalent (`s[len(s)-1]`, `s[:len(s)-1]`) uses the abstract `seq_sub` (length law only), so
a faithful exact pop should lower to `Seq.([..])` slicing, not to that rewrite.

Cheapest next levers for this family (ranked by stubs unblocked here):
1. a whole-module self-field alias analysis for mutators on `self.<f>` (h03 h05 h06 h07 h10; lvB's 13);
2. cross-mixin `#@ declared_in` stubs for the functions.py emitters (h09 and the other functions.py stubs);
3. cap-r325-typepos (lvC patch, small) and the IR-node value model (h02 h04 h11).
