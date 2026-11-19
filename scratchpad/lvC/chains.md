# lvC chain census: R325 opaque-int fallback, small/medium home files (run #5, batch lvC)

Base 07fe9acc3 (run5-int33 = main + u25 + lvA). Method = lvA's: port the VERBATIM live body into a
scratch copy of the mirror (`bin/port-one-mirror-body.py --convert [--replace]`, `scratchpad/lvC/probe.sh`),
emit `--no-proof` (incl. the Why3 type-check) on QUICK, read the first blocker; hand-patch it in the
scratch copy or build the candidate capability in the scratch emitter `st/` and re-emit the verbatim
body, until TC-OK; then `--fun` (NORMAL) and an honesty read of the emitted body. To read a route-#325
refusal's WhyML, `st/src/pycsl/pycsl.py` carries a scratch-only dump (`LVC_DBG_MLW`, never landed).
Probe outputs: `probe/r1_*` (first links, = cv8), `probe/r2_*`..`r4_*` (later links).

## Chain table

| stub | file | link 1 (cv8 first blocker) | link 2 | link 3 | end state |
|---|---|---|---|---|---|
| `_typeddict_check_subscript` | core_ir_semantic | R325 on `_` from `warnings_warn_1`, "used" at `Some _ ->`: a SCANNER FALSE POSITIVE -- the discarded `let _ = (warnings_warn_1 ..) in ()` tracked `_` as a tainted local and the wildcard PATTERN of the `x in td_vars` match (`Some _ -> true`) was read as a use (cap-r325-wildcard) | L3-TC: the VERIFIED wall-2 walker `_typeddict_walk_subscripts` calls the leaf with a hard-coded `(any map int (option int))`; the converted leaf's `sub` is κ=string `map string (option int)` (cap-w2a-leaf-type) | TC-OK | **CONVERTED** |
| `_namedtuple_check_subscript` | core_ir_semantic | same as above (cap-r325-wildcard) | same (cap-w2a-leaf-type) | TC-OK | **CONVERTED** |
| `PyCSLWeaver._subst_var` | Module3_Weaver | R325 in `pv_size`: `list` "used" in `size_list (l : list pyval) : int` -- a SCANNER FALSE POSITIVE: the dead `val constant list : int` (from `isinstance(x, list)`) and the WhyML TYPE `list` are different namespaces (cap-r325-typepos, spiked) | R325 (real): the caller `_desugar_for` puts the result `pyCSLWeaver__subst_var_3` (an `Any`, int-erased) into `Seq.snoc` | honesty: the body is dataclass reflection (`_is_dc`, `_dc_fields`, `getattr(node, f.name)`, `_dc_replace(node, **repl)`): every step is an opaque call over an erased node | **REFUSED** (needs a dataclass-reflection / IR-node model) |
| `_rewrite_subscript_calls_in_stmt` | monomorphize | R325 in `pv_size` (same false positive, cap-r325-typepos) | L3-TC `int -> option int` vs `int` at the `new` dict return | honesty: `stmt.items()` lowers to `stmt_items_0 ()` (input-blind), the loop targets `k`, `v` are `any int`, the list arm is `list_comp 0`: an input-blind FACADE | **REFUSED** (needs the pyval `Any`-walker lowering for a dict-REBUILDING recursion; signature `stmt: Any -> Any` is int-erased) |
| `collect_module_constants` | module_collect | R325: `getattr(node, "body"/"csl_shared_decls", ..)` on the imported `ast.Module` (cap-R325-call-getattr-unknown) | L3-TC `unbound type symbol py_module_node` (cv8 B1b): `functions._param_type_str` types the param `py_module_node` whenever `_uses_pyast_stmt`, but the `pyast_stmt`/`psl`/`py_module_node` block lives in `_emit_exprir_theory`, emitted only for an emit_ir (`@mutable_state`) file -- an EMITTER DEFECT, but fixing it means emitting the whole emit_ir/pyast theory into module_collect | honesty: (a) the return `{n: v for n, v in candidates.items() if ..}` lowers to `dict_comp 0` -- the function's ONLY output is input-blind; (b) the emitted body reads `_module_const_int pycsl_none` and tests `pycsl_none = pycsl_none` for `target is None` after the tuple-unpack rebinding `target, value = ..` (the None-initialised locals are folded, the unpack store is not seen) | **REFUSED** (facade return; 3+ links incl. a dict-comprehension model) |
| `collect_module_globals` | module_collect | same getattr (cap-R325-call-getattr-unknown) | same theory gap | same `dict_comp`/None-folding honesty | **REFUSED** |
| `_ChainDesugarer.visit_Compare` | desugar | R325: `ast.Compare(..)` constructor result `link` into `Seq.snoc` (cap-R325-call-ast-ctor) | in-place `ast.copy_location` / `fix_missing_locations` on constructed nodes, `self._n += 1` | -- | **REFUSED** (needs pure_ast node constructors + in-place mutation model) |
| `_try_reaches_assert` | desugar | R325: `ast.walk(tree)` element `_n` (cap-R325-call-ast-walk) | worklist fixpoint `while _changed:` over a dict of bools: no variant without a counting model of `_has` (lvA's `\diverges` refusal class) | -- | **REFUSED** (ast.walk model + termination) |
| `_check_gt4_polymorphic_recursion` | monomorphize | R325 in `_extract_ast_subscript`: stdlib `_ast.walk(validated_ast)` element (cap-R325-call-ast-walk) | `set(gen_tvars)` constructor (lvB's family, excluded) | `PyCSLSemanticError(..., code=..)` raise with an f-string over `!r` | **REFUSED** (stdlib-ast walk model; set ctor owned by lvB) |
| `_ContractParser._grab_reviewer_id` | Module2_Parser | R325 in `_parse_trusted`: `m.group(0)` -> `m_group_1 0` (input-blind) flows into the record field `trusted_reviewer` (cap-R325-call-re) | `re.match(<lit>, self.source[pos:])` lowers `_re_match_2 h (array_slice (getattr__contractparser self h') ..)`: `self.source` is an opaque getattr erased to `array int`, not a string field | needs an Optional[Match] model (`m is None`, `m.group(0)`) -- lvA refused `_nat_to_int_with_sidecond` for the same reason | **REFUSED** (3 links: re.Match model + string `self.source` field + record string field; big owed file) |
| `_ContractParser._parse_contract` | Module2_Parser | R325: `_m_di.group(0)` (same Match model) | 81-line dispatcher returning ~60 distinct clause-node kinds | -- | **REFUSED** (Match model + scale) |
| `_ContractParser._parse_quantifier` | Module2_Parser | R325 in `_parse_or_rhs`: `cls = Exists if is_exists else Forall` -- a CLASS OBJECT as a value (`_class_py_exists` constant) then called `cls(var, ..)` (probe r2: hand-patched to explicit `if is_exists: Exists(..) else Forall(..)`) | L3-TC: `binder_type=ty` puts a `string` into the `option string` record field (no `Some` lift for a str actual in `_call_record_constructor`) (probe r3: `binder_type` dropped, scratch only) | L3-TC: the `Exists`/`Forall` RECORD (`py_exists`) is returned where the method returns `ExprIR` = `emit_ir`: needs the `IrExists`/`IrForall` emit_ir construction with `iropt_str`/`iropt_ir` options (`_lower_irnode_construction` covers only the Module5 `_csl_forall` read shape); then `ForallItems` -> `IrForallItems`, the `DictView` isinstance + `domain.kind`/`.coll` reads on an emit_ir, the `reversed(names)` rebuild loop | **REFUSED** (>= 4 capabilities in the `expressions.py` call/ctor lowering, `\trusted` twins; and link 4 is a FIDELITY wall: `DictView` is not an emit_ir constructor -- `isinstance(domain, DictView)` is the opaque `py_isinstance_DictView_emit_ir_op` and `domain.kind == "items"` lowers to `str_eq_op (kind_of !domain) "items"`, the emit_ir NODE-KIND tag, not DictView's `kind` field (probe r3 line 1195): a faithful lowering needs an emit_ir ADT extension, which moves every emit_ir mirror) |

## Set cover

Capabilities built (emitter-local, law-free, axiom-free, no new model):

- **cap-r325-wildcard** (`src/pycsl/pycsl.py`, `_run_pipeline`, a `\trusted` twin): route #325's taint scanner
  skips every `_` token. In WhyML `_` is the reserved wildcard PATTERN (`let _ = e in`, `Some _ ->`, `| _ ->`,
  `fun _ ->`) and can never be referenced, so no `_` token is a read of any value. Removes a false
  positive only; named bindings of a fallback are untouched (witness 8901). Checked: a Python variable
  named `_` is emitted `py_underscore` (`whyml_ident`), so every bare `_` token in an emission is an
  emitter-generated wildcard. Emission-neutral (the scanner
  only decides refusals).
- **cap-w2a-leaf-type** (`module6_whyml/functions.py` `_emit_function_block`, NO mirror twin;
  `module6_whyml/generic_fold.py`, no mirror): the wall-2 `.items()` walker hands its leaf an arbitrary
  `any <T>` for the matched sub-dict; `<T>` is now the type the leaf's first (`dict`) parameter is EMITTED
  at, computed with the same `_dict_param_whyml_type` over the leaf's IR `dict_key_types` /
  `dict_value_types`. A `\trusted` stub leaf has no key-type evidence -> the legacy
  `map int (option int)` (byte-identical). Sound for any leaf: the value is unconstrained, so a leaf
  precondition on it remains an unprovable call VC (witness 8905).

`warnings.warn`: NO new model. It stays the existing unmodelled opaque call (`val warnings_warn_1 (x0: int)
: int`, no spec), its result discarded. Decision: the two leaves' contracts claim only type safety + frame
(`requires True`, `ensures True`, `assigns \nothing`) -- partial correctness, no `no_exception` -- so an
exceptional exit under `-W error` (UserWarning) is outside every claim; the warning registry / stderr are
not modelled state (the `recognize_check_warn_fold` precedent already treats the call as a report-only
side channel in verified mirror code). A `#@ no_exception` claim over a `warnings.warn` call must still
fail (witness 8902).

Cover: {wildcard, leaf-type} converts `_typeddict_check_subscript` + `_namedtuple_check_subscript`.

Spiked, NOT landed (no conversion consumes it this batch): **cap-r325-typepos** -- route #325's scanner
skips tokens inside a WhyML TYPE expression (after a `:`: identifiers / `'a` / balanced `( .. )` groups /
`Upper.` module qualifiers, stopping at any other token or keyword). It removes the `pv_size` / `list`
false positive of `_subst_var` and `_rewrite_subscript_calls_in_stmt`, but both are refused further down
(honesty). Patch: `scratchpad/lvC/typepos.patch`.

## Gates (candidate = base + cap-r325-wildcard + cap-w2a-leaf-type + the 2 conversions)

- `--fun _typeddict_check_subscript`: SUCCESS, own goals 2/2 Valid, file total 1512/1512 (`--no-check-vacuity`;
  vacuity is covered by the whole-file run below, which re-probes every function -- a default `--fun` repeats
  that ~1.5 h pass and was stopped at 50 min). `--fun _namedtuple_check_subscript`: SUCCESS, 2/2, 1512/1512.
- WHOLE-FILE `core_ir_semantic` mirror (LOW, default non-vacuity gate ON): **Verification SUCCESS, 1517/1517
  Valid, 0 non-Valid**, 1 h 51 min wall.
- Honesty read: each leaf reads `sub["value"]`, `sub["index"]`, `fname`, and the `td_vars` / `nt_vars` membership;
  the literal tags hash into the emission (`"Var"`, `"String"` / `"Number"`); `recv.get(..)` / `idx.get(..)` on the
  int-erased sub-dict values are plain non-deterministic `val`s (a sound over-approximation, the int-erasure
  seam), `isinstance(recv, dict)` is `any bool`. Not input-blind. Contract = type safety + frame only.
- Mutation (`"Number"` -> `"Numbr"` in the mirror body): emission moves (`idx_get_1 .. = 2056183843` ->
  `1797805438`), mirror-sync fidelity FAILS (rc 1). (The proof cannot fail: the contract claims only `ensures True`.)
- Mirror sweep vs base: 53/53, **1 MOVED = core_ir_semantic** (the home), 0 GONE, 0 APPEARED.
- Corpus root vs base: 2895/2899, **0 MOVED, 0 GONE, 0 APPEARED** (4 new witness sources). pyref: 2185/2185,
  0/0/0.
- Fidelity: check-self-annotate-sync rc 0 (944 verbatim), self-annotate-mirror-check rc 0, doc-coherency rc 0.
- `\trusted` (governing `#@ \trusted` grep): 413 -> 411. trusted-reasons.tsv: 2 rows removed.

## Witnesses (8900-8905)

| id | expected | base | candidate | claim |
|---|---|---|---|---|
| 8900 wildcard_discard | PASS | REFUSED (R325 on `Some _`) | **PASS** | discarded `warnings.warn` + `k in seen` match in one function |
| 8901 wildcard_value_used_false | FAIL | REFUSED | REFUSED (R325 on the named `r`) | the warn RESULT bound and used as int (CPython TypeError) |
| 8902 warn_no_exception_false | FAIL | REFUSED | REFUSED | `no_exception \all` over `warnings.warn` (raises UserWarning under `-W error`) |
| 8903 wildcard_post_false | FAIL | REFUSED | FAIL (postcondition) | CPython-false `\result == n + 1` on the admitted shape |
| 8904 w2a_verified_leaf | PASS | FAIL (L3-TC: `map int` vs `map string`) | **PASS** | wall-2 walker over a VERIFIED string-keyed leaf |
| 8905 w2a_leaf_requires_false | FAIL | FAIL | FAIL (call precondition) | leaf requires `not ("type" in sub)`; walker only calls it on a dict with `"type"` |

## Side finding (NOT in scope, NOT fixed): None-folding unsoundness at base

`scratchpad/lvC/side/none_fold_unpack.py` PROVES `\result == 0` at base 07fe9acc3 while CPython `f(1) == 1`:

    t = None; u = None
    if x > 0: t, u = 1, 2
    if t is None: return 0
    return 1

Emission: the `if t is None` test lowers to `if (pycsl_none = pycsl_none)` (the tuple-unpack store
`let (_tu_t, _tu_u) = (1, 2) in t := _tu_t; ..` is emitted, but the READ of `t` folds to the None constant). With
a plain store (`t = 1`, `side/none_fold_plain.py`) the test is the correct `(!t = pycsl_none)`. So a
"None-initialised, never-reassigned local reads as `None`" fold does not count tuple-unpack targets as stores.
The module_collect conversions hit exactly this (`target, value = ..` then `if target is None: continue`).
Root cause not located (it is not `_recognize_none_constant_guard`); needs a route + witness by the driver.
