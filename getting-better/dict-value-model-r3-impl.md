# Implementation plan: route R-gate (claim-gated `#UND` hashing refusal) and the conversion boundary

*Driver run #3, wall cycle #2, steps 5-7 (`config/skills/self-tcb-reduction-driver/SKILL.md` §4, Gates
P / S / B / C). Executor `rg`, worktree `/home/fabrice/git/pycsl-rg`, base `289fe6029`. Inputs:
`getting-better/dict-value-model-r3.md` (the report) and `getting-better/dict-value-model-r3-response.md`
(the independent review). Corpus IDs reserved for this plan: 6400-6449. Time box 2026-10-28T12:00Z.*

---

## 0. What this plan decides, and how it can be refuted

The review recommends **route R-gate**. An underivable (`#UND`) value in a hashing position is refused when
the enclosing function claims `#@ no_exception` covering TypeError. Functions without such a claim keep the
exception ambient. The review leaves one question open (§5.4): is "ambient" honest? Put another way, does
an un-claimed function's `ensures` hold whenever it returns normally?

R-gate rests on three premises. Each one is falsifiable, and the plan tests them **before any edit to
`src/`**:

| premise | why R-gate needs it | falsifier (spike leg) |
|---|---|---|
| **P1 (LINK-3).** In an un-claimed function, an ambient implicit exception only ends the function **abnormally**. It never produces a normal return whose state contradicts a proved `ensures`, in that function or in any caller. | Without P1, admitting `#UND` in un-claimed code is still a false proof of an `ensures`. "Ambient" would be a relabelling, not a soundness argument. | S0 |
| **P2 (cost).** Refusing `#UND` only under a claim refuses no PASS file: no root or pyref PASS file, no mirror, no `pycsl_lib` module (or a precisely narrowed set). | A refused mirror loses a proved file. A refused PASS corpus file is a regression. | S1 |
| **P3 (witness).** The open `#UND` probes PROVE at base. If they already fail, there is nothing to repair. | Repair discipline (brief rule 7): witness PROVED at base, REFUSED on the candidate. | S2 |

**Refutation exit (Gate P).** If S0 refutes P1, R-gate is **unsound as a closure of the family**. The route
is then recorded as CERTIFIED-BOUNDARY with its reopening test, and nothing is built: no `src/` edit, no
corpus file, and no census row. The task's decision rule says so explicitly. If S1 refutes P2, the cost
is narrowed precisely (file, function, site). If the narrowed cost includes a PASS mirror or PASS corpus
file that cannot be justified, the result is again CERTIFIED-BOUNDARY, with the measured cost as the
reopening census. The build (§4) starts only if S0 and S1 pass and S2 confirms.

---

## 1. Conversions: a `Dict[str, Any]` value model is CERTIFIED-BOUNDARY

The report and the review agree, and this plan adopts their verdict without building anything.

- **Reason (measured).** A `Dict[str, Any]` read is the *first* blocker for only 19 of the 370
  refused or type-clashing stubs (report §4.1-§4.2). The annotation-only route-(a) spike gets 0 of 4
  stubs to TC-OK. In every case the chain advances one link, to an hval *consumer* (report §4.5). For the
  best leaf (398 `_record_key`), the review hand-wrote the full chain (`rk_hval_chain.mlw`, S1 /
  S1-z3). That chain needs two emitter capabilities for one stub:
  - a `Tuple[PyVal, …]` return codomain;
  - an hval-polymorphic `tuple`.

  It proves under Alt-Ergo, but Z3 times out on the witness. That is the `pairs_get` E-matching cost,
  and each step costs a 1-3 h whole-file re-proof of a big mirror. No value model is the object; the
  levers ledger ("no lever unlocks more than one stub") stands.
