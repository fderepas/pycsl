# 12-0015-convergence-spec-18 — field + \old + param method ensures must reach the abstract delegate

STATUS: DONE

## Problem (from gap-18)
The public `open()` wrapper in `pure_lib/os/__init__.py` delegates to the abstract
`val _filesystem_sys_open_2` — the lowering of the module-global method call
`_filesystem.sys_open(...)`. The delegate's `ensures` are built by the classifier maps in
`src/pycsl/module6_whyml/functions.py`. The sys_open REOPEN FRAME guard

```
(dir_lookup(\old(self.disk), 5, pathname) >= 0) ==> (\forall ino; inode_size(self.disk,ino) == inode_size(\old(self.disk),ino))
(dir_lookup(\old(self.disk), 5, pathname) >= 0) ==> (\forall q;  dir_lookup(self.disk,5,q)  == \old(dir_lookup(self.disk,5,q)))
```

references self-fields (`self.disk`), `\old(...)`, AND the param `pathname`. This
`field + \old + param` combination is handled by NO map and so is DROPPED from the delegate val.
The clause IS present on the full method `val unixinodefilesystem__sys_open`, but the wrapper calls
the trimmed delegate, which has nothing to copy — so the wrapper's two frame postconditions are
unprovable (`open'vc`: `inode_size` frame → Unknown; `dir_lookup` frame → Timeout).

## Root cause (file:line)
`src/pycsl/module6_whyml/functions.py`, `_build_method_field_old_ensures_map` (def at line 932),
its `classify` helper (line 942). The helper allows self-field leaves, `\old(self.f)`, and
quantifier-BOUND vars (spec-17), but REJECTS any other bare `Var` — including a method PARAM. A
clause that mixes a param with `field + \old` is therefore excluded.

The sibling `_build_method_field_param_result_ensures_map` (line 807) already shows the correct
shape for params: it builds `pmap = {p: f"x{i}" for i, p in enumerate(formal_params)}` and
`rename(...)`s each param `Var` to the delegate's positional parameter name `x0`, `x1`, … (the
abstract val is declared with params `(x0: t0) (x1: t1) …`, expressions.py:894). `self` and `x_i`
live in distinct namespaces, so there is no collision.

## Fix
Extend `_build_method_field_old_ensures_map` to MIRROR the param+result map's param handling:

1. `classify` accepts a bare `Var` when its name is a quantifier-BOUND var (keep as-is, spec-17)
   OR a method PARAM (allow). Only a free LOCAL var (neither bound nor a param) is still rejected.
   Same for `ArrayLen` over a param.
2. After classify, RENAME each param `Var` to its positional `x_i` using the SAME `pmap`
   (`{p: f"x{i}" for i, p in enumerate(formal_params)}`) and a `rename` walk identical to the
   param+result map. Bound vars are NOT in `pmap`, so they are left untouched.

No clause's logical content changes — this purely makes an existing, body-faithful, already-on-the-
full-method ensures REACH the delegate the wrapper calls.

## Exact edit
`src/pycsl/module6_whyml/functions.py`, `_build_method_field_old_ensures_map`:
- `classify`'s `Var` case: `return None if (name in bound or name in params) else False` — thread the
  method's `params` set in alongside `bound`.
- `ArrayLen` case: also allow a var that is a param.
- Add a `rename` helper (copied from the param+result map) and, in the `out` loop, build
  `pmap`/`pset` from `func["formal_params"]` and `rename(e, pmap)` each kept clause.

## Gate
1. FULL run `pycsl pure_lib/os/__init__.py` → Valid count >= 1238 AND
   `grep -iE 'Unknown|Timeout|FAILED|INCOMPLETE|unproven'` EMPTY (the two `open'vc` frames now Valid;
   chmod and write stay Valid).
2. Corpus byte-diff sweep both-ways vs HEAD → BYTE-IDENTICAL (the new param case fires ONLY when a
   method's field+old ensures references a param; the corpus has none, so emission is unchanged).
3. `\trusted` count unchanged; no model weakening.
