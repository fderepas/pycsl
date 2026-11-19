# ROUTE #99 — THE UB-7.7 MEMOIZATION GATE COLLECTS MUTATED FIELDS ONLY WHEN THE RECEIVER
# IS LITERALLY `self`, SO A FIELD MUTATED THROUGH ANY OTHER RECEIVER IS INVISIBLE AND THE
# STALE-CACHE UNSOUNDNESS ROUTE #94 CLOSED IS REOPENED

**SEVERITY 1. FOUND, REPRODUCED, MINIMAL PAIR MEASURED, POSITIVE CONTROL REFUSING FOR THE
RIGHT REASON, CPython CONTRADICTS A PROVED POSTCONDITION.** Found by the `continue`-census
generator — it is the FIFTH hit in five tries, and the census's own ranked candidate #3.

>>> **A CONFINEMENT/COLLECTION CHECK KEYED ON THE SYNTACTIC SHAPE OF A WRITE TARGET
>>> ENUMERATES THE SHAPES ITS AUTHOR HAPPENED TO PICTURE.** Generator #9 of the campaign,
>>> landing on the gate that route #94 built.

## THE ONE-LINE STATEMENT

A `@cached_property` reading `self.a` proves `#@ ensures \result == self.a` when `a` is
mutated by a free function taking the object as a PARAMETER (`def bump(c: C): c.a = c.a + 1`).
Make the very same mutation a METHOD (`self.a = self.a + 1`) and the gate REFUSES the file.
The mutation, the field, the cache and the contract are identical; only the RECEIVER differs.

## THE MINIMAL PAIR — THEY DIFFER ONLY IN THE RECEIVER OF THE WRITE

```python
class C:
    def __init__(self) -> None:
        self.a: int = 0

    #@ ensures \result == self.a
    #@ assigns \nothing
    @cached_property
    def total(self) -> int:
        return self.a
```

| mutator | receiver | verdict |
|---|---|---|
| `def bump(self): self.a = self.a + 1` (a METHOD) | `self` | **REFUSED** — `PyCSLIRError`, UB-7.7 gate fires |
| `def bump(c: C): c.a = c.a + 1` (a FREE FUNCTION) | `c` | **`Verification SUCCESS! All contracts formally proven.`** — `c__total'vc` postcondition **Valid** |

**CPython ground truth**, same program, foreign-receiver version:

```
before:     total = 0   a = 0
after bump: total = 0   a = 1
PyCSL PROVED  ensures \result == self.a   ->   total == a   is False
```

The cached value is stale exactly as route #94 described; the gate simply never saw the
mutation.

## THE MECHANISM, READ OFF THE SOURCE (not inferred)

`src/pycsl/frontend/module5/memoization_rt.py:92-98` — the collector:

```python
for g in funcs:
    if str(g.get("name", "")).rsplit("__", 1)[-1] == "__init__":
        continue
    ...
        if (cur.get("stmt") in ("FieldAssign", "FieldAugAssign")
                and cur.get("object") == "self"):        # <-- HERE
            mutated.add(cur.get("field"))
if not mutated:
    return                                                # <-- and the gate exits
```

`mutated` is a set of FIELD NAMES, and the consumer four lines below refuses a memoized
function reading any field in it. But a field is only ever ADMITTED to that set when the write
is spelled `self.<f> = …`. A write spelled `c.<f> = …` — the ordinary way a free function
mutates an object it was handed — is a `FieldAssign` with `object == "c"`, so it is skipped,
`mutated` stays EMPTY, and `if not mutated: return` disarms the whole gate before the
consumer runs.

>>> **THIS IS THE `continue`-CENSUS SIGNATURE FOR THE FIFTH TIME: ONE LOOP DOING TWO JOBS.**
>>> The `object == "self"` test is CORRECT for the job the loop was written for — finding the
>>> class's OWN mutators, which is what the `__init__` carve-out above it is reasoning about.
>>> It is a DELETED OBLIGATION for the verification the same loop feeds, because staleness is
>>> a property of THE FIELD, not of who writes it. The cache does not care which receiver
>>> dirtied the value.

## WHY IT SURVIVED ROUTE #94's OWN REVIEW — AND THIS IS THE PART WORTH CARRYING

Route #94's repair was careful and was negative-tested. Its docstring even records the harder
lesson it had already learned — that the first version of the repair lived in a per-function
visitor and *silently did nothing*, and that it had to be moved to the post-class hook. So the
author was explicitly thinking about **when** the population is assembled.

They were not thinking about **how wide** it is. The fix moved the collector to a place where
it could see all the functions, and then filtered those functions by a syntactic shape.

>>> **GETTING THE TIMING OF A POPULATION RIGHT AND ITS BREADTH WRONG PRODUCES A GATE THAT
>>> PASSES EVERY TEST ITS AUTHOR WROTE.** #94's witnesses (1257 self-mutator REFUSED, 1258
>>> construct-only field ACCEPTED) are both still correct and both still pass; neither one can
>>> see this hole, because both spell the mutation with `self`.

## STATUS

