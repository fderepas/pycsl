# Disciplined mixin composition in PyCSL — worked examples

The trait literature (Schärli et al. ECOOP 2003; Ducasse et al. TOPLAS
2006; Damiani et al. FAC 2014) gives a clean verification story for
mixins that follow a few rules. Python's runtime doesn't enforce those
rules, but a verifier can — by recognizing a discipline at the
annotation level and rejecting code that breaks it.

This document shows what disciplined mixin code looks like in practice
through six examples, ranging from textbook-clean to "this is why the
discipline exists." Each example shows the Python source, the PyCSL
annotations required to make composition machine-checkable, and the
verification obligations the trait calculus produces.

The discipline, in one paragraph: a mixin declares (a) what methods it
provides, (b) what methods it requires from any class composing it, (c)
what fields it touches, and (d) the contract each provided method
satisfies *assuming* the required methods satisfy their declared
contracts. Composition is then a mechanical check: for each composed
class, the verifier confirms that every required method is actually
provided (by another mixin or by the composing class), that no two
mixins provide the same method without an explicit resolution, and
that no two mixins touch the same field without an explicit
resolution. The trait verification machinery handles each mixin once;
composition only re-checks the resolution moves.

The PyCSL annotation surface needed for this discipline is small:

- `#@ mixin` marks a class as a mixin (not instantiable on its own).
- `#@ provides <method>` declares a method this mixin contributes.
- `#@ requires_method <method>: <signature>` declares a method this
  mixin needs from the composing class, with its expected contract.
- `#@ touches_field <name>: <type>` declares a field this mixin
  reads or writes.
- `#@ compose_from <Mixin1>, <Mixin2>, ...` on a concrete class
  declares the trait composition explicitly, and may include
  `resolve <method> from <Mixin>` or `exclude <method> from <Mixin>`
  clauses for conflict resolution.

These annotations don't change runtime behaviour — they're checked
statically by the verifier and erased at execution time, exactly like
PyCSL's existing `#@ requires`/`#@ ensures` directives.

---

## Example 1 — A stateless mixin (the textbook case)

The clean case. A mixin contributes methods that depend only on a
declared interface, with no field interactions.

```python
#@ mixin
class Comparable:
    """Provides equality and ordering operations from a single
    comparison primitive."""

    #@ requires_method compare_to: (self: Comparable, other: Comparable) -> int
    #@   ensures \result < 0 or \result == 0 or \result > 0

    #@ provides __eq__
    #@ ensures \result == (self.compare_to(other) == 0)
    #@ assigns \nothing
    def __eq__(self, other: 'Comparable') -> bool:
        return self.compare_to(other) == 0

    #@ provides __lt__
    #@ ensures \result == (self.compare_to(other) < 0)
    #@ assigns \nothing
    def __lt__(self, other: 'Comparable') -> bool:
        return self.compare_to(other) < 0

    #@ provides __le__
    #@ ensures \result == (self.compare_to(other) <= 0)
    #@ assigns \nothing
    def __le__(self, other: 'Comparable') -> bool:
        return self.compare_to(other) <= 0
```

Composing it:

```python
#@ compose_from Comparable
class Version:
    #@ requires major >= 0
    #@ requires minor >= 0
    def __init__(self, major: int, minor: int):
        self.major = major
        self.minor = minor

    #@ provides compare_to
    #@ ensures \result < 0 or \result == 0 or \result > 0
    #@ ensures \result == 0 <==> (self.major == other.major and self.minor == other.minor)
    #@ assigns \nothing
    def compare_to(self, other: 'Version') -> int:
        if self.major != other.major:
            return self.major - other.major
        return self.minor - other.minor
```

**Verification obligations.**

- `Comparable` is verified once, in isolation, against the abstract
  `compare_to` interface declared in `requires_method`. The proof
  obligation for `Comparable.__lt__` is: assuming `compare_to`
  satisfies its declared post-conditions, `__lt__` satisfies its own
  post-condition. Why3 discharges this trivially.
- `Version` is verified against `Comparable`'s requirements: does
  `Version.compare_to` satisfy the contract declared in
  `Comparable`'s `requires_method`? Yes — the post-condition
  `\result < 0 or \result == 0 or \result > 0` is established by
  the body. Why3 discharges this with linear arithmetic.
- Composition itself adds nothing new — there are no conflicts, no
  field interactions, no overrides.

**What the discipline buys.** `Comparable` becomes a verified component
that any class providing `compare_to` can import. No re-verification
of `Comparable.__eq__` per composition. This is the incremental
verification result from Damiani et al. 2014.

---

