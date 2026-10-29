# levers-r3.md — LEVERS ledger, driver run #3 (SKILL §A.6), executor lv1

Base `76537c560` (main + R5-str + `_split_rocq_check_output`; `#@ \trusted` lines 445,
`trusted-reasons.tsv` 417 markers). Time box 2026-10-27T00:00Z. Measured facts only; every
"unlocks" number below is a count of stubs that reached the stated stage in a scratch tree
with the lever prototyped, NOT an estimate. Scratch instruments under the session scratchpad
`lv1/` (`tc.sh` = port + `--no-proof --keep-mlw` + clash slice, one stub at a time, mirror file
restored between; `port_sig.py`; `apply_guard.py` + `fix_guard*.py`; `apply_r5x.py`).

Stage names: **TC-OK** = verbatim live body ported, marker deleted, file emits AND Why3
type-checks; **4-green** = the four oracles of `bin/screen-conversion-candidate.sh`
(untrusted-emitted, yield-erasure, shadowed-selfcalls, emitted-vacuity) green;
**PROVES** = home-file whole-file proof 0 non-Valid.

## Ranked ledger (ROI = unlocked x confidence / cost; no-new-cert and proven-feasible first)

| rank | lever | what | stubs unlocked (MEASURED) | cost | new cert? | risk | verdict |
|---|---|---|---|---|---|---|---|
| 1 | **L-T1 guarded constructor arm in the Term->Term transform recognizer** | `generic_fold.py` (NOT mirrored): accept `if isinstance(t, C) and t.F == "<lit>" and len(t.L) == K: return Ctor(...)` before C's general arm; lowered inside C's match arm as `if pystr_eq v_F "<lit>" then (match v_L with <K-cons> -> (match (n__list v_L) with <K-cons r> -> Ctor .. r_i .. \| _ -> general) \| _ -> general) else general` | **1** (`proof2why3/canonical.py::_iff_app_to_binop`): TC-OK, **4-green**, **PROVES** (canonical.py whole-file 65 Valid / 0 non-Valid, 99 s) | ~140 lines in a non-mirrored file; corpus exposure = files with a term-ADT transform (fail-closed gate) | **no** (same `term` inductive, `Phase2i_TermIR` cert; `val pystr_eq` precedent; ledger 3) | low | **BUILD (picked)** |
| 2 | L-R5x: R5-str residual extension | `enumerate(<R5 split/splitlines local>)` -> the existing array loop arm; a `for x in <str>.split/splitlines() \| R5 local \| flat List[str] formal` target counts as a string source of a `seq string` accumulator (so `"sep".join(acc)` -> `str_join_seq`) | **0** of the 45 stubs whose live body has `split/splitlines` AND `enumerate`/`.join`; chain advanced by one link in **2** (`pycsl.py::_function_body_eqs`: now stops at `re` `m.group(1)`; `pycsl.py::_parse_goal_blocks`: now stops at the `List[Tuple[str,str]]` accumulator / `-> int` return) | ~40 lines (`stmt_control_flow.py`, `statements.py` — mirrored files, `\trusted` twins) + corpus re-proofs | no | low | **BROKEN-NOT-BUILT (0 yield)**; reopening = `re` model (R5-lib, new shape, coupling rule) and a string-tuple list model |
| 3 | L-SIG: port the LIVE signature with the body | replace the mirror stub's placeholder annotations (`-> int`, `'PyConstVal'`, ...) with the live ones (mirror-only) | **net <= 0** over the 141 stubs whose signatures differ: 1 new TC-OK (`pure_ast._parse_number`, only because the live def has NO annotation, i.e. by DE-modelling the `PyConstVal` result its callers rely on), 3 previously TC-OK stubs regress to L3-TC; the other 137 keep their blocker class (110 REFUSED, 29 L3-TC total) | mirror-only | no | caller re-typing in the mirror | **REFUTED** [COST/SCALE: signatures are not the binding link] |
| 4 | L-T2 `_expand_nat_to_int` in the same recognizer | needs 5 fragments: local `let`, `t.ty in {"nat","Nat"}` set-literal guard, list comprehension over a `list string` field building `list term`, a cross-module `mk_arrow_chain` call, `return t` default arm | 1 (by reading; NOT prototyped) | ~2-3 h | no | medium | ranked below L-T1 (same file, 5x the surface for the same yield) |
| 5 | `proof2why3/parser.py::lex` termination | census r3: only termination fails. Needs (a) the computed-receiver `s[j].isdigit()` to reach the SAME `py_isdigit_op` as `c.isdigit()`, (b) `isalpha c -> isalnum c` (no relation between the uninterpreted `py_is*_op` exists: a new trusted fact, or a definitional char-class model), (c) `str_length_op op > 0` for the 14-literal op list, (d) an invariant language for `s[i].isdigit()` | 1 (by reading the emission; 4 links) | high | (b) would be a new trusted fact unless built definitionally | medium | [COST/SCALE] definitional char-class model |
| 6 | `pure_ast._Unparser.write` (receiver mutator `.extend` on `self._source`) | faithful receiver+`writes` lowering | 1, but the honest frame `assigns self._source` costs ~15 re-trusts (the mirror's own note: `write` is an effectful first-class callback of `interleave`) | high (pure_ast whole-file 2.4 h) | no | net negative | [COST/SCALE] effectful higher-order callback lowering |
| 7 | empty-list literal typed by its destination (`[]` at an `array <record>` field / tuple slot / `or []`) | split job 1 of `(Array.make 1024 0)` | 0 standalone by reading: it is the first clash of 11 stubs at HEAD, and every one of the 11 emitted lines shows a further link (`loc_get_1`/`term_get_1` receiver-less facades in `pycsl._record_key`/`_synthesize_block`, `ir_get_1` in `run_ir_semantic_checks`, `getattr`/`ast.walk` in `ConcurrencyChecker.check`) | medium (11 consumer sites keyed on the string) | no | corpus `1871` guard | not prototyped |
| 8 | exception payload (`_ContractParser._err`, `_Parser.error`, `_Parser.unsupported`) | TC-OK already; vacuity RED (msg erased) + shadowed-selfcalls RED (callers route through `self__err_1`) | 0 without BOTH a string exception payload (new shape) and the self-call routing fix | high | yes (payload shape) | — | [COST/SCALE] |
| 9 | generator-sequence model | 3 yield-RED (`iter_fields`, `iter_child_nodes`, `_sexp_tokens`) | 0 without the model | high | yes | — | [COST/SCALE] |

Ranking rationale: L-T1 is the only lever with a MEASURED non-zero yield at every stage
(TC-OK -> 4-green -> PROVES) and it needs no new certificate; its cost is one non-mirrored
file, so the mirror-coverage ratchet and the mirror sweep cannot move (lesson a4). L-R5x and
L-SIG were prototyped and measured at 0 / net-negative.

## Why the yields are 1, not tens (the census-r3 finding, re-confirmed)

No lever found here unlocks more than one stub: the 417 markers sit behind long chains
(int-erasure seam, `re`/`subprocess`/`os.path`, records-as-`int`, receiver-less facades), and
every prototype that advanced a chain (R5-str: 4, L-R5x: 2) moved it ONE link. The cheap
conversions left are shape extensions of an existing certified recognizer in a cheap file
(canonical.py proves in ~100 s), one stub per shape.

## L-T1 — build record (STEP 2)

**B1 `cc380d4fa`** — `src/pycsl/module6_whyml/generic_fold.py` only (not mirrored: mirror
coverage and the mirror sweep cannot move by construction; measured 0 MOVED anyway).
- The guarded arm (above). First emission recursed directly on the pattern-bound elements
  (`_iff_app_to_binop v__g0`): canonical.py then had **2 non-Valid** (`variant decrease`,
  Timeout 26.75 s / 30 s) — Why3's structural variant does not discharge the two-step
  `element < list < term` descent. Fixed by reading the recursed elements off the
  element-wise `n__list` map (one step, the step `_flip_comparisons` already proves) with a
  fallback arm (unreachable at run time; an over-approximation, never an assumption).
- **SOUNDNESS REPAIR found while building it.** The term-ADT recognizers emit a FIXED
  `ensures { true }` and drop the user's contract. MEASURED at base `76537c560`: a
  `_flip_comparisons`-shape transform annotated `#@ ensures False` emitted
  `let rec ... ensures { true }` and printed `Verification SUCCESS! All contracts formally
  proven.` — a false proof. New fail-closed gate `_term_contract_trivial` on all 7 term
  recognizers (fold, transform, list_build, flatten_arrow, free_vars, pp_wrapper, string_pp):
  they fire only when every `ensures`/`requires` is the literal `True` and no raises /
  no_exception claim is made. Corpus and mirror byte-diff 0 => no existing file depended on
  the hole.
- Witnesses (IDs 5820-5822): 5820 PASS (base: REFUSED, route #252 erased->builtin slot),
  5821 PASS twin, **5822 expected FAIL** (base: false SUCCESS; now refused). 5820/5821 carry no
  `requires/ensures True` lines (the claim-vacuity ratchet went RED on the first planes run
  when they did: 1793 > 1791 / 1133 > 1131; removed, re-run green).

| gate (B1) | rc | result |
|---|---|---|
| fidelity `check-self-annotate-sync.sh` / `self-annotate-mirror-check.sh` | 0 / 0 | 929 verbatim / 53 mirrors in sync |
| corpus root `byte-diff-compare.py bd-base bd-cand2 --new-source 5820 5821 5822` | 0 | 2429 base / 2431 cand .mlw, 0 MOVED / 0 GONE / 0 APPEARED (5822 refused -> no .mlw) |
| corpus pyref `byte-diff-compare.py .../pyref --min-files 2000` | 0 | 2186 / 2186, 0 MOVED |
| mirror `mirror-emit-sweep.sh` base vs cand2 | 0 | 53 / 53, 0 MOVED -> no mirror proof owed |
| `run-soundness-planes.sh` | 1 -> 0 | first run 1 RED (`check-claim-vacuity`, witness contracts), after the fix all 61 green (817 s) |
| ledger | — | `proof_axiom_allowlist.py` untouched; no `axiom` emitted |

**B2 `418aa28f8`** — conversion `proof2why3/canonical.py::_iff_app_to_binop` (445 -> 444).

| gate (B2) | rc | result |
|---|---|---|
| whole-file `pycsl.py src/self-annotate/src/proof2why3/canonical.py` | 0 | 65 Valid / 0 non-Valid, SUCCESS (309 s incl. queue) |
| `--fun _iff_app_to_binop` | 0 | 52 Valid, SUCCESS |
| emit-diff | — | `val _iff_app_to_binop (t: term) : term requires/ensures {true}` -> `let rec` match over all 9 ctors + `__list` helper; nothing else moves; reads head/args/op/lhs/rhs/arg/body (non-vacuous) |
| fidelity | 0 / 0 | 930 verbatim / 53 in sync |
| mirror sweep vs B1 | 0 with `--expect-moved proof2why3__canonical` | exactly 1 MOVED = canonical.mlw, its diff byte-equal to the proved emission's diff |
| corpus | — | `src/pycsl` unchanged since B1 (inert by construction) |
| planes | 0 | 61 green (732 s) |
| `check-trusted-reasons.py` | 0 | 416 markers <-> 416 rows |
| count | — | `#@ \trusted` lines 445 -> **444** |

## L-T2 status + lv2 build record (`substitute`, driver run #3)

**L-T2 was already built** before lv2 started: cv3 L-T2 `400ff13df` (block arm + default
identity arm) and the conversion `db8d0dc67` (`_expand_nat_to_int`, 445 -> 444), then L-T3 /
L-T3b (`_sort_arrow_hypotheses`, `_dedup_arrow_chain`, 444 -> 442). This ledger's rank-4 row
was stale. lv2 therefore spiked the SIX remaining `canonical.py` stubs (verbatim port,
`--no-proof`, first blocker, at `778aa6e22`):

| stub | first blocker (measured) |
|---|---|
| `_normalize_type_string` | R325: `_re.split` has no model (re library) |
| `_normalize_names` | transform recognizer declines (dict comprehension over `zip`, `substitute(..) if mapping else ..`, calls of `_camel_to_snake` / `_normalize_type_string`) -> generic lowering -> R325 `tuple_1` |
| `substitute` | 2-parameter transform (a `Dict[str, str]`) -> recognizer declines -> R325 `tuple_1` |
| `_alpha_rename` | a WRITING self-call (`counter[0] += 1`) inside an opaquely lowered generator |
| `_flatten_foralls` | in-place `binders.extend(..)` (no certified mutator lowering) |
| `_ac_normalize` | nested closure `collect` captures `operands`, `t` (unfaithful lift) |

`substitute` was picked: one new value shape, no certificate. **B1** (`generic_fold.py`,
`preamble._emit_term_theory` - neither mirrored): `_recognize_term_transform_strmap`, a
separate fail-closed path of the transform recognizer for exactly two params `(t: U, m:
Dict[str, str])` (IR `dict` + key/value types `string`). The dict is the abstract type
`term__strdict`; `m.get(t.F, t.F)` -> uninterpreted `val function f__get`, the filtering
`{k: v for k, v in m.items() if k not in t.B}` -> uninterpreted `val function f__restrict m
v_B`. Both are deterministic in their inputs (the body never mutates `m`), so they are an
over-approximation, never an assumption (no axiom). The IR keeps a tuple comprehension
target only as `_comp_var`; that is immaterial here because `restrict` claims nothing about
which entries survive. Kept from L-T1: `_term_contract_trivial` gates it (it sits inside the
recognizer after the gate); recursion on the `list term` child goes through the
element-wise `f__list` map (structural `variant { l }`); no fallback arm was needed.
Fragment-by-fragment (scratch tree): 2-param path -> TC FAIL `unbound re_sub_op` (the
abstract-op block is spliced after the LAST `type` line, and the first prototype emitted
`type f__dict` inside the function group) -> `type term__strdict` moved to the term theory
-> TC-OK -> four oracles of `screen-conversion-candidate.sh` green (untrusted-emitted 903
definitions / 0 re-abstracted; yield-erasure OK; shadowed-selfcalls 14 = ratchet;
emitted-vacuity no new erasure) -> `--fun substitute` SUCCESS -> whole file SUCCESS.
Hardening before the build: comprehension / generator variables may not shadow `t` / `m`,
and every builder's value type must equal its constructor slot type (fail closed).
**B2**: conversion `proof2why3/canonical.py::substitute` (mirror signature `mapping: int` ->
`Dict[str, str]`, the live one; verbatim body), trusted-reasons row removed; 442 -> **441**.

Gate battery (one run on the B2 tree, uncommitted at the time, base `778aa6e22`; bases
v10/ca + v10/ma = emission of `c53b5e381`, main docs-only since; logs under the lv2
scratchpad). B1 alone is mirror-inert by construction (`substitute` still `\trusted`, so no
mirror function reaches the new path) and has the same `src/pycsl` as B2.

| gate | rc | result |
|---|---|---|
| fidelity `check-self-annotate-sync.sh` / `self-annotate-mirror-check.sh` | 0 / 0 | 933 verbatim / 53 mirrors in sync |
| whole file `pycsl.py src/self-annotate/src/proof2why3/canonical.py` | 0 | 189 Valid / 0 non-Valid, SUCCESS (base 179) |
| `--fun substitute` | 0 | SUCCESS, 0 non-Valid |
| emit-diff (canonical.mlw vs v10/ma) | — | `type term__strdict` in the term theory; `val substitute (t: term) (mapping: int) : term` -> `get`/`restrict` `val function`s + `let rec substitute` over all 9 ctors + `substitute__list`; nothing else moves; 0 `axiom`; reads name/head/args/op/lhs/rhs/arg/binders/ty/body + mapping (non-vacuous) |
| corpus root `byte-diff-compare.py v10/ca cand --new-source 6800 6801` | 0 | 2563 / 2564, 0 MOVED / 0 GONE / 0 APPEARED (6801 refused -> no .mlw) |
| corpus pyref `--min-files 2000` | 0 | 2186 / 2186, 0 MOVED |
| mirror sweep vs v10/ma `--expect-moved proof2why3__canonical` | 0 | 53 / 53, exactly 1 MOVED = canonical.mlw, byte-equal to the proved emission |
| `run-soundness-planes.sh` | 1 -> 0 | first run 1 RED `check-assigns-underdeclaration` (TRAP 4 > 3): the first B1 stashed a NEW self field in the `\trusted` mirror method `_scan_preamble_needs`, whose declared frame omits it. Fixed by computing the need inside the non-mirrored `_emit_term_theory`; re-run 61/61 green |
| trusted-reasons | 0 | 413 markers <-> 413 rows |
| doc-coherency / assumed-facts `--emit-dir` | 0 / 0 | in sync / every fact reviewed (ledger unchanged, no axiom) |
| refusal-witness-coverage / advice-audited / dropped-mutation / getattr-erasure / open-route-carriers | 0 each | 341 demonstrated / 168 of 231 / 0 dropped / DECLARED 0 / carriers reproduce |
| trusted-frame-honesty / trusted-raises-honesty / clause-survival `--emit-dir` | 0 / 0 / 0 | 0/1, 0/93 / 19 declared, 52 silent (was 53: `substitute`'s `raise` left the trusted set) / 10 ledgered deficits of 1506 |
| witnesses | — | 6800 base REFUSED (R325 `tuple_1`) -> cand PROVES; 6801 (expected FAIL) cand REFUSED (contract gate declines -> R325), base REFUSED |
| count | — | `#@ \trusted` lines 442 -> **441** |

Residuals: (a) `get`/`restrict` are uninterpreted, so `substitute` proves type-safety,
termination and frame only (the fixed `ensures True` shape), not that renaming is correct;
(b) the IR drops a comprehension's tuple target (`_comp_var`) - harmless here (see above),
but the older DictComp recognizers that READ `k`/`v` by name (generic_fold.py ~2887, ~3320,
~11203) rely on the unpacking order the IR does not record: UN-PROBED, a candidate red-team
probe (`{v: k for k, v in d.items()}` vs `{k: v ...}`).

## lv4 build record (`_flatten_foralls`, driver run #3, 2026-10-29)

Base `370db7dc2` (main; `#@ \trusted` 439, trusted-reasons 411). Bases v12/ca + v12/ma.

**B1 `8a6f26cd1`** - `generic_fold.py` only (not mirrored). The `while True:` SCAN loop in a
single-class block arm of a 1-param term transform (`scan` in `_parse_block_arm`; annotations
7.220, translational T.6.230): a local structural `let rec f__scanK (state) variant { s_cur }`
(`continue` = recursive call, accepted only after the one `cur = cur.F` step under an
isinstance narrowing; `break` = return the state), the list accumulators through a defined
total append `f__app`, the look-ahead `while isinstance(w, C) and ..: w = w.G` as a local
structural skip; plus `list(t.F)` / `[]` fresh list locals, `tuple(x)` identity and the
`if xs: y = E` re-binding. ALIASING guard: a mutated list must be created by the block and
not read before the loop. Fragment-by-fragment (scratch tree): verbatim port -> TC-OK (first
emission) -> `--fun _flatten_foralls` 222 Valid / 0 -> four screen oracles green
(untrusted-emitted 906 / 0 re-abstracted; yield-erasure OK; shadowed-selfcalls 14 = ratchet;
emitted-vacuity no new erasure) -> whole file 241 Valid / 0 (base 225). Witnesses 7100
(PASS, 18 Valid; base REFUSED), 7101 (`ensures False`, refused), 7102 (aliased list, refused;
MEASURED load-bearing: with the aliasing check disabled 7102 PROVES an unfaithful model),
7103 (continue without a spine step, refused; with the descent check disabled the
`variant decrease` times out, 2 non-Valid: defence in depth).

**B2 `14d58d01f`** - conversion `proof2why3/canonical.py::_flatten_foralls` (439 -> **438**;
trusted-reasons 411 -> 410). Gate battery on the B2 tree: fidelity 0 / 0 (936 verbatim, 53
mirrors); doc-coherency 0; root byte-diff 0 MOVED / 0 GONE / 0 APPEARED (2592 / 2593, 7100
new); pyref 0 MOVED (2186 / 2186); mirror 1 MOVED = canonical.mlw, byte-equal to the proved
emission; planes 61/61; trusted-reasons 410 <-> 410; assumed-facts 0; refusal-witness-coverage
361; advice-audited 188; dropped-mutation 0; getattr-erasure DECLARED 0; open-route-carriers 0;
frame-honesty 0/1, 0/93; raises-honesty 19 / 50 silent (was 51); clause-survival 10 ledgered
of 1542.

**B3 `aac72b30f` / B4 `1751aef78`** - the AC flatten-sort-refold arm (`_parse_ac_guard`,
annotations 7.221, translational T.6.231) and the conversion of
`proof2why3/canonical.py::_ac_normalize` (438 -> **437**; trusted-reasons 410 -> 409). First
blocker at base: REFUSED at `functions.py:9781` (the lifted `collect` captures `operands`,
`t`). Built WITHOUT touching the mirrored wiring: `compute_term_adt_spec` pairs a transform
with the lifted sibling that follows it and marks it folded; the folded sibling's own
recognition returns `{"folded": True}` and emits nothing, which `functions.py` reaches
before its closure-capture refusal. Fragment-by-fragment (scratch tree): TC FAIL `unbound
term__list_size_nonneg` (the group preceded the file's size theory: a size-mode transform
group now declares it when first) -> exact string equality: `use string.OCaml as SO` makes
every later int literal ambiguous with `int63` (measured), and `str_eq_op` is absent from
the `--fun` emission, so the root call `G(t)` is lowered to its descent branch (`t.F ==
t.F` is reflexive) and every inner test stays `pystr_eq` -> TC-OK -> `--fun` 4 non-Valid:
the leaf called `_ac_normalize q` TWICE (fixed: one `let`), a global-lemma context pushed
`flatten_arrow_chain__eta` over its limit (fixed: the length laws are ghost functions
called where used), and the non-emptiness postcondition of `collect` timed out (local
`let rec`, then as a group member with `variant { term__size q + 1 }`, measured both) ->
fixed by returning `(h, r)` = the non-empty reversed accumulator `Cons h r` (syntactic) ->
`--fun` 259 Valid / 0 -> whole file 277 Valid / 0 -> four oracles green. Witnesses 7104
(PASS 124 Valid; base REFUSED), 7105 (`ensures False`, refused), 7106 (`collect(node)`
itself: declined, refused). Gate battery on the B4 tree: fidelity 0 / 0 (938, 53); doc 0;
root 0 MOVED (2592 / 2594); pyref 0 MOVED (2186); mirror 1 MOVED = canonical, equal to the
proved emission; planes 61/61; trusted-reasons 409 <-> 409; assumed-facts 0; rwc 361;
advice 188; dropped-mutation 0; getattr DECLARED 0; carriers 0; frame-honesty 0/1, 0/93;
raises-honesty 19 / 49 silent; clause-survival 10 ledgered of 1543.
Residual: the key `x.M()` is an uninterpreted total function, so an exception the key
method could raise is outside the model (the same stance as every term recognizer, which
claims nothing about exceptions: `_term_contract_trivial` refuses any raises claim).

**Spikes stopped (measured blockers).**

| candidate | first blocker (measured) | why stopped |
|---|---|---|
| `parser.py::lex` (termination) | the emitted outer `while (!i < !n)` carries no variant; the digit / ident inner loops test the COMPUTED receiver `s[j].isdigit()` / `s[j].isalnum()`, lowered to the polymorphic receiver-blind-by-type `val isdigit_1 (x0: 'a0) : int` / `isalnum_1` (expressions.py ~12270), NOT `py_isdigit_op` of `c = s[i]`, so `j > i` after the inner loop is unprovable; no `py_isalnum_op` exists, so `isalpha c -> isalnum c` has no carrier (Python defines `isalnum` of one char as `isalpha or isdecimal or isdigit or isnumeric`, so a DEFINITIONAL model is possible, but it lives in mirrored `expressions.py` / the abstract-op preamble and moves every corpus file using it); the op loop's `i += str_length_op op` needs `length op > 0` for 14 `Seq.get` literals (two built by `pystr_cat (pystr_chr 92) ..`). `--fun lex` cannot even run: it emits `val _parser__parse_* .. variant {..}` (`unexpected 'variant' clause`), a pre-existing `--fun` defect for parser.py. | 4 links, the first in a mirrored file |
| normalize (5) | `normalize_whyml_axiom` / `normalize_prover_output`: REFUSED R325, and the failing site is the ALREADY-converted `_strip_all_parens` (`re_sub_3` opaque int): one `re.sub(pat, lambda m: .., out, count=1)` in the file turns the file's `re.sub` binding opaque. `_nat_to_int_with_sidecond` = `re.compile(..).sub(<nested def>)`, `_expand_anon_binders` = `pattern.sub(lambda, s, count=1)` in `while True`, `_alpha_rename` = `re.match` + `sorted(key=lambda)` + `re.escape` f-string pattern. NO stub needs only a literal pattern + string replacement. | no candidate in scope |
| `canonical.py::_alpha_rename` | writes `counter[0]` (mirror frame `assigns counter`) from inside a generator self-call; dict built by a store loop; `f"v{counter[0]}"`; recursion on `substitute`'s result | state threading through a term transform: new shape |
| `proof_axiom_allowlist.py::parse_rocq_assumptions_block` | L3-tc: `(int, array int)` vs `(int, int)`: the `tuple[bool, list[str]]` return annotation lowers to `(int, int)` (int-erasure of the PEP 585 element type) while `names: list[str]` lowers to `array int` | type lowering in mirrored types.py |
| `ir_schema.py::validate_ir` | REFUSED: optional TypedDict key `"name"` read | dict-shape model |
| `frontend/exec_splice.py::_ExecSplicer.visit_Expr` | REFUSED: reads the exception object bound by `except .. as exc` | exception payload model |
| `proof2why3/crosscheck.py::CrossCheckResult.diagnostic` | L3-tc `string` vs `int`: `for label, ok in self.pairwise.items()` (a property returning a dict literal) lowers to the 0-ary input-blind `self_pairwise_items_0 ()` with `label` / `ok` erased to `any int` | property-call + dict-items tuple loop (mirrored statements) |
| `frontend/import_classifier.py::_stub_set` | FOUR ORACLES GREEN (L3-tc ok, untrusted-emitted 907, yield OK, shadowed 14, vacuity no new erasure) but HOLLOW: the emission is `if not (path_isdir_op stub_dir) then any int else set_comp 0` (mirror return placeholder `-> int`; `set()` -> `any int`; the comprehension over `Path.iterdir()` -> the input-blind `set_comp 0`). REJECTED by rule 5 (non-vacuity); the vacuity oracle passes it because `stub_dir` is read by the `is_dir` test. A screen false-green worth a ratchet. | hollow |

## Residuals (honest)

1. **Contract-dropping beyond the term family is UN-PROBED.** `generic_fold.py` has 399
   fixed `ensures { true }` emission sites; only the 7 term recognizers are now gated. Any
   other recognizer that fires on a function with a non-trivial user contract would drop it
   the same way. Next step: one probe per recognizer family (a program of the recognized
   shape with `#@ ensures False`), then the same fail-closed gate.
2. L-T2 (`_expand_nat_to_int`) is BUILT (cv3) and `substitute` converted (lv2); the 5
   remaining canonical.py stubs each need their own shape (see the lv2 table above).
3. L-R5x stays un-built (0 yield); its chains stop at `re` (R5-lib) and a string-tuple list.
4. `pycsl.py --help` crashes (`ValueError: unsupported format character ' '` in an argparse
   help string) — noticed in passing, not fixed.
