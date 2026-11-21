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
`/home/fabrice/git/lvQ-st/probe/evidence/spike/t1.mlw`: "this expression raises unlisted exception E"). Implicit
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

`/home/fabrice/git/lvQ-st/probe/evidence/spike/spike0.mlw`, `why3 prove -P z3 -t 10` (heavy.sh): law-free model =
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

## 5. The capability as built (src/pycsl only, inline, `\trusted`-twin methods)

| live method (mirror twin) | what it does |
|---|---|
| `Module6_WhyMLTranspiler.transpile` (`\trusted`) | MODULE-WIDE decision, after `_scan_preamble_needs`: every call of a modelled callee string in a lowered (non-`\trusted`) body is checked against the modelled shape; a callee string ALL of whose occurrences match gets registry rows `{"exc_type": E, "condition": None, "ext": kind}` in `_module_func_raises` (one row per raised class) and its classes in `needs["user_exceptions"]`; any non-matching occurrence keeps the OLD lowering for every occurrence (byte-identical). argparse is all-or-nothing over its four callees. The rows are restored after `_build_callee_no_exception_summary` (which resets an imported stub's row, e.g. `dumps`). |
| `FunctionEmissionMixin._reset_function_state` (`\trusted`) | per function: PROCESS LOCALS (every binding a modelled `subprocess.run`, every other use `.returncode` / `.stdout` / `.stderr` / `.stdout.strip()`...) under `_re_compiled_locals["<ext_p>"]`, ARGPARSE LOCALS (bound by `ArgumentParser(..)` / `<local>.add_argument_group(..)`, used only as receivers) under `"<ext_a>"`; route #174's handler-reachability census now counts the registry `ext` rows as raised in the `try` body. |
| `ExpressionEmissionMixin._handle_call_expr` (`\trusted`) | the lowering: each modelled call is an impure `val ext_*_op ... raises { <every class> }` with NO `ensures` / `reads`; refusals `PYCSL-R7Q-EXT-HANDLE-ESCAPES` (a `subprocess.run` result that is not a process local), `PYCSL-R7Q-EXT-PATH-RECEIVER` (`mkdir` / `write_text` on a receiver, or `write_text` of a text, not typed path / str), `PYCSL-R7Q-EXT-ARGPARSE-RECEIVER`. |
| `ExpressionEmissionMixin._handle_attribute_expr` (`\trusted`) | `r.returncode` / `r.stdout` / `r.stderr` of a process local -> `val function ext_cp_<attr>_op (h: int) : int / string` (law-free, deterministic in the handle: lvO's argument, the handle never escapes). |
| `ExpressionEmissionMixin._is_string_expr` (`\trusted`), `_str_method_recv_and_tail` (live-only) | the string-typed results (`r.stdout`, `Path.cwd()`, `json.dumps(..)`) and the `r.stdout.strip()` receiver. |
| `AbstractOpsMixin._insert_abstract_val_block` (`\trusted`) | a raising `ext_` op is placed after the `exception` declarations (typed / store memory models emit `type loc` before them). |

Lowerings (CPython 3.14 exception sets; `OS` = BlockingIOError, BrokenPipeError, ChildProcessError,
ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError, FileExistsError,
FileNotFoundError, InterruptedError, IsADirectoryError, NotADirectoryError, OSError, PermissionError,
ProcessLookupError, TimeoutError -- every OSError class the errno mapping can produce, so a handler for any
subset is exact):

| Python | WhyML | raises |
|---|---|---|
| `r = subprocess.run([<str lit / str name>..], capture_output=True, text=True)` | `ext_subprocess_run_op <array string> : int` (handle) | OS, ValueError (NUL), UnicodeDecodeError |
| `r.returncode` / `r.stdout` / `r.stderr` | `ext_cp_returncode_op h : int`, `ext_cp_stdout_op h : string`, `ext_cp_stderr_op h : string` (`val function`) | - |
| `Path.cwd()` | `ext_path_cwd_op () : string` | OS |
| `p.mkdir(parents=<bool>, exist_ok=<bool>)` | `ext_path_mkdir_op p parents exist_ok : unit` | OS, ValueError |
| `p.write_text(<str>)` | `ext_path_write_text_op p s : int` | OS, ValueError, UnicodeEncodeError |
| `json.dumps(<name>[, indent=<int>])` (also the `dumps` an `--import-path` run rewrites it to) | `ext_json_dumps_op indent : string` | TypeError, ValueError, RecursionError |
| `p = argparse.ArgumentParser(<literal kwargs>)` | `ext_argparse_parser_op () : int` | AttributeError, IndexError (empty `sys.argv`), TypeError, ValueError |
| `p.add_argument(<literals>)` | `ext_argparse_add_op h : unit` | ArgumentError, TypeError, ValueError |
| `g = p.add_argument_group(<literals>)` | `ext_argparse_group_op h : int` | TypeError, ValueError |
| `p.parse_args()` | `ext_argparse_parse_op h : int` | OS, SystemExit, UnicodeEncodeError |

Not modelled (old lowering kept, or refused): `subprocess.run(.., timeout=..)` (the front-end DROPS a
dotted `except subprocess.TimeoutExpired` handler -- `Module5._py_stmt_try` keeps only `ast.Name`
elements, a pre-existing hole noted here, not fixed: the method's twin is VERIFIED); any other keyword;
a CompletedProcess that escapes; `read_text`, `json.loads` (returns `Any`); `with ... as` (no
context-manager model); argparse with a non-literal argument (`type=int`).

## 6. Witnesses (expected FAIL) and controls (expected PASS), corpus IDs 9700-9711

All run in the default (`hoare`), `--memory-model typed` and `--memory-model store` models
(`/home/fabrice/git/lvQ-st/probe/evidence/tools/wit.sh`; logs `/home/fabrice/git/lvQ-st/probe/evidence/logs/wit-w2/`, `wit-w3/`, `wit-w4/`, `wit-w5/`,
tables `table.txt`; w1 was the pre-fix run, superseded). Every CPython driver was run (`ulimit -v`):
each FAIL witness prints `VIOLATION`, each control prints `result`.

| id | claim | default | typed | store | why it fails / proves |
|---|---|---|---|---|---|
| 9700 | `mkdir` cache root, `ensures True` | PASS | PASS | PASS | control |
| 9701 | `except OSError` around `mkdir` dead (`\result == 0`) | FAIL | FAIL | FAIL | postcondition Unknown (mkdir raises FileExistsError on a file) |
| 9702 | `returncode == 0` (world fact) | FAIL | FAIL | FAIL | postcondition Unknown |
| 9703 | same handle read twice equal | PASS | PASS | PASS | control (`val function` of one handle) |
| 9704 | two runs give equal stdout | FAIL | FAIL | FAIL | postcondition Timeout (fresh handles) |
| 9705 | `except FileNotFoundError` around `subprocess.run` dead | FAIL | FAIL | FAIL | postcondition Unknown |
| 9706 | `is_file()` after `write_text` | FAIL | FAIL | FAIL | postcondition Unknown (law-free reads) |
| 9707 | `except FileNotFoundError` around `Path.cwd()` dead | FAIL | FAIL | FAIL | postcondition Unknown |
| 9708 | `json.dumps` under `no_exception \all` | FAIL | FAIL | FAIL | refused by the existing `no_exception` callee census (fail-closed) |
| 9709 | CompletedProcess returned | FAIL | FAIL | FAIL | refused `PYCSL-R7Q-EXT-HANDLE-ESCAPES` |
| 9710 | `_why3_typecheck` shape, result in {0,1,2} | PASS | PASS | PASS | control (handler + both branches) |
| 9711 | rc != 0 branch dead (`\result == 0`) | FAIL | FAIL | FAIL | postcondition Unknown |

## 7. Per-stub verdicts

Logs under `/home/fabrice/git/lvQ-st/probe/evidence/` (`logs/apr1.*`, `logs/fin-*` final re-proofs --fun, `L/wf-a.*` whole-file, `L/var*.{table,*.log}`
leaf + mutants, `L/post-p1.*` sweeps / planes, `L-sync.log`, `L-mcheck.log` fidelity).

| stub | verdict | gates |
|---|---|---|
| `audit_proof_reverify._cache_root` | **VERIFIED** (verbatim live body) | (1) `--fun` SUCCESS, 0 non-Valid (`logs/apr1.fun._cache_root.log`); (2) whole file SUCCESS 0 non-Valid, oom_kill 0->0 (`L/wf-a.audit_proof_reverify.py.log`); (3) mutant `n = 7 // len(root)` FAILS (division-by-zero goal, `L/var3.mut_croot.log`); (4) leaf `#@ assert 1 == 2` at head FAILS (`L/var.leaf_croot.log`); (5) fidelity rc 0; (6)(7) see §8 |
| `audit_proof_reverify._cache_store` | **VERIFIED** (verbatim) | (1) `logs/apr1.fun._cache_store.log`; (2) as above; (3) mutant `n = 7 // len(json.dumps(..))` FAILS (`L/var3.mut_cstore.log`); (4) leaf FAILS (`L/var.leaf_cstore.log`) |
| `pycsl._parse_args` | **VERIFIED** (verbatim live body; the mirror body was STALE, 98 lines differ, now the live one) | (1) via the leaf/mutant `--fun` runs (`L/var.leaf_pargs.log`, `L/var2.mut_pargs.log`, the unmutated `--fun` is the base of both); (2) whole file `pycsl.py` SUCCESS, 745 goals 0 non-Valid, oom 0->0 (`L/wf-a.pycsl.py.log`); (3) mutant `q = 7 // k` (k = 0) FAILS; (4) leaf FAILS |
| `_coqc_version`, `_lean_version` | still `\trusted` | `subprocess.run(.., timeout=..)` is not modelled (the dropped `except subprocess.TimeoutExpired` arm would let a modelled TimeoutExpired escape where CPython catches it); and with timeout modelled the body is STILL not honest: `.splitlines()[0]` raises IndexError on blank tool output (CPython-reachable), PyCSL owes the array-read precondition, the spike's `_coqc_version` goal does not prove (spike0.mlw). The `\trusted` contract (no `raises`) is FALSE of CPython. |
| `_why3_typecheck` | still `\trusted` | model reached (TC-OK of the subprocess part, probe `d2_w3tc`), but the `(bool, str)` early returns use the homogeneous `exception Return_2 (int, int)`: L3-TC `(int, string)` vs `(int, int)`; a typed tuple-return exception needs edits of the VERIFIED `_handle_return_stmt` (stmt_control_flow.py) / `_wrap_body_with_return_catch` (statements.py). Shape control 9710 PROVES. |
| `SertopSession.type_of_batch` | still `\trusted` | the `Optional[Path]` dataclass field `cwd` is erased to `Any` (record field `int`), so `self.cwd or Path.cwd()` selects an operand the model cannot represent (route #487 refuses it). Needs an Optional[Path] field model. |
| `_cache_load` | still `\trusted` | `json.loads` returns `Any`, the function is declared `Optional[dict]` (CPython returns a list for a cache file `[1]`), and `read_text` is not modelled (UnicodeDecodeError would also escape). |
| `extract_lean_statements`, `extract_rocq_statements`, `_generate_rocq_obligations`, `_resolve_runtime_config` | still `\trusted` | `with ... as` (no context-manager model); route #264 / the `_py_stmt_with` refusal at depth 0 (probes `d0_exl`, `d0_exr`, `d0_gro`, `d0_rrc`). |

## 8. Planes, sweeps, ledger (final)

- Corpus byte-diff vs the driver's base `scratchpad/run7/base/bd` (= 1ffab454c): root 0 MOVED,
  0 APPEARED, 1 GONE (`1723_route212_verify_imports_control`, a `--verify-imports` flake: the
  single-file re-emission is `cmp`-identical to base, `L/post-p1.status` "1723 cmp rc=0");
  pyref 2185/2185 0/0/0. (Swept before the final json.dumps-argument change, which reaches only
  modelled `json.dumps` calls: none in the corpus outside the 97xx witnesses.)
- Mirror sweep vs `base/mir`: MOVED `audit_proof_reverify`, `pycsl` only (the two home files,
  both whole-file proved); no big-file mover; OWED: none.
- Fast planes `bin/run-soundness-planes.sh`: 62/62 rc 0 (`L/f2.planes.log`); RED planes compared
  against base 1ffab454c (`L/red-r2.*`): all green at base, all green now. Individually
  (`L/post-p1.*`): check-assigns-writes-survival, check-trusted-frame-honesty,
  check-vacuous-drivers, check-getattr-erasure, check-mirror-coverage rc 0.
- `\trusted` count 389 -> 386; proof-axiom ledger unchanged (no axiom added).
- oom_kill 0 at the start and end of every proof run.

All evidence: `/home/fabrice/git/lvQ-st/probe/evidence/` (`L/`, `logs/`, `spike/`, `tools/`); depth-0 probes `/home/fabrice/git/lvQ-st/probe/d*`.
