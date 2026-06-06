# PyCSL Enhancement Proposal: Polymorphic / Generic Datatypes

**Status:** Draft / high-level design
**Scope:** `#@ datatype` grammar, polymorphic functions/predicates/lemmas, static semantics, WhyML lowering
**Audience:** PyCSL maintainers, contract authors
**Depends on:** `#@ datatype`; composes with `#@ lemma`, inductive predicates, typed quantifiers
**Anchor:** corpus `0540` — `#@ datatype Option[T] = Nothing | Just(T)` is recorded as *failing today*
**Non-goal:** implementation patches — this specifies *what* must hold, not the diff.

---

## 1. Motivation

PyCSL's `#@ datatype` declares only **monomorphic** Why3 algebraic types. Corpus `0540`
documents the gap directly: `#@ datatype Option[T] = Nothing | Just(T)` fails because the
`[T]` type-parameter syntax is not in the grammar. The consequences showed up earlier in
practice:

- **Type duplication.** Modelling JSON with a *tight* type required three near-identical
  carrier types — `Json`, `JsonList`, `JsonMembers` — and three traversal functions, purely
  because there was no reusable `List[T]`. Collapsing to one type to avoid the duplication
  re-introduced junk values. A generic list dissolves the dilemma.
- **No lemma reuse.** A structural fact like "length of an append is the sum of lengths" must be
  re-proved for every monomorphic carrier instead of once, polymorphically.

Why3 already provides everything needed: it is first-order logic *with polymorphic types*, ships
the archetypal `list 'a` with `Nil`/`Cons`, and supports polymorphic recursion in both logic and
programs. This proposal surfaces parametric polymorphism in PyCSL — generic datatypes plus the
polymorphic functions, predicates, and lemmas required to make them useful.

## 2. Scope

**In scope:** parametric (unconstrained) polymorphism — generic datatypes `Name[T1, …]`,
polymorphic functions/predicates/lemmas with type parameters, type applications
(`List[int]`, `Pair[int, Json]`), and Why3's built-in polymorphic equality on type variables.

**Out of scope (future):** bounded polymorphism / type-class-style constraints ("T must be
ordered"), higher-kinded type parameters, and higher-order functions (passing a function such as
`sum_numbers` into a generic traversal). These are noted in §11.

## 3. Surface syntax

Aligned with Python's native generic syntax (PEP 695 bracketed type parameters), so annotated
code stays close to ordinary typed Python.

```
datatype_def ::= "#@ datatype" NAME ["[" tyvars "]"] "=" ctor ("|" ctor)*
tyvars       ::= NAME ("," NAME)*
ctor         ::= NAME ["(" payload ("," payload)* ")"]
payload      ::= type
type         ::= "int" | "bool" | "str" | "float"
               | NAME                       # a type variable in scope, or a nullary datatype
               | NAME "[" type ("," type)* "]"   # application of a generic datatype
```

Functions, predicates, and lemmas introduce their own type parameters in brackets after the name
(PEP 695 `def f[T](...)`):

```python
#@ datatype Option[T] = Nothing | Just(T)
#@ datatype Pair[A, B] = MkPair(A, B)
#@ datatype List[T]    = LNil | LCons(T, List[T])      # generic + recursive

#@ ensures \result == p                                # swap is involutive at the type level
#@ assigns \nothing
def swap[A, B](p: Pair[A, B]) -> Pair[B, A]:
    match p:
        case MkPair(a, b):
            return MkPair(b, a)

#@ ensures \result >= 0
#@ \variant xs
#@ assigns \nothing
def length[T](xs: List[T]) -> int:
    match xs:
        case LNil():        return 0
        case LCons(h, t):   return 1 + length(t)
```

**Note (consistent with the "where is `Json` defined in pure Python" observation):** a generic
PyCSL datatype is a contract-level type, not a runtime Python type. A signature annotation like
`x: Option[int]` is read by the PyCSL front end; it is *not* required to be executable Python.
Files using generic datatypes are verification artifacts, exactly as monomorphic `#@ datatype`
files already are.

## 4. The JSON model, refactored with a generic list

The tight model from earlier becomes a single reusable list plus a thin member pair — no
duplicated spine types:

