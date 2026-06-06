# Concurrent Access Model for PyCSL — Strategy 3

## Sequential Reduction via Mutex Discipline

**Goal:** Extend PyCSL to verify multithreaded Python programs by reducing
concurrency to sequential WP proofs wherever mutex discipline holds.

The key insight: if all accesses to a shared variable are protected by the
same mutex, then within a critical section the variable behaves like a local
one. WP can treat the critical section body as sequential code. Only
unprotected accesses require explicit concurrent reasoning (Rely/Guarantee),
which is deferred to a later phase.

---

## Phase 1 — New `#@` Annotations

### 1.1 Shared-state declarations

Declare which variables are shared across threads and which mutex protects
them:

```python
#@ shared x protected_by lock_a
#@ shared counter protected_by mutex_counter
#@ shared buffer protected_by buf_lock
```

A variable without a `protected_by` clause is **unprotected shared state** —
PyCSL emits a warning and treats it conservatively (any thread may modify it
at any point).

### 1.2 Thread entry-point annotation

Mark functions that serve as thread entry points:

```python
#@ thread_entry
def worker(arg: int) -> None:
    ...
```

This tells PyCSL that `worker` may execute concurrently with other
`thread_entry` functions (and with `main`).

### 1.3 Critical section boundaries

Mark mutex acquire/release so PyCSL knows where sequential reasoning is
valid:

```python
#@ acquires lock_a
lock_a.acquire()
# ... critical section: x behaves like a local variable here ...
#@ releases lock_a
lock_a.release()
```

Alternatively, support Python's `with` statement as syntactic sugar:

```python
#@ critical lock_a
with lock_a:
    x += 1
    #@ ensures x == \old(x) + 1
```

### 1.4 Mutex invariants

Each mutex can carry an invariant that must hold whenever the mutex is
**unlocked** (i.e., whenever no thread is inside the critical section):

```python
#@ mutex_invariant lock_a: x >= 0 and x <= 100
```

This invariant is:
- **assumed** on `acquire` (the thread entering the critical section may
  assume it)
- **proved** on `release` (the thread leaving the critical section must
  re-establish it)

This is the classical monitor invariant pattern and is the core mechanism
that makes sequential WP work for shared state.

---

## Phase 2 — Pipeline Changes

### 2.1 Module2 (Parser) — Grammar extensions

Add grammar rules to `csl.lark`:

```
shared_decl    : "shared" NAME "protected_by" NAME
thread_entry   : "thread_entry"
acquires       : "acquires" NAME
releases       : "releases" NAME
critical       : "critical" NAME
mutex_invariant: "mutex_invariant" NAME ":" expr
```

New CSLNode subclasses:

```python
@dataclass
class SharedDecl(CSLNode):
    variable: str
    mutex: str

@dataclass
class ThreadEntry(CSLNode):
    pass

@dataclass
class Acquires(CSLNode):
    mutex: str

@dataclass
class Releases(CSLNode):
    mutex: str

@dataclass
class CriticalSection(CSLNode):
    mutex: str

@dataclass
class MutexInvariant(CSLNode):
    mutex: str
    expr: CSLNode
```

### 2.2 Module3 (Weaver) — AST attachment

New `csl_*` fields on `ast.Module`:

| Field | Type | Content |
|-------|------|---------|
| `csl_shared_decls` | `List[SharedDecl]` | Shared variable declarations |
| `csl_mutex_invariants` | `Dict[str, CSLNode]` | Mutex name → invariant expr |

New fields on `ast.FunctionDef`:

| Field | Type | Content |
|-------|------|---------|
| `csl_thread_entry` | `bool` | True if marked as thread entry |

New fields on `ast.With` / statement level:

| Field | Type | Content |
|-------|------|---------|
| `csl_critical_mutex` | `str | None` | Mutex name for critical section |
| `csl_acquires` | `str | None` | Mutex being acquired |
| `csl_releases` | `str | None` | Mutex being released |

### 2.3 Module4 (SemanticAnalyzer) — Validation

New checks:

