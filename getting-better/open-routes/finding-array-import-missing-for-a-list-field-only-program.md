# FINDING (#49, gen #31) — the record decl drives the imports, and TWO disjunctions say so
#                           while implementing it for one witness each
#
# `needs_array`: a class whose only array is a list FIELD emits `array` without importing it.
# `needs_seq`:   a dict FIELD whose values are lists emits `seq` without importing it.

**STATUS: LIVE, FAIL-CLOSED.** Not a soundness route — the file dies loudly — but a whole
shape of program cannot be verified at all, and the failure names a Why3 symbol rather than
anything the user wrote.

## The witness

```python
_ = 0  # anchor


#@ class invariant \length(self.xs) == 0
class C:
    def __init__(self) -> None:
        self.xs: list = []

    #@ ensures \result >= 0
    #@ assigns \nothing
    def n(self) -> int:
        return 0
```

    File ".pycsl_*.mlw", line 6, characters 25-30:
    unbound type symbol 'array'
    [-] Verification FAILED or INCOMPLETE.

The emitted preamble is

```
  use int.Int
  use int.EuclideanDivision
  use ref.Ref

  type c = { mutable xs: array int }
    invariant { ((Array.length xs) = 0) }
    by { xs = (Array.make 0 0) }
```

— `use array.Array` is absent while `array int`, `Array.length` and `Array.make` are all
used. The `use` list is evidently driven by the array locals/parameters/expressions of the
FUNCTION bodies, and a class FIELD (with its invariant and its `by` witness) does not put
anything into that set.

## Notes worth keeping

* The field path's empty-list witness is `(Array.make 0 0)` — the FAITHFUL length — which
  is the same length-0 spelling the sibling route
  (`route225-a-returned-empty-list-has-length-1024.md`) argues the VALUE form of `[]` should
  have. The emitter already writes it in one place; the two paths simply disagree.
* Both the TRUE invariant (`== 0`) and a FALSE one (`== 1024`) die at the same typecheck
  error, so nothing is proved either way — it is a completeness wall, not a false green.

## Shape of the repair

