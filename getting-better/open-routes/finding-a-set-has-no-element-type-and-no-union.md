# A `Set[T]`'s element type survives `add` and not `in` — and there is no union

**Status: FINDING, two independent walls, each located by a two-line program.** Not a
soundness route: both fail CLOSED, with a Why3 type error, and neither certifies anything.
What they cost is the conversion track — the campaign's actual purpose.

## Why this was measured

`getting-better/driver-backlog.md`'s honest ranking puts the conversion track's #1 blocker at
"the `int`-placeholder annotations on `\trusted` stubs", and the worked example is

    mirror:  def _walk_stmt(self, node: ast.AST, held: int,      func_name: str) -> None
    live:    def _walk_stmt(self, node: ast.AST, held: Set[str], func_name: str) -> None

with the note that re-typing `held` to `Set[str]` moves the error from `int vs array int` to
`int vs int -> option int` — "the next expression in the same body (`held | {mutex}`, a set
union)". That is a diagnosis by symptom. Two probes turn it into two facts.

## Wall 1 — the element type of a set is `int`, whatever the annotation says

```python
#@ ensures True
#@ assigns \nothing
def has(held: Set[str], m: str) -> bool:
    return m in held
```

    File "…mlw", line 13: This expression has type string, but is expected to have type int

The same program with `Set[int]` and `m: int` **VERIFIES**. So membership works; what does
not work is the ELEMENT TYPE.

**And then the write path was probed, which is where this stops being "sets are untyped"
and becomes something sharper:**

    held.add(m)     Set[str], m: str      SUCCESS
    m in held       Set[str], m: str      FAILED    string where an int is expected

**One type, two paths, and only one of them carries the element type.** `add` on a
`Set[str]` lowers correctly; membership on the same value lowers against `map int`.
Membership is not untyped — it is typed to `int`, always, which is why `Set[int]` passes it
and `Set[str]` cannot.

The static-semantics reference says `τ(set) = dict`, *"sets share the dict model"*, and the
dict model types its key: `τ(Dict[K, V]) = dict (* κ=string ⇒ map string (option ν), native
String.(=); else map int *)`. Probed, the dict half holds — `k in d` and `d[k]` both VERIFY
for `Dict[str, int]`.

**AND THE SET HALF IS NOT AN OVERSIGHT — it is a documented, deliberate, DEFERRED gate, and
the source says so at the line that makes the decision.** `module6_whyml/functions.py` ~137:

```python
kt = getattr(self, "_dict_key_types", {}) or {}
_sk = "string" if (_mut_coll and kt.get(arg) == "string") else "int"
```

with thirteen lines of comment above it: a by-reference (mutated) `Set[str]` param genuinely
emits the raw-string map write, so its type must agree; a NON-by-ref set param "must STAY
`map int`", because it is forwarded to sibling `val` bridges still typed `map int` and a
`map string` here would mistype the bridge — *"that cross-method κ=string agreement is the
deferred I4 fixpoint"*.

So `held.add(m)` verifying and `m in held` failing, on the same `Set[str]`, is one gate
seen from two sides: `.add` MAKES the parameter mutated, and mutation is what buys the
string key.

**Predicted and confirmed.** If that reading is right, a `Set[str]` parameter that is BOTH
added to AND tested should type-check, because the `.add` promotes it:

```python
#@ assigns held
def f(held: Set[str], m: str) -> bool:
    held.add(m)
    return m in held            # VERIFICATION SUCCESS
```

It does. One line of code explains all ten probes, and the explanation was checked by
predicting an eleventh rather than by re-reading the first ten.

### What that changes about the repair

Not "add the missing string-key branch" — the branch exists and is gated for a reason. The
work is the **I4 fixpoint the source names**: propagate κ=string across method boundaries so
a read-only `Set[str]` param and the sibling `val` bridges it is forwarded to agree. That is
a module-level inference, the same shape as the `_mutated_collection_params` fixpoint
already there, and it is the thing standing between the conversion track and every mirror
function that merely READS a `Set[str]`.

