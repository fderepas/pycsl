# FINDING (#49, gen #31) — a `List[T]` taken OUT of a `Dict[K, List[T]]` cannot be passed to anything

**Not a route: nothing false is certified.** It is a completeness wall, and it is the
current floor of the `\trusted` conversion track, so it is recorded with its measurements
rather than as a note in a log.

## The twenty-line witness

```python
#@ ensures \result >= 0
def total(xs: List[int]) -> int:
    return len(xs)

class C:
    def __init__(self, m: Dict[int, List[int]]) -> None:
        self.m: Dict[int, List[int]] = m

    #@ ensures \result >= 0
    def g(self, k: int) -> int:
        return total(self.m[k])
```

    This expression has type seq.Seq.seq int,
    but is expected to have type array.Array.array int @rho

The FILE is refused — this is a type error in the emitted module, not an unproven goal.

## Two models of "a Python list", and no bridge

| where the list appears | WhyML type |
|---|---|
| a parameter or local annotated `List[T]` | `array T` (mutable, `@rho` region) |
| the VALUE of a `Dict[K, List[T]]` | `seq T` (immutable) |

Both choices are defensible on their own. A Python list is mutable, so a parameter must be
an `array`; a Why3 `map` is a LOGIC value and cannot hold a mutable program array, so a dict
value must be a `seq`. What does not exist is any operation that turns one into the other,
so the moment a list LEAVES a dict it can be read (`len`, indexing) and passed to nothing.

## The second, separable blocker underneath it — repaired in the same sitting

Before the error above is even reached, the SELF-FIELD dict subscript emits an int
placeholder for the missing key:

    match Map.get self.contracts_map (get_lineno node) with | Some v_ -> v_ | None -> 0 end
                                                                               ^^^^^^^^^^
    This expression has type int, but is expected to have type seq.Seq.seq int

`_dv_missing_default(nu)` is the consolidated per-ν placeholder and already answers
`string`, `hval`, `emit_ir`, `seq …` and `map …`. The self-field branch in
`expressions.py` (~14643) re-implemented TWO of those five inline and had no arm for the
rest. Patch held at `$SCRATCH/g31/fix_selffield_dict_default.py`; the two inline arms are
byte-for-byte what the helper returns for the same ν, so it is behaviour-preserving where
there was an answer and additive where there was not.

## Why this is the conversion track's floor

`PyCSLWeaver.visit_FunctionDef` is the cheapest `\trusted` stub in the mirror to convert —
five live lines, in the mirror file that proves fastest. Its body is

    if node.lineno in self.contracts_map:
        self._dispatch_function_contracts(node, self.contracts_map[node.lineno])

i.e. exactly "take a `List[CSLNode]` out of a `Dict[int, List[CSLNode]]` and pass it".
THREE blockers were found by building it on an offline copy of the tree, in this order:

  1. `self.m = m` from an annotated `__init__` parameter loses the annotation
     (`Module5_IREmitter._collect_class_fields` infers from the RHS SHAPE alone) —
     patch `$SCRATCH/g31/fix_field_param_ann.py`, censused, corpus-byte-inert;
  2. the missing-key placeholder above — patch `fix_selffield_dict_default.py`;
  3. **this one**, which is a modelling decision and not a bug.