1. **Balanced acquire/release:** every `acquires` has a matching `releases`
   within the same function scope (or use `critical` blocks which are
   balanced by construction).
2. **Protected access check:** every read/write of a `shared` variable
   occurs inside a critical section for its declared mutex. Violations
   produce `PyCSLSemanticError`.
3. **Mutex invariant scope:** the invariant expression may only reference
   the shared variables protected by that mutex.
4. **No nested locking** (initially): acquiring a mutex while already
   holding it is rejected. Hierarchical locking can be added later.

### 2.4 Module5 (IREmitter) — New IR fields

Top-level IR additions:

```json
{
  "shared_vars": [
    {"name": "x", "mutex": "lock_a", "type": "int"}
  ],
  "mutex_invariants": {
    "lock_a": { "type": "BinOp", "op": ">=", ... }
  },
  "thread_entries": ["worker", "producer", "consumer"]
}
```

Per-function body additions for critical sections:

```json
{
  "type": "CriticalSection",
  "mutex": "lock_a",
  "body": [ ... ],
  "assume_invariant": { ... },
  "prove_invariant": { ... }
}
```

### 2.5 Module6 (WhyMLTranspiler) — WhyML generation

The critical translation. Each mutex + its protected variables become a
WhyML module with a ref and an invariant:

```whyml
module SharedState

  use int.Int
  use ref.Ref

  val x : ref int

  (* Mutex invariant: assumed on acquire, proved on release *)
  predicate lock_a_inv (x_val: int) =
    x_val >= 0 /\ x_val <= 100

end
```

A critical section translates to:

```whyml
let worker () =
  (* acquire: assume mutex invariant *)
  assume { lock_a_inv !x };
  (* critical section body — sequential WP applies *)
  x := !x + 1;
  (* release: prove mutex invariant *)
  assert { lock_a_inv !x }
```

The `assume` at acquire and `assert` at release is the standard
monitor-invariant encoding. WP computes the weakest precondition of the
critical section body sequentially — no interleaving reasoning needed.

**Outside critical sections**, shared variables are modeled as havoc'd
(assigned arbitrary values satisfying the mutex invariant) at every
potential yield point:

```whyml
(* Between critical sections, x could be anything satisfying the invariant *)
any_x: int;
assume { lock_a_inv any_x };
x := any_x;
```

---

## Phase 3 — Memory Model Extension

Add a fourth memory model: `"concurrent"`.

| Model | Value | Semantics |
|-------|-------|-----------|
| `hoare` | `"hoare"` | Value-semantic arrays, no heap |
| `typed` | `"typed"` | Heap-based refs |
| `store` | `"store"` | Heap-based store record |
| **`concurrent`** | `"concurrent"` | Typed model + mutex discipline |

The `concurrent` model extends `typed` (since shared variables must be
refs) and adds:
- Mutex invariant predicates
- `assume`/`assert` pairs at acquire/release boundaries
- Havoc of shared state between critical sections

Selected via `--memory-model concurrent` on the CLI or `#@ \memory_model concurrent` in the source.

---

## Phase 4 — Static Checker (Lightweight Mthread Analog)

Before running WP, a static pass analyzes the program to:

1. **Build a shared-access map:** for each shared variable, collect all
   read/write program points and which mutex (if any) is held.
2. **Flag unprotected accesses:** emit warnings or errors for shared
   variable accesses outside any critical section.
3. **Flag potential deadlocks:** detect lock-ordering violations in
   functions that acquire multiple mutexes.

This is a lightweight analog of Frama-C's Mthread — no abstract
interpretation, just syntactic/scope analysis. It runs as a pass within
Module4 (SemanticAnalyzer) or as a new Module3.5.

Implementation: `src/pycsl/ConcurrencyChecker.py`

```python
class ConcurrencyChecker:
    def check(self, tree: ast.AST) -> List[ConcurrencyWarning]:
        """Walk the AST, track held mutexes, flag unprotected accesses."""
        ...
```

---

## Phase 5 — Agent Support

### 5.1 Skill updates