## Example 2 — A stateful mixin (the interesting case)

Adding mutable state requires explicit `touches_field` declarations.
This is what "stateful traits" (Bettini, Damiani, Schaefer ECOOP 2007)
formalize.

```python
#@ mixin
class CountingMixin:
    """Counts how many times any operation has been invoked.
    
    Adds one field. Provides one method (read_count). Requires
    the composing class to call self._increment_count() in
    methods that should be counted."""

    #@ touches_field _count: int
    #@ class invariant self._count >= 0

    #@ provides __init__counting
    #@ ensures self._count == 0
    #@ assigns self._count
    def __init__counting(self) -> None:
        """Called by the composing class's __init__ to initialize
        this mixin's state. Naming convention: __init__<mixin> for
        each mixin requiring init-time setup."""
        self._count = 0

    #@ provides read_count
    #@ ensures \result == self._count
    #@ ensures \result >= 0
    #@ assigns \nothing
    def read_count(self) -> int:
        return self._count

    #@ provides _increment_count
    #@ ensures self._count == \old(self._count) + 1
    #@ assigns self._count
    def _increment_count(self) -> None:
        self._count = self._count + 1
```

Composing it:

```python
#@ compose_from CountingMixin
class Counter:
    #@ ensures self._count == 0
    #@ ensures self._value == 0
    #@ assigns self._count, self._value
    def __init__(self):
        self.__init__counting()  # initialize CountingMixin's state
        self._value = 0

    #@ requires amount >= 0
    #@ ensures self._value == \old(self._value) + amount
    #@ ensures self._count == \old(self._count) + 1
    #@ assigns self._value, self._count
    def add(self, amount: int) -> None:
        self._value = self._value + amount
        self._increment_count()
```

**Verification obligations.**

- `CountingMixin.read_count` and `_increment_count` are verified
  against the class invariant `self._count >= 0` and their declared
  post-conditions. Both discharge trivially.
- `Counter.__init__` must establish `CountingMixin`'s class invariant
  by the time it returns. The explicit call to `__init__counting()`
  is what makes this provable — without it, `self._count` would be
  uninitialized and `self._count >= 0` would not be establishable.
- `Counter.add` must preserve `CountingMixin`'s class invariant
  across its body. The `assigns` clause must include `self._count`
  because `_increment_count` modifies it. PyCSL's existing
  assigns-checking handles this.
- **No field conflict**: `Counter` doesn't define `_count`, and
  `CountingMixin` doesn't define `_value`. No resolution clause
  needed.

**What the discipline buys.** The class invariant `self._count >= 0`
is established by `CountingMixin` once and inherited by every
composing class. The composer never has to re-prove it. They only
have to *not break it* — which is exactly the modular reasoning
that behavioral subtyping is designed to enable.

**What breaks without the discipline.** Without
`touches_field _count`, the verifier can't know that
`CountingMixin._increment_count` writes a field that `Counter.add`'s
`assigns` clause must include. Python's runtime doesn't care; the
verifier does. The annotation is what makes the mutation visible
across the mixin boundary.

---

## Example 3 — Conflict resolution (the case the discipline exists for)

Two mixins provide the same method. Without explicit resolution, the
composition is rejected by the verifier (even if Python's C3 would
silently pick one).

```python
#@ mixin
class SizedFromList:
    #@ touches_field _items: list
    
    #@ provides __len__
    #@ ensures \result == \length(self._items)
    #@ ensures \result >= 0
    #@ assigns \nothing
    def __len__(self) -> int:
        return len(self._items)


#@ mixin
class SizedFromCounter:
    #@ touches_field _counter: int
    #@ class invariant self._counter >= 0
    
    #@ provides __len__
    #@ ensures \result == self._counter
    #@ ensures \result >= 0
    #@ assigns \nothing
    def __len__(self) -> int:
        return self._counter
```

Composing both — must resolve the `__len__` conflict explicitly:

```python
#@ compose_from SizedFromList, SizedFromCounter
#@ resolve __len__ from SizedFromList
class Hybrid:
    #@ ensures self._items == []
    #@ ensures self._counter == 0
    #@ assigns self._items, self._counter
    def __init__(self):
        self._items = []
        self._counter = 0
    
    # __len__ comes from SizedFromList; SizedFromCounter.__len__
    # is excluded from the composed class.
    
    #@ requires item is not None
    #@ ensures self._items == \old(self._items) + [item]
    #@ ensures self._counter == \old(self._counter) + 1
    #@ assigns self._items, self._counter
    def add(self, item) -> None:
        self._items = self._items + [item]
        self._counter = self._counter + 1
```

**Verification obligations.**

