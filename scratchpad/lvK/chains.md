# lvK (run #5, last batch): TC-OK-PARTIAL conversions under the lvI honesty rule

Base run5-int48 b105e8d87. Censuses: getting-better/run5-chain-census.md (s004 s019 s040 s048; cv9),
getting-better/run5-hot-chain-census.md (h003; cv10).

Rule applied: a converted body may hold a sound-but-input-blind piece ONLY if the contract claims
nothing about it AND the body reads its real inputs wherever its effect / result depends on them; a
body whose RESULT is input-blind is a facade and is not converted.

## Conversions

### PyCSLWeaver._validate_function_contracts (frontend/Module3_Weaver.py)  [s048]
- LIVE equivalent rewrite: `for _cm in getattr(node, "csl_acts", []) or []:` ->
  `if getattr(node, "csl_acts", []):` / `for _cm in getattr(node, "csl_acts", []):` (body re-indented).
  Equivalence: `x or []` iterates `x` when truthy, `[]` (nothing) otherwise; the rewrite does the same.
  It reads the attribute twice: `csl_acts` is a plain instance attribute of the `ast.FunctionDef` (set
  by `_init_function_csl_fields` / `_dispatch_function_contracts`; no property, no __getattr__ on ast
  nodes), nothing runs between the two reads, so both are the same object. First draft (`_acts =
  getattr(..)` / `if _acts: for _cm in _acts:`) emitted the loop over a mutable ref WITHOUT a snapshot
  length / variant: `--fun` 1 termination Timeout (fun/vfc1.log) -> replaced. No new capability: the
  getattr is the same opaque `pycsl_getattr_unknown_<h> node` lowering the `csl_trusted` /
  `csl_abstract` reads of the same function already use, the loop the landed erased-iterable
  `iter_length` snapshot / `iter_get` lowering with its variant. The cv9 `_cv9_list` stand-in is NOT
  used. Mirror ported verbatim (bin/port-one-mirror-body.py --convert).
- Honesty: the emitted body reads `node` everywhere its effect depends on it: the trusted/abstract
  guard (`pycsl_getattr_unknown_* node`), the acts loop (`iter_* (getattr node)`, `type(_cm).__name__`),
  the ensures loop (`get_csl_ensures node`, `get_expr/get_op/get_left/get_right/get_value`), the
  variant/diverges guard (`get_csl_function_variants node`, `get_csl_diverges node`); its effects (raise
  PyCSLSemanticError / warnings.warn / raise ValueError) are guarded by those reads. OPAQUE: the pyast
  attribute getters (no pyast-attribute model) and the warn message strings (hashed literals). The
  contract (`requires True` / `ensures True` / `assigns \nothing`, raises inferred) claims nothing
  about either: no verdict, no message.

### _Tok.__repr__ (frontend/pure_ast.py)  [h003]
- LIVE equivalent rewrite: `{self.start}` -> `({self.start[0]}, {self.start[1]})`. Equivalence:
  `start` is always a 2-tuple of ints (`tokenize` TokenInfo.start, or `_lex.to_byte` which returns
  `pos` or `(row, len(...))`), and `str((a, b)) == f"({a}, {b})"` for ints (repr(int) == str(int)).
  Mirror: ported verbatim + faithful retype `def __repr__(self) -> str:` (the cv10 [T] link);
  the record field `start: Tuple[int, int]` is the already-verified `_Tok.__init__` model.
- Honesty: the emitted body reads `self.py_type`, `self._tok_string` (`str_repr_op`),
  `self._tok_start.field0` / `.field1` (both `int_to_string`): every field the repr depends on.
  OPAQUE: `_tokenize.tok_name[self.type]` is `subscript_get (get_tok_name _tokenize) self.py_type`, an
  opaque table indexed by the REAL type field (not a constant); its str is `int_to_string` of the
  erased handle. The contract (`ensures True`, frame) claims nothing about the string.

## Refusals

### ReverifyReport.summary (audit_proof_reverify.py) [s004]: REFUSED
- The RESULT string carries three pieces the census reached only through stand-ins that DROP them:
  `{self.elapsed_compile_s:.2f}` (base L3-tc: `real` where `int` expected: no float format / float->str
  lowering), `len(self.qualname_results)` (array vs erased iterable) and `sum(1 for (_, ok, _) in ..
  if ok)` (lowers to `sum_1`, an unconstrained int). A stand-in is not a port (mirror-sync fidelity
  requires the live body), and with any of them the returned string is input-blind exactly where it
  depends on its inputs. No equivalent live rewrite exists for `:.2f` (correct float rounding needs a
  float model): that is a NEW emitter capability (fstring-float-format + float-str), out of scope.