```python
#@ datatype List[T] = LNil | LCons(T, List[T])
#@ datatype Member  = MkMember(str, Json)
#@ datatype Json    = JNull | JBool(bool) | JInt(int) | JStr(str)
#@                  | JArr(List[Json]) | JObj(List[Member])
```

**Honest scope of the win.** Generics remove the *type* duplication (one `List[T]` serving both
arrays and object-member lists) and enable *polymorphic lemma reuse* (`length`, `append`, `mem`,
`reverse` proved once, used at `List[Json]` and `List[Member]`). They do **not** collapse the
traversal to a single function: an element-dependent operation like the numeric sum still needs a
`Json`-specific walk (a true one-function fold would require higher-order functions — §2,
out of scope). The gain is "tight type + reusable lemmas," not "one function."

## 5. Lowering to WhyML (Module 6 — WhyML Transpiler)

PyCSL type parameters map to Why3 type variables `'a, 'b, …`; type applications map to applied
type constructors.

| PyCSL | WhyML |
|---|---|
| `#@ datatype Option[T] = Nothing \| Just(T)` | `type option 'a = Nothing \| Just 'a` |
| `#@ datatype List[T] = LNil \| LCons(T, List[T])` | `type list 'a = LNil \| LCons 'a (list 'a)` |
| `Pair[int, Json]` (type application) | `pair int json` |
| `def length[T](xs: List[T]) -> int` | `let rec function length (xs: list 'a) : int … variant { xs }` |
| `def swap[A,B](p: Pair[A,B]) -> Pair[B,A]` | `let function swap (p: pair 'a 'b) : pair 'b 'a` |

Payload positions now additionally admit a **type variable** (→ `'a`) and an **application of a
generic datatype** (→ `name t1 … tn`), in addition to the existing scalar and concrete-datatype
mappings.

## 6. The SMT-encoding reality

Why3's *logic* is polymorphic, but most SMT backends are not — Z3, for instance, does not
support polymorphism. Why3 bridges this with a standard driver transformation that **encodes
polymorphic types into monomorphic types** before dispatch. Design consequences:

1. **PyCSL emits genuinely polymorphic WhyML** and relies on Why3's existing poly-encoding; it
   does **not** monomorphize in the front end by default.
2. **Performance caveat.** Poly-encoding can degrade solver performance on heavy goals. An
   *optional* eager monomorphization at instantiation sites (emit `list int`, `list json` as
   separate monomorphic types) is offered as a Phase 4 escape hatch for hot spots.
3. **Polymorphic equality** (`=` at any type variable) is available from Why3 and lowers
   directly; no per-type equality declaration is required for the unconstrained case.

## 7. Interplay with the companion features

- **Lemma functions (prove once, reuse everywhere).** A polymorphic lemma
  `\forall a b: List[T]. length(append(a, b)) == length(a) + length(b)`, proved by induction in a
  single `#@ lemma length_append[T](...)`, applies at *every* instantiation — the headline
  payoff over monomorphic carriers.
