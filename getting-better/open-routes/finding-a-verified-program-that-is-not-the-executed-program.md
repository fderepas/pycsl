# The verified program is not the executed program

**Status: FINDING, a FAMILY with EIGHTEEN instances across FIVE independent mechanisms,
spanning at least seventeen `# pycsl-expected: PASS` corpus drivers, every one reproduced in
CPython.**

    mechanism                                         functions   files
    `#@ datatype` constructors                            11        9
    `#@ compose_from` provider methods                     3        3
    the verifier supplying a name Python lacks             2        2
    a `@dataclass` annotation contradicting its default    1        1
    the `int` placeholder making a signature unsatisfiable 1        1

A PyCSL file is two things at once: a Python program and a specification of that program.
Every instrument in this repo checks the second against the prover. This finding is about
the first — about drivers whose PYTHON half does not run, so that what was verified is a
program nobody can execute.

None of these is unsoundness in the prover's own terms. Each is a place where a directive,
a modelling choice or an annotation introduces something the Python program does not have,
and the contract is then discharged over an exit the program never reaches. A contract over
a function with no normal exit is VACUOUSLY TRUE — see the sibling record
`finding-a-contract-over-a-function-that-never-returns.md` and wall-lesson (v5).

## How they were found, and why not earlier

`bin/check-corpus-contract-truth-args.py` grew three axes this generation, in this order:

1. **POST-STATE** — `#@ ensures self.f == \old(self.f) + 1`, evaluated against a snapshot
   taken before the call. Found `0554`.
2. **NO-NORMAL-EXIT** — the tuple loop stopped BREAKING on the first raise, so "raises on
   THIS argument" could be told apart from "has no normal exit at all". Named `0496`.
3. **PREDICATE** — any `#@ ensures` over `\result` that is not an equality. The census said
   this was the largest evaluable group the oracle was skipping: **102 clauses of
   `#@ ensures \result >= 0` alone**, plus a tail of `>= x`, `> 0`, `>= 1`, `>= 5`,
   `\str_length(\result) == …`. Population 579 functions / 6114 evaluations ->
   **692 / 7063**.

The third axis found **five more instances in one run**, all of them under
`#@ ensures \result >= 0` — the most ordinary clause in the corpus. Nothing was hiding.
The oracle had simply never been able to read the clause.

**Which instrument should have found them and why did it not:** every oracle here is
CONTRACT-DRIVEN. It runs a corpus function only when a clause it can evaluate asks it to.
A file whose clauses are all inequalities was never executed at all — not by this oracle,
not by the suite (which runs the verifier, never CPython), not by
`check-class-invariant-establishment` (which constructs objects and never calls methods).
The gap was not in any instrument's POPULATION FILTER; it was in the shape of the question.

## Mechanism 1 — a directive whose names have no runtime counterpart

### `#@ compose_from`: the provider is flattened in the verifier, not in Python

`0549.py::Facade.run`, `0554.py::Service.tick`, `1858::Facade.run`. Censused: **all eleven
composing classes in the corpus compose a provider they do not inherit, and in ten of the
eleven the provided name is absent from the instance at runtime.** Full record, including
the repair and the measurement that the obvious repair was itself REFUSED, in
`finding-a-contract-over-a-function-that-never-returns.md`.

### `#@ datatype`: the constructors exist only in the annotation world

**ELEVEN functions across NINE files** — the largest single mechanism in the family, and
eight of them only appeared when the ZERO-ARGUMENT oracle stopped folding "the function
raised" into "could not run standalone":

    0521.py::build_and_read   NameError: name 'Some' is not defined
    0527.py::left_is_leaf     NameError: name 'Node'
    0531.py::guarded          NameError: name 'MSome'
    0533.py::leaf_is_zero     NameError: name 'Leaf'
    0535.py::is_red_or_green  NameError: name 'Blue'
    0536.py::unwrap           NameError: name 'Wrap'
    0540.py::use_int          NameError: name 'Just'      0540.py::use_str   likewise
    0546.py::get              NameError: name 'Some'
    1003.py::use_int          NameError: name 'Just'      1003.py::use_str   likewise

```python
#@ datatype Option[T] = Nothing | Just(T)

#@ ensures \str_length(\result) == \str_length(s)
def use_str(s: str) -> str:
    o = Just(s)              # NameError: name 'Just' is not defined
    match o:
        case Just(v): return v
        case Nothing(): return ""
```

`Just` and `Nothing` are declared by the directive and defined nowhere in Python. They are
used in **executable position** — an assignment and a `match`, not a `#@ ghost` or an
annotation — so the body is ordinary Python that raises `NameError` on every call. Both
drivers are `# pycsl-expected: PASS` and both certify a `\str_length` relation over a
function with no run.

This is the same species as `compose_from` and a different directive, which is what makes
it a family rather than a bug.

### The obvious repair was TRIED, and it is not free

Add the Python definitions the `match` needs:

```python
@dataclass
class Nothing: pass

@dataclass
class Just:
    _0: Any
```

**`0540` then RUNS — `use_int()` is 7, `use_str("ab")` is `"ab"` — and it still
VERIFIES.** `match` finds the constructors through the dataclass `__match_args__`, and the
proof goes through unchanged in its conclusions.

But the EMISSION MOVES, and it moves in a way that has to be understood before this is
called a fix:

```
+   type just = { mutable _0: int }
-     let o = ref (Just 7) in            +     let o = (Just 7) in
-     match !o with                      +     match o with
```

