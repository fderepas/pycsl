# Gate S spike: the frozen value type on two real mirror files (wall `dict-value-model-r4`)

*Executor sp4, driver run #7, step S of `getting-better/dict-value-model-r4-impl.md` (§1 F3 / F9, §2.1-§2.2,
§3 row S). Tree `/home/fabrice/git/pycsl-sp4`, branch `run7-sp4`, base `ca505a20c` (= main HEAD at brief time).
No `src/` edit. All proofs measured 2026-11-13 16:49Z-18:25Z, slice `oom_kill` 0 at the start and end of every
run (`scratchpad/sp4/out/battery.log`).*

## 0. Verdict

**Gate S: PASS on both files for the PRIMARY candidate** (frozen 9-constructor theory + hoisted loop length +
route (e2) `pairs_get`, the driver's log-848 primary). The CONTROL candidate (same, with the recursive
`pairs_get`) also passes on both files once measured in a simultaneous pair (see §2.1: a first, unpaired run of
it read +27.4 % on `types.py`; the paired re-run reads +0.2 %).

| file | candidate | C1 union Valid (patched / pristine) | C2 lost by both | C3 pipeline wall (AE first, Z3 on AE failures) | C4 new Z3 Timeouts on AE-unproved goals | verdict |
|---|---|---|---|---|---|---|
| `module6_whyml/types.py` | **primary (e2)** | 3691 / 3691 = **100 %** | **0** | 778.6 s vs 749.7 s = **+3.8 %** (vs the r2 pristine re-run 745.2 s: +4.5 %) | **0** | **PASS** |
| `module6_whyml/types.py` | control (recursive `pairs_get`), paired run r2 | 3692 / 3692 = 100 % | 0 | 747.0 s vs 745.3 s = +0.2 % | 0 | PASS |
| `module6_whyml/types.py` | control, first (unpaired) run | 3692 / 3692 = 100 % | 0 | 955.5 s vs 749.8 s = +27.4 % | 0 | (REFUTE on C3 — load artefact, §2.1) |
| `module6_whyml/functions.py` | **primary (e2)** | 1203 / 1203 = **100 %** | **0** | 127.1 s vs 126.3 s = **+0.6 %** | **0** | **PASS** |
| `module6_whyml/functions.py` | control | 1204 / 1204 = 100 % | 0 | 126.6 s vs 126.3 s = +0.2 % | 0 | PASS |

Goal counts differ by one between pristine and (e2) because (e2) deletes an obligation by design: the
`pairs_get'vc` "variant decrease" goal of the recursive definition no longer exists (pristine: Valid in 0.13 s /
0.03 s AE, 0.01 s Z3). It is listed as REMOVED-BY-DESIGN and excluded from C1-C3; no other goal is unmatched.

**Replicate (fr4 R6 / R8 on `frontend/monomorphize.py`): harness confirmed.** Pristine = fr4's / rp4's control
exactly (AE 235 / 237, Z3 231 / 237, `_collect_generic_decls` 20 / 20 in 0.99 s); hoisted rich = 235 / 237 AE,
`_collect_generic_decls` 20 / 20 in 0.53 s (R8c). fr4's own R6 recipe re-built (`--fr4-minimal`: new
constructors appended, only `hval_truthy` arms + absent defaults, no hoist) reproduces R6: **228 / 237, 7
`_collect_generic_decls` loop-variant Timeouts** (13 / 20). A finding beyond R8 (§3): my frozen-order,
full-arm candidate WITHOUT the hoist does **not** lose them (235 / 237, 20 / 20 in 1.01 s).

**F3 reopening rows at HEAD: 0 / 5 TC-OK** (unchanged from rp4; expected — the frozen theory is not in the
emitter yet). §4 gives each row's cv12 id, edit spec and what it still needs beyond the frozen theory: only
**398 (s362)** and **034 (s030)** are closed by items already in the plan (§2.2 + T + W-hash); **400 (s374)** needs a
non-theory capability (route #487, str-valued `or` as a value), **001 (s001)** is out of the frozen set (a
set-valued dict field, `HSet` excluded), **250 (s253)** needs `hval_truthy` at an IfExp test and a nested typed
map field. The plan's ">= 2 / 5" bar is reachable only with 398 and 034.

