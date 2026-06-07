# comment.md — review of the `pure_lib/os` + inliner-fix push (origin/main `ecca09d..68ca006`)

**Reviewed:** 2026-06-06, after `git pull`. Range = 10 commits on top of my glossary
commit `ecca09d`. Cross-referenced against `arity.md` (the plan) and the prior reasoning
trace.

```
68ca006 Add verification report: 3920/4198 Valid (93.4%)
8d9f749 Fix os module for inlined verification (93.4% proven)     ← source workarounds
f50484c feat: PyCSL-proven contracts for pure_lib/os module (no \trusted)
0b6b5f4 test: add file write/read round-trip test for pure_lib/os
6026be8 feat: add PyCSL annotations to pure_lib/os module
dfba7a3 feat: implement pure_lib/os module API backed by UnixInodeFileSystem
3992159 feat: improve pure_lib/os inode filesystem specification
757751e feat: add pure_lib/json — pure-Python json using pure_lib/re
7a789fd feat: add pure_lib/re — pure-Python re subset for json
35441ec Fix inliner type errors for module-level global instances ← transpiler fix
```

The arity bug was addressed in **two** places: a transpiler fix (`35441ec`) **and** a set
of source-side workarounds in `pure_lib/os` (`8d9f749`). The first is legitimate; the
second is where the concern is.

---

## 1. `35441ec` — the transpiler fix (Strategy B, partial)

This is the previously-uncommitted in-tree work, now landed. It is the **Strategy B** path
from `arity.md §3` (re-infer types post-hoc in Module 6), not Strategy A (assert at the
inline boundary).

**Genuinely good — keep:**
- `types.py::_field_type_of` extended to resolve `global.<field>`, not just `self.<field>`.
  Necessary and correct for inlined access to a module-global record's array field.
- `ir_inline.py` dotted-receiver freshening (`entries.append` → `entries__inlN.append`).
  Real correctness fix, orthogonal to typing.
- `pycsl.py` importing module-level helper functions from dependency modules (so inlined
  bodies can reference `_unpack_inode` etc.).

**As predicted, it only fixes layer 2a (declaration typing), not 2b (operation selection):**
- `_collect_array_var_assigns` got the array-returning-call arm + a `while changed`
  transitive var-to-var fixpoint + a `seed` — exactly the whack-a-mole `arity.md §2a`
  warned the post-hoc approach would require.
