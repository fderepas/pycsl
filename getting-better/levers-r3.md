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

See the commit messages and §"Battery" below (filled in as each gate lands).
