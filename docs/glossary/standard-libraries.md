**Standard libraries**, in PyCSL, are modeled — never executed. PyCSL proves a
program against curated **contract stubs** that describe what each standard-
library API is *modeled* to do, not against the real implementation. The stub's
contract is the source of truth for proof generation.

PyCSL's Python models live in `src/pycsl_lib/` (the formally-verified standard
library; the resolver also searches a `Lib/` layout). When Module 1 (the
ingestor) sees `from os.path import join`, it parses the model — not CPython — and
proves against the `#@` contracts on it.

The contracts a consumer trusts here are not merely asserted: each model's bodies
are themselves **body-verified within `src/pycsl_lib/`** (e.g. the `os` model
carries zero bare `\trusted`), so the import-boundary "stub" a program relies on
is backed by the library's own machine-checked proofs.

---

## Why standard libraries matter in PyCSL

A program that calls `os.path.join`, `len`, or `str.split` cannot be verified
without a model of those calls. PyCSL never runs them; it trusts a contract.
That makes each stub an explicit trust boundary — an inaccurate stub is a silent
soundness hole, exactly like a [load-bearing](load-bearing.md) file. The
[extreme rigor](extreme-rigor.md) bar therefore applies: body-verify the stub's
behavior where possible, axiom-anchor what you cannot, and track every remaining
`\trusted` stub as a named gap.

An "API entry" worth a stub is any of: a module function (`os.path.join`), a
builtin (`len`, `range`), a method (`str.split`, `list.append`), a class
(`re.Pattern`), an instantiation (`dict()`), or a module attribute (`sys.argv`).

---

## Concrete examples

The same discipline generalizes across languages — each entry is a contract
stub *modelling* the API, not its source:

### Python (the implemented case)

```python
#@ requires len(path) >= 0
#@ ensures len(\result) >= len(path)
#@ raises { TypeError }
def join(path: str, *paths: str) -> str: ...
```

Real stubs live in `src/pycsl_lib/` (`os.path.join`, `str.split`, `struct.pack`,
the `itertools`/`multiprocessing` modules, …).

### Go

`strings.Split(s, sep) []string`, `os.Open(name) (*File, error)` — modeled by a
contract over lengths and the error sentinel, with the `error` return as an
explicit success/failure discriminant (Go has no exceptions).

### C

`<string.h>` `strlen` (`requires` a NUL-terminated buffer; `ensures \result` =
index of the first NUL), `memcpy(dst, src, n)` (`requires \valid(dst, n)` and
`\separated`), `<stdio.h>` `fopen` (returns a handle or NULL). The contract
carries the memory-safety preconditions C leaves implicit.

### C++

`std::vector<T>::push_back` (`ensures size()` grows by one), `std::string::substr`
(`requires pos <= size()`). Stubs model the STL container contracts (size,
bounds, iterator validity) rather than the template implementation.

---

## Related terms

- [trusted stub](trusted-stub.md)
- [extreme rigor](extreme-rigor.md)
- [load-bearing](load-bearing.md)
- [trust seam](trust-seam.md)

> **In short:** standard libraries are *modeled by contract*, never executed —
> each stub is a trust boundary held to the same rigor as first-party code.