**CLOSED** (gen #16). Repair scoped below; outcome and residue at the end of this file.

## THE REPAIR, SCOPED

Key the collection on the PATH BEING WRITTEN, not on the receiver's spelling:

1. Admit a `FieldAssign`/`FieldAugAssign` to `mutated` whenever the object's STATIC TYPE is the
   class owning the memoized reader — or, conservatively and much more simply, admit it for ANY
   receiver, since `mutated` is already only a set of field NAMES and is already compared by
   name against the memoized function's reads. Admitting every receiver makes the gate
   strictly wider and can only add refusals.
2. **MEASURE THE COST OF (1) BEFORE LANDING IT.** Widening to any receiver will also catch a
   field of an UNRELATED class that merely shares a field name with the memoized reader's
   class. That is a false refusal, and route #94's own docstring warns against exactly this
   class of over-refusal ("a blanket field-read ban would delete that real capability — the
   corpus-1057 mistake"). So the name-only merge is the cheap version and the type-aware
   version is the correct one; census which is needed by counting shared field names across
   classes in the corpus.
3. **BOTH DIRECTIONS MUST BE MEASURED:** the foreign-receiver exploit must be REFUSED after the
   repair, AND witness 1258 (a `@cached_property` over a construct-only field) must still
   VERIFY — that is the real capability route #94 deliberately preserved.
4. The remaining residue after (1): a mutation through a receiver obtained from a container
   (`objs[0].a = 1`) or an attribute chain (`self.inner.a = 1`), whose `object` is neither a
   plain name nor `self`. Decide explicitly whether the collector sees those, and if it cannot,
   give the residue an OBSERVER rather than a comment — route #98's lesson.

## CLOSED — AND THE FIRST REPAIR WAS INCOMPLETE, WHICH IS THE FINDING

**THE ROUTE HAD TWO INDEPENDENT NARROWINGS AND ONLY FIXING BOTH CLOSED IT.** Fixing the
receiver test alone left the exploit PROVING; the measurement, not an argument, is what said
so:

| repair state | mutator BEFORE class | mutator AFTER class (the exploit) |
|---|---|---|
| at a32ec69e | (blocked by an unrelated fence, see below) | **PROVES** |
| receiver test widened only | **REFUSED** | **STILL PROVES** |
| + check moved to `visit_Module` end | REFUSED | **REFUSED** |

The second narrowing is the one worth carrying: route #94 put the check at the end of
`visit_ClassDef` and justified it in writing — *"by here `generic_visit` has emitted every
method of the class, **so the set is complete**."* Every method OF THAT CLASS is complete; a
module-level function defined after the class is not. **#94 moved the check ONE level
(function → class) when it needed to move TWO (function → class → MODULE).** Its own stated
lesson — *a check needing a whole-program fact cannot live in a per-node visitor* — was
exactly right, and **a class is still a node**.

## THE ORDERING HALF CANNOT BE ISOLATED BY A WITNESS — MEASURED, SO NOBODY RE-TRIES IT

Two attempts, both blocked by unrelated LOUD fences, both read rather than assumed:

* mutator declared BEFORE the class needs `def bump(c: "C")`, and at baseline the parameter
  emits as `int` (the class is not yet declared): `This expression has type int, but is
  expected to have type PyCSL_Program.c`.
* mutator AFTER the class with its parameter *named* `self` (so the old receiver test would
  pass and only ordering would hide it): `unbound function or predicate symbol 'self'` —
  `self` in a contract is special-cased to a method receiver.

>>> **A CONTROL THAT FAILS IS A CLAIM ABOUT THE CONTROL UNTIL YOU READ WHICH GOAL FAILED.**
>>> Witness 1283 was first committed claiming to isolate the ordering half. Reading its
>>> baseline failure reason showed it does not — it fails on a forward-reference type error.
>>> Its docstring now records what it actually measures.

## WITNESSES

* **1282** — the exploit (foreign receiver, mutator after the class). SUCCESS at a32ec69e,
  REFUSED now. Requires BOTH halves of the repair.
* **1283** — the standing record of the two isolation fences above. xFAIL both sides, for
  *different* reasons on each side, which the docstring states.
* **1284** — **CAPABILITY CONTROL, MUST PROVE.** A memoized reader of a construct-only field
  `k` while a foreign-receiver mutator writes a DIFFERENT field `a`. The widened collection
  must not refuse it — route #94's own warning was that "a blanket field-read ban would
  delete that real capability (the corpus-1057 mistake)". Measured SUCCESS.
* Pre-existing 0515, 0516, 1257, 1258 — the whole exposed population (only four corpus files
  use a memoizing decorator) — each re-measured and unchanged.

## RESIDUE, NAMED AND LEFT OPEN ON PURPOSE

`mutated` is still a FLAT SET OF FIELD NAMES, so an unrelated class's write to a field of the
same name refuses a memoized reader. **That over-refusal is PRE-EXISTING, not introduced
here** — the set was already global and name-keyed — and widening the receiver adds more of
the same kind, never a new kind. Census: 72 distinct field names across the corpora, **20
owned by more than one class** (`disk` 11, `x` 8, `v` 6, `n` 6). Keying `mutated` on
`(class, field)` pairs would fix the over-refusal in BOTH directions and is the right
follow-up; it is a widening of SCOPE, not of SOUNDNESS, so it is recorded here rather than
smuggled into a soundness repair.
