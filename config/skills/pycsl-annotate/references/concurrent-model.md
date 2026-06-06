# Concurrent model (mutex-discipline verification)

Load when working with `--memory-model concurrent` and Python's
`threading` module.

Use `--memory-model concurrent` (or `pycsl-flags: --memory-model concurrent`) for files that use Python's `threading` module. This model reduces concurrency to sequential WP proofs using the monitor-invariant pattern.

**Module-level declarations** (place at the top of the file, before any `import` or `def`):

```python
#@ shared <var> protected_by <mutex>   # var is protected by the named mutex
#@ shared <var>                        # var is shared but unprotected (warning)
#@ mutex_invariant <mutex>: <expr>     # invariant that must hold while mutex is free
#@ lock_order <mutex1>, <mutex2>, ...  # total order for nested locking (deadlock prevention)
```

**Function-level annotations:**

```python
#@ thread_entry      # marks the function as a thread entry point
#@ acquires <mutex>  # function acquires mutex (for with-lock-as patterns)
#@ releases <mutex>  # function releases mutex
```

**Statement-level annotations** (place immediately before a `with` statement):

```python
#@ critical <mutex>  # declare this with-block is a critical section for <mutex>
```

**How verification works:**

1. At critical section entry: the verifier havoces all shared variables protected by `<mutex>` and `assume { mutex_inv }`.
2. Inside the section: verify the body sequentially.
3. At critical section exit: `assert { mutex_inv }` (must still hold after modification).

**Rules:**
- Shared variable writes MUST be inside a `#@ critical` (or `#@ acquires`/`#@ releases`) block — otherwise Module4 raises a semantic error.
- Nested locking REQUIRES `#@ lock_order` at module level.
- `queue.Queue`, `threading.Lock`, `threading.RLock` etc. are trusted thread-safe and need no `#@ shared` annotation.

**Minimal example:**

```python
#@ shared counter protected_by lock_counter
#@ mutex_invariant lock_counter: counter >= 0
import threading
lock_counter = threading.Lock()
counter = 0

#@ thread_entry
#@ \diverges
def worker() -> int:
    #@ critical lock_counter
    with lock_counter:
        counter += 1
    return 0
```