- **Reopening test (the review's §4).** Reopen when the emitter gains, for another reason, both a
  `Tuple[PyVal, …]` return codomain and one hval-polymorphic builtin. Then re-run
  `scratchpad/wall-dict/spike/run.sh` on rows 398, 400, 034, 001 and 250 (the small leaves of report
  §4.3). The wall reopens if at least two of the five reach TC-OK.

---

## 2. Route R-gate: the rule under test

The rule sits in the per-function hashing pass of `src/pycsl/pycsl.py` (the #349-#383 walk; the refusal
is raised after the `_hc349 & _u365` intersection, around line 8677). It adds a **second polarity**:
- **Positive deny-list.** Unchanged and unconditional (a list / dict / set, an unhashable record, an
  unverified `__hash__` / `__eq__`).
- **New refusal.** A hashed leaf whose derived class set contains `#UND`, or is empty (no source), is
  REFUSED iff the **innermost enclosing function** claims exception-freedom over TypeError:
  - `no_exception_all`, or
  - a named list meeting {`TypeError`, `Exception`, `BaseException`}.

  Today the named form cannot carry TypeError: `KNOWN_EXCEPTIONS` excludes it, and a named
  `no_exception TypeError` is rejected (probe `l3e`). So in practice the rule is `\all`.
- **Exemption.** A site the #383 guard `_gr383g` has already shown to be hashed on the path keeps the
  deny-list check only.

What it does **not** do:
- It converts nothing.
- It makes no value derivable.
- It changes no WhyML, so every PASS `.mlw` is byte-identical by construction.
- It adds no axiom and no facade.

---

## 3. THE SPIKE: the first executed action (Gate S)

### S0: LINK-3 premise probes (make-or-break, soundness)

The question is whether an *ambient* TypeError from a `#UND` hash site can turn into a **normal return**
that falsifies a proved `ensures`. There are two channels:
- the same function catches or swallows the exception;
- a caller does.

Probes go under `scratchpad/rg/probes/`. Each one is a full `pycsl.py` proof via `heavy.sh`, plus the
CPython `__main__` result.

| probe | shape | the claim it tests |
|---|---|---|
| `l3a` | `try: {m.get("a")} except TypeError: return 2` in an un-claimed `ensures \result == 1` | handler in the same function |
| `l3b` / `l3f` | un-claimed callee hashes `#UND`; un-claimed caller `except TypeError` / `except Exception` | handler in a caller |
| `l3i` | bare `except:` | handler, any class |
| `l3h` | `with contextlib.suppress(TypeError):` | suppressing context manager |
| `l3g` / `l3j` / `l3k` / `l3o` | `return` inside `finally`, in the hashing function | finally-swallow, same function |
| `l3p` | un-claimed callee hashes `#UND`; caller `try: out[0] = h(m) finally: return` | finally-swallow, caller |
| `l3n` | the `l3o` shape with a KeyError `d["a"]` instead of a hash | is a finally-swallow hole specific to hashing? |
| `l3d` | `no_exception \all` caller calls an un-claimed callee that hashes `#UND` | the review's `p_claim_calls_unclaimed` (§6 below) |
| `l3e` | `no_exception TypeError` | can the named form carry the claim? |

**Pass:**
- every caught or swallowed form is refused, fails, or is fail-closed (a Why3 type error);
- `l3d` is recorded separately.

**Refuted:** any form PROVES while CPython returns normally with a different result.

### S1: the gated e1 log-mode flip, measured

- **Instrument.** A LOG-ONLY copy of `pycsl.py` (`scratchpad/rg/spike/patch.py`, applied to a scratch
  `git archive` tree; never committed) writes one row per underivable hashed leaf:
  - file and function;
  - line;
  - kind: `UND`, `NONE` (no source), or `UND-IT` (a hashed iterable's elements);
  - `claimed` (the `#@ no_exception` block above the `def`);
  - `guarded` (#383g);
  - the leaf and the site.
- **Run.** `heavy.sh bash scratchpad/rg/spike/scan.sh <list> <tag> <budget> <jobs> --no-proof`
  (QUICK, resumable) over:
  - the root corpus (`test-suite/corpus/pycsl-reference/*.py`);
  - pyref (`test-suite/corpus/python-reference/**.py`);
  - the 53 mirrors;
  - the 104 `pycsl_lib` modules.
- **Positive control.** The witnesses must log `claimed=1` (done: `get_hash.py` `f` / `g`, `q4`,
  `q6`). The ungated mirror count must be of the order of e1's 679 / 27 (calibration: the instrument
  sees the population the full flip saw).
- **Pass:** 0 claimed, unguarded rows in a PASS file (root or pyref expected PASS, any mirror, any
  `pycsl_lib` module that screens rc 0 at base).
- **Refuted:** any such row. That row is the precise cost.

### S2: the red-team pair at base

- `{m.get("a")}` and `seen.add(f.get("name"))` under `no_exception \all`
  (`/home/fabrice/git/pycsl/scratchpad/wall-dict/drv/get_hash.py`), q4, q6, and the rh1 / e1 / g3
  residual probes must PROVE at base.
- The same bodies without the claim must also PROVE.

---

## 4. Build (only if S0 ∧ S1 pass; Gate B / C)

1. **Code.** The predicate goes inline in the hashing pass in `src/pycsl/pycsl.py`, using the per-function
   claim set built from `_ir342["functions"][*].contracts` (route #347's pattern). There is no new `def`
   in a mirrored file, and the mirror twin is `\trusted`. The message carries a new code
   `PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM`.
2. **Corpus 6400-6449.** Witnesses (expected FAIL / refused): `get_hash` `f` and `g`, q4, q6, the rh1 /
   e1 / g3 residual probes. Controls (expected PASS):
   - un-claimed bodies that hash `#UND`;
   - claimed bodies that hash derivable values.
3. **Census.** `bin/refusal-witness-census.tsv` rows via `_census_row` (`heavy.sh`), plus the advice
   audit.
4. **Docs.**
   - `test-suite/annotations.md` §7.120+;
   - `docs/pycsl-translational-reference.md` §T.6.131+;
   - REPAIR notes in `route383` / `route394` / `route421`;
   - an `open-routes/README.md` entry.
5. **Battery** (brief rule 5, each rc teed in full):
   - fidelity (both sync gates);
   - root + pyref byte-diff against `/home/fabrice/git/pycsl-rg-base` (both counts);
   - mirror emit sweep (0 MOVED expected; MOVED = OWED proof);
   - `pycsl_lib` screen;
   - planes (61);
   - getattr-erasure;
   - clause-survival;
   - `check-assumed-facts --emit-dir`;
   - carriers;
   - advice audit;
   - witness coverage.

   Ledger 3; `\trusted` count unchanged (a soundness repair converts nothing).

---

## 5. Costed scope

| item | cost |
|---|---|
| S0 | 18 small proofs, about 15 min of NORMAL slot |
| S1 | about 4,400 corpus + 53 mirror + 104 lib `--no-proof --no-typecheck` runs, QUICK slot, in resumable chunks under 170 s each, about 60-90 min |
| S2 | 5-8 small proofs |
| build + battery (only on pass) | about 3-4 h, including two corpus sweeps (base + candidate) |
| mirror proofs | none OWED by construction (no WhyML change) |

---

## 6. Recorded separately, not widened: a claimed caller and an un-claimed callee

The review's O7 (`p_claim_calls_unclaimed`) is reproduced here as probe `l3d`. If it PROVES, a
`no_exception \all` caller's claim is false whenever an un-claimed same-file callee hashes `#UND`.
- **KeyError:** route #178 already refuses this shape (probe `l3c`'s message).
- **TypeError from hashing:** no route does.

So it is a hole of its own, and R-gate (intra-procedural) does not close it. It is recorded as a separate
open route. R-gate is **not** widened to cover it.

---

## 7. Results

*(Filled in after the spike; see §R below.)*

---

## §R. Spike results (Gate S), 2026-10-28T03:15-03:55Z: S0 REFUTES, so the verdict is CERTIFIED-BOUNDARY

The evidence is in `getting-better/systematic-soundness-r3/rg-dict-r3/`:
- `probes/` holds the S0 sources and full outputs;
- `s2/` holds the S2 sources and base outputs;
- `spike/` holds the log-mode instrument (`patch.py`, `scan.sh`), the per-tree logs and rc files, and the
  `finally` census.

Every pycsl run went through `scratchpad/heavy/heavy.sh`. S0 and S2 are full proofs at base. S1 is
`--no-proof --no-typecheck` on a `git archive` copy of 289fe6029 with the log patch.

### S0: LINK-3 premise (P1): REFUTED

**What the documents say.**
- `docs/pycsl-static-semantics-reference.md` §2.1.13 gives `no_exception` its meaning.
  - **The obligation universe.** It is `active(f) = no_exception_set(f) ∪ (no_exception_all(f) ?
    KNOWN_EXCEPTIONS : ∅)`, and `KNOWN_EXCEPTIONS = {ZeroDivisionError, IndexError, KeyError,
    ValueError, StopIteration}`. **TypeError is outside it.** A named `no_exception TypeError` is
    rejected (probe `l3e`: "no_exception names unknown exception 'TypeError'"), so a claim covering
    TypeError can only be `\all`.
  - **What `\all` covers in practice.** The refusal routes (#174, #304, #347, #349) read `\all` as
    "any class".
- The trigger model (`config/skills/pycsl-exception-model/SKILL.md`, "Inter-procedural rules") makes
  every implicit exception outside a claim **ambient**. A WhyML `ensures` is a normal-termination
  postcondition. So an un-claimed function's `ensures` is claimed only for a normal return. That is
  sound only if no ambient exception can turn into a normal return.

**What the probes measured** (all full proofs at base 289fe6029; CPython results from the `__main__`
drivers):

| probe | channel | base result | CPython |
|---|---|---|---|
| `l3a` | `except TypeError` in the hashing function | REFUSED (route #174) | 2 |
| `l3b` / `l3f` | caller `except TypeError` / `except Exception` | REFUSED (route #174) | 2 |
| `l3i` | bare `except:` | REFUSED (route #174) | 2 |
| `l3c` | caller `except KeyError` (KeyError control) | REFUSED (route #178) | 2 |
| `l3h` | `with contextlib.suppress(TypeError)` | REFUSED (route #257) | 2 |
| `l3g` / `l3j` / `l3k` | `return r` in `finally` of an `-> int` function | FAIL (Why3 type error, fail-closed) | 2 |
| `l3q` | `break` in `finally` inside a loop | FAIL | 2 |
| **`l3o`** | `return` in `finally` of an `-> None` function, around `hash(m.get("a"))` | **rc=0 PROVED** `ensures out[0] == 1` | `out[0] == 2` |
| **`l3p`** | un-claimed callee hashes `#UND`; un-claimed caller `out[0] = 2; try: out[0] = h(m) finally: return` | **rc=0 PROVED** `ensures out[0] == 1` | `out[0] == 2` |
| **`l3n`** | the `l3o` shape with a KeyError `d["a"]` | **rc=0 PROVED** | `out[0] == 2` |
| **`l3d`** | `no_exception \all` caller returns `h(m)`; un-claimed `h` hashes `{m.get("a")}` | **rc=0 PROVED** | TypeError |

**LINK-3 finding.** In an un-claimed function, an ambient exception does **not** only end the function
abnormally.
- **The channel.** A `return` inside `finally:` discards the in-flight exception and makes the
  function return normally. The model lowers the `finally` return as the normal path, `()`.
- **The consequence.** The proved `ensures` of that function, or of a caller (`l3p`), is false of a
  normal return.
- **Already closed.** Handlers (#174, #178) and suppressing context managers (#257).
- **Still open.** A jump in the finalbody is not refused: route #21 handles a `finally` with
  handlers, and route #156 handles a jump in the try *body*.

So a hash TypeError in an un-claimed function **can** invalidate an `ensures` that its callers rely on.
R-gate would leave `l3o` and `l3p` admitted (no claim anywhere), while the full flip would refuse both.
By the task's decision rule, R-gate is **unsound as a closure of the `#UND` family** and is **not
built**.

The hole is not specific to hashing (`l3n` is a KeyError). It is recorded as **open route #431**
(`open-routes/route431-finally-jump-swallows-ambient-exception.md`), with measured repair cost **0**:
- an AST census finds no `return` / `break` / `continue` inside any `finally:` among 4,149 root, 2,217
  pyref, 53 mirror and 104 `pycsl_lib` files (`spike/finally_census.tsv`, `spike/finally_census.py`);
- PEP 765 makes the shape a SyntaxWarning in CPython 3.14.

`l3d` is the review's `p_claim_calls_unclaimed`. It is recorded separately as **open route #430**. It is
not widened into R-gate.

### S1: gated log-mode flip (P2): narrowed to 1 root PASS file

The instrument is calibrated against e1's full flip (`systematic-soundness-r3/e1-r392-395/`):
- **Positive control.** Every S2 witness logs `claimed=1`, and every un-claimed control logs
  `claimed=0` (`spike/s2.log`).
- **Ungated mirror population.**
  - UND: 568 distinct `#UND` sites in 24 mirrors, plus 37 hashed-iterable (`UND-IT`) rows.
  - NONE: 76 no-source leaves in 26 mirrors. Most are slice bounds such as `x[1:]`: the base pass
    treats every subscript slice as hashed, which is noise for this measurement.

  Together: 33 mirrors, against e1's 679 sites / 27 mirrors at `3b2d2e763`.
- **Ungated corpus population.** It covers e1's seven PASS files: 0882, 0883 and 3600 (UND), 1318
  (NONE), pyref 0091 and 0212 (NONE), and `counter_proves` (UND-IT).
- **Verdict agreement.** The rc=0 counts reproduce the known populations: root 2,513 (the byte-diff
  baseline is 2,512 `.mlw`), pyref 2,186, and lib with the same 17 non-zero rc as e1's `lib-base.tsv`.

**Gated cost** (rows with `claimed=1`, unguarded):

| tree | files scanned | rc=0 | claimed rows | claimed files | in a PASS file |
|---|---|---|---|---|---|
| mirror | 53 | 53 | **0** | 0 | 0 |
| `pycsl_lib` | 104 | 87 | **0** | 0 | 0 |
| pyref | 2,217 | 2,186 | **0** | 0 | 0 |
| root | 4,149 | 2,513 | 8 | 7 | **1**: `6336_r427_ctl_snapshot_iteration.py` (expected PASS, rc=0); the other 6 are expected FAIL: 3341, 3342, 5069, 5368, 5501, 5992 |

The one PASS cost is a route-#427 control. `d[k + 100]` / `d[k + 300]` (`d: Dict[int, int]`) are under
`no_exception \all`, with `k` from `list(d.keys())` and from a generator over another dict. The int key
plus an int literal is derived as `#UND`. That is a derivation-precision gap, not a TypeError: CPython is
fine. The review's static prediction (O13 / O14: 0 mirrors, flip-scan claims only in expected-FAIL
files) is **confirmed for mirrors, lib and pyref**. It is **refined for root**: 1 PASS file, which the
review's grep over the 16 first-scan files could not see because 6336 postdates that scan.

### S2: witnesses at base (P3): confirmed

Full proofs at base (`s2/*.base.out`):
- `w01_get_hash`, the coordinator's `get_hash.py`: `{m.get("a")}` and `seen.add(f2.get("name"))` under
  `\all`;
- `w02_q4`;
- `w03_q6` (`seen.add(f.get("name"))` over `List[Dict[str, Any]]`);
- `w05_values_loop` (`v in seen` over `m.values()`);
- `w06_dict_key_get` (`{m.get("a"): 1}`).

Each is **rc=0 PROVED**, while CPython raises TypeError. The un-claimed twins `c_01` … `c_06` are also
rc=0 PROVED, except `c_04`. `w04` / `c_04` (`{mk()}` with an un-annotated `mk`) is FAIL at base, a
Why3 type clash and fail-closed, so it is not a witness. These are the witnesses R-gate would have
refused. Together with `l3o` / `l3p` (un-claimed), they are the live false proofs of the `#UND` family at
289fe6029.

### Verdict

- **Conversions:** CERTIFIED-BOUNDARY (§1; reason and reopening test from the review §4).
- **Hashing `#UND` residual, route R-gate:** CERTIFIED-BOUNDARY. Gate S refuted P1 (S0: `l3o`, `l3p`).
  Nothing was built.
  - **Reopening test.** Repair open route #431 (refuse a jump in `finally:`; measured cost 0). Then
    re-run S0: every channel must be REFUSED or FAIL.
  - **Then build R-gate per §4**, with these measured inputs:
    - cost 1 root PASS file (6336), to narrow by deriving `int + int-literal` / dict-key elements
      precisely, or justify;
    - 0 mirrors, 0 lib, 0 pyref;
    - witnesses `s2/w01-w03, w05, w06` (corpus IDs 6400-6449 remain unused).
  - **Route #430** stays a separate repair (route #178's callee summary extended with a
    "hashes `#UND`" bit) and must be costed on its own.
- **`\trusted` count:** unchanged (442 lines at 289fe6029; the brief's 448 is an older figure). Ledger: 3. No `src/`, corpus or census file was touched, so the
  emitter battery (byte-diff, mirror sweep, fidelity, census) has nothing to gate and was not run, by
  design. The only `bin/` change registers the four live carriers of #430 / #431 in
  `bin/check-open-route-carriers.py` (the project's gate for OPEN routes). That gate ran, through
  heavy.sh: rc=0, 14 carriers, the 4 new ones SUCCESS (`rg-dict-r3/gates/open-route-carriers.log`).

*Order of work, stated honestly.* The S0 probes `l3a` to `l3p` and the S1 positive control ran while this
plan was being drafted (03:15-03:30Z): the task asked for the LINK-3 answer before planning. No `src/`,
`bin/` or corpus file had been edited when this plan was committed.
