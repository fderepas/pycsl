# 12-0015-convergence-gap-18 — STDLIB-AGENT gap: field+\old+param method ensures don't reach the delegate val

**Loop:** `config/skills/pycsl-stdlib-coverage`, gap-17 Brick 5 (the sys_open REOPEN FRAME).
Module `pure_lib/os/`. Discovered while landing the reopen frame; blocks Brick 6 (flip the
content round-trip).

## Context
gap-17 write-side is committed (HEAD `6ed1cf4`): `sys_write` exports the SIZE post-state
`inode_size(disk,fd_inode[fd]) >= len(data)` and the namespace frame
`\forall q; dir_lookup(disk,5,q)==\old(dir_lookup(disk,5,q))`, both proven and propagated to the
`write()` wrapper (the previous tool fix — spec-17 — added the quantifier-bound-var case to the
field-`\old` ensures classifier + the lookup_frame trigger). The last rung is `sys_open`'s reopen
frame: on a present-name open (the O_RDONLY reopen) the body writes NO disk byte, so it preserves
every inode SIZE and every name's resolution. Added to `sys_open` (riding its existing
fd-resolution-fidelity trust; body-faithful — present path mutates only the fd table) and to the
`open()` wrapper:
```
#@ ensures (dir_lookup(\old(self.disk), 5, pathname) >= 0) ==> (\forall ino: int; inode_size(self.disk, ino) == inode_size(\old(self.disk), ino))
#@ ensures (dir_lookup(\old(self.disk), 5, pathname) >= 0) ==> (\forall q: str; dir_lookup(self.disk, 5, q) == \old(dir_lookup(self.disk, 5, q)))
```

## THE GAP — `field + \old + param` method ensures are silently dropped from the abstract delegate
The public `open()` wrapper delegates to the abstract `val _filesystem_sys_open_2` (the lowering of
the `_filesystem.sys_open(...)` module-global method call). The delegate's `val` ensures are built by
the classifier maps in `src/pycsl/module6_whyml/functions.py`
(`_build_method_field_result_ensures_map`, the param+result variant, and
`_build_method_field_old_ensures_map`). Empirically (confirmed by the stdlib-agent):
- `field + param + \result` (no `\old`) → propagates (e.g. gap-14 `dir_lookup(self.disk,5,pathname) < 0`
  IS on the delegate, line 27 of the emitted `__init__.mlw`).
- `field + \old` (no param) → propagates (the spec-17 fix; the write-side `\forall q` frame with NO
  param is on the `sys_write` delegate).
- **`field + \old + param` → DROPPED.** The reopen frame's guard
  `dir_lookup(\old(self.disk),5,pathname) >= 0` references BOTH `\old(self.disk)` AND the param
  `pathname`. `_build_method_field_old_ensures_map`'s `classify` REJECTS any param `Var` leaf, so the
  whole clause is excluded from the delegate `val`. The clause IS present on the full method
  `val unixinodefilesystem__sys_open`, but the WRAPPER calls the trimmed delegate — which has nothing
  to copy — so the wrapper's two frame postconditions are unprovable.

## Symptom (full `pycsl pure_lib/os/__init__.py`)
1238 Valid, **2 unproven — both `Postcondition of goal open'vc`** (the wrapper):
- `inode_size` reopen frame → Unknown (845 144 steps),
- `dir_lookup` reopen frame → Timeout (30s, 7 458 071 steps).
chmod (3 sub-goals) and write (4 sub-goals) all Valid — the regression is confined to the two new
open-wrapper frame ensures. `--fun` is NOT diagnostic here (it trusts callees as bare vals); only the
full run shows it.

## Empirical confirmation of the root cause
Dropping the param antecedent (making the clauses param-free `\old`+field) → both frame clauses DID
appear on `_filesystem_sys_open_2`. Re-adding the `...pathname...` guard → dropped again. The param
reference is the precise, sole blocker. (The param-free form is UNSOUND — the frame is false on the
O_CREAT-of-absent path, which DOES change the created inode/name — so the guard is required.)

## Root cause (file:line)
`src/pycsl/module6_whyml/functions.py` — `_build_method_field_old_ensures_map`'s `classify` helper
admits field-subscript leaves and `\old(...)` but REJECTS any bare/param `Var`. The sibling
param+result map already shows the fix shape: it RENAMES param Vars to the positional `x_i` of the
delegate signature. The `\old` map needs the same param→`x_i` renaming so a clause that is
field + `\old` + param reaches the delegate.

## Proposed fix (for the tool-agent's spec)
Extend `_build_method_field_old_ensures_map` to ACCEPT param `Var` leaves and rename them to the
delegate's positional parameter names (`x0`, `x1`, …) — exactly as the param+result map already does —
so `field + \old + param` clauses are emitted on the delegate `val`. Do NOT change the logical content
of any clause; this is purely making an existing (and already body-faithful, already on the full-method
val) ensures REACH the delegate the wrapper calls.

## Gate (independent, by the coordinator)
- [ ] `pycsl pure_lib/os/__init__.py` → 0 unproven (both open-wrapper frames Valid; chmod/write stay Valid).
- [ ] byte-diff sweep both-ways vs HEAD `functions.py` → corpus byte-identical (the new param case fires
  ONLY for a method whose field+old ensures references a param — confirm no corpus file regresses).
- [ ] `\trusted` count unchanged; no model weakening.
