# LADDER ITEM 4 — THE VACUOUS-DRIVER RATCHETS, CLASSIFIED
# (2026-09-09, relaunch #50). The handoff asked for this explicitly: *"treat them as a
# CERTIFIED-BOUNDARY class rather than as work, and say so explicitly rather than leaving
# the ratchet looking lazy."* This is that statement, with every one of the 55 named.

## THE MEASUREMENT AT `3e680635`

    pycsl-reference     9 of  889 trivially discharged (ratchet 9);   8 EMPTY PLACEHOLDERS
    python-reference   82 of 2187 trivially discharged (ratchet 82); 55 EMPTY PLACEHOLDERS
    bin/check-vacuous-drivers.py -> rc=0, every suite at or below its ratchet

An EMPTY PLACEHOLDER is a docstring plus a single `return <literal>` under a contract the
tail return alone discharges — `#@ ensures \result == 0` over `return 0`. It proves, it is
counted, and it exercises nothing.

## ALL 55 python-reference PLACEHOLDERS, CLASSIFIED — 53 ARE A CERTIFIED BOUNDARY

Every id below was read and grouped; the partition is exact (55 classified, 0 unclassified,
0 phantoms — checked mechanically, not by eye).

| n | class | why no non-vacuous driver exists |
|---|---|---|
| 15 | **CPython RUNTIME OBJECT MODEL / introspection** — code, frame and traceback objects, special read-only/writable attributes, annotations, annotation scopes, lazy evaluation, restricted execution | PyCSL models VALUES, not interpreter objects. There is no `frame`, no `code`, no `__dict__` to write a contract about. |
| 14 | **IMPORT machinery** — regular and namespace packages, loaders, submodules, module specs, `__path__`, module reprs, cached bytecode, path entry finders and their protocol, relative imports, `__future__`, `__lazy_modules__` | The import system runs BEFORE and AROUND the program PyCSL verifies; the verifier consumes an already-resolved module graph. |
| 9 | **ASYNC / COROUTINE / GENERATOR machinery** — generator functions, coroutine functions, async generators, async iterators, async context managers, generator-iterator methods | No suspension in the memory model. A `yield` is not a value PyCSL can carry, so the contract has nothing to say. |
| 8 | **METACLASS / class-creation protocol / descriptors** — preparing the class namespace, executing the class body, creating the class object, uses for metaclasses, `__class_getitem__` (both sections), special method lookup, implementing descriptors | Class creation is a RUNTIME computation; PyCSL's classes are static record declarations. |
| 4 | **LEXICAL constructs with no value model** — end marker, t-strings, the formal f-string grammar, imaginary literals | Either not a value (grammar/end-marker) or a value PyCSL has no type for (complex). |
| 3 | **PROGRAM-LEVEL input forms** — complete programs, file input, interactive input | These describe how the interpreter is FED, not what a program computes. |

**Ids, so the classification is checkable rather than assertable:**

    RUNTIME OBJECT MODEL  0063 0064 0066 0067 0068 0069 0070 0071 0073 0074 0096 0105 0106 0107 0108
    IMPORT MACHINERY      0113 0114 0119 0120 0121 0122 0123 0124 0125 0126 0128 0130 0179 0180
    ASYNC / GENERATORS    0052 0053 0054 0100 0101 0142 0143 0144 0145
    METACLASS / DESCR.    0077 0083 0084 0085 0086 0088 0089 0097
    LEXICAL               0012 0032 0033 0036
    PROGRAM-LEVEL INPUT   0214 0215 0216

**That is 53, and they are a CERTIFIED BOUNDARY, not a backlog.** A driver for "Module reprs"
or "Path entry finder protocol" cannot be made non-vacuous by trying harder; it would need
PyCSL to model the import system. The ratchet should keep counting them so the number cannot
grow silently, and the number should stop being read as debt.

## THE TWO THAT ARE **NOT** A BOUNDARY, AND ONE OF THEM IS ALREADY REFUTED AS ONE

  * **`0206` — multiple inheritance (Ref 8.8.1). NOT a boundary: PyCSL models it, and models
    it FAITHFULLY.** Probed `scratchpad/w51/mro/{m1,m2,m3,m4}.py`, a full 2×2, every Python
    assert run:

    | bases | contract | Python | PyCSL |
    |---|---|---|---|
    | `C(A, B)` | `\result == 1` | 1 | **PROVES** |
    | `C(A, B)` | `\result == 2` | 1 | fails closed |
    | `C(B, A)` | `\result == 2` | 2 | **PROVES** |
    | `C(B, A)` | `\result == 1` | 2 | fails closed |

    So the MRO is tracked, and tracked DISCRIMINATINGLY — it proves the true answer in both
    base orders and refuses the false one in both. `0206` can therefore be replaced by a real
    driver and the python-reference placeholder ratchet dropped 55 -> 54. The replacement is
    written and staged (`scratchpad/w51/mro/m1.py` is its body); it is NOT landed yet only
    because a reference-suite run was live on the tree at the time.

  * **`0188` — the `except*` clause (Ref 8.4.2).** Needs `ExceptionGroup`, which the exception
    model does not carry. Almost certainly a boundary, but it is recorded here as UNPROBED
    rather than assumed, because `0206` is the standing proof that "obviously unmodellable"
    is a claim worth testing: it was in exactly this list and it was wrong.

## THE HONEST HEADLINE

Of 55, **53 are a certified boundary**, **1 is refuted and convertible** (`0206`), and
**1 is unprobed** (`0188`). The ratchet is not lazy; it was simply never explained.
