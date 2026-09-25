# The verified program is not the executed program

**Status: FINDING, a FAMILY with five instances across three independent mechanisms, every
one of them in a `# pycsl-expected: PASS` corpus driver, every one reproduced in CPython.**

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

`0540.py::use_str`, `1003_parametric_datatype_faithful.py::use_str` (and `use_int` beside
it, outside the oracle's population only because it takes no argument).

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
it a family rather than a bug. The honest repair for the corpus is one both files could
carry today: define the constructors in Python (a `dataclass`, a `NamedTuple`) so the
`match` has something to match. Whether PyCSL should REQUIRE that is the same design
question `compose_from` raises, and it is recorded, not decided.

## Mechanism 2 — an annotation that contradicts the value beside it

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

## Mechanism 3 — the `int` placeholder, measured

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