Add the class-field element types (and the `by` witness's constructors) to whatever set
decides the preamble `use` lines. The gate is the corpus byte-diff: a program that already
imports `array.Array` for another reason must stay byte-identical, so the rule has to ADD
to the set and never reorder it.

Measured 2026-09-24. Witness: `$SCRATCH/g31/orl/r.py`.

## FOUND IT — the condition is there, and it is restricted to ONE element type

`module6_whyml/preamble.py`, the `needs_array` disjunction (~line 1849), last disjunct:

```python
    # relaunch #16: a STRING-ELEMENT LIST FIELD (`StructFormat.slots: List[str]`) lowers
    # to `array string` in the record type decl, which is emitted whether or not any BODY
    # uses an array op — so the `use array.Array` must be pulled from the FIELD, not only
    # from the bodies. Without it the record decl itself is `unbound type symbol 'array'`.
    or any(_fd.get("type") in ("list", "tuple")
           and _fd.get("value_type") == "string"
           for _td in (self.ir.get("type_decls", []) or [])
           for _fd in (_td.get("fields", []) or []))
```

The diagnosis in that comment is exactly right and the guard is one conjunct too narrow:
`and _fd.get("value_type") == "string"`. An INT-element list field lowers to `array int` in
the same record decl and needs the same import. Relaunch #16 fixed the instance it had a
witness for (`StructFormat.slots: List[str]`) rather than the rule its own comment states.

**THE SAME SHAPE AS THE OTHER FOUR THIS SESSION** — a repair scoped to the witness rather
than to the mechanism (wall-lesson (s4)'s corollary: a repaired mechanism is not a repaired
route). The repair here is to delete the element-type conjunct.

GATE: the byte-diff decides. A corpus program with a list field and no other array use
cannot currently be in the PASSING corpus — it dies at `unbound type symbol 'array'` — so
the change should be corpus-byte-inert, and if it is not, the moved files are the ones to
read.

### CONFIRMED BY THE CONTROL

The identical program with ONE list PARAMETER added to the method — which trips the
`has_list_param` disjunct and nothing else — verifies:

```python
    #@ requires \length(ys) >= 0
    def n(self, ys: list) -> int: ...
```
    [+] Verification SUCCESS! All contracts formally proven.

So the field, its invariant `(Array.length xs) = 0` and its `by { xs = (Array.make 0 0) }`
witness are all fine; only the import is missing. **And note what that control also shows:
the field path's model of `[]` is length 0 and the TRUE invariant PROVES on it** — the
faithful behaviour the value path (`route225-a-returned-empty-list-has-length-1024.md`) had to
be repaired into.

### THE POPULATION, BEFORE LANDING (lesson d3)

89 files across both corpora, `src/pycsl`, `src/self-annotate/src` and `src/pycsl_lib`
declare a `list`/`List[...]`/`tuple`/`Tuple[...]` SELF FIELD — 133 sites. That is the set
the widened disjunct can reach, and it is large, so the byte-diff is not a formality here:
the change ADDS a `use array.Array` line to any of those files that did not already need
`array` for another reason.

Two things the gate must check, not assume:

  * the import's POSITION. `array.Array` must be emitted AFTER `map.Map` — both provide
    `([])` and the later import wins, so an `arr[i]` on an `array int` mis-resolves to
    `Map.get` if the order flips. The emission site already orders them; the byte-diff of
    any MOVED file must show the line in the right place.
  * an expected-FAIL corpus witness that fails *for this reason* would start PASSING and
    turn up as an XPASS. None is known, but the suite is what says so.

### THE COUNTER-PROGRAM TO CONSTRUCT BEFORE LANDING (lesson u4)

This change cannot FORBID anything — it only adds a `use` line — so the (u4) test takes a
different shape here: what program could the ADDED import break?

The emitter's own comment names it:

    # `array.Array` MUST be imported AFTER `map.Map` — both provide a `([])` operator, and
    # when both are in scope the later import wins. With map.Map imported last, `arr[i]` on
    # an `array int` is mis-resolved to `Map.get` …

So the program to build and run BOTH WAYS is **a class with a dict field AND a list field
whose body subscripts the dict** — today it dies on `unbound type symbol 'array'` and says
nothing, so the check is only possible after the fix is applied. If `d[k]` still resolves to
the map after `array.Array` joins the scope, the change is safe; if it does not, the
disjunct has to pull `use array.Array` without disturbing a map-only file's resolution.

Do not treat the corpus byte-diff as the answer to this one: the shape may simply be absent
(it would currently be a FAILING file, so it cannot be in the passing corpus) — which is
lesson (t4) in its own right.

### THE COUNTER-PROGRAM WAS BUILT, AND THE ORDERING CONCERN IS RETIRED BY MEASUREMENT

The class with BOTH a dict field and a list field, whose body subscripts the dict:

```python
class C:
    def __init__(self) -> None:
        self.d: Dict[str, int] = {}
        self.xs: list = []

    #@ requires \has_key(self.d, "k")
    #@ ensures \result == self.d["k"]
    def get(self) -> int:
        return self.d["k"]
```

**VERIFIES TODAY**, unchanged — and the reason is the point: `self.d["k"]` is a SUBSCRIPT,
and `uses_subscript` is already a `needs_array` disjunct, so `use array.Array` is already in
scope for it. Every program that can exercise the `([])` resolution order ALREADY imports
both theories; the widening can only add the import to files that use no subscript, no
`for`, no array literal and no array parameter at all. **There is no program whose
resolution order this change can flip**, which is a stronger statement than "the byte-diff
was clean" and is the kind the (u4) test is for.

What remains to gate is therefore only the ordinary one: the corpus byte-diff (89 files
across the tree declare a list/tuple self field, so the population is large) and an XPASS
check on the 31 expected-FAIL corpus files that declare one.

---

## IT IS A PAIR, NOT A SINGLETON — `needs_seq` HAS THE IDENTICAL BUG

Found while pricing an unrelated conversion. A class field annotated
`Dict[int, List[int]]` correctly resolves its value type to `seq int` (the resolver has
handled `Dict[K, List[T]]` since nested-map.md / #15) and then:

    unbound type symbol 'seq'

The `needs_seq` disjunction, TEN LINES BELOW `needs_array` in the same block, ends with the
same field clause and the same over-narrow conjunct:

```python
          or any(_fd.get("type") in ("list", "tuple")
                 and _fd.get("value_type") == "string"
                 for _td in (self.ir.get("type_decls", []) or [])
                 for _fd in (_td.get("fields", []) or []))
```

It covers a `List[str]` field (`seq string`) and NOT a DICT field whose value type is
`seq …`. Same shape, same relaunch, same comment ("the record decl is emitted from the
FIELD"), same one-witness scope.

**So the record-decl-drives-the-imports rule is stated correctly in the source, twice, and
implemented for exactly the two witnesses relaunch #16 had in hand.** Both repairs belong in
one increment: widen the `needs_array` clause to any `list`/`tuple` field, and add to
`needs_seq` any field whose resolved `value_type` starts with `seq `.

That second half also explains why nobody hit it: reaching it requires an ANNOTATED dict
field whose values are lists, and the unannotated spelling (`self.m = m`, typed only on the
`__init__` parameter) silently degrades the value type to `int` long before the import
matters — which is the OTHER gap, recorded in the backlog under the Module3_Weaver
conversion.

### THE (u4) TEST FOR THE SEQ HALF

Same shape as the array half and the same answer: the change can only ADD `use seq.Seq`,
and it can only add it to a file that uses no seq anywhere else — because every other
`needs_seq` disjunct (a `seq`-typed dict value on a FUNCTION, a seq-promoted var, a
`@mutable_state` class, a vararg `*str` param, a module string-list constant, a
str-literal-iterating body, `_uses_stmt_ir`) is a body- or signature-level use that already
pulls the theory. So no program whose `([])` resolution could shift is affected: the ones
that could are already importing it.

Witness `1879` (a class with `self.m: Dict[int, List[int]]`, PASS after the fix) fails
today with `unbound type symbol 'seq'`, measured.