- The `statements.py` change is **one line** — just passing `seed=array_vars`. So the
  abstract-vs-concrete operation selection (`subscript_set (x:int)` vs concrete
  `a[i] <- v` + `Array.length` bounds check, `statements.py:388-460`) is **untouched**.
  Array *mutation* through an inlined body still can't lower correctly. This is precisely
  the layer the reasoning trace stopped at ("…I need the actual array mutation function…
  `Array.set`") and never implemented.

**Process gaps:**
- **No reference-corpus driver** anywhere in the range (`test-suite/corpus/pycsl-reference`
  is untouched). The fix is validated *only* against `pure_lib/os`, contrary to the
  reference-corpus discipline (a language/transpiler change must add a `058x` driver). It
  is therefore ungated — a future refactor can silently regress it.
- No evidence of the emission-identical byte-diff gate, which matters here because
  `types.py`/`statements.py` type **every** function, not just inlined ones.

---

## 2. `8d9f749` — the source workarounds (the concern)

Because 2b was never fixed and other gaps surfaced, the module was deformed to fit the
transpiler. This is exactly the **Block-1 trap** `arity.md §9` said to avoid: trading a
transpiler debt for a *library-faithfulness* debt, which is worse under the project's
extreme-rigor / faithful-semantics philosophy. Specific regressions:

1. **`-> bytes` changed to `-> list`, body unchanged.** `_pack_uint16_be` (and the other
   `_pack_*`) now declare `-> list` but still `return bytes([...])`. The annotation now
   *lies* about the returned value purely to trip PyCSL's array detector. The Python is
   type-incoherent (mypy would reject it). The type annotation is supposed to be ground
   truth, not a lever to steer the transpiler.

2. **`ensures \result >= 0` → `ensures True` on array-returning helpers.** A real
   postcondition replaced with a vacuous one. Several of the 3 920 "Valid" VCs are now
   proving `True`. The 93.4 % headline therefore **overstates assurance** — some of that
   green is contracts that no longer say anything.

3. **`DirEntry.path = '/' + name` → `self.path = name`** — a behavioural change: paths lose
   their leading-slash semantics. And `scandir` now `items.append(inode_num)` instead of
   `DirEntry(...)` (its own new docstring admits "Return an iterator of DirEntry inode
   numbers"). That **breaks the `os.scandir` contract** — scandir must yield `DirEntry`
   objects. The model no longer faithfully reflects real `os` semantics; it reflects what
   the transpiler could currently prove.

4. **`_set_bitmap` rewritten to avoid `~`** (clear-bit via read-mask-subtract). This one is
   a *legitimate* semantics-preserving rewrite and is defensible — but it still papers over
   a real transpiler gap (no bitwise `~`) that should be tracked, not silently absorbed.

5. **`listdir`/`scandir` rewritten to scan the disk directly** instead of calling
   `_read_directory` "to avoid the tuple-in-array limitation." Restructuring a *consumer* to
   dodge a transpiler limitation (tuples in arrays) is the same anti-pattern — the limitation
   is now hidden rather than recorded.

---

## 3. Commit hygiene

`8d9f749` is titled "Fix os module" but contains **35 323 insertions** — it swept in the
entire vendored CPython `lib/` tree (`argparse.py`, `ast.py`, `typing.py`, `inspect.py`,
`subprocess.py`, …), plus `os-call.txt`, `list.txt`. The actual fix is ~70 lines across two
files. A 35k-line "fix" commit is unreviewable and pollutes history; the vendoring should
be its own commit (or `.gitignore`d). Worth untangling before it ossifies.

---

## 4. Credit where due

- 93.4 % Valid (0 Invalid) on a **full inode filesystem** stub with **zero `\trusted`** is a
  substantial result, and the body-verified, no-`\trusted` approach (`f50484c`) is squarely
  in line with the `agent-stdlib-annotate` policy. The `#@ proof rocq/lean` anchoring on the
  irreducible bitmap kernel is the right move.
- The transpiler-side keepers in §1 are real progress on the method-call contract gap (A2c)
  for module-level globals.
- `pure_lib/re` + `pure_lib/json` as pure-Python, dependency-layered stubs is a clean idea.

---

## 5. Recommendations

1. **Fix layer 2b in the transpiler** (operation selection: route an inlined, now-concrete
   array to `Array.set`/concrete subscript, not `subscript_set`). This is the gap that forced
   the consumer rewrites. Until then, array *mutation* through inlining is unsupported and
   should be documented as such.
2. **Back out the faithfulness-deforming source edits** (restore `-> bytes`, real `ensures`,
   `DirEntry`/`scandir` semantics). If they must stay temporarily, mark each with a tracked
   `# TODO(arity): transpiler gap` and state honestly in `report.md` which contracts are now
   vacuous — so the 93.4 % isn't read as 93.4 % *meaningful* assurance.
3. **Add reference-corpus drivers** for the inliner array fix (`arity.md §6`, `0583`–`0586`,
   including a mutation driver for 2b) so the fix is gated, not validated against one module.
4. **Re-run `report.md`** after restoring real specs for an honest assurance number, and add
   the byte-diff gate result.
5. **Split the vendored `lib/` dump** out of the fix commit.
6. Track the smaller transpiler gaps surfaced here as first-class issues: bitwise `~`,
   tuples-in-arrays, and `bytes`/`list` unification (the fact that `-> bytes` isn't treated
   as `array int` is the root of regression #1 — fixing *that* would remove the temptation to
   mislabel return types).

**Bottom line:** the transpiler fix (`35441ec`) is real but half — it closes declaration
typing and leaves operation selection open. The 93.4 % was reached partly by deforming the
`os` model to the transpiler's current shape (vacuous `ensures`, lying return types, a broken
`scandir` contract). Under this project's standards that's debt to pay down, not a result to
lock in — the headline number should be re-derived once the specs are honest again.
