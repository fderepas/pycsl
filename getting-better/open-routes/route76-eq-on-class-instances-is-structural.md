# ROUTE #76 — `==` ON CLASS INSTANCES IS STRUCTURAL, PYTHON'S IS IDENTITY

**STATUS: CLOSED at `ecd41b8f` — found AND closed 2026-09-11 (gen #7).** Reproduced at HEAD,
mechanism read off the emission, ground truth measured by RUNNING each program under
CPython (not reasoned about).

**THIS IS THE DUAL OF ROUTES #42/#52.** Those found `is` decided by VALUE equality — `is`
too WEAK. This is the mirror image: `==` on class instances decided by STRUCTURAL
equality — `==` too STRONG. #42/#52 were closed by giving `is` its own IR operator; the
`==` side of that same coin was never examined.

**IT IS THE #69 CLASS, THE SERIOUS ONE:** a FALSE POSTCONDITION about ordinary TOTAL
Python. No `no_exception`, no memory-model flag, no opt-in of any kind.

## THE ROUTE

```python
class C:
    v: int
    def __init__(self, v: int) -> None:
        self.v = v

#@ ensures \result == x          # <-- FALSE OF THE PROGRAM. PyCSL: SUCCESS.
def dup(x: C) -> C:
    return C(x.v)
```

**CPython measured, not reasoned about:** `dup(a) == a` is **`False`**. `C` defines no
`__eq__`, so Python's `==` falls back to *identity*, and `dup` returns a FRESH object.

**BOTH DIRECTIONS MEASURED, which is what makes this a route and not a gap:**

    \result == x    FALSE of the program  ->  **Verification SUCCESS**   (the unsoundness)
    \result != x    TRUE  of the program  ->  FAILED                     (so not merely incomplete)

## THE MECHANISM, READ OFF THE EMITTED WhyML

```whyml
type c = { mutable v: int }

let dup (x: c) : c
  ensures  { (result = x) }        (* Why3 logic `=` — STRUCTURAL on the record *)
=
  { v = x.v }                      (* a fresh record with the same field value *)
```

`==` is emitted as Why3's polymorphic logic `=`. On a record type that is equality of the
FIELD VALUES. Python's `==` on a class that defines no `__eq__` is `object.__eq__`, i.e.
**identity**. Two distinct objects with equal fields are `=` in Why3 and `!=` in Python.

## CARRIER 2 — A USER-DEFINED `__eq__` IS DISCARDED OUTRIGHT

Sharper than carrier 1, because here the user *wrote the definition* and the tool ignored it:

```python
class C:
    v: int
    def __init__(self, v: int) -> None: self.v = v
    def __eq__(self, o: 'C') -> bool:  return False      # NOTHING is equal

#@ ensures \result == x          # <-- PyCSL: SUCCESS.  CPython: ident(a) == a is False
def ident(x: C) -> C:
    return x
```

Module 5 **skips dunders for body emission** (its own comment, `preamble.py` ~9060), so
`__eq__` is never emitted and never consulted. This is the #73/#74/#75 shape — **a
built-in default beats the definition the user wrote** — with the default being Why3's
structural `=` rather than a hand-added oracle.

## THE ESCALATION: THE FALSE FACT DISCHARGES A **PRECONDITION**

Not merely an `ensures` about objects — it certifies a CALL whose documented precondition
is false at runtime:

```python
#@ ensures \result == x
def dup(x: C) -> C:            return C(x.v)

#@ requires a == b
#@ ensures \result == 1
def only_if_equal(a: C, b: C) -> int:  return 1

#@ ensures \result == 1
def caller(x: C) -> int:
    return only_if_equal(dup(x), x)    # `a == b` is FALSE here in CPython
```
**`[+] Verification SUCCESS! All contracts formally proven.`** — CPython measures the
call-site precondition as `False`. So contract-based reasoning about object equality is
unsound in BOTH the assume and the guarantee direction.

## WHAT MAKES IT SHARP: THE `@dataclass` CARRIER IS **CORRECT**

Measured in the same session, and it is the control that bounds the route:

```python
@dataclass
class P:
    v: int
#@ ensures \result == x
def dup(x: P) -> P: return P(x.v)
```
CPython: `dup(a) == a` is **`True`** — `@dataclass` GENERATES a structural `__eq__`.
PyCSL: SUCCESS. **FAITHFUL.** Structural `=` is the right model here.

So this is not "object equality is unmodelled". It is: the model hard-codes STRUCTURAL
equality, which is right for exactly the classes whose `__eq__` *is* structural
(`@dataclass` with default `eq=True`, `NamedTuple`) and wrong for every other class —
a plain class (identity), a custom `__eq__`, and `@dataclass(eq=False)` (identity again).
Same shape as route #59's List-vs-Dict control: two kinds of class have DIFFERENT equality
semantics in Python and the model gives both the same one.

## WHAT FAILS CLOSED, AND ONLY BY A TYPE ACCIDENT — READ THIS BEFORE BUILDING

**THE WHOLE BODY PLANE IS CONFINED BY ONE SHARED WHY3 TYPE ACCIDENT.** Nine dunder
carriers were enumerated mechanically (`__eq__`, `__ne__`, `__lt__`, `__bool__`, `__len__`,
`__contains__`, `__getitem__`, `__add__`, plus a non-dunder control). In a function BODY
every one dies with the SAME Why3 message:

    This expression has type PyCSL_Program.c @rho, but is expected to have type int

i.e. the class record type is not usable where the lowering wants an int. **That is a
`SAFE-TYPED` verdict, which this campaign has banked as a type accident and never a
guard.** The SPEC plane has no such constraint — `requires`/`ensures` lower `==` to
polymorphic `=`, which typechecks fine on records — and that is the whole reason the route
lives in the spec plane only.

**REOPENING CONDITION FOR THE WHOLE DUNDER FAMILY, stated once:** any change that makes a
class record type usable in an int context in a BODY (an unboxing, a `__bool__`/`__len__`
lowering, an `__eq__`-to-int coercion) reopens ALL NINE body carriers simultaneously. One
condition to watch, not nine.

**THE VALUE-LEVEL ESCALATION FAILS CLOSED, and by Why3's OWN REGION TYPING** — the same
mechanism that fails-closed route #59's return carrier. `setv(dup(x)); return x.v` with
`ensures \result == 5` comes back **Unknown**: the logic `=` between two records does NOT
make them the same REGION, so a write through one is not a write through the other.
Recorded so the next generation does not re-probe it.

**INCIDENTAL EMISSION BUG FOUND ALONGSIDE (not this route, worth its own look):** a local
with an EXPLICIT class annotation whose RHS is a CALL is pre-declared as `let b = ref 0` —
an int — so `b: C = dup(a)` ill-types. The annotation is ignored when the RHS is a Call.
That is the same "the RHS is a Call and the guard keys on a bare name" shape route #59's
return carrier had.

## REPAIR — BUILT, GATED AND LANDED (see `## THE LANDED GUARD` below)

Refuse (or model faithfully) a spec-plane `==`/`!=` whose operands are of a user CLASS type
whose `__eq__` is NOT structural:

  * `@dataclass` with default `eq=True`, and `NamedTuple`  -> ALLOW (measured faithful).
  * plain class with no `__eq__`                           -> Python is IDENTITY; refuse,
    or lower to the `is` operator that routes #42/#52 already built.
  * class with a user-defined `__eq__`                     -> the definition is discarded;
    refuse.
  * `@dataclass(eq=False)`                                 -> identity again; refuse.

**THE CENSUS COMES FIRST** (lesson (p)): routes #42/#52 already built a dedicated `is`
IR operator, so the identity machinery EXISTS and may be reusable rather than new. And the
cost question that decides the shape is how many corpus/mirror specs compare two
class-typed operands with `==` — that must be MEASURED before a refusal is written, since
a refusal that breaks the mirror is a fidelity-plane failure.

## WITNESSES (to land with the repair)

    carrier 1  plain class, fresh object      `\result == x`  PROVES  / CPython False
    carrier 1' true twin                      `\result != x`  FAILS
    carrier 2  user `__eq__` returns False     `\result == x`  PROVES  / CPython False
    control    `@dataclass`                    `\result == x`  PROVES  / CPython True (FAITHFUL)
    escalation precondition discharge          SUCCESS         / CPython precondition False


---

# THE LANDED GUARD — AN ALLOWLIST, AND WHY THAT IS THE POINT

`module6_whyml/expressions.py::_handle_binop`, immediately before `op = op_translate(raw_op)`
(so every earlier special case — the whole `is None` / `pycsl_none` family included —
returns before the guard is ever consulted, and is therefore untouched).

**THE SINGLE MOST TRANSFERABLE THING IN THIS FILE: AN ALLOWLIST KEYED ON SYNTAX FAILS
CLOSED WHEN THE HAZARD MOVES; A BLOCKLIST KEYED ON SYNTAX FAILS OPEN.** This campaign has
banked "a guard keyed on a syntactic location is defeated by moving the hazard one step"
SIX times. The resolution is not to abandon syntax — it is to invert the polarity.

**TWO BLOCKLIST DESIGNS WERE BUILT OUT AND REFUTED BY MEASUREMENT BEFORE EITHER LANDED:**

  1. *"Refuse when the function body CONSTRUCTS an instance."* **Defeated one call deeper.**
     With the constructor moved into `mk` — `def dup(x): return mk(x.v)` — `dup`'s body
     contains no constructor at all and `\result == x` still PROVED. Witness 1192.
  2. *"Lower the comparison to an uninterpreted `obj_eq` predicate plus reflexivity."*
     **Refuted by Why3's own RECORD EXTENSIONALITY:** Why3 already derives
     `{v = x.v} = x`, so reflexivity re-collapses the two objects and ANY
     equality-derived predicate inherits the defect. Without reflexivity the five
     reference locks stop proving. There is no setting of that dial that works.

**WHAT THE ALLOWLIST ADMITS**, each faithful under Python's own rules:

  1. a **NamedTuple / TypedDict** — Python GENERATES a structural `__eq__` there, so the
     model's structural `=` is exactly right (witness 1191);
  2. two **syntactically identical pure READ PATHS** — the same object, trivially;
  3. **`\result` against a pure READ PATH when EVERY `return` in the function returns
     exactly that path** — the accessor idiom (`return self.toks[self.i]`), which hands
     back THE object in the slot rather than a copy (witness 1190).

A **READ PATH** deliberately excludes a Call: a constructor builds a NEW object on every
evaluation, so `mk() == C(1)` is False in Python even though both sides read alike.
A class defining its **own `__eq__`** is refused outright — Module 5 skips dunders for body
emission, so the user's definition is DISCARDED and structural equality silently
substituted for it.

**SPELLING IS CANONICALIZED SO THE ALLOWLIST IS NOT DEFEATED BY IT.** `a[-k]` and
`a[\length(a) - k]` name the SAME CELL, hence the same object, and lock 0934 spells the
clause one way and its body the other. Both are normalized onto one form before comparison.
Without that the guard over-refused a green reference lock — caught by running the locks,
not by reading them.

**WRITTEN INLINE, AS EXPLICIT-STACK WALKS, NOT AS HELPER METHODS.** A new LIVE `def` with
no mirror counterpart breaks `bin/check-mirror-coverage.py`'s ratchet — the same constraint
the route #45 NaN recognizer records a few lines above in the same function. That plane is
green precisely because the guard obeyed it.

## PROBING THE REPAIR FOR THE GAP IT LEAVES FOUND A LIVE ONE — BEFORE LANDING

The first cut resolved a class-typed operand through `\result`, a typed local/param, and a
constructor Call only. It **MISSED the ELEMENT of a `List[<record>]`**, so

    #@ ensures a[0] == a[1]        # two distinct objects, equal fields

still **PROVED** where CPython answers False. The resolver now reaches a Subscript through
the record-array param/field maps (`_record_array_params` / `_record_array_fields`).
Witness 1193. This is the second time in two generations that probing one's own repair
paid immediately, and it cost one probe.

## GATES — ALL GREEN

  * **ALL 33 SOUNDNESS PLANES GREEN** (`--slow`, rc=0, why3 on PATH, clean tree).
    An earlier battery was **DISCARDED** because source was edited while it ran: a
    mixed-tree verdict is worthless, and that is a process lesson worth keeping.
  * **IR CONFORMANCE 38/38, 0 MISMATCH** — run deliberately, because gen #6's
    dependency-frame repair was byte-inert on BOTH corpora and still broke two frozen IR
    goldens. Conformance sits one pipeline stage earlier than every byte-diff.
  * **FIDELITY** `check-self-annotate-sync.sh` green — 887 un-trusted mirror functions
    verbatim. `check-mirror-coverage.py` green.
  * **BLAST RADIUS: 0 newly-refused files across 1645 corpus files + the mirror.** And the
    guard either RAISES or FALLS THROUGH — it never alters emitted text — so it is
    **byte-inert BY CONSTRUCTION**, not merely by sampling.
  * **METRIC UNCHANGED**: markers 459 - grep 484 - offset 25 - unattached 0. A refusal
    costs the trust surface nothing, which is the expected shape of a soundness window.
  * **9/9 exploits refuse** (carrier 1, carrier 2, the precondition escalation, the
    subscript element, the ctor operand, the ctor one call deeper, the ctor with a callee
    `ensures`, the ctor via a local, the list-element carrier); **5 corpus locks + the
    accessor + the NamedTuple control still prove**; 0901 matches its PRE-EXISTING baseline
    failure (verified by re-running it with the guard removed — not assumed).

## RESIDUE — THREE ITEMS, EACH WITH ITS REOPENING CONDITION

  1. **`@dataclass` IS NOW OVER-REFUSED, and this is a COMPLETENESS regression, not an
     unsoundness.** Python generates a structural `__eq__` for a default `@dataclass`, so
     its `==` is faithful and ought to be allowed as `NamedTuple` is. `_record_types`
     carries `is_namedtuple`/`is_typeddict` but **no dataclass marker**, and the marker
     lives in Module 5 — a MIRRORED file, so threading it owes a whole-file re-proof.
     MEASURED cost of the over-refusal TODAY: **zero corpus files** (the census found no
     dataclass comparison anywhere). REOPENING CAPABILITY: thread `is_dataclass` from
     `Module5_IREmitter._is_dataclass_decorated` into the type_decl and add it to the
     allowlist alongside `is_namedtuple`. Users who want structural equality can use a
     NamedTuple today, and the refusal message says so.
  2. **THE RECORD-FIELD CARRIER `b.p == b.q` FAILS CLOSED BY A TYPE ACCIDENT, NOT BY THIS
     GUARD.** Measured: it is a `PIPELINE ERROR` with the guard NOT firing (the resolver
     does not reach a `FieldGet` whose field type is a record). **A `SAFE-TYPED` verdict is
     an accident, never a guard** — this campaign's own banked lesson. REOPENING CONDITION:
     the day a record-typed FIELD read becomes comparable, this carrier is live and the
     guard will not see it. The fix is one more branch in the same resolver
     (`FieldGet` -> receiver class -> `field_types[field]`).
  3. **THE DEEPER BOUNDARY: THE VALUE MODEL HAS NO OBJECT IDENTITY, AND THE SPEC GRAMMAR
     HAS NO `is`.** Measured: `#@ ensures \result is x` does not even PARSE — routes
     #42/#52 gave `is` its own IR operator in the BODY plane only, so there was no identity
     machinery to reuse. The five reference locks prove their TRUE claims through the
     structural reading, i.e. by an unsound inference that happens to reach a true
     conclusion; the allowlist keeps exactly those and refuses the rest. A COMPLETE repair
     needs a real identity notion (an opaque per-object slot set fresh at each constructor),
     whose blast radius is EVERY record emission in the corpus and therefore hundreds of
     re-proofs — **beyond the MEASURED BOX CEILING of about four whole-file proofs**, which
     is a measured reason and not a guess. That makes it a COST/SCALE boundary, recorded
     here with its capability rather than ground on.
     **THE VALUE-LEVEL ESCALATION IS SEPARATELY FAIL-CLOSED, BY WHY3'S OWN REGION TYPING** —
     `setv(dup(x)); return x.v` with `ensures \result == 5` comes back Unknown, because a
     logic `=` between two records does not make them the same REGION. Same mechanism that
     fails-closed route #59's return carrier. Do not re-probe it.
