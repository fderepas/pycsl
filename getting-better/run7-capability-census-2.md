# Run #7 capability census 2 (cv13) — PARTIAL (stopped by driver redirect, log 838)

Executor cv13, branch `run7-cv13` at c15a2afed. Census only: no `src/pycsl` edit in the tree, no proof. Every
emission is a QUICK `--no-proof --keep-mlw` heavy.sh job (20 s gap) or a `why3 prove --type-only` of a hand-patched
`.mlw`. **STATUS: PARTIAL, 2026-11-13T14:10Z.** The driver redirected cv13 to the dict-value requirements census
(the dict-model boundary is reopened). This note records what the families scope measured before the stop; it is
not a final ranking. Raw data: `scratchpad/cv13/` (probe/results.tsv, spec/*.json, mlwx/*, rest.json, desk.json,
pop.py, desk.py, probe.sh, chunk.sh, patch.py with an AST-precise `arename`).

Scratch stand-in trees (HEAD copies under `scratchpad/cv13/`): `st` plain; `stMR` = pycsl.py's
`PYCSL-SEM-METHOD-RECURSION-UNCHECKED` raise skipped (l.31110, termination assumed); `stMRTP` = stMR + lvC's
`typepos.patch`; `st303` = functions.py route #303 raise disabled (l.846).

## 0. Interim ranking (bundles <= 3, measured, excluding lvQ / lvR / u43 / open decisions)

| rank | bundle (not built) | completes (honest TC-OK, measured) | home + proof h | build | risk |
|---:|---|---|---|---|---|
| 1 | **re-lastgroup** (law-free `re_lastgroup_op h : string`, gated on every top-level alternative being a named group) + **record-list tuple return** (`Tuple[List[<record>], str]` codomain + a record-seq `materialize`) | `_lex_contract` (Module2_Parser; `c066_a2` -> `mlwx/c066_x1` rc 0). Free [R]s: the computed `_TOKEN_RE` written as its literal (or capability: constant-fold the compile argument), `re.compile` not `_re.compile` (`c066_a4`: the alias is not a module-const regex), `if not m:` for `if m is None:` (`c066_a3`: `is None` drops the handle), `m.group(0)`, `_st = pos` for `m.start()` (anchored match), plus lvR's dead progress guard `if m.end() <= pos: raise` for the loop variant | Module2_Parser (~0.5 h est.) | S + S | low (law-free op; typing fix). Payload of the `_ContractSyntaxError` stays `any string` (f-string `!r`) |
| 2 | **generator-as-seq** (a pure, terminating generator lowered as the list of its yields; Iterator[T] -> List[T]) | `_sexp_tokens` (sertop; verbatim `c343_0` is the cv12 facade `: unit`; stand-in `c343_y1` TC-OK, input-reading). Loop variants must be added in the mirror (normal conversion work) | sertop (small, est. 0.2 h) | M | med (eager vs lazy: sound only for pure, exception-free, terminating bodies) |
| 3 | **method recursion with a structural emit_ir measure** (`let rec` + `variant { size ir }` for a self-recursive method on an `"ExprIR"` parameter) + **module-const str dict get / if-chain** (free [R] as an if-chain) + **str.encode('utf-8') iteration** | `_expr_to_whyml_string_ctx` (expressions; `c241_M3` TC-OK in stMR with [T] `local_refs: Set[str]` + `_ghost_string_vars` field decl; `mlwx/c241_x1` rc 0 with the let rec/variant). Needs the MISSING mirror sibling `whyml_string_literal` ported (identifiers.py: `c241_W1`/`c241_W2`: dict get, encode, then a list-literal iteration typing wall) and u43's StrConcat projectors (`ir["left"]` lowers to `left_of`, which is `IrOther ""` on `IrStrConcat`) | expressions (~11 h) + identifiers | M + S + M | med |

Nothing else in the six families completed a stub within 3 capabilities.

## 1. Family findings

- **(a) re.Match gate widening.** Every widening except `m.lastgroup` has a free behaviour-identical [R]:
  `_re.` -> `re.`; a List[str]-element / slice / field subject -> an annotated `x: str = ...` local; `m is None`
  -> `not m`; a compound test `if a or m is None` -> two `if`s (`c057_a3`); `m.group()` -> `m.group(0)`;
  `m.start()` -> `pos` for an anchored `P.match(s, pos)`; a computed pattern -> its literal. Measured: `_lex_contract`
  closes (rank 1); `_parse_contract` (`c057_a3`) passes the re gate and stops on the CSL clause-union return
  (`py_label` record vs `emit_ir`, ~40 clause classes); `_rewrite_annotation_str` (`c161_b1`) needs an
  isinstance-narrowed Any subject, a tuple-keyed dict and an `-> Any` return (dict/Any boundary); `_fold_blocks`
  (`c043_*`) is #303 + typed unpack of `Tuple[List[str], int]` / `Optional[Tuple[str,str]]` (lvR T1 generalized).
- **(b) R327 binder collisions.** 23 stubs carry a real collision (18 GIANT, >500 lines). An AST-precise live
  rename ([R], `spec/c*_r1.json`) moves every measured chain ONE link, then: #504/#498 identity tests (s081, s095,
  s243), #303 (s125, s244), nested-def lift (s151), local `.pop` (s252), dict/set alias into a field (s295, s317),
  boolop value (s299), unhashable set element (s308), kwarg `.format` (s226), R542 (s283), #381 hash (s285, s311),
  slice `del` (s245). Past #303 (st303): R252 (s125), non-growable append (s244), slice del (s245). Emitter hygiene
  is not worth building: renaming the generated binders globally re-emits 586/12/37 files (route #333 comment); a
  collision-conditional rename is emission-inert but touches every binder site (L). Live renames cost nothing.
- **(c) method recursion.** With the termination check skipped (stMR), 0 of 19 chains close: list-param byref
  append (s069, s070), field append (s041), pop (s342), param rebind (s331), nested lift (s256, s293), ctor
  invariant obligation (s048, s174), erased/Optional values (s333, s335, s037), set iteration (s068), dataclass
  field reflection (s079), Any-IR stmt reads (s309), record-tree child lists (s042). Only emit_ir-typed recursion
  has a structural measure (`size`, ensures >= 1); its one small member is s241 (rank 3).
- **(d) generators.** 5 generator stubs; only `_sexp_tokens` is pure-str (rank 2). `iter_child_nodes` / `walk`
  need pyast typing; `buffered` is a contextmanager.
- **(e) Optional unions.** 0 complete. `_get_mutex_invariant_ir` (`c112_e1`): the emitter builds
  `_union__get_mutex_invariant_ir_0` but types the return `emit_ir` (an Optional[ExprIR] codomain fix), then the
  Dict[str, CSLNode] field and the verified `_py_stmt_with`'s `val function mutex_invariant_ir` (pure) disagree with
  the body's `_fresh_var_counter` write. `_parse_happy` (`c059_0`): Optional/List record fields of HappyProperty
  (a record-type change that moves every importer). `_union_local_read_projection` (`c264_0`): missing mirror sibling
  `_union_read_projection` over dict-of-dict state (boundary). `get_type_comment` (`c189_R`): Optional[str]
  truthiness + pyast getattr.
- **(f) #303 precision.** With #303 disabled (st303): `_fold_blocks` -> typed unpack (above); `_compute_shared_module_maps`
  -> R252; `dump` -> nested lift; `_emit_shared_state` (`c284_R`) -> str_concat over erased operands;
  `_handle_tuple_unpack_stmt` -> a dict/set alias wall. 0 complete. The precise fix is per-slot types from the callee's
  declared Tuple return (shared with typed-unpack).

## 2. The 68 rest stubs (need-list >= 3 after run #6)

All 68 were probed depth-0 and, where cv11 had one, by replaying its spec (`c<sid>_0` / `c<sid>_R` in
results.tsv). None reached TC-OK except the external `_get_module_exports` facade (`c141_R`). First walls:
local in-place mutators (`.pop/.extend/.setdefault/.sort/.reverse/.discard/.add/.update`: s005 s016 s017 s018 s035
s106 s119 s134 s166 s167 s184 s220 s236 s251 s265 s281 s316 s342), mostly over Any-IR worklists; R252 erased-to-
builtin (s036 s107 s109 s122 s123 s143 s146 s335); R542 / R381 / R325 dict values (s161 s168 s276 s281 s282 s285
s152); recursion (s068 s069 s070 s309); filesystem (s014 s016 s017 s018 s141 s143: lvQ). The dominant blocker is
the Dict[str, Any] / Any-IR value model, which is the redirected scope.