- **`contract-writer` skill:** add rules for `shared`, `acquires`,
  `releases`, `critical`, and `mutex_invariant` annotations.
- **`invariant-writer` skill:** add rules for mutex invariants — they are
  structurally similar to class invariants.
- **`pycsl-annotate` skill:** add the concurrent annotation patterns and
  their NEVER constraints (e.g., never access shared state outside a
  critical section without explicit justification).

### 5.2 agent-annotate.py guards

New guards for the GuardPipeline:

| Guard | What it fixes |
|-------|--------------|
| `_guard_shared_access` | Wraps unprotected shared accesses in `#@ \trusted` |
| `_guard_mutex_invariant` | Adds default `True` mutex invariant if missing |
| `_inject_critical_sections` | Detects `with lock:` patterns and adds `#@ critical` |

### 5.3 agent-reconcile.py

New recommendation target: `"concurrent-access-error"` — when the prover
fails because a mutex invariant cannot be re-established on release.

---

## Phase 6 — Test Suite

### 6.1 Reference tests

Add tests in `test-suite/corpus/pycsl-reference/`:

| Test | Feature |
|------|---------|
| `0250` | Basic shared variable + mutex invariant |
| `0251` | Critical section with `with` syntax |
| `0252` | Two threads, one shared counter |
| `0253` | Multiple mutexes protecting different variables |
| `0254` | Unprotected access (expected semantic error) |
| `0255` | Nested critical sections (expected error, initially) |
| `0256` | Mutex invariant violated on release (expected proof failure) |

### 6.2 Integration tests

Add to `tests/to_annotate/`:

```python
# 070-concurrent-counter.py
import threading

counter = 0
lock = threading.Lock()

def increment():
    global counter
    with lock:
        counter += 1

def worker():
    for _ in range(100):
        increment()
```

---

## Appendix A — Examples Adapted from Frama-C Mthread

The three examples below are adapted from the Frama-C Mthread example suite
(`frama-c-mthread-examples/`). Each shows the original C pattern, the Python
translation, the PyCSL-annotated version, and the expected analysis outcome.

---

### A.1 — Matrix: Partitioned Mutex Protection

**Original C pattern** (`matrix2.c`): A shared matrix is split into N
stripes. Each thread owns stripe `i` (indices `i, i+N, i+2N, …`) and
protects it with `locks[i]`. The main thread reads the full matrix by
acquiring each lock in turn. Mthread proves **no race conditions** because
every cell is consistently protected by exactly one mutex.

**Python translation:**

```python
import threading

N = 5
S = 150

matrix: list = [0] * S
locks: list = [threading.Lock() for _ in range(N)]

def compute(index: int, prev: int) -> int:
    return prev + 1

def completed(total: int) -> bool:
    return total > 1000

def job(k: int) -> None:
    """Worker thread: updates stripe k of the matrix."""
    while True:
        with locks[k]:
            j = k
            while j < S:
                matrix[j] = compute(j, matrix[j])
                j += N

def main() -> None:
    threads = []
    for i in range(N):
        t = threading.Thread(target=job, args=(i,))
        t.start()
        threads.append(t)

    total = 0
    while not completed(total):
        total = 0
        for i in range(N):
            with locks[i]:
                j = i
                while j < S:
                    total += matrix[j]
                    j += N
```

**PyCSL-annotated version:**

```python
#@ shared matrix protected_by locks    # partitioned: matrix[j] protected by locks[j % N]
#@ mutex_invariant locks[i]: \forall j. (0 <= j and j < S and j % N == i) ==> matrix[j] >= 0

#@ thread_entry
def job(k: int) -> None:
    #@ requires 0 <= k and k < N
    while True:
        #@ critical locks[k]
        with locks[k]:
            j = k
            #@ loop_invariant k <= j and j <= S and j % N == k
            #@ loop_invariant \forall m. (0 <= m and m < S and m % N == k and m < j) ==> matrix[m] >= 0
            #@ loop_variant S - j
            while j < S:
                matrix[j] = compute(j, matrix[j])
                j += N

def main() -> None:
    total = 0
    while not completed(total):
        total = 0
        i = 0
        #@ loop_invariant 0 <= i and i <= N
        #@ loop_invariant total >= 0
        #@ loop_variant N - i
        while i < N:
            #@ critical locks[i]
            with locks[i]:
                j = i
                #@ loop_invariant i <= j and j <= S
                #@ loop_invariant total >= 0
                #@ loop_variant S - j
                while j < S:
                    total += matrix[j]
                    j += N
            i += 1
```

