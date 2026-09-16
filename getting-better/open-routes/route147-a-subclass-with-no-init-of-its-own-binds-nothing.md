# ROUTE #147 — a subclass with NO `__init__` of its own inherits the base's constructor, and the model gives it an EMPTY `init_params`

**Status: OPEN. Found and reproduced by gen #28 (2026-09-16). NOT repaired — deliberately.**
Severity 1. Three shapes, all measured with CPython contradicting. Generator: carrier-rerun
(on gen #28's own route-#144 repair).

## The defect

`_collect_init_construction` (`src/pycsl/frontend/module5/construction_synth.py`) captures
`init_params` from the class's OWN `__init__`, and gen #28's route-#144 repair added a
merge for a DERIVED `@dataclass`. Neither covers the plainest Python rule of all:

> **a class that declares no `__init__` inherits the first `__init__` in its MRO.**

For such a subclass `init_params` is `[]`, so `_call_record_constructor`'s guard
`if (init_params or kwonly_params) and (...)` is FALSE, the whole binding block is skipped,
and every field takes `_field_default`'s **definite** literal.

## The three measured shapes (all at `2db4bb76`, i.e. WITH #144/#145/#146 repaired)

A base field cannot be read directly off a derived record (`o.afld` emits the unmangled
name and type-errors — a separate pre-existing fail-closed gap), so each probe reads the
inherited field through an INHERITED METHOD.

  1. **A PLAIN subclass of a `@dataclass`** (`scratchpad/g28/p2.py`)

         @dataclass
         class Ay:
             afld: int
             #@ ensures \result == self.afld
             def get(self) -> int: return self.afld

         class Cee(Ay):
             pass

         Cee(7).get()    #@ ensures \result == 0   <-- PROVED; CPython gives 7

  2. **A PLAIN subclass of a PLAIN class with an explicit `__init__`** (`scratchpad/g28/p3.py`)
     — same shape, same verdict, no `@dataclass` anywhere.

  3. **An UNDECORATED subclass of a `@dataclass` that declares its own annotation**
     (`scratchpad/g28/p4.py`) — Python does NOT run `@dataclass` on it, so `cfld: int = 0`
     is a bare annotation and `Cee(7)` still calls `Ay`'s inherited `__init__(afld)`.
     `\result == 0` PROVED; CPython gives 7. This shape also shows why the repair cannot
     simply reuse #144's merge: **inheriting a constructor is not the same operation as
     synthesizing one from the merged field list** — for (3) the synthesized answer
     `(afld, cfld)` would be wrong, because Python never runs the decorator here.

## The scoped repair (NOT landed)

Module 5 emits a third dataclass-family key, `"init_inherits": True`, for a class that
(a) declares NO `__init__` in its own body, (b) is NOT `@dataclass`-decorated (the
decorated case is #144's SYNTHESIZE arm, already landed), and (c) has bases.
`ir_resolve.apply_inheritance.merge_one` then, for such a class, walks the C3 MRO
`_in_mro[sub][1:]` (already computed there for routes #123/#125), calls `merge_one` on each
ancestor record so its own list is final, and COPIES WHOLESALE from the FIRST ancestor that
has a constructor:

```python
td["init_params"]          = list(anc["init_params"])
td["init_body"]            = copy.deepcopy(anc.get("init_body", []))
td["init_kwonly_params"]   = list(anc.get("init_kwonly_params", []))
td["init_kwonly_defaults"] = dict(anc.get("init_kwonly_defaults", {}))
td["init_unknown_fields"]  = list(anc.get("init_unknown_fields", []))
```

Copy, never merge: the derived class contributes nothing to a constructor it merely
inherits.

## WHY GEN #28 DID NOT LAND IT — THE BLAST RADIUS IS THE MIRROR'S EXCEPTION HIERARCHY

Census over `test-suite/corpus/pycsl-reference`, `test-suite/corpus/python-reference`, the
53 mirrors and `src/pycsl_lib`, resolving bases through a global class table:

  - classes that would GAIN an inherited `init_params`: **5** — `PyCSLSemanticError`,
    `PyCSLIRError` and one sibling in `src/self-annotate/src/errors.py`, one in
    `src/self-annotate/src/frontend/pure_ast.py`, one in `src/pycsl_lib/re/_engine.py`;
  - **CONSTRUCTION SITES of those 5: 86**, overwhelmingly `raise PyCSLSemanticError(msg,
    code=...)` / `raise PyCSLIRError(msg, stage=..., code=...)` spread across
    `core_ir_semantic.py`, `ir_schema.py` and their siblings.

Every one of those 86 sites currently constructs a record whose fields all take their
defaults; after the repair each would bind its message/stage/code arguments, which MOVES
the emission of a large share of the 53 mirrors and owes each of them a whole-file
re-proof. That could not be censused, predicted and gated inside gen #28's battery budget,
and **a half-gated construction-binding change is worse than an honest open route** (the
gen #14 / route #96 and gen #27 / route #144 precedent).

**For gen #29: predict the MOVED mirror set BEFORE the sweep, budget the whole-file
re-proofs of every mirror that raises, and expect honest failures — a constructor that
starts binding its arguments can legitimately break a mirror proof, and that cost is the
finding.**

## Reproduction

  - `scratchpad/g28/p2.py`, `scratchpad/g28/p3.py`, `scratchpad/g28/p4.py` — each PROVES
    `\result == 0` at `2db4bb76`; CPython returns 7 for all three.
  - probe-ledger rows: `g28-plain-subclass-of-a-dataclass-binds-nothing`,
    `g28-plain-subclass-of-an-explicit-init-binds-nothing`,
    `g28-undecorated-subclass-declaring-its-own-annotation`.
