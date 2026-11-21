# Run #8 lvX report: `_sha256_file` (VERIFIED) and `SertopSession.type_of_batch` (still trusted)

Executor lvX, driver run #8 batch C. Tree `/home/fabrice/git/pycsl-lvX`, branch `run8-lvX`, base
0057c8b94. All log paths below are relative to the tree root (`scratchpad/lvX/...`).

Commits (never pushed):
- f55effdb2: WIP capability, conversion and witnesses.
- be1a7a78b, 8163f8c0e: WIP report drafts.
- a5303269e: the gated conversion. It adds the census rows and drops the stale trusted-reasons row.
- (this report)

## Stub 1 `pycsl._sha256_file`: VERIFIED

### The link: `Path(<str>)`

The live emitter changes only in two `\trusted`-twin methods: `expressions._handle_call_expr`
and `_is_string_expr`. Both carry the same inlined test.

Old lowering: the generic `path_1 (str_hash_op s) : int` facade.

New lowering: `val function ext_path_of_str_op (s: string) : string`.
- It is deterministic: pathlib's parsing is lexical.
- It is law-free. It is not the identity, and it has no length, prefix or injectivity law.
- It raises nothing.

The model applies only when all of these hold. Otherwise the old lowering is kept.
- Every import binding of `Path` is the absolute `from pathlib import Path`, and there is no star import.
- Route #610's tables (`shadow_r610` for the function, `shadow_mod_r610` for the module) show
  `Path` is not bound in the function and not rebound at module level. The check fails closed
  when a table is absent.