- **Inductive predicates, generically.** `#@ inductive forall_list[T](p, xs)` ("every element
  satisfies `p`") is defined once and reused; Why3 supports polymorphic inductive predicates.
- **Typed quantifiers.** With the quantifier proposal, a binder may range over a type parameter:
  `\forall x: T in xs; …`.
- **Mutually-recursive generics.** Generic versions of the `Tree`/`Forest` pair (corpus
  0533/0534) lower to a polymorphic `type tree 'a = … with forest 'a = … end`.

## 8. Soundness & static semantics (Module 4)

A generic declaration is well-formed iff:

1. **All type variables are bound.** Every `T` used in a constructor payload or signature is
   declared in the enclosing `[…]`. No free type variables (rejected).
2. **Type-constructor arity is respected.** A generic datatype is always applied to the right
   number of type arguments where a type is expected; an unapplied `List` is valid only in a
   type-constructor position, never as a complete type.
3. **Kinding.** Type variables appear only in type positions, never as values. **Parametricity:**
   a polymorphic function may not branch on, compare, or otherwise inspect a value of a bare type
   variable beyond what its operations allow (e.g. no `if t == 0` when `t : T`).
4. **Recursion/positivity unchanged.** A generic recursive datatype obeys the same rules as a
   monomorphic one; a generic recursive function still needs `#@ \variant`; a generic inductive
   predicate still needs strict positivity.
5. **No partial type application** in type positions (Why3 requires full application).

| Module | Change |
|---|---|
| **Module 2 — Parser** | parse `[tyvars]` on datatypes/functions and `Name[args]` type applications |
| **Module 3 — Weaver** | record type-parameter scopes on the relevant nodes |
| **Module 4 — Semantic Analyzer** | type-variable binding/scoping, arity & kind checks, parametricity, positivity for generic recursive/inductive defs |
| **Module 5 — IR Emitter** (`ir_schema`) | carry type-parameter lists and type-application nodes |
| **Module 6 — WhyML Transpiler** | emit `'a` vars, `type n 'a = …`, polymorphic `let [rec] function`/`predicate`/`lemma`; rely on Why3 poly-encoding (optional monomorphization in P4) |

## 9. Phasing

| Phase | Delivers | Risk |
|---|---|---|
| **P1 — Non-recursive generics** | `Option[T]`, `Pair[A,B]` + polymorphic functions; revive corpus 0540 as PASS | low |
| **P2 — Recursive generics** | `List[T]`, `Tree[T]` + polymorphic recursive functions with structural `\variant` | medium |
| **P3 — Generic predicates & lemmas** | polymorphic inductive predicates and lemma functions (prove-once/reuse); mutually-recursive generics | medium; leans on the lemma/inductive proposals |
| **P4 — Performance & constraints** | optional per-site monomorphization for solver hot spots; investigate bounded polymorphism via Why3 `clone` | medium / research |

Each phase ships corpus drivers in the existing numbering style: a PASS plus FAIL twins — an
**unbound type variable**, a **wrong type-arity application** (`Pair[int]`), and a
**parametricity violation** (inspecting a `T`-typed value), all of which must be rejected.

## 10. Validation

- **0540 revival:** `Option[T]` (and a `map_option`/`get_or_else` over it) verifies, closing the
  documented gap.
- **Polymorphic lemma reuse:** `length_append[T]` proved once and instantiated at `List[int]`
  and `List[Json]` in the same file, both discharging — the core value proposition.
- **JSON refactor:** the §4 generic-list model verifies with a single `List[T]` type, and a
  `wf`/`forall_list` predicate over it carves out well-formedness, demonstrating type-reuse
  without junk values.
- **Encoding gate:** generated WhyML typechecks under Why3 with poly-encoding enabled; a
  monomorphization-on toggle produces equivalent results for the same corpus.

## 11. Open questions

1. **Poly-encoding vs monomorphization policy.** When should P4 monomorphize automatically —
   never, on a per-function pragma, or by a solver-timeout heuristic?
2. **Bounded polymorphism.** Ordering/equality constraints and a type-class-like mechanism map
   naturally onto Why3 `clone`/theory instantiation; is a `#@ datatype List[T: Ord]` surface
   worth a follow-on, or should constraints be passed as explicit comparison parameters?
3. **Higher-order functions.** A single generic fold (`fold[T,A](f, xs, acc)`) would let the JSON
   sum become truly one function; this needs first-class function values in the transpilable
   subset — a separate, larger proposal.
4. **Type-argument inference.** Must call sites/annotations always spell out `List[Json]`, or can
   PyCSL infer type arguments while still honoring its PEP 484 "annotate everything" rule?
5. **Cross-module generic libraries.** A reusable verified `List[T]` theory (type + functions +
   lemmas) shared across files points, again, at theory cloning.

---

### Appendix — the four companion proposals as a unit

With this proposal the quartet of thin PyCSL surfaces over existing Why3 capabilities is complete:

- **Polymorphic datatypes** *parameterize* the carrier types (this proposal).
- **Inductive predicates** *define* relations over those carriers.
- **Typed quantifiers** let contracts *range over* the carriers and relations.
- **Lemma functions** *prove* the (now polymorphic, reusable) inductive consequences SMT cannot
  reach alone.

Each leans on a feature Why3 already implements — polymorphic types, inductive definitions,
first-order quantification over any sort, and lemma/`induction` proving. Together they move the
"needs an imported Rocq/Lean proof" boundary substantially outward while keeping the proofs
in-toolchain and the surface language recognisably Python.
