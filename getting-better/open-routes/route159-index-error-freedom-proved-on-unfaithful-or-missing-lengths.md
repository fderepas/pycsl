# ROUTE #159 — `no_exception IndexError` proved for index operations whose length is unfaithful or unchecked

**Status: CLOSED AND FULLY GATED by gen #29 (2026-09-16), battery H (with #158/#160). Witness 1546 (erased dict-literal KeyError) added during drafting.** Severity 1.
Generator: hand (following #158's placeholder into the bounds VC).

## Measured at `e27e6797` — each PROVED `no_exception IndexError`, CPython raises IndexError

| shape | emitted | why |
|---|---|---|
| `xs = []; xs[0]` | `assert { in_bounds ((Array.length xs)) (0) }` | placeholder length 1024 |
| `xs = []; xs[0] = 5` | same, on the store | placeholder length 1024 |
| `[][0]` | `(subscript_get 0 0)` | erased read, no obligation |
| `xs.append(1); xs[3]` | `(Seq.get !xs 3)` | `Seq.get` is total, no obligation |
| `"abc"[5]` | `(str_sub_op !s 5 1)` | substring, no obligation |
| `(1, 2)[5]` | `(subscript_get pycsl_erased_t 5)` | erased read, no obligation |

## Repair

`_handle_subscript` (trusted in the mirror): a seq read bounds against `Seq.length`, a string read
against `String.length`, an erased read against `0` (unprovable), and an array read against `0`
when the receiver is the placeholder literal or a local known to be empty. The STORE handler cannot
see the size (the store withdraws the fold), so `pycsl.py::_run_pipeline` strengthens
`in_bounds ((Array.length X))` to `in_bounds (0)` inside a `let X = (Array.make 1024 0) in` scope with
no `X_len` sidecar and no rebinding. Only functions declaring `no_exception IndexError` carry these
asserts. Witnesses 1538-1543 (XFAIL), 1544/1545 (PASS controls).

**Battery H (every leg predicted and hit):** emission measured BEFORE predicting (stated) — vs the
#155-#157-closed tree 1180 -> 1196, 0 MOVED / 0 GONE / 0 APPEARED, python-reference and mirrors
inert; conformance 38/38 + 38/38; suite 3679/3697 same 18, zero XPASS; planes --slow 34/34.
