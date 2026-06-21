# os return-code → OSError: FULL conversion (every fallible function) — STATUS

**Branch:** `os-exception-rootcause` (working tree; STOP-AT-PROPOSAL — nothing committed/pushed).
**Builds on:** `20260620-2357-FIX1-DONE-os-conversion-STATUS.md` (Fix 1 hierarchy + mkdir/rmdir/stat PoC).
**Re-verify before merge** — exact commands below. Every claim here is a reproducible machine verdict.

---

## HEADLINE

**23 / 23 fallible os functions converted; open = DONE (raises FileNotFoundError/OSError, no `-1`).**

Every fallible `os.*` function now RAISES `OSError` (or the precise subclass) on its documented
failure instead of returning `-1`. The module proves **`Verification SUCCESS`, 0 non-Valid, 0
`\trusted`**. The pre-existing module-level non-vacuity flag was **NARROWED, not widened**:
baseline `{listdir, lseek, scandir}` → after `{lseek}`. All 19 `formal_os_*.py` tests are green.
A CPython differential oracle confirms model⇄CPython agreement for all 23.

---

## 1. Per-function ledger (against the mission's EXPLICIT list)

### MUST convert (were returning `-1`) — 16/16 DONE

| function | failure raise | precise subclass | `-1` gone | proves |
|---|---|---|---|---|
| open     | FileNotFoundError (ENOENT) / OSError | **yes** (ENOENT discriminant is the same branch) | yes | ✓ |
| close    | OSError (EBADF) | generic | yes | ✓ |
| read     | OSError (EBADF) | generic (CPython OSError too) | yes | ✓ |
| write    | OSError (EBADF/ENOSPC) | generic | yes | ✓ |
| chmod    | OSError | generic (CPython FileNotFoundError IS-A OSError) | yes | ✓ |
| dup      | OSError (EBADF/EMFILE) | generic | yes | ✓ |
| fstat    | OSError (EBADF) | generic | yes | ✓ |
| lstat    | **FileNotFoundError** | **yes** (dir_lookup<0 discriminant) | yes | ✓ |
| link     | OSError | generic | yes | ✓ |
| unlink   | OSError | generic | yes | ✓ |
| remove   | OSError | generic | yes | ✓ |
| makedirs | OSError | generic | yes | ✓ |
| rename   | OSError | generic | yes | ✓ |
| symlink  | OSError | generic | yes | ✓ |
| readlink | OSError | generic (CPython OSError too) | yes | ✓ |
| truncate | OSError | generic | yes | ✓ |

### Add a raising failure contract (fallible, previously NO failure path) — DONE

| function | failure raise | notes |
|---|---|---|
| lseek    | OSError (EBADF/EINVAL) | success ensures (SEEK_SET offset) preserved |
| listdir  | OSError (absent / not-a-dir) | the failure `return []` paths now `raise OSError` |
| scandir  | OSError (absent / not-a-dir) | same |
| pread    | OSError (EBADF) | wrapper checks `fd>=64 or fd_open[fd]==0` before delegating; EOF `b''` preserved |

### mkdir / rmdir / stat — already DONE in the prior PoC (unchanged here)

### Assessed extras (mission's "convert if spec documents OSError failure AND modelled")

| function | decision | why |
|---|---|---|
| getxattr, listxattr | LEAVE (logged) | pure no-op STUBS returning 0; NO modelled state interaction and NO failure branch — there is no `-1` to remove and no modelled failure condition. Converting would require first MODELLING xattr state (out of mission scope). FLOOR n/a (never returns `-1`). |
| chflags             | LEAVE (logged) | same — no-op stub returning 0, no modelled failure path. |
| copy_file_range     | LEAVE (logged) | same — no-op stub returning 0, no modelled fd/byte transfer. |
| _kill / kill        | LEAVE (logged) | no-op stub returning 0; the process table is not modelled, so there is no ESRCH/EPERM failure condition to discriminate. FLOOR n/a. |

These four are honestly out of FLOOR scope: the FLOOR is "do not leave a `-1` in a fallible function."
None of them returns `-1` — they are non-failing no-op stubs. They are flagged here as residuals to
revisit once their underlying resource is actually modelled (then they become fallible and must raise).

### LEAVE, documented (per the mission)

- `access` — returns bool (0/1) per spec; does NOT raise. UNCHANGED. (os.access genuinely returns False.)
- `islink` — returns bool per spec; stub returns 0. UNCHANGED.
- `getcwd, getpid, getenv, get_exec_path, fspath, fsdecode, fsencode, walk` — non-fallible. UNCHANGED.

---

## 2. FLOOR check (non-negotiable): NO `-1` left in any fallible function

