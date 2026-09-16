# ROUTE #150 — a constructor's effects OUTSIDE its top-level `self.<f> = ...` stores are DROPPED

**Status: REPAIR DRAFTED by gen #29 (worktree wt149, drafts 3-5, together with #148/#149); battery D pending.** Severity 1. Generator:
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


## Gen #29 drafts (in wt149, with #148/#149)

  * **Draft 3 (fail-closed).** `_collect_init_construction` flags an OPAQUE constructor: any `super()`
    call, any call whose callee is rooted at `self` or whose arguments mention `self` (except a
    short list of pure builtins), any other load of bare `self`; a `@dataclass` with a synthesized
    constructor and its own `__post_init__`. `visit_ClassDef` widens `init_unknown_fields` and
    `init_unknown_cf_fields` to every field.
  * **The golden gate caught draft 3's PRECISION.** Frozen goldens 0442 and 0443 start their
    constructors with `super().__init__()` and failed on `only-derived=[init_unknown_*]`. Those
    constructions are faithful, so **draft 4 COMPOSES a LEADING `super().__init__(<positional
    args>)`** in `apply_inheritance`: the holder is found as route #147 finds one (through
    `init_inherits`, stop at anything unmodelled), its `init_body` is substituted with the arguments
    and prepended for every field this class does not store itself; an unmodelled/opaque holder, a
    bad arity, an omitted argument without a stateable default, or a composed value over names that
    are not this constructor's parameters makes the class opaque. A merged base field is widened
    through a popped side key `init_opaque150`, and the key is copied by the #147 inherit walk.
    Goldens back to 38/38.
  * **Draft 5 — carrier of draft 4:** a derived `@dataclass` runs an INHERITED `__post_init__`
    (`B(1).get() == 1` proved on draft 4, CPython 7). Records carry `has_post_init150`; non-record
    classes go on a module-level `post_init_nonrecord150` list; both popped.
  * Witnesses 1493-1502 (XFAIL, each PROVING at HEAD), 1503-1505 (PASS, FAILING at HEAD), 1506 (PASS
    on both). FAIL-CLOSED at HEAD and untouched: a property setter / `__setattr__` override
    intercepting a constructor store (pipeline errors).
  * WATCH: a FOREIGN stateless base defining `__post_init__` is not seen (no record, not in this
    module's list); `super(B, self).__init__` and `A.__init__(self, k)` are opaque, not composed.
