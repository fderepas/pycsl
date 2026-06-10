STATUS: OPEN

# Convergence gap — iteration 5 (no `ord`/`chr` char↔int bridge; generic call mis-types `string` args as `int`)

**Loop:** `config/skills/pycsl-stdlib-coverage` — Phase 0, leaf L1 of `stronger-than-os.md`:
the directory-entry NAME codec round-trip (`decode(encode(name)) == name`), the smallest leaf
that makes every name-keyed namespace consequence (mkdir → access-present) provable.
**Iteration:** N = 5.

## Summary

The string-domain name codec PROVES today — that is done (see "What landed" below). The
gap is the BYTE side: the on-disk dirent name field is 30 *bytes*, and writing the faithful
byte codec (`b[i] = ord(name[i])` to encode, rebuild the string from the bytes to decode)
hits **Gap 5 — there is no `str`↔`bytes`/char↔int bridge in the emitter**. Concretely the
emitter cannot give a meaning to `ord(c)` / `chr(b)` for a single character, so the on-disk
bytes cannot be related to the filename string, and `_dir_lookup`'s `name == pathname` can
only round-trip in the STRING view, not against the actual on-disk bytes.

## Minimal reproducer

`pure_lib_test/probe_c.py`:
```python
#@ requires \str_length(name) >= 1
#@ assigns \nothing
#@ ensures 0 <= \result and \result <= 255
def probe_c_ord_char(name: str) -> int:
    return ord(name[0])
```
Run: `.venv/bin/python3 src/pycsl/pycsl.py pure_lib_test/probe_c.py`

## Why3 / emitter symptom

Emission fails to type-check (the VC is never even reached):
```
File "...probe_c.mlw", line 19, characters 11-32:
This expression has type string, but is expected to have type int
```
The emitted WhyML (probe_c.mlw, verbatim):
```
val ord_1 (x0: int) : int
val str_sub_op (s: string) (lo len: int) : string
  ensures { result = (String.substring s lo len) }
let function probe_c_ord_char (name: string) : int =
  (ord_1 (str_sub_op name 0 1))      (* str_sub_op : string, fed to int-param ord_1 *)
```

## Root cause (file:line)

Two cooperating facts in `src/pycsl/module6_whyml/expressions.py`:

1. **No `ord`/`chr` handler.** `ord` is not a recognized builtin (`_call_named_builtins`
   handles `len`/`min`/`max`/`sorted`/`isinstance`/… but not `ord`/`chr`). So it falls
   through to the generic unannotated-callee path at **expressions.py:1073-1092**, which
   declares `val ord_1 (x0: int) : int` — i.e. it ASSUMES every argument is `int`:
   ```python
   coerced_args = [self._coerce_to_int(a) for a in args]            # line 1079
   ...
   self._add_abstract_op(f"val {arity_fn} {' '.join(f'(x{i}: int)' for i in range(n))} : int")  # 1086
   ```
2. **`_coerce_to_int` does not coerce a `string` expression.** `name[0]` lowers to
   `(str_sub_op name 0 1)` (a `string`; `s[i]` → `String.substring`, expressions.py:1625-1637).
   `_coerce_to_int` (**expressions.py:150-182**) only hashes *string literals* and *tuple
   literals* and zero-fills *array/map* shapes; a non-literal `string`-typed expression
   falls through unchanged (`return whyml_str`, line 182). So the `string` flows as the
   `int`-typed argument of `ord_1` → the type error above.

The same wall blocks `chr(b)` (an `int → string` char op) and the `name.encode(...)` byte
buffer (modeled as a length-1 opaque array — `_pad_name` docstring,
`pure_lib/os/UnixInodeFileSystem.py`).

## Proposed fix (tool side)

Add a faithful char↔int bridge so a single character round-trips through a byte:

1. In `_call_named_builtins` (or a dedicated handler), recognize `ord(x)` and `chr(x)`:
   - `ord(c)` where `c : string` (a 1-char string) → an abstract
     `val ord_op (c: string) : int  ensures { 0 <= result <= 1114111 }`
     (or `<= 255` when the caller constrains it), typed `string → int`.
   - `chr(n)` where `n : int` → `val chr_op (n: int) : string
     ensures { String.length result = 1 }`, typed `int → string`.
   - Pin the round-trip with a cross-validated axiom (Rocq/Lean,
     per the SMT-escape order in csl-philosophy): `ord_op (chr_op n) = n` for
     `0 <= n <= 255`, and `chr_op (ord_op c) = c` for `String.length c = 1`. This is the
     `UnixFs.*` analogue for the char codec — an irreducible fact, so a cited lemma, never a
     bare `\trusted`.
2. Defensive: in `_coerce_to_int`, a `string`-typed non-literal expression passed where
   `int` is expected should route through `ord_op` (or be rejected loudly) rather than
   silently emitting an ill-typed operand — so the generic path can never again produce
   `int`-param-applied-to-`string`.

With `ord_op`/`chr_op` + the round-trip axiom, the byte-level name codec
(`b[i] = ord(name[i])`, rebuild via `chr`) becomes emittable and its round-trip provable,
and `_dir_lookup` can resolve names against the ACTUAL on-disk bytes — completing L1's byte
side and unblocking the Gap-4a name-keyed consequence tests
(`10-2204-convergence-gap-4.md` §4a).

## What landed this iteration (the strongest provable in-place form)

The **string-domain name codec is implemented and PROVEN, in place**, in
`pure_lib/os/UnixInodeFileSystem.py`:
- `_encode_name(name) -> str`  (`requires \str_length(name) <= 30; ensures \result == name`)
- `_decode_name(stored) -> str`  (`ensures \result == stored`)
- `_name_codec_roundtrip(name) -> str`  (`ensures \result == name`) — the round-trip leaf,
  the string twin of the proven inode-field codec round-trip.

Standalone proof (`pure_lib_test/probe_namecodec_leaf.py`): all VCs **Valid**
(Alt-Ergo, ≤ 554 steps), zero `\trusted`, zero proof axioms. The byte-shape `_pad_name`
(length-only) is kept unchanged for the on-disk layout; the gap above is the ONLY thing
between this string-view round-trip and a faithful on-disk byte round-trip.

## Probes (kept under pure_lib_test/)

- `probe_a.py` — string identity round-trip: PROVES.
- `probe_b.py` — two-call string round-trip `decode(encode(s)) == s`: PROVES.
- `probe_c.py` — `ord(name[0])`: the Gap-5 wall (type error, does not emit).
- `probe_namecodec_leaf.py` — the landed leaf, standalone: PROVES.