```
grep -cE "return -1|== -1" src/pycsl_lib/os/__init__.py    # => 0
grep -ci trusted          src/pycsl_lib/os/__init__.mlw    # => 0
```
**0 `-1` returns and 0 `-1` ensures remain in the os wrapper.** Every fallible function raises.

---

## 3. Non-vacuity vs the PRE-EXISTING baseline — NARROWED, not widened

The os module's `--check-vacuity` is a KNOWN pre-existing module-level failure (the documented
nonlinear-integer-division module context, `getting-better/csys-vacuity-investigation/ROOT-CAUSE.md`).
The mission rule: report it, do not ship vacuous green, and do NOT let the conversion WIDEN the flagged set.

- **BASELINE (PoC tree, before this run):** flagged `{listdir, lseek, scandir}` (3).
- **AFTER raw conversion (intermediate):** flagged `{fstat, lseek, pread, read}` — this WOULD have widened
  the set (fstat/read/pread newly vacuous). ROOT CAUSE diagnosed: the raising wrappers were INLINING
  their int-returning kernel `sys_*` bodies, which imported the `inode_size`/`block_content_eq`
  nonlinear-div facts into the wrapper's normal-return context and tipped it vacuous.
- **FIX (zero-trust, sound):** marked `sys_fstat`, `sys_read`, `sys_pread` (and `sys_close`, `sys_truncate`
  for the unit-clash, see §5) `#@ no_inline` — the modular-verification boundary keeps each wrapper's
  context just the kernel post-state + the raise guard. This is the SAME sound mechanism os already uses
  (sys_open/sys_write). It adds no trust (a false ensures fails the callee, not the caller).
- **AFTER FIX (final, stable across two runs):** flagged `{lseek}` (1) — **strictly NARROWER than baseline.**

`lseek` remains vacuous (it was ALSO in the baseline). It cannot be de-inlined: its SEEK_SET success
ensures (`\result == pos`, `fd_offset[fd] == pos`) need the inlined body; marking `sys_lseek` no_inline
makes those postconditions Timeout/Unknown. So `lseek` stays a PRE-EXISTING, logged module-level GAP
(the nonlinear-div vacuity), routed to the human — NOT introduced or widened by this conversion.

```
PYTHONHASHSEED=0 PYTHONPATH=src/pycsl .venv/bin/python -m pycsl \
    src/pycsl_lib/os/__init__.py --check-vacuity --vacuity-timelimit 10
# => GATE FAILED on {lseek} only (pre-existing; baseline was {listdir,lseek,scandir})
```

---

## 4. CPython differential oracle (ROOT-CAUSE Fix 2b) — WIRED and PASSING

New harness `bin/os-cpython-differential.py` runs the SAME documented FAILURE inputs (absent path,
bad fd, existing dir for mkdir, …) against REAL CPython `os` and asserts model⇄CPython agree that
each fallible function raises an OSError-or-subclass.

```
python3 bin/os-cpython-differential.py
# [+] DIFFERENTIAL FLOOR PASSED: model and CPython agree that every fallible os
#     function raises an OSError-or-subclass on its documented failure input.
```
- **23/23 PASS the floor.** 11 have PRECISE subclass agreement (open/close/read/write/pread/lseek/
  dup/fstat/stat/lstat/readlink); 12 use generic OSError where CPython raises the precise subclass
  (FileExistsError/FileNotFoundError) — still caught by `except OSError` via the Fix-1 hierarchy.
- The precise-subclass gap for the 12 generic ones is the documented kernel-discriminant cost
  (refining mkdir/rmdir to FileExistsError needs a cheaper kernel errno than the collapsed `-1`,
  per the prior STATUS §2.1). It is a FLOOR-compliant deferral (generic OSError, not `-1`).

---

## 5. Tool change (gated, byte-identical) + stdlib `no_inline` adds

**Tool fix — `src/pycsl/module6_whyml/stmt_control_flow.py` (`_handle_return_stmt`):** a latent emitter
bug. A `string`-element list returned at the TAIL (non-raise) position of an `array string`-returning
function wrongly emitted the int `materialize` (`seq int -> array int`) instead of `materialize_str`,
failing L3 type-check. It was masked until now because `os.listdir`/`scandir` had early `return []`
paths (→ `use_raise` True → correct `Return_seq_str`/`materialize_str`); converting their failure paths
to `raise OSError` removed the early returns, exposing the tail path. Fix: the tail seq-local return now
checks `_func_return_type == "array string"` and uses the string bridge (mirroring the already-correct
`use_raise` path). **Gated:** corpus byte-diff sweep over 605 files = **0 differences** (the fix only
affects the previously-FAILING string-list-tail case); corpus 0383 still SUCCESS.

