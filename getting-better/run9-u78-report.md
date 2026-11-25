# Run #9 u78 report: rt88 K1 repaired (no receiver-class narrowing when an override of `m` exists); rt88 f19 repaired (no narrowing for a defaulted or keyword-only parameter)

Executor u78, driver run #9, short soundness repair (defensive). Branch `run9-u78` in `/home/fabrice/git/pycsl-u78`, created from `run9-u77` (d1ad1764f). Never pushed.

- Base tree: `/home/fabrice/git/pycsl-u78b`, detached at run9-u77.
- Paths are relative to `scratchpad/u78/` unless absolute.
- Every heavy job went through heavy.sh, with `HEAVY_PRIO=1` (granted) or `HEAVY_QUICK=1` (the `--no-proof` batch), `PYTHON_CPU_COUNT=2` and `TMPDIR=scratchpad/u78/tmp`.
- oom_kill was 15 before and after every job.
- No log contains EDQUOT, "Disk quota exceeded" or "No space left". No classifier stop occurred.

## Verdict

- **K1 (latent defect, u77 dead code): REPAIRED.**
  - Cause: `frontend/ir_resolve.py::apply_inheritance` clears `td["bases"]` on every merged class. So u77's `_bs77` family was always `{C}`, and descendants were never included.
  - Fix: a dotted call `x.m(..)` is NOT narrowed when the resolved IR records ANY override pair (`ir["overrides"]`) whose sub method or base method is named `m`. The any-class union (the run9-u76 rule) then applies to that edge.
  - `ir["overrides"]` holds three kinds of pair: `merge_one`'s pairs; route #278's MRO pairs (grandchildren, fieldless intermediates, class-body bindings); and the pairs of classes from merged modules. Route #580 already reads the same source.
  - This was the simplest sound option. It computes no family: it turns the narrowing off for any method name that is overridden.
  - Cost: it can over-refuse only when an unrelated class pair overrides a method of the same name. That is the pre-u77 behaviour.
- **f19 (acceptance INTRODUCED by u77): REPAIRED.**
  - A parameter is narrowed only when it has no default (`param_defaults`) and is not keyword-only (`kwonly_params`).
  - Keyword-only parameters are excluded outright, because a non-literal keyword-only default is not even recorded in `param_defaults`.