**Expected outcome:** All proof obligations discharged. The partitioned mutex
scheme ensures each cell `matrix[j]` is protected by `locks[j % N]`. No
race conditions. This demonstrates that Strategy 3 handles **fine-grained
locking** — not just a single global lock.

**What Mthread found (C version):** "Possible read/write data races: none."
The same result should hold for the PyCSL version by construction.

---

### A.2 — Shared Variables: Race Condition Detection

**Original C pattern** (`sharedvars.c`): Six global variables with varying
sharing patterns. Some are only accessed by one thread (`u1`, `u2`, `u3`),
others are truly shared across threads without any mutex protection (`s4`,
`s5`, `s6`). Mthread detects **three race conditions** on `s4`, `s5`, `s6`.

**Python translation:**

```python
import threading

# Unshared variables — accessed by at most one thread at a time
u1 = 0   # Used by main before thread, then by thread1
u2 = 0   # Only used by main
u3 = 0   # Used by thread3 before spawning thread31, then by thread31

# Shared variables — accessed concurrently WITHOUT mutex protection
s4 = 0   # Used by main and thread4  → RACE
s5 = 0   # Used by thread5 and thread51  → RACE
s6 = 0   # Used by thread4 and thread6  → RACE

def f1() -> None:
    global u1
    t = u1
    u1 += 1

def f31() -> None:
    global u3
    t = u3
    u3 = 31

def f3() -> None:
    global u3
    u3 = 3
    t31 = threading.Thread(target=f31)
    t31.start()

def f4() -> None:
    global s4, s6
    t = s4       # RACE: s4 also written by main
    s4 = 4
    t = s6       # RACE: s6 also written by f6
    s6 = 4

def f51() -> None:
    global s5
    t = s5       # RACE: s5 also written by f5
    s5 = 51

def f5() -> None:
    global s5
    t51 = threading.Thread(target=f51)
    t51.start()
    s5 = 5       # RACE: s5 also read/written by f51

def f6() -> None:
    global s6
    t = s6       # RACE: s6 also written by f4
    s6 = 6

def main() -> None:
    global u1, u2, u3, s4
    u1 = 1
    t = u1
    u2 = 1
    u3 = 1

    t1 = threading.Thread(target=f1)
    t1.start()

    u2 = 1
    t = u2

    t3 = threading.Thread(target=f3)
    t3.start()

    s4 = -1
    t4 = threading.Thread(target=f4)
    t4.start()
    s4 = 1       # RACE: s4 also read/written by f4

    t5 = threading.Thread(target=f5)
    t5.start()
    t6 = threading.Thread(target=f6)
    t6.start()
```

**PyCSL-annotated version (intentionally buggy — no protection):**

```python
#@ shared s4
#@ shared s5
#@ shared s6
# No protected_by → PyCSL ConcurrencyChecker flags all three as unprotected

#@ thread_entry
def f4() -> None:
    global s4, s6
    t = s4       #! ConcurrencyChecker: WARNING — read of shared s4 outside critical section
    s4 = 4       #! ConcurrencyChecker: WARNING — write of shared s4 outside critical section
    t = s6       #! ConcurrencyChecker: WARNING — read of shared s6 outside critical section
    s6 = 4       #! ConcurrencyChecker: WARNING — write of shared s6 outside critical section

#@ thread_entry
def f6() -> None:
    global s6
    t = s6       #! ConcurrencyChecker: WARNING — read of shared s6 outside critical section
    s6 = 6       #! ConcurrencyChecker: WARNING — write of shared s6 outside critical section
```

**PyCSL-annotated version (fixed with mutexes):**

