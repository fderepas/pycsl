A **formal test** is a test written with **abstract (symbolic) values** instead of concrete
literals, so that its verification covers **all possible inputs** satisfying the preconditions —
not just one sample.

---

## Why formal tests matter in PyCSL

A conventional unit test picks concrete values (`filename = "testfile"`, `content = [72, 101, …]`)
and checks one execution path. A formal test replaces those with universally quantified parameters
constrained by `#@ requires` clauses. When PyCSL proves the formal test's postcondition, the
result holds for **every** filename up to 80 characters and **every** content buffer up to 10 000
bytes — an exhaustive guarantee no finite test suite can provide.

The relationship between a concrete test and its formal counterpart:

| Aspect | Concrete test (`0001.py`) | Formal test |
|--------|--------------------------|-------------|
| Inputs | `"testfile"`, `[72, 101, …]` | `filename: str`, `content: str` with `#@ requires` |
| Coverage | One execution | All inputs satisfying preconditions |
| Assertions | `assert n == 24` | `#@ ensures \result == 0 or \result == 1` |
| Verdict | Runtime pass/fail | Prover Valid/Unknown/Timeout |
| Bugs found | Only on chosen values | On any value, including edge cases |

A formal test is the **demand-driver** for correctness of an entire API surface: if the prover
discharges it, the API is proven correct for all inputs in the precondition's domain.

---

## Structure of a formal test

```python
#@ requires \str_length(filename) <= 80
#@ requires \str_length(content) <= 10000
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def formal_test_0001(filename: str, content: str):
    fd = open(filename, O_CREAT | O_WRONLY)
    ...
```

1. **Preconditions** (`#@ requires`): bound the symbolic inputs to a meaningful domain.
2. **Body**: the same sequence of API calls as the concrete test, but on the symbolic parameters.
3. **Postcondition** (`#@ ensures`): the property that must hold for every input in the domain.
4. **No concrete literals for data under test**: filenames, buffer contents, sizes are all
   parameters — the prover explores every admissible value.

Control-flow assertions inside the body (`assert fd >= 3`) become verification conditions: if the
prover cannot discharge one, it has found a symbolic input that violates the assertion — a real
bug, not a flaky test.

---

## From concrete test to formal test

The recipe is mechanical:

1. **Parameterize**: replace every concrete input with a function parameter.
2. **Constrain**: add `#@ requires` to bound each parameter to the domain the API supports
   (e.g., filename length ≤ 80, buffer length ≤ 5 120).
3. **Generalize assertions**: replace `assert n == 24` (specific to one input) with
   `assert n == len(content)` (universal).
4. **Add a postcondition**: state the overall property (`\result == 0` means the round-trip
   succeeded for *any* input in the domain).

---

## Concrete examples

### Concrete test (0001.py)

```python
TEST_STRING = "Hello, PyCSL filesystem!"
TEST_BYTES = [ord(c) for c in TEST_STRING]
fd = open("testfile", O_CREAT | O_WRONLY)
n = write(fd, TEST_BYTES)
assert n == len(TEST_BYTES)
```

Checks one 24-byte string written to one filename.

### Formal test (its formal counterpart)

```python
#@ requires \str_length(filename) <= 80
#@ requires \length(data) <= 5120
#@ ensures \result == 0 or \result == 1
def formal_test_0001(filename: str, data: list):
    fd = open(filename, O_CREAT | O_WRONLY)
    if fd < 3:
        return 1
    n = write(fd, data)
    if n != len(data):
        return 1
    close(fd)
    return 0
```

Proves that **every** file up to 80 chars and **every** buffer up to 5 120 bytes either
round-trips correctly or returns a well-defined error code.

---

## Related terms

- [reference test](reference-test.md) — a numbered concrete test in the corpus
- [demand-driver](demand-driver.md) — a program that justifies building a feature
- [verification condition](verification-condition.md) — the proof obligations generated from a formal test
- [loop invariant](loop-invariant.md) — needed when a formal test body contains loops

> **In short:** a formal test replaces concrete inputs with symbolic parameters and
> `#@ requires` constraints, so the prover verifies the test for all possible inputs at once —
> turning one test into a universal proof.
