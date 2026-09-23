# FINDING (#49, gen #31) — a cross-GROUP `#@ verify_module` call emits a `use`-less qualified name

**STATUS: FOUND, MEASURED AND CLOSED IN THE SAME SESSION.** Not a soundness route — an
EMISSION defect that fails loudly. The repair, the witness (`1844`), the negative twin
(`1845`) and the mutual-recursion driver (`1846`) landed together; see the CLOSURE section
at the end.

## THE CLAIM

`test-suite/annotations.md` row 29: a method tagged `#@ verify_module <name>` is emitted
into its own Why3 `module`, and

> A cross-module `self.<m>(...)` call (**a sibling in a different `verify_module` group**,
> or the flat default module) is lowered to the **proven** contract of the callee via Why3
> module `clone`-refinement … i.e. a PROVEN cross-module interface, **never** an
> assumed-`val` boundary.

The parenthesis names two cases. **The second works. The first does not.**

## THE MEASUREMENT

One class, two methods, `--memory-model hoare`:

| variant | result |
|---|---|
| `leaf` in `#@ verify_module LeafMod`, `caller` in the FLAT default module | **verifies** — and claiming `\result >= 7` (the body's value, not the contract's `>= 0`) correctly FAILS, so the boundary does convey the contract |
| `leaf` in `#@ verify_module Leaf`, `caller` in `#@ verify_module Top`      | **`unbound function or predicate symbol 'LeafSig.c__leaf'`** |

Reading the emission makes the cause a single missing line. The flat module gets its
imports:

```whyml
module PyCSL_Program
  use Shared
  use LeafModSig                          (* <-- emitted *)
  let c__caller (self: c) : int … = (LeafModSig.c__leaf self)
```

and a GROUP module does not:

```whyml
module Top
  use Shared                              (* <-- and nothing else *)
  let c__caller (self: c) : int … = (LeafSig.c__leaf self)     (* unbound *)
  clone TopSig with val c__caller = c__caller
```

`Module6_WhyMLTranspiler.py` emits `use {g}Sig` for every group **only into
`PyCSL_Program`** (the `for g in sorted(groups): main.append(f"  use {g}Sig")` loop). The
per-group provider module is built from `self._shared_use_lines()` alone, so a call site
that the expression layer correctly rewrote to `LeafSig.c__leaf` names a module the
enclosing module never imported.

## WHY THIS IS NOT A ROUTE

Why3 rejects the file. Nothing is proved, nothing is assumed, and the failure is total
rather than silent. The TCB is unchanged.

## THE FIX, AND ITS ONE STRUCTURAL CONSTRAINT

Give each provider module `use <Other>Sig` for every other group. The one thing that
cannot stay as it is: the emitter currently appends `Sig_g` and `Prov_g` **interleaved**,
group by group (`out_modules` = shared, LeafSig, Leaf, TopSig, Top), so `Top` cannot
`use LeafSig` if `Leaf` sorts after `Top` — Why3 requires a module to be defined earlier in
the file than its use. Emitting **all** `<G>Sig` modules first and **then** all provider
modules removes the constraint entirely, and it is safe because a `Sig` module is bodyless
`val`s over `Shared` and can never depend on a provider. Cyclic groups then cost nothing:
`use` edges run provider → Sig only, and the Sig layer is acyclic by construction.

## BLAST RADIUS, MEASURED BEFORE ANY FIX IS ATTEMPTED

`#@ verify_module` occurs in **zero** corpus files and in exactly one library source,
`src/pycsl_lib/os/UnixInodeFileSystem.py` (`ReadMod`, `FindSlotMod`, `FindFreeMod`). Any
repair here is corpus-byte-inert by construction; the whole of its observable effect is on
that one file and on programs nobody has written yet. That is also why the defect survived:
the single real user's three groups did not happen to call each other across the boundary
the directive exists to create.

A separate, smaller defect found in the same probe — a LOWERCASE group name emitting
`module leafSig`, which Why3 rejects with an error naming a symbol the user never wrote —
is already repaired, with witness `1842` and control `1843`.

Measured 2026-09-23. Files: `$SCRATCH/g31/vm/{vm2_s,vm3_s}.py` and their `.mlw`.


---

## CLOSURE (same day)

**Repaired.** `_transpile_modular` now emits **all** `<G>Sig` modules first and **then** all
providers, and each provider carries `use <Other>Sig` for every other group (its own is
excluded — the trailing `clone {g}Sig` is what binds that one, and `use`ing it as well
would shadow the real `let` the module is defining).

Measured, the same two-method class that produced the finding:

| file | before | after |
|---|---|---|
| `1844` — `leaf` in `LeafMod`, `caller` in `TopMod`, claiming `\result >= 0` | `unbound function or predicate symbol 'LeafModSig.c__leaf'` | **verifies** |
| `1845` — the same file claiming `\result >= 7` (the BODY's value) | (could not emit) | **FAILS**, as it must: the boundary conveys the contract, not the body |
| `1846` — `Amod` and `Bmod` calling EACH OTHER | `unbound function or predicate symbol 'BmodSig.c__b_leaf'` | **verifies** |

`1846` is the reason the repair is a REORDERING rather than a topological sort of the
groups: a sort would have to fail on mutually-calling groups, and after the split there is
nothing to fail on — the `use` edges run provider → Sig only and the Sig layer is acyclic
by construction.

The corpus is byte-inert: `Module6_WhyMLTranspiler` takes this path only when some
non-`\trusted`, non-`\abstract` function carries `verify_module`, and no corpus file does.
Confirmed by sweep rather than by that argument alone.

**STILL OPEN, AND SEPARATE.** `src/pycsl_lib/os/UnixInodeFileSystem.py` — the one real user
— still fails, and with a DIFFERENT symbol: `unbound function or predicate symbol
'dir_find_free_prefix'`. That is the axiom-isolation path (a `#@ proof`-cited symbol not in
scope inside a group module), not the call path this finding is about, and it failed
identically before and after the repair. It wants its own probe.
