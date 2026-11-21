# ROUTE #144 — a `@dataclass`'s `init_params` was built from THIS class's `AnnAssign`s only

**Status: CLOSED AND FULLY GATED by gen #28 (2026-09-16), commit in battery A.**
Severity 1. Found by gen #27 (deferral-audit), repaired and gated by gen #28.
Witnesses `1424 1425 1426 1427 1443` (XFAIL) and `1433 1434 1435 1436 1437 1438` (PASS).

## The deferral that hid it

`src/pycsl/frontend/module5/construction_synth.py:355-358` deferred a past-arity field to
`_call_record_constructor`, whose own justification (`module6_whyml/expressions.py:12694`)
is the premise that fails:

> *"an OVER-arity call (a Python error) binds nothing (all defaults — fail-closed, never a
> false full binding)."*

**`len(args) > len(init_params)` is a Python error only when `init_params` really IS the
constructor's parameter list.** For a `@dataclass` it was not.

## The shapes, all measured PROVING at `2887ba44` with CPython contradicting

  - **A (1424)** a DERIVED `@dataclass`: `construction_synth.py` synthesized `init_params`
    from this class's own `AnnAssign`s and `ir_resolve.py:2298` merged `fields`,
    `class_invariants`, `field_defaults` and `constants` — **and not `init_params`**. A
    legal `C(1, 2)` on `class C(B)` looked over-arity, bound nothing, and every field took
    `_field_default`'s definite integer. `\result == 0` PROVED; CPython 2.
  - **B (1425)** a `ClassVar` member is an `ast.AnnAssign` and entered `init_params`
    although Python's `@dataclass` skips it (PEP 557 pseudo-field), so the positional
    binding was OFF BY ONE and every field took its NEIGHBOUR's argument — a definite
    WRONG value, not a lost default. `\result == 2` PROVED; CPython 1.
  - **C (1427)** the donor base is a `@dataclass` that ALSO writes an explicit `__init__`.
    `dataclasses._set_new_attribute` never overwrites a class attribute, so that
    `__init__` wins for the BASE — but `__dataclass_fields__` is still published and the
    SUBCLASS inherits those names. `\result == 0` PROVED; CPython 2.
  - **D (1443)** the same defect under MULTIPLE inheritance: `Cee(Ay, Bee)(1, 2, 3)` bound
    nothing at all. `get() == 0` PROVED; CPython 2.

## The repair (FAITHFUL, option 1 of the two gen #27 scoped)

  1. `construction_synth.py` drops `ClassVar`-annotated members from the synthesized
     `init_params`, and publishes the class's own field list as `dataclass_fields` for
     EVERY `@dataclass` — including one that carries an explicit `__init__`, because such
     a class still publishes `__dataclass_fields__` to its subclasses.
  2. `ir_resolve.apply_inheritance.merge_one` PREPENDS the base dataclasses' fields,
     walking the C3 MRO **REVERSED** (`_in_mro[sub][1:]` reversed — Python's
     `cls.__mro__[-1:0:-1]`), with a redeclared field keeping its **BASE position**.
     The receiver gate is `init_dataclass_synth` (a `@dataclass` with no explicit
     `__init__`); the donor list is the base's `dataclass_fields`.

## THE ORDER WAS A CARRIER ON THE REPAIR ITSELF (witness 1426)

Draft 1 walked the DECLARED bases left-to-right. `dataclasses._process_class` walks the
REVERSED MRO, so `class Cee(Ay, Bee)` takes **Bee's** fields first. Draft 1 PROVED
`Cee(1, 2, 3).get() == 1` where CPython gives 2; the SINGLE-inheritance twin, where the
two orders agree, is the positive control and proved `== 1` correctly.

## A PRE-EXISTING FAIL-CLOSED GAP FOUND WHILE PROBING (not a route)

**A base field cannot be read DIRECTLY off a derived record**: the record type is emitted
correctly (`type c = { mutable c_a: int; mutable b: int }` with the literal
`{ c_a = 1; b = 2 }`), but the ACCESS `c.a` is emitted unmangled and Why3 answers
`unbound function or predicate symbol 'a'`. Measured identical at HEAD and on the repair.
So **every #144-family probe must read an inherited field through an INHERITED METHOD — a
probe that reads it directly has measured nothing.**

## Blast radius — the one gen #27 feared is NOT there

Gen #27's "128 derived/`ClassVar` dataclasses, most of them the mirror's own CSL AST node
hierarchy" counted DECLARATIONS, not classes whose `init_params` MOVE. The mirror's 125
CSL-AST dataclasses all derive from FIELDLESS bases (`CSLNode`, `ContractWrapper`), so the
merged list equals the own list for every one of them. Census over the two corpora, the 53
mirrors and `pycsl_lib`, with cross-file bases resolved through a global class table:

  - classes whose `init_params` MOVE: **ONE** — `StatementEmissionMixin` in
    `src/self-annotate/src/module6_whyml/statements.py`, which is **never constructed**;
  - construction sites of a moved class: **ZERO**; `ClassVar` dataclass members: **ZERO**.

(`src/pycsl/ir_schema.py` carries 113 more, but `src/pycsl` is not an input to the
verifier; its mirror `src/self-annotate/src/ir_schema.py` has none.)

Measured: all three emission planes BYTE-INERT — pycsl-reference 1083/1103 with exactly 20
new source files, python-reference 2199/2199, mirrors 53/53, 0 MOVED / 0 GONE / 0 APPEARED.
