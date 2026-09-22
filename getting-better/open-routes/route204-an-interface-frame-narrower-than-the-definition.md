# Route #204 — an `#@ interface assigns` narrower than the definition's

**Status:** CLOSED (gen #30). SEV-1. A false contract PROVES in an IMPORTER while CPython
disagrees on an argument the precondition admits.

## The witness

Owner (`1707_route204_interface_assigns_narrower_than_definition.py`, expected FAIL):

```python
#@ requires \length(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == 5
#@ interface assigns \nothing
#@ interface requires \length(a) >= 1
def bump(a: List[int]) -> None:
    a[0] = 5
```

Importer:

```python
#@ requires \length(a) >= 1
#@ ensures \result == 0
def caller(a: List[int]) -> int:
    x = a[0]
    bump(a)
    return x - a[0]
```

`\result == 0` **PROVED**. CPython: `caller([1])` is **-4**, and `[1]` satisfies the
precondition.

## Why it is invisible to both vacuity notions

The absurd twin `\result == 999` is REFUSED and the shipping non-vacuity gate stays
silent, because the caller's context is SATISFIABLE: the narrow frame says `a[0]` is
unchanged, the inherited definition `ensures` says `a[0] == 5`, and together they merely
force "the element was already 5". A context that is consistent-but-false is exactly what
a frame lie produces, and neither CONTEXT vacuity (the shipping gate) nor CLAIM vacuity
(`bin/check-claim-vacuity.py`, built the same day) can see it.

## Where it came from

`module6_whyml/functions.py::_emit_narrowing_vc` documents what it proves:

    ensures:  forall params result. def_requires -> def_ensures -> iface_ensures
    requires: forall params. iface_requires -> def_requires

Read as a checkable claim, that lists TWO clause kinds. Module 5 carries a THIRD —
`interface.assigns` — into the IR, and `functions.py` hands it to importers as the val's
frame. Nothing proved it was a weakening.

## The repair

A refusal at the IR seam in `pycsl.py::_run_pipeline`, beside route #200's, keyed on an
`interface.assigns` that omits a definition `assigns` target. Code `PYCSL-SEM-IFACE-FRAME`.
The rule: **an interface frame may claim MORE writes than the definition, never fewer.**

**Placement was measured, not assumed.** The first version sat before `_ir_resolve`, and
the importer still PROVED — the exploit needs two files and the importer is the one that
proves the false thing, so a pre-resolution check sees only the importer's own functions.
Moved to after import resolution, where the owner's narrowed frame is in the IR.

## Controls

`1708_route204_interface_assigns_complete_control.py` (expected PASS) is the same module
with `#@ interface assigns a[0]` — the feature still works. Corpus `0660`, the b-impl
narrowing witness, still proves. Mirror-sync green (the choke point's twin is `\trusted`,
so no mirror edit and no re-proof).
