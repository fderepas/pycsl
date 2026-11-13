# Run #7 lvQ: a faithful open-world model of external effects

Executor lvQ, driver run #7 batch A, 2026-11-13. Tree `pycsl-lvQ`, branch `run7-lvQ`, base 1ffab454c.
Scratch tree for probes: `/home/fabrice/git/lvQ-st` (a `git archive` of 1ffab454c; probe logs in
`/home/fabrice/git/lvQ-st/probe/<tag>.{log,mlw,src.py,patchlog}`).

## 1. Census of what exists (lesson p), at 1ffab454c

| effect | existing lowering at HEAD | raises modelled? | verdict |
|---|---|---|---|
| `subprocess.run(args, **kw)` | generic dotted fallback `subprocess_run_1 <args>`: keywords DROPPED, an opaque `int` result, no `raises` | no | facade; R325 refuses it only when the int is then used arithmetically (`_why3_typecheck`) |
| `r.stdout` / `r.stderr` / `r.returncode` | `(r.stdout or r.stderr).strip()` lowered to `strip_0 ()`: the RECEIVER IS DROPPED (d0_coqc.mlw l.99) | no | facade |
| `Path / str` | `val function path_join_op (a b: string) : string` (#31 path model, Path = Why3 `string`) | n/a (pure) | faithful (deterministic, law-free) |
| `p.is_file()` / `is_dir()` / `exists()` | #31 `val path_isfile_op (s: string) : int` (impure, law-free) | no (CPython 3.14 `os.path.isfile` swallows OSError/ValueError: correct) | faithful |
| `p.resolve()` | #31 `val path_resolve_op` (impure) | no | (not needed here) |
| `p.mkdir(parents=True, exist_ok=True)` | `root_mkdir_0 ()`: receiver and keywords dropped, no raise | no | facade |
| `Path.cwd()` | `path_cwd_0 ()` opaque int; R325 when passed on (type_of_batch) | no | refused |
| `p.write_text(s)` / `p.read_text()` | generic receiver-less ops | no | facade |
| `json.dumps` / `json.loads` | the interpreter's own `json` signature as `val` with every parameter `int`; `loads` declares `raises { JSONDecodeError, TypeError }` | partly | opaque ints |
| `except subprocess.TimeoutExpired` | the dotted handler tag is DROPPED from the arm list (d0_coqc.mlw l.100: `with FileNotFoundError ->` only) | - | dead handler |
| `with open(..) as f` / `with X as y` | refused (`_py_stmt_with` drops the binding) | - | refused |
| lvO re.Match model (§7.320) | int HANDLE + law-free `val function` reads, no axiom | VCs for None/IndexError | the pattern copied below |
| `src/pycsl_lib` os/plib/subproc/json/hlib | closed-world toys, refused under `--import-path` (route #326, cv11 §4.1) | - | FORBIDDEN (brief) |

Semantics that decide the verdicts (read from the emitter, functions.py `_emit_function`):
a verified function's ESCAPING exceptions (own `raise`, callee `#@ raises`) are added to its own
`raises { .. }`; Why3 rejects any unlisted escaping exception at type-check (measured,
`/home/fabrice/git/lvQ-st/spike/t1.mlw`: "this expression raises unlisted exception E"). Implicit
IndexError of a subscript is NOT an escaping exception: it is the Why3 array-read precondition,
owed in every body (the polarity of route #527).

## 2. Depth-0 at HEAD (verbatim live body, `--no-proof --keep-mlw`, QUICK)

| stub (mirror file) | probe | verdict | first blocker |
|---|---|---|---|
| `_coqc_version` (audit_proof_reverify.py) | d0_coqc | L3-TC | `array string` vs `int` (splitlines facade); receiver of `.strip()` dropped; `TimeoutExpired` handler dropped |
| `_lean_version` (audit_proof_reverify.py) | d0_lean | L3-TC | same as `_coqc_version` |
| `_cache_root` (audit_proof_reverify.py) | d0_croot | TC-OK **FACADE** | `root_mkdir_0 ()`: receiver/keywords dropped, no raise |
| `_cache_load` (audit_proof_reverify.py) | d0_cload | L3-TC | `int` vs `_union__cache_load_0` (json.loads opaque int returned as `Optional[dict]`) |
| `_cache_store` (audit_proof_reverify.py) | d0_cstore | L3-TC | `int -> option int` (dict payload) vs `int` (json.dumps signature-typed `int`) |
| `_why3_typecheck` (pycsl.py) | d0_w3tc | REFUSED R325 | `r` from `subprocess_run_1` used as an int |
| `_parse_args` (pycsl.py) | d0_pargs | TC-OK **FACADE** | every `add_argument` receiver-less, keywords dropped, `parse_args` cannot raise SystemExit |
| `SertopSession.type_of_batch` (proof2why3/sertop.py) | d0_tob | REFUSED R325 | `path_cwd_0` opaque int passed to `run_sertop_batch` |
| `extract_lean_statements` (proof2why3/extract.py) | d0_exl | REFUSED route #264 | `augmented_path` bound only inside `with tempfile.NamedTemporaryFile(..) as tf` |
| `extract_rocq_statements` (proof2why3/extract.py) | d0_exr | REFUSED route #264 | `companion_path` (same `with ... as`) |
| `_generate_rocq_obligations` (pycsl.py) | d0_gro | REFUSED | `with ... as mf` (context manager) |
| `_resolve_runtime_config` (pycsl.py) | d0_rrc | REFUSED | `with ... as _cf` (context manager) |

## 3. STEP 0 spike (hand-written `.mlw`, no emitter edit)

`/home/fabrice/git/lvQ-st/spike/spike0.mlw`, `why3 prove -P z3 -t 10` (heavy.sh): law-free model =
impure `val`s with NO `ensures` / `reads`, each declaring every exception CPython can raise there;
results of a world query are fresh per call; the `CompletedProcess` is an int handle read by
`val function`s (deterministic in the handle, exactly lvO's match-handle argument: the handle never
escapes). No axiom.

| goal | expected | result |
|---|---|---|
| `_cache_root` (verbatim, ensures true, escaping OSError family declared) | PROVE | Valid |
| `_cache_root_leaf` (assert false at head) | FAIL | Timeout |
| `_cache_root_noexc` (every raise wrapped `absurd`) | FAIL | Timeout |
| `_cache_root_world` (`is_file` after mkdir is false) | FAIL | Timeout |
| `two_reads` (two `is_file` reads equal) | FAIL | Timeout |
| `_why3_typecheck` (verbatim shape) | PROVE | Valid |
| `w3_world` (returncode is 0) | FAIL | Unknown |
| `w3_leaf_handler` / `w3_leaf_else` (FileNotFoundError arm, rc != 0 branch reachable) | FAIL | Unknown |
| `_coqc_version` (`.splitlines()[0]`) | FAIL (blank tool output is CPython-reachable) | Timeout |

**Spike verdict: GO.** An open-world model is expressible soundly without an axiom. It also shows
that `_coqc_version` / `_lean_version` can NOT be converted honestly: `(out.stdout or
out.stderr).strip().splitlines()[0]` raises IndexError when the tool prints nothing (a `coqc` on PATH
that prints nothing), and PyCSL owes the in-bounds precondition there.

## 4. Plan

Build (inline, in `\trusted`-twin live methods): the PATH writes `mkdir` / `write_text`, `Path.cwd()`,
`json.dumps`, and the `subprocess.run` handle with `returncode` / `stdout` / `stderr` reads; each
call raises every exception CPython can raise there, registered so the existing escaping-exception
and handler machinery (`_callee_raised_in`, `_handle_try_stmt`) sees it. Targets: `_cache_root`,
`_cache_store`, `SertopSession.type_of_batch`, `_why3_typecheck`. Expected to stay trusted with a
measured reason: `_coqc_version`, `_lean_version` (IndexError), `_cache_load` (json.loads returns
`Any`, declared `Optional[dict]`), `_parse_args` (no argparse model yet), the four `with ... as` stubs
(no context-manager model).

(Results are appended below as they are measured.)