### ConcurrencyChecker._walk_stmt (frontend/ConcurrencyChecker.py) [s019]: REFUSED
- Three stand-ins, each removing input dependence the effect needs: (1) `target.id` / `getattr(node,
  'lineno', 0)` (erased pyast fields) into the `str` / `int` slots of `_warn_if_unprotected` are refused
  by route #252 fail-closed; replaced by literals the appended warning (the method's whole effect)
  stops depending on the variable name -> facade effect; (2) `held | {mutex}` (set union, erased
  element) dropped; (3) the `_walk_body <-> _walk_stmt` method-recursion cycle is refused by ir-semantic
  (no termination measure); a structural variant would need a size measure on the erased `ast.AST`
  node (no pyast-node model). All three are new capabilities (pyast node typing, erased set union,
  method-recursion measure) -> skip.

### _ContractParser._parse_inductive_rules (frontend/Module2_Parser.py) [s040]: REFUSED (lvF upheld)
- Re-evaluated under the lvI rule. Emitted (cv9 s040_2.mlw): the token walk is real (`at_name`,
  `expect_name`, `expect_op`, `_parse_expr` all advance `self.i`), but each `rules.append((rname,
  self._parse_expr()))` lowers to `let _ = (!rname, _parse_expr self) in rules := Seq.snoc !rules (any
  int)`: the value is computed and DISCARDED, the list element is a fresh unconstrained int. The
  function's RESULT is the rule list; its length follows the loop but every element (the only thing
  the two callers consume) is input-blind. That is not the augassign shape (there the blind piece was a
  guard whose outcome the contract does not mention, while the result/effect read the real inputs);
  here the blind piece IS the result's content -> facade on the result, refused. Needs a (str, ExprIR)
  tuple element model (vm-unerase-tuple), a new capability.

## Gate record (candidate = run5-lvK working tree, base b105e8d87)
| gate | result |
|---|---|
| `--fun pycslweaver___validate_function_contracts` | 280/280 Valid, rc 0 (fun/vfc2.log). First draft (local `_acts`): 1 termination Timeout (fun/vfc1.log), replaced |
| `_tok____repr__'vc` (pure_ast: `--fun` refused on pure_ast, goal proved in the full emitted module tc/c1) | 5/5 split goals Valid, Alt-Ergo 2.6.3 AND Z3 4.13.3 (fun/repr1.log) |
| mutation Module3 (frame: hidden `node.csl_trusted = True`) | REJECTED, PYCSL-METHOD-FRAME (route #316) (fun/mvfc1.log) |
| mutation pure_ast (claim: `ensures \result == "Tok()"`) | NOT proved: postcondition Timeout under both provers (fun/mrepr2.log); frame mutation `self.string = ""` refused at L3-tc (immutable field) |
| corpus root + pyref vs base | root 3002/3002 0 MOVED/GONE/APPEARED; pyref 2185/2185 0/0/0 (sw/cmp-corpus-c.txt, cmp-pyref-c.txt) |
| mirror vs base | exactly 3 movers: frontend/Module3_Weaver (conversion), frontend/pure_ast (conversion + `_tokenize` / `get_tok_name` decls), pycsl (DECLARATION-ONLY: the `_validate_function_contracts` val gains `raises { PyCSLSemanticError, ValueError }`; no caller in pycsl.mlw; QUICK type-check rc 0, tc/c3). expressions / statements NOT moved |
| honesty planes | yield-erasure rc 0, computed-rhs-erasure rc 0, emitted-vacuity rc 0 (0 input-blind, no NEW erasure) |
| fast planes | 62/62 green (sw/planes-c.txt; incl. trusted-reasons, claim-vacuity, termination honesty, untrusted-emitted) |
| fidelity | check-self-annotate-sync rc 0, self-annotate-mirror-check rc 0, doc-coherency --check rc 0 |
| `\trusted` (grep-substring) | 406 -> 404 (markers 378 -> 376) |
| ledger | 3 (no axiom / proof line / proof-axiom file touched) |

OWED (not run): whole-file `frontend/Module3_Weaver.py`, `frontend/pure_ast.py` mirror proofs
(`pycsl.py` moved by a declaration only, type-checks).
