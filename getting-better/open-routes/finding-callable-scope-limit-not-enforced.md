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

## 2026-09-24 — THE CAPABILITY IS CHEAPER THAN THE NOTE ABOVE PRICES IT

The note says the check "needs the record/variant table, and that table lives in Module 6",
and prices the repair as a Module-6 refusal at the point where the default happens —
`module6_whyml/functions.py::_callable_tag_to_whyml`:

```python
        # Unknown bare name — sound fallback to `int`; Why3 rejects a mismatched
        # application rather than admitting an unsound type.
        return "int"
```

That site is the right DIAGNOSIS and the wrong PLACE, for a reason lesson (n4) exists to
catch: **`_callable_tag_to_whyml`'s mirror twin is UN-TRUSTED** (`#@ requires True /
ensures True / assigns \nothing`, no `\trusted`), so a `raise` added there is a verbatim
body port that must itself PROVE, plus a whole-file re-proof of
`module6_whyml/functions.py`. That is the expensive half of the seam, and it is exactly the
shape that broke `_check_lemma` twice.

**The table is not actually Module-6-only.** `_record_types` / `_variant_types` are BUILT
from `ir_data["type_decls"]`, which `_run_pipeline` already holds — the same dict the
`#@ datatype` exhaustiveness check reads. So the admissible set is

    {"int", "bool", "str", "float"} ∪ {td["name"] for td in ir_data["type_decls"]}

and the refusal belongs at the `_run_pipeline` choke point, whose mirror twin is `\trusted`
and already in the raises-honesty population: no marker, no emission move, no re-proof.
The `callable:` tags are on the function/param symtypes in the same IR.

GATE, unchanged from the note above: zero corpus, `src/`, mirror and `pycsl_lib` sources
annotate a `Callable` over a bare collection name, and the four `Callable` negatives cover
other shapes — but the UNKNOWN-CLASS census still has to be taken before landing, because
this half fires on a different population than the one already measured.

### AND THE CENSUS IS DONE — ZERO

AST scan of `test-suite/corpus`, `src/pycsl`, `src/self-annotate/src`, `src/pycsl_lib` and
`tests`: **17 files contain a `Callable[...]` annotation, and exactly TWO name something
that is neither a builtin tag (`int` `bool` `str` `float` `None` `Any`) nor a class or
`#@ datatype` declared in the same file — `List` and `bytes`.** Both are the COLLECTION
half that is already repaired (the corpus `Callable` negatives), and neither is a class
name at all.

So the unknown-CLASS half has **no occurrences anywhere in the tree**: the refusal is
byte-inert by construction, the same way the collection half was. Nothing is left to price.

Remaining work: the `_run_pipeline` check above (admissible set = the four builtin tags
plus `{td["name"] for td in ir_data["type_decls"]}`), its message, and a witness/control
pair in the corpus (`Callable[[Rekt], int]` for a `Rekt` that does not exist, which today
verifies while emitting `f: int -> int`).

### AND THE SAME TEST APPLIED HERE — TWO ADDITIONS TO THE ADMISSIBLE SET

An hour after the `#@ datatype` exhaustiveness item was RETIRED for exactly this reason
(a clean census of what exists, and a rule that would have forbidden a good program —
wall-lesson (u4)), the same test was run on this one: construct the strongest program the
refusal would forbid, and check whether it is good.

Two came back GOOD, and both verify today:

  * **an IMPORTED class.** `Callable[[Box], int]` with `Box` defined in another unit and
    reached through `--import-path` verifies, and the emission carries
    `type box = { mutable n: int }` — so import resolution has already put `Box` into
    `ir_data["type_decls"]` by the time `_run_pipeline` runs. Admissible for free; the
    check had to be measured, not assumed.
  * **a TYPEVAR.** `Callable[[T], int]` with `T = TypeVar("T")` verifies today, and a set
    built from `type_decls` alone would have refused it. `typevar_registry`, the PEP 695
    `type_params` on a function, and a parametric datatype's `type_params` are therefore
    part of the admissible set.

The refusal is still worth landing — a name that is NOT a class, NOT a datatype, NOT a
typevar and NOT a primitive tag has no reading under which `int` is the right answer — but
the census (17 files, two hits, both the already-repaired collection half) was NOT what
established that. **The census bounds the damage to today's tree; only the constructed
counter-programs say whether the rule is right.**

### THE PATCH AND ITS WITNESSES ARE DRAFTED

`$SCRATCH/g31/fix_callable_scope.py` (the `_run_pipeline` check, with the widened
admissible set) and `$SCRATCH/g31/w/187{7,8}.py`. Both witnesses were run against TODAY's
tree so the before-state is measured, not assumed:

| file | today | expected after |
|---|---|---|
| 1877 — `Callable[[Rekt], int]`, `Rekt` undeclared, body `return f(x)` under `#@ requires f(x) >= 0` | **SUCCESS** (the route) | REFUSED |
| 1878 — the same with `Box` declared | SUCCESS | SUCCESS |

Note that both are NON-VACUOUS: the precondition `f(x) >= 0` is what discharges the
postcondition, so the arrow is genuinely applied rather than merely declared. The first
draft returned a constant and would have proved nothing about the `Callable` at all.