- Without the `#@ resolve __len__ from SizedFromList` clause, the
  verifier rejects the composition with a clear error: "method
  `__len__` is provided by both `SizedFromList` and
  `SizedFromCounter`; add a `resolve` or `exclude` clause."
- With the clause, only `SizedFromList.__len__` is part of `Hybrid`.
  Its contract `\result == \length(self._items)` becomes `Hybrid`'s
  `__len__` post-condition.
- The fact that `SizedFromCounter` *also* provides a `__len__` with
  a different post-condition (`\result == self._counter`) is
  discarded — the user explicitly chose `SizedFromList`'s
  semantics. The verifier doesn't try to prove
  `\length(self._items) == self._counter` unless the user
  explicitly states it.
- The class invariant `self._counter >= 0` from `SizedFromCounter`
  is *still* inherited and must be preserved by `add`. Resolving
  `__len__` doesn't disinherit the mixin's invariants — only the
  resolved method is taken from one side.

**What the discipline buys.** Python's C3 would pick
`SizedFromList.__len__` (left-to-right precedence) silently. The
discipline forces the user to acknowledge the choice. If they
later swap the order or add a new mixin, the conflict resurfaces
and they must re-resolve. No silent semantic changes from
refactoring base-class order.

---

## Example 4 — The diamond pattern (where MRO matters)

The classical multiple-inheritance diamond, made tractable by
disciplined mixin composition.

```python
#@ mixin
class Loggable:
    """Provides logging to a buffer."""
    #@ touches_field _log: list
    
    #@ provides log
    #@ ensures self._log == \old(self._log) + [message]
    #@ assigns self._log
    def log(self, message: str) -> None:
        self._log = self._log + [message]
    
    #@ provides __init__loggable
    #@ ensures self._log == []
    #@ assigns self._log
    def __init__loggable(self) -> None:
        self._log = []


#@ mixin
#@ compose_from Loggable
class TimedMixin:
    """Logs entry to and exit from operations. Depends on Loggable
    for the log() method; composing class must include both."""
    #@ touches_field _start_time: int
    
    #@ requires_method log: (self: TimedMixin, msg: str) -> None
    
    #@ provides start
    #@ ensures self._start_time == now
    #@ ensures self._log == \old(self._log) + ["start at " + \str(now)]
    #@ assigns self._start_time, self._log
    def start(self, now: int) -> None:
        self._start_time = now
        self.log("start at " + str(now))


#@ mixin
#@ compose_from Loggable
class CountedMixin:
    """Counts operations and logs each. Also depends on Loggable."""
    #@ touches_field _count: int
    #@ class invariant self._count >= 0
    
    #@ requires_method log: (self: CountedMixin, msg: str) -> None
    
    #@ provides record
    #@ ensures self._count == \old(self._count) + 1
    #@ ensures self._log == \old(self._log) + ["op " + \str(\old(self._count))]
    #@ assigns self._count, self._log
    def record(self) -> None:
        self.log("op " + str(self._count))
        self._count = self._count + 1


# The diamond: both TimedMixin and CountedMixin depend on Loggable.
#@ compose_from TimedMixin, CountedMixin
class Operation:
    #@ ensures self._log == []
    #@ ensures self._start_time == 0
    #@ ensures self._count == 0
    #@ assigns self._log, self._start_time, self._count
    def __init__(self):
        self.__init__loggable()
        self._start_time = 0
        self._count = 0
```

**Verification obligations.**

- `Loggable` is verified once.
- `TimedMixin` is verified once, with `Loggable.log` available as a
  required method. `TimedMixin.start`'s contract is proven assuming
  `log` satisfies `Loggable.log`'s contract.
- `CountedMixin` is verified once, similarly.
- `Operation`'s composition is checked: `Loggable` is composed
  exactly once (because both `TimedMixin` and `CountedMixin` declare
  it as a dependency, but the linearization recognizes the
  diamond). The `_log` field is touched by all three mixins
  consistently; no resolution needed because `Loggable` is the
  unique provider.
- All three class invariants (`Loggable._log` being a list,
  `CountedMixin._count >= 0`, etc.) are conjoined and checked at
  every method boundary in `Operation`.

**What the discipline buys.** The diamond is resolved at composition
time, not silently at runtime. Each mixin's contract is verified in
isolation. The composed `Operation` is verified incrementally — only
the composition rules, not the mixin bodies, are re-checked.

This is exactly the diamond problem the C3 algorithm solves at
runtime, made *visible* at verification time. The trait literature's
flattening semantics ensures the result is unambiguous; behavioral
subtyping (Family 2 from the survey) ensures the inherited contracts
compose correctly.