## 1. What was measured, and how

### 1.1 Base emissions (QUICK)

`scratchpad/sp4/emit.sh` (one `HEAVY_QUICK=1 heavy.sh` job), at `ca505a20c`:
`PYTHONHASHSEED=0 .venv/bin/python3 src/pycsl/pycsl.py --no-proof --keep-mlw --import-path src/pycsl <file>`
for `src/self-annotate/src/module6_whyml/types.py` (1672 lines), `.../functions.py` (2638 lines) and
`.../frontend/monomorphize.py` (973 lines, identical size to rp4's `mono.mlw`). All three rc 0, `L3-tc ✓`
(`scratchpad/sp4/em/*.emit.out`, `out/emit.log`).

### 1.2 The pipeline's per-prover call (read from `src/pycsl/pycsl.py` at HEAD)

`_run_proofs` builds `base_cmd = ["why3", "prove", "-a", "split_vc"]` (+ `-a induction_pr` only when the module
declares an `inductive`; none of these files does), `_dispatch_provers(base_cmd, provers, "30", ...)`, and
`_run_why3_prove` appends `-P <prover> --timelimit 30 --json` (`pycsl.py:38600`). Provers: `_DEFAULT_PROVERS =
["Alt-Ergo,2.6.3,", "Z3,4.13.3,"]` (`pycsl.py:38995`, = `config/agents-config.json`). No `-j` flag: why3.conf's
`running_provers_max = 2` applies. No `--steps`. Used verbatim by `scratchpad/sp4/prove.sh`:

    why3 prove -a split_vc -P "<Alt-Ergo,2.6.3,|Z3,4.13.3,>" --timelimit 30 --json <file.mlw>

each run its own `HEAVY_PRIO=1 heavy.sh` job, at most two of mine at a time (`pair.sh` chains). Note: the live
dispatcher runs the LAST-listed prover (Z3) first and Alt-Ergo on its residuals; the brief's pipeline wall is
AE first. Both orders are reported (§2); the verdict uses the brief's.

### 1.3 The patch (`scratchpad/sp4/gen.py`, reproducible: `gen.py IN OUT [--e2] [--no-hoist] [--fr4-order] [--fr4-minimal]`)

Rebuilt from response §3.5 / R6 / R8 (fr4's `mono_rich*.mlw` were never committed and the rp4 worktree is gone);
it prints a per-transform census and exits non-zero when an expected anchor is missing.

| transform | what | types | functions | mono |
|---|---|---|---|---|
| T1 | `type hval = HNone \| HBool bool \| HInt int \| HFloat real \| HStr string \| HTuple hval_list \| HArr hval_list \| HMap hpairs \| HNode hval` (impl §2.1 order) + `use real.Real as R` (qualified: an unqualified `real.Real` shadows int `+`/`-`/`=` and fails type-check) | 1 | 1 | 1 |
| T2 | `hval_truthy`: + `HNone -> false`, `HBool b -> b`, `HFloat f -> not (R.(=) f 0.0)`, `HTuple l -> l <> HNil` (all 9 tags) | 1 | 1 | 1 |
| T3 | `hint_of`: + `HBool b -> if b then 1 else 0` (numeric tower) | 1 | 1 | 1 |
| T4 | sequence views polymorphic over `HArr`/`HTuple`: `hval_len`, `hval_str_mem`, `hval_nth_str`, and the emitted `for`-iteration length / element matches | 3 | 3 | 3 + 9 |
| T5 | every absent default `(HInt pycsl_none)` -> `HNone` | 7 | 21 | 9 |
| T6 | the `d[k]` junk continuation `None -> (HInt 0)` -> `None -> (any hval)` (impl F6 (i)) | 0 | 2 | 2 |
| T7 | HOISTED iteration length: `let _n_<i> = <len> in while !<i> < _n_<i> ... variant { _n_<i> - !<i> }` for every loop whose length term matches over / views an hval and reads no mutable state | 0 (2 loops kept inline: the length is `hval_values_len self._record_types`, a mutable field, no `match`) | 1 | 3 |
| E2 | (primary only) `pairs_get` = `val function pairs_get (p: hpairs) (k: string) : option hval` + `axiom pairs_get_nil : forall k [pairs_get PNil k]. ...` + `axiom pairs_get_cons : forall k k' v t [pairs_get (PCons k' v t) k]. pairs_get (PCons k' v t) k = (if k = k' then Some v else pairs_get t k)` — fr4 R3b's equations and triggers; a `val function` (not R3b's logic-only `function`) because the emitted program code calls `pairs_get` | 1 | 1 | 1 |

No `or`-default `match v_or with ... | HNode _ -> v_or end` and no exhaustive `isinstance` table occurs in these
three files at HEAD (every other emitted match over `hval` has a `_` arm; Why3's exhaustiveness check would
reject a missed one). Type-check: `scratchpad/sp4/tc.sh` (`HEAVY_QUICK=1 heavy.sh`, `why3 prove --type-only`):
all patched files clean (only unused-variable warnings; `out/*.tc.out`, `out/tc.log`). Patched pair kept:
`scratchpad/sp4/spk/{types,functions}_{e2,rich}.mlw` (+ the monomorphize variants).

### 1.4 Analysis (`scratchpad/sp4/analyze.py`)

Goal identity across pristine and patched = (goal name, explanations, start line mapped patched -> pristine by
a line diff, occurrence rank); locations in other files (the stdlib `set.mlw` clone refinement) are not
shifted. Per-goal wall = prover time, `Timeout` counted at 30 s. Per-goal tables:
`scratchpad/sp4/out/{types_e2,types_rich,types_rich_r2,func_e2,func_rich,mono_rich}.goals.tsv` (pristine AE /
Z3 verdict + time, patched AE / Z3 verdict + time, one row per goal).

## 2. Tables

### 2.1 `module6_whyml/types.py` (3692 goals pristine)

| run | AE Valid | AE Valid-sum | AE all-goal sum | Z3 Valid | Z3 sum | union | pipeline AE->Z3 | pipeline Z3->AE (live order) | process wall AE / Z3 |
|---|---|---|---|---|---|---|---|---|---|
| pristine (r1, paired with e2) | 3669 | 288.6 s | 749.2 s | 3692 | 30.1 s | 3692 | 749.8 s | 30.1 s | 1062 s / 212 s |
| pristine (r2, paired with control r2) | 3669 | 287.9 s | 744.7 s | (r1) | | 3692 | 745.3 s | 30.1 s | 1042 s* / — |
| **primary e2** | 3668 / 3691 | 294.9 s | 778.1 s | 3691 / 3691 | 29.1 s | 3691 | **778.6 s** | 29.1 s | 1100 s / 217 s |
| control r1 (unpaired) | 3669 | 442.4 s | 954.8 s | 3692 | 43.2 s | 3692 | 955.5 s | 43.2 s | 1440 s / 331 s |
| control r2 (paired) | 3669 | 289.8 s | 746.3 s | (r1) | | 3692 | 747.0 s | 43.2 s | 1068 s / — |

(*from `battery.log`.) The 23 AE non-Valid goals are the SAME goals on every run (14 "High failure" Alt-Ergo
aborts — exit 2 / signal 6 — and 9 Timeouts, all in the IR preamble: `wf_ir_binds`, `size`, `size_*_dec`,
`irlen`); Z3 proves every one of them in every variant, so C2 / C4 hold with margin. **The control r1 read is
a load artefact:** its median per-goal AE time ratio vs pristine is 1.43 over *all* both-Valid goals
(uniform, i.e. host load — it ran while my other chain was queued and other executors' jobs held both other
slots), and the paired re-run r2 (pristine and control started 82 s apart, 1042 s / 1068 s) gives +0.2 %. The
one function with a genuine widening cost on this file is the hval function
`typeinferencemixin___field_type_of` (+81 s in r1, +2.9 s under e2; see the tsv). e2 median ratio vs r1
pristine: 1.01.

### 2.2 `module6_whyml/functions.py` (1204 goals pristine)

| run | AE Valid | AE Valid-sum | AE all-goal sum | Z3 Valid | Z3 sum | union | pipeline AE->Z3 | pipeline Z3->AE | process wall AE / Z3 |
|---|---|---|---|---|---|---|---|---|---|
| pristine | 1201 | 36.0 s | 126.0 s | 1203 | 37.9 s | 1204 | 126.3 s | 38.0 s | 161 s / 69 s |
| **primary e2** | 1200 / 1203 | 36.8 s | 126.8 s | 1201 / 1203 | 67.8 s | 1203 | **127.1 s** | 67.9 s | 163 s / 100 s |
| control | 1201 | 36.3 s | 126.3 s | 1203 | 37.8 s | 1204 | 126.6 s | 37.9 s | 162 s / 69 s |

The 3 AE non-Valid goals are the same 3 Timeouts in all three runs, each proved by Z3. One Z3 change under e2:
`functionemissionmixin___build_method_writes_map__Lassigns'vc` (postcondition, pristine line 1864) goes
Valid -> Timeout under Z3; Alt-Ergo proves it in 0.02 s, so it costs nothing AE-first and it is not a C4 goal
(+30 s in the live Z3-first order: 38.0 s -> 67.9 s). (The "whole-file ~1.6 h" figure for this file is the
full `pycsl.py` run with the vacuity probes; the per-prover proof calls themselves take < 3 min.)

### 2.3 Replicate: `frontend/monomorphize.py` (237 goals)

| variant | AE Valid | AE Valid-sum | `_collect_generic_decls` AE | Z3 Valid | union | pipeline AE->Z3 |
|---|---|---|---|---|---|---|
| pristine (fr4 / rp4 control: AE 235, Z3 231, 20 / 20 in 1.32 s) | 235 | 18.9 s | 20 / 20, 0.99 s | 231 | 237 | 75.7 s |
| frozen theory + hoist (= fr4 `mono_rich_hoist`, R8c: 235, 20 / 20 in 0.71 s) | 235 | 12.0 s | 20 / 20, 0.53 s | 235 | 237 | 61.3 s (-18.9 %) |
| frozen theory, NO hoist (my order, all arms) | 235 | 12.5 s | 20 / 20, 1.01 s | — | — | — |
| fr4 R6 recipe re-built (`--fr4-minimal`: appended order, truthy + defaults only, no hoist) (R6: 228, 13 / 20) | **228** | 16.5 s | **13 / 20** (7 loop-variant Timeouts, 215 s) | — | — | — |
| fr4 order, all arms, NO hoist (`--no-hoist --fr4-order`) | NOT RUN: queued 20 min behind other executors, killed so my PRIO wait stopped holding off their jobs; open | | | | | |

Pristine Z3 also has fr4's 6 Timeouts (all `pyval` / `wf_ir`, AE proves them); the widened file proves 4 of
them under Z3 as well (`wf_ir_deep_shallow`, `_subst_type_in_ir`, 2 x `_subst_type_in_ir__dict`).

## 3. Reading

- The widening is free on both real files under the primary template: +3.8 % / +0.6 % pipeline wall, no
  goal lost, no new Z3 timeout where Alt-Ergo fails. Route (e2) does not cost Alt-Ergo anything on these files
  and removes one obligation.
- R6's loss is **not** intrinsic to width: rebuilt exactly as fr4 described it, it reproduces (7 lost
  variant goals); with the frozen constructor order and the full arm set it does not occur even without the
  hoist. The hoist stays in the template (it is sound, cheap and removes the risk); the order sensitivity means
  the emitter must emit the frozen order, and that a later constructor addition at the end of the type can
  re-trigger R6 — a reason to keep the hoist mandatory. Which of the two differences (constructor order or the
  extra `HTuple` / `HBool` arms) is the trigger is left open (the `--no-hoist --fr4-order` row of §2.3 was not run; file `spk/monomorphize_rich_nohoist_fr4order.mlw` is generated and type-checks).