This is the third position of a mechanism this campaign keeps meeting: route #148/#149
repaired a FIELD whose type came from an `__init__` parameter, and
`finding-a-list-out-of-a-dict-cannot-be-passed-anywhere.md` carries the matrix of which read
forms work for which element types. Here the container is a set and the answer is that there
is no element type to get wrong.

## Wall 2 — set UNION is modelled for ONE SHAPE, in ONE PLACE

**CORRECTION, and it is the third this session; each one came from probing a sentence
instead of writing it.** The first draft of this section said "set union is not modelled".
Reading `module6_whyml/expressions.py` ~6259 says otherwise — there is a union lowering, and
its own comment names its gate: *"item34.md CF4: `<set> | {x}` (set union with a set
literal, e.g. the for-loop's `local_refs | {target}`) … @mutable_state"*. Probed:

    local_refs | {target}   inside a `@mutable_state` class, Set[int]    SUCCESS
    local_refs | {target}   inside a `@mutable_state` class, Set[str]    SUCCESS
    local_refs | {target}   in a STANDALONE function                     FAILED
    a | b                   set | set, anywhere                          FAILED

So the union exists, it is element-typed, and it is gated on TWO things at once: the right
operand must be a set LITERAL, and the enclosing class must be `@mutable_state`. Both gates
are deliberate and documented in the code; what nobody had written down is that together
they exclude the shape the conversion track actually needs.

**`ConcurrencyChecker` is not a `@mutable_state` class** — checked, in both the live tree and
the mirror — so `held | {mutex}` inside `_walk_stmt` is outside the gate on the second
count even though it matches the first exactly. The backlog's "`int vs int -> option int`"
is a union lowering DECLINING to fire, not a union lowering that does not exist.

## The shape of wall 2, stated exactly

```python
#@ ensures True
#@ assigns \nothing
def widen(held: Set[int], m: int) -> None:
    held2 = held | {m}
    _ = held2
```

    This expression has type int -> option.Option.option int, but is expected to have
    type int

`Set[int]` MEMBERSHIP verifies in the program above, so this is not the element type: the
`|` falls through to the scalar path and produces the map itself where an `int` is expected.
Both `Set[str]` and `Set[int]` fail identically, which is the signature of a gate that did
not open rather than of a type that is wrong.

## What it costs, exactly

`ConcurrencyChecker._walk_stmt` is one of the cheapest conversion candidates in the mirror
(~17 s to prove) and it needs BOTH walls closed: the signature re-typed to `Set[str]` (wall
1) and `held | {mutex}` lowered (wall 2). Neither is a one-line repair, and the order
matters — wall 2 is invisible until wall 1 is closed, which is exactly how the backlog found
it and why the backlog's note reads as one confusing error instead of two clear ones.

**A chain of type repairs is not a blocker, it is a sequence of blockers, and only the first
one is ever visible.** The cheapest way to see the second is a two-line program, not another
conversion attempt: `def f(held: Set[int], m: int)` with one operator in the body costs
twenty seconds and tells you which half of the error is which.

## THE WHOLE SURFACE, PROBED — a set supports exactly two operations

The four probes above answer `_walk_stmt`'s question. Ten answer the general one, and the
answer is smaller than "union is missing":

    m in held           Set[int]    SUCCESS
    held.add(m)         Set[int]    SUCCESS
    -------------------------------------------------------------------
    held.add(m)         Set[str]    SUCCESS   — the WRITE path types the element
    s | {x}   in a @mutable_state class, Set[int] and Set[str]   SUCCESS
    -------------------------------------------------------------------
    m in held           Set[str]    FAILED    string where an int is expected
    m in held           Set[str]    FAILED    inside @mutable_state too — not the gate
    s | {x}   in a STANDALONE function        FAILED    the @mutable_state gate
    a | b     set | set, anywhere             FAILED    the set-literal gate
    held & other        Set[int]    FAILED    map where an int is expected
    held - other        Set[int]    FAILED    "
    held ^ other        Set[int]    FAILED    "
    held.union(other)   Set[int]    FAILED    "
    held.intersection(other)        FAILED    "
    len(held)           Set[int]    FAILED    "
    k in d              Dict[str,int] SUCCESS — and the dict types BOTH paths
    d[k]                Dict[str,int] SUCCESS