- `Path` is not a function or a class of the unit.
- There is exactly one positional argument, with no keyword, and the emitter types it as a
  string (a str, or a Path through the #31 erasure).

TypeError for a non-str argument is refuse-only: it is not modelled. The change adds no new
self field and no registry row.

### The respelling

- Live and mirror `pycsl.py` both gain a module-level `from pathlib import Path`.
- The body becomes `_p = Path(path); return hashlib.sha256(_p.read_bytes()).hexdigest()`.
- The mirror twin is verbatim, with `\trusted` dropped.

Fuzz against the chunked loop (`scratchpad/lvX/fuzz_sha.py`, run under ulimit) covered 219 real
files: empty, 1 byte, around 8192 bytes, 5 MiB, 200 random files, missing, a directory, a
trailing `/`, `//`, unreadable (mode 0), NotADirectory, a symlink, a dangling symlink,
`/proc/self/status`, `""`, and an embedded NUL.
- 218 cases are identical.
- One case differs inside the same family: `""` raises FileNotFoundError in the old body and
  IsADirectoryError in the new one, because `Path("")` is `.`. Both are OSError.

### Gates

| gate | result | log |
|---|---|---|
| `--fun _sha256_file` (PYTHON_CPU_COUNT=4) | SUCCESS, 754 Valid / 0 non-Valid, oom_kill 0->0 | `scratchpad/lvX/L/fun._sha256_file.log`, `p/fun1.oom` |
| whole-file mirror `pycsl.py` (HEAVY_LOW, PYTHON_CPU_COUNT=6) | SUCCESS, 813 Valid / 0 non-Valid, oom_kill 0->0 (21:57Z-22:34Z) | `L/wf.pycsl.log`, `L/wf.out` |
| leaf-reachability (`#@ assert 1 == 2` at the head of the single block) | FAILS: only that assertion fails (Timeout) | `L/var.leaf.log`, `L/var.out` |
| mutant (`_n7 = 7 // len(path)`) | FAILS: division-by-zero goal | `L/var.mut.log` |
| fidelity x3 (sync, mirror-check, doc-coherency) | rc 0 / 0 / 0 | `L/E.txt` |
| corpus byte-diff vs base8/bd (one comparator per tree, cwd = tree root) | root: 3275 base / 3280 candidate, 0 MOVED, 0 GONE, 0 APPEARED, 5 new sources; pyref: 2185 / 2185, 0 / 0 / 0 | `L/p1.cmp-root.txt`, `L/p1.cmp-pyref.txt`, `L/p1.status` |
| M1 moved list | EMPTY: every corpus `Path(<str>)` sits in a `__main__` driver or is otherwise not lowered, so no re-proof was owed | `L/p1.moved-root.txt`, `L/p1.moved-pyref.txt` |
| mirror sweep vs base8/mir | 53 emitted; only `pycsl.mlw` moved (the home) | `L/p1.mir.diff`, `L/p1.mir.pycsl.diff` |
| fast planes | 61/62. The RED `check-trusted-reasons` is the stale `_sha256_file` row, dropped in a5303269e; re-run rc 0 (338 markers <-> 338 rows) | `L/p1.planes.log`, `L/p1.trusted-reasons-after.log` |
| individual planes | all rc 0: vacuous-drivers, getattr-erasure, mirror-coverage, assumed-facts, claim-vacuity (1791 at ceiling 1791), assigns-writes-survival, trusted-frame-honesty (single-underscore emit dir `L/p1.emit1`), count-trusted-directives | `L/p1.<plane>.log` |
| frontend-only / core-only conformance | rc 0 (38 OK / 0 MISMATCH) | `L/p1.fe-conf.log`, `L/p1.core-conf.log` |
| oom_kill | 0 at the start and end of every proof and of post.sh | `L/p1.status` |

The mirror diff for `pycsl.mlw` contains three changes:
- `_sha256_file` changes from a `val` to a `let` body with lvV's raises set.
- The new `ext_path_of_str_op`, `ext_path_read_bytes_op` and `ext_sha256_hexdigest_op` declarations appear.
- The `\trusted` callers `_check_rocq_proofs` and `main` gain the same `raises` row, through the
  escaping-row registration, as in lvV's `_cache_key`.

### Witnesses (IDs 10140-10145)

Full proofs: `L/witfull.tsv`, oom 0->0.

| id | expected | hoare | typed | store |
|---|---|---|---|---|
| 10140 deterministic `Path(s) == Path(s)` | PASS | SUCCESS | FAILED (see below) | FAILED |
| 10141 `str(Path(s)) == s` (not the identity) | FAIL | FAILED | FAILED | FAILED |
| 10142 `str(Path("")) == ""` | FAIL | FAILED | FAILED | FAILED |
| 10143 `Path` shadowed by a function-local import | FAIL | REFUSED (pre-existing "imported name shadows a module binding") | REFUSED | REFUSED |
| 10144 FileNotFoundError reachable through `Path(<str>)` + sha | FAIL | FAILED | FAILED | FAILED |
| 10145 `_sha256_file` shape under `except OSError` | PASS | SUCCESS | SUCCESS | SUCCESS |

10140 in typed and store fails closed. Because the body is pure, it is emitted as a `let function`,
and these models add the frame `ensures { !int_mem = old !int_mem }`. Why3 rejects that with
"This function depends on external variables, it cannot be used as pure" (`scratchpad/lvX/ty/*.typed.log`).

This is an emitter incompleteness, not unsound:
- A `str` control (`s.strip() == s.strip()`) fails in typed too, as Unknown.
- The corpus PASS verdict is the default model's.

Census rows for 10141-10144 were made with `_census_row`, not `--append-new`, and appended to
`bin/refusal-witness-census.tsv`.

The #610 guard was also checked at emission level. With a `Callable` parameter named `Path`, no
`ext_path_of_str_op` is emitted (`scratchpad/lvX/ev/callable_param_purity.py`).

### Finding (pre-existing, not fixed, out of scope)

A `Callable[[str], int]` parameter is lowered as a PURE logic function (`path: string -> int`,
`let function`). So `Path(s) == Path(s)` with a stateful callable (an `itertools.count` lambda)
PROVES `\result == True`, while CPython gives False.

This is a soundness gap in the Callable model, independent of the Path model. The evidence is
`scratchpad/lvX/ev/callable_param_purity.py`, whose emission is in `scratchpad/lvX/w1/` from the
first 10143 draft. It is not committed as a corpus witness, because it would be an XPASS.

## Stub 2 `SertopSession.type_of_batch`: still `\trusted` (not attempted, measured reason)

Link 1 (the `Optional[Path]` dataclass field `cwd` as `option string`) cannot be built inside the
brief's file limits.
- The record field type is decided in `module6_whyml/preamble.py`, at the record emitter's
  `elif ftype == "option":` branch (line 9180).
- That branch gives `option string` / `option emit_ir` only under the
  `_mutable_state_classes` / `_uses_ir_node_param` gate, and collapses every other `Optional`
  field to `int`.
- A probe confirms that even an `Optional[str]` dataclass field is `int` today:
  `scratchpad/lvX/q/dc1.py` emits `type s = { mutable a: int; mutable b: int; mutable c: int }`.
- The current mirror `sertop.mlw` has `mutable cwd: int` (`scratchpad/lvX/s0/sertop.mlw`).

The brief forbids touching `preamble.py` (lvW works there). So link 1 is blocked, and link 2 (the
emitter-wide `Optional[str] = None` default fill) was not started: alone it converts nothing.

To unblock it, a run with `preamble.py` access needs two things:
- widen that gate for a `str`/`Path` `value_type`, either per class or for dataclass fields;
- have Module 5 give `Optional[Path]` the `value_type` "string".

Both changes are corpus-visible: three corpus files carry `Optional` fields.

## Counts

- `\trusted` (count-trusted-directives, grep-substring): 367 -> 366; markers 338.
- Proof-axiom ledger: 3, unchanged (no axiom added).
- No new `#@ \trusted`.
