# Run #9 u76 report: rt84 F1 repaired (faithful float-field PyVal carrier); route #634 closed (PYCSL-FUNCTION-FRAME)

Executor u76, driver run #9, soundness repair. Branch `run9-u76` in `/home/fabrice/git/pycsl-u76`. It is `run9-u74` (4214d8ceb) merged with `ghost-assign-bc6` = L21 (ba48d5888) in 435dc8f66. The merge was clean, and the census TSV needed no union.

- Base tree (detached at the merge base ba48d5888 = L21): `/home/fabrice/git/pycsl-u76b`.
- Head snapshot tree: `/home/fabrice/git/pycsl-u76h`.
- Paths are relative to `scratchpad/u76/` unless absolute. Never pushed.
- Every heavy job went through heavy.sh with `PYTHON_CPU_COUNT=2` and `TMPDIR=scratchpad/u76/tmp`.
- oom_kill was 15 before and after every job. No counted log contains EDQUOT, "Disk quota exceeded" or "No space left".

## Verdict

- **F1 (introduced by u74, false proof): REPAIRED, with a sound and faithful arm.** The u74 `_to_cache_payload` conversion still proves whole-file with the repaired arm:
  - audit_proof_reverify.py: 88 Valid / 0 non-Valid;
  - audit_proof.py: rc 0, "All contracts formally proven".
  - Both proved emissions are byte-identical to the head mirror sweep. No re-trust.