So the conversion is not landable as a patch. Either the callee takes the `seq` (and then
the mirror's `_dispatch_function_contracts` stub's annotation carries a type the live
signature does not, which the mirror-sync checker permits — it strips annotations — but
which would make the mirror's contract a statement about a different function), or the two
list models get a bridge, which is a design question and not an increment.

RECORDED AS THE ANSWER TO "why has the `\trusted` count not moved": it is not that no stub
is cheap. The cheapest stub in the tree is five lines, and it needs two patches and a
modelling decision. Measured 2026-09-24; witnesses `$SCRATCH/g31/treeconv/pl.py` and the
mirror trial in `$SCRATCH/g31/conv_trial2.log`.

## THE 2x2 THAT LOCATES IT: the ELEMENT type, not the key type, not the declaration site

`self.m.get(k, [])` bound to a local, then `len(fp)`, `#@ ensures \result >= 0`, on the live
tree — four files differing in one annotation:

| field annotation | verdict |
|---|---|
| `Dict[str, List[str]]` | **SUCCESS** |
| `Dict[int, List[str]]` | **SUCCESS** |
| `Dict[str, List[int]]` | FAILED — `seq int` where `int` expected |
| `Dict[int, List[int]]` | FAILED — same |

The KEY type is irrelevant and so is the declaration site (an `__init__` AnnAssign behaves
exactly like a `@dataclass` class-body field; `0746.py` is the corpus's working instance and
an `__init__`-declared twin of it also verifies). **The discriminator is the ELEMENT type.**

`statements.py` ~5900 promotes a list local to `_seq_locals` — the set `len()` lowers with
`Seq.length` — under

    if (_acounts.get(_nm, 0) >= 2
            or (_et == "string" and _is_seq_src(_firstv.get(_nm)))
            or (_et == "emit_ir" and self._uses_pyast_parser()
                and _is_seq_src(_firstv.get(_nm)))):

so a SINGLE-assign local gets promoted when its element type is `string` (or `emit_ir`, and
that one is file-gated) and not otherwise. A `seq int` local is left in the array model and
`len` then falls through to the array branch.

**This is the third instance this generation of one shape**: a rule stated correctly in
prose and implemented for the element type the first witness happened to have. The other two
were `needs_array`'s `and _fd.get("value_type") == "string"` conjunct and its `needs_seq`
twin ten lines below — both repaired, both found the same way, by a witness that used the
feature with a different type.

NOT ATTEMPTED HERE, deliberately. The comment on that branch says the emit_ir disjunct is
file-gated because un-gating it "re-shaped `stmt_control_flow`'s `_body_d`" — i.e. the
promotion set is load-bearing for emission everywhere, and widening `string` to `int` is a
full-corpus byte-diff question, not a patch. Priced and recorded; the queue already holds
four gated increments.

## THE SUBSCRIPT FORM FAILS EVEN WHERE `.get` WORKS — so the placeholder patch has no green witness

The 2x2 above used `self.m.get(name, [])`. Replacing it with the SUBSCRIPT `self.m[name]`,
keeping the working `Dict[str, List[str]]` annotation:

    fp = self.m[name]; return len(fp)
      LIVE     FAILED — `This expression has type int, but is expected to have type
                         seq.Seq.seq string`     (the `| None -> 0` placeholder)
      PATCHED  FAILED — `This expression has type seq.Seq.seq string, but is expected to
                         have type int`           (`len` on a seq local that was never
                                                   promoted to `_seq_locals`)

So `fix_selffield_dict_default.py` is correct and it **has no green witness**: it moves a
file from one type error to the next one. That is recorded here and the patch is NOT landed.
A patch whose only evidence is "the error message changes" is not an increment — the same
standard that let the field-param fix land once it got `1896`/`1897`.

The working matrix as it stands, all on a `@mutable_state` class with the field declared in
`__init__`:

| read form | `List[str]` values | `List[int]` values |
|---|---|---|
| `self.m.get(k, [])` then `len(local)` | **SUCCESS** | FAILED (promotion is `string`-only) |
| `self.m[k]` then `len(local)` | FAILED (placeholder, then promotion) | FAILED |
| a dict PARAMETER, `len(m[k])` | SUCCESS | **SUCCESS** |

The parameter row is the one that works for both element types, and it is the row that has
an explicit branch (`expressions.py` ~6410, `_dict_value_types[var] == "seq int"`). Every
FAILED cell is a missing branch beside a present one, not a design limit — except the
`seq`/`array` wall at the top of this file, which is.