The class declaration makes `Just` a RECORD as well as a variant constructor, and the local
loses its `ref`. The file verifies either way, but it is no longer verifying quite the same
model — which is exactly the thing a corpus repair must not do quietly to nine drivers at
once.

So the measurement is recorded and the repair is NOT landed. What it establishes is that
the gap is closable at all, and where the real decision lies: either `#@ datatype` emits the
Python-level constructors itself (so the declaration is the definition, and the model is
unaffected), or the directive REQUIRES the definitions and Module 5 learns not to
double-model a class that a `#@ datatype` already declares. Both are design changes to a
documented directive, with nine drivers in the blast radius, and lesson (u4) applies: a rule
binds every program that could be written, not only the nine that exist.

## Mechanism 2 — the verifier supplies a name the program does not have

Two drivers, two different ways, and the second one states the equivalence it breaks.

### `0640.py::f` — a stdlib name resolved at verification time, never imported

```python
#@ ensures \result == -5
def f() -> int:
    return ast.literal_eval("-5")        # NameError: name 'ast' is not defined
```

The file never imports `ast`. It does not have to: PyCSL evaluates
`ast.literal_eval` on a compile-time-constant argument AT VERIFICATION TIME, with the host's
own `ast`, and emits the value `-5`. That is exactly what makes `\result == -5` provable —
and the docstring says so, calling the host evaluation "the source of truth". The host is
not the program's truth. CPython has no `ast` in that module's namespace.

### `0642.py::f` — `exec` splicing, and the equivalence claim that is false

```python
#@ ensures \result == 6
def f() -> int:
    exec("x = 5\ny = x + 1")
    return y                              # NameError: name 'y' is not defined
```

PyCSL parses the constant string at verification time and splices the statements in place.
The driver's own docstring: *"the splice emits byte-identical WhyML to the inline form (the
soundness evidence: verification-equivalent, rev4 §8.5)"*.

**Byte-identical emission to the inline form is evidence that the MODEL matches the inline
form. It is not evidence that PYTHON does** — and Python does not. `exec` inside a function
body cannot create a local binding in CPython (function locals are resolved statically);
measured both ways, including `locals().get("y")`, which is `None`. The inline form returns
6; the `exec` form raises. The two are verification-equivalent and not program-equivalent,
which is the whole of this finding in one driver.

## Mechanism 3 — an annotation that contradicts the value beside it

`0746.py::Registry.arity`:

```python
@dataclass
class Registry:
    formal_params: Dict[str, List[str]] = None      # <- annotation vs. default

    #@ ensures \result >= 0
    def arity(self, name: str) -> int:
        fp = self.formal_params.get(name, [])       # AttributeError: 'NoneType'
        return len(fp)
```

`Dict[str, List[str]] = None` is rejected by every Python type checker without `Optional`.
PyCSL models the field by the ANNOTATION, so `arity` is proved over a map while
`Registry().arity(name)` raises for every name. The file's own `__main__` block writes
`r.formal_params = {}` before calling — **the author working around it by hand, inside the
driver, and nothing reading that**.

The defect is narrow and the rule that closes it is narrow too: a field whose declared type
and default value disagree should be refused, exactly as a type checker refuses it. Sibling
of routes #148/#149, which repaired the field type where it came from an `__init__`
parameter.

## Mechanism 4 — the `int` placeholder, measured

`0453.py::FunctionAnalyzer.visit_FunctionDef`:

```python
#@ ensures \result >= 0
#@ assigns self.everything_fine
def visit_FunctionDef(self, node: int) -> int:
    if not node.name.islower() and not (...):       # AttributeError: 'int' has no 'name'
```

`int` is what PyCSL models an AST node as. The consequence is that **the declared signature
is unsatisfiable**: no `int` has `.name`, so no call that respects the annotation can run.
The annotation is not a description of the argument; it is a placeholder for a type the
modeller does not have.

This is the conversion track's named **#1 blocker** — "int-placeholder annotations on
`\trusted` stubs" — sitting in a green corpus driver with a contentful postcondition over
it, and it is the first time that blocker has been caught by an INSTRUMENT rather than
by hand at a conversion attempt. `0453`'s docstring is unusually honest about its limits
("the concrete outcome for a specific source string is NOT proven … which PyCSL does not
model (honest per the plan)") and says nothing about the signature being uninhabitable.

## What this family costs, stated exactly

* **Not unsoundness in the prover.** Each contract is true of the model. Nothing here shows
  a false claim about a value the program computes.
* **The corpus over-states what it demonstrates.** Five PASS drivers and the flagship of
  the mixin feature certify properties of programs that raise on every input. A reader
  counting green drivers as evidence that the modelled feature works is counting wrong.
* **The reachability question is now asked.** `NEVER_RETURNS` in
  `bin/check-corpus-contract-truth-args.py` names all eight of today's instances with a
  reason each, and an UNNAMED one turns the plane red. `#@ \diverges` is READ from the
  directive rather than listed, because a function promised not to return is the one shape
  where having no normal exit IS the contract.

## Wall-lesson (x5)

**An instrument that only runs what it can check will never tell you what it cannot run.**
Every oracle in this battery executes a corpus function *because* a clause asked it to. The
five defects above sat under `#@ ensures \result >= 0` — the most common clause in the
corpus — and the reason no instrument had executed those functions was not a filter anyone
chose. It was that the question "does this program run" had never been separated from the
question "is this contract true".