**Membership, `add`, and a union with a literal inside a `@mutable_state` class. That is the
entire modelled surface of a Python set.** Every other binary operator, every named
equivalent of one, and `len` fail the same way — the set's map falls through to the scalar
path.

Stated that way the conversion consequence is not "one operator is missing" but "a set is a
bag you can put things in and ask about, and nothing else", which is a different size of
build and a different sentence to put in a backlog. The four probes were written to settle
one function's chain; the ten were written because four probes that all fail the same way is
a reason to ask how far the sameness goes.

`held.add(m)` verifying is the interesting half: MUTATION of a set parameter is modelled,
with a `#@ assigns held` frame, while reading its size is not.

## The I4 fixpoint's blast radius, censused — ZERO corpus, 159 mirror functions

The repair the source names ("that cross-method κ=string agreement is the deferred I4
fixpoint") would normally be a frightening change: a parameter's WhyML type is the most
load-bearing thing in an emission, and the corpus-inertness plane exists to catch exactly
that. Censused instead of assumed — every `Set[str]`/`FrozenSet[str]` parameter in the tree,
split by whether its body mutates it:

    both corpora                0 read-only,   4 mutated
    src/self-annotate/src     159 read-only,  10 mutated
    src/pycsl                 231 read-only,  20 mutated

**No read-only `Set[str]` parameter exists in either corpus.** The fixpoint therefore cannot
move a single corpus emission — the plane that would dominate the risk is inert by
construction, and the byte-diff would say so rather than being argued about.

What it moves is 159 mirror functions, which is precisely the population the conversion track
is blocked on: `ConcurrencyChecker._walk_stmt`, `_walk_body` and `_warn_if_unprotected` are
three of the backlog's cheapest candidates and all three are gated on that one line.

This is the rarest shape a typing change can have — all of the upside in the mirror, none of
the exposure in the corpus — and it is an accident of what the corpus happens to contain,
which is why it had to be counted rather than guessed.

### CORRECTION to the blast radius — 120 of those 159 are already converted

The 159 read-only `Set[str]` parameters in the mirror were counted without asking which of
them are in `\trusted` stubs. Split:

    in `\trusted` stubs   39 read-only,  0 mutated    <- the conversion population
    already converted    120 read-only, 10 mutated    <- these already PROVE, today

**So 120 mirror functions read a `Set[str]` parameter and verify right now**, which is a
fact the earlier sentence ("the 159 mirror functions the conversion track is blocked on")
flatly contradicts. `Module5_IREmitter._scan_2d_in_expr` is one of them: it takes two
`Set[str]` parameters, it is NOT `\trusted`, and it is a verbatim copy of live source.

The reason is the other half of the tagger. `_tag_str_keyed` fires on a membership whose key
is PROVABLY a string — a literal, a `str`-annotated name. `_scan_2d_in_expr`'s key is
`root.get("name")`, which the tagger cannot prove, so κ stays `int`, the parameter lowers to
`map int`, and everything downstream agrees with everything else. **The parameter's declared
element type never enters into it in either direction**, which is why 120 functions are fine
and the two-line probe is not.

So the wall is narrower and more precisely placed than the first count suggested:

> a read-only `Set[str]` parameter whose membership key the tagger can PROVE is a string.

That is the shape a converted function tends to have — it is reading a set of names against
a `str` local — and it is why the wall shows up at conversion time and not in the 120
functions already there. Thirty-nine `\trusted` stubs carry a read-only `Set[str]`; how many
of those hit the wall is not knowable without converting them, and saying so is better than
reusing a number that was never about this.

Fifth correction in this record, and the fifth found by counting something that had been
asserted. The counts that matter are always one split finer than the one already taken.

## THE ONE-LINE FIX WAS TRIED, AND IT FAILS AT THE FIRST CALL EDGE

Deleting the `_mut_coll` conjunct on an offline tree makes the read-only `Set[str]`
membership verify, keeps the `Set[int]` control green, and leaves all 14 emittable set-using
corpus files byte-identical. The mirror sweep then moved exactly two files, and both moved
the SAME function's `let` and its abstract `val` together — which was written up here as
"the bridge the comment warns about does not desync".

**That was a statement about two DECLARATIONS. A call site is a third thing.** Re-proving
the moved file takes eight seconds to disagree:

    module6_whyml/statements.py, line 1350:
      This expression has type string -> option.Option.option int,
      but is expected to have type int -> option.Option.option int

      rest_code := (self__stmts_to_whyml_5 self rest local_refs declared_refs indent in_loop)
                                                     ^^^^^^^^^^ promoted to `map string`
      val statementemissionmixin___stmts_to_whyml … (local_refs: map int (option int)) …

The promoted parameter is PASSED ONWARD and the callee is still int-keyed — precisely the
sentence in `functions.py` ("it is forwarded to sibling `val` bridges … a `map string` here
would mistype the bridge") that this record had just declared measured and empty. The
measurement was real; the inference from it was not, and the difference is that a sweep
compares TEXT while a proof type-checks a PROGRAM.

### What that makes the item

κ=string must propagate along CALL EDGES. `local_refs` is threaded through the mirror's
entire statement/expression emitter — `_e`, `_expr_to_whyml`, `_expr_to_whyml_string_ctx`,
`_emit_body_code`, `_emit_array_local_reassign`, `_stmts_to_whyml` — every one of them
declared `local_refs: map int (option int)` today. Promoting one promotes all of them, which
moves most of the mirror and requires each moved file to be RE-PROVED;
`module6_whyml/expressions.py` alone is a measured **2h57m**.

So the repair is a module-level fixpoint with a double-digit-hour proof bill, not a one-line
deletion with two re-proofs. That is the size to carry, and it is a number rather than a
shrug.

**Ready for whoever builds it:** the mechanism (one line, confirmed by a prediction), the
exposure (ZERO read-only `Set[str]` params in either corpus; 39 in `\trusted` mirror stubs;
120 mirror functions already converted and proving), the ten-probe surface map, and two
witnesses — `1909` and `1910` — measured PASS on the patched tree with `1909` measured
FAILING on the live one.

## GATED, so it cannot be rediscovered

A measured gap that lives only in prose gets found again by the next reader from scratch.
This one is now three files in `bin/check-open-route-carriers.py` (5 carriers -> 8):

    setelem-carrier-read-only-str-set-membership.py   asserted FAILED
    setelem-control-mutated-str-set-membership.py     asserted SUCCESS
    setelem-control-int-set-membership.py             asserted SUCCESS

The carrier is NOT a false proof — it does not type-check, so nothing is certified and
nothing is unsound. It is gated like a route anyway, because the day it starts VERIFYING is
the day this record has to change, and the person who makes it verify is the one who should
change it. The plane says so in its own message: *"When this VERIFIES the I4 fixpoint has
landed: move all three files into the corpus as witnesses in the same commit"*.

The controls are the diagnosis, not decoration: one says the same membership works on a
MUTATED parameter (so the mechanism is `_mut_coll`), the other says `Set[int]` membership
works on a read-only one (so the mechanism is the ELEMENT TYPE, not the membership path).
Between them the carrier is localised to a single line of source without reading any.

Bite-tested: asserting the carrier SUCCESS makes the plane exit 1.

### The bill, re-measured after BOTH proofs finished — smaller than the first estimate

    module6_whyml/statements.py       8 s   FAILED   (one call edge)
    Module6_WhyMLTranspiler.py     40m43s   **SUCCESS**

The sweep said two mirror files move and no more; one of them re-proves clean. The section
above was written with the failing proof in hand and the passing one still running, and it
said "promoting one promotes all of them, which moves most of the mirror". That was an
estimate built from the half of the evidence that had arrived.

**The actual next step is one call edge**: `statements.py` line 1350 passes the promoted
`local_refs` to `_stmts_to_whyml`, whose own parameter is still `map int` because nothing in
ITS body tests a string key, so Module 5's usage tagger never fires for it. The propagation
rule is therefore exactly the one the source comment names — a parameter that RECEIVES a
κ=string argument is κ=string — and it is a module-level pass over call edges, not a rewrite
of the emitter.

Whether it cascades is a three-minute sweep away and is unmeasured. What is no longer true
is the double-digit-hour figure.

## THE ACTUAL MECHANISM: two extractors, the same rule, implemented in one

Chasing the call edge led to the real cause, and it is not a fixpoint at all.

`Module5_IREmitter` has TWO κ extractors, thirty lines apart:

```python
def _m5_get_dict_key_type(annotation):          # used for PARAMETERS
    if ... annotation.value.id in ("Dict", "dict") ... :
        if k.id == "str": return "string"
    return None                                  # <- a Set[str] gets None

def _m5_get_field_key_type(annotation):          # used for record FIELDS
    """…`Set[str]`/`FrozenSet[str]` → the element `str` (a set's element IS its key)…"""
    if head in ("Dict", "dict"):   return _m5_get_dict_key_type(annotation)
    if head in ("Set", "set", "FrozenSet", "frozenset"):
        if elt.id == "str": return "string"       # <- the set case, right here
```

**A set's element is its key — stated in the FIELD extractor's own docstring, and absent
from the PARAMETER one.** So a `Set[str]` parameter never gets κ from its DECLARATION; it
can only acquire it from Module 5's USAGE tagger, which fires on a membership with a
provably-string key. That is why `held.add(m)` works (the tagger fires, and `.add` also makes
the parameter by-reference), why `m in held` fails in a function that only reads, and why the
callee down the call edge never gets it either — `_stmts_to_whyml` passes `local_refs`
through and never tests it, so nothing tags it.

**This is the gen #31 shape for the fifth time**: one rule, stated correctly in two adjacent
places, implemented in one of them. (`finding-array-import-missing-for-a-list-field-only-program.md`
— the record decl from the FIELD; routes #148/#149 — the field type from an `__init__`
parameter; the `Dict[K, List[T]]` matrix; the set's read path versus its write path; and now
the parameter extractor versus the field extractor.)

### Probed: reading κ from the declaration makes the carrier VERIFY

With `_m5_get_field_key_type` used at the parameter site as well, and the `_mut_coll`
conjunct dropped:

    setelem-carrier-read-only-str-set-membership.py   **Verification SUCCESS**
    setelem-control-int-set-membership.py             Verification SUCCESS

No fixpoint, no propagation pass: both ends of a call edge read the same DECLARATION, so
they agree by construction. The remaining question is what the mirror does, and that is a
three-minute sweep rather than an argument.

## THE COMPLETE BILL, both halves measured

With BOTH halves — the parameter extractor reading a set's element type, and the
`_mut_coll` conjunct dropped — every exposure was swept:

    CORPUS   81 set/dict-annotated files emitted through both trees:  **1 MOVED**
             `0884.py` (expected-FAIL). Its `acc: Set[str]` goes
             `ref (map int (option int))` -> `ref (map string (option int))` and
             `map_update_some` becomes polymorphic. It still does not verify — but its
             FAILURE MODE CHANGES, from the frame failure the witness is about to a Why3
             TYPE ERROR. Lesson (m5) applies exactly: "expected-FAIL and still FAILED" is
             not a pass, and a witness that fails for a new reason has stopped witnessing.

    MIRROR   53 files swept:  **10 MOVED**, including
             module6_whyml/expressions.py          (a measured 2h57m to re-prove)
             module6_whyml/statements.py
             module6_whyml/functions.py
             module6_whyml/stmt_control_flow.py
             … and six more

So the bill is: ten mirror re-proofs, one of them three hours, plus a corpus witness whose
meaning has to be restored or re-stated. **The one-part change moved two files; the correct
two-part change moves ten.** Both numbers are in this record on purpose — the item's size
has now been estimated once and measured twice, and the measurements disagree with each
other in both directions.

NOT LANDED. What IS landed is everything needed to land it in one sitting: the mechanism
(one line in `Module5_IREmitter`, one in `functions.py`), the carrier triple gated in
`check-open-route-carriers.py`, the witnesses `1909`/`1910` measured both ways, the exact
mover lists above, and `$SCRATCH/g31/land_i4b.py` — the patch itself, written and probed.