---

## Example 5 — Required-method composition (real mixin reuse)

A mixin that's parameterized by an abstract operation. This is the
shape most real-world Python mixins should take, and the discipline
makes the dependency explicit.

```python
#@ mixin
class Cached:
    """Memoizes a computation. The composing class must provide
    compute() with a deterministic, side-effect-free contract."""
    
    #@ touches_field _cache: dict
    #@ touches_field _cache_valid: bool
    
    #@ requires_method compute: (self: Cached) -> int
    #@   ensures \result == \old(\result)   # determinism
    #@   assigns \nothing                    # purity
    
    #@ provides __init__cached
    #@ ensures self._cache_valid == False
    #@ ensures self._cache == {}
    #@ assigns self._cache, self._cache_valid
    def __init__cached(self) -> None:
        self._cache = {}
        self._cache_valid = False
    
    #@ provides invalidate
    #@ ensures self._cache_valid == False
    #@ assigns self._cache_valid
    def invalidate(self) -> None:
        self._cache_valid = False
    
    #@ provides get
    #@ ensures \result == self.compute()
    #@ ensures self._cache_valid == True
    #@ assigns self._cache, self._cache_valid
    def get(self) -> int:
        if not self._cache_valid:
            self._cache["value"] = self.compute()
            self._cache_valid = True
        return self._cache["value"]
```

A composing class — note that the determinism precondition is what
makes the memoization correct:

```python
#@ compose_from Cached
class FactorialCache:
    #@ requires n >= 0
    #@ ensures self._n == n
    #@ ensures self._cache_valid == False
    #@ ensures self._cache == {}
    #@ assigns self._n, self._cache, self._cache_valid
    def __init__(self, n: int):
        self._n = n
        self.__init__cached()
    
    #@ provides compute
    #@ ensures \result == factorial(self._n)   # using pure factorial axiom
    #@ ensures \result >= 1
    #@ assigns \nothing
    def compute(self) -> int:
        result = 1
        i = 1
        #@ loop invariant 1 <= i and i <= self._n + 1
        #@ loop invariant result == factorial(i - 1)
        #@ loop variant self._n - i + 1
        while i <= self._n:
            result = result * i
            i = i + 1
        return result
```

**Verification obligations.**

- `Cached.get` is verified assuming `compute` is deterministic and
  pure. The post-condition `\result == self.compute()` follows
  trivially in the "cache miss" branch and from determinism in the
  "cache hit" branch.
- `FactorialCache.compute` is verified against `Cached`'s required
  contract: is it deterministic? (Yes — same `self._n`, same
  result.) Is it pure? (Yes — `assigns \nothing`.)
- The composition adds no obligations beyond those.

**What the discipline buys.** `Cached` is a verified component
parameterized by an abstract `compute`. Any class providing a
deterministic pure `compute` can compose with `Cached` and inherit
the correctness of memoization. The compositional verification
result generalizes to arbitrary new uses without re-verifying
`Cached`.

This is also exactly the use case where `axiom_from` shines: the
`compute` method in `FactorialCache` references a `factorial`
function that's defined axiomatically via
`#@ axiom_from rocq Pycsl.Reference.Factorial.factorial_def` —
the pure mathematical factorial. The mixin verifies; the
implementation verifies; the proof side carries the algebra.

---

## Example 6 — A counter-example (real Python that the discipline rejects)

Not all Python mixin code fits the discipline. Here's a realistic
example of code that breaks, with an explanation of why.

```python
class LoggingMixin:
    """Logs every method call. The 'logging' isn't optional or
    parameterized — it's monkey-patching."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._log = []
        # Patch all the methods on self to log themselves:
        for name in dir(self):
            if not name.startswith('_'):
                original = getattr(self, name)
                if callable(original):
                    def make_wrapped(orig, n):
                        def wrapped(*a, **kw):
                            self._log.append(n)
                            return orig(*a, **kw)
                        return wrapped
                    setattr(self, name, make_wrapped(original, name))


class Database(LoggingMixin):
    def query(self, sql: str) -> list:
        return []  # pretend implementation
    
    def insert(self, row: dict) -> None:
        pass


db = Database()
db.query("SELECT 1")   # Logs "query"
db.insert({"a": 1})    # Logs "insert"
```

**Why the verifier rejects this.**

- `LoggingMixin.__init__` uses `dir(self)` and `setattr(self, ...)`
  — runtime introspection and dynamic dispatch override.
  PyCSL has no model for these.
- The `provides` declarations would have to enumerate *every*
  method of the composing class, which the mixin can't know at
  its own definition time. The whole point of this style is that
  it works for arbitrary subclasses without listing them.
