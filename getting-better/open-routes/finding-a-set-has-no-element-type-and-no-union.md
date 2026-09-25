# A `Set[T]` has no element type, and no union

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
not work is the ELEMENT TYPE. A `Set[str]` lowers to the same `map int (option int)` a
`Set[int]` does, and the `str` member is then a type error at the use site — the set's own
declaration never carried the element type at all.

This is the third position of a mechanism this campaign keeps meeting: route #148/#149
repaired a FIELD whose type came from an `__init__` parameter, and
`finding-a-list-out-of-a-dict-cannot-be-passed-anywhere.md` carries the matrix of which read
forms work for which element types. Here the container is a set and the answer is that there
is no element type to get wrong.

## Wall 2 — set UNION is not modelled, for any element type

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
`|` operator produces the map itself where an `int` is expected, i.e. the union has no
lowering and the expression falls through to the scalar path. Both `Set[str]` and `Set[int]`
fail identically.

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
    held | other        Set[int]    FAILED    map where an int is expected
    held & other        Set[int]    FAILED    "
    held - other        Set[int]    FAILED    "
    held ^ other        Set[int]    FAILED    "
    held.union(other)   Set[int]    FAILED    "
    held.intersection(other)        FAILED    "
    len(held)           Set[int]    FAILED    "
    m in held           Set[str]    FAILED    string where an int is expected

**Membership and `add`. That is the entire modelled surface of a Python set.** Every binary
operator, every named equivalent of one, and `len` all fail the same way — the set's map
falls through to the scalar path — and the element type is `int` no matter what the
annotation says.

Stated that way the conversion consequence is not "one operator is missing" but "a set is a
bag you can put things in and ask about, and nothing else", which is a different size of
build and a different sentence to put in a backlog. The four probes were written to settle
one function's chain; the ten were written because four probes that all fail the same way is
a reason to ask how far the sameness goes.

`held.add(m)` verifying is the interesting half: MUTATION of a set parameter is modelled,
with a `#@ assigns held` frame, while reading its size is not.