```python
import threading

lock_s4 = threading.Lock()
lock_s56 = threading.Lock()

s4 = 0
s5 = 0
s6 = 0

#@ shared s4 protected_by lock_s4
#@ shared s5 protected_by lock_s56
#@ shared s6 protected_by lock_s56
#@ mutex_invariant lock_s4: true
#@ mutex_invariant lock_s56: true

#@ thread_entry
def f4() -> None:
    global s4, s6
    #@ critical lock_s4
    with lock_s4:
        t = s4
        s4 = 4
    #@ critical lock_s56
    with lock_s56:
        t = s6
        s6 = 4

#@ thread_entry
def f6() -> None:
    global s6
    #@ critical lock_s56
    with lock_s56:
        t = s6
        s6 = 6
```

**Expected outcome:** The unfixed version produces `PyCSLSemanticError` for
every unprotected shared access. The fixed version passes proof — trivially,
since the mutex invariants are `true`. This example is primarily a test of
**race detection**, not proof strength.

**What Mthread found (C version):**
- `s4`: race — read by `f4`, write by `main`, all unprotected
- `s5`: race — read by `f51`, write by `f5`, all unprotected
- `s6`: race — read/write by `f4` and `f6`, all unprotected
- `u1`, `u2`, `u3`: no races (sequential access patterns)

---

### A.3 — Dining Philosophers: Complex Locking and Message Passing

**Original C pattern** (`philo.c`): Five philosopher threads, each
acquiring two adjacent forks (mutexes). Threads may send messages on a
shared queue. Mthread detects a **race condition on `end2`** — read by
`main` without any lock, written by worker threads under various lock
combinations.

**Python translation:**

```python
import threading
import queue
import random as rng

N = 5
end2 = 0
locks: list = [threading.Lock() for _ in range(N)]
msg_queue: queue.Queue = queue.Queue(maxsize=5)

def aux(left: int, right: int, msg: int) -> None:
    global end2
    with locks[left]:
        with locks[right]:
            if rng.random() > 0.5 and msg != 2:
                end2 = 1
                msg_queue.put(msg)

def philosopher(p: int) -> None:
    left = p - 1 if p > 0 else N - 1
    right = p + 1 if p < N - 1 else 0
    while True:
        aux(left, right, p + 1)

def main() -> None:
    threads = []
    for i in range(N):
        t = threading.Thread(target=philosopher, args=(i,))
        t.start()
        threads.append(t)

    end_flag = 0
    while not (end_flag != 0 and end2 != 0):   # RACE: reading end2 without lock
        try:
            end_flag = msg_queue.get(timeout=1)
        except queue.Empty:
            pass
```

**PyCSL-annotated version (showing the race):**

```python
#@ shared end2
# No protected_by: deliberately unprotected to demonstrate race detection
# Mthread output: "end2: read by <main> at line N, unprotected;
#                   write by philosopher[0] at line M, protected by locks[1] locks[4]"

#@ thread_entry
def philosopher(p: int) -> None:
    #@ requires 0 <= p and p < N
    left = p - 1 if p > 0 else N - 1
    right = p + 1 if p < N - 1 else 0
    while True:
        aux(left, right, p + 1)

def aux(left: int, right: int, msg: int) -> None:
    #@ requires 0 <= left and left < N
    #@ requires 0 <= right and right < N
    global end2
    #@ acquires locks[left]
    with locks[left]:
        #@ acquires locks[right]
        with locks[right]:
            if msg != 2:
                end2 = 1              # Protected by locks[left] AND locks[right]
                msg_queue.put(msg)
```

**PyCSL-annotated version (fixed — add a dedicated lock for end2):**

