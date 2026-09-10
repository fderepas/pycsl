# ROUTE #59 — A DICT ASSIGNMENT IS A VALUE COPY, SO ALIASED MUTATION IS INVISIBLE

**STATUS: OPEN. A PARTIAL REPAIR IS BUILT, FULLY MEASURED AND STAGED AT
`getting-better/staged-route59/` — NOT LANDED, AND LANDING IT DOES NOT CLOSE THIS ROUTE.**
It closes the ALIAS ASSIGNMENT carriers. The RETURN carrier (a getter handing out an
internal dict) is measured broken and is NOT covered — see the section near the end. Found 2026-09-10 (gen #4). Reproduced twice at HEAD, mechanism read off
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

## THE LIST CONTROL FOR THE RETURN CARRIER — SAFE, AND IT COMPLETES THE PICTURE

The same getter-hands-out-an-internal-collection shape at the `List` carrier:

    m = self.get();  m[0] = 9;  return self.a[0]      CPython: 9
    \result == 9  TRUE  -> fails        \result == 1  FALSE -> fails

Both directions fail, so it is UNDECIDED rather than wrong. Combined with the earlier
carriers this gives the whole comparison, and it is clean:

    carrier                     List                          Dict
    ------------------------    --------------------------    --------------------------
    local alias, then mutate    CORRECT (true twin proves)    **UNSOUND** (false proves)
    symmetric / chained         CORRECT                       **UNSOUND**
    field aliased into a local  (n/a, same as above)          **UNSOUND**
    callee mutates a param      CORRECT (true twin proves)    undecided (safe)
    getter returns internal     undecided (safe)              **UNSOUND**
    rebind after alias          undecided (safe)              (would break if ref shared)

    slice copy `b = a[0:1]`     CORRECT (see below)            (dict slicing has no analogue)

**AND THE COMPLEMENT DIRECTION IS ALSO CORRECT FOR LISTS.** `b = a[0:1]` must produce an
INDEPENDENT list in Python — the mirror image of #59, where sharing rather than copying
would be the defect:

    a = [1];  b = a[0:1];  b[0] = 9;  return a[0]      CPython: 1
    \result == 9  (FALSE, i.e. aliased)  -> fails      \result == 1  (TRUE) -> **PROVES**

So the model copies where Python copies and shares where Python shares, for lists, in every
carrier probed. The dict/list asymmetry really is about the DICT's copy-on-bind and nothing
more general.

**LISTS ARE NEVER WRONG — they are either faithful or undecided. DICTS ARE WRONG IN THREE
OF SIX CARRIERS.** That is the sharpest statement of route #59, and none of it would have
been visible from probing a single carrier: the very first list probe came back FAITHFUL and
would have been read as "reference semantics are modelled" had the census stopped there.

## THE RETURN CARRIER'S POPULATION COUNT — ZERO EVERYWHERE

Scanning for "a method whose body returns `self.<attr>` where that attribute is dict/set
typed": **0 in `src/pycsl`, 0 in the mirror, 0 in the corpus.**

Two consequences, and both matter for whoever extends the repair:
  * no mirror proof is currently false on account of this carrier — checked, not assumed,
    because a live instance inside the self-annotation would outrank the route itself;
  * extending the guard to cover it should be BYTE-INERT on both gated populations, exactly
    as the alias-carrier repair measured. That does not remove the obligation to MEASURE it
    — the first build of the alias repair had a clean corpus diff and still killed the
    mirror.

So both halves of route #59 are, today, defects nobody has tripped. That is the argument
for fixing them now rather than after someone writes the obvious Python.

---

## ROUTE #59 IS RULE **R1/R3** OF A DISCIPLINE THIS PROJECT ALREADY WROTE DOWN — AND ONLY **R2** IS ENFORCED

`docs/pycsl-ownership-discipline.md` §2 lists what is **rejected (out of scope)**:

    (R1) Shared mutable aliasing.  "Two live references to one mutable object, both written
         (`a = b; a.append(1); b.append(2)`; or storing a list in a dict *and* keeping the
         original and mutating both). The interleaving is observable and not value-expressible."
    (R2) Mutable default arguments (`def f(x, acc=[])`) — a hidden cross-call shared object.
    (R3) Mutate-through-alias of a stored object — `self.x = p` then later `p.append(...)`
         expecting `self.x` to change.

**Route #59 IS R1, and its field/return carriers ARE R3.** So the defect is not that the
boundary was never considered — it is that **the boundary is DOCUMENTED BUT NOT ENFORCED**,
and the tool answers inside it anyway.

**R2 IS ENFORCED. MEASURED:**

    def g(x: List[int] = []) -> int: ...
    [!] PIPELINE ERROR: Mutable default argument in function 'g': a list/dict/set default
        is a single object shared across all calls (a shared-aliasing bug) and is outside
        PyCSL's value-semantics boundary (ownership discipline R2). Use a `None` sentinel...

There is even a corpus witness for it, marked `# pycsl-expected: FAIL`. So one of the three
rules refuses, and the other two — the ones route #59 lives in — silently return
"Verification SUCCESS" on a false postcondition.

**THIS ALSO QUALIFIES A SOUNDNESS CLAIM THE DOC MAKES.** §3 states the snapshot semantics is
"a **sound under-approximation**: it never proves a false postcondition, because it models
*less* sharing than Python has". Measured, that sentence holds only WHEN THE BOUNDARY IS
ENFORCED. It is not, for R1/R3, and `\result == 1` proves where CPython answers 2. An
under-approximation of sharing is sound only if programs that exceed it are REFUSED; if they
are accepted, modelling less sharing is exactly how a false postcondition gets proved.

**WHAT THIS CHANGES ABOUT THE REPAIR — IT IS NOT A NEW RESTRICTION.** The staged patch does
for R1/R3 precisely what the emitter already does for R2: refuse, with a diagnostic naming
the discipline. It removes no capability the project ever claimed to have; it makes an
already-declared boundary honest. That is a considerably easier thing to justify landing
than a new refusal would be, and the R2 diagnostic is the template its message should follow.

**FOLLOW-UP FOR THE NEXT RELAUNCH:** R3's other spelling — `self.x = p` (p a mutable local)
followed by `p[...] = ...`, i.e. the STORE direction rather than the READ direction probed
here — is not yet measured. The staged guard fires on `b = self.d`, not on `self.d = b`.

## R3's STORE DIRECTION IS BROKEN TOO — A FIFTH CARRIER, ALSO UNCOVERED

The follow-up recorded above, measured. This is the spelling the ownership doc names
verbatim (`self.x = p` then later mutate `p`):

```python
    #@ ensures \result == 1        # FALSE of the program — and it PROVES
    def probe(self) -> int:
        p: Dict[int, int] = {1: 1}
        self.d = p                 # STORE the local into the field
        p[1] = 2                   # then mutate the local
        return self.d[1]           # CPython: 2
```

Reproduced twice; the true twin (`\result == 2`) fails. Emission:

```whyml
let p = ref (map_update_some (const (None: option int)) 1 1) in
self.d <- !p;                          (* the field gets a COPY of p's value *)
p := map_update_some !p 1 2;           (* p's own ref moves on *)
(match Map.get self.d 1 with ...)      (* the field never saw it *)
```

**THE STAGED GUARD DOES NOT FIRE**, because it inspects a LOCAL BINDING whose RHS is a dict;
here the assignment TARGET is a field. Third carrier the repair misses, after the getter
return.

### THE CARRIER TALLY, KEPT HONEST

    BROKEN, covered by the staged patch:      local->local, symmetric, chained, field->local
    BROKEN, NOT covered:                      getter return (`m = self.get()`)
                                              field store  (`self.d = p`, then mutate p)
    SAFE (undecided):                         callee mutates a dict parameter
    SAFE by a type accident only:             the whole `set` carrier

**Six broken carriers, four covered.** The staged patch is worth landing for the reduction,
and route #59 stays OPEN until the two Call/field-target carriers are closed too. Both share
one cause with the four already handled — the binding copies a pure map — so a single
generalisation ("a dict-valued binding whose RHS is not a FRESH construction, where either
side is later mutated") should close all six. It must be measured against the MIRROR, not
the corpus: every version of this repair so far has had a clean corpus diff.

## COSTING THE GENERALISED REPAIR — AND A FALSE POSITIVE I HAD TO CORRECT IN MY OWN SCAN

The generalisation that would close all six carriers has two new parts. Both are costed at
ZERO on the two GATED populations:

    RHS is a CALL returning a dict, bound then mutated
        LIVE 0 · MIRROR 0 · CORPUS 0
    TARGET is a FIELD (`self.d = p`), the local mutated AFTER the store
        LIVE 1 · MIRROR 0 · CORPUS 0

**THE MIRROR NUMBER STARTED OUT AS 1 AND WAS WRONG.** My first scan asked "is this local
mutated anywhere in the function?" and flagged
`module6_whyml/functions.py::_refine_tuple_return_type`, which is NOT `\trusted` — i.e. a
VERIFIED mirror method apparently exercising the route. That would have outranked the route
itself. Reading the body killed it:

    _st = dict(symtab)          # a FRESH dict
    _st[_k] = _ty               # mutated BEFORE
    self._current_symbol_table = _st

The mutation precedes the store, so it is not the carrier at all. **An order-insensitive
scan over-reports a data-flow property, and the over-report was in the most alarming
direction.** Re-run with statement ordering, the mirror count is 0. Lesson recorded because
the same shape of scan is used all over this campaign to cost repairs.

**THE ONE LIVE SITE IS REAL AND IS NOT MIRRORED**:

    src/pycsl/module6_whyml/functions.py::_prescan_pyval_locals
        L1180  self._pyval_locals = pyval
        L1195  pyval.add(tgt)          # relies on Python aliasing so the field sees it

That is PyCSL's own emitter using exactly the reference semantics its ownership discipline
(R3) rejects. It is correct Python and it is not modelled — and `_prescan_pyval_locals` has
no mirror counterpart, so no proof is affected today. It does mean the generalised refusal
must be gated on the MUTATION-AFTER-STORE ordering rather than mere co-occurrence, or it
would refuse the emitter's own source the moment that method were mirrored.

## IS THE ROUTE CONFINED TO THE `hoare` MEMORY MODEL? NO — THE OTHERS CANNOT EMIT A DICT

Worth asking, because if another model already handled aliasing correctly the repair would
be "use that model" rather than "refuse". Measured on witness 1125:

    --memory-model hoare   ->  PROVES the false claim   (the route)
    --memory-model typed   ->  emission error: `unbound type symbol 'option'`
    --memory-model store   ->  emission error: `unbound type symbol 'option'`

The other two are not failing closed on the ALIASING; they cannot emit a dict AT ALL,
because their preambles never bring the `option` type into scope and a dict lowers to
`map <k> (option <v>)`. So the route is confined to `hoare` only in the sense that `hoare`
is the only model that can express the program — no alternative model to adopt, and the
repair stands as scoped.

**A SMALL SEPARATE FINDING, RECORDED SO IT IS NOT LOST:** the `typed` and `store` memory
models cannot emit ANY dict-valued code. That is a completeness gap in those models
(a missing preamble import), not a soundness one, and it is not route #59's business — but
it does mean any future measurement that varies the memory model must not read their failure
as a fails-closed result. It is an emission error, several stages before the prover.

## `del` AND `.pop()` AS ALIAS MUTATIONS — BOTH FAIL CLOSED, AND ONE IS AN EXPLICIT REFUSAL

Probed because the staged guard's mutation gate lists STATEMENT kinds
(`ArraySet`, `ArraySliceSet`, `DelSubscript`, ...), so a mutating METHOD CALL through the
alias could slip past it. Measured:

    a = {1:1, 2:2};  b = a;  del b[1];    read len(a)   ->  emission type error (closed)
    a = {1:1, 2:2};  b = a;  b.pop(1);    read len(a)   ->  **EXPLICIT REFUSAL**

The `.pop()` refusal is worth quoting, because it is the same reasoning as route #59 arrived
at independently and already written into the emitter:

    `b.pop(...)` MUTATES its receiver in place, and no certified lowering models it: the
    call becomes an abstract operation that takes NEITHER the receiver NOR a `writes`
    clause, so the mutation would be SILENTLY ABSENT from the model while the run still
    reported 'All contracts formally proven' ...

**SO THE GUARD'S STATEMENT-KIND GATE IS HARMLESS HERE**: a mutating method call cannot reach
a lowered program at all, and `del` cannot lower either. `DelSubscript` is in the gate anyway,
so if `del` is ever given a lowering the guard already covers it.

This also strengthens the case that #59's repair belongs: the emitter ALREADY refuses
in-place receiver mutation for exactly the "silently absent from the model" reason, and
already refuses R2 mutable defaults. Alias assignment is the same hazard reached by a
different syntax, and it is the one still answered instead of refused.
