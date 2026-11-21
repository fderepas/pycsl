# ROUTE #147 — a subclass with NO `__init__` of its own inherits the base's constructor, and the model gives it an EMPTY `init_params`

**Status: CLOSED AND FULLY GATED by gen #29 (2026-09-16), battery B' (drafts 1-3 gen #28, 4-6 gen
#29) — see the "Gen #29" section at the end. Witnesses 1444-1449 1457-1461 (XFAIL), 1450-1456
1462 1463 (PASS). The "NOT landed" reasoning below is gen #28's, kept as the record;
its blast-radius fear was measured WRONG (every one of the 86 construction sites is a `raise`,
and `raise C(args)` lowers to a bare `raise C`) and the repair is byte-inert on all three planes.**
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


## Gen #29 — drafts 4, 5, 6 (the repair as landed)

**Draft 4 (found uncommitted after a reboot).** Draft 3's separate `has_own_init` IR key appeared on
14 of the 38 frozen conformance goldens (front-end-only conformance 24 OK / 14 MISMATCH). The walk
now keys on `init_inherits` alone: stop at the first ancestor that is NOT `init_inherits`, walk
THROUGH one that is.

**Draft 5 — five carriers of the repair, found by rerunning it against itself.**
  1. An UNMODELLED ancestor ahead of the definer (`class Cee(Exception, Ay): pass`): the walk
     `continue`d past `records.get(...) is None` and copied Ay's constructor. `Cee(7).get() == 7`
     PROVED; CPython 5 (BaseException's constructor binds nothing). Witness 1457.
  2. The same with an in-module STATELESS base (no fields, so no record) that defines a constructor.
     Witness 1458.
  3. and 4. Against my own fences — a walk-through list `{object, Generic, ABC}`, then `{object}`:
     stateless user classes NAMED `ABC` and `object` proved the same false `== 7`. Witnesses 1459,
     1460. FINAL RULE: every unmodelled ancestor STOPS the walk with nothing copied; the real
     `object` is last in every C3 MRO, so stopping on it loses nothing.
  5. `@dataclass(init=False)` generates no constructor, so it INHERITS; #147 excluded every decorated
     class and #144 synthesized one. `Cee(7).get() == 0` PROVED at `da51d62b` AND on draft 4; CPython
     107. New helper `_dc_decorator_init_false` (constant keyword only — census of `dataclass(...
     init=` over both corpora, the mirrors, `src/pycsl` and `src/pycsl_lib`: ZERO). Witnesses 1461
     (XFAIL), 1462 (PASS, fails at `da51d62b`), 1463 (PASS on both).
  FAIL-CLOSED: `__init__ = _mk` bound in the class body; `@dataclass(init=False)` over a dataclass base
  (false claim); a `*args` constructor storing a literal (the #139 channel carries it).

**Draft 6 — the conformance leg MISSED its prediction and was right.** Draft 4's comment claimed no
golden declares a based, undecorated, `__init__`-less class; goldens 0444 and 0445 do, and failed on
`only-derived=['init_inherits']`. The key is now a Module-5 -> `apply_inheritance` SIDE CHANNEL,
POPPED once every record is merged, so the RESOLVED IR the goldens freeze never carries it.
Dependency IR is cached RAW (before `apply_inheritance`), so an IMPORTED inheriting ancestor still
carries the key during the walk — measured faithful on a cross-module diamond
(`scratchpad/g29/c10.py`: false `== 7` refused, true `== 107` proves).

LESSON: **AN UNMODELLED NAME IN A WALK IS NOT "NOTHING THERE".** `records.get(x) is None` means the
model cannot see `x`, and a `continue` on it is an assumption about `x`'s behaviour.
