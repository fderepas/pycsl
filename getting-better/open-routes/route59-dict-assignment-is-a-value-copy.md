# ROUTE #59 — A DICT ASSIGNMENT IS A VALUE COPY, SO ALIASED MUTATION IS INVISIBLE

**STATUS: OPEN — REPAIR BUILT, FULLY MEASURED, STAGED AT `getting-better/staged-route59/`, NOT LANDED.** Found 2026-09-10 (gen #4). Reproduced twice at HEAD, mechanism read off
the emission, ground truth confirmed against CPython.

## THE ROUTE

```python
#@ ensures \result == 1          # FALSE of the program — and it PROVES
def f() -> int:
    a: Dict[int, int] = {1: 1}
    b: Dict[int, int] = a
    b[1] = 2
    return a[1]
```

CPython: `a is b` is `True`, so `b[1] = 2` mutates the one shared dict and `a[1]` is **2**.
The model proves `a[1] == 1`.

**BOTH DIRECTIONS MEASURED, which is what makes this a route rather than a gap:**

    \result == 1   FALSE of the program   ->  **PROVES**   (the unsoundness)
    \result == 2   TRUE  of the program   ->  fails        (so it is not merely incomplete)

## THE MECHANISM, READ OFF THE EMITTED WhyML

```whyml
let a = ref (map_update_some (const (None: option int)) 1 1) in
let b = ref !a in                     (* a NEW ref holding a COPY of a's VALUE *)
b := map_update_some !b 1 2;          (* updates b's own ref; a is untouched *)
(match Map.get !a 1 with | Some v_ -> v_ | None -> 0 end)
```

A Python dict is modelled as a PURE Why3 `map` held in a `ref`. `b = a` lowers to
`let b = ref !a` — a fresh reference initialised with the *value* of `a`. Mutation through
`b` writes `b`'s own cell. In Python both names denote the SAME object.

## WHAT MAKES THIS SHARP: THE LIST CARRIER IS CORRECT

The identical program over a `List[int]` is FAITHFUL — measured in the same session:

```python
a: List[int] = [1];  b: List[int] = a;  b[0] = 2;  return a[0]
```
    \result == 2   TRUE   ->  PROVES        \result == 1   FALSE  ->  fails

So this is not "reference semantics are unmodelled". Lists alias correctly (a shared
mutable `array`); dicts do not (a copied pure `map`). **The two collection types have
DIFFERENT aliasing semantics in the model and only one of them matches Python** — which is
exactly why probing the carriers of a working construct pays, and why the list result alone
would have been a false reassurance.

Callee mutation is ALSO correct for lists: `g(a)` where `g` does `x[0] = 2` under
`#@ assigns x[0..1]` proves `a[0] == 2` and refuses `a[0] == 1`.

## WHY NOTHING CAUGHT IT

* the CORPUS cannot see it — this is a semantic divergence, not an emission change;
* `check-param-mutator-visibility` measures a mutation made by a CALLEE, not aliasing
  between two locals in one frame;
* the mirror does not exercise it: the emitter's own dicts are not aliased and re-mutated
  this way, so every mirror proof stays green;
* and it fails in the SILENT direction — the false claim proves rather than the true claim
  failing, so no gate goes red.

## THE CARRIER CENSUS — DONE (gen #4, same session)

Every one measured in BOTH directions.

    **BROKEN — the false claim PROVES:**
      b = a;  b[1] = 2;  return a[1]              the original witness
      b = a;  a[1] = 2;  return b[1]              **SYMMETRIC** — it breaks whichever
                                                  name is mutated and whichever is read
      a -> b -> c;  c[1] = 2;  return a[1]        **CHAINS** through three names
      b = self.d;  b[1] = 2;  return self.d[1]    **THE FIELD CARRIER**, i.e. a dict
                                                  ATTRIBUTE aliased into a local

    **SAFE — fails closed in BOTH directions (a completeness gap, not a route):**
      g(a) where g does x[1] = 2, then return a[1]    the CALL carrier

So the route is NOT "dict mutation is unmodelled". It is specific to the ALIAS ASSIGNMENT,
and within that it is symmetric, transitive through chains, and reaches `self.<attr>` as
well as locals. A callee mutating a dict PARAMETER is undecided rather than wrong, which is
the safe direction — and notably the `List` parameter equivalent is fully FAITHFUL, so the
list/dict asymmetry shows up at the call boundary too.

## THE PATTERN EXISTS IN THE LIVE EMITTER — EXACTLY ONCE

A scan of `src/pycsl` for "alias a dict-typed local or `self.<attr>` into a name, then
subscript-store through that name" finds **one** site:

    src/pycsl/module6_whyml/statements.py::_mark_string_seq_locals
        svt = self._seq_value_types      then      svt[...] = ...

**It is NOT in the mirror at all** (no `_mark_string_seq_locals` there), so no mirror proof
is currently asserting something false on account of it — checked, because a live instance
inside the self-annotation would have been a much sharper finding than the route itself.
But it does mean repair option 1 changes real emitter behaviour at that site, and the
corpus byte-diff will see it. That is the first thing to measure when costing the repair.

## CANDIDATE REPAIR — NOT YET COSTED

Two shapes, and the cheap one may not be available:
1. lower a dict-to-dict local assignment as a REFERENCE bind (share the ref) rather than
   `ref !a`, matching the list/array treatment; or
2. REFUSE the aliasing assignment outright, which fails closed and costs only programs that
   alias a dict — the fails-closed direction the campaign prefers when a model is wrong.

## THE COST IS MEASURED, AND IT IS ZERO ON BOTH GATED POPULATIONS

Scanning for the alias assignment — an `x = y` whose RHS is a dict-typed local, or an
`x = self.<attr>` whose target is later subscript-stored:

    CORPUS   0 files, 0 sites      (over the whole test-suite corpus)
    MIRROR   0 files, 0 sites      (over all 53 self-annotate mirrors)
    LIVE     1 file,  1 site       src/pycsl/module6_whyml/statements.py
                                   ::_mark_string_seq_locals   `svt = self._seq_value_types`

**So a REFUSAL (option 2) is corpus-byte-inert BY MEASUREMENT, not by construction, and
owes no mirror re-proof either** — nothing in either gated population performs the
assignment it would refuse. That is an unusually cheap repair for a soundness route, and
it is the campaign's preferred direction when a model is known to be wrong.

The single LIVE site is emitter source, not a program the emitter lowers, so a refusal at
lowering time does not touch it. It matters only for option 1 (make the assignment a real
reference bind), and only if `_mark_string_seq_locals` is ever mirrored — it is not today.

**WHAT A REFUSAL DOES AND DOES NOT BUY.** It cannot make any currently-failing program
prove; it converts a WRONG ANSWER into NO ANSWER for programs nobody has written yet. That
is the whole point — the defect is that the model answers confidently and incorrectly, and
the corpus being empty of the shape is exactly why it went unnoticed for so long rather
than a reason to leave it.

**STILL REQUIRED BEFORE LANDING** (the byte-inert-corpus lesson: the mirror is a SECOND,
stricter population, and route #57 was correctly byte-inert AND ill-typed): run the corpus
byte-diff and at least a `why3 prove --type-only` on the mirrors, and confirm the emitted
`.mlw` set is unchanged rather than assuming it from the site count.

---

## OPTION 1 (SHARE THE REF) IS REFUTED BEFORE BUILDING — READ THIS FIRST

The obvious principled fix is to make the dict case do what the LIST case already does.
Side by side, from the emitted WhyML:

    LIST  (correct)                       DICT  (broken)
    let a = Array.make 1 1 in             let a = ref (map_update_some ...) in
    let b = a in        <-- SHARES        let b = ref !a in   <-- NEW ref, COPIED value
    b[0] <- 2;                            b := map_update_some !b 1 2;
    a[0]                                  Map.get !a 1

So "emit `let b = a` and share the ref" looks like a two-line change. **IT IS NOT SAFE, and
the reason is the mirror image of the defect itself.**

A Python dict local is REBOUND with the same syntax it is aliased with:

    a = {1: 1};  b = a;  b = {2: 2}      # rebinding b — `a` is UNCHANGED, a[1] is still 1

If `b` and `a` share one ref, the rebinding `b := ...` writes THROUGH to `a`, and the model
would then be wrong in the opposite direction — it would report `a` changed when Python says
it did not. Trading an unsound read for an unsound write is not a repair.

**THE LIST MODEL DOES NOT HAVE THIS PROBLEM, AND THAT WAS MEASURED TOO** rather than
assumed. `a = [1]; b = a; b = [3]; return a[0]` — true of the program is 1:

    \result == 1   TRUE   ->  fails          \result == 3   FALSE  ->  fails

Both directions fail, so list rebinding-after-aliasing is UNDECIDED, not wrong. The list
model gets away with sharing because a Why3 `array` binding is not reassigned through `:=`;
the dict model, built on a `ref`, would be.

**CONCLUSION: take option 2, the REFUSAL.** It is not merely the cheaper repair or the
campaign's stylistic preference for failing closed — it is the one that does not create a
second defect while closing the first. Any future attempt at option 1 must handle REBINDING
in the same change, and must re-run the four BROKEN carriers above plus this rebinding pair
in both directions.

This is the "probe your own repair for the gap it leaves" discipline (the one that found
route #58 an hour after #53) applied BEFORE the build rather than after it.

---

## THE `set` CARRIER — PROBED, FAILS CLOSED, BUT ONLY BY A TYPE ACCIDENT

A `set` is modelled by the same `map`-in-a-`ref` machinery as a dict, so it is the obvious
sibling carrier. Probed two spellings of the mutation, both directions:

    a: Set[int] = {1};  b = a;  b.add(2);   then  `2 in a`   -> emission dies on a type error
    a: Set[int] = {1};  b = a;  b |= {2};   then  `2 in a`   -> emission dies on a type error
                                                                (both the true and false twin)

CPython says `2 in a` is **True** in both cases — the alias mutates the one shared set.

So the set carrier is NOT currently a route, and the reason is that the aliased-set mutation
does not lower at all. **That is a type ACCIDENT, not a guard**, and it is the third one this
generation has had to write down as such (see also the `Optional` union carriers and the
mixed int/float arithmetic boundary).

**REOPENING CAPABILITY:** the moment an aliased set becomes mutable-and-lowerable — `.add`
through a second name, or `|=` — the set carrier inherits route #59 immediately, because it
shares the copy-on-assign lowering. The staged repair already covers it: its guard tests
`_field_type_of(...) in ("dict", "set", "frozenset")` and the `_dict_locals` membership that
`_rhs_yields_map` populates for sets too. Re-run these two probes after any change to set
lowering.

---

## THE RETURN CARRIER IS ALSO BROKEN, AND THE STAGED REPAIR DOES **NOT** COVER IT

Found by probing the staged repair for the gap it leaves — the discipline that produced
route #58 an hour after #53. It pays again here.

```python
@mutable_state
@dataclass
class C:
    d: Dict[int, int] = field(default_factory=dict)

    def get(self) -> Dict[int, int]:
        return self.d                 # hands out the INTERNAL dict

    #@ ensures \result == 1           # FALSE of the program — and it PROVES
    def probe(self) -> int:
        self.d[1] = 1
        m: Dict[int, int] = self.get()
        m[1] = 2
        return self.d[1]              # CPython: 2
```

Reproduced twice. Both directions measured: `\result == 1` PROVES, `\result == 2` fails.

Emission:

```whyml
self.d <- map_update_some self.d 1 1;
let m = ref (self_get_0 ()) in        (* a FRESH ref over the RETURNED VALUE *)
m := map_update_some !m 1 2;          (* writes m's own cell *)
(match Map.get self.d 1 with ...)     (* self.d never saw it *)
```

**WHY THE STAGED GUARD MISSES IT.** That guard fires when the RHS of the binding is a bare
`Var` or a `self.<field>` read. Here the RHS is a **Call**, so nothing matches — the same
copy-on-bind happens one syntactic step away. Exactly the shape of route #58 relative to
#53: *a repair covers the PATH it edits, not the SEMANTICS it means to fix.*

**THIS MATTERS FOR ANYONE ABOUT TO LAND `staged-route59/`:** landing it closes the ALIAS
ASSIGNMENT carriers and DOES NOT CLOSE THE ROUTE. Handing out an internal collection from a
getter is one of the most common patterns in real Python, so this carrier is arguably more
reachable than the one the repair was built for.

**EXTENDING THE REPAIR.** The same mutation gate applies — refuse a binding whose RHS is a
call returning a dict/set when a later statement stores through the bound name. The
information needed is already at hand: `_first_assign_kind` returns "dict" for such a call
(via `_rhs_yields_map`'s Call branch and the module return-type map), so the guard only has
to stop keying on the RHS *node kind* and key on "kind == dict AND the RHS is not a fresh
construction" instead — a `DictLit`, `dict()`/`set()` Call, or a comprehension being the
fresh cases. **That inversion must be measured against the mirror before it is believed:
the read-only-rebind lesson says the corpus will stay clean while the mirror decides.**