- No narrower template is needed (nothing refuted), so none was measured.

## 4. F3 pre-check: the five reopening rows at HEAD

Runner: `scratchpad/sp4/reopen/` — `setup.sh` builds a FRESH tree (`git archive ca505a20c src bin json config`)
and a pristine copy; `probe.sh <variant> <rel> <Qual.fn>` restores the file, ports the live body verbatim with
`bin/port-one-mirror-body.py --convert` (falls back to `--replace` only for a non-facade), applies the
annotation-only edit of `edits.py`, emits `--no-proof --keep-mlw` (type-check on), restores the file and
checks the restore with `cmp`; `drain.sh` runs `queue.tsv` (12 variants) as one QUICK `heavy.sh` job each.
Fixes vs `scratchpad/wall-dict/spike/run.sh`: all five F3 rows (it had 282 instead of 001 / 250), ports at
HEAD instead of reading stale pre-ported files, fresh tree from git, checked restore. All 12 ported (marker
deleted) and restored OK. Results `reopen/out/summary.txt` (first Why3 error / refusal per variant, by
`clash.py`) and `reopen/out/<v>.out` / `<v>.mlw`.

| cv4 row | cv12 id | stub | edit spec | result at HEAD | still needs, beyond the frozen theory |
|---|---|---|---|---|---|
| 398 | **s362** | `pycsl._record_key` | `3980` none; `398a` `rec: Dict[str, PyVal]`; `398b` + return `Tuple[Tuple[PyVal x5], PyVal, Tuple[PyVal, ...]]` | 3980 L3-TC `:1396` `(Array.make 0 0)`; 398a L3-TC `:1392` hval `or`-default passed to `tuple_1 (x0: int)`; 398b REFUSED route #349 in caller `_merge_records_best_of_n` (`best[key]` hashes a possibly-unhashable key) | T: `Tuple[PyVal, ...]` codomain = `HTuple` and the hval-polymorphic `tuple` (impl §2.2/§3 T); route #521's "container may hold None" return assert must accept a PyVal slot; **W-hash** (Q1) for the caller. All inside the plan |
| 400 | **s374** | `pycsl._synthesize_block` | `4000` none; `400a` `rec: Dict[str, PyVal]` | both REFUSED route #487 (`", ".join(...) or "goal"`, `pr.get("answer", "") or ""`: a str-valued `or` used as a value) | a **str-valued `or`-as-value** lowering (#487 capability, cv12 `cap-boolop-value`), plus `cap-fstring-float-format` (`f"{t:.2f}"`); then hval `join`. Not delivered by the theory |
| 034 | **s030** | `core_ir_semantic._namedtuple_check_call` | `0340` none; `034a` `call, nt_arities: Dict[str, PyVal]` | 0340 L3-TC `:2322` `nt_arities` (map int vs int); 034a L3-TC `:2318` `callee` (hval) as a `map string` key | **narrowing substitution** after `isinstance(callee, str)` (`hstr_of` at the key position, impl §2.2), then the `nt_arities[callee]` 3-tuple unpack over an `HTuple` value (`len`, `nth`) and the KeyError presence assert. All inside the plan |
| 001 | **s001** | `Module6_WhyMLTranspiler._build_callee_no_exception_summary` | `0010` none; `001a` `functions: List[Dict[str, PyVal]]` | both REFUSED route #325 (`self._module_func_no_exception[name] = set(...)`: a set-valued dict FIELD is an opaque int) | a typed `Dict[str, Set[str]]` field model (cv12 `cap-R325-nonint-dict-value-field`) — `HSet` is excluded from the frozen set (impl §2.1) and the store is a field root (refused by §2.4). **Not reachable in this track** |
| 250 | **s253** | `ExpressionEmissionMixin._handle_sum_call` | `2500` none; `250a` `expr: Dict[str, PyVal]`; `250b` + `known_elems / known_sizes: Dict[str, PyVal]` locals | 2500 L3-TC `:3326` `!vname` (string) as an int key; 250a / 250b L3-TC `:3317` / `:3315` `expr.get("args")` (hval) as an IfExp **test** lowered as a string truth test | T: `hval_truthy` at every IfExp / `if` test (impl §2.2); then `subscript_get` on hval (`expr.get("args", [{}])[0]`), `str(elems[i]).lstrip("-").isdigit()` / `int(...)` over hval (cv12 `cap-R325-call-str-to-number`), and the `getattr(self, "_known_collection_elements", {})` nested typed-map field. Partly outside the plan |