- **Route #634 (pre-existing cross-module false proof): CLOSED, fail-closed in both units.** The fix is a new refusal, `PYCSL-FUNCTION-FRAME`. It fires when a module-level, non-`\trusted` function declares `#@ assigns` but its body may write a parameter that the frame does not name.
  - The refusal is checked in the defining unit (the function's `let`).
  - It is also checked in every importer (the function's `val`). There, the imported body's frame is measured, not taken from the declaration.
- **The list twin was also a live false proof at L21:**
  - The helper declares `assigns \nothing` and writes `xs[0]` in a loop, and the importer claims `xs[0] == 0`.
  - At L21, BOTH modules PROVED it, while CPython prints 5 (`c/m634d.py`, `c/x634d.py`).
  - It is now refused too.
- **Movement vs L21** (head d5b3ab94e, measured once per tree, cwd = tree root, before any narrowing):
  - corpus root 3343 / 3356 (+13 new witnesses): **0 MOVED, 2 GONE** (`0337`, `9063_u30_r568_w04_any_receiver_pure_caller`), 0 APPEARED beyond the new files;
  - pyref 2185 / 2185, 0 / 0 / 0;
  - mirror 53 / 53, **2 MOVED** (`audit_proof_reverify`, `audit_proof`: the u74 pair, nothing new). Both moved files are proved (above).
  - The cost was this low, so no narrowing was needed.


Commits: f7df800a2 (both repairs, WIP), d5b3ab94e (witnesses, docs, P1 evidence), plus the census and report commits listed in §6.

## 1. F1: the float-field PyVal carrier (module6_whyml/expressions.py `_pyval_wrap`, arm "run #9 u74 (a)")

**Defect (rt84 F1).** u74 wrapped a `float` record-field read in hval position as `HInt (real_hcarrier_op x)`. The equality arms are NOT erasure-neutral:
- `hval_eq_float_lit` unfolds to `match v with HFloat f -> hreal_eq f c | _ -> false`;
- `hval_eq (HInt _) (HFloat c)` is `false` for a non-integral `c`.

So `{"a": r.x}` followed by `d.get("a") != 1.5` PROVED with r.x = 1.5.

**Repair (no `val`, no law, no axiom: the ledger stays 3).** The value is now the FAITHFUL tag of what the slot can hold:

```
(let _u76f = <x> in if any bool then HFloat _u76f
  else (match hreal_int_of _u76f with Some _u76i -> HInt _u76i | None -> HFloat _u76f end))
```

- A Python float is `HFloat x`.
- Only when `x` is integral may the value be a Python int, `HInt i` with `from_int i = x` (the numeric tower: a `float` annotation accepts an int).
- A claim is proved only if it holds on every branch, and each branch is the faithful model of a value the slot can hold. So every arm that decides a tag agrees with CPython on that value: `hval_eq`, the literal unfoldings, `hval_truthy`, isinstance, the `or` default, `hval_canon`, `hval_hashable`. All of these rely on the same FLOAT-FINITE assumption (route #606) as every `HFloat`.
- `isinstance(.., float)` stays undecided for an integral value (`HInt` is opaque), as it is for a float param. It is decided True for a non-integral value.
- `real_hcarrier_op` is gone. The arm is still program-context only: in a spec it falls through to the old `HInt <real>` and fails closed at Why3 type-check.

**Consumers checked** (full proofs at head; base = L21; CPython is the `__main__` print of each file in `c/`):

| probe | what | CPython | head | L21 |
|---|---|---|---|---|
| f1 / 10510 | `d.get("a") == 1.5`, claim 1 | 0 | NOT proved | L3-tc fail-closed |
| f2 / 10511 | `v = d["a"]; v != 0.5`, claim 1 | 0 | NOT proved | L3-tc |
| f3 | `isinstance(.., float)`, claim 0 | 1 | NOT proved | L3-tc |
| e1 / 10512 | `d["a"] == d["b"]` (b = 1.5 stored, `hval_eq`) | 0 | NOT proved | L3-tc |
| e2 / 10513 | `== 2.0` (integral literal) | 0 | NOT proved | — |
| e3 / 10514 | truthiness | 0 | NOT proved | L3-tc |
| e4 / 10515 | `isinstance(.., int)` | 0 | NOT proved | — |
| e7 | `== True` (r.x = 1.0) | 0 | NOT proved | — |
| e8 | `d["a"] != d["b"]` (b = 0.5) | 0 | NOT proved | — |
| e6 | `{"a": [r.x]}` (float inside a list) | 0 | L3-tc fail-closed (unchanged path) | — |
| e5 | `v is None` claim 1 (TRUE) | 1 | PROVED (correct) | — |
| p1 / 10516 | `requires r.x == 1.5`, `== 1.5`, claim 0 (TRUE) | 0 | **PROVED** | L3-tc |
| p2 / 10517 | `requires r.x == 0.5`, truthy (TRUE) | 0 | PROVED | — |
| p3 / 10518 | `requires r.x == 1.5`, `isinstance(.., float)` (TRUE) | 0 | PROVED | — |
| p4 / 10519 | `requires r.x == 2.0`, `== 2` (TRUE, numeric tower) | 0 | PROVED | — |

Logs are in `c/h/<n>.log` and `c/b/<n>.log` (verdicts via `v.sh`); witness logs are in `wit/pycsl-u76/`. Every false claim is unprovable, and every true one proves. The PASS controls show the carrier is precise, not just opaque. Other consumers:
- ordering goes through `hint_of`, which is `hval_opaque_int` on `HFloat`: undecided, so fail-safe;
- `str()` goes through `hstr_of` / `hval_opaque_str`: undecided;
- a dict KEY is never a wrapped value (keys are `string`).

**The u74 conversion still proves** (P1.sh, worktree at d5b3ab94e's src):
- `audit_proof_reverify.py` whole-file: rc 0, "All contracts formally proven", 88 Valid / 0 non-Valid (`pr/audit_proof_reverify.whole.log`). The emitted `elapsed_compile_s` entry is the new carrier (`pr/audit_proof_reverify.whole.mlw`).
- `audit_proof.py` whole-file: rc 0, "All contracts formally proven" (`pr/audit_proof.whole.log`).
- Both `.mlw` are byte-identical (`cmp`) to the head mirror-sweep emissions `sw/head1/mir/*.mlw`.
- oom_kill 15 / 15.

## 2. Route #634: the declared frame of a module function is now checked against its body

**Where the hole was.** `transpile` (Module6_WhyMLTranspiler.py) already computes each function's conservative parameter write set and its `undeclared` part (`_r316_frame`). There were two gaps:
- (a) `_emit_function_block` (functions.py) refused an undeclared write only for a METHOD (`PYCSL-METHOD-FRAME`, route #316). A plain function's `#@ assigns \nothing` was never compared with its body, and Why3 accepted the `let` because it infers the write.
- (b) An IMPORTED function is injected by ir_resolve as a `\trusted` stub. `transpile` then takes its frame AT ITS WORD (`_eff316 = declared`), so its `undeclared` was always empty. The importer emitted `val f (r: r) : int` with no `writes` and believed `assigns \nothing`.

Why does the in-module caller fail safe (fr2) while the importer does not? Why3 propagates an inferred `let` effect to in-module callers, but an imported `val` has only what the declaration says.

**Fix.**
- (a) `PYCSL-FUNCTION-FRAME` (functions.py, inline beside PYCSL-METHOD-FRAME) applies to a non-method that declares `#@ assigns` with a non-empty `undeclared`. It covers non-`\trusted` functions, and IMPORTED ones, meaning a name not in `own_names_r521`, the set of functions this file defined before import resolution. `imported_names_r521` was not usable: it missed `f` when `R` was imported alongside it (measured on x634, it held only `{'R'}`).
- (b) In `transpile`, for an imported module-level function that is trusted and declares `assigns`, `undeclared` is now measured on its BODY. That is its direct stores plus, over the settled fixpoint, the effect of every callee it forwards a parameter to (the same propagation code as the fixpoint, one pass). The effective frame (`written`, `positions`, used by call stubs and #317) is unchanged.
- No new key is added to the IR dict (no `repr`-hash movement).
- A user `\trusted` function in its own unit keeps its declared frame. A function with NO `assigns` keeps the inferred / #317 frame.
- Neither edited method has a verified mirror twin: `_emit_function_block` is absent from the mirror, and `transpile` is `\trusted`. So no §10.4 re-port is owed. `pycsl.py` and `ir_resolve.py` are untouched.

**Probes** (full proofs; CPython = `python3 -E -s` from `c/`):

| probe | shape | CPython | head | L21 |
|---|---|---|---|---|
| m634 (helper) | `assigns \nothing`, `r.b = 5` in a loop | — | REFUSED PYCSL-FUNCTION-FRAME | PROVED |
| x634 / 10520 | importer claims r.b == 0 | 5 | REFUSED PYCSL-FUNCTION-FRAME | **PROVED (false)** |
| fr2 / 10521 | same, one module | 5 | REFUSED | NOT proved (fail-safe) |
| fr | straight-line `r.b = 5` | 5 | REFUSED | L3-tc fail-closed |
| m634d (helper) | `assigns \nothing`, `xs[0] = 5` in a loop (list) | — | REFUSED | PROVED |
| x634d / 10522 | importer claims xs[0] == 0 | 5 | REFUSED | **PROVED (false; new finding)** |
| m634e / x634e | write through an alias `q = r; q.b = 5` | 5 | REFUSED / REFUSED | (L3-tc) / — |
| m634f / x634f | write through a callee `h(r)` | 5 | REFUSED / REFUSED PYCSL-VAL-ARG-UNFRAMED (h, no assigns) | — |
| m634b + x634p / 10523 | honest `assigns r.b`; caller claims r.a unchanged | 1 | PROVED (val has `writes { r.b }`) | PROVED |
| m634b + x634b / 10524 | honest `assigns r.b`; caller claims r.b == 0 | 5 | NOT proved | NOT proved |
| m634n + x634n / 10525 | `assigns \nothing`, read-only; caller claims r.b unchanged | 0 | PROVED | PROVED |

CPython is 5 in every false-claim row. That covers m634, x634, x634d, fr2, fr, x634e, x634f and x634b; `c/x634*.py`, `fr2.py` and `fr.py` print it. Logs are in `c/h/`, `c/b/`, `wit/`.

## 3. Movement vs L21 (sw1.sh: base sweep in pycsl-u76b at ba48d5888, head sweep in pycsl-u76h at d5b3ab94e, each with cwd = its tree root)

| plane | base | head | MOVED | GONE | APPEARED |
|---|---|---|---|---|---|
| corpus root (`sw/head1/C-root.txt`) | 3343 | 3356 | 0 | **2** | 0 (+15 new source files: 13 witnesses + helpers zu76b / zu76n) |
| pyref (`C-pyref.txt`) | 2185 | 2185 | 0 | 0 | 0 |
| mirror (`C-mir.txt`, `diffrq-mir.txt`) | 53 | 53 | **2** | 0 | 0 |

The emission counts and rc of both trees are in `logs/sw1.out`. oom_kill was 15 at the start and end.

- **GONE `9063_u30_r568_w04_any_receiver_pure_caller`** (expected FAIL, unchanged). `caller(c: Any, o: Any)` declares `assigns \nothing` and calls `c.m(..)`, which writes `self.flag`. That was VERIFY-FAIL and is now REFUSED by PYCSL-FUNCTION-FRAME at emission. Its census row was re-measured with the real `_census_row` (REFUSAL).
- **GONE `0337`** (no `pycsl-expected` line; it is a `--no-proof` parse-only fixture). `array_fill_zero(arr: list, n)` declares `#@ assigns \nothing` and writes `arr[i] = 0`. That declared frame is FALSE of the program (CPython mutates `arr`), so the refusal is correct: a true positive of the new rule, not an over-refusal. Its docstring already says the honest frame would be `assigns arr[0..n]`. **Not edited:** the driver decides whether the fixture gets the honest frame or an expected-FAIL marker.
- **MOVED `audit_proof_reverify`, `audit_proof`.** These are the u74 pair (vs L21; u74 itself moved them). The u76 carrier changes only `audit_proof_reverify.mlw`. Both whole-file proofs are owed and DONE (§1). The proved `.mlw` are byte-identical to `sw/head1/mir/`.
- Nothing else moved. The parameter-frame rule cost exactly one corpus file that was not a witness (0337, a dishonest frame). So no narrowing was done: it was measured before narrowing, as the brief asks.

## 4. Witnesses (corpus IDs 10510-10525; helpers in the corpus root `zu76a.py`, `zu76b.py`, `zu76d.py`, `zu76n.py`)

| id | expected | verdict at head | CPython |
|---|---|---|---|
| 10510-10515 | FAIL (F1: eq non-integral literal, `!=`, stored-float `hval_eq`, integral literal, truthiness, `isinstance(.., int)`) | VERIFY-FAIL (u74 head PROVED 10510/10511; L21 L3-tc) | 0 each (claims 1) |
| 10516-10519 | PASS (F1 controls: eq literal, truthy, isinstance float, `== 2` numeric tower) | PROVED | 0 (claims 0) |
| 10520 | FAIL (#634: imported `assigns \nothing`, record field write in a loop; helper zu76a) | REFUSED PYCSL-FUNCTION-FRAME (L21 PROVED) | 5 |
| 10521 | FAIL (#634 owner side, one module) | REFUSED PYCSL-FUNCTION-FRAME | 5 |
| 10522 | FAIL (#634 list twin, helper zu76d) | REFUSED PYCSL-FUNCTION-FRAME (L21 PROVED) | 5 |
| 10523 | PASS (honest `assigns r.b`, the other field preserved; helper zu76b) | PROVED | 1 |
| 10524 | FAIL (honest `assigns r.b`, claim on the written field) | VERIFY-FAIL | 5 |
| 10525 | PASS (read-only `assigns \nothing`; helper zu76n) | PROVED | 0 |

- Logs: P1 run `wit/pycsl-u76/`; re-run on the final snapshot bb2f6efe7 `wit/pycsl-u76h/` (`logs/G2/wit.txt`).
- Census rows come from the REAL `_census_row` (`cen_rows.py` imports `bin/check-refusal-witness-coverage.py`): `logs/CEN2.out` and `logs/G2/cen.txt`.
- The full `--append-new` was started first and killed. It had picked up 515 PRE-EXISTING uncensused expected-FAIL witnesses (a debt older than this branch, hours of proofs), and appended nothing.
- The vacuous `#@ requires True` lines were dropped from the new files (claim-vacuity ratchet 1131, fast plane red on G); that commit is bb2f6efe7.
- `ls test-suite/corpus/pycsl-reference | cut -d_ -f1 | sort | uniq -d` is empty for numeric ids.

## 5. Gates (final snapshot `pycsl-u76h` = bb2f6efe7; its src / bin / test-suite are identical to the branch head; later commits touch only scratchpad and this report)

| gate | result | log |
|---|---|---|
| byte-diff root vs L21 | 0 MOVED / 2 GONE (0337, 9063: both explained in §3) / 0 APPEARED (+15 new sources), rc 1 because the GONE are flagged | `sw/head1/C-root.txt` |
| byte-diff pyref vs L21 | rc 0, 2185 / 2185, 0 / 0 / 0 | `sw/head1/C-pyref.txt` |
| mirror vs L21 | 2 MOVED (audit_proof_reverify, audit_proof), both whole-file PROVED | `sw/head1/C-mir.txt`, `diffrq-mir.txt` |
| check-assigns-writes-survival (single-underscore emission, 53 files) | rc 0 (HOLE 0, TRAP 1398 ≤ 1399, TRAP-NMS 1501) | `logs/G/lg/check-assigns-writes-survival.txt` |
| check-trusted-frame-honesty | rc 0 (0/1, 0/63) | `logs/G/lg/check-trusted-frame-honesty.txt` |
| check-getattr-erasure | rc 0 | `logs/G/lg/check-getattr-erasure.txt` |
| check-assigns-underdeclaration | rc 0 (TRAP 3 / HOLE 0) | `logs/G/underdecl.txt` |
| fidelity: check-self-annotate-sync / self-annotate-mirror-check / doc-coherency / sibling-concrete / stdlib-contract | rc 0 / 0 / 0 / 0 / 0 | `logs/G/{sync,mircheck,doccoh,sibfid,stdfid}.txt` |
| run-soundness-planes.sh (fast + conversion tier), teed | **rc 0, 62 / 62 green** on bb2f6efe7 (G on 2c8ad9e43 was 61 / 62: claim-vacuity `requires True` 1141 > 1131, from the new files; fixed) | `logs/G2/planes.txt` (`logs/G/planes.txt`) |
| check-claim-vacuity (individually) | rc 0, 1791 / 8867 at the ceiling | `logs/G2/claim-vacuity.txt` |
| count-trusted-directives | rc 0; `\trusted` (canonical grep) **364** (u74's 365 → 364; u76 adds none) | `logs/G/count-trusted.txt`, `logs/G.out` |
| proof-axiom ledger | `proof_axiom_allowlist.py` diff vs L21: 0 lines (ledger 3) | `logs/G.out` |
| duplicate corpus ids | 0 | `logs/G.out` |
| whole-file proofs of moved mirror files | audit_proof_reverify 88 / 0 rc 0; audit_proof rc 0 | `pr/*.whole.log` |
| witness proofs on the final snapshot | 16 / 16 as expected | `logs/G2/wit.txt`, `wit/pycsl-u76h/` |

- The ledger slow planes, underdeclaration and fidelity ran on 2c8ad9e43. Its src is identical to bb2f6efe7 (only corpus text and the census changed after it), so the mirror emission they read is unchanged.
- oom_kill was 15 throughout. No log contains a quota string.
- The tooling rule (34) holds: `pycsl.py`, `bin/` proof tooling and the prover setup are unchanged by u76. The only `bin/` change is the census TSV.

**rt84 probe table, head vs L21, with CPython** (full proofs unless marked QUICK):

| probe | CPython | head (u76) | L21 |
|---|---|---|---|
| f1 / f2 / f3 | 0 / 0 / 1 | NOT proved ×3 | L3-tc fail-closed ×3 |
| k1 / k2 | 1 / 2 | L3-tc fail-closed | NOT proved |
| k3 | 1 | NOT proved | NOT proved |
| k4 (QUICK) | 1 | L3-tc fail-closed | type-checks |
| k5 (honest) | 0 | PROVED | — |
| k6 / k7 (QUICK) | 0 / 1 | L3-tc fail-closed | L3-tc fail-closed |
| k8 (honest) | 0 | NOT proved (incompleteness) | NOT proved |
| k9 (QUICK) | 1 | L3-tc fail-closed | type-checks |
| fr2 | 5 | REFUSED PYCSL-FUNCTION-FRAME | NOT proved |
| m634 / x634 | — / 5 | REFUSED / REFUSED | PROVED / **PROVED** |

Logs: `c/h/*.log`, `c/b/*.log`; `logs/CEN2.out` has the k-probe CPython lines.

## 6. Commits (branch run9-u76, never pushed)

- 435dc8f66 — merge of ghost-assign-bc6 (L21) into run9-u74
- f7df800a2 — F1 carrier, PYCSL-FUNCTION-FRAME (owner + importer)
- d5b3ab94e — witnesses 10510-10525 + helpers, docs rows (static-semantics reference, annotations.md §7.11), P1 evidence
- 2c8ad9e43 — census rows (real `_census_row`), sweep compares, report draft
- bb2f6efe7 — `requires True` dropped from the new files, census rows re-measured
- ba07502c9 — G gate logs
- this report commit

**Open for the driver:**
- (1) `0337` (see §3): give it the honest `assigns arr[0..n]` or an expected-FAIL marker. It is not edited here.
- (2) 515 pre-existing expected-FAIL witnesses have no census row (`--append-new` would run them all).
- (3) Not covered: a write to a MODULE GLOBAL from a plain function with `assigns \nothing` (`_r316.global`). Methods are refused for it (PYCSL-METHOD-GLOBAL-WRITE), but plain functions are not checked by this change. Route #634's scope is parameters. It was not measured here and is a candidate probe.
- (4) An imported user-`\trusted` function whose REAL body writes a parameter outside its declared frame is now refused in the importer. This is fail-closed; a stub body (`...` / `pass`) is unaffected.

Trees `/home/fabrice/git/pycsl-u76b` (L21) and `/home/fabrice/git/pycsl-u76h` (bb2f6efe7) are kept for re-proof.

