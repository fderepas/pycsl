# Route #205 — an over-claiming `#@ interface` was refused at home and believed everywhere else

**Status:** CLOSED (gen #30). SEV-1.

## The witness

Owner (`1709_route205_interface_lie_escapes_to_importers.py`, expected FAIL):

```python
#@ assigns \nothing
#@ ensures \result == 3
#@ interface ensures \result == 7
def three() -> int:
    return 3
```

Importer:

```python
from lie import three

#@ ensures \result == 7
def ask() -> int:
    return three()
```

The owner FAILS on its own — its narrowing goal `\result == 3 -> \result == 7` is false,
exactly as designed. The importer **PROVED `\result == 7`**, with and without `--deep`.
CPython answers 3.

The emitted importer unit says it plainly:

```whyml
val three () : int
  ensures  { (result = 7) }     (* the interface, and NO narrowing goal *)
```

## Where it came from

The same docstring as route #204, one sentence later: *"Emitted only in the owning unit
(where the function is a real `let`, so the definition is established by the body)."* Read
as a claim, that sentence says the check does not run **where the interface is believed**.
A modularity feature whose lie is rejected at home and accepted abroad is the worst
possible direction for the error.

## The repair

Emit the same narrowing goals in the `emit_as_val` path, at the early return that sat
BEFORE the existing `if _iface:` call. The goal needs no body: it proves the interface
follows from the **definition contract**, which the owning unit separately proves of its
body. So an importer that never compiles the owner still cannot believe an unsupported
interface.

## Controls

`1710_route205_interface_honest_narrowing_control.py` (expected PASS): `ensures \result ==
3` with `interface ensures \result >= 0` still proves, and so does an IMPORTER of it.
Corpus `0660` still proves. Mirror-sync green at 887 verbatim functions.