```python
lock_end2 = threading.Lock()

#@ shared end2 protected_by lock_end2
#@ mutex_invariant lock_end2: end2 == 0 or end2 == 1

def aux(left: int, right: int, msg: int) -> None:
    #@ requires 0 <= left and left < N
    #@ requires 0 <= right and right < N
    global end2
    #@ acquires locks[left]
    with locks[left]:
        #@ acquires locks[right]
        with locks[right]:
            if msg != 2:
                #@ critical lock_end2
                with lock_end2:
                    end2 = 1
                    #@ ensures end2 == 1
                msg_queue.put(msg)

def main() -> None:
    # ...
    end_flag = 0
    while True:
        #@ critical lock_end2
        with lock_end2:
            done = end2 != 0
        if done:
            break
        try:
            end_flag = msg_queue.get(timeout=1)
        except queue.Empty:
            pass
```

**Expected outcome:** The unfixed version triggers a `ConcurrencyChecker`
warning on the `end2` read in `main`. The fixed version passes — the mutex
invariant `end2 == 0 or end2 == 1` is trivially maintained.

**What Mthread found (C version):**
- `end2`: race — read by `<main>` unprotected, written by `jobs[0]`
  protected by `locks[1] locks[4]`, by `jobs[2]` protected by
  `locks[1] locks[3]`, etc. No single consistent mutex protects `end2`.
- No other races (fork mutexes are correctly used).
- 4 iterations to reach fixed point.

**Additional lessons from this example:**
- **Nested locking** (`locks[left]` then `locks[right]`): Phase 1
  initially rejects this, but the philosophers example motivates adding
  `#@ lock_order` annotations in a future phase.
- **Message passing**: the `msg_queue` is thread-safe by construction
  (Python's `queue.Queue`). PyCSL should recognize `queue.Queue` as a
  trusted concurrent primitive — no annotation needed.
- **Inconsistent protection**: `end2` is written under different lock
  combinations by different threads. This is not "protected by a mutex"
  in the Strategy 3 sense — it requires either a dedicated lock (as in
  the fix) or Rely/Guarantee reasoning (future work).

---

### A.4 — Summary: What Each Example Exercises

| Example | Concurrency Pattern | Strategy 3 Outcome | Key Feature Tested |
|---------|--------------------|--------------------|-------------------|
| Matrix | Fine-grained partitioned locking | ✅ Fully provable | Parameterized mutex invariants, array partitioning |
| Shared Variables | No synchronization (races) | ⚠️ Race detection | ConcurrencyChecker warnings, unprotected `#@ shared` |
| Philosophers | Nested locking + inconsistent protection | ⚠️ Partial — needs dedicated lock for `end2` | Nested `#@ acquires`, `#@ lock_order` motivation |

---

## Implementation Order

| Step | Module | Effort | Dependencies |
|------|--------|--------|-------------|
| 1 | Grammar + CSLNode classes (Module2) | 1 day | None |
| 2 | Weaver attachment (Module3) | 1 day | Step 1 |
| 3 | Semantic validation (Module4) | 2 days | Step 2 |
| 4 | ConcurrencyChecker static pass | 2 days | Step 2 |
| 5 | IR emission (Module5) | 1 day | Step 3 |
| 6 | WhyML transpilation (Module6) | 3 days | Step 5 |
| 7 | Memory model `concurrent` | 1 day | Step 6 |
| 8 | Reference tests | 2 days | Step 6 |
| 9 | Skill + agent updates | 2 days | Step 8 |
| 10 | Integration tests + coordinator | 1 day | Step 9 |

**Total estimate: ~16 days**

---

## Limitations and Future Work

- **Phase 1 scope:** only mutex-based synchronization. No lock-free
  algorithms, no condition variables, no barriers.
- **No automatic inference:** shared declarations and mutex invariants
  must be provided by the user (or the LLM agent). A future Mthread-like
  abstract interpretation pass could infer them.
- **No hierarchical locking:** nested mutex acquisition is rejected
  initially. A lock-ordering annotation (`#@ lock_order lock_a < lock_b`)
  could be added later.
- **Rely/Guarantee:** unprotected shared state is flagged but not verified.
  A future phase could add `#@ rely` / `#@ guarantee` annotations for
  lock-free code, requiring the user to supply interference specs.
- **Threading model:** assumes `threading.Thread` or equivalent. No
  support for `asyncio`, `multiprocessing`, or actor models initially.
