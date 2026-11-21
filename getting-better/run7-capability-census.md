# Run #7 capability census (cv12)

Executor cv12, driver run #7, 2026-11-13. Tree `pycsl-cv12`, branch `run7-cv12` at 1ffab454c (= `ghost-assign-bc6`
HEAD at run #7 start). Census only. Nothing was built, no `src/pycsl` file was edited in the tree, and no proof was
run. Every emission was a `--no-proof --keep-mlw` run (Why3 type-check included) or a `why3 prove --type-only` of a
hand-patched `.mlw`, each one a separate QUICK heavy.sh job (slot 3). From 10:40Z there was a 20 s gap between jobs,
at the driver's request. Raw data is in `scratchpad/cv12/` of this tree:
- `probe/results.tsv`, plus `<tag>.src.py/.log/.mlw/.patchlog` for each probe;
- `spec/c*.json`, the new link specs, applied with cv11's `patch.py`;
- `mlwx/*.mlw/.log`, the emission-level stand-ins;
- `chains.json`, one list of links per stub;
- `pop.json`, the selection;
- `sizes.json`, the live body sizes;
- `gen_doc.py`, which generates the tables in §2-§3.

**Method.** The population is every governing `#@ \trusted` stub at HEAD whose cv11 need-list, minus run #6's
builds, has at most 2 capability ids, plus every HONESTY-WALL and TC-OK-PARTIAL row. That gives 281 rows: 224
walked, 53 EXCLUDED as external-world (lvQ owns them), and 4 EXCLUDED as open user decisions (`PyCSLError.__init__`
and the 3 `\diverges` rows). Two stale rows (`_expr_to_whyml`, `_track_collection_metadata`) were removed: they were
converted in run #6 and only share a name with another def.

Each stub goes through the following steps:
1. A verbatim port at HEAD (`bin/port-one-mirror-body.py --convert [--replace]` into the scratch copy `st`), then a
   replay of cv11's deepest chain spec (`_R` probes, otherwise depth-0 `_0`).
2. Where the wall allowed it, the chain was EXTENDED with up to 3 new links:
   - [R], a behaviour-identical live respelling;
   - [T], a mirror retype or signature fix;
   - [S], a stand-in for an unbuilt capability. Stand-ins come in three forms:
     - scratch emitter trees (`stNR`: the Module3 name-rebinding refusal disabled; `stDA`: the functions.py
       #243/#244 collection-alias raise disabled; `stTP`: lvC's unlanded `scratchpad/lvC/typepos.patch`; `stX103`:
       a CSL-class retype in the scratch LIVE Module2);
     - a body edit (`[S]` in the specs);
     - an emission-level hand patch of the `.mlw` blocker, then `why3 prove --type-only` (`mlwx/`).
3. Every TC-OK was read off the `.mlw` for honesty: input-reading, the facades, and leaf reachability.

A chain counts as CLOSED only at an honest TC-OK. Terminal classes used below:
- STOP: the next wall is a capability, and the walk stopped there.
- BOUND: the next wall is a `Dict[str, Any]` / Any-IR value read, i.e. the CERTIFIED-BOUNDARY of
  `getting-better/dict-value-model-r3-impl.md` §1.
- CORRECT: the refusal is a real semantic fact, not a model gap.
- EXT: an external-world wall.
- TC-OK-PARTIAL: type-checks with stand-ins, but the result is input-blind or a facade.

**STATUS: FINAL (2026-11-13T12:22:14Z): 222 of 224 selected chains walked (2 stale rows removed); 270 probes + 5 emission-level stand-ins.**

## 0. Headline: capability ranking (measured at HEAD)

A capability, or a bundle of 2, gets credit for a stub only when the stub's chain CLOSES at an honest TC-OK with
that capability simulated. Everything else on the chain must be free: an [R] behaviour-identical live respelling or
a [T] mirror retype / signature fix. Proof hours are the last measured whole-file times; "est." marks a small file
with no measured time. Rows are greedy: each row assumes the rows above it are built.

