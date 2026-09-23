# FINDING (#49, gen #31) — the `Callable` C5 scope limit was half a rule

**STATUS: FOUND, MEASURED, PARTLY REPAIRED IN THE SAME SESSION** (witness `1852`, controls
`1853`/`1854`). Not a soundness route. The unrepaired half is named at the end with the
reason it was not attempted.

## THE CLAIM

annotations.md §12.17, **Static plane (Interpreted)**:

> Scope limit (C5): only `int`/`bool`/`str`/`float` and record/variant names are admissible
> as arg/return types (stricter than S1, sound; `bytes`/`list`/`dict`/`set`/`Any`/
> nested-`Callable`/ellipsis rejected with `PYCSL-TY3-CALLABLE-SCOPE`).

## THE MEASUREMENT

| annotation | verdict |
|---|---|
| `Callable[[int], int]` | SUCCESS (admissible) |
| `Callable[[Rec], int]` for a real record | SUCCESS, emits `f: py_rec -> int` (admissible) |
| `Callable[[Any], int]` | REFUSED `PYCSL-TY3-GT1` ✓ |
| `Callable[..., int]` | REFUSED ✓ |
| `Callable[[Callable[[int], int]], int]` | REFUSED ✓ |
| `Callable[[List[int]], int]`, `Dict[...]`, `Set[...]` | REFUSED ✓ |
| **`Callable[[bytes], int]`** | **SUCCESS** |
| **`Callable[[list], int]`** | **SUCCESS** |
| **`Callable[[dict], int]`** | **SUCCESS** |
| **`Callable[[set], int]`** | **SUCCESS** |

The subscripted collection forms were refused **only because they are `ast.Subscript`
nodes**, which is a different rule. The BARE names are `ast.Name`, so `_callable_type_tag`
fell through to `return tag`; Module 6 then found no record or variant of that name and
defaulted the arrow domain to `int`. All four emit

```whyml
  let function apply (f: int -> int) (x: int) : int
```

— byte-identical to `Callable[[int], int]`.

The class constant `_CALLABLE_SCALAR_TAGS = frozenset({"int", "bool", "str", "float"})`
sits two screens above the check and is **referenced nowhere in the file**: the residue of
the rule the documentation describes.

## THE REPAIR

An explicit equality chain in `_callable_type_tag` over the seven collection builtins
(`bytes`, `bytearray`, `list`, `dict`, `set`, `frozenset`, `tuple`), refusing with
`PYCSL-TY3-CALLABLE-SCOPE` and a message that says what the domain silently became.

An equality CHAIN rather than a set membership or a `frozenset` literal, because this
method's mirror twin is UN-TRUSTED and a verbatim body port — route #218's dunder-hook test
is written the same way and for the same reason (`==` lowers through `str_eq_op`; a set
literal does not).

CENSUS BEFORE LANDING: zero corpus, `src/`, mirror and `pycsl_lib` sources annotate a
`Callable` over a bare collection name; the corpus's four `Callable` negatives cover the
bad-subscript form, a `List[int]` domain, a `"Nope"` string return and `Any`. Byte-inert.

## THE HALF THAT IS NOT REPAIRED, AND WHY

**A typo'd or otherwise unknown CLASS name is still silently `int`.**
`Callable[[Rekt], int]` — for a `Rekt` that does not exist — verifies and emits
`f: int -> int`, exactly as `bytes` did.

Refusing it needs the record/variant table, and that table lives in **Module 6**
(`_record_types`/`_variant_types`), not in the Module 5 emitter where this check sits —
`_callable_type_tag`'s own comment says so: "Module 6 resolves the class name against the
known record/variant types". A Module-5-local guess would also have to cope with a class
declared LATER in the file than the annotation.

So the capability is named rather than half-built: **move the admissibility test to the
point where `_record_types`/`_variant_types` are populated, or have Module 6 refuse an
unresolved `callable:` tag instead of defaulting its domain to `int`.** The second is
probably the smaller change and is where the default currently happens.

Not a route either way: a wrong domain makes the WhyML arrow disagree with the argument at
the call site, and Why3's typechecker rejects that — the same accident that keeps the
legacy-`Generic[T]` finding from being a route. Worth repairing for the same reason: a
silent `int` for a name the user wrote is a diagnostic failure, and the guarantee is
resting on the backend rather than on the rule.

Measured 2026-09-23.
