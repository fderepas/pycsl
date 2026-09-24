# ROUTE #226 (#49, gen #31) — a `#@ class invariant` the CONSTRUCTOR never establishes is assumed by every method

**STATUS: LIVE SEV-1.** A false postcondition is certified on ordinary total Python — no
`no_exception`, no opt-in, no `\trusted` anywhere.

## The witness

```python
_ = 0  # anchor


#@ class invariant self.n >= 5
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result >= 5
    #@ assigns \nothing
    def get(self) -> int:
        return self.n
```

    [+] Verification SUCCESS! All contracts formally proven.

CPython: `C().get()` is `0`, and `0 >= 5` is False.

## The mechanism, in the emitted module

```
  type c = { mutable n: int }
    invariant { (n >= 5) }
    by { n = 10 }

  let c__get (self: c) : int
    ensures  { (result >= 5) }
  =
    self.n
```

Two facts, and the second is the route:

1. **`by { n = 10 }` is SYNTHESIZED TO SATISFY THE INVARIANT.** Why3 requires a type
   invariant to be inhabited, and the emitter discharges that by constructing a value the
   invariant accepts. The witness follows the invariant, so it is satisfiable whatever the
   invariant says. (Seen first on a list field: `invariant { Array.length xs = 1024 }` with
   `by { xs = (Array.make 1024 0) }`, for a field initialised to `[]`.)
2. **`__init__` IS NOT EMITTED AT ALL.** There is no `c____init__` in the module. So
   nothing ever checks that the REAL constructor establishes the invariant — and every
   method gets it as a free assumption, because a Why3 type invariant holds at every
   function boundary for a value of that type.

> **Read the CORRECTION section below before quoting point 2.** The emitter *does* raise
> the invariant VC where a record is CONSTRUCTED (`let c = { n = 0 }`), so a file that
> builds one is caught. The obligation is attached to the CONSTRUCTION SITE rather than
> to the CLASS — so a file that defines the class, publishes a reader for it, and lets
> some other file build it is never asked. That is measured, and it is the real shape.

annotations.md row 1 of §class contracts says the invariant "**must hold at every method
boundary**". The constructor's exit is a method boundary. The documentation states the
obligation; the implementation checks inhabitation instead.

## How far it goes — measured, not assumed

| probe | verdict |
|---|---|
| scalar: `self.n = 0` under `invariant self.n >= 5`, method returns `self.n`, `ensures \result >= 5` | **SUCCESS — the route** |
| the same with a TRUE invariant (`self.n = 7`, `>= 5`) | SUCCESS (correct — invariants ARE assumed by methods, which is what makes the false one dangerous) |
| list field: `self.xs = []` under `invariant \length(self.xs) == 1024` | the INVARIANT is accepted (file verifies) |
| …and a method returning `len(self.xs)` with `ensures \result == 1024` | FAILED |
| …and an in-bounds element read `self.xs[i]` for `i < 1024` | FAILED |

So the SCALAR path is a complete carrier — the false fact reaches a postcondition — while
the LENGTH path stops short, because `len(self.xs)` does not lower to `Array.length` of the
record field. That asymmetry is worth keeping: it means the severity is not bounded by "you
can only lie about lengths", and it means a repair must be checked on the scalar path.

## Prior art — searched before claiming this is new