| rank | capability / bundle (NOT yet built) | stubs it COMPLETES (chain closed, measured) | home files + proof h | build | soundness risk | make-or-break spike |
|---:|---|---|---|---|---|---|
| 0 | *(no capability: rewrite-only conversions)* | **3**: `calcsize` (struct_format; `cs314_1`), `PreambleEmissionMixin._mutex_inv_application` (preamble; `cs289_3`), `parse_rocq_assumptions_block` (proof_axiom_allowlist; `cs348_2`) | struct_format 0.14, preamble ~0.3 est., proof_axiom_allowlist ~0.25 est. = ~0.7 h | none (§1.1 respellings) | none new | - |
| 1 | **cap-typed-local-lowering**: six typing-SELECTION defects of the emitter (T1-T6, §4.1). No new semantics: each is a Why3 type error today, i.e. fail-closed | **5**: `_function_body_eqs`, `_parse_goal_blocks` (pycsl.py), `_Harvester._normalize_leading` (Module1_Ingestor), and VERBATIM `calcsize` + `_mutex_inv_application` (rank 0 already converts them with respellings) | pycsl.py 0.5, Module1_Ingestor ~0.25 est. (+ the rank-0 homes if verbatim) = **~0.75 h new**, plus the movers of the mirror sweep | S-M (~8 h) | low-med. Typing only, but T2/T4 change generic local / `len` lowering and can MOVE verified mirror emissions: a byte-diff plus mirror-emit sweep is mandatory | T3 + T2 on `_parse_goal_blocks` (verbatim body, [T] unquoted return) with a mirror-emit sweep showing that only pycsl.py moves |
| 2 | **cap-str-replace-count** (a law-free `str_replace_first_op` for `s.replace(a, b, 1)`) | **+1** given rank 1: `Module6_WhyMLTranspiler._sig_val_from_let` (`cs007_3` + `mlwx/cs007_x1`: its nested `_hdr_name` inlined by an [R]; T2 for the hoisted `_nm: str`) | Module6_WhyMLTranspiler 1.0 h | S (~4 h) | low (law-free, deterministic `val function`, like `str_replace_op`) | the `_sig_val_from_let` port must reach TC-OK with `out` built from `str_replace_first_op` |
| 3 | cap-re-gate-widening: lvO's re.Match gate opened to `import re as _re`, a str subject that is an element of a `List[str]` (not only str-DECLARED), `m is None`, `m.group()`, `m.start()`; plus (M) a COMPUTED compiled pattern and `m.lastgroup` | 0 complete. It would let `_function_body_eqs` go verbatim (there free [R]/[T] cleared it). It is the measured wall of `_ContractParser._parse_contract` (lvP: then the `py_label` record seam), `_lex_contract` (computed pattern + lastgroup: `cs066_1`) and `_rewrite_annotation_str` (Any subject) | - | S + M | low | - |
| 4 | cap-fresh-object-frame | 0 honest. `unparse` reaches TC-OK (`mlwx/cs221_x1`) but is a pure delegation to the trusted `_Unparser().visit`: FACADE | pure_ast 3.3 h | S-M | med | - |
| 5 | cap-name-rebinding-model (the brief's group of 5) | **0**. All 5 chains hit a REAL wall past the stand-in (§1.3). The refusals are correct | - | - | - | - |
| 6 | cap-vm-unerase-dict (the brief's group of 6) | **0** inside the current decision. Three are Dict[str,Any] (the boundary); `calcsize` no longer needs it; two need typed dict-of-list PLUS dict-items iteration and pyast attr write-back | - | XL | crosses the decision (§1.3) | - |

**Totals over the 222 walked chains** (224 selected minus 2 stale rows):
- CLOSED: 3 with free links only, 4 more with ranks 1-2 simulated.
- PARTIAL: 9 TC-OK-PARTIAL, all needing 2+ capabilities or a value model, or a facade:
  `unparse`, `_emit_bitwise_or_power` (lvI's proof wall), `_emit_suite`, `_write_docstring_and_traverse_body`,
  `_sexp_tokens`, `ReverifyReport.summary`, `_expr_to_whyml_string_ctx`, `_walk_stmt`, `_max_end`.
- END ON A WALL: 48 on the Dict[str,Any] / Any-IR boundary, 8 on a correctness refusal, 3 on an external-world
  model, and 1 on an honesty wall. The remaining 146 STOP on a large capability (§3), led by:
  - R327 binder-name collisions needing live renames (12; 8 in GIANT >500-line dispatchers);
  - method-recursion termination (6, +3 partial);
  - the IR-node / pyast value models (12);
  - Optional unions (5);
  - generators (5);
  - pyast attribute write-back (5);
  - self-field collection mutators.
- No other capability or bundle of 2 completes a stub.

## 1. Closed chains and the exact changes

### 1.1 Closed today with free links only (no capability)

| stub (home) | links (probe) | exact change | honesty at TC-OK |
|---|---|---|---|
| `calcsize` (module6_whyml/struct_format.py, live l.274) | `cs314_0` L3-TC → `cs314_1` **TC-OK** | [R] `count_str, char = m.group(1), m.group(2)` → `count_str: str = m.group(1)` / `char: str = m.group(2)`. This is pure and in the same order. | Input-reading: `re_match_op <literal> fmt !pos`, `re_group_op`, `str_to_int`, `Map.get sizes char`. Every return is reachable. Both cv11 needs are GONE at HEAD: lvO's re.Match model covers `_TOKEN_RE.match(fmt, pos)`, and the str->int dict literal is a `Map` |
| `PreambleEmissionMixin._mutex_inv_application` (module6_whyml/preamble.py, live l.4681) | `cs289_R` → `cs289_1` → `cs289_3` **TC-OK** | [R] Iterate `self._mutex_inv_params(mutex, inv_str)` directly into `parts: List[str]` (for/append), test `if not parts`, then `" ".join(parts)`. This is ONE call, and `parts` has the same length as `params` | Input-reading: `safe_mutex_name mutex`, the callee value `self__mutex_inv_params_2 mutex inv_str`, `whyml_ident` per element, `str_join_seq`. Both returns are reachable |
| `parse_rocq_assumptions_block` (proof_axiom_allowlist.py, live l.78) | `cs348_R` → `cs348_1` → `cs348_2` **TC-OK** | cv11 [R]: fold the early `return True, []` into a `closed` flag + `break` (`splitlines` is pure). [T] `line: str = raw.strip()`. [R] `line.startswith((a, b, ..))` → an or-chain of `startswith`. [R] `line.split(" : ", 1)[0]` → `line[:line.find(" : ")]` (identical inside the `" : " in line` branch) | Input-reading: `str_splitlines_op`, `str_strip_op`, `str_contains_op`, `str_startswith_op` ×6, `str_find_op` / `str_sub_op`. Every path is reachable. (`cs348_1`, with the annotation alone, is TC-OK but its tuple-`startswith` is an input-blind `(any int)`) |

### 1.2 Closed with rank-1 stand-ins (emission level)

| stub (home) | links | what was simulated (all in `scratchpad/cv12/mlwx/`, `why3 prove --type-only` rc 0) |
|---|---|---|
| `_function_body_eqs` (pycsl.py, live l.38319) | `cs354_R` → `_1` → `_2` → `_3` → `_4` → `mlwx/cs354_x1` | Free links: [R] a plain `import re` for the two module compiles (they are the only `_re.` uses in the mirror); [T] `line: str = lines[i]`, which gives lvO's str-DECLARED subject; [R] `_c: str = cur`; [T] the unquoted return annotation. The re.Match model then applies. The ONE simulated wall: `res.append((_c, i))` becomes `Seq.snoc !res (!_c, !i)` (T3) |
| `_parse_goal_blocks` (pycsl.py, live l.38089) | `cs359_0` → `_1` → `_2` → `_3` → `mlwx/cs359_x1` | [T] unquoted return; [R] accumulate `cur_hdr: str` instead of re-binding a `List[str]` (or T2b below). Simulated: the hoisted annotated `str` locals typed `string` (T2), the `(header, line)` record append (T3), and the VERIFIED caller `_check_goal_conservation`'s `len(_parse_goal_blocks(..))` as `Array.length` (T4: its emission MOVES, so pycsl.py is re-proved) |
| `_Harvester._normalize_leading` (frontend/Module1_Ingestor.py, live l.413) | `cs045_R` → `_1` → `_2` → `mlwx/cs045_x1` | [R] `any(<genexp>)` → for/break; the truth test → `is not None` (a non-None `(kw, name)` 2-tuple is always truthy); `[ln.strip() for ln in raw_lines]` → for/append. Simulated: the None test of the Optional[Tuple] result of the VERIFIED `_match_block_hdr` as `match .. with None` (T5), and `snapshot_str` for the trusted List[str] `_fold_blocks` (T6) |
| `Module6_WhyMLTranspiler._sig_val_from_let` (live l.2302) | `cs007_R` → `_1` → `_2` → `_3` → `mlwx/cs007_x1` | Free: [R] cv10's index offset instead of the slice; [R] an index loop over `let_lines`; [R] a behaviour-identical inline of the capture-free nested `_hdr_name` (one pass collecting `hdr_idxs` + `hdr_nms`, same first-keyword match and split/strip reads). Simulated: the count-1 `ln.replace(p, "val ", 1)` (rank 2), the hoisted `_nm: str` (T2) with its two consequences (the `""` literal, and `str_eq_op` on the element) |

### 1.3 The brief's single-need groups at HEAD

- **cap-name-rebinding-model (5): 0 complete, and the refusals are CORRECT.** In the stand-in tree `stNR` (Module3's
  rebinding raise disabled), every chain reaches a real dynamic-namespace fact:
  - `_scan_preamble_needs` (`cs291_NR`), `_transpile_modular` (`cs009_NR`) and `transpile` (desk) import from
    LIVE `module6_whyml/generic_fold.py`, whose module scope (l.41459-41463) re-binds every `recognize_*` through
    `globals()[n] = _rc420_gate(n, fn)`. Python runs the #420 gate wrapper while the model would read the ungated
    def.
  - `_build_nodes` creates the AST classes with `type(name, (base,), body)` (route #405, `cs201_NR`).
  - `_run_pipeline` uses eval / `getattr` on a namespace / `globals()` (`cs366_NR`).
  - `generate_json` (+ `__init__`, whose only allocation site it is): the trigger is `setattr(_n, _f, _c)` in live
    `frontend/desugar.py:404`. Next comes `_r42_stack.pop()`, then Any-tree item stores and `json.dumps` (`cs093_NR`).
  - The fix for the generic_fold group is a LIVE refactor of generic_fold's gate (apply it inside the defs). That is
    not a capability.
- **cap-vm-unerase-dict (6): 0 complete inside the current decision.**
  - `calcsize` no longer needs it.
  - `_record_key` is the r3 boundary leaf (rk_hval_chain). The reopening test (a `Tuple[PyVal, ..]` codomain plus an
    hval-polymorphic builtin) is NOT met: run #6's native-tuple returns type the slots, not PyVal.
  - `_emit_prefunctions_infra` and `_shared_use_lines` store into the heterogeneous flags `Dict[str, Any]` returned
    by `_scan_preamble_needs`. There is no in-decision version short of a live refactor of the flags into a class,
    and that function is itself correctness-walled.
  - `_attach_labels_and_ghost_assigns` (`Dict[int, List[str]]`) and `visit_With` (`Dict[int, List[CSLNode]]`) are
    TYPED-value dicts, which stay inside the decision. Past that seam, though, the `.mlw` shows `for line, nodes in
    d.items()` as `any int` (input-blind) and ast node attribute write-back: 2+ more capabilities.
- **cap-dict-alias (statements.py, 4): 0.** With `stDA` (the #243/#244 raise disabled) the next walls are:
  - route #303 (`_handle_assign_stmt`, `_handle_tuple_unpack_stmt`, a GIANT 1194/243-line body);
  - an R325 Dict[str,int] field (`_handle_ghost_assign_stmt`);
  - route #301 nested targets (`_stmts_to_whyml`);
  - and the Any-tree IR walks (the boundary).
- **cap-import-system-local-module (2): CORRECT.** `visit_Module` calls `__import__` (route #326); `_transpile_modular`
  hits the generic_fold rebinding first.
- **cap-inplace-mutator-computed-receiver (2): 0.**
  - `parse_contract`: [R] `_cp = _ContractParser(..)`, then route #506 inside the converted `_err` ([R] there, which
    costs a Module2 re-proof), then route #315: `_ContractParser.__init__` calls `_lex_contract`.
  - `_parse_extracted_contracts`: [R] `d[k] = d.get(k, []) + parsed`, then R489: the LIVE imported
    `parse_node_contracts` has no frame.
- **cap-vm-unerase-union / -list / -irnode (2 each): 0.** Optional-field records (`HappyProperty.param` / `.protects`),
  an Optional[ExprIR] return, CSL-node-as-IR seams, and route #579 (CSL classes are not resolved IR classes).

## 4. Recommended batches

### 4.1 Batch B: cap-typed-local-lowering, plus the 3 rewrite-only conversions (6 stubs)

**Scope.** Six emitter typing-selection fixes. Each one is a Why3 type error today, i.e. fail-closed:

| fix | defect (measured site) | needed by |
|---|---|---|
| T1 | a tuple-unpack `a, b = <str expr>, <str expr>` types its locals `int` (`cs314_0`) | `calcsize` verbatim |
| T2 | a local that is ASSIGNED MORE THAN ONCE, or first bound from a method call, is hoisted to the function top as `ref 0` whatever its annotation or RHS type (`params: List[str] = self.m(..)`, `cs289_1`; `cur_hdr: str = ""`, `cs359_3`; `_nm: str = ""`, `cs007_3`). A single annotated first binding IS typed (`line: str = raw.strip()`, `cs348_2`). The literal and the `==` that flow from the hoisted local then lower int-wise too (an `""` hash, `=` on string). T2b: an annotated `List[str]` local re-bound to `[]` loses its `str_join_seq` join (`cs359_1`) | `_parse_goal_blocks`, `_sig_val_from_let`, `_mutex_inv_application` verbatim |
| T3 | a tuple-LITERAL append into a `List[Tuple[..]]` local lowers to `(any int)` (lvP typed only tuple RETURNS) (`cs354_4`, `cs359_3`) | `_function_body_eqs`, `_parse_goal_blocks` |
| T4 | `len(<call returning List[Tuple[..]]>)` lowers to `iter_length`, not `Array.length` (`mlwx/cs359_x1`, in the verified `_check_goal_conservation`) | `_parse_goal_blocks` |
| T5 | `x is None` / `is not None` of an `Optional[Tuple]` call result compares the option with the int `pycsl_none` (`cs045_1`) | `_normalize_leading` |
| T6 | the `List[str]` result of a trusted method is wrapped in the int `snapshot` instead of `snapshot_str` (`mlwx/cs045_x1`) | `_normalize_leading` |

There is also an optional T0: parse PEP 563 quoted annotations (`-> "List[Tuple[str, str]]"`). Today they lower to
`int`. 14 trusted pycsl.py/pure_ast stubs carry one, and [T] covers it for free.

**Stubs.**
- The rank-0 conversions, which can land FIRST, without any emitter change, as the §1.1 respellings:
  - `calcsize` (struct_format.py 0.14 h);
  - `_mutex_inv_application` (preamble.py ~0.3 h est.);
  - `parse_rocq_assumptions_block` (proof_axiom_allowlist.py ~0.25 h est.).
- After T1-T6:
  - `_function_body_eqs` and `_parse_goal_blocks` (pycsl.py 0.5 h, which also re-proves the moved verified caller
    `_check_goal_conservation`);
  - `_Harvester._normalize_leading` (Module1_Ingestor.py ~0.25 h est.);
  - optionally `calcsize` / `_mutex_inv_application` verbatim instead of respelled.

**Build.** S-M (~8 h).

**Risk.** T2 and T4 change generic hoisting and `len` lowering. The gate is the byte-diff sweep plus
`bin/mirror-emit-sweep.sh` against the 1ffab454c baseline. The expected movers are only the home files. Any other
mover means the fix is too broad: narrow it to the hoisted-local declaration site, or pay that file's proof. The
no-new-`\trusted` / ledger-3 rules are unaffected (no stub, no axiom).

**Make-or-break spike.** T3 + T2 on the verbatim `_parse_goal_blocks` ([T] unquoted return only). It must reach
TC-OK with `blocks` a seq of `(header, line)` records and stay input-reading, and the mirror-emit sweep must move
only pycsl.py. If T2 cannot be scoped without moving expressions/statements emissions, batch B shrinks to
T1 + T3 + T5 + T6 plus the rank-0 respellings: 5 stubs, `_parse_goal_blocks` then via its [R] accumulation
respelling (`cs359_3`) needs T3 + T4 only.

### 4.2 Batch C: cap-str-replace-count (1 stub on top of batch B)

**Scope.** A law-free `val function str_replace_first_op (s pat rep: string) : string` for `s.replace(a, b, 1)`,
mirroring `str_replace_op`. Plus the [R] inline of the capture-free nested `_hdr_name` in the live
`_sig_val_from_let` (behaviour-identical; no helper extraction, per rule 9).

**Stub.** `Module6_WhyMLTranspiler._sig_val_from_let`. TC-OK at `mlwx/cs007_x1` once T2 (batch B) and the count-1
replace are simulated. Home Transpiler ~1 h.

**Make-or-break spike.** Port `_sig_val_from_let` with the inline: `out` must be built from
`str_replace_first_op !ln "let .." "val "`, and the public-entry selection must read `str_split_elem_op` over the
stripped header.

**Caveat.** This is one stub. Nothing else completes. Every remaining capability is a value model (Dict[str,Any] /
Any-IR: a user decision; IR-node / pyast: XL), a termination decision (method recursion, 7 chains;
`#@ \diverges` is open), or a GIANT-dispatcher conversion. If the driver prefers, slot C can instead go to
**R327 live renames + cap-tuple-unpack-alias-303 precision** (the first walls of 10+ GIANT statement/expression
dispatchers). That completes no stub; it only moves those chains one link.

## 2. Per-stub chain table (every selected row; EXCLUDED rows listed)

| sid | stub | file | cv11 end | probes (tag:verdict) | terminal at HEAD | chain notes |
|---|---|---|---|---|---|---|
| s001 | `Module6_WhyMLTranspiler._build_callee_no_exception_summary` | Module6_WhyMLTranspiler.py | DEPTH-STOP | cs001_R:L3-TC | **BOUND** cap-vm-unerase-dict | replay r10xh122_2: L3-TC map_update_some .. (bool_conv (contracts_get_2 <h> 0)): the per-function contracts Dict[str,Any] read as int: dict-model boundary (and the set-valued field _module_func_no_exception: cap-R325-nonint-dict-value-field) |
| s002 | `Module6_WhyMLTranspiler._compute_shared_module_maps` | Module6_WhyMLTranspiler.py | DEPTH-STOP | cs002_R:REFUSED | **STOP** cap-tuple-unpack-alias-303 | depth-0 and replay r10xh127_2 both MOVED (cv11: route #252 erased-to-builtin) to route #303: _tq_ke, _tq_ne, _tq_pe, _tq_ste = .. then _tq_ste.append(..) (a list in a tuple-unpack group) in the 232-line body; then cv11's irnode wall |
| s003 | `Module6_WhyMLTranspiler._emit_prefunctions_infra` | Module6_WhyMLTranspiler.py | DEPTH-STOP | cs003_0:REFUSED | **BOUND** cap-vm-unerase-dict | depth-0 R elem-store-nonlist: needs = self._scan_preamble_needs(..) (trusted, mirror -> int; live Dict[str, Any] of bools/sets/ints) then needs['needs_array'] = True and needs flows into _emit_preamble(needs): a heterogeneous Dict[str,Any] = the CERTIFIED-BOUNDARY value model (dict-value-model-r3-impl.md §1). An in-decision version would need the flag record retyped as a class (a live refactor of _scan_preamble_needs, whose own chain is CORRECT-walled by generic_fold's #420 rebinding) |
| s004 | `Module6_WhyMLTranspiler._maybe_emit_no_exception_assert` | Module6_WhyMLTranspiler.py | DEPTH-STOP | cs004_R:L3-TC | **STOP** cap-vm-unerase-set | replay r10xh125_3: L3-TC active := {.. for .. in getattr(self, '_..', ())}: a set comprehension over a getattr-defaulted self field typed int where a set array is expected (cv11 set typing + mirror field decl) |
| s006 | `Module6_WhyMLTranspiler._shared_use_lines` | Module6_WhyMLTranspiler.py | DEPTH-STOP | cs006_0:REFUSED | **BOUND** cap-vm-unerase-dict | depth-0 R elem-store-nonlist, same root as s003: needs = self._scan_preamble_needs(..) (trusted; live Dict[str, Any]) then an item store into it: heterogeneous Dict[str,Any] = CERTIFIED-BOUNDARY; no in-decision version (the flags dict mixes bool/set/int values) |
| s007 | `Module6_WhyMLTranspiler._sig_val_from_let` | Module6_WhyMLTranspiler.py | DEPTH-STOP | cs007_R:L3-TC; cs007_1:L3-TC; cs007_2:TC-OK; desk; cs007_3:L3-TC; mlwx/cs007_x1:TC-OK | **CLOSE-STANDIN**  | replay r10xh129_4 (cv10's [R] index-offset + nested _hdr_name converted): L3-TC materialize_str !out: out: List[str] gets seq int elements (ln from the slice let_lines[_off:]) / [R] for _j in range(_off, len(let_lines)): ln = let_lines[_j] (no slice): the loop is typed; next L3-TC: out := Seq.snoc !out (ln_replace_3 <h> <h> 1): ln.replace(a, b, 1) (3-arg str.replace) is an opaque int; also the nested _hdr_name is emitted as an opaque _hdr_name_1 over a str hash (cap-closure-lift) / [S] stand-in: ln.replace(p, 'val ', 1) -> 2-arg replace (str_replace_op): TC-OK; out is input-reading (let_lines[_j], str_replace_op); BUT the nested _hdr_name (its marker deleted with the parent's, cv10) is still emitted as an opaque val _hdr_name_1 (x0: int) over the str hash, so the public-entry selection (_off) is input-blind: TC-OK-PARTIAL / remaining: a law-free count-1 replace model (str_replace_first_o |
| s009 | `Module6_WhyMLTranspiler._transpile_modular` | Module6_WhyMLTranspiler.py | DEPTH-STOP | cs009_0:REFUSED; desk; cs009_NR:REFUSED | **CORRECT** cap-generic-fold-rc420-rebind | depth-0: namespace-dict writes at merged lines 10965.. (the body imports live modules incl. generic_fold: same #420 globals() rebinding as s291) / desk: the body does from module6_whyml.generic_fold import ...; the module-scope globals()[n] = _rc420_gate(n, fn) loop is a REAL rebinding (s291/cs291_NR measured the next wall); plus 209 body lines over Dict[str,Any] IR / MEASURED in stNR: next wall = generic_fold.py l.41459-41462 module-scope globals() rebinding (identical to cs291_NR) |
| s011 | `Module6_WhyMLTranspiler._wrap_call_with_callee_raises_assert` | Module6_WhyMLTranspiler.py | DEPTH-STOP | cs011_R:REFUSED | **BOUND** cap-vm-unerase-dict | replay r10xh123_3: MOVED (cv11 L3-TC irnode) to R325: _r521_v from r.get(..) on an Any/Dict[str,Any] callee record, asserted not None (route #521): a Dict[str,Any] value read = boundary |
| s012 | `Module6_WhyMLTranspiler.transpile` | Module6_WhyMLTranspiler.py (GIANT 1292 lines) | DEPTH-STOP | cs012_R:REFUSED; desk | **CORRECT** cap-generic-fold-rc420-rebind | replay r10xh126_2: name-rebinding refusal (namespace-dict writes in the merged program) / desk: transpile's body (live l.564-1980) does from module6_whyml.generic_fold import compute_pyval_list_walker_names (live l.1762): the same REAL #420 rebinding measured for s009/s291 (stNR); plus the 1400-line orchestrator over Dict[str,Any] IR (dict boundary) and copy/external walls |
| s013 | `_audit_one_prover` | audit_proof.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-R325-call-subprocess, cap-erased-to-builtin-slot-arg, cap-field-collection-writeback, cap-fs-path-model |
| s015 | `_index_proofs_dir` | audit_proof.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-exception-object-read, cap-fs-path-model, cap-return-exn-nonint |
| s019 | `ReverifyReport.summary` | audit_proof_reverify.py | TC-OK-PARTIAL | cs019_R:TC-OK | **TC-OK-PARTIAL** cap-float-str | replay r9xs004_4 at HEAD: TC-OK only through cv9's stand-ins for float->str / f-string float format / genexp sum (3 capabilities): unchanged |
| s020 | `_cache_key` | audit_proof_reverify.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-R325-str-encoding-op, cap-fs-path-model, cap-hashlib-model, cap-sorted-str-list, cap-str-join-array |
| s021 | `_cache_load` | audit_proof_reverify.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-fs-path-model, cap-json-model |
| s022 | `_cache_root` | audit_proof_reverify.py | TC-OK-FACADE | - | EXCLUDED (EXCL-external) | cap-fs-path-model |
| s023 | `_cache_store` | audit_proof_reverify.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-fs-path-model, cap-json-model |
| s024 | `_coqc_version` | audit_proof_reverify.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-R325-call-subprocess |
| s025 | `_lean_version` | audit_proof_reverify.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-R325-call-subprocess |
| s026 | `_sha256_file` | audit_proof_reverify.py | DEPTH-STOP | cs026_0:REFUSED | **EXT** cap-hashlib-model | depth-0: h = hashlib.sha256(); h.update(..) in a file-read loop: hashlib + filesystem (external, lvQ) |
| s027 | `_to_cache_payload` | audit_proof_reverify.py | DEPTH-STOP | cs027_0:L3-TC | **BOUND** cap-vm-unerase-dict | depth-0 L3-TC: returns a heterogeneous JSON payload dict {'compile_ok': bool, 'compile_stdout': str, .., 'elapsed': float, 'proofs': [..]}: a Dict[str,Any] value = boundary (and json-facing) |
| s028 | `verify_lean_file` | audit_proof_reverify.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-R325-call-subprocess, cap-context-manager-model, cap-fs-path-model, cap-sorted-key |
| s029 | `verify_rocq_file` | audit_proof_reverify.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-R325-call-subprocess, cap-context-manager-model, cap-fs-path-model, cap-heterogeneous-list |
| s030 | `_namedtuple_check_call` | core_ir_semantic.py | DEPTH-STOP | cs030_R:L3-TC | **STOP** cap-dict-of-tuple-values | replay r9xs016_3: L3-TC let (nfields, field_names, defaulted) = nt_arities[callee]: a Dict[str, Tuple[int, List[str], int]] value read (map string (option int)): a typed tuple-valued dict (inside the decision: not Any), then cv11's irnode wall |
| s031 | `_returns_literal_none` | core_ir_semantic.py | DEPTH-STOP | cs031_R:REFUSED; cs031_TP:TC-OK | **BOUND** cap-vm-unerase-any-tree | replay r9xs014_3: R325 false positive in the generated pv_size on the WhyML TYPE list ((l : list pyval)); stand-in = lvC's unlanded typepos.patch (scratchpad/lvC/typepos.patch, applied to stTP, applies cleanly at HEAD with a 2096-line offset) / stand-in stTP (typepos.patch) + cv9's lifted helper: TC-OK but a FACADE: the walk is input-blind (node_get_1 <hash> independent of node, typeof_op of a constant param tag, node_values_0 ()) and the lifted helper is a let rec with no variant; the honest form needs the Dict[str,Any] IR tree model (boundary) + closure-lift (rule 9 forbids the helper extraction cv9 used) |
| s033 | `run_ir_semantic_checks` | core_ir_semantic.py | DEPTH-STOP | cs033_R:L3-TC | **STOP** cap-vm-unerase-list | replay r9xs013_4: L3-TC Array.make 0 0 (array int) where array string is expected: an empty List[str] literal default typed int-array; 59-line driver of the semantic checks (then cv11 set-ctor + irnode walls) |
| s034 | `PyCSLError.__init__` | errors.py | TC-OK-FACADE | - | EXCLUDED (EXCL-decision(line>=0)) |  |
| s037 | `ConcurrencyChecker._walk_stmt` | frontend/ConcurrencyChecker.py | TC-OK-PARTIAL | cs037_R:TC-OK | **TC-OK-PARTIAL** cap-method-recursion-cycle | replay r9xs019_4 at HEAD: TC-OK only through cv9's 9 stand-in patches (pyast typing, recursion dropped): unchanged, 4 capabilities |
| s038 | `ConcurrencyChecker.check` | frontend/ConcurrencyChecker.py | DEPTH-STOP | cs038_0:REFUSED | **STOP** cap-self-field-alias-analysis | depth-0: self._thread_entries.add(..) on a self SET field (no certified lowering for a field receiver; cv11 cap-inplace-mutator-add + self-field alias analysis) |
| s041 | `_Harvester._build` | frontend/Module1_Ingestor.py | DEPTH-STOP | cs041_R:L3-TC | **STOP** cap-field-collection-writeback | replay r9xs023_4: L3-TC tgt.child_suites <- _cs_out on a ref-int target (a record field write-back through an erased element of a List[_Target]); + cv11 method recursion |
| s042 | `_Harvester._emit_suite` | frontend/Module1_Ingestor.py | TC-OK-PARTIAL | cs042_R:TC-OK | **TC-OK-PARTIAL** cap-method-recursion-cycle | replay (cv9 stand-in: the recursive self._emit_suite(child) dropped): TC-OK at HEAD, unchanged from cv11: the honest form needs the method recursion (termination over the suite tree) and the child-suite elements (iter_get over an erased list: input-blind footer arg) |
| s043 | `_Harvester._fold_blocks` | frontend/Module1_Ingestor.py | DEPTH-STOP | cs043_R:REFUSED | **STOP** cap-R325-str-concat-opaque | replay (10 patches; lvO's _match_block_hdr now converted so 2 GMISS): R325 folded += <str concat over an erased operand>: the fold accumulates into a local typed int (T2-like) mixed with tuple-unpack aliasing (cv11: str-join-array, str-encoding-op); 31-line body, not walked further |
| s044 | `_Harvester._make` | frontend/Module1_Ingestor.py | DEPTH-STOP | cs044_R:REFUSED | **STOP** cap-pyast-node-typing | replay r9xs022_3 (cv9's [T] made _Target.__init__ Any-typed): route #252 in _emit_block_footer (Any report_line into PyCSLContract(line_number: int)); desk (live l.293-340): type(node).__name__ dispatch, getattr(node, 'decorator_list', None), min([...], default=..), a lambda closure mk, tuple (_Target, List[List[stmt]]) returns: pyast-node typing + closure-lift, not one capability |
| s045 | `_Harvester._normalize_leading` | frontend/Module1_Ingestor.py | DEPTH-STOP | cs045_R:L3-TC; cs045_1:L3-TC; cs045_2:L3-TC; mlwx/cs045_x1:TC-OK | **CLOSE-STANDIN**  | replay (cv11's any(genexp) -> loop [R]; its _match_block_hdr stand-ins are now GMISS because lvO CONVERTED _match_block_hdr): L3-TC if _match_block_hdr(ln): the truth test of an Optional[Tuple[str,str]] result lowers to <> 0 on an option / [R] any(genexp) -> a for/break loop and the truth test -> 'is not None' (a non-None (kw, name) 2-tuple is always truthy: behaviour-identical): still L3-TC: (_match_block_hdr ln) = pycsl_none compares an option with the int None; and the non-block arm [ln.strip() for ln in raw_lines] lowers to an input-blind list_comp 0 / [R] the non-block arm [ln.strip() for ln in raw_lines] -> a for/append List[str] loop (honest str_strip_op per line); remaining L3-TC: the None test of the Optional[Tuple[str,str]] result / emission-level stand-ins on cs045_2.mlw (mlwx/cs045_x1.mlw, why3 --type-only rc 0): (match _match_block_hdr ln with None -> false \| Some _ -> true |
| s047 | `Module2_Parser.parse_contract` | frontend/Module2_Parser.py | DEPTH-STOP | cs047_0:REFUSED; cs047_1:REFUSED; cs047_3:REFUSED | **STOP** cap-ctor-with-calls-315 | depth-0 route #280: _ContractParser(contract_str).parse() (method call on a fresh constructor result) / [R] _cp = _ContractParser(contract_str); return _cp.parse(): route #506 in the CONVERTED _ContractParser._err (its f-string payload is unlowered once a caller catches _ContractSyntaxError) / [R] bind both f-strings to locals (in _err: a VERIFIED twin, costs a Module2 re-proof) => route #315: _ContractParser.__init__ calls _lex_contract (not a field initialiser), so the construction cannot be lowered; needs _ContractParser.__init__ converted (s048, cap-ctor-invariant-obligation) + a ctor-with-calls lowering + then the {e} read of the caught exception (cap-exception-object-read) |
| s048 | `_ContractParser.__init__` | frontend/Module2_Parser.py | DEPTH-STOP | cs048_R:REFUSED | **STOP** cap-method-recursion-cycle | replay r9xs028_3: MOVED from the route #226 ctor obligation to a method recursion cycle (_parse_atom -> _parse_atom through a METHOD call): the recursive-descent parser needs a termination measure across method edges (or the open #@ \diverges decision) |
| s051 | `_ContractParser._parse_act_block` | frontend/Module2_Parser.py | DEPTH-STOP | cs051_R:L3-TC | **STOP** cap-heterogeneous-list | replay r9xs034_2: L3-TC clauses: List[Given\|Requires\|..] gets IrRequires(..) where the list is typed given: a heterogeneous CSL clause list (cv11 cap-heterogeneous-list) + irnode |
| s053 | `_ContractParser._parse_assigns_target` | frontend/Module2_Parser.py | HONESTY-WALL | cs053_R:L3-TC | **STOP** cap-vm-callable-value | replay: L3-TC region := self._try(self._parse_assigns_region) (a bound-method value passed to the higher-order _try, unit in the model): callable values + the heterogeneous target list (cv11 HONESTY-WALL) |
| s054 | `_ContractParser._parse_atom_bs` | frontend/Module2_Parser.py | DEPTH-STOP | cs054_R:L3-TC | **STOP** cap-vm-unerase-irnode | replay r9xs043_2 (248-line body): L3-TC a SubscriptFieldAccess IR constructor result (emit_ir) returned where the mirror's _parse_atom_bs return is int: the CSL-node-as-IR return model (+ cv11 kind-judge-list-arg) |
| s057 | `_ContractParser._parse_contract` | frontend/Module2_Parser.py | DEPTH-STOP | cs057_0:REFUSED | **STOP** cap-re-match-model-ext | depth-0: R325 _m_di_group_1: the declared_in arm's _re.match(..) under import re as _re is outside lvO's gate (plain import re, str NAME subject); lvP measured past it: py_label record vs emit_ir (the record-vs-ADT seam of the label arm) |
| s058 | `_ContractParser._parse_datatype` | frontend/Module2_Parser.py | DEPTH-STOP | cs058_R:L3-TC | **STOP** cap-vm-unerase-list | replay r9xs037_2: L3-TC DatatypeDecl record (variants: List[Tuple[str, List[..]]] = any_array ()) returned where the mirror expects int: a record-with-list-of-tuple-fields value + the mirror retype of _parse_datatype's return (cv9: MIRROR-RETYPE + cap-vm-unerase-list) |
| s059 | `_ContractParser._parse_happy` | frontend/Module2_Parser.py | DEPTH-STOP | cs059_R:L3-TC | **STOP** cap-vm-unerase-union | replay r9xs035_2 (protects= dropped as cv9's stand-in): L3-TC happyproperty_param = !param (string vs int): HappyProperty.param / .target are Optional[str] fields and .protects Optional[List[str]] (all int in the record model): an Optional-scalar/list FIELD model (L); plus the dropped protects=[path] list field |
| s060 | `_ContractParser._parse_happy_targets` | frontend/Module2_Parser.py | DEPTH-STOP | cs060_R:L3-TC | **STOP** cap-vm-unerase-union | replay: L3-TC HappyProperty record built with Optional fields (protects/param/secret) = pycsl_none int where the record expects emit_ir/strings: the Optional-field record model (as s059) |
| s066 | `_lex_contract` | frontend/Module2_Parser.py | HONESTY-WALL | cs066_0:L3-TC; cs066_1:L3-TC | **STOP** cap-re-match-model-ext | depth-0 L3-TC: Tok record field _tok_string = m_group_0 () (int): m.group() / m.start() / m.lastgroup on _TOKEN_RE.match(source, pos) are outside lvO's gate (only m.group(k) with k literal, m.end()); then the (toks, source) tuple return of a record list (cv11 note) / [R] m is None -> not m, m.group() -> m.group(0), m.start() -> pos before the anchored match, _re.escape('\|') and P -> P with plain re; [S] m.lastgroup -> m.group(0); [T] -> Tuple[List[_Tok], str]: the re.Match model still does not apply (_TOKEN_RE_match_2 (str_hash_op source) pos is opaque: the compiled pattern is COMPUTED by '\|'.join(re.escape(o) for o in _OP_ALTERNATIVES), lvO's gate needs a literal); kind/group/end opaque => input-blind tokens. Needs the re model for a computed pattern + lastgroup (M) |
| s067 | `Module3_Weaver._attach_labels_and_ghost_assigns` | frontend/Module3_Weaver.py | DEPTH-STOP | cs067_R:L3-TC; cs067_R:L3-TC | **HONEST-WALL** cap-dict-items-iteration | replay of cv9 r9xs056_2 at HEAD: same terminal, L3-TC labels_by_line: Dict[int, List[str]] lowered map int (option int) (a TYPED-list-valued dict, not Dict[str,Any]) / read off the .mlw past the seam: for line, nodes in contracts_map.items() lowers to line = any int / nodes = any int (input-blind), python_ast: int, ast.walk opaque (ast_walk_1), setattr_3 ast_node <h> labels: needs a dict-items model + cap-pyast-node-attr-writeback; not one capability |
| s072 | `Module3_Weaver._expand_happy_properties` | frontend/Module3_Weaver.py (GIANT 800 lines) | DEPTH-STOP | cs072_R:REFUSED | **STOP** cap-identity-vs-literal | replay (794 lines, GIANT): identity test on a CSLNode field value (route #498) |
| s074 | `Module3_Weaver._field_write_site` | frontend/Module3_Weaver.py | DEPTH-STOP | cs074_R:L3-TC | **BOUND** cap-vm-unerase-dict | replay: L3-TC returns a site dict {'kind': .., 'node': .., ..} (any_map) where the mirror expects int: a Dict[str,Any] site record = boundary (+ cv11 growable-list-local, return-exn-nonint) |
| s075 | `Module3_Weaver._happy_predicate` | frontend/Module3_Weaver.py | HONESTY-WALL | cs075_R:REFUSED | **STOP** cap-R325-call-deepcopy | replay (9 patches): R325 copy.deepcopy(..) of a CSL node (no model) + nested closure + pyast unparse (cv11 HONESTY-WALL) |
| s076 | `Module3_Weaver._parse_extracted_contracts` | frontend/Module3_Weaver.py | DEPTH-STOP | cs076_0:REFUSED; cs076_1:REFUSED | **STOP** cap-R489-imported-callee-frame | depth-0 route #280: trailing_contracts_map.setdefault(k, []).extend(parsed_nodes) / [R] d[k] = d.get(k, []) + parsed_nodes (behaviour-identical: the lists are created and held only by this local dict) clears #280; next wall R489: self.parser_module.parse_node_contracts is the LIVE Module2_Parser def (imported under --import-path, no #@ assigns), its body reaches the program dunder AST.__repr__ through self.parse_contract: a cross-module inferred-frame wall (the mirror's own Module2 twin has assigns \nothing but is not what is imported); then Dict[int, List[CSLNode]] typed-value maps + a 2-dict tuple return |
| s077 | `Module3_Weaver._region_bound_str` | frontend/Module3_Weaver.py | HONESTY-WALL | cs077_0:REFUSED | **STOP** cap-erased-to-builtin-slot-arg | depth-0: route #252: an erased CSL-node payload returned through -> str (str(node.value) of a CSL Number / Var name); cv11: float-str + getattr-dynamic + irnode |
| s078 | `Module3_Weaver._subscript_read_site` | frontend/Module3_Weaver.py | DEPTH-STOP | cs078_R:L3-TC | **STOP** cap-vm-unerase-irnode | replay r9xs046_5: L3-TC an emit_ir (sub.subscript_value) where int is expected in the pyast attribute chain test: the pyast/IR node seam |
| s079 | `Module3_Weaver._subst_csl_param` | frontend/Module3_Weaver.py | HONESTY-WALL | cs079_0:REFUSED | **STOP** cap-method-recursion-cycle | depth-0: _subst_csl_param recurses through a method call (CSL tree walk): termination measure across method edges; then dataclass reflection (cv11) |
| s080 | `Module3_Weaver._synthesize_selfcomp` | frontend/Module3_Weaver.py | HONESTY-WALL | cs080_0:REFUSED | **STOP** cap-closure-lift | depth-0 (153 lines): the nested _call captures formal, hp, secset (not faithfully liftable) + pyast ctor model + deepcopy (cv11 HONESTY-WALL) |
| s081 | `Module3_Weaver.process` | frontend/Module3_Weaver.py (GIANT 2226 lines) | DEPTH-STOP | cs081_0:REFUSED | **STOP** cap-binder-hygiene-R327 | depth-0 (2226 lines, GIANT): R327 _cc_a vs the _cc_ binder namespace |
| s082 | `PyCSLWeaver._attach_loop_contracts` | frontend/Module3_Weaver.py | DEPTH-STOP | cs082_R:REFUSED | **STOP** cap-pyast-node-attr-writeback | replay: node.csl_variants.append(..) on an ast node field list (not a growable local): pyast node attr write-back + field-collection write-back |
| s083 | `PyCSLWeaver._desugar_acts` | frontend/Module3_Weaver.py | DEPTH-STOP | cs083_R:L3-TC | **STOP** cap-vm-unerase-irnode | replay r9xs045_2: same terminal: L3-TC the requires record { binop_left = !a ..} gets a CSL node (int) where emit_ir is expected: the CSL-node-as-IR value model |
| s086 | `PyCSLWeaver._subst_var` | frontend/Module3_Weaver.py | HONESTY-WALL | cs086_TP:REFUSED | **STOP** cap-static-method-class-call | stand-in stTP: the typepos false positive is gone; next wall R325 in the caller _desugar_for: PyCSLWeaver._subst_var(..) (a staticmethod called through the class name) lowers to an opaque pyCSLWeaver__subst_var_3 int; then (cv11) dataclasses.fields/replace reflection on the CSL node (cap-dataclass-reflection) + the CSL-node IR model |
| s087 | `PyCSLWeaver.visit_ClassDef` | frontend/Module3_Weaver.py | DEPTH-STOP | cs087_R:L3-TC | **STOP** cap-pyast-node-attr-writeback | replay (95 lines): L3-TC setattr on the ast.ClassDef node record (csl_* attributes): pyast node attr write-back |
| s088 | `PyCSLWeaver.visit_For` | frontend/Module3_Weaver.py | DEPTH-STOP | cs088_R:L3-TC | **STOP** cap-pyast-node-attr-writeback | replay: L3-TC setattr on the ast.For node (node.csl_invariants = ..): pyast node attribute write-back (+ method-arg frame) |
| s089 | `PyCSLWeaver.visit_FunctionDef` | frontend/Module3_Weaver.py | DEPTH-STOP | cs089_R:REFUSED | **STOP** cap-method-arg-frame | replay: route #316 in the callee _dispatch_function_contracts: it writes its ast node argument, which lowers to int and cannot be framed: pyast-node method-arg frame + attr writeback |
| s090 | `PyCSLWeaver.visit_Module` | frontend/Module3_Weaver.py | DEPTH-STOP | cs090_0:REFUSED | **STOP** cap-inplace-mutator-add | depth-0: self._csl_bound_names.add(..) on a self set field (no certified lowering on a field receiver) + cv11 computed-receiver mutator |
| s091 | `PyCSLWeaver.visit_While` | frontend/Module3_Weaver.py | DEPTH-STOP | cs091_R:L3-TC | **STOP** cap-pyast-node-attr-writeback | replay: L3-TC setattr on the ast.While node (csl loop contracts): pyast node attribute write-back |
| s092 | `PyCSLWeaver.visit_With` | frontend/Module3_Weaver.py | DEPTH-STOP | cs092_R:L3-TC; desk | **STOP** cap-pyast-node-attr-writeback | replay r9xs050_2: L3-TC self.contracts_map: Dict[int, List[CSLNode]] field read seq int vs int / desk (live body l.438-472): node.csl_critical_mutex / csl_acquires / csl_releases stores on the ast.With node + self.generic_visit(node) (trusted NodeVisitor dispatch, cap-dynamic-getattr-method-dispatch): two further capabilities after the dict typing |
| s093 | `Module5_IREmitter.generate_json` | frontend/Module5_IREmitter.py | DEPTH-STOP | cs093_NR:REFUSED; cs093_NR:REFUSED; desk | **EXT** cap-json-model | stand-in stNR + PyCSLToJSONEmitter.__init__ ported too (its only allocation site): the trigger is setattr(_n,_f,_c) in live frontend/desugar.py:404 (normalize_stores, imported by the body) / next wall: _r42_stack.pop() (route #42 walk over emitter.program_ir: List[Any]); desk: then _r42_n['op'] = ... item store through an Any element of a Dict[str,Any] tree (dict-model boundary) and json.dumps (external, lvQ) / desk: return json.dumps(emitter.program_ir, indent=indent) |
| s094 | `PyCSLToJSONEmitter.__init__` | frontend/Module5_IREmitter.py | DEPTH-STOP | cs093_NR:REFUSED; cs094_0:REFUSED | **STOP** cap-boolop-value | converts only with generate_json (vacuous alone): same chain as s093 / depth-0 alone: and/or used as a VALUE on non-bool operands in the __init__ body (it was TC-OK in cv11's s094_1); in the generate_json combo (cs093_NR) it did not stop there: converting it is vacuous anyway without generate_json |
| s095 | `PyCSLToJSONEmitter._build_function_ir` | frontend/Module5_IREmitter.py (GIANT 1465 lines) | DEPTH-STOP | cs095_0:REFUSED | **STOP** cap-binder-hygiene-R327 | depth-0 (1464 lines, GIANT): R327 _r230_ binder namespace collision |
| s096 | `PyCSLToJSONEmitter._build_function_symbol_table` | frontend/Module5_IREmitter.py | DEPTH-STOP | cs096_R:REFUSED | **BOUND** cap-inplace-mutator-setdefault | replay (377 lines): dict_key_types.setdefault(..) on a local Dict of symbol-table type tags built from pyast annotations: no certified setdefault lowering, over Dict[str,Any] symtabs |
| s097 | `PyCSLToJSONEmitter._collect_class_fields` | frontend/Module5_IREmitter.py | DEPTH-STOP | cs097_R:REFUSED | **STOP** cap-vm-irnode-R1-narrowing-view | replay (462 lines): R567 rhs.func of a value isinstance-tested against a NON-IR class (the R1 per-receiver view built in run #6 does not cover record-modelled receivers): unchanged from lvP |
| s101 | `PyCSLToJSONEmitter._collect_union_arms` | frontend/Module5_IREmitter.py | DEPTH-STOP | cs101_0:REFUSED | **STOP** cap-inplace-mutator-pop | depth-0: stack.pop() on a local worklist of pyast annotation nodes (no certified pop; lvB's fresh-local lowering is not landed at HEAD) then pyast-node typing of the Union arms |
| s103 | `PyCSLToJSONEmitter._csl_in` | frontend/Module5_IREmitter.py | DEPTH-STOP | cs103_0:L3-TC; cs103_T1:REFUSED | **STOP** cap-R579-csl-class-resolution | depth-0 L3-TC: node.cslin_element (CSLIn field typed CSLNode -> int) passed to _csl_to_ir (ExprIR) / [T] CSLIn.element/collection -> 'ExprIR' (in the LIVE frontend/Module2_Parser.py of the scratch tree: the mirror imports the live class): next wall route #579: node.collection.func after isinstance(node.collection, CallExpr) -- CallExpr is a CSL class imported from Module2, not a resolved pycsl IR class: the CSL-node value model (cap-vm-unerase-irnode for CSL nodes, XL) |
| s104 | `PyCSLToJSONEmitter._csl_list_to_ir` | frontend/Module5_IREmitter.py | DEPTH-STOP | cs104_0:REFUSED | **STOP** cap-emit-ir-item-store-model | depth-0 R566: an item store into an IR-typed dict in a @mutable_state class (IR nodes are immutable values: the recorded #566 boundary) + getattr-dynamic |
| s105 | `PyCSLToJSONEmitter._detect_array_dimensions` | frontend/Module5_IREmitter.py | DEPTH-STOP | cs105_R:REFUSED | **STOP** cap-closure-lift | replay: the nested _collect_augextend captures strict_array_cands: not faithfully liftable (pass captures as params + unique name: an [R] that edits a nested def), then cv11 elem-store-nonlist over pyast nodes |
| s108 | `PyCSLToJSONEmitter._emit_protocol_interface` | frontend/Module5_IREmitter.py | DEPTH-STOP | cs108_0:REFUSED | **BOUND** cap-inplace-mutator-computed-receiver | depth-0 route #280: .append on a computed receiver (an entry of the Dict[str,Any] protocol IR): boundary |
| s110 | `PyCSLToJSONEmitter._encode_callable_annotation` | frontend/Module5_IREmitter.py | DEPTH-STOP | cs110_0:L3-TC | **STOP** cap-vm-unerase-irnode | depth-0: L3-TC iter_length (args_of !slice_node) (array emit_ir) where int is expected: the pyast-node-as-IR seam of a Callable[[..], R] annotation (cv11 irnode + list) |
| s111 | `PyCSLToJSONEmitter._field_type_from_annotation_inst` | frontend/Module5_IREmitter.py | DEPTH-STOP | cs111_0:L3-TC | **STOP** cap-missing-mirror-sibling | depth-0 L3-TC: self._m5_tuple_record_name(..) has NO mirror twin (an opaque int val); adding a sibling stub would be a new \trusted (rule 8), so the sibling must be ported verified first (it and _m5_tuple_slot_tags are small staticmethods), then pyast annotation typing |
| s112 | `PyCSLToJSONEmitter._get_mutex_invariant_ir` | frontend/Module5_IREmitter.py | DEPTH-STOP | cs112_0:L3-TC; cs112_1:L3-TC | **STOP** cap-optional-irnode-return | depth-0: mirror stub signature is -> int (live Optional[Dict[str, Any]]); L3-TC raise (Return_emit_ir pycsl_none) / [T] -> Optional["ExprIR"]: same L3-TC, the Optional IR return is lowered as plain emit_ir with None = int: needs an Optional[ExprIR] return codomain (cv11 cap-vm-unerase-union for an IR arm; Module5 already has iropt_str readers, not an IR option); then self._mutex_invariants_csl.get(mutex) (Dict[str, CSLNode] field) and the converted callers' bespoke mutex_invariant_ir reader must agree with the converted body |
| s113 | `PyCSLToJSONEmitter._m5_get_type_name` | frontend/Module5_IREmitter.py | DEPTH-STOP | cs113_R:REFUSED; cs113_2:REFUSED; cs113_3:L3-TC | **STOP** cap-optional-str-return | replay: route #175: except Exception after except PyCSLIRError: raise -- handler matching knows only the builtin hierarchy (the earlier specific handler already decides the PyCSLIRError path) / [S] stand-in except Exception -> except ValueError (x3) for the hierarchy model: next wall route #350: the mirror stub signature has dedup: int=None (live dedup: bool = False): a [T] fix / [T] dedup: bool = False: next L3-TC raise (Return_str !_pth): _pth = self._m5_...(annotation) returns Optional[str] from trusted/converted helpers typed int; 3 links walked (hierarchy stand-in, [T], now the Optional[str] callee typing), 66-line body with ~10 helper calls still ahead |
| s115 | `PyCSLToJSONEmitter._match_pattern_to_ir` | frontend/Module5_IREmitter.py | DEPTH-STOP | cs115_R:REFUSED | **STOP** cap-method-recursion-cycle | replay: _match_pattern_to_ir self-recursion through a METHOD call (pattern tree): termination across method edges |
| s116 | `PyCSLToJSONEmitter._normalize_literal_annotation` | frontend/Module5_IREmitter.py | DEPTH-STOP | cs116_R:L3-TC | **STOP** cap-pyast-node-typing | replay: L3-TC val_elts := (if isinstance(inner, Tuple) then list(inner.elts) else [inner]): a pyast list field vs an int-erased node (66-line body) |
| s117 | `PyCSLToJSONEmitter._normalize_union_annotation` | frontend/Module5_IREmitter.py | DEPTH-STOP | cs117_R:REFUSED | **STOP** cap-getattr-dynamic | replay (100 lines): getattr(self, '_union_synth_cache', ..) where the name is bound in the MRO but not an instance field (route #396/#397: cv11 getattr-dynamic) + nested-unpack target |
| s118 | `PyCSLToJSONEmitter._populate_protocol_conformance` | frontend/Module5_IREmitter.py | DEPTH-STOP | cs118_0:REFUSED | **BOUND** cap-inplace-mutator-setdefault | depth-0: self.program_ir.setdefault(..) on the Dict[str,Any] program IR: boundary |
| s120 | `PyCSLToJSONEmitter._py_expr_fstring` | frontend/Module5_IREmitter.py | DEPTH-STOP | cs120_R:L3-TC | **STOP** cap-vm-unerase-irnode | replay r9xs093_2: L3-TC parts := snoc (self._py_expr_to_ir(v.value)) where parts is int-typed: a List[ExprIR] local of IR results (+ cv11 method recursion through the format spec) |
| s121 | `PyCSLToJSONEmitter._py_stmts_to_ir` | frontend/Module5_IREmitter.py | DEPTH-STOP | cs121_R:REFUSED | **STOP** cap-method-recursion-cycle | replay: _py_stmt_match <-> _py_stmts_to_ir mutual recursion through METHOD calls: termination across method edges |
| s125 | `PyCSLToJSONEmitter.visit_ClassDef` | frontend/Module5_IREmitter.py (GIANT 640 lines) | DEPTH-STOP | cs125_0:REFUSED | **STOP** cap-binder-hygiene-R327 | depth-0 (625 lines, GIANT): R327 _class_ binder namespace collision |
| s126 | `PyCSLToJSONEmitter.visit_FunctionDef` | frontend/Module5_IREmitter.py | DEPTH-STOP | cs126_R:REFUSED | **BOUND** cap-inplace-mutator-setdefault | replay: self.program_ir.setdefault(..) on the Dict[str,Any] program IR field: boundary |
| s127 | `PyCSLToJSONEmitter.visit_Module` | frontend/Module5_IREmitter.py (GIANT 1309 lines) | DEPTH-STOP | cs127_R:REFUSED | **CORRECT** cap-import-system-local-module | replay r9xs069_2: route #326 import-system refusal: the 1308-line visit_Module body calls __import__ with frontend resolved to a local file (a REAL dynamic import; pycsl resolves imports statically) |
| s128 | `_ChainDesugarer.visit_Compare` | frontend/desugar.py | DEPTH-STOP | cs128_0:REFUSED | **STOP** cap-R325-call-ast-ctor | depth-0: R325 link = ast.Compare(..) (a pure_ast node constructor call with no model) appended to links; then node attr write-back (cv11) |
| s129 | `_try_reaches_assert` | frontend/desugar.py | REFUSED-termination | - | EXCLUDED (EXCL-decision(diverges)) | cap-R325-call-ast-walk, cap-diverges |
| s130 | `normalize_stores` | frontend/desugar.py | HONESTY-WALL | cs130_0:REFUSED | **STOP** cap-dynamic-getattr-setattr | depth-0: setattr(node, field, ..) with a non-literal field in normalize_stores' own body (the same desugar.py site that blocks generate_json): dynamic attribute model on AST nodes |
| s131 | `_ExecSplicer.visit_Expr` | frontend/exec_splice.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-R325-call-ast-parse, cap-R506-trigger-site, cap-pyast-ctor-model |
| s132 | `_stub_set` | frontend/import_classifier.py | TC-OK-FACADE | - | EXCLUDED (EXCL-external) | cap-fs-path-model, cap-vm-unerase-str |
| s133 | `check_imports` | frontend/import_classifier.py | DEPTH-STOP | cs133_R:L3-TC | **STOP** cap-pyast-node-typing | replay r9xs093_3: L3-TC collect_imports(tree): the converted callee takes tree as pyval while check_imports' ast.AST parameter lowers to int; then stubs = _stub_set(stub_dir) is the filesystem facade (external, lvQ) so the result is input-blind on the stub set |
| s135 | `_Inliner._hoist_calls_in_expr` | frontend/ir_inline.py | DEPTH-STOP | cs135_0:REFUSED | **BOUND** cap-inplace-mutator-extend | depth-0: pre.extend(..) on a parameter list of Dict[str,Any] IR statements (no certified lowering for a param receiver) + method-arg frame: boundary |
| s136 | `_Inliner.inline_stmts` | frontend/ir_inline.py | DEPTH-STOP | cs136_R:REFUSED | **BOUND** cap-R274-writing-call-in-comprehension | replay (7 patches): R274 self.inline_stmts (writing) inside a comprehension; over Dict[str,Any] IR statement lists: boundary |
| s137 | `_inline_calls` | frontend/ir_inline.py | CERTIFIED-BOUNDARY | cs137_0:REFUSED | **BOUND** cap-inplace-mutator-update | depth-0 (78 lines): _cb.update(..) dict mutator over Dict[str,Any] inline-candidate maps (cv11 CERTIFIED-BOUNDARY: certified-boundary-escape) |
| s138 | `_recursive_methods` | frontend/ir_inline.py | DEPTH-STOP | cs138_R:REFUSED | **BOUND** cap-R274-writing-call-in-comprehension | replay r9xs074_6: R274 the nested reaches_self (writes its local seen/stack) called inside the set comprehension; desk: a closure over edges = {name: _method_edges(f, ..) for name, f in fmap.items()} of Dict[str,Any] function IRs (f.get('self_type')): closure-lift + the dict boundary |
| s139 | `apply_inline_globals` | frontend/ir_inline.py | CERTIFIED-BOUNDARY | cs139_0:REFUSED | **BOUND** cap-inplace-mutator-pop | depth-0: f.pop(..) on a Dict[str,Any] function IR (cv11 CERTIFIED-BOUNDARY: certified-boundary-escape): boundary |
| s140 | `_find_record_type_from_dep_imports` | frontend/ir_resolve.py | DEPTH-STOP | cs140_R:L3-TC | **STOP** cap-vm-unerase-union | replay: L3-TC sub_resolved := _resolve_module_path(..): an Optional[Path] union return assigned to an int local (union + cv9's _cv9_str/_cv9_int helper stand-ins over Dict[str,Any] import records; the module path resolution is filesystem-facing) |
| s142 | `_inject_functions` | frontend/ir_resolve.py | DEPTH-STOP | cs142_0:REFUSED | **BOUND** cap-inplace-mutator-computed-receiver | depth-0 route #280: .insert on a computed receiver (ir['functions'] of the Dict[str,Any] dependency IR): boundary |
| s144 | `_resolve_direct_imports` | frontend/ir_resolve.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-R325-call-ast-parse, cap-defaultdict-list, cap-fs-path-model, cap-import-system-local-module |
| s145 | `_resolve_imported_base_classes` | frontend/ir_resolve.py | DEPTH-STOP | cs145_R:REFUSED | **BOUND** cap-inplace-mutator-setdefault | replay: ir_data.setdefault(..) on the Dict[str,Any] program IR (no certified lowering; the receiver is a Dict[str,Any] = boundary) |
| s147 | `_resolve_module_imports` | frontend/ir_resolve.py | DEPTH-STOP | cs147_R:REFUSED | **BOUND** cap-R542-any-container | replay: route #542: all_calls (collected from Dict[str,Any] function IRs) iterated while it may be a number: the IR value model (boundary) |
| s148 | `_resolve_module_path` | frontend/ir_resolve.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-fs-path-model, cap-import-system-local-module |
| s149 | `_resolve_wildcard_imports` | frontend/ir_resolve.py | DEPTH-STOP | cs149_R:REFUSED | **STOP** cap-dict-alias | replay: list alias refusal: dep_funcs may BE needed_names (a call may return its argument) and is passed to the mutating _inject_functions: a may-alias analysis (M); over Dict[str,Any] dependency IRs |
| s150 | `_strip_dir_scan_proofs` | frontend/ir_resolve.py | HONESTY-WALL | cs150_R:REFUSED | **BOUND** cap-vm-unerase-dict | replay: R325 out = dict(ir) (a Dict[str,Any] IR copy, no model) then out['..'] = kept: boundary |
| s151 | `apply_composition` | frontend/ir_resolve.py | DEPTH-STOP | cs151_0:REFUSED | **STOP** cap-binder-hygiene-R327 | depth-0 (229 lines): R327 locals C and c both lower to c (a live rename, S); cv11's next wall cap-closure-lift; Dict[str,Any] composition IRs after |
| s154 | `resolve_imports` | frontend/ir_resolve.py | DEPTH-STOP | cs154_R:REFUSED | **BOUND** cap-erased-to-builtin-slot-arg | replay (346-line body): route #252: Any-typed import records flow into _resolve_module_path(level: int, main_file: str, ..): typing the Dict[str,Any] import record = boundary |
| s155 | `collect_module_constants` | frontend/module_collect.py | HONESTY-WALL | cs155_0:REFUSED | **STOP** cap-getattr-dynamic | depth-0: R325 in the callee _module_const_int: getattr(node, <dynamic>) on an ast constant (cv11: getattr-unknown, dict-comp, unbound symbol, none-fold-unpack) |
| s156 | `collect_module_globals` | frontend/module_collect.py | HONESTY-WALL | cs156_0:REFUSED | **STOP** cap-getattr-dynamic | depth-0: R325 target from getattr(node, <dynamic>) on an ast node (cv11: getattr-unknown, dict-comp, none-fold-unpack) |
| s157 | `_check_gt4_polymorphic_recursion` | frontend/monomorphize.py | DEPTH-STOP | cs157_0:REFUSED | **STOP** cap-pyast-node-typing | depth-0: R325 in the converted callee _extract_ast_subscript: node from the opaque ast.walk (_ast_walk_1) pattern-matched as a pyval: the stdlib ast.walk over pyast nodes (+ set ctor) |
| s158 | `_collect_instantiations` | frontend/monomorphize.py | DEPTH-STOP | cs158_R:REFUSED | **BOUND** cap-iterable-termination-variant | replay: a for loop over an iterable whose length term reads an erased (any) value has no legal variant; the iterable is a Dict[str,Any] IR walk (binding it to a typed local needs the IR value typed: boundary) |
| s160 | `_record_classification` | frontend/monomorphize.py | DEPTH-STOP | cs160_0:REFUSED | **BOUND** cap-inplace-mutator-setdefault | depth-0: ir_data.setdefault(..) on the Dict[str,Any] program IR: boundary |
| s161 | `_rewrite_annotation_str` | frontend/monomorphize.py | HONESTY-WALL | cs161_R:L3-TC | **STOP** cap-re-match-model-ext | replay s161 (lvO): L3-TC Map.get rename_map (any int): the key comes from a match group on an Any-typed subject (outside lvO's gate: str NAME subject) and the tuple-key dict; needs the re.Match model for an Any subject + a typed key |
| s162 | `_rewrite_annotations` | frontend/monomorphize.py | DEPTH-STOP | cs162_R:REFUSED | **BOUND** cap-elem-store-nonlist | replay: element store through a value the model does not represent as a list (an annotation slot inside a Dict[str,Any] function IR): boundary |
| s164 | `_rewrite_subscript_calls_in_stmt` | frontend/monomorphize.py | HONESTY-WALL | cs164_TP:L3-TC | **BOUND** cap-vm-unerase-dict | stand-in stTP: next L3-TC raise (Return !new): new = dict(stmt) / {**stmt} is a Dict[str,Any] IR statement copy returned where the mirror expects int: a Dict[str,Any] value = dict-model boundary |
| s165 | `_rewrite_subscript_to_name` | frontend/monomorphize.py | HONESTY-WALL | cs165_TP:L3-TC | **STOP** cap-pyast-node-typing | stand-in stTP + r9xs114_2: L3-TC ct := _type_str !slice_node: an ast Subscript's slice (int) passed to a converted callee typed pyval: pyast-node typing (cv11: r325-typepos + irnode) |
| s169 | `Ellipsis.__new__` | frontend/pure_ast.py | HONESTY-WALL | cs169_0:REFUSED | **CORRECT** cap-ub76-new-singleton | depth-0: UB-7.6 a non-trivial __new__ (the Ellipsis singleton): a correctness rule (object identity of a singleton), not a capability gap |
| s170 | `NodeTransformer.generic_visit` | frontend/pure_ast.py | HONESTY-WALL | cs170_0:REFUSED | **STOP** cap-dynamic-getattr-setattr | depth-0: setattr(node, field, new_node) / delattr(node, field) with non-literal field names (the NodeTransformer protocol): dynamic attribute model + generator iter_fields (cv11 HONESTY-WALL) |
| s171 | `NodeVisitor.generic_visit` | frontend/pure_ast.py | HONESTY-WALL | cs171_0:REFUSED | **STOP** cap-generator-yield-model | depth-0: route #542 for field, value in iter_fields(node) (a generator lowered as int) + dynamic method dispatch |
| s172 | `NodeVisitor.visit` | frontend/pure_ast.py | HONESTY-WALL | cs172_0:REFUSED | **STOP** cap-dynamic-getattr-method-dispatch | depth-0: route #309 getattr(self, 'visit_' + name, self.generic_visit): a non-literal method lookup with a non-literal default = dynamic dispatch on the visitor (cv11 HONESTY-WALL) |
| s173 | `NodeVisitor.visit_Constant` | frontend/pure_ast.py | HONESTY-WALL | cs173_0:REFUSED | **STOP** cap-method-arg-frame | depth-0: route #316 in the trusted callee NodeVisitor.generic_visit (writes its ast node argument, unframeable int) + dynamic dispatch (cv11) |
| s174 | `_Parser.__init__` | frontend/pure_ast.py | DEPTH-STOP | cs174_R:REFUSED | **STOP** cap-method-recursion-cycle | replay: the whole recursive-descent _Parser (~40 methods) forms a method recursion cycle once __init__ converts: termination measure across method edges (or #@ \diverges, an open decision) |
| s175 | `_Parser._fin` | frontend/pure_ast.py | DEPTH-STOP | cs175_R:L3-TC | **BOUND** cap-emit-ir-inplace-field-write | replay r10xh.. ([T] end_tok: Optional[_Tok]): L3-TC et := end_tok, an Optional record narrowed by 'is not None' in a conditional expression; desk: then node.lineno / col_offset / end_lineno stores on the immutable emit_ir node (the recorded CORRECTNESS boundary of in-place IR field writes) |
| s176 | `_Parser._fin_block` | frontend/pure_ast.py | HONESTY-WALL | cs176_R:L3-TC | **STOP** cap-dynamic-getattr-setattr | replay: L3-TC _max_end(getattr(node, <dynamic>)) : pycsl_getattr_unknown int where a pytuple_int_int position is expected: dynamic getattr on an AST node + in-place emit_ir field writes |
| s177 | `_Parser._max_end` | frontend/pure_ast.py | TC-OK-PARTIAL | cs177_R:TC-OK | **TC-OK-PARTIAL** cap-dynamic-getattr-setattr | replay at HEAD: TC-OK only through cv10's stand-ins (dynamic getattr of position fields, recursion): unchanged |
| s178 | `_Parser._slice` | frontend/pure_ast.py | DEPTH-STOP | cs178_R:L3-TC | **STOP** cap-self-field-untyped-ctor | replay: L3-TC the _Parser state record (toks: array _tok, i, _lines: array int vs the declared tuple types) built by a constructor whose fields are untyped (cv11 cap-self-field-untyped-ctor) + method recursion |
| s180 | `_Parser.node` | frontend/pure_ast.py | DEPTH-STOP | cs180_R:L3-TC | **STOP** cap-pyast-dynamic-ctor | replay: L3-TC return !n (int) where emit_ir is expected: n = _N(kind)(**fields) builds an AST node by a dynamic class lookup |
| s182 | `_Precedence.next` | frontend/pure_ast.py | DEPTH-STOP | cs182_R:REFUSED | **STOP** cap-enum-value-lookup | replay: route #339: _Precedence(self.value + 1) enum value lookup (may raise ValueError); needs an enum value model (M) |
| s183 | `_Unparser.__init__` | frontend/pure_ast.py | DEPTH-STOP | - | EXCLUDED (EXCL-external) | cap-context-manager-model |
| s185 | `_Unparser._write_docstring_and_traverse_body` | frontend/pure_ast.py | TC-OK-PARTIAL | cs185_R:TC-OK | **TC-OK-PARTIAL** cap-effectful-callback | replay at HEAD: TC-OK as in cv11 but partial: node: int (pyast erased), the docstring and traverse callees are opaque vals over get_body node, writes { } although the callees write _pyobj_state (fresh/self frame) |
| s186 | `_Unparser._write_fstring_inner` | frontend/pure_ast.py | DEPTH-STOP | cs186_R:L3-TC | **STOP** cap-raises-clause-propagation | replay (cv11 spec incl. raises ValueError on the stub): L3-TC 'raises unlisted exception ValueError' in the VERIFIED caller _Unparser.visit_FormattedValue (let rec): converting the stub makes its ValueError visible to callers whose contracts do not list it: the callers' raises clauses must be widened (verified-contract changes, a pure_ast re-proof ~3 h) -- a truthful [T] on verified twins, then cv11's method recursion |
| s187 | `_Unparser.buffered` | frontend/pure_ast.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-context-manager-model, cap-generator-yield-model |
| s188 | `_Unparser.delimit_if` | frontend/pure_ast.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-context-manager-model, cap-self-field-alias-analysis, cap-effectful-callback |
| s190 | `_Unparser.interleave` | frontend/pure_ast.py | HONESTY-WALL | cs190_0:REFUSED | **STOP** cap-effectful-callback | depth-0: R325 seq = iter(seq); f(next(seq)): an iterator protocol + a callable parameter f (effectful callback, cv11) |
| s191 | `_Unparser.items_view` | frontend/pure_ast.py | HONESTY-WALL | cs191_0:L3-TC | **STOP** cap-vm-callable-value | depth-0 L3-TC: traverser(items[0]) where traverser is a callable PARAMETER (int in the model): callable values + effectful callback |
| s192 | `_Unparser.set_precedence` | frontend/pure_ast.py | DEPTH-STOP | cs192_0:REFUSED | **STOP** cap-vm-unerase-dict | depth-0: element store self._precedences[node] = precedence through a non-list value: a Dict[node, _Precedence] keyed by AST nodes (object-identity keys, enum values) |
| s193 | `_Unparser.visit_BoolOp` | frontend/pure_ast.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-context-manager-model, cap-effectful-callback, cap-global-nonlocal-write |
| s194 | `_Unparser.visit_Dict` | frontend/pure_ast.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-context-manager-model, cap-effectful-callback |
| s195 | `_Unparser.visit_JoinedStr` | frontend/pure_ast.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-context-manager-model, cap-self-field-alias-analysis, cap-effectful-callback |
| s196 | `_Unparser.visit_Lambda` | frontend/pure_ast.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-context-manager-model, cap-self-field-alias-analysis, cap-effectful-callback |
| s197 | `_Unparser.visit_MatchClass` | frontend/pure_ast.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-builtin-kwarg-zip-strict, cap-context-manager-model, cap-effectful-callback |
| s198 | `_Unparser.visit_MatchMapping` | frontend/pure_ast.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-builtin-kwarg-zip-strict, cap-context-manager-model, cap-effectful-callback |
| s199 | `_Unparser.visit_arguments` | frontend/pure_ast.py | DEPTH-STOP | cs199_0:L3-TC | **STOP** cap-pyast-node-typing | depth-0 L3-TC: for a, d in elements (zip of node.args with padded defaults) -- the elements of a pyast list zip are int: pyast list fields + zip pairs; 49-line body of writes (cap-effectful-callback) |
| s200 | `_Unparser.write` | frontend/pure_ast.py | HONESTY-WALL | cs200_0:REFUSED | **STOP** cap-self-field-alias-analysis | depth-0: self._source.extend(text) (varargs *text) on a self List[str] field; an [R] self._source = self._source + list(text) would change the list's IDENTITY, which _Unparser's buffered() save/restore observes: needs a self-field in-place extend model (cv11: effectful-callback + self-field alias) |
| s201 | `_build_nodes` | frontend/pure_ast.py | DEPTH-STOP | cs201_NR:REFUSED; cs201_NR:REFUSED | **CORRECT** cap-dynamic-class-type-ctor | stand-in stNR (Module3_Weaver rebinding refusal disabled): next wall / route #405: _build_nodes creates the AST node classes with type(name,(base,),body); outside the closed class world (route #405 refusal is a soundness rule, not a capability gap) |
| s202 | `_decode_escapes` | frontend/pure_ast.py | DEPTH-STOP | cs202_R:REFUSED | **STOP** cap-R325-module-constant-dict | replay: R325 _SIMPLE_ESCAPES (a module-level str->str dict constant) read by subscript: cv10 S-M module-constant dict model; then chr(int(x, 16)) and bytes (cv11) |
| s203 | `_decode_fstring_middle` | frontend/pure_ast.py | TC-OK-PARTIAL | cs203_R:TC-OK | **STOP** cap-dependent-return-type | replay r10xh015_2 at HEAD: TC-OK, input-reading (if is_raw then text else _decode_escapes text 0), but only through the STAND-IN retype _decode_escapes(..) -> str, false for is_bytes=True (live returns bytes): needs a value-dependent str\|bytes result narrowed by the literal False (cv10), M |
| s204 | `_decode_string` | frontend/pure_ast.py | DEPTH-STOP | cs204_0:REFUSED | **STOP** cap-bytes-value-model | depth-0 R558: body.encode('latin-1', ..) if False else bytes(..): the bytes value model + a value-dependent str\|bytes tuple slot (cv11) |
| s205 | `_lex` | frontend/pure_ast.py | HONESTY-WALL | cs205_R:REFUSED | **STOP** cap-tokenize-model | replay: route #315: _Tok construction whose constructor reads t.type of a value of unknown kind; the body lexes with the stdlib tokenize (cv11: cap-tokenize-model, external-ish) |
| s206 | `_merge_str_constants` | frontend/pure_ast.py | HONESTY-WALL | cs206_R:REFUSED | **STOP** cap-augassign-subscript-field | replay: a[i].value += v (augmented assignment to a field of a subscripted base, not modelled) on IR string constants + in-place emit_ir field write (CORRECTNESS boundary) |
| s207 | `_parse_number` | frontend/pure_ast.py | HONESTY-WALL | cs207_R:REFUSED | **STOP** cap-R325-call-str-to-number | replay: R325 py_val = float(s) / complex(..) (no model): str->float/complex conversions (cv11 S + M) |
| s208 | `_self_test` | frontend/pure_ast.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-builtin-kwarg-open-encoding, cap-fs-path-model |
| s209 | `_set_ctx` | frontend/pure_ast.py | HONESTY-WALL | cs209_0:L3-TC | **STOP** cap-emit-ir-inplace-field-write | depth-0 L3-TC: node.ctx <- ctx on the immutable emit_ir ADT (an in-place IR field write; the RETURN interface records it as an honest uninterpreted emit_ir -> string -> emit_ir only while trusted): the recorded [CORRECTNESS] boundary on _set_ctx |
| s210 | `comments` | frontend/pure_ast.py | HONESTY-WALL | cs210_0:REFUSED | **STOP** cap-tokenize-model | depth-0: R325 tokenize.generate_tokens(..) (stdlib tokenize, cv10 XL) |
| s211 | `copy_location` | frontend/pure_ast.py | HONESTY-WALL | cs211_0:REFUSED | **STOP** cap-dynamic-getattr-setattr | depth-0: setattr(new_node, attr, value) with a non-literal attribute name on an AST node (the name-rebinding check refuses a dynamic setattr on a receiver it cannot see is a local instance); then getattr(old_node, attr) reads = pyast dynamic attribute model (cv11 HONESTY-WALL) |
| s212 | `dump` | frontend/pure_ast.py | HONESTY-WALL | cs212_R:REFUSED | **STOP** cap-tuple-unpack-alias-303 | replay (53 lines): route #303 in the nested _format: (simple, value) unpacked from a recursive call result passed to the recursive _format which 'may write it' (immutable str/bool in fact: the imprecise #303 again) + nested closure + dynamic getattr |
| s213 | `fix_missing_locations` | frontend/pure_ast.py | HONESTY-WALL | cs213_0:L3-TC | **STOP** cap-generator-yield-model | depth-0 L3-TC: iter_length (iter_child_nodes node) where iter_child_nodes is a GENERATOR (unit in the model): the generator-yield model (XL) + dynamic getattr/setattr |
| s214 | `get_source_segment` | frontend/pure_ast.py | DEPTH-STOP | cs214_R:REFUSED | **STOP** cap-bytes-value-model | replay: R325 first = lines[..].encode()[col:].decode() str concat over an erased (bytes) operand: the bytes value model + str-encoding ops (cv11) |
| s215 | `increment_lineno` | frontend/pure_ast.py | HONESTY-WALL | cs215_0:REFUSED | **STOP** cap-generator-yield-model | depth-0 route #542: for child in walk(node): walk is a generator lowered as int (iterable may be a number): generator model + dynamic setattr |
| s216 | `iter_child_nodes` | frontend/pure_ast.py | HONESTY-WALL | cs216_0:REFUSED | **STOP** cap-generator-yield-model | depth-0 route #542: for name, field in iter_fields(node): a generator iterable lowered as int |
| s219 | `main` | frontend/pure_ast.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-fs-path-model, cap-hash-judge-class-set |
| s221 | `unparse` | frontend/pure_ast.py | DEPTH-STOP | cs221_0:L3-TC; mlwx/cs221_x1:TC-OK | **TC-OK-PARTIAL**  | depth-0 L3-TC: unparse = _Unparser().visit(ast_obj); the call to the trusted visit writes _pyobj_state but unparse's frame (assigns \nothing, true in Python: the object is fresh) has writes { } / emission-level stand-in (writes { _pyobj_state } hand-added to the emitted let unparse; why3 prove --type-only via heavy.sh: rc 0, log scratchpad/cv12/mlwx/cs221_x1.log): TC-OK, but the body is a delegation: unparser = any _unparser (the trusted _Unparser.__init__), result = the trusted visit val over the erased ast_obj: int; converting it proves nothing about the input (FACADE-like); needs cap-fresh-object-frame (M) and buys no honest content until _Unparser.visit is modelled |
| s222 | `walk` | frontend/pure_ast.py | HONESTY-WALL | cs222_R:REFUSED | **STOP** cap-generator-yield-model | replay: todo.extend(iter_child_nodes(node)) + yield: a generator function over a deque worklist (generator model + extend lowering) |
| s223 | `validate_ir` | ir_schema.py | DEPTH-STOP | cs223_R:REFUSED | **STOP** cap-typeddict-optional-key | replay (cv9 TypedDict retype of ir: Any): route #398: ir['functions'] on a total=False TypedDict key; presence follows from the _REQUIRED_TOP - ir.keys() emptiness test, which the model does not connect: path-sensitive key presence (M); the live parameter is ir: Any (a Dict[str,Any] IR: boundary for the faithful form) |
| s224 | `AbstractOpsMixin._add_abstract_op` | module6_whyml/abstract_ops.py | DEPTH-STOP | cs224_0:REFUSED | **STOP** cap-inplace-mutator-setdefault | depth-0 (116 lines): self._abstract_ops.setdefault(..) on a self dict field (no certified lowering) + self-field alias |
| s228 | `AutoTrustMixin._check_witness_vals` | module6_whyml/auto_trust.py | HONESTY-WALL | cs228_0:REFUSED | **CORRECT** cap-eval | depth-0: a dynamic eval that can bind into the module namespace (auto_trust.py l.75): a REAL dynamic namespace, refused by the name-binding rule |
| s229 | `AutoTrustMixin._should_auto_trust_tuple_return` | module6_whyml/auto_trust.py | DEPTH-STOP | cs229_R:L3-TC | **BOUND** cap-vm-unerase-dict | replay: L3-TC the callee _tuple_return_has_array_slot(body_stmts, array_vars) returns array where int is expected (a [T] retype is free) but body_stmts is a List[Dict[str,Any]] IR body walked by a nested closure: boundary + closure-lift |
| s230 | `GhostSpecOpsMixin._handle_ctor_payload_expr` | module6_whyml/expr_ghost_spec_ops.py | DEPTH-STOP | cs230_R:L3-TC | **BOUND** cap-vm-unerase-irnode | replay r10xh050_2: L3-TC idx := iratt_index_of node (an emit_ir child) where the mirror local is int: the IR ADT child-field typing (Proj/CtorPayload index), XL ; desk: int(node.index) (the IR ADT child-typed index, as s231), then getattr(self, '_constructors', {}).get(ctor, {}) = Dict[str, Dict[str, Any]]: boundary |
| s231 | `GhostSpecOpsMixin._handle_proj_expr` | module6_whyml/expr_ghost_spec_ops.py | DEPTH-STOP | cs231_R:L3-TC | **STOP** cap-ir-adt-int-field | replay r10xh051_2: L3-TC idx := iratt_index_of node: int(node.index) of the Proj IR node (the certified emit_ir ADT types index as a child emit_ir); desk: then node.tuple.to_dict().get('name', '') (a Dict[str,Any] read: boundary) |
| s232 | `ExpressionEmissionMixin._call_bytes_methods` | module6_whyml/expressions.py | DEPTH-STOP | cs232_R:L3-TC | **STOP** cap-vm-unerase-list | replay r10xh056_6: L3-TC Seq.get ptypes 0 = <str hash>: the List[str] param-type list from a callee is an int-encoded seq (a List[str] local typing gap, as in s289) + cv11's str.strip(arg) model |
| s233 | `ExpressionEmissionMixin._call_named_builtins` | module6_whyml/expressions.py (GIANT 1069 lines) | DEPTH-STOP | cs233_R:REFUSED | **STOP** cap-inplace-mutator-pop | replay (1043 lines, 69 cv10 patches, GIANT): _r321_work.pop() worklist (exact-pop model) |
| s234 | `ExpressionEmissionMixin._call_record_constructor` | module6_whyml/expressions.py | DEPTH-STOP | cs234_R:REFUSED | **BOUND** cap-elem-store-nonlist | replay (456 lines): element store through a non-list value (a list held in a Dict[str,Any] IR record): boundary |
| s235 | `ExpressionEmissionMixin._coerce_dotted_args` | module6_whyml/expressions.py | DEPTH-STOP | cs235_R:L3-TC | **STOP** cap-dict-ifexp-literal | replay (2 RMISS: cv10's rewrites no longer match the live body): L3-TC Map.get !_rl !_id typed int where a string is expected: a local str->str dict built by an if-expression literal (cv11 cap-dict-ifexp-literal); 180-line body |
| s237 | `ExpressionEmissionMixin._dotted_ensures_suffix` | module6_whyml/expressions.py | DEPTH-STOP | cs237_0:REFUSED | **STOP** cap-hash-judge-class-set | depth-0: remote hash judge in the verified _handle_field_get_expr: self_type (derived class set ExpressionEmissionMixin \| list/dict/set) hashed by self._class_constants.get(self_type, {}) -- the field typing of the caller's self_type, M |
| s238 | `ExpressionEmissionMixin._emit_bitwise_or_power` | module6_whyml/expressions.py | TC-OK-PARTIAL | cs238_R:TC-OK | **TC-OK-PARTIAL** cap-ir-number-int-view | replay r10xh062_4 at HEAD: still TC-OK (cv10's [R]/[T] links); lvI (run #5) REVERTED it at proof time: route #259's py_pow 'y >= 0' obligation on a constant-folded IR Number exponent needs an int view of the Number payload (proof-level wall, not visible at --no-proof); child-IR guards havoc (partial honesty); expressions.py proof ~11 h |
| s239 | `ExpressionEmissionMixin._emit_membership` | module6_whyml/expressions.py (GIANT 574 lines) | DEPTH-STOP | cs239_R:REFUSED | **BOUND** cap-erased-to-builtin-slot-arg | replay (570 lines, GIANT): route #252 Any IR names into whyml_ident(name: str): IR payload typing = boundary |
| s240 | `ExpressionEmissionMixin._expr_to_whyml` | module6_whyml/expressions.py (GIANT 2944 lines) | DEPTH-STOP | cs240_R:REFUSED | **STOP** cap-definite-assignment-flow | replay (2937 lines, GIANT): definite-assignment of _r358_mn not proven on every path (a flow-sensitive definite-assignment model or an [R] initialiser) |
| s241 | `ExpressionEmissionMixin._expr_to_whyml_string_ctx` | module6_whyml/expressions.py | TC-OK-PARTIAL | cs241_R:TC-OK | **TC-OK-PARTIAL** cap-method-recursion-cycle | replay r10xh.. at HEAD: TC-OK only through cv10's stand-ins (the recursive call dropped, a missing mirror function stubbed): needs method recursion + the missing sibling: unchanged |
| s242 | `ExpressionEmissionMixin._handle_attribute_expr` | module6_whyml/expressions.py (GIANT 944 lines) | DEPTH-STOP | cs242_R:REFUSED | **STOP** cap-binder-hygiene-R327 | replay (943 lines, GIANT): R327 _ri vs the _ri binder namespace (cv11 then nested-unpack target) |
| s243 | `ExpressionEmissionMixin._handle_binop` | module6_whyml/expressions.py (GIANT 2273 lines) | DEPTH-STOP | cs243_0:REFUSED | **STOP** cap-binder-hygiene-R327 | depth-0 (2273 body lines): R327 _r230_a vs the emitter's _r230_ binder namespace; [R] live rename is S, cv11's next wall cap-identity-vs-literal; a 2273-line dispatcher is not a near candidate |
| s244 | `ExpressionEmissionMixin._handle_call_expr` | module6_whyml/expressions.py (GIANT 1623 lines) | DEPTH-STOP | cs244_0:REFUSED | **STOP** cap-binder-hygiene-R327 | depth-0 (1623-line body): R327 binder-namespace collision -- GIANT, not walked |
| s245 | `ExpressionEmissionMixin._handle_dotted_call` | module6_whyml/expressions.py (GIANT 1386 lines) | DEPTH-STOP | cs245_R:REFUSED | **STOP** cap-tuple-unpack-alias-303 | replay (1377 lines, GIANT): route #303 over a 7-name tuple unpack from _resolve_dotted_signature |
| s249 | `ExpressionEmissionMixin._handle_join_call` | module6_whyml/expressions.py | DEPTH-STOP | cs249_R:L3-TC | **BOUND** cap-vm-unerase-dict | replay r10xh065_4: L3-TC Map.get expr 'args' (a Dict[str,Any] IR call node read as map string int, compared with a str): boundary |
| s250 | `ExpressionEmissionMixin._handle_len_call` | module6_whyml/expressions.py | DEPTH-STOP | cs250_R:REFUSED | **STOP** cap-erased-to-builtin-slot-arg | replay r10xh067_5 (cv10's 4 links): MOVED from L3-TC irnode to route #252: an Any-typed IR field value flows into whyml_ident(name: str) in the 268-line body: typing the IR payload is the real fix (the IR-node value model, XL) |
| s252 | `ExpressionEmissionMixin._handle_subscript` | module6_whyml/expressions.py (GIANT 785 lines) | DEPTH-STOP | cs252_0:REFUSED | **STOP** cap-binder-hygiene-R327 | depth-0 (785 lines, GIANT): R327 binder-namespace collision (_idx_); cv11 then inplace pop |
| s253 | `ExpressionEmissionMixin._handle_sum_call` | module6_whyml/expressions.py | DEPTH-STOP | cs253_R:L3-TC | **STOP** cap-vm-unerase-dict | replay: L3-TC Map.get self._known_collection_elements vname: a Dict[str, Dict[int, str]]-valued field (nested typed map) read as int; + cv11 str->number |
| s254 | `ExpressionEmissionMixin._is_emit_ir_expr` | module6_whyml/expressions.py | DEPTH-STOP | cs254_R:L3-TC | **STOP** cap-vm-unerase-irnode | replay (223 lines, 19 cv10 patches): L3-TC emit_ir where int is expected in the operand classification (cv10 helper stand-ins _cv10_isemit): IR value model + missing mirror sibling |
| s255 | `ExpressionEmissionMixin._is_string_expr` | module6_whyml/expressions.py (GIANT 645 lines) | DEPTH-STOP | cs255_R:REFUSED | **STOP** cap-R274-writing-call-in-comprehension | replay (643 lines, GIANT; the cv10 spec partly misses at HEAD: patch.py RMISS + traceback): R274 the recursive _is_string_expr (writing) inside a comprehension |
| s256 | `ExpressionEmissionMixin._iter_len_expr` | module6_whyml/expressions.py | DEPTH-STOP | cs256_R:REFUSED | **STOP** cap-method-recursion-cycle | replay: self-recursion of _iter_len_expr through a METHOD call: termination across a method edge (structural measure over the IR tree; L, or the open #@ \diverges decision) |
| s257 | `ExpressionEmissionMixin._linear_form` | module6_whyml/expressions.py | DEPTH-STOP | cs257_R:REFUSED | **BOUND** cap-R542-any-container | replay: route #542 dict(lv) on an Any IR payload: boundary |
| s258 | `ExpressionEmissionMixin._match_pattern_cond` | module6_whyml/expressions.py | DEPTH-STOP | cs258_R:L3-TC | **BOUND** cap-vm-unerase-dict | replay: L3-TC kind := pat.get('pattern', 'Unknown') typed int: the match pattern is a Dict[str,Any] IR node: boundary |
| s259 | `ExpressionEmissionMixin._pop_quant_binder` | module6_whyml/expressions.py | DEPTH-STOP | cs259_R:REFUSED | **STOP** cap-dict-alias | replay: #243/#244: a non-fresh dict/set value stored into the self field _quant_scalar_binders (save/restore of a binder scope): a field alias model (+ heterogeneous tuple return) |
| s260 | `ExpressionEmissionMixin._push_quant_binder` | module6_whyml/expressions.py | DEPTH-STOP | cs260_R:L3-TC | **STOP** cap-vm-unerase-union | replay: L3-TC Map.get self._dict_locals var with var a _union (Optional[str]) where string is expected: an Optional param used as a key without narrowing |
| s261 | `ExpressionEmissionMixin._resolve_dotted_signature` | module6_whyml/expressions.py | DEPTH-STOP | cs261_0:REFUSED | **STOP** cap-array-local-rebind | depth-0 (221 lines): reassigning an array local from a non-literal rhs (the array-local model is not rebindable; cv11 cap-array-local-rebind) |
| s262 | `ExpressionEmissionMixin._static_width` | module6_whyml/expressions.py | DEPTH-STOP | cs262_R:REFUSED | **STOP** cap-R542-any-container | replay r10xh063_3: MOVED to route #542: dict(uv) on an Any value (may be a number) -- an IR payload typing issue (IR value model) |
| s264 | `ExpressionEmissionMixin._union_local_read_projection` | module6_whyml/expressions.py | DEPTH-STOP | cs264_R:L3-TC | **STOP** cap-vm-unerase-union | replay: L3-TC the converted _union_read_projection returns an Optional union (_union__union_read_projection_2) where the stub's declared return expects its own type: Optional[str] return passthrough between two union types (+ missing mirror sibling) |
| s266 | `FunctionEmissionMixin._emit_function` | module6_whyml/functions.py | DEPTH-STOP | cs266_0:REFUSED | **STOP** cap-inplace-mutator-add | depth-0 (80 lines): _nd.add(..) on a set bound from a non-fresh value (getattr default / field): no certified lowering; + self-field alias, set typing |
| s267 | `FunctionEmissionMixin._emit_narrowing_vc` | module6_whyml/functions.py | DEPTH-STOP | cs267_R:REFUSED | **BOUND** cap-R325-str-concat-opaque | replay: R325 str_concat over erased operands (lines.append(f'...{erased}...') of IR-derived values): typing the IR payload (cv10 capmeta: M) (the erased operands are Dict[str,Any] IR reads: boundary) |
| s268 | `FunctionEmissionMixin._emit_subtyping_goals` | module6_whyml/functions.py | DEPTH-STOP | cs268_R:REFUSED | **BOUND** cap-method-arg-frame | replay r10xh124_2: route #316 in the callee _render_refinement_goal: its argument sub_fn (a Dict[str,Any] function IR) lowers to int and cannot be named in writes: framing a dict argument needs the dict value model (boundary) |
| s269 | `FunctionEmissionMixin._emit_union_arm_vc` | module6_whyml/functions.py | DEPTH-STOP | cs269_R:REFUSED | **BOUND** cap-R325-str-concat-opaque | replay: R325: lines.append(f'...{x}...') where an operand comes from a Dict[str,Any] IR read, so the f-string falls back to the opaque int string encoding (str_concat over hashes): typing the IR-derived operands = boundary |
| s270 | `FunctionEmissionMixin._mixin_dep_pseudo_functions` | module6_whyml/functions.py | DEPTH-STOP | cs270_R:L3-TC; cs270_1:L3-TC | **BOUND** cap-vm-unerase-dict | replay r10xh121_2: L3-TC let (_tu_params, _tu_ret) = self__parse_mixin_sig_1 (..): the trusted _parse_mixin_sig stub has no return annotation (pass body) / [T] _parse_mixin_sig -> Tuple[List[Tuple[str, str]], str]: next L3-TC: its argument dep.get('sig', '') is a Dict[str,Any] read (dep_get_2 .. : int); the body builds List[Dict[str, Any]] pseudo-function records with heterogeneous values = dict-model boundary |
| s271 | `FunctionEmissionMixin._param_type_str` | module6_whyml/functions.py | DEPTH-STOP | cs271_R:REFUSED | **BOUND** cap-erased-to-builtin-slot-arg | replay (241 lines): route #252: an Any symbol-table type (Dict[str,Any] symtab value) into self._callable_whyml_arrow(symtype: str): boundary |
| s272 | `FunctionEmissionMixin._parse_mixin_sig` | module6_whyml/functions.py | DEPTH-STOP | cs272_R:L3-TC | **STOP** cap-annotated-local-typing | replay (cv10's 6 [R] links): L3-TC ret := 'int' into a local hoisted as ref 0 (T2); read off the .mlw past it: s.rsplit('->', 1) and part.split(':', 1) opaque (maxsplit split models), [p.strip() for p in lhs.split(',') if p.strip()] an input-blind list_comp 0, lhs.strip() an opaque lhs_strip_0 (); T2 + split-maxsplit + list-comp models: 3 capabilities |
| s273 | `FunctionEmissionMixin._render_refinement_goal` | module6_whyml/functions.py | DEPTH-STOP | cs273_0:REFUSED | **BOUND** cap-method-arg-frame | depth-0 route #316 in the trusted callee _reset_function_state(func): the function-IR dict argument lowers to int, unframeable: dict-model boundary (cv11: cap-method-arg-frame) |
| s274 | `FunctionEmissionMixin._reset_function_state` | module6_whyml/functions.py (GIANT 5322 lines) | DEPTH-STOP | cs274_R:REFUSED | **STOP** cap-hash-judge-class-set | replay (5310 lines, GIANT): the hash judge on self._vararg_str_param (class set includes list/dict/set) added to a set |
| s277 | `PreambleEmissionMixin._emit_inductive_decls` | module6_whyml/preamble.py | DEPTH-STOP | cs277_R:REFUSED | **BOUND** cap-R325-str-concat-opaque | replay: R325 str_concat over an erased operand in out.append(..) (inductive decl dicts read from the Dict[str,Any] IR): boundary |
| s278 | `PreambleEmissionMixin._emit_module_globals` | module6_whyml/preamble.py | DEPTH-STOP | cs278_0:REFUSED | **STOP** cap-inplace-mutator-pop | depth-0: self._module_global_classes.pop(..) on a self dict field (no certified pop on a field receiver; self-field alias) |
| s279 | `PreambleEmissionMixin._emit_opaque_class_aliases` | module6_whyml/preamble.py | DEPTH-STOP | cs279_0:REFUSED | **BOUND** cap-inplace-mutator-add | depth-0: declared_types.add(st) on a Set[str] PARAMETER (no certified lowering for a param receiver; cv11 + method-arg frame), and the loop reads func.get('kind') / func['self_type'] of Dict[str,Any] function IRs: boundary |
| s287 | `PreambleEmissionMixin._fresh_globals_facts` | module6_whyml/preamble.py | DEPTH-STOP | cs287_R:REFUSED | **BOUND** cap-iterable-termination-variant | replay: a for loop over an erased (any) iterable has no legal variant; the iterable is read from the Dict[str,Any] IR (shared_vars): boundary |
| s288 | `PreambleEmissionMixin._inductive_referenced_axiom_decls` | module6_whyml/preamble.py | DEPTH-STOP | cs288_R:REFUSED | **STOP** cap-getattr-dynamic | replay: R325 in cv9's _cv9_split stand-in: s from getattr(self, <name>, ..) unknown; the axiom registry is a class-level dict read by getattr (cv11 getattr-dynamic + str.split) |
| s289 | `PreambleEmissionMixin._mutex_inv_application` | module6_whyml/preamble.py | DEPTH-STOP | cs289_R:L3-TC; cs289_1:L3-TC; cs289_3:TC-OK | **CLOSE-OK**  | replay r9xs132_2 ([T] params: List[str]): L3-TC params := self__mutex_inv_params_2 .. (array string) into a local hoisted as ref 0 / [R] the genexp join -> a for/append parts list + ' '.join(parts): the loop is now honest (str_join_seq over parts, whyml_ident !v); the ONLY remaining wall is the annotated local params hoisted as ref 0 (an emitter local-typing defect for an annotated List[str] local bound from a method call) / [R] behaviour-identical live respelling: iterate self._mutex_inv_params(mutex, inv_str) directly into parts: List[str] (for/append), test 'if not parts' (same length as params), ' '.join(parts) => TC-OK; input-reading (safe_mutex_name mutex, the callee result self__mutex_inv_params_2 mutex inv_str, whyml_ident per element, str_join_seq); both returns reachable. Verbatim needs an S emitter fix (a List[str] local bound from a method call is hoisted as ref 0) + genexp-j |
| s290 | `PreambleEmissionMixin._precompute_axiom_logic_funcs` | module6_whyml/preamble.py | DEPTH-STOP | cs290_0:REFUSED | **STOP** cap-inplace-mutator-add | depth-0 (97 lines): self._axiom_logic_funcs.add(..) on a self set field (no certified lowering on a field receiver) |
| s291 | `PreambleEmissionMixin._scan_preamble_needs` | module6_whyml/preamble.py (GIANT 1487 lines) | DEPTH-STOP | cs291_NR:REFUSED; cs291_NR:REFUSED | **CORRECT** cap-generic-fold-rc420-rebind | stand-in stNR: the trigger is REAL: the body imports recognize_* from live module6_whyml/generic_fold.py, whose module scope (l.41459-41463) rebinds every recognize_* via globals()[n] = _rc420_gate(n, fn) / next wall: module-scope globals() writes in generic_fold.py (REAL rebinding: the model would verify the ungated def while CPython runs the #420 gate wrapper); further: needs Dict[str,Any] IR reads throughout (func.get(...)) = dict-model boundary |
| s292 | `PreambleEmissionMixin._subst_self_in_expr` | module6_whyml/preamble.py | HONESTY-WALL | cs292_0:REFUSED | **BOUND** cap-closure-lift | depth-0: the nested rec (captures repl; another lifted rec in the file) is not faithfully liftable (cap-closure-lift); desk: rec deep-copies an Any IR tree (dict(e), e.items(), e['object'] = repl): Dict[str,Any] tree rewrite = boundary |
| s294 | `sort_functions_by_scc` | module6_whyml/scc.py | DEPTH-STOP | cs294_R:L3-TC | **BOUND** cap-vm-unerase-dict | replay: L3-TC Array.make 0 0 (an empty List[str] default typed array int); desk: Tarjan SCC over {func['name']: func} Dict[str,Any] function IRs and Dict[str, tuple] scc_info: boundary |
| s295 | `StatementEmissionMixin._emit_body_code` | module6_whyml/statements.py (GIANT 818 lines) | DEPTH-STOP | cs295_0:REFUSED | **STOP** cap-binder-hygiene-R327 | depth-0 (816 body lines): R327 the live local _ri collides with the emitter binder namespace _ri...; [R] a live rename is S, but cv11's later wall is cap-dict-alias and the body is the 816-line statement dispatcher (not walked further here) |
| s296 | `StatementEmissionMixin._emit_first_assign` | module6_whyml/statements.py | DEPTH-STOP | cs296_R:L3-TC | **STOP** cap-dict-ifexp-literal | replay r10xh101_4 (25 patches, 89 lines): L3-TC (getattr(self, '_record_types', None) or {}).get(...) over self._current_symbol_table: string->option string map vs the int the mirror expects: a typed str->str dict field read through an or-default (cv11 cap-dict-ifexp-literal) + irnode |
| s297 | `StatementEmissionMixin._emit_frame_condition` | module6_whyml/statements.py | DEPTH-STOP | cs297_R:L3-TC | **STOP** cap-vm-unerase-list | replay (281 lines): L3-TC contains_check (str_hash_op t) field_targets: a seq-typed local used where the int-encoded set membership expects int: list vs set-of-str seam |
| s298 | `StatementEmissionMixin._expr_to_whyml` | module6_whyml/statements.py | DECL-ONE-CAP | not walked | (cv11 terminal kept) |  |
| s299 | `StatementEmissionMixin._handle_array_set_stmt` | module6_whyml/statements.py | DEPTH-STOP | cs299_0:REFUSED | **STOP** cap-binder-hygiene-R327 | depth-0 (360 lines): R327 _fk vs the _fk binder namespace (a live rename, S); cv11: then cap-boolop-value |
| s300 | `StatementEmissionMixin._handle_assign_stmt` | module6_whyml/statements.py (GIANT 1194 lines) | DEPTH-STOP | cs300_R:REFUSED; cs300_DA:REFUSED; desk | **BOUND** cap-vm-unerase-any-tree | replay r10xh097_3: route #243/#244 alias refusal raised in the VERIFIED _handle_array_slice_set_stmt: local_refs passed on (to _expr_to_whyml) then passed to the mutating parameter of _stmts_to_whyml / stand-in stDA (functions.py #243/#244 collection-alias raise disabled): next wall route #303 in the 1194-line body itself: _n319, _dp319 = _stack319.pop() over a List[Tuple[Any,int]] stack / desk (live l.1436-1660): the #319/#320 blocks walk the function IR as an Any tree (_f319.get('body'), stacks of (Any, int) / (Any, Any, Any, bool) tuples): Dict[str,Any] / Any-element reads = the dict-model boundary; not completable inside the current decision |
| s301 | `StatementEmissionMixin._handle_expr_stmt` | module6_whyml/statements.py (GIANT 1139 lines) | DEPTH-STOP | cs301_R:REFUSED | **STOP** cap-identity-vs-literal | replay r10xh103_3 (1139-line body): route #498 identity test against a value that may be freshly built (a None-building expression) -- GIANT body, not walked further |
| s302 | `StatementEmissionMixin._handle_ghost_assign_stmt` | module6_whyml/statements.py | DEPTH-STOP | cs302_0:REFUSED; cs302_DA:REFUSED | **STOP** cap-R325-self-dict-field | depth-0: the same remote #243/#244 refusal in _handle_array_slice_set_stmt / stand-in stDA: next wall R325 in the body: self._ghost_tuple_vars[target] = int(ghost_type[-1]) -- the Dict[str,int] field (declared in the statements.py AND types.py mirrors) is refused as a non-int-valued dict field; a field-value-typing fix (S-M) then the rest of the 94-line body (string-ctx emission, _e callbacks) unknown |
| s303 | `StatementEmissionMixin._handle_return_stmt` | module6_whyml/statements.py | DECL-FAIL | cs303_0:PORT-ABORT | **STOP** cap-base-override-refines | PORT-ABORT: a mixin sibling interface stub (no live def of its own: the live method lives in another mixin): a declared_in swap needs the base-override refinement (cv11 DECL-FAIL) |
| s304 | `StatementEmissionMixin._handle_tuple_unpack_stmt` | module6_whyml/statements.py | DEPTH-STOP | cs304_DA:REFUSED | **STOP** cap-tuple-unpack-alias-303 | stand-in stDA: next wall route #303: _crt, _cpt, _re3, _re4 = self._resolve_dotted_signature(func_name) groups _cpt (a List[str]) with str names, and passing a STR of the group to whyml_ident is read as an in-place write of the list (imprecise: str is immutable); a per-name typed #303 (S-M) then the rest of the 243-line body (re.search on _re36 alias = outside lvO's gate) |
| s306 | `StatementEmissionMixin._stmts_to_whyml` | module6_whyml/statements.py (GIANT 810 lines) | DEPTH-STOP | cs306_DA:REFUSED | **STOP** cap-nested-unpack-target | stand-in stDA (#243/#244 disabled) on the cv10 r10xh104_3 spec: next wall route #301, a nested tuple loop/unpack target in the 799-line body ([R] flatten by index is possible; further walls unknown; cv11 also needs cap-identity-vs-literal) |
| s307 | `StatementEmissionMixin._track_collection_metadata` | module6_whyml/statements.py | DECL-FAIL | not walked | (cv11 terminal kept) |  |
| s308 | `StatementEmissionMixin._typed_local_vars` | module6_whyml/statements.py (GIANT 939 lines) | DEPTH-STOP | cs308_R:REFUSED | **STOP** cap-binder-hygiene-R327 | replay r10xh106_4 (939-line body): R327 in the nested _scan_seq_alias (_ae vs the _ae binder namespace) -- GIANT body, not walked further |
| s311 | `ControlFlowStmtMixin._handle_for_stmt` | module6_whyml/stmt_control_flow.py (GIANT 1278 lines) | DEPTH-STOP | cs311_R:REFUSED; cs311_1:REFUSED; cs311_2:REFUSED | **STOP** cap-object-identity-model | replay r10xh109_3: MOVED to route #449: self._expr_to_whyml(var_ir, inv_refs, subst=inv_subst) but the stmt_control_flow.py sibling interface stub _expr_to_whyml lacks invariant_ctx/subst (statements.py's stub got them in run #6, lvN) / [T] the stmt_control_flow.py _expr_to_whyml interface stub given invariant_ctx/subst (as statements.py's): next wall R327, live local _idx_name collides with the emitter's _idx_ binder namespace / [R] rename _idx_name -> a non-binder name: next wall route #498: an identity test against a fresh object() sentinel in the 1278-line body (cap-identity-vs-literal / object-identity model, M); 3 extra links walked, chain still open |
| s312 | `ControlFlowStmtMixin._handle_match_stmt` | module6_whyml/stmt_control_flow.py | DEPTH-STOP | cs312_0:REFUSED | **STOP** cap-emit-ir-item-store-model | depth-0 (108 lines): R566 an item store into an IR-typed dict (the immutable-IR boundary of #566) + cv11 str typing |
| s313 | `ControlFlowStmtMixin._render_match_pattern` | module6_whyml/stmt_control_flow.py | DEPTH-STOP | cs313_R:REFUSED | **STOP** cap-match-pattern-lowering | replay: route #30: a match pattern arm with no faithful lowering (cv11 poison-marker-literal) + method recursion over patterns |
| s314 | `calcsize` | module6_whyml/struct_format.py | HONESTY-WALL | cs314_0:L3-TC; cs314_1:TC-OK | **CLOSE-OK**  | depth-0 at HEAD: the re.Match model (lvO) now covers _TOKEN_RE.match(fmt, pos) and the str->int dict literal is a Map (cv11's two needs are GONE); the only wall: count_str, char = m.group(1), m.group(2) types both locals int (L3-TC line 113) / [R] split the tuple unpack into count_str: str = m.group(1) / char: str = m.group(2) (behaviour-identical: pure group reads, same order) => TC-OK, input-reading (re_match_op .. fmt !pos, re_group_op, str_to_int, Map.get sizes char), every return reachable. A live respelling (or an S emitter fix typing tuple-unpack elements from a str-typed tuple) converts it; struct_format.py proof ~0.14 h |
| s315 | `parse_format` | module6_whyml/struct_format.py | HONESTY-WALL | cs315_R:L3-TC | **STOP** cap-return-exn-mutable | replay lvO's spec: L3-TC 'top-level exception Return__union_parse_format_0 has mutable components': an Optional[StructFormat] return whose record has an array field (slots) cannot ride a Why3 exception; then (desk) the same count_str/char tuple-unpack typing as calcsize, _CHAR_TO_TYPE.get(char), slots.extend([t] * count) (lvO: route #369 kwarg, .extend) |
| s317 | `TypeInferenceMixin._track_collection_metadata` | module6_whyml/types.py | DEPTH-STOP | cs317_0:REFUSED | **STOP** cap-binder-hygiene-R327 | depth-0 (198 lines): R327 _u_el vs the emitter's _u_ binder namespace (live rename, S); cv11's next wall cap-dict-alias |
| s318 | `_load_axiom_registry` | proof2why3/crosscheck.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-fs-path-model, cap-stdlib-ast-model, cap-vm-unerase-str |
| s319 | `crosscheck_file` | proof2why3/crosscheck.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-R325-call-subprocess, cap-fs-path-model, cap-sorted-key, cap-vm-unerase-dict |
| s320 | `main` | proof2why3/crosscheck.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-param-rebind-nested, cap-argparse-model, cap-fs-path-model, cap-stdout-model |
| s321 | `IRCrossCheckResult.diagnostic` | proof2why3/crosscheck_ir.py | DEPTH-STOP | cs321_0:REFUSED | **STOP** cap-R489-implicit-dunder | depth-0 R489: the callee exists__pp is a bodyless val with an inferred frame and its f-string {binders} dispatches to the program dunder Token.__repr__ (not #@ assigns \nothing): declare Token.__repr__ assigns \nothing (a mirror contract on a dunder, S) is the cv11 single need; further walls unknown |
| s323 | `_load_axiom_registry` | proof2why3/crosscheck_ir.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-fs-path-model, cap-stdlib-ast-model, cap-vm-unerase-str |
| s324 | `crosscheck_file_ir` | proof2why3/crosscheck_ir.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-R325-call-subprocess, cap-fs-path-model, cap-sorted-key, cap-vm-unerase-dict |
| s325 | `main` | proof2why3/crosscheck_ir.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-hash-judge-class-set, cap-argparse-model, cap-fs-path-model, cap-stdout-model |
| s326 | `extract_lean_statements` | proof2why3/extract.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-R325-call-subprocess, cap-context-manager-model |
| s327 | `extract_rocq_statements` | proof2why3/extract.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-R325-call-subprocess, cap-context-manager-model |
| s328 | `extract_lean_statements_meta` | proof2why3/extract_lean_meta.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-heterogeneous-list, cap-R325-call-subprocess, cap-json-model |
| s329 | `_is_ofnat_lit` | proof2why3/from_lean_json.py | DEPTH-STOP | cs329_0:L3-TC | **BOUND** cap-vm-unerase-dict | depth-0 L3-TC: _tu_args from a tuple unpack of a Lean-JSON node (Dict[str,Any]) read as a map: the Lean JSON value is Dict[str,Any] (boundary, json-facing) |
| s330 | `_linearize_app` | proof2why3/from_lean_json.py | DEPTH-STOP | cs330_0:REFUSED | **STOP** cap-inplace-mutator-insert | depth-0: args.insert(0, ..) (no certified lowering, cv10 M) over Lean-JSON Dict[str,Any] nodes (boundary after) |
| s332 | `_construct_indices` | proof2why3/from_sexp.py | DEPTH-STOP | cs332_0:REFUSED | **STOP** cap-sexp-tuple-value-model | depth-0: the mirror stub returns int (live Optional[Tuple[str, int]]: a [T] is free) but the body walks construct_node: Any, an S-expression of nested tuples (isinstance(.., tuple), [1], recursive helpers): the sexp value model (L) |
| s334 | `_project_app` | proof2why3/from_sexp.py | DEPTH-STOP | cs334_0:REFUSED | **STOP** cap-sexp-tuple-value-model | depth-0 (55 lines): route #542: info = <sexp>[k] may be a number: Any-typed S-expression tuples |
| s337 | `_expand_anon_binders` | proof2why3/normalize.py | REFUSED-termination | - | EXCLUDED (EXCL-decision(diverges)) | cap-diverges |
| s338 | `_nat_to_int_with_sidecond` | proof2why3/normalize.py | HONESTY-WALL | cs338_0:REFUSED | **STOP** cap-re-compiled | depth-0: R325 in the callee _strip_all_parens: a compiled pattern's .sub(..) has no model (lvA modelled re.sub / re.compile only as module functions; cv11 cap-re-compiled + a named-def callable replacement) |
| s339 | `normalize_surface` | proof2why3/parser.py | REFUSED-termination | - | EXCLUDED (EXCL-decision(diverges)) | cap-diverges, cap-optstr-sentinel |
| s340 | `parse_type_expr` | proof2why3/parser.py | DEPTH-STOP | cs340_0:REFUSED; cs340_1:L3-TC | **STOP** cap-record-union-return | depth-0 route #233: str(exc) of the caught SyntaxError/IndexError / [S] stand-in str(exc) -> a literal (for cap-exception-object-read): next L3-TC: returning Unsupported(..) where the declared return Term is a Union of record classes (Var \| App \| .. \| Unsupported): a record-sum return model (L); then _Parser(tokens).parse_expr() and the f-string of p.toks[p.pos:] (Token.__repr__, R489) |
| s341 | `SertopSession.type_of_batch` | proof2why3/sertop.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-R325-call-pathlib, cap-R325-call-subprocess |
| s343 | `_sexp_tokens` | proof2why3/sertop.py | HONESTY-WALL | cs343_0:TC-OK | **TC-OK-PARTIAL** cap-generator-yield-model | depth-0: TC-OK, but the generator is emitted as 'let _sexp_tokens (s: string) : unit' -- the yielded token stream is erased (a FACADE: the yields are not the result); needs the generator/yield sequence model (cv11 HONESTY-WALL) |
| s344 | `extract_via_sertop` | proof2why3/sertop.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-vm-unerase-list, cap-R325-call-subprocess |
| s345 | `parse_sexp` | proof2why3/sertop.py | DEPTH-STOP | cs345_0:L3-TC | **STOP** cap-sexp-tuple-value-model | depth-0 L3-TC: parse_sexp returns _sexp_parse(tokens), a recursive nested list/str S-expression value (int in the model): a recursive sexp value model (L) |
| s346 | `run_sertop_batch` | proof2why3/sertop.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-exception-hierarchy-model, cap-R325-call-subprocess |
| s347 | `sertop_version` | proof2why3/sertop.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-vm-unerase-list, cap-R325-call-subprocess |
| s348 | `parse_rocq_assumptions_block` | proof_axiom_allowlist.py | DEPTH-STOP | cs348_R:L3-TC; cs348_2:TC-OK | **CLOSE-OK**  | replay (cv11 [R]: the early 'return True, []' folded into a closed flag + break): L3-TC line := str_strip_op !raw into a local hoisted as ref 0 (T2); past it, read off the .mlw: ' : ' in line as int contains_check, line.startswith(<tuple>) as an input-blind (any int), line.split(' : ', 1)[0].strip() opaque / [T] line: str = raw.strip() (the annotated FIRST binding is typed, unlike s359's re-assigned one); [R] line.startswith((a, b, ..)) -> an or-chain of startswith (identical); [R] line.split(' : ', 1)[0] -> line[:line.find(' : ')] (identical inside the ' : ' in line branch); with cv11's [R] (the early 'return True, []' folded into a closed flag + break; identical, splitlines is pure) => TC-OK, input-reading (str_splitlines_op block, str_strip_op, str_contains_op, str_startswith_op x6, str_find_op/str_sub_op), every path reachable; home proof_axiom_allowlist.py (small, est. 0.25 h) |
| s349 | `_build_soundness_report` | pycsl.py (GIANT 619 lines) | DEPTH-STOP | cs349_R:REFUSED | **STOP** cap-hash-judge-class-set | replay (606 lines, GIANT): hash judge: _pd_x (class set list/dict/set) added to a set |
| s350 | `_check_rocq_proofs` | pycsl.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-R325-call-subprocess, cap-fs-path-model, cap-heterogeneous-list |
| s351 | `_dispatch_provers` | pycsl.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-R325-call-subprocess, cap-closure-lift |
| s353 | `_find_coqc` | pycsl.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-fs-path-model, cap-vm-unerase-union |
| s354 | `_function_body_eqs` | pycsl.py | HONESTY-WALL | cs354_R:L3-TC; cs354_1:L3-TC; cs354_2:L3-TC; cs354_3:L3-TC; cs354_4:L3-TC; mlwx/cs354_x1:TC-OK | **CLOSE-STANDIN**  | replay s354 (cv11 [R] enumerate -> index loop): L3-TC cur := m.group(1) opaque: _LET_FN_RE / _BODY_EQ_RE are compiled under import re as _re (outside lvO's plain-import gate) / [R] import re as _re -> a plain import re for the two module-level compiles (the only _re uses in the mirror): still opaque: lvO's gate also needs a str-DECLARED subject (line = lines[i] is unannotated) / [T] line: str = lines[i]: the re.Match model now APPLIES (re_match_op <literal pattern> !line 0, re_group_op !m 1); next L3-TC: the quoted return annotation 'Tuple[List[Tuple[str, int]], List[str]]' lowers to (array int, int); res elements are (any int) (the (cur, i) pair with cur Optional-narrowed in an elif conjunct) / [T] unquoted return annotation: the tuple return types; next L3-TC: res: List[Tuple[str, int]] appended (cur, i) with cur an Optional[str] narrowed only in the elif conjunct -> (any int) elements |
| s355 | `_generate_rocq_obligations` | pycsl.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-context-manager-model, cap-fs-path-model |
| s356 | `_json_goal_records` | pycsl.py | DEPTH-STOP | cs356_R:L3-TC | **EXT** cap-json-model | replay: L3-TC [r for r in _parse_why3_json(stdout) if ..] (a list comprehension over the trusted JSON parser's records: List[Dict[str,Any]]) returned where the mirror stub returns int: json-facing records (lvQ) + list-of-dict elements |
| s357 | `_merge_records_best_of_n` | pycsl.py | DEPTH-STOP | cs357_0:L3-TC | **BOUND** cap-vm-unerase-dict | depth-0 L3-TC: k = _record_key(rec) over List[List[dict]] goal records: _record_key is the dict-boundary leaf (s362); best-of-N over Dict[Tuple, dict]: boundary |
| s358 | `_parse_args` | pycsl.py | TC-OK-FACADE | - | EXCLUDED (EXCL-external) | cap-argparse-model |
| s359 | `_parse_goal_blocks` | pycsl.py | DEPTH-STOP | cs359_0:L3-TC; cs359_1:L3-TC; cs359_2:REFUSED; cs359_3:L3-TC; mlwx/cs359_x1:TC-OK | **CLOSE-STANDIN**  | depth-0 L3-TC: header := join_1 !cur_header (an opaque join taking int) and the function returns int: the QUOTED return annotation "List[Tuple[str, str]]" in the mirror stub lowers to int (cv9's _cv9_join helper stand-in is superseded) / [T] unquoted -> List[Tuple[str, str]]: the return types; still header := join_1 !cur_header: a List[str] local that is REBOUND (cur_header = [] inside the loop) loses its str_join_seq lowering / [S] cur_header = [] -> cur_header.clear(): refused (clear has no certified lowering); the remaining wall is an emitter local-typing gap: an annotated List[str] local rebound to [] inside a loop is joined by an opaque join_1 (the never-rebound parts: List[str] of s289 gets str_join_seq). An S-M emitter fix; then the (header, line) tuple append typing (as s354) / [R] behaviour-identical respelling of the join: accumulate cur_hdr: str (line if first else cur_hdr + ' |
| s360 | `_parse_why3_json` | pycsl.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-inplace-mutator-extend, cap-json-model, cap-tuple-unpack-alias |
| s361 | `_print_soundness_report` | pycsl.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-boolop-value, cap-json-model, cap-stdout-model |
| s362 | `_record_key` | pycsl.py | DEPTH-STOP | cs362_0:L3-TC | **BOUND** cap-vm-unerase-dict | depth-0 L3-TC (int vs ...): rec.get('term') or {} -> nested Dict[str,Any] reads + a heterogeneous tuple return; this is the dict-value-model-r3 best leaf (row 398, rk_hval_chain.mlw): needs a Tuple[PyVal,...] return codomain + an hval-polymorphic tuple = the CERTIFIED-BOUNDARY reopening test (dict-value-model-r3-impl.md §1). Run #6's native-tuple returns type slots, not PyVal: the reopening test is NOT met; no in-decision version exists |
| s364 | `_resolve_runtime_config` | pycsl.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-context-manager-model, cap-fs-path-model, cap-json-model |
| s365 | `_run_audit_mode` | pycsl.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-argparse-model, cap-erased-to-builtin-slot-arg, cap-fs-path-model |
| s366 | `_run_pipeline` | pycsl.py (GIANT 36959 lines) | DEPTH-STOP | cs366_NR:REFUSED; cs366_NR:REFUSED | **CORRECT** cap-dynamic-namespace | stand-in stNR / next wall: getattr on a namespace object as callee, dynamic eval binding into module namespace, globals() use, module alias _md466 (pycsl.py itself): REAL dynamic namespace; also the pipeline driver is external-world (subprocess/fs) |
| s367 | `_run_proofs` | pycsl.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-R325-call-subprocess, cap-argparse-model, cap-closure-lift |
| s369 | `_run_vacuity_gate` | pycsl.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-R325-call-subprocess, cap-closure-lift, cap-context-manager-model |
| s372 | `_run_why3_prove` | pycsl.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-R325-call-subprocess, cap-heterogeneous-list |
| s373 | `_sha256_file` | pycsl.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-context-manager-model, cap-fs-path-model, cap-hashlib-model, cap-inplace-mutator-update |
| s375 | `_synthesize_legacy_text` | pycsl.py | DEPTH-STOP | cs375_R:L3-TC | **STOP** cap-list-of-dict-elements | replay s375_3 (cv11's [R] for/append + [T] records: List[Dict[str, Any]]): same terminal at HEAD: the list element is int while the trusted _synthesize_block(rec: dict) takes map string (option int): a List[Dict] element model (the body only PASSES each dict on, so this stays inside the dict decision); the result is input-reading only up to the trusted _synthesize_block val |
| s376 | `_why3_typecheck` | pycsl.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-R325-call-subprocess |
| s377 | `main` | pycsl.py | HONESTY-WALL | - | EXCLUDED (EXCL-external) | cap-argparse-model, cap-definite-assignment-flow, cap-fs-path-model |

## 3. Where the chains stop (terminal wall x count)

| terminal | capability | chains | size / risk (capmeta) | stubs |
|---|---|---:|---|---|
| BOUND | `cap-vm-unerase-dict` | 16 | XL / high | s001, s003, s006, s011, s027, s074, s150, s164, s229, s249, s258, s270, s294, s329, s357, s362 |
| STOP | `cap-binder-hygiene-R327` | 12 | S (live rename) / low | s081, s095, s125, s151, s242, s243, s244, s252, s295, s299, s308, s317 |
| STOP | `cap-pyast-node-typing` | 6 | L / med-high | s044, s116, s133, s157, s165, s199 |
| STOP | `cap-method-recursion-cycle` | 6 | L / high (termination) | s048, s079, s115, s121, s174, s256 |
| STOP | `cap-vm-unerase-irnode` | 6 | XL / high | s054, s078, s083, s110, s120, s254 |
| STOP | `cap-vm-unerase-union` | 5 | L / high | s059, s060, s140, s260, s264 |
| STOP | `cap-pyast-node-attr-writeback` | 5 | L / high (node aliasing) | s082, s087, s088, s091, s092 |
| BOUND | `cap-inplace-mutator-setdefault` | 5 | M / med | s096, s118, s126, s145, s160 |
| STOP | `cap-generator-yield-model` | 5 | XL / high | s171, s213, s215, s216, s222 |
| STOP | `cap-tuple-unpack-alias-303` | 4 | ? / ? | s002, s212, s245, s304 |
| STOP | `cap-vm-unerase-list` | 4 | XL / high | s033, s058, s232, s297 |
| STOP | `cap-getattr-dynamic` | 4 | M / high | s117, s155, s156, s288 |
| STOP | `cap-dynamic-getattr-setattr` | 4 | XL / high | s130, s170, s176, s211 |
| CORRECT | `cap-generic-fold-rc420-rebind` | 3 | ? / ? | s009, s012, s291 |
| STOP | `cap-re-match-model-ext` | 3 | ? / ? | s057, s066, s161 |
| STOP | `cap-inplace-mutator-add` | 3 | M / med | s090, s266, s290 |
| STOP | `cap-inplace-mutator-pop` | 3 | M / med | s101, s233, s278 |
| BOUND | `cap-erased-to-builtin-slot-arg` | 3 | M / high (typing the upstream value is the real fix) | s154, s239, s271 |
| STOP | `cap-hash-judge-class-set` | 3 | M / med | s237, s274, s349 |
| BOUND | `cap-R325-str-concat-opaque` | 3 | M / med | s267, s269, s277 |
| STOP | `cap-sexp-tuple-value-model` | 3 | ? / ? | s332, s334, s345 |
| BOUND | `cap-vm-unerase-any-tree` | 2 | ? / ? | s031, s300 |
| STOP | `cap-self-field-alias-analysis` | 2 | L / high | s038, s200 |
| STOP | `cap-vm-callable-value` | 2 | XL / high | s053, s191 |
| STOP | `cap-identity-vs-literal` | 2 | M / med | s072, s301 |
| STOP | `cap-erased-to-builtin-slot-arg` | 2 | M / high (typing the upstream value is the real fix) | s077, s250 |
| STOP | `cap-closure-lift` | 2 | M / med | s080, s105 |
| STOP | `cap-method-arg-frame` | 2 | M / med | s089, s173 |
| EXT | `cap-json-model` | 2 | L / med | s093, s356 |
| STOP | `cap-emit-ir-item-store-model` | 2 | ? / ? | s104, s312 |
| BOUND | `cap-inplace-mutator-computed-receiver` | 2 | L / high | s108, s142 |
| BOUND | `cap-R274-writing-call-in-comprehension` | 2 | M (or per-stub live rewrite) / low | s136, s138 |
| BOUND | `cap-R542-any-container` | 2 | ? / ? | s147, s257 |
| STOP | `cap-dict-alias` | 2 | M / med | s149, s259 |
| BOUND | `cap-iterable-termination-variant` | 2 | M / med | s158, s287 |
| BOUND | `cap-elem-store-nonlist` | 2 | M-L / med | s162, s234 |
| STOP | `cap-vm-unerase-dict` | 2 | XL / high | s192, s253 |
| STOP | `cap-bytes-value-model` | 2 | L / med | s204, s214 |
| STOP | `cap-tokenize-model` | 2 | XL / high | s205, s210 |
| STOP | `cap-dict-ifexp-literal` | 2 | ? / ? | s235, s296 |
| BOUND | `cap-method-arg-frame` | 2 | M / med | s268, s273 |
| STOP | `cap-vm-unerase-set` | 1 | M / med | s004 |
| EXT | `cap-hashlib-model` | 1 | L / med | s026 |
| STOP | `cap-dict-of-tuple-values` | 1 | ? / ? | s030 |
| STOP | `cap-field-collection-writeback` | 1 | L / high | s041 |
| STOP | `cap-R325-str-concat-opaque` | 1 | M / med | s043 |
| STOP | `cap-ctor-with-calls-315` | 1 | ? / ? | s047 |
| STOP | `cap-heterogeneous-list` | 1 | L / high | s051 |
| HONEST-WALL | `cap-dict-items-iteration` | 1 | ? / ? | s067 |
| STOP | `cap-R325-call-deepcopy` | 1 | M / med | s075 |
| STOP | `cap-R489-imported-callee-frame` | 1 | ? / ? | s076 |
| STOP | `cap-static-method-class-call` | 1 | ? / ? | s086 |
| STOP | `cap-boolop-value` | 1 | M / med | s094 |
| STOP | `cap-vm-irnode-R1-narrowing-view` | 1 | ? / ? | s097 |
| STOP | `cap-R579-csl-class-resolution` | 1 | ? / ? | s103 |
| STOP | `cap-missing-mirror-sibling` | 1 | S (mirror port) / low | s111 |
| STOP | `cap-optional-irnode-return` | 1 | ? / ? | s112 |
| STOP | `cap-optional-str-return` | 1 | ? / ? | s113 |
| CORRECT | `cap-import-system-local-module` | 1 | XL / high | s127 |
| STOP | `cap-R325-call-ast-ctor` | 1 | L / med | s128 |
| BOUND | `cap-inplace-mutator-extend` | 1 | M / med | s135 |
| BOUND | `cap-inplace-mutator-update` | 1 | M / med | s137 |
| BOUND | `cap-inplace-mutator-pop` | 1 | M / med | s139 |
| CORRECT | `cap-ub76-new-singleton` | 1 | - / boundary | s169 |
| STOP | `cap-dynamic-getattr-method-dispatch` | 1 | XL / high | s172 |
| BOUND | `cap-emit-ir-inplace-field-write` | 1 | XL / high (CORRECTNESS boundary) | s175 |
| STOP | `cap-self-field-untyped-ctor` | 1 | M / med | s178 |
| STOP | `cap-pyast-dynamic-ctor` | 1 | L / high | s180 |
| STOP | `cap-enum-value-lookup` | 1 | ? / ? | s182 |
| STOP | `cap-raises-clause-propagation` | 1 | M / med | s186 |
| STOP | `cap-effectful-callback` | 1 | XL / high | s190 |
| CORRECT | `cap-dynamic-class-type-ctor` | 1 | ? / ? | s201 |
| STOP | `cap-R325-module-constant-dict` | 1 | S-M / low | s202 |
| STOP | `cap-dependent-return-type` | 1 | M / med | s203 |
| STOP | `cap-augassign-subscript-field` | 1 | S (rewrite) / low | s206 |
| STOP | `cap-R325-call-str-to-number` | 1 | M / med | s207 |
| STOP | `cap-emit-ir-inplace-field-write` | 1 | XL / high (CORRECTNESS boundary) | s209 |
| STOP | `cap-typeddict-optional-key` | 1 | M / med | s223 |
| STOP | `cap-inplace-mutator-setdefault` | 1 | M / med | s224 |
| CORRECT | `cap-eval` | 1 | XL / high (unmodellable) | s228 |
| BOUND | `cap-vm-unerase-irnode` | 1 | XL / high | s230 |
| STOP | `cap-ir-adt-int-field` | 1 | ? / ? | s231 |
| STOP | `cap-definite-assignment-flow` | 1 | S / low | s240 |
| STOP | `cap-R274-writing-call-in-comprehension` | 1 | M (or per-stub live rewrite) / low | s255 |
| STOP | `cap-array-local-rebind` | 1 | M-L / med | s261 |
| STOP | `cap-R542-any-container` | 1 | ? / ? | s262 |
| STOP | `cap-annotated-local-typing` | 1 | ? / ? | s272 |
| BOUND | `cap-inplace-mutator-add` | 1 | M / med | s279 |
| BOUND | `cap-closure-lift` | 1 | M / med | s292 |
| STOP | `cap-R325-self-dict-field` | 1 | ? / ? | s302 |
| STOP | `cap-base-override-refines` | 1 | M / med | s303 |
| STOP | `cap-nested-unpack-target` | 1 | S (or live rewrite) / low | s306 |
| STOP | `cap-object-identity-model` | 1 | XL / high | s311 |
| STOP | `cap-match-pattern-lowering` | 1 | ? / ? | s313 |
| STOP | `cap-return-exn-mutable` | 1 | ? / ? | s315 |
| STOP | `cap-R489-implicit-dunder` | 1 | M / med | s321 |
| STOP | `cap-inplace-mutator-insert` | 1 | M / med | s330 |
| STOP | `cap-re-compiled` | 1 | S / low | s338 |
| STOP | `cap-record-union-return` | 1 | ? / ? | s340 |
| CORRECT | `cap-dynamic-namespace` | 1 | ? / ? | s366 |
| STOP | `cap-list-of-dict-elements` | 1 | ? / ? | s375 |

## 5. Reproduction (every claim above)

- **Probe runner.** `scratchpad/cv12/chunk2.sh` (cv11's `chunk.sh` with a 20 s gap) drains `queue.list` one job at a
  time with `HEAVY_QUICK=1 /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh bash scratchpad/cv12/probe.sh <rel>
  <Qualified.fn> <tag> [spec.json]`.
  - `probe.sh` is cv11's, pointed at `scratchpad/cv12`. It copies the HEAD mirror file into the scratch tree (`st`,
    or the tree named in `probe/<tag>.tree`), runs `bin/port-one-mirror-body.py <tree> <rel> <fn> --convert
    [--replace]`, then `patch.py <spec>`, then `probe/<tag>.extra.sh`, then `python3 src/pycsl/pycsl.py <file>
    --import-path <tree>/src/pycsl --no-proof --keep-mlw`.
  - It writes one row per probe to `probe/results.tsv`, plus `probe/<tag>.{src.py,log,mlw,patchlog}`.
- **Scratch trees.** All are HEAD copies under `scratchpad/cv12/`:
  - `st`: plain HEAD;
  - `stNR`: Module3_Weaver l.2639 `if _rb_bad and False`;
  - `stDA`: the functions.py #243/#244 `raise` guarded off;
  - `stTP`: `patch -p0 src/pycsl/pycsl.py < scratchpad/lvC/typepos.patch`, which applies at a 2096-line offset;
  - `stX103`: CSLIn fields annotated `"ExprIR"` in the scratch live Module2_Parser.py.
- **Emission-level stand-ins.** `scratchpad/cv12/mlwx/<tag>_x1.mlw`, each checked by `heavy.sh why3 prove --type-only
  <file>`. The logs are `mlwx/*.log`; rc 0 for cs045_x1, cs007_x1, cs354_x1, cs359_x1 and cs221_x1.
- **Chains and tables.** One list of links per stub is in `scratchpad/cv12/chains.json` (tag, capability, state,
  note). The tables in §2/§3 come from `python3 scratchpad/cv12/gen_doc.py`. The selection comes from
  `scratchpad/cv12/pop.py` (cv11 `merged11.json` minus run #6 builds, at HEAD).
- **Not walked.** 68 governing stubs whose cv11 need-list keeps 3+ capabilities after run #6 (`scratchpad/cv12/rest.json`;
  e.g. `_Unparser.get_type_comment`, `IRCrossCheckResult.pairwise`, `compute_sccs`). Their small members were
  desk-checked and all need 3+ unbuilt capabilities (dict / closure / recursion).
- **OOM.** `pycsl.slice/pycsl-heavy.slice/memory.events` oom_kill was 0 at 09:29Z and 0 at the end. No proof was
  run.