```
bash bin/byte-diff-sweep.sh /tmp/bd_baseline   # tool fix stashed
bash bin/byte-diff-sweep.sh /tmp/bd_withfix    # tool fix applied
diff -rq /tmp/bd_baseline /tmp/bd_withfix       # => (no output) 0 differences
```

**Stdlib `#@ no_inline` adds — `src/pycsl_lib/os/UnixInodeFileSystem.py`:** `sys_close`, `sys_truncate`
(unit-clash: inlining an int-returning `return` into a None-returning raising wrapper clashed the
`Return` exception with the unit result), and `sys_fstat`, `sys_read`, `sys_pread` (vacuity: see §3).
All sound modular boundaries (no trust added); the os module still proves SUCCESS with 0 `\trusted`.

---

## 6. Formal-test migration — all 19 `formal_os_*.py` green on the exception model

The tests that rode the `-1`/return-code model were migrated to the exception contract (e.g. open's
`dir_lookup<0 ==> result==-1` ENOENT discriminant became `try open(absent) except OSError: return 1`;
`rc = close(fd); if rc != 0` became `close(fd)`; presence/absence consequences now prove
UNCONDITIONALLY since the success-path `dir_lookup` views are no longer guarded by `\result == 0`).

```
for f in src/pycsl_lib_test/formal_os*.py; do
  PYTHONHASHSEED=0 PYTHONPATH=src/pycsl .venv/bin/python -m pycsl "$f"; done
# => all 19 report Verification SUCCESS
```
Honest residual value-gaps kept (NOT weakened to vacuous): `truncate` size-field and `chmod` mode-field
consequences have no name-keyed accessor at the os.* layer, so those tests assert name-presence via
`access` instead; `readlink`/`fstat` keep the range/geometry bound (no content/inode accessor).

---

## 7. Patch surface (working tree, uncommitted)

```
src/pycsl/module6_whyml/stmt_control_flow.py   (tool: array-string tail-return materialize_str fix; byte-diff 0)
src/pycsl_lib/os/UnixInodeFileSystem.py        (no_inline: sys_close/sys_truncate/sys_fstat/sys_read/sys_pread)
src/pycsl_lib/os/__init__.py                    (16 -1->raise conversions + 4 raising failure contracts)
src/pycsl_lib_test/formal_os_{close,dir,enoent,listing,meta,namespace,namespace2,query,roundtrip,symlink}.py
                                                (migrated to the exception model — all SUCCESS)
bin/os-cpython-differential.py                  (NEW: ROOT-CAUSE Fix 2b external oracle — PASS)
```

## 8. Reproduce (all)

```
# module proof (SUCCESS, 0 trusted)
PYTHONHASHSEED=0 PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/pycsl_lib/os/__init__.py
grep -ci trusted src/pycsl_lib/os/__init__.mlw                       # 0
grep -cE "return -1|== -1" src/pycsl_lib/os/__init__.py              # 0
# non-vacuity (flagged {lseek} only — narrower than baseline)
PYTHONHASHSEED=0 PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/pycsl_lib/os/__init__.py --check-vacuity --vacuity-timelimit 10
# CPython differential oracle
python3 bin/os-cpython-differential.py
# all formal tests
for f in src/pycsl_lib_test/formal_os*.py; do PYTHONHASHSEED=0 PYTHONPATH=src/pycsl .venv/bin/python -m pycsl "$f"; done
# tool byte-diff gate (0 differences over 605 files)
bash bin/byte-diff-sweep.sh /tmp/bd_withfix
```

## 9. DONE vs OPEN

- **DONE (machine-verified):** all 16 MUST + 4 add-failure-contract conversions; module SUCCESS / 0
  `\trusted`; FLOOR met (no `-1`); vacuity NARROWED to `{lseek}`; CPython differential 23/23 PASS;
  19 formal tests green; tool fix byte-diff 0.
- **OPEN / routed to the human (honest GAPs, NOT closed):**
  1. `lseek` module-context nonlinear-div vacuity — PRE-EXISTING (in the baseline `-1` model), not
     widened; cannot de-inline without losing the SEEK_SET offset consequence. (csys-vacuity-investigation.)
  2. Precise FileExistsError/FileNotFoundError for the 12 generic-OSError functions — needs a cheaper
     kernel errno discriminant (prior STATUS §2.1). FLOOR-compliant deferral (generic OSError, not `-1`).
  3. getxattr/listxattr/chflags/copy_file_range/_kill — no-op stubs; become fallible (and must raise)
     only once their underlying resource (xattr table / process table) is modelled.
```
