STATUS: DONE

# 11-2325-convergence-spec-17 — TOOL-AGENT spec: trigger the `UnixFs.Dir.lookup_frame` axiom

**Gap input:** `11-2325-convergence-gap-17.md`. **Owner surface:** `src/pycsl/` only.

## Root cause

`src/pycsl/module6_whyml/preamble.py`, the `_AXIOM_REGISTRY["UnixFs.Dir.lookup_frame"]`
entry (preamble.py:287–291 pre-edit). The registered Rocq+Lean-cross-validated axiom is
emitted (via `_emit_preamble_axioms` / `_emit_class_inv_axioms` as `axiom <name> : <body>`)
as a **module-global** Why3 axiom in scope for every goal in the file, with **NO E-matching
trigger**. Its antecedent is the bounded slot frame
`( forall k. 0 <= k < 16 -> slot_inode d1 5 k = slot_inode d0 5 k )` (+ the `slot_name` twin).
That pattern matches the slot-frame `#@ assert`s carried by EVERY other block-5-touching
syscall, so the solver instantiates `lookup_frame` on goals unrelated to name resolution and
then chases its conclusion `dir_lookup d1 5 name = dir_lookup d0 5 name` for unconstrained
`name`. Two failures in the full `pycsl pure_lib/os/__init__.py` run (baseline 0 unproven):

1. **`chmod'vc` Assertion Timeout** (30.00s, ~4.0M steps) — REGRESSION. `sys_chmod`'s
   directory-uniqueness slot-frame asserts are exactly the axiom's antecedent shape; chmod
   needs no dir_lookup frame at all but the global axiom fires and blows up.
2. **`write'vc` Postcondition Unknown** (~390k steps) — the `write()` wrapper's namespace
   frame `\forall q; dir_lookup(disk,5,q)==\old(dir_lookup(disk,5,q))` won't propagate across
   the bare `return _filesystem.sys_write(...)` delegation.

## Fix

Add a Why3 **multi-pattern E-matching trigger** to the axiom's outer quantifier so it
instantiates ONLY when both `dir_lookup` applications of its conclusion are present — i.e. on
a genuine namespace-frame goal (the write wrapper) and never on a bare slot-frame assert
(chmod, which has no dir_lookup pair). The trigger binds `d0`, `d1`, `name`. The LOGICAL
content is unchanged — only the trigger annotation is added.

Why3 syntax verified to parse (`/tmp/trig_test_a.mlw`, `why3 prove` exit 0): comma-separated
binders of differing types in one `forall`, with the `[...]` trigger list directly after the
binder list and before the `.`:

```
forall d0 : array int, d1 : array int, name : string
  [dir_lookup d1 5 name, dir_lookup d0 5 name].
  ( forall k : int. 0 <= k < 16 -> slot_inode d1 5 k = slot_inode d0 5 k ) ->
  ( forall k : int. 0 <= k < 16 -> slot_name  d1 5 k = slot_name  d0 5 k ) ->
  dir_lookup d1 5 name = dir_lookup d0 5 name
```

## Exact edit

`src/pycsl/module6_whyml/preamble.py`, `_AXIOM_REGISTRY["UnixFs.Dir.lookup_frame"]`: the
former three separate `forall d0. forall d1. forall name.` binders become one comma-separated
binder list carrying the trigger `[dir_lookup d1 5 name, dir_lookup d0 5 name]`. An
explanatory comment above the entry records the trigger and why. No `_AXIOM_FUNCTIONS` /
`_CLASS_INV_AXIOMS` / cross-check changes (same symbols, same citation).

## Gate

1. FULL run: `pycsl pure_lib/os/__init__.py` → Valid count >= 1229 AND zero
   `Unknown|Timeout|FAILED|INCOMPLETE|unproven` (chmod and write both Valid).
2. Corpus byte-diff both-ways vs HEAD preamble → BYTE-IDENTICAL (corpus has no os/dir_lookup
   references, so the with-trigger emission must equal HEAD's no-entry emission).
3. `\trusted` count unchanged (7); proof cross-check still maps the citation to
   `LookupFrame.{v,lean}`.

## Addendum — the trigger was necessary but NOT sufficient (second tool fix)

After the trigger, `chmod'vc` returned to Valid (the global axiom no longer fires on bare
slot-frame asserts), but `write'vc`'s namespace-frame postcondition (line 1501 of the emitted
`pure_lib/os/__init__.mlw`: `forall q. dir_lookup(disk,5,q) == old(dir_lookup(disk,5,q))`)
remained Unknown (~344k steps). Root cause: the wrapper `write()` calls the module-global
instance method `_filesystem.sys_write(...)`, which is lowered to the abstract `val
_filesystem_sys_write_2` (`module6_whyml/expressions.py:803+`). Its ensures are propagated
from the `_module_method_field_old_ensures` map, built by
`_build_method_field_old_ensures_map` (`module6_whyml/functions.py:932`). That map's `classify`
helper rejected ANY bare `Var` leaf — including a quantifier-BOUND variable. The frame
`forall q; dir_lookup(self.disk,5,q) == \old(...)` is a self-field mutating contract whose `q`
is universally bound, so `classify` wrongly disqualified it and the abstract `val` shipped
WITHOUT the namespace frame — the wrapper had nothing to copy.

Second edit (`module6_whyml/functions.py`, `classify`): thread a `bound` frozenset of
quantifier-binder names; on a `Forall`/`Exists` node, extend `bound` with its `var` and
classify the body; a `Var` leaf is allowed iff its `name` is in `bound` (otherwise still
rejected as a caller-visible param/local). This admits quantified self-field frames into the
field-old map; the existing `_dotted_ensures_suffix` already renders `Forall` clauses. The
byte-diff stays identical (no corpus method has a quantified self-field `\old` frame).

Final gate result: `pycsl pure_lib/os/__init__.py` → 1238 Valid, 0 unproven (chmod Valid,
write Valid incl. the namespace frame at ~34.8k steps); corpus byte-diff BOTH-WAYS BYTE-
IDENTICAL across both edited files.