- The contract of `db.query` is *changed* by composition — it now
  has a side effect on `_log` that wasn't in `Database.query`'s
  declared `assigns` clause. The mixin retroactively breaks the
  composing class's contracts.

**The disciplined alternative.**

```python
#@ mixin
class LoggingMixin:
    """Provides explicit logging primitives. Composing classes
    must call self._log_call(name) at the start of methods they
    want logged. No introspection, no monkey-patching."""
    
    #@ touches_field _log: list
    
    #@ provides __init__logging
    #@ ensures self._log == []
    #@ assigns self._log
    def __init__logging(self) -> None:
        self._log = []
    
    #@ provides _log_call
    #@ ensures self._log == \old(self._log) + [name]
    #@ assigns self._log
    def _log_call(self, name: str) -> None:
        self._log = self._log + [name]


#@ compose_from LoggingMixin
class Database:
    #@ ensures self._log == []
    #@ assigns self._log
    def __init__(self):
        self.__init__logging()
    
    #@ ensures self._log == \old(self._log) + ["query"]
    #@ assigns self._log
    def query(self, sql: str) -> list:
        self._log_call("query")
        return []
    
    #@ ensures self._log == \old(self._log) + ["insert"]
    #@ assigns self._log
    def insert(self, row: dict) -> None:
        self._log_call("insert")
```

**What changed.** The "magic" went away. Each method that wants to
be logged calls `_log_call("name")` explicitly. The mixin
contributes the field and the primitive, the composing class
contributes the calls. The mutation is visible in every method's
`assigns` clause, and the contract correctly states that the method
appends to the log.

This is the trade-off the discipline imposes. You lose the ability
to retroactively modify methods you didn't write. You gain modular
verification, clear assigns clauses, and contract preservation.
Most production code that uses mixins does so for capabilities
(`Comparable`, `Hashable`, `Iterable`) where this discipline is
natural. Code that uses mixins for cross-cutting concerns
(logging, transaction management, security) often needs to be
re-written in the disciplined style — or verified outside the
mixin framework entirely.

---

## Summary

The discipline imposes four rules on Python mixins:

1. **No state crosses mixin boundaries silently** — declare every
   field a mixin touches via `touches_field`.
2. **No method depends on undeclared interfaces** — declare every
   method a mixin needs from the composing class via
   `requires_method`, with the expected contract.
3. **No method conflict resolves silently** — when two mixins
   provide the same method, the composing class must `resolve` or
   `exclude` explicitly.
4. **No retroactive contract modification** — a mixin cannot
   change the contract of a method it didn't provide.

In return, you get:

- Each mixin verified once, in isolation, against its declared
  interface.
- Composition verified incrementally — only the resolution moves
  are re-checked.
- Diamond inheritance handled cleanly via the trait-flattening
  semantics.
- Clear error messages when composition is ill-formed.
- Contracts that compose by conjunction and refinement, not by
  hope.

The price is that Python mixin code intended for runtime
introspection (logging via `setattr`, transaction wrappers via
`__getattribute__`, security via `__getattr__` hooks) doesn't fit
the discipline. These patterns are common but not universal; for
the self-hosting case (annotating `pycsl`'s own source with PyCSL
contracts), the discipline is comfortable because pycsl's own
mixin use is exactly the textbook kind.

The implementation cost for PyCSL is a handful of new directives
(`mixin`, `provides`, `requires_method`, `touches_field`,
`compose_from`, `resolve`, `exclude`) and a composition-checking
pass that runs after MRO computation. The verification machinery
underneath is the same flat-record + behavioral-subtyping
combination recommended in the broader survey — the trait
discipline just makes the obligations crisper and more modular.

## References

- Schärli, N., Ducasse, S., Nierstrasz, O., Black, A. P. *Traits:
  Composable Units of Behavior.* ECOOP 2003.
- Ducasse, S., Nierstrasz, O., Schärli, N., Wuyts, R., Black, A. P.
  *Traits: A Mechanism for Fine-Grained Reuse.* ACM TOPLAS 28(2),
  2006.
- Bettini, L., Damiani, F., Schaefer, I. *Stateful Traits.* ECOOP
  2007.
- Damiani, F., Dovland, J., Johnsen, E. B., Schaefer, I.
  *Verifying Traits: An Incremental Proof System for Fine-Grained
  Reuse.* Formal Aspects of Computing 26, 2014.
- Servetto, M., Zucca, E. *Iteratively Composing Statically
  Verified Traits.* arXiv:1902.09685, 2019.