- **Files not touched:** `pycsl.py` and `ir_resolve.py`.
- **Where the edit is:** inline in `Module6_WhyMLTranspiler.transpile` (the route #316 block). The mirror twin of `transpile` is `\trusted` (`src/self-annotate/src/Module6_WhyMLTranspiler.py:481`), so no §10.4 re-port is owed.
- **Docs:** `docs/pycsl-static-semantics-reference.md` §frame rules. The u77 paragraph, which claimed descendants were included, is corrected.
- **Movement vs run9-u77: NOT MEASURED** (time box; see §3). The driver should run it.

## 1. The fix (src/pycsl/Module6_WhyMLTranspiler.py)

```python
for _p316 in _pp316:
    if (_ann316.get(_p316) in _rec316
            and _p316 not in (_f316.get("param_defaults") or {})
            and _p316 not in (_f316.get("kwonly_params") or [])):
        _rc77[_p316] = _ann316[_p316]
...
_C77 = _rc77.get(_h77) if _h77 else None
if isinstance(_C77, str) and any(
        isinstance(_o78, dict) and (
            str(_o78.get("sub_method", "")).endswith("__" + _tail316)
            or str(_o78.get("base_method", "")).endswith("__" + _tail316))
        for _o78 in (self.ir.get("overrides") or [])):
    _C77 = None
```

- `_C77 = None` sends the edge down u77's existing "not narrowed" arm (`_npx316.append(None)`). For that edge, `_effn316` and `_bodyw634` then use every method with the same name.
- `_effn316` stays a subset of `_eff316` (rt88 (c)), and is now a larger subset than at u77.
- `_eff316` is not touched, nor is any emitted `writes` or `_r316_frame` positions / global. The change can therefore only move the PYCSL-FUNCTION-FRAME accept / refuse decision, and only toward refusal.

## 2. rt88 probes and witnesses

QUICK `--no-proof` runs, cwd = tree root: `q.sh`, `q.out`.
- Head logs: `q/h/*.log`, at 825d97dea (src identical to the final commit).
- Base logs: `q/b/*.log`, at run9-u77.
- CPython output: `cpython.txt`.

| probe / witness | shape | CPython | head u78 | run9-u77 |
|---|---|---|---|---|
| rt88 f23 / **10540** | same module: R.total pure, D(R).total writes self, `f(r: R)` `assigns \nothing`, g passes D(0) | `g() = 5`, claim 0 | **REFUSED PYCSL-FUNCTION-FRAME (`r`)** | L3-tc fail (type d vs r) |
| rt88 f23x owner / **10541** | f23 without g (the owner) | `d.a after f(D(0)) = 5` | **REFUSED PYCSL-FUNCTION-FRAME (`r`)** | accepted (q rc 0) |
| **10542** + helper `zu78a.py` | R and D(R) in the MERGED helper module, f in the witness | `5` | **REFUSED PYCSL-FUNCTION-FRAME (`r`)** | accepted |
| rt88 f19 / **10543** | `f(t: T, r: R = S(0))`, S.total writes t.v | `f(T(0)) = 0, t.v = 1` | **REFUSED PYCSL-FUNCTION-FRAME (`t`)** | accepted |
| **10544** | grandchild: D(R) defines no total, E(D).total writes self (route #278 MRO pair) | `5` | **REFUSED PYCSL-FUNCTION-FRAME (`r`)** | accepted |
| **10545** | keyword-only `f(t: T, *, r: R = S(0))` | `t.v = 1` | **REFUSED PYCSL-FUNCTION-FRAME (`t`)** | accepted |

- The rt88 probe sources themselves (`o88f23`, `o88f23x`, `o88f19`) are in `q/h` and `q/b`, with the same verdicts as their witnesses.
- run9-u76 refused the same three probes with the same PYCSL-FUNCTION-FRAME message (`r`, `r`, `t`); see the rt88 table and `/home/fabrice/git/pycsl/scratchpad/rt88/c/b/`. Head now matches run9-u76.

**Full proofs on the head.** `wit.sh`, logs `wit/*.log`, run at 0f59d7c24 (src identical to the final commit):

| id | expected | head |
|---|---|---|
| 10532 (u77 control) | PASS | rc 0, All contracts formally proven |
| 10535 (u77 control, local constructor) | PASS | rc 0, All contracts formally proven |
| 10537 (+ zu77a, u77 importer control) | PASS | rc 0, All contracts formally proven |
| 10540 to 10545 | FAIL | rc 1, PYCSL-FUNCTION-FRAME (each) |

- **Census rows:** made with the REAL `_census_row` of `bin/check-refusal-witness-coverage.py` (`cen_rows.py`, `logs/CEN.out`). Six REFUSAL rows were appended to `bin/refusal-witness-census.tsv`.
- **Corpus ids:** 10540 to 10545 plus the helper `zu78a.py`, all inside [10540, 10549]. Duplicate numeric ids: 0.

## 3. Movement vs run9-u77: NOT MEASURED (time box)

**What happened.**
- `sw.sh` sweeps a base tree (pycsl-u78b) and then a head tree (pycsl-u78), each with cwd = its tree root.
- It waited 55 min in the heavy queue. Both slots were held by another executor's `--slow` planes run and by the driver's v85 sweeps.
- It started at 12:16Z. The witness proofs and census ran first.
- At 12:31Z the base corpus sweep was at file 1551 / 6419, about 100 files a minute under load.
- At that rate, base + head (root, pyref and mirror) would have ended after the 14:30Z hard box, with no time left for the gates.
- I killed my own job (pgid 234699) after checking the parent chain: heavy.sh 234699 -> sw.sh 432306 -> byte-diff-sweep 434221. I ran the gates instead.
- The partial `sw/base/` output is VOID and is not used. Liveness is in `/home/fabrice/git/pycsl-u78/progress.txt`.

**What the code bounds (no measurement).**
- The change can only turn an accept into a PYCSL-FUNCTION-FRAME refusal. It cannot change emitted text: `_eff316`, the emitted `writes` and the positions / global of `_r316_frame` are untouched, and `undeclared` only feeds the refusal.
- So any movement could only be GONE. That means root / pyref files that relied on u77's narrowing for a method name that has an override somewhere, or for a defaulted or keyword-only record parameter.
- Mirror: all 53 mirror files still emit at head (`logs/G/lg/mir_emit`, 53 .mlw), so no mirror file is GONE.
- MOVED / APPEARED cannot happen by construction, but byte equality with a base emission was NOT measured.
- **The driver must run the root / pyref / mirror byte-diff vs run9-u77 before integrating.** The command is `scratchpad/u78/sw.sh`, without the witness and gate lines.

## 4. Gates

Run on pycsl-u78 at 3c22cc453, which has the final src / bin / test-suite / docs; this report commit adds only the report and logs. Script `G.sh`, summary `G.out`, logs `logs/G/`. Started 12:41:47Z, ended 14:11:05Z. oom_kill 15 -> 15.

| gate | result | log |
|---|---|---|
| fast planes (`run-soundness-planes.sh`, teed, ALL 62 in one run) | rc 0; **62 / 62 ok** | `logs/G/planes.txt` |
| check-assigns-writes-survival (single-underscore emission dir, 53 files) | rc 0 (HOLE 0, HOLE-NOWRITES 8, TRAP 1398 <= 1399, TRAP-NMS 1501) | `logs/G/lg/check-assigns-writes-survival.txt` |
| check-trusted-frame-honesty | rc 0 (0/1, 0/63) | `logs/G/lg/check-trusted-frame-honesty.txt` |
| check-getattr-erasure | rc 0 (DECLARED 0) | `logs/G/lg/check-getattr-erasure.txt` |
| check-assigns-underdeclaration | rc 0 (TRAP 3, HOLE 0) | `logs/G/underdecl.txt` |
| fidelity: check-self-annotate-sync / self-annotate-mirror-check / doc-coherency | rc 0 / 0 / 0 | `logs/G/{sync,mircheck,doccoh}.txt` |
| count-trusted-directives | rc 0; `\trusted` (canonical grep) **364** | `logs/G/count-trusted.txt`, `G.out` |
| proof-axiom ledger | `proof_axiom_allowlist.py` diff vs run9-u77: 0 lines (ledger 3) | `G.out` |
| duplicate numeric corpus ids | 0 | `G.out` |

- Rule 34: `pycsl.py`, `bin/` tooling and the prover setup are unchanged.
- Mirror emissions were not byte-compared (see §3). The emitter edit is in a `\trusted` twin, and no mirror proof is claimed.

## 5. Commits (branch run9-u78, never pushed)

- 825d97dea: the fix (Module6_WhyMLTranspiler.py), witnesses 10540 to 10545 + zu78a, QUICK probes (`q.sh`, `q/`, `cpython.txt`)
- 0f59d7c24: docs row (static-semantics reference, frame rules)
- 3c22cc453: census rows for 10540 to 10545, witness / control proof logs, sweep / gate scripts
- this commit: the report and the gate logs

**Not addressed:** the pre-existing gap where a descendant is defined only in a module that the owner does not import. The owner cannot see that class at all. That was already the case at run9-u76 (rt88 f8 / f22: OVERRIDE-FRAME and L3-tc keep it fail-closed). The fix covers every class in the merged IR.
