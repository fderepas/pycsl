# Route #217 (CLOSED) — an item store into a `bytes(...)`-bound local PROVED, while CPython raises

**Found and closed:** 2026-09-23, gen #30, while pricing the handoff's "DO THIS FIRST NEXT
WINDOW" item.

## The exploit

```python
#@ ensures \result == 9
def f() -> int:
    b = bytes([1, 2, 3])
    b[0] = 9
    return b[0]
```

At the parent commit: **`[+] Verification SUCCESS! All contracts formally proven.`**

CPython: `TypeError: 'bytes' object does not support item assignment`. The model was
proving a postcondition about a program that cannot run — the same shape as route #215.

## Why it proved

`PYCSL-SEM-SUBSCRIPT` already carries the right refusal and the right message:

> Subscript assignment to immutable 'bytes' variable 'b' — a Python `bytes` object does
> not support item assignment (TypeError). Use a `bytearray` for a mutable byte buffer.

It keys on the SYMBOL TABLE typing the local `"bytes"`, and
`Module5_IREmitter._build_function_symbol_table` typed every plain `x = <expr>` local as
`"Any"` with ONE exception: a bare bytes LITERAL (`b = b"abc"`). A `bytes(...)` CONSTRUCTOR
stayed `"Any"`, so the guard never saw the local it was written for.

**This is lesson (t3) again, in the other direction.** The guard's population is "locals
the symbol table calls `bytes`", and the constructor form never entered it.

## What was and was not already known

Witness `1725_gen30_bytes_count_form_excluded.py` pins the COUNT form `b = bytes(2)` and
its docstring names this exact gap as "pre-existing and separate". It fails today because
the emission is ILL-TYPED, which its own docstring flags as an accident doing the
enforcing.

**The ITERABLE form `bytes([...])` had no witness at all** — and it is the form that
actually occurs: eight of the nine corpus sites the handoff enumerated.

## The repair, and its measured cost

One branch in `_build_function_symbol_table`: a local bound from a `bytes(...)` call is
typed `"bytes"`. Its mirror twin is `\trusted`, so **no mirror edit and no re-proof** — the
choke-point rule. Mirror sync re-measured after landing: 887 verbatim, unmoved.

**Whole-corpus byte-diff, both sides emitted fresh:**

    1303 baseline .mlw / 1302 candidate
    0 MOVED · 0 APPEARED · exactly 1 GONE

and the one GONE is `1725_gen30_bytes_count_form_excluded`, which is
`# pycsl-expected: FAIL` either way and now fails **by the refusal** instead of by the
ill-typedness. That is the improvement its docstring asks for, not a regression.

`src/pycsl_lib/os/UnixInodeFileSystem.py` — the only `pycsl_lib` site — emits
byte-identically. The mirror and the live tree contain ZERO such locals (the two greps that
look like hits are comments about this very bug).

**A guess in the handoff was checked and is WRONG, which is why it was checked:** typing
the ITERABLE form was expected to possibly make reads MORE faithful (`b[0] == 65` provable
from `_py_expr_constant`'s real byte values). Every one of the five surviving corpus
emissions is byte-identical, so it does not.

## Witnesses

* `1809_route217_bytes_constructor_local_item_store.py` — expected FAIL (the exploit).
* `1810_route217_ctl_bytearray_item_store_still_verifies.py` — expected PASS: `bytearray`
  is MUTABLE and the identical program over it must still verify, or the repair would be
  indistinguishable from a ban on byte buffers.
* The read-only form `b = bytes([65, 66, 67]); return b[0]` still verifies (checked by
  hand).
* `1725` keeps its FAIL and gains a real refusal.

## Still owed

The handoff's follow-on stands: with the refusal in place, the `bytes` COUNT form can take
the `Array.make n 0` lowering `bytearray` already has, because the type error is no longer
the only thing holding the line. That is a separate, byte-diff-RISKY change and is NOT done
here.
