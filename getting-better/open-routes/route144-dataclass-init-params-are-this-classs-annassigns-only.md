# ROUTE #144 — a `@dataclass`'s `init_params` is built from THIS class's `AnnAssign`s only

**Status: OPEN. Found and reproduced by gen #27 (2026-09-16). NOT repaired — deliberately.**
Severity 1. Two shapes, both measured with CPython contradicting. Generator: deferral-audit.

## The deferral that hid it

`src/pycsl/frontend/module5/construction_synth.py:355-358`:

> *"A field WITHOUT a default bound past the provided arity, or a non-scalar (list/dict/set)
> field, is handled by `_call_record_constructor` (positional-prefix binding + typed default) —
> sound."*

The named guard exists, at `src/pycsl/module6_whyml/expressions.py:12702`:

```python
if (init_params or kwonly_params) and (
        (args and len(args) <= len(init_params)) or kwargs_map or kwonly_defaults):
```

and its own justification, at `expressions.py:12694-12696`, is the premise that fails:

> *"an OVER-arity call (a Python error) binds nothing (all defaults — fail-closed, never a false
> full binding)."*

**`len(args) > len(init_params)` is only a Python error when `init_params` really is the
constructor's parameter list.** For a `@dataclass` it is not: `construction_synth.py:361-365`
builds it from this class's own `ast.AnnAssign` nodes,

```python
fnames = [stmt.target.id for stmt in node.body
          if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name)]
init_params = list(fnames)
```

and the base-class merge at `src/pycsl/frontend/ir_resolve.py:2298-2301` merges **`fields`,
`class_invariants`, `field_defaults` and `constants` — and not `init_params`**.

## Shape A — a DERIVED dataclass (all fields collapse to their defaults)

```python
from dataclasses import dataclass
_ = 0  # anchor

@dataclass
class B:
    a: int

@dataclass
class C(B):
    b: int

#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = C(1, 2)
    return c.b
```

**PyCSL: `Verification SUCCESS`. CPython: `probe()` returns 2.**
Python's synthesized `__init__` takes base fields first, then own fields, so `C(1, 2)` is legal;
the model sees `len(args)=2 > len(init_params)=1`, binds nothing, and `_field_default`
(`expressions.py:12673`) hands back the **definite** integer `rec_info['defaults'].get(fn, 0)`.

CONTROL, which must behave the other way: the same class flattened (`@dataclass class D: a: int;
b: int`), where `len(args) == len(init_params)`, the binding fires, and the false
`\result == 0` is REFUSED. Measured: refused.

## Shape B — a `ClassVar` member (the positional binding is OFF BY ONE and binds the WRONG field)

```python
from dataclasses import dataclass
from typing import ClassVar
_ = 0  # anchor

@dataclass
class P:
    k: ClassVar[int] = 10
    x: int
    y: int

#@ ensures \result == 2
#@ assigns \nothing
def probe() -> int:
    p = P(1, 2)
    return p.x
```

**PyCSL: `Verification SUCCESS`. CPython: `probe()` returns 1.**
A `ClassVar` annotation is an `ast.AnnAssign` and so enters `fnames`, but Python does not make it
an `__init__` parameter. The model binds `k=1, x=2`; Python binds `x=1, y=2`. This shape is worse
than Shape A: it is not a lost default, it is a **definite wrong value silently taken from the
neighbouring argument**.

## No other gate catches either shape

The only wrong-arity hard error is `_namedtuple_walk_construction`, gated at
`src/pycsl/core_ir_semantic.py:64-70` on `td.get("kind") == "record" and td.get("is_namedtuple")`,
and `is_namedtuple` is set only by `_emit_namedtuple_record` (`Module5_IREmitter.py:2885 / 2948 /
3046`) — never for a `@dataclass`. Nor is the field marked unknown: `self._init_unknown` is reset
at `construction_synth.py:94` and the dataclass branch adds nothing to it.

## The two candidate repairs (NOT landed)

  1. **FAITHFUL** — make `init_params` the real signature: prepend the base dataclasses' fields
     (in MRO order, base-first) and drop `ClassVar`-annotated members. This is the correct model
     and it CHANGES EMISSION for every derived-dataclass construction.
  2. **FAIL-CLOSED** — refuse when `len(args) > len(init_params)` instead of silently binding
     nothing. Cheap, but it refuses every legal derived-dataclass construction, which is a large
     completeness loss.

Repair (1) is the right one; (2) is acceptable only if (1) proves intractable.

## Why gen #27 did not land it — THE BLAST RADIUS IS THE MIRROR ITSELF

Census of derived-or-`ClassVar` `@dataclass` classes over pycsl-reference, python-reference, the
53 mirrors and `pycsl_lib`: **128 sites**, and the overwhelming majority are in
`src/self-annotate/src/frontend/Module2_Parser.py` — the mirror's own CSL AST node hierarchy
(`Requires(ContractWrapper)`, `BinOp(CSLNode)`, `UnaryOp(SingleExprNode)`, …). Repair (1) moves
the emission of every mirror file that constructs one of those nodes, and repair (2) would refuse
them outright. Neither could be censused, predicted and gated inside gen #27's remaining window,
and **a half-gated construction-binding change is worse than an honest open route** (the gen #14 /
route #96 precedent).

**For gen #28: census the CONSTRUCTION sites (not the class declarations) whose argument count
exceeds the model's `init_params`, predict the MOVED set BEFORE the sweep, and expect honest
failures — a constructor that starts binding the right fields can legitimately break a mirror
proof, and that cost is the finding.**

## Reproduction

  - `scratchpad/g27/k1.py` (Shape A, PROVES; CPython 2) and `scratchpad/g27/k1ctl.py`
    (the flattened control, correctly REFUSED)
  - `scratchpad/g27/k4.py` (Shape B, PROVES; CPython 1)
  - probe-ledger rows: `g27-derived-dataclass-init-params-miss-the-base-fields`,
    `g27-dataclass-classvar-shifts-the-positional-binding`
