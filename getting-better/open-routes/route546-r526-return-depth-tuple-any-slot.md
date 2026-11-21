# OPEN ROUTE #546 — ROUTE #526's RETURN-DEPTH RULE COLLAPSES A TUPLE's SLOTS TO ONE DEPTH: AN `Any` / `object` SLOT ANYWHERE IN A `Tuple[..]` RETURN ANNOTATION (`any_from` = 1) ADMITS A None RETURNED IN EVERY OTHER SLOT (`-> Tuple[Any, int]` RETURNING `(k, None)`), AND THE CALLER READS THAT SLOT AT ITS DECLARED int / str KIND WITH NO FENCE: `g(k)[1] + 1`, `len(t[1])`, `t[1] * 2`, `t[1] < 3`, `10 // (t[1] + 1)`, A RAN
**Status: REPAIRED (run #4, u21, 9107a22b2), was OPEN, Severity 1.** MECHANISM: Module 5 computes return / parameter None depths per node (post-order); a TOP-LEVEL `Tuple[..]` is the INTERSECTION of its slots and keeps per-slot depths (`r526_return_none_depths.slots`); Module 6 judges a returned tuple display slot by slot (an element that may be None, or a None-bound local, owes the ordinary obligation unless ITS slot admits None; a None literal an unprovable one). Witnesses 25/25 NOT PROVED on a PyCSL-R521 obligation (default; typed / store fail Why3 typing at base and HEAD); corpus 8620-8624 FAIL, controls 8640-8642 PASS. Residual (named, u21): a tuple nested in Optional / Union / a container keeps u18's union of slots -- **CLOSED run #5 by u27** (see "Residual closure" below). Repaired by executor u21 (run #4) in 9107a22b2 (+ its ledger / docs commit), off int28 5627aee66; no new def in a mirrored body, no axiom; annotations §7.546. Over-refusal: corpus byte-diff root 0 MOVED / 0 GONE / 0 APPEARED (24 new sources), pyref 0 / 0 / 0, mirror 53/53 0 / 0 / 0 (nothing owed); rt43 / rt44 37 honest controls emission-identical to int28.  Red-team round 52 (driver run #4, 2026-11-04, on 2ad6cfd15 = main with routes through #539 incl. #521-#526: 1914 probes g1300-g1341, 1836 CPython-breaching, 263 confirmed (probe, mode) pairs in 10 families; the import families F4 / F9 / F10 prove in typed / store too). Census `scratchpad/rt52/census.tsv`; family block from `scratchpad/rt52/FINDINGS.txt`.
Witnesses `witnesses-r546/` (25; dependency modules rt52dep*.py copied beside the probes that import them): `g1301_bb1201_tup_any_slot0.py`, `g1301_bb1202_tup_obj_slot0.py`, `g1306_bg1224_tup_any_int_add.py`, `g1306_bg1226_tup_any_int_len.py`, `g1306_bg1228_tup_obj_int.py`, `g1306_bg1229_tup_int_any.py`, `g1306_bg1232_tup_pyval_int.py`, `g1308_bi1200_a_mul.py`, `g1308_bi1201_a_lt.py`, `g1308_bi1206_a_unpack_add.py`, `g1308_bi1207_a_local_var.py`, `g1308_bi1208_a_str_len.py`, `g1308_bi1209_a_str_concat.py`, `g1308_bi1210_a_str_in.py`, `g1308_bi1219_a_via_get.py`, `g1308_bi1220_a_via_none_local.py`, `g1308_bi1221_a_via_ifexp.py`, `g1308_bi1227_a_tuple_obj_str.py`, `g1317_br1206_tup_branch.py`, `g1317_br1208_tup_none_default.py`, `g1317_br1209_tup_any_bool.py`, `g1317_br1211_tup_object_int.py`, `g1317_br1212_tup_any3.py`, `g1317_br1213_tup_pyval.py`, `g1317_br1214_tup_str_upper_eq.py`.

Driver repro on int28 (= main 9721f9b0a + u19 / u20's #540-#545, landing), 2026-11-04T01:00Z: 10 rt52 exemplars (bb1201 bb1242 bb1258 bc1332 bd1226 bd1246 be1237 bm1200 bt1200 bv1215) rc=0 Verification SUCCESS while CPython breaks the claim (scratchpad/rt52/driver-repro.txt) — so none of these is closed by the pending #540-#545 landing.

```
F1 ROUTE #526's RETURN-DEPTH RULE COLLAPSES A TUPLE's SLOTS TO ONE DEPTH: AN `Any` / `object` SLOT ANYWHERE IN A `Tuple[..]` RETURN ANNOTATION (`any_from` = 1) ADMITS A None RETURNED IN EVERY OTHER SLOT (`-> Tuple[Any, int]` RETURNING `(k, None)`), AND THE CALLER READS THAT SLOT AT ITS DECLARED int / str KIND WITH NO FENCE: `g(k)[1] + 1`, `len(t[1])`, `t[1] * 2`, `t[1] < 3`, `10 // (t[1] + 1)`, A RANGE BOUND, AN UNPACK, A METHOD'S / A NONE-LOCAL'S / A `.get`'s None (25)
  EXEMPLAR: g1301/bb1201_tup_any_slot0.py: `def g(k: int) -> Tuple[Any, int]: return (1, None)`; `#@ no_exception \all` `def f(k: int) -> int: t = g(k); return t[1] + 1`; g1306/bg1226_tup_any_int_len.py: `-> Tuple[Any, str]` returning `(1, None)`, `return len(t[1])`; g1306/bg1229_tup_int_any.py: `-> Tuple[int, Any]` returning `(None, 1)`, `return t[0] + 1`
  CPYTHON: bb1201: f(1) -> TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'; bg1226: f({}, 'a') -> TypeError: object of type 'NoneType' has no len(); bg1229: same as bb1201
  PYCSL CMD: cd /home/fabrice/git/pycsl-rt52 && PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH PYTHONHASHSEED=0 /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh .venv/bin/python3 src/pycsl/pycsl.py /home/fabrice/git/pycsl/scratchpad/rt52/g1301/bb1201_tup_any_slot0.py --import-path src/pycsl  ->  rc=0 'Verification SUCCESS'
  WHY: mlw/bg1224_tup_any_int_add.mlw: `let g (k: int) : (int, int) = (1, pycsl_none)` (no R521 obligation on the escape) and `let f .. = let t = ref (g 1) in ((let (_, _r1_) = !t in _r1_) + 1)` (no fence on the read). annotations.md §7.521 CLAIM GATE: `r526_return_none_depths` keeps ONE `admit` set / ONE `any_from` depth per annotation, so the `Any` in slot 0 admits depth 1 for slot 1 too; the caller's slot read is typed by the annotation's int slot and is never may-be-None. REPAIR: compute admit / any_from per tuple slot (per path), not per depth.
  PROBES: g1301/bb1201_tup_any_slot0.py g1301/bb1202_tup_obj_slot0.py g1306/bg1224_tup_any_int_add.py g1306/bg1226_tup_any_int_len.py g1306/bg1228_tup_obj_int.py g1306/bg1229_tup_int_any.py g1306/bg1232_tup_pyval_int.py g1308/bi1200_a_mul.py g1308/bi1201_a_lt.py g1308/bi1206_a_unpack_add.py g1308/bi1207_a_local_var.py g1308/bi1208_a_str_len.py g1308/bi1209_a_str_concat.py g1308/bi1210_a_str_in.py g1308/bi1219_a_via_get.py g1308/bi1220_a_via_none_local.py g1308/bi1221_a_via_ifexp.py g1308/bi1227_a_tuple_obj_str.py g1317/br1206_tup_branch.py g1317/br1208_tup_none_default.py g1317/br1209_tup_any_bool.py g1317/br1211_tup_object_int.py g1317/br1212_tup_any3.py g1317/br1213_tup_pyval.py g1317/br1214_tup_str_upper_eq.py
```

## Residual closure (run #5, executor u27, branch run5-u27 off run5-int34 06ad15036)

u21's walk intersected only a TOP-LEVEL `Tuple[..]`; one nested in `Optional` / `Union` / a container kept u18's union, so
`-> Optional[Tuple[Any, int]]` returning `(1, None)` was no escape and `t = g(k); if t is not None: x = t[1]; return x + 1`
PROVED `no_exception \all` (CPython TypeError). RULE (annotations §7.546 "Residual closed"): Module 5 intersects EVERY
fixed tuple node, keeps an Optional / Union root's slot-wise intersection of its one-length tuple arms in `slots`, a
container-of-tuple's element slots in `elt_slots`, and a parameter's union-rule `hold` (the caller-side taint, unchanged);
Module 6 judges a returned display slot by slot / element by element, and a container argument of a FILE function against
its parameter's depths (u21 let any parameter with a record, and every top-level Optional / Union parameter, take any
container). No new code (`PyCSL-R521`), no axiom, no new def in a mirrored body; edited methods' twins are `\trusted`
(`_build_function_ir`, `_stmts_to_whyml`, `_expr_to_whyml`; functions.py `_emit_function_block` has none) except the
live / mirror `_match_subject_union_info` source fix below.

Evidence (`scratchpad/u27/`): witnesses `wit2/` (23) + `wit3/` (8) + controls `ctl/` (10) + `ctl2/` (5), full proofs in
hoare / typed / store at base 06ad15036 and HEAD (`full1.tsv`, `full2.tsv`). 12 witnesses PROVED at base (default model:
r01 r02 r03 r07 r08 s01 s02 s03 s04 s06 s08 s10) -> 12/12 NOT PROVED at HEAD on the `PyCSL-R521` fence sub-goal; in typed /
store all fail Why3 typing (`variable int_mem / store does not occur`) at base AND HEAD (never proved). The other shapes
(parameters, containers of tuples, nested tuple, tuple local: 18) were Why3 typing errors at base; 16 now carry a new
fence (emission). Controls proving at base keep proving (c01 c05 c08 d01-d05: 8/8 default-model SUCCESS at HEAD, emission
byte-identical); container-of-tuple controls c06 / c07 / c09 / c10 are typing errors at base and HEAD, and emit byte-identically.
Corpus 8940-8951 FAIL, 8952-8959 PASS.

Over-refusal / inertness: corpus byte-diff root 0 MOVED / 0 GONE / 0 APPEARED (2899 / 2919 .mlw, 20 new sources),
pyref 0 / 0 / 0 (2185 / 2185); rt43 / rt44 149 honest controls: verdicts identical, 22 / 22 emissions byte-identical.
Mirror sweep 53 / 53: MOVED exactly `module6_whyml/stmt_control_flow.py` (one line, `_match_subject_union_info`;
`scratchpad/u27/mirror-diff.txt`). Without a source change the rule adds there one obligation its model cannot discharge
(`return var_name, vinfo` with `var_name = subj.get("name")` in the `str` slot of `-> Optional[Tuple[str, PyVal]]`); live
and mirror now read `subj.get("name") or ""` (a nameless subject has no symbol-table entry either way: same result), and
the obligation is gone. `why3 prove --type-only` of the moved .mlw rc 0; `--fun controlflowstmtmixin___match_subject_union_info`
104 / 104 sub-goals Valid at HEAD (104 / 104 at base). OWED (driver, batched): the §10.4 whole-file re-proof of the mirror
`module6_whyml/stmt_control_flow.py` (no other mirror file moves; statements / expressions / functions / Transpiler are
byte-identical and owe nothing).
Residuals (named, annotations §7.546): a tuple LOCAL / call argument or return is judged against the intersection; a tuple
nested in a tuple slot is that slot's intersection; tuple arms of different lengths / several container shapes keep no
slot shape; a `X | None` (BitOr) root annotation has no record (unchanged); u21's `r553_param_none_stores` lands a callee's
`xs[0] = (None, 1)` at depth 1, so its caller's argument is now owed at the call (sound over-refusal).
