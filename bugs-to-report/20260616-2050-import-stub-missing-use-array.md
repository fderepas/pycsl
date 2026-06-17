# Imported return-code-only stub fails to emit `use array.Array` → `unbound type symbol 'array'`

STATUS: CONFIRMED

## Summary

When a formal test imports a `pure_lib.os` stub whose public contract is
RETURN-CODE-ONLY but whose helper-predicate closure references `array int`
(e.g. `chmod`, `truncate`), and NO other imported stub carries an explicitly
`array`-typed parameter or `ensures`, the emitted WhyML omits the
`use array.Array` clause while still emitting `array`-typed declarations
(`val function slot_inode (disk: array int) ...`). Why3 then rejects the module
at L3-tc with `unbound type symbol 'array'`.

## Minimal repro

```python
# /tmp/c1.py
from pure_lib.os import chmod
#@ requires True
#@ ensures \result == 1
def c(d: str, m: int) -> int:
    rc = chmod(d, m)
    if rc == 0 or rc == -1:
        return 1
    return 0
```

```
PYTHONHASHSEED=0 PYTHONPATH=src/pycsl .venv/bin/python -m pycsl /tmp/c1.py --no-proof
```

Output:
```
[level] L1 ✓  L2 ✓  L3-tc ✗
[!] Emitted WhyML does NOT type-check (L3-tc failed) — NOT a success:
File "/tmp/c1.mlw", line 9, characters 33-38:
unbound type symbol 'array'
```

`/tmp/c1.mlw` line 9 is `val function slot_inode (disk: array int) (blk: int) (k: int) : int`,
and the preamble (`use int.Int`, `use ref.Ref`, `use string.String`) is MISSING
`use array.Array`.

## Why it is intermittent (and the workaround that proves it is the trigger)

The clause IS emitted when the import set contains a stub with an explicit
array-referencing `ensures`. `mkdir`/`access` carry
`dir_lookup(_filesystem.dir, 5, name) ...` ensures (an array term), which
triggers `use array.Array`. Co-importing and CALLING them fixes it:

```python
from pure_lib.os import mkdir, chmod, access, F_OK   # mkdir/access trigger `use array.Array`
```
→ `[+] Verification SUCCESS! All contracts formally proven.`

So the `use array.Array` emission is gated on an array term appearing in an
imported contract's `ensures`/param, but NOT on array terms that enter only
through the transitively-pulled-in helper `val`/`predicate` declarations
(`slot_inode`, `inode_bytes_valid`, the empty-disk axiom). The helper closure
should also drive the `use`.

## Impact

- Broke `pure_lib_test/formal_os_meta.py` (chmod/truncate imported with a
  str-keyed observer but no array-trigger) until a `mkdir`+`access` co-import
  was added.
- Surfaces whenever someone writes a formal test for a return-code-only
  filesystem stub in isolation. The workaround (co-import an array-trigger op)
  is non-obvious and easy to mistake for a stale-typing error.

## Suggested fix

When collecting the preamble `use` set for the emitted module, scan the
transitive helper-declaration closure (the `val function`/`predicate`/`axiom`
declarations actually emitted), not only the imported contracts' `ensures`/param
types, for `array` occurrences — and emit `use array.Array` if any appears.

## Repro environment

- Found while authoring os filesystem formal tests (test-supervise-sl mission).
- `PYTHONHASHSEED=0`, hoare memory model.
