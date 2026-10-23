# self-field-append-wall — INDEPENDENT Gate-R response

**Verdict: CONFIRM (clean M1 — nothing turns RED), with two mandatory REFINE corrections to the report's framing.**
The facade is real (Step 1, quoted). A faithful `self._field <- snoc (old self._field) x` write-back is
model- and contract-compatible: it discharges setenv's actual contract *and* an observational read-back driver,
axiom-free, non-vacuous (Step 2, `why3 prove -P z3` cited). No currently-green corpus proof regresses — but that
is because **no green corpus proof exercises the append at all**, not because the effect is "safely invisible."
The report's "vacuously-green corpus could turn RED" fear is unfounded, and the true cost is larger than a
"minimal write-back."

---

## Step 1 — Facade CONFIRMED

Emitted `src/pycsl_lib/proc/__init__.mlw` for `setenv` (via
`PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py src/pycsl_lib/proc/__init__.py --import-path src/pycsl --keep-mlw`):

```
128  let processstate__setenv (self: processstate) (key: string) (value: string) : unit
131    let self__env_vals = Array.make 1024 0 in     (* FRESH local, array int (int-erased) *)
133    let self__env_keys = Array.make 1024 0 in     (* FRESH local *)
...
150      self__env_keys[!self__env_keys_len] <- key;   (* writes the LOCAL *)
151      self__env_keys_len := !self__env_keys_len + 1;
152      self__env_vals[!self__env_vals_len] <- value;
154      self._env_count <- (self._env_count + 1)       (* only the COUNT hits the field *)
```

`self._env_keys <- …` / `self._env_vals <- …` are **never emitted**. The append writes a throwaway 1024-cell local;
the real field is unchanged. Emission site located: `statements.py:2980-2982`
(`body_code = "    let {safe_tgt} = Array.make 1024 0 in ..."` for any append target not in `local_refs`/`ref_params`,
i.e. every self-field) plus the write itself at `statements.py:1404-1406`
(`{safe_arr}[!{len_ref}] <- {arg}; {len_ref} := !{len_ref} + 1`). **CONFIRMED.**

## Step 2 — the faithful effect vs. the corpus

### Baseline reality (the report's premise is only 1/3 true)
Running each affected module (`… --import-path src/pycsl`, no keep-mlw):

| module | append site | baseline status |
|---|---|---|
| `proc` (`_env_keys`/`_env_vals`) | `setenv` | **RED / INCOMPLETE** — Why3 typecheck failure at mlw line 45: `raise (Return_str self._argv_keys[index])` — `_argv_keys : array int` read where `string` expected. **Unrelated to append** (it's the `argv` int-erasure wall). Whole-module typecheck fails → setenv's VCs never reach the prover. |
| `iomod` (`_buf`) | `__init__`/`write` | **RED / INCOMPLETE** — type error at mlw line 86: `fileio` vs `int`. Unrelated to append. |
| `hlib` (`_input`) | `update` | **GREEN** — but `update` is `#@ \trusted`, emitted as `val sha256__update (self: sha256) (data: int) : unit` — an **abstract val with NO body**. The append body is *entirely absent* from the proof. |

So of the three named "affected corpus" programs, two are already RED for reasons that have nothing to do with the
append, and the one that is GREEN has the append abstracted behind `\trusted`. **No green proof exercises the
append facade.** Additionally, `setenv` carries `assigns …` only — **no `ensures`** — so even were it proven, its
own VC never depended on the append effect either way.

### The faithful write-back oracle (hand `.mlw`, contract-compatibility route)
A minimal *emitter* spike is fundamentally blocked: the field is `array int` initialized `Array.make 0 0`, so
there is nowhere to write back an appended cell without retyping the field to `seq`. I therefore took the report's
sanctioned alternative — a hand `.mlw` modeling `setenv`'s real contract with the faithful effect
(`scratchpad/setenv_faithful.mlw`). `why3 prove -P z3`:

```
Goal processstate'vc.                        Valid (0.01s)      -- seq-field record + invariant
Goal processstate__setenv_faithful'vc.       Valid (0.02s)      -- self._env_keys <- snoc (old self._env_keys) key
                                                                    with observational snoc + tail postconditions
Goal test_setenv_readback'vc.                Valid (0.02s)      -- append then read the tail back (driver observation)
Goal processstate__setenv_evil'vc.           Unknown            -- WRONG write-back (snoc value into keys) does NOT prove
```

The faithful `self._env_keys <- snoc (old self._env_keys) key`:
1. typechecks + proves Valid against setenv's real `writes {…}` frame (no axiom — `seq.Seq` + `snoc` intrinsic);
2. discharges an observational append→read-back driver (`test_setenv_readback` Valid) — the effect is **real**;
3. is non-vacuous (the evil-twin is correctly *not* Valid).

This matches the report's R3 claim for the modeling axis. **Ledger stays 3 (no new axiom).**

## Why CONFIRM, with two REFINE corrections

**CONFIRM the load-bearing question:** the faithful effect does *not* turn any currently-green corpus proof RED —
the M1 blast radius on the green set is **empty**. The facade is not load-bearing for any green proof.

**REFINE #1 — the "vacuously-green corpus" framing is inaccurate.** There is no vacuously-green corpus proof of
the append to break: hlib's append is `\trusted`-abstracted (not in the proof), and proc/iomod don't typecheck at
baseline. The risk the report worries about (a faithful effect exposing a latent-vacuous *green* contract) simply
does not exist here, because the append never sits inside a discharged VC today.

**REFINE #2 — the cost is NOT a "minimal write-back," and proc/iomod are not usable green oracles until
prerequisites land.** For the homogeneous case the field is `array int` sized 0; a faithful write-back is
*impossible* as an array op (can't index a 0-cell array). It requires retyping the field to `seq` — touching the
record type, the constructor `by { … }`, and **every read** `self._env_keys[i]` — i.e. the seq-field retrofit,
plus the pyval element for the heterogeneous collectors. Moreover, before proc/iomod can serve as *green* M1
oracles at all, their pre-existing, unrelated int-erasure typecheck failures (proc `argv` array-int→string; iomod
`fileio`-vs-int) must be fixed first; otherwise the append change lands in a non-typechecking module and cannot be
validated on the real pipeline.

## Bottom line for the driver
Build is **sanctioned on soundness grounds** (clean M1: faithful effect is axiom-free, contract-compatible, and
regresses nothing green). But scope it honestly: it is a **seq-field-retrofit emitter change**, not a one-line
write-back, and the "make-or-break" as originally posed (keep the corpus green) is **moot** — the append is not in
any green proof. If the goal is to *observe* the effect on the pipeline (not just model it), you must first repair
proc's `argv` and iomod's `fileio` int-erasure so a green baseline exists to protect.

---
### Oracle artifacts
- Emitted facade (regenerate): `PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py src/pycsl_lib/proc/__init__.py --import-path src/pycsl --keep-mlw` → `src/pycsl_lib/proc/__init__.mlw:128-155` (gitignored; removed after inspection)
- Baseline runs: `… src/pycsl_lib/{proc,iomod,hlib}/__init__.py --import-path src/pycsl`
- hlib abstract-val: `… src/pycsl_lib/hlib/__init__.py --import-path src/pycsl --keep-mlw` → `val sha256__update …`
- Faithful hand model: `scratchpad/setenv_faithful.mlw` + `why3 prove -P z3` output above
- Emitter sites: `src/pycsl/module6_whyml/statements.py:2980-2982` (shadow-local decl), `:1404-1406` (local write), `ir_scanner.py:642` (`find_append_targets`)
- **No source edits made; tree left exactly as found.**