Pre-check reading: the F3 bar (>= 2 / 5) can only be met by **398 + 034**; 400 needs #487, 001 is out of the
frozen set, 250 needs str->number and a getattr-field model.

## 5. Commands and files (all under `/home/fabrice/git/pycsl-sp4/scratchpad/sp4/`)

- `emit.sh` (QUICK) -> `em/{types,functions,monomorphize}.mlw` (+ `.emit.out`), log `out/emit.log`.
- `gen.py` -> `spk/*.mlw`: `gen.py em/X.mlw spk/X_rich.mlw` (control), `--e2` (primary),
  `--no-hoist`, `--fr4-order`, `--fr4-minimal` (monomorphize variants).
- `tc.sh` (QUICK, `--type-only`) -> `out/*.tc.out`, `out/tc.log`.
- `prove.sh <tag> <file> <prover>` (the pipeline call, §1.2) chained by `pair.sh` under `HEAVY_PRIO=1 heavy.sh`
  -> `out/<tag>.json` (raw per-goal why3 JSON), `out/<tag>.err`, `out/battery.log` (start / end, wall,
  oom_kill before -> after: 0 -> 0 on every run).
- `analyze.py <name> <pristine.mlw> <patched.mlw> <pri.ae> <pri.z3> <pat.ae> <pat.z3> [--removed g] [--tsv t]`
  -> the tables above and `out/*.goals.tsv`. Exact invocations:
  - `analyze.py types-e2 em/types.mlw spk/types_e2.mlw out/types_pri.ae.json out/types_pri.z3.json out/types_e2.ae.json out/types_e2.z3.json --removed "pairs_get'vc"`
  - `analyze.py types-control-r2 em/types.mlw spk/types_rich.mlw out/types_pri.ae.r2.json out/types_pri.z3.json out/types_rich.ae.r2.json out/types_rich.z3.json`
  - `analyze.py functions-e2 em/functions.mlw spk/functions_e2.mlw out/func_pri.ae.json out/func_pri.z3.json out/func_e2.ae.json out/func_e2.z3.json --removed "pairs_get'vc"`
  - `analyze.py functions-control em/functions.mlw spk/functions_rich.mlw out/func_pri.ae.json out/func_pri.z3.json out/func_rich.ae.json out/func_rich.z3.json`
  - `analyze.py mono-rich-hoist em/monomorphize.mlw spk/monomorphize_rich.mlw out/mono_pri.ae.json out/mono_pri.z3.json out/mono_rich.ae.json out/mono_rich.z3.json`
  - verdict printouts: `out/verdicts.txt`.
- `reopen/` (F3): `setup.sh`, `probe.sh`, `edits.py`, `queue.tsv`, `drain.sh`, `clash.py`, `out/summary.txt`,
  `out/<v>.out`.
- Committed: the scripts, `em/*.emit.out`, the patched pair `spk/{types,functions}_e2.mlw` and
  `spk/{types,functions}_rich.mlw`, `out/*.goals.tsv`, `out/battery.log`, `out/verdicts.txt`, the reopening
  outputs. Not committed (bulk, regenerable): `em/*.mlw`, the monomorphize `.mlw` variants, raw `out/*.json`.
