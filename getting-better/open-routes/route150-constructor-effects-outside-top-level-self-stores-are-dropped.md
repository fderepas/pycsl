# ROUTE #150 — a constructor's effects OUTSIDE its top-level `self.<f> = ...` stores are DROPPED

**Status: OPEN. Found and reproduced by gen #29 (2026-09-16).** Severity 1. Generator:
carrier-rerun (the #148/#149 construction neighbourhood). Six LIVE shapes, one mechanism.

## The mechanism

`_call_record_constructor` builds the object as ONE record literal from what the collectors
saw: top-level `self.<f> = <expr>` stores (captured / `field_defaults`), route #83's
control-flow stores (UNKNOWN) and route #79's uncapturable RHS (UNKNOWN). ANY OTHER statement of
`__init__` that changes `self` is invisible, and the literal states the pre-effect value as a
DEFINITE fact.

## Measured at `acba66f3` — each PROVED with CPython contradicting (`scratchpad/g29/pi/`)

| probe | shape | model | CPython |
|---|---|---|---|
| p1/p2 | `@dataclass` + `__post_init__` storing `self.x = 7`; `P(1).x` / `P(1).get()` | `{ x = 1 }`, `== 1` PROVED | 7 |
| p3 | `__init__: self.x = 1; self._setup()` (`_setup` stores 7, declares `assigns self.x`) | `{ x = 1 }` | 7 |
| p5 | `me = self; me.x = 7` | `{ x = 1 }` | 7 |
| p6 | `setattr(self, "x", 7)` | `{ x = 1 }` | 7 |
| p7 | `init_p(self)` — a module function storing `p.x = 7` | `{ x = 1 }` | 7 |
| p4b | `B.__init__: super().__init__(k + 100)` over `A.__init__: self.x = k`, read via `get()` | `{ b_x = 0; ... }` | 107 |

## Scoped repair (not landed) — fail-closed first

In `_collect_init_construction`, a constructor statement that can change `self` other than by a
recognized store — any `super()` call, any call whose callee or arguments mention `self` (a bare
`self` or a `self.<m>` callee), any load of bare `self` into a binding/argument/container — makes
EVERY field UNKNOWN (scalars via `init_unknown_fields`, collections via `init_unknown_cf_fields`);
a `@dataclass` (or any class) defining `__post_init__` does the same for the synthesized
constructor. A faithful `super().__init__` (route #147-style copy of the base's binding with the
argument substituted) is a later completeness step, NOT part of this repair.

**Cost warning:** this changes the construction literal of every class whose `__init__` calls a
method — the mirrors and python-reference certainly contain such classes. Census the constructed
classes (not the declared ones — gen #28's lesson) and PREDICT the moved set; an M1 landing
(emission moves, each moved program re-proves or fails honestly) is expected.