`route165-a-receiverless-method-stub-skips-the-class-invariant.md` is a DIFFERENT mechanism
(a call boundary whose stub has no receiver, so the callee's invariant is not re-checked).
Nothing in `open-routes/` or `getting-better/` records the CONSTRUCTOR obligation. The
closest prose is this session's own backlog note about the inhabitation witness, written
twenty minutes before the scalar probe turned it into a route.

## Shape of the repair — **written when it was not built; it now IS**

Kept as written so the order of discovery is readable. The built version is below
("THE REPAIR, BUILT AND RUN ON AN OFFLINE COPY OF THE TREE"), and it differs from this
sketch in two ways that were both found by measuring: the honest fallback for a
computing constructor is to emit NOTHING and record it, not to refuse; and the gate
cannot key on `td["field_defaults"]`, which is a witness map.


Emit the constructor's obligation, the way `#@ mutex_invariant`'s initial-state check was
repaired earlier this same generation: that one now emits
`goal _check_initial_<m> : <m>_inv <literals>` over the CONSTRUCTOR'S LITERAL initial values
rather than asserting inside a program function
(`finding-mutex-invariant-initial-check-unprovable.md`). The same device applies here —
`goal _check_class_inv_<C> : <inv>[fields := <__init__'s literal assignments>]` — and the
same limitation applies: it is exact only when `__init__` assigns literals. For a
constructor that computes, the honest fallback is to REFUSE rather than to assume.

GATE BEFORE LANDING: every corpus class with a `#@ class invariant` currently gets the
invariant for free. Emitting the obligation will make some of them fail, and each failure
is either a real defect in that driver or a limit of the literal-substitution device — the
census is the work, exactly as it was for the mutex one.

Measured 2026-09-24. Witnesses: `$SCRATCH/g31/w/ci{,2,3,4}.py`.

## THE CENSUS THE REPAIR NEEDS — taken before building anything

AST scan of both corpora, `src/pycsl`, `src/self-annotate/src` and `src/pycsl_lib`:

    files carrying a `#@ class invariant`   214
    classes carrying one                    184
      · `__init__` assigns only LITERALS    160   (constants, negated constants, empty
                                                   collections, `[0] * N`, `list()`/`dict()`/
                                                   `set()`/`bytes()`/`bytearray()` calls)
      · `__init__` COMPUTES something        24

So the literal-substitution device — the one `#@ mutex_invariant`'s initial-state check
already uses — reaches **160 of 184** classes, and the honest fallback (REFUSE rather than
assume) would land on 24. That is a big enough population that the repair cannot be landed
blind: emitting the obligation will make some of those 160 FAIL, and each failure is either
a real defect in that driver or a limit of the substitution.

**Every one of these 184 classes is getting its invariant for free today.** That is the
number that makes this a SEV-1 rather than a curiosity: it is not a corner of the language
nobody uses; it is the headline class contract, used in 214 files, and the obligation that
would make it mean something has never been emitted.

SUGGESTED ORDER FOR THE REPAIR, so the 24 do not block the 160:
  1. emit `goal _check_class_inv_<C>` by substituting `__init__`'s literal assignments,
     for the 160 — and read every new failure;
  2. for the 24 computing constructors, emit NOTHING YET and record them, rather than
     refusing in the same increment; a refusal there is a second, separable decision with
     its own blast radius.

## CENSUS B — the RESTRICTED device, and what it would break (measured before building)

The census above counted constructors by whether they assign only literals (160 of 184).
That is the device's OUTER bound. The obligation actually has to be STATED in WhyML, and
the statable form is a pure-logic goal over ints:

    goal _check_class_inv_<C> : forall <f1> … <fn> : int. <f1> = <lit1> -> … -> (<inv>)

so the device's INNER bound is narrower: every field int-typed AND literal-initialised, and
the invariant mentioning nothing but those fields. AST scan of both corpora, `src/pycsl`,
`src/self-annotate/src`, `src/pycsl_lib` (`$SCRATCH/g31/census226b.py`):

    files with a `#@ class invariant`      214
    classes carrying one                   210
    IN SCOPE of the restricted device      113

(210, not census A's 184: the two scanners attribute the `#@ class invariant` comment
to a class differently — A walks the decorator/comment block from the class down, B from
the class up, so B also picks up a second class sharing one comment block. The 113 was
taken with B and is the number the repair is scoped to; the discrepancy is in the
denominator, not the population.)
      · out of scope, non-int / non-literal field       96
      · out of scope, invariant calls a predicate        1   (0706.py:C, `field_nonneg`)

Then the question the gate is really asking — **would emitting the obligation break any of
them?** Evaluating each in-scope invariant clause against the constructor's own literals:

    in-scope invariant clauses                          139
      · SATISFIED by the constructor's literals         137
      · VIOLATED  by the constructor's literals           0
      · not evaluable (invariant names a module const)    2   (0284 `max_allowed`,
                                                               0285 `limit`)

**ZERO violated.** Every in-scope corpus class already establishes its invariant — the
obligation has simply never been asked. So this repair is expected to be additive on the
corpus, which is the opposite of the `#@ mutex_invariant` initial-state repair (where the
goal was unprovable in every program until the ref was made concrete). The two free-name
clauses are the device's third exclusion: restrict to invariants whose every identifier is
a field of the class, and the population is 111.

That does NOT lower the severity. 113 classes get an obligation they happen to meet; the
other 97 — and every future class — keep getting theirs for free.

## THE OBLIGATION, TESTED BY HAND IN WhyML BEFORE ANY EMITTER CHANGE

Both candidate statements were added to the carrier's own generated module
(`$SCRATCH/g31/r226/`) and run through `why3 prove -P alt-ergo`, in the false AND the true
version. No emitter was touched to get these four numbers.

| statement added to the carrier's module | `self.n = 0` (FALSE inv) | `self.n = 7` (TRUE inv) |
|---|---|---|
| A: `let _check_class_inv_c () : c = { n = 0 }` | **Unknown** | Valid |
| B: `goal _check_class_inv_c : forall n : int. n = 0 -> (n >= 5)` | **Unknown** | Valid |

So the obligation IS statable and IS decided, both ways, by the prover the pipeline already
runs — the route is a missing statement, not a prover limitation. `c__get'vc` stays Valid in
every one of the four runs, so neither form disturbs the existing goals.

**Form B is the one to build**, though A is less code. A reuses `_build_witness_str`, the
SAME builder that produces the `by { … }` witness — and that builder takes array lengths
from `array_lengths`, which is `_extract_array_lengths(class_invs)`: read off the INVARIANT.
Widening A to array fields later would therefore quietly re-derive the value from the
invariant and re-open exactly this route, one generation after closing it. B's premises are
the constructor's literals written out, with no shared builder that can substitute the
invariant's own data for them. It is also the form `#@ mutex_invariant`'s initial-state
check already uses (`goal _check_initial_<m>`), so the module grows one more goal of a
shape the corpus has seen.

Scope for increment 1, from census B: the 111 classes that are all-int, all-literal AND
whose invariant names nothing but their own fields (113 minus 0284/0285, whose invariants
name a module constant — those need the constant in scope at the goal and are a separable
second step).

## CORRECTION AND SHARPENING — the CONSTRUCTION SITE *is* checked; the MODULE BOUNDARY is not

Six more probes, run before building the repair, because "the constructor is never checked"
was too coarse a sentence to leave standing (`$SCRATCH/g31/r226/p{1..6}.py`):

| probe | verdict |
|---|---|
| p5: the carrier PLUS `def use(): c = C(); return c.get()` | **FAILED** |
| p4: `self.n = n`, no `#@ requires`, plus `use(): c = C(1); …` | **FAILED** |
| p3: the same with `#@ requires n >= 5` on `__init__` and `C(7)` | SUCCESS (correct) |
| p1: `self.n = n`, no `#@ requires`, NO construction in the file | **SUCCESS — a second carrier** |
| p2: `self.s: str = "bad"` under `invariant self.s == "ok"` | FAILED (string path does not carry) |
| p6: the carrier PLUS `def read(c: C) -> int: return c.get()` | **SUCCESS — the severity** |

So the emitter DOES check the invariant where a record is CONSTRUCTED — `let c = { n = 0 }`
raises the type-invariant VC and p5 fails. That is worth saying plainly: the original
sentence "nothing ever checks that the real constructor establishes the invariant" is wrong
as written. What is missing is narrower and worse-placed: **the obligation is attached to
the CONSTRUCTION SITE, not to the CLASS.** A file that defines the class and never builds
one is never asked the question.

p6 is why that is a soundness bug and not a vacuity curiosity. The file publishes

    #@ ensures \result >= 5
    def read(c: C) -> int: return c.get()

and it VERIFIES. Every caller of `read` is entitled to `>= 5`; in CPython `read(C())` is
`0`. The class is a library type, the function is its public reader, and the construction
happens in some other file — which is the ordinary shape of a module, not a contrivance.

p1 adds a SECOND carrier that increment 1 does NOT close: `self.n = n` from an unannotated
`__init__` parameter, with no `#@ requires`. There is no literal to state the goal about, so
the literal-substitution device is silent there. The honest statement for that shape is
`forall n. n >= 5`, which is FALSE — i.e. the correct outcome is that such a class does not
verify unless `__init__` carries a `#@ requires`, and p3 shows that `#@ requires` on
`__init__` already works. That is a second increment with its own blast radius (the 96
non-int/non-literal classes), and it is recorded here rather than folded into the first.

Increment 1 closes the p6 shape — the goal fails, so the file stops verifying — which is
the one that publishes a false contract across the module boundary.

## THE REPAIR, BUILT AND RUN ON AN OFFLINE COPY OF THE TREE (no live edit, a battery was in flight)

`src/` was copied to `$SCRATCH/g31/tree226/src`, the patch applied THERE, and the witnesses
run against that copy. Result, with the emitted goal beside each verdict:

| file | verdict | goal emitted |
|---|---|---|
| 1890 `self.n = 0` under `>= 5`, plus `read(c: C)` | **FAILED** | `forall n:int. n = 0 -> ((n >= 5))` |
| 1891 the same with `self.n = 7` | SUCCESS | `forall n:int. n = 7 -> ((n >= 5))` |
| 1892 `self.n = n` from a parameter | SUCCESS (the recorded debt) | none |
| p8 `self.n = three()` | SUCCESS (debt) | none |
| p9 the store inside an `if` | SUCCESS (debt) | none |

### AND THE FIRST CUT WAS WRONG, IN A WAY ONLY THE ADJACENT WITNESS COULD SHOW

The first version gated on `fn in defaults`, where `defaults = td["field_defaults"]`. That
read as "the constructor gave this field a literal". **It does not.** Module 5 line ~3980
stores

    field_witness = {f["name"]: field_defaults.get(f["name"], 0) for f in fields}

under the key `field_defaults`, so a field the constructor never gives a literal reads back
as the DEFINITE literal `0`. The first cut therefore emitted `n = 0 -> (n >= 5)` for

    def __init__(self, n: int) -> None:
        self.n = n

and 1892 went FAILED. The verdict is arguably the one you want; the REASON is a claim the
source does not make, and shipping it would have put a false premise in a soundness goal.

The three shapes are distinguishable in Module 6 without touching Module 5 — measured on the
offline tree, by dumping `td`'s keys:

    parameter      -> `init_params` non-empty
    computed       -> `init_unknown_fields` carries the field   (route #83's key)
    control flow   -> `init_unknown_cf_fields` as well
    paramless + no unknown field -> `field_witness` IS `field_defaults`

and the census says all 113 in-scope corpus classes already satisfy the tightened gate, so
the honesty costs nothing. (Checked separately: `C(7)` DOES construct `{ n = 7 }`, so the
witness map's fabricated 0 does not reach a construction site — that was probed, not
assumed, because a fabricated definite literal is exactly route #139/#145's shape.)

### Four real corpus classes, run against the patched offline tree

    0006 Counter      SUCCESS   goal … forall _value : int. _value = 0 -> ((_value >= 0))
    0076 Point        SUCCESS   goal … forall _x _y : int. _x = 0 -> _y = 0 -> (((_x >= 0) && (_y >= 0)))
    0192 Buffer       SUCCESS   goal … _size = 0 -> _capacity = 10 ->
                                     ((_size >= 0)) /\ ((_capacity > 0)) /\ ((_size <= _capacity))
    0244 MagicNumber  SUCCESS   goal … forall magic_number : int. magic_number = 42 -> ((magic_number = 42))

One field, two fields, three invariant clauses on two fields, and an equality — all four
discharge, which is what the census predicted. The full corpus number is the gate's job.

### A THIRD carrier, absent from the corpus and NOT closed by increment 1: `@dataclass`

    #@ class invariant self.n >= 5
    @dataclass
    class C:
        n: int = 0

    #@ ensures \result >= 5
    def read(c: C) -> int: return c.n       # SUCCESS; CPython read(C()) is 0

Same emitted shape (`invariant { n >= 5 } by { n = 10 }`), same module-boundary severity.
The gate does not fire because a dataclass's SYNTHESIZED `__init__` takes every field as a
parameter, so `init_params` is `['n']` — and that exclusion is CORRECT rather than a miss:
`C(3)` is legal Python, so the obligation for a dataclass is `forall n. n >= 5`, which the
default `= 0` does nothing to discharge. The honest statement for this shape is that such a
class cannot establish its invariant at all, which is a refusal, not a goal.

Census note: ZERO classes carrying a `#@ class invariant` in either corpus, `src/pycsl`,
`src/self-annotate/src` or `src/pycsl_lib` are dataclasses — the scan's "no `__init__`"
bucket came out empty — so this shape is a live hole with no user today.

So route #226 has FOUR carriers and increment 1 closes one of them:

| carrier | closed by increment 1 |
|---|---|
| paramless `__init__`, literal store (`self.n = 0`) | **yes** |
| `__init__` parameter (`self.n = n`) | no — 1892 records it |
| computed (`self.n = three()`) / control-flow store | no — p8 / p9 record it |
| `@dataclass` with a field default | no — recorded here |

That is worth stating plainly rather than filing the route as closed: **increment 1 closes
the shape the corpus actually uses (113 classes) and leaves three shapes open.** The route
file stays LIVE until all four are answered.

### Inheritance and the two out-of-scope corpus files, also run offline

    0442 (Base/Sub)  SUCCESS
        goal _check_class_inv_base : forall base_start : int. base_start = 7 -> ((base_start >= 0))
        goal _check_class_inv_sub  : forall sub_start extra : int.
                                       sub_start = 7 -> extra = 0 -> ((sub_start >= 0)) /\ ((extra >= 0))

Two goals, the subclass carrying BOTH invariants over BOTH fields, and the ambiguous field
name qualified (`base_start` / `sub_start`) because the goal reuses `_field_label` — the
same function the `invariant` and the `by { }` witness already use, which is why the
qualification came out right without being asked for.

    0284 / 0285  REFUSED before the repair, REFUSED after

These are the two whose invariants name a module constant (`max_allowed`, `limit`). Both are
`# pycsl-expected: FAIL` files that never reach emission at all, so the "invariant names a
module constant" exclusion is currently untestable on the corpus — it is a rule about a
shape no corpus file exercises. Recorded as such rather than claimed as covered.

### The Rocq/Lean proof corpus is out of the blast radius, checked rather than assumed

None of the thirteen files carrying a `*.proofs/rocq/` tree (0342, 0352, 0538, 0539, 0542,
0708, 0711, 0712, 0714, 0753, 0777, 0778, 0779) declares a `#@ class invariant`, so no
emitted module that feeds the external-proof extraction gains a goal. That matters because a
new goal in such a module would change what `pycsl --rocq` regenerates, and the `.aux` build
output under those trees is already noisy in this working tree.

### Two more pre-gate numbers, so the suite's arithmetic is predicted before it runs

* **Invariants using `*`, `/`, `//` or `%` among the 113 in scope: ZERO.** Every one is a
  comparison or a conjunction of comparisons over literals, so the new goals are trivially
  discharged and the census's Python-`eval` agreement with Why3 is not a coincidence waiting
  to be found out on nonlinear arithmetic.
* **32 of the 113 sit in `# pycsl-expected: FAIL` files.** They stay FAIL: a file fails for
  a reason, and adding a goal that DISCHARGES cannot remove it. The remaining 81 sit in PASS
  files whose constructors already satisfy their invariants, so they stay PASS. **Predicted
  suite delta: the standing eighteen, plus 1890 as a new expected-FAIL and 1891/1892 as new
  PASSes — no XPASS, no new XFAIL.**

## INCREMENT 2's DESIGN, written down now so it is not re-derived

Carriers 2 and 4 (an `__init__` PARAMETER, and `@dataclass`) have the same honest
obligation, and it is PREMISE-FREE:

    goal _check_class_inv_<C> : forall <f1> … <fn> : int. (<inv>)

"the invariant must hold for any instance this constructor can produce". For
`def __init__(self, n: int): self.n = n` under `self.n >= 5` that is `forall n. n >= 5`,
which is false — correct, because `C(1)` is legal Python. For a `@dataclass` with
`n: int = 0` it is the same statement, and the default discharges nothing, because `C(3)`
is legal too.

**AND IT WOULD BREAK A GOOD PROGRAM AS WRITTEN** — the (u4) test, applied before building:

    #@ class invariant self.n >= 5
    class C:
        #@ requires n >= 5
        def __init__(self, n: int) -> None: self.n = n

verifies today (measured, `$SCRATCH/g31/r226/p3.py`, including a `C(7)` call site), and it
is sound: the constructor's precondition is exactly what makes the invariant establishable.
A premise-free goal would refuse it.

So increment 2 needs `__init__`'s `#@ requires` as the goal's premises, mapped from
PARAMETERS to FIELDS through `init_body` (which already carries
`{'field': 'n', 'value': {'type': 'Var', 'name': 'n'}}`). **The type_decl does NOT carry
`init_requires` today** — its keys are `init_params`, `init_body`, `init_ensures` — so
increment 2 begins with a Module-5 IR addition, and that is a different kind of change from
increment 1, which touched Module 6 only. Sizing it honestly: a new IR key is not byte-inert
for anything that compares IR, so it needs its own byte-diff and its own conformance-golden
check, which is why it is not folded into increment 1.

The fallback if that proves expensive: emit the premise-free goal ONLY when `__init__` has
no `#@ requires` at all — which is knowable at Module 5 without a new key being read
downstream, and covers the `@dataclass` carrier outright (a synthesized `__init__` has no
contract).

## HOW TO REPRODUCE THE CENSUS (the script lives in a scratchpad that will not survive)

Walk `test-suite/corpus/pycsl-reference`, `test-suite/corpus/python-reference`, `src/pycsl`,
`src/self-annotate/src`, `src/pycsl_lib`. For each `.py` containing `#@ class invariant`,
`ast.parse` it and for each `ClassDef` read UPWARD from `node.lineno - 2` collecting
`#@ class invariant` lines, skipping lines that start with `#` or `@`, stopping at anything
else. Then, from the class's `__init__`:

  * a field is `self.<name>` on the left of an `Assign` (single target) or an `AnnAssign`;
  * it is IN SCOPE iff its annotation (when present) is `int`/`bool` AND its RHS is an int
    literal, a negated int literal, or a `bool` — `const_int` folds `UnaryOp(USub, …)`,
    which Python's parser does not (that was route #139);
  * the CLASS is in scope iff it has an `__init__`, has at least one field, every field is
    in scope, and every `self.<n>` named in its invariants is one of those fields;
  * exclude an invariant that calls anything (`\w+\s*\(`) other than `\length`.

Then substitute each field's literal into its invariant text and `eval` it with an empty
builtins dict; count SATISFIED / VIOLATED / not-evaluable. The 2026-09-24 numbers are 214
files, 210 classes, 113 in scope, 139 clauses, 137 satisfied, 0 violated, 2 not evaluable.

The EMITTER's gate is narrower than the census's and deliberately so: it additionally
requires `init_params` empty and the field absent from `init_unknown_fields` /
`init_unknown_cf_fields`, because `td["field_defaults"]` is a witness map that fabricates 0
(see the CORRECTION section). All 113 pass it.

## THE EXECUTABLE ORACLE FOR THE SHAPES THE EMITTER CANNOT STATE

Increment 1 emits the obligation only where it can be STATED exactly. The other three
carriers are all RUNNABLE, and that is a whole instrument rather than a consolation:
**`bin/check-class-invariant-establishment.py`** constructs every PASS-expected corpus class
that `C()` builds and evaluates its own `#@ class invariant` on the object.

    75 C()-constructible classes across both corpora, 84 evaluable clauses, 0 FALSE,
    3 not evaluable

and the sensitivity test, which is the only test of a detector that means anything — one
file per open shape:

    zz1 paramless literal (the shape increment 1 closes)  FALSE
    zz2 `@dataclass` with a field default                 FALSE
    zz3 computed (`self.n = three()`)                     FALSE

### The FOURTH shape needs SAMPLING, and its entire population is witness 1892

A class whose `__init__` takes arguments has no canonical instance, so the plane skips it.
Sampling the int parameters over `(0, 1, -1, 2, 5, 10, 100, -100)` — skipping any `__init__`
that carries a `#@ requires`, because its precondition may exclude the samples — covers it.
Measured across both corpora:

    classes with int-parameter constructors and no `#@ requires` : **1**
    and it is `1892`, this route's own recorded debt, FALSE at `args=[0]`.

So the sampling extension is BUILT and MEASURED (`$SCRATCH/g31/inv_sample.py`) and is NOT
landed with increment 1, for a reason worth stating: its only finding is a corpus file
deliberately marked PASS to record this route's second carrier. A plane that is red on
purpose blocks every commit, and a plane with a silent exception is worse. **It lands with
INCREMENT 2**, when 1892 stops verifying and the plane goes green by the repair rather than
by an allow-list.

### INCREMENT 2's BLAST RADIUS, censused: it is ONE corpus file, and that file is 1892

Classes with a `#@ class invariant` AND a parameterised `__init__`, across both corpora,
`src/pycsl`, `src/self-annotate/src` and `src/pycsl_lib`:

    parameterised-`__init__` classes with a class invariant   46
      · `__init__` carries a `#@ requires`                    20
      · it does not                                           26
    `@dataclass` classes with a class invariant                0

but almost all 46 take a COLLECTION parameter (`Parser(toks)`, `Cursor(toks)`, `Inode(...)`),
not an int. Restricting increment 2 to the shape it can state — every field an `int`, every
one bound directly to an int `__init__` parameter or to a literal — the population that
would newly receive a goal is:

    classes with int-parameter constructors and no `#@ requires` : **1**

and it is `1892`, this route's own recorded debt. So increment 2 is, on today's corpus, a
one-file change that turns a green witness red on purpose — which is the cleanest possible
shape for a soundness increment, and it is also why the SAMPLING half of
`check-class-invariant-establishment` has to land with it rather than before it.

The 20 with a `#@ requires` are the reason the premises are not optional: `#@ requires n >= 5`
on `__init__` is exactly what makes such a class establishable, and a premise-free goal would
refuse a good program (measured, `$SCRATCH/g31/r226/p3.py`).

### INCREMENT 2's GOAL SHAPE, worked out so it does not need re-deriving

The obvious form — substitute the constructor's values into the invariant TEXT — is the
same fragile substring surgery that cost lesson (b5). The robust form binds everything and
states the bindings as premises:

    goal _check_class_inv_<C> :
      forall <sorted(set(field labels) | set(int params))> : int.
        <label_i> = <value_i> -> …          (one per field: its literal, or its param)
        <requires_j> -> …                   (`__init__`'s `#@ requires`, lowered as-is)
        (<inv>)

Nothing is substituted; the invariant is emitted exactly as it already is, in terms of its
field labels. Three cases fall out of the same expression, which is why this shape and not
another:

    self.n = 0        labels {n}, params {}      forall n. n = 0 -> (n >= 5)       FALSE ✓
    self.n = n        labels {n}, params {n}     forall n. n = n -> (n >= 5)       FALSE ✓
                      (the binder set is a UNION, so the shared name binds once)
    self.m = n        labels {m}, params {n}     forall m n. m = n -> (m >= 5)     FALSE ✓
    + `#@ requires n >= 5`                       forall m n. m = n -> n >= 5
                                                   -> (m >= 5)                     TRUE  ✓

and the last line is the (u4) counter-program, which the premise-free version would have
refused. Increment 1's emission is the special case with no params, and it is left exactly
as it is rather than folded in — its goldens are already refreshed, and rewriting a landed
emission to share code with a new one is how a byte-diff becomes unreadable.

WHAT IS STILL NEEDED IN MODULE 5: `init_requires`, collected exactly like `init_ensures`
(`construction_synth._collect_init_ensures` reads `child.csl_ensures`; the `csl_requires`
twin is already attached by the weaver), emitted onto the type_decl ONLY when non-empty —
so the 20 classes that have one move their IR golden and the rest do not.

### CORRECTION to increment 2's cost: **Module 5 needs NO change — the IR already carries it**

The paragraph above says increment 2 "begins with a Module-5 IR addition" for
`init_requires`, and that a new IR key is not byte-inert for anything that compares IR. Both
sentences are true in general and neither applies, because **route #15 already put it
there**: the type_decl carries

    "init_contract_check": {"requires": [<IR>], "ensures": [<IR>], "param_types": {...}}

emitted whenever a constructor has a NON-TRIVIAL `#@ requires`/`#@ ensures` — 34 such
constructors tree-wide, 13 in the reference corpus, 21 in `src/pycsl_lib`, zero in the
mirrors. `param_types` is there too, and it exists for exactly the reason increment 2 needs
it: `init_params` is a list of NAMES and `__init__` is never emitted as a function, so the
types cannot be recovered downstream.

So increment 2 is **Module 6 only**: no IR key, no `*.ir.json` movement, no IR version
question. That is a materially smaller increment than the record said an hour ago, and the
reason to write the correction rather than edit the original is that "check whether the
thing you need is already in the IR" is the step that was skipped.

### And increment 2 cannot disturb increment 1's emission — censused, not hoped

Folding the `#@ requires` premises into the same goal would change increment 1's output for
any PARAMLESS constructor that carries one. Census across both corpora, `src/pycsl`,
`src/self-annotate/src` and `src/pycsl_lib`:

    paramless `__init__` with a class invariant AND a non-trivial `#@ requires` : **0**

so the 60 corpus modules and 12 frozen goldens that increment 1 moves stay byte-identical
under increment 2. That is the check that makes a shared-code-path increment safe to write,
and it is the one that is easiest to skip because the answer is "obviously zero".

### INCREMENT 2, BUILT AND MEASURED OFFLINE (Module 6 only)

    1890 paramless literal                 FAILED   forall n. n = 0 -> ((n >= 5))
    1891 the control                       SUCCESS  forall n. n = 7 -> ((n >= 5))
    1892 from an `__init__` PARAMETER      **FAILED**  forall n. n = n -> ((n >= 5))
    1900 `@dataclass`, field default 0     **FAILED**  forall n. n = n -> ((n >= 5))
    1901 `#@ requires n >= 5` on __init__  **SUCCESS**
            forall n. n = n -> (n >= 5) -> ((n >= 5))
    the computed / control-flow store      SUCCESS, no goal — STILL A CARRIER

So carriers 2 and 4 close, 1 stays closed, the (u4) counter-program survives, and **route
#226 is left with ONE open carrier**: a constructor that COMPUTES the field's value. That
one is not a miss — Module 5 marks such a field in `init_unknown_fields`, the model does not
claim to know its value, and the honest obligation needs the CALLEE'S postcondition
(`three()` ensures `\result == 3`) rather than a literal. That is increment 3.

THE SAMPLING HALF OF `check-class-invariant-establishment` IS NO LONGER NEEDED and is not
landed: its entire population was 1892, which increment 2 turns expected-FAIL, and the plane
skips expected-FAIL files. **The emitter closing a shape retires the runtime oracle for it**
— which is the right order, and worth noticing, because the oracle was written first.

TWO WRONG LOWERINGS BEFORE THE RIGHT ONE (wall-lesson (j5)): `_expr_to_whyml(req, set())`
emits `val constant n : int`, colliding with the record field label `n`; passing the
parameters as `lr` makes them REFS (`!n >= 5`). The right form is the one
`_emit_init_contract_checks` already uses for these very clauses — `_current_symbol_table` +
`_formal_params` + `_current_params` + `_in_spec`.

### The one thing increment 2's gate has to look hard at

`param_types` comes from route #15's `init_contract_check`, which Module 5 emits ONLY when a
constructor clause is non-trivial. A class whose `__init__` has no `#@ requires`/`#@ ensures`
therefore has NO `param_types` at all, and the scope test `_ci_ptypes.get(p, "") in
("", "int", "bool")` reads every parameter as int by default — 1892 is exactly that case,
which is why the default has to be permissive.

The safety net is the FIELD side, not the parameter side: the gate already requires
`field_types[fn] == "int"` for every field, and it requires every identifier in the lowered
invariant to be a field label. A `List[...]`-annotated field is typed `list` and excluded; an
UNANNOTATED field bound to a list parameter is typed `int` by the RHS-shape inference (the
defect the field-param increment repairs), but then its invariant almost certainly says
`\length(self.f)`, which lowers to `Array.length f` and fails the identifier check.

"Almost certainly" is not a proof, which is why the landing order puts the FIELD increment
BEFORE this one — after it, `self.toks = toks` from an annotated parameter carries the
parameter's real type and the field is excluded properly — and why the gate's byte-diff
audit must list the moved files by NAME, not just count them.

### And the collection-parameter classes were checked by EMISSION, before the gate

Seven of the 45 classes whose `__init__` takes a collection — `0661` (`Inode(initial: list)`,
nineteen preconditions), `0900` (`Cursor(toks)`), `0925`, `0933`, `0966`, `1190`, `1685` —
emitted with `--no-proof --keep-mlw` against increment 2's tree:

    0661 … 1685      **(no goal)**, all seven

so the scope gate excludes them, as the field-type test and the identifier test predict. Two
minutes of emission, and it turns "almost certainly" into "measured on the seven that worry
me most". The gate still lists every moved file by name.

## INCREMENT 3 — the LAST carrier, and why it is a different kind of work

After increment 2 the route has ONE carrier: a constructor that COMPUTES the field's value.

    #@ ensures \result == 3
    def three() -> int: return 3

    #@ class invariant self.n >= 5
    class C:
        def __init__(self) -> None:
            self.n = three()          # SUCCESS; `read(C())` is 3 in CPython

Module 5 marks `n` in `init_unknown_fields` and `init_body` is EMPTY — the call is dropped —
so Module 6 has nothing to state an obligation about, and emitting the premise-free
`forall n. n >= 5` would refuse a class whose computation DOES satisfy its invariant. That
is the (u4) case again, and it is decisive: the honest obligation needs the CALLEE'S
POSTCONDITION.

THE SHAPE, if someone builds it:

    goal _check_class_inv_<C> :
      forall <labels> : int.
        <callee's `#@ ensures` with `\result` replaced by the field's label> -> …
        (<inv>)

so `three()`'s `\result == 3` becomes the premise `n = 3`, and `forall n. n = 3 -> n >= 5`
is FALSE — correct — while a `three()` ensuring `\result >= 5` discharges it.

WHAT IT COSTS, and this is why it is not increment 2's sibling: **Module 5 must record the
call**. `init_body` carries `{'field': …, 'value': <IR>}` only for literals and names; a
`Call` value is dropped and the field goes to `init_unknown_fields` instead. Carrying it is a
new IR key or a widened `init_body`, and EITHER moves `*.ir.json` — which is the
conformance-golden question increments 1 and 2 both avoided, and the one that raises
docs/ir.md §10's version bump.

SCOPE, from census A: 24 of 184 classes have a COMPUTING constructor. The subset whose
computation is a single call to a contract-carrying function is smaller still and has not
been counted — count it before building.

### INCREMENT 3's POPULATION IS **ZERO**, and that reframes the whole increment

Before building anything, count the shape. Computed constructor stores in a class carrying a
`#@ class invariant`, across both corpora, `src/pycsl`, `src/self-annotate/src` and
`src/pycsl_lib`:

    computed stores                                                   72
      · the computation is a CALL to a function with an `#@ ensures`   **0**
      · anything else                                                  72

and the 72 break down as

    Call(bytearray)   33      e.g. `self.disk = bytearray(1024)`
    BinOp             23      e.g. `self.disk = [0] * 1024`
    List              16      e.g. `self.disk = [...]`

**every one of them a CONTAINER construction**, not an int computation. So `self.n = three()`
— the shape the third carrier is written in, and the shape increment 3's
callee-postcondition device is designed for — **does not occur anywhere in the tree**.

CONSEQUENCES, and they point in opposite directions:

  * Increments 1 and 2 together close every shape the tree ACTUALLY CONTAINS. That is worth
    saying plainly, and it is stronger than "two of four carriers".
  * The third carrier is still a live unsoundness for any program that writes it, so the
    route stays LIVE and its carrier stays registered. But increment 3 would be built for a
    constructed witness only — its device (substitute the callee's `#@ ensures`) has no user
    to be right or wrong about, and it is the one increment that moves `*.ir.json`.

So increment 3 is DEMOTED, not scheduled: the cost is the highest of the three and the
measured demand is nil. What would raise its priority is a corpus program that computes a
SCALAR field in `__init__` — there is not one today.

The container stores are a separate question and not this route's: a `\length` invariant on
a list field does not reach a postcondition (measured when this route was found — a method
returning `len(self.xs)` FAILS), which is why the scalar path was the carrier in the first
place.

### Increment 2's suite arithmetic, predicted before the run

`1892` flips from `# pycsl-expected: PASS` to `FAIL` and STOPS verifying, so it stays a
"passed" row — the suite scores against the expectation, and the expectation moves with the
file in the same commit. Two files are added (`1900`, `1901`). So the suite should read
**total + 2, passed + 2, the standing EIGHTEEN, zero XPASS**.

The class-invariant PLANE's numbers should NOT move: `1892` and `1900` become expected-FAIL
and are skipped, and `1901`'s constructor needs an argument so it was never
`C()`-constructible. 75 classes / 84 clauses / 0 FALSE either way.
