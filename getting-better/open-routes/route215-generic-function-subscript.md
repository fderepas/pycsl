# Route #215 — `f[T](...)` on a generic FUNCTION is not Python, and the model proved it

**CLOSED** by a refusal at `pycsl.py::_run_pipeline` (`PYCSL-SEM-GENERIC-SUBSCRIPT-CALL`).
Witness `1796_gen30_witness_generic_function_subscript_call.py`, control
`1797_gen30_route215_control_plain_generic_call.py`.

## How it was found — the advice audit, not a hunt for routes

`bin/check-refusal-advice-audited.py` audits a refusal's ADVICE by writing the program the
message tells you to write. Auditing `monomorphize.py`'s GT4 line — *"The recursive call
must use a concrete type"* — produced a file that would not verify. Three controls said
where the problem was:

| file | verdict |
|---|---|
| generic CLASS `Box[T]`, instantiated `Box[int]` | VERIFIES |
| NON-generic `def depth(n)` with `#@ \variant n` | VERIFIES |
| generic FUNCTION `def ident[T](n)`, called `ident[int](3)` | FAILS |

The emission explained it: the call lowered to **`(any int)`**.

## The route

```python
#@ requires n >= 0
#@ ensures \result == n
def ident[T](n: int) -> int:
    return n

#@ ensures \result == 0            # FALSE, and it PROVED
def probe() -> int:
    a = ident[int](1)
    x = a
    a = ident[int](2)
    return x - a
```

emitted

```whyml
let probe () : int
  ensures { (result = 0) }
=
  let x = ref 0 in
  let a = ref 0 in
  a := (any int);
  x := pycsl_erased_a;
  a := (any int);
  (!x - pycsl_erased_a)
```

The per-NAME erased constant (route #41's device) is **not refreshed on REBINDING**, so the
two calls collapse to one value and `x - a` is provably 0.

## The ground truth is sharper than the obvious reading

`ident[int](1)` is **not valid Python**. PEP 695 makes a generic CLASS subscriptable
(`Box[int]()` RUNS, via `__class_getitem__`) but a generic FUNCTION is not — CPython 3.14
answers `TypeError: 'function' object is not subscriptable`. So the model was not computing
a different number from CPython; it was **proving a postcondition about a program that
cannot run at all**.

I nearly recorded "CPython answers -1". Running the carrier is what caught it — that is the
difference between a route record and a guess, and it cost one command.

* The TRUE twin (`\result == 0 - 1`, what the runnable spelling computes) is REFUSED.
* The PLAIN call `ident(1)` IS valid Python and IS lowered faithfully (`a := (ident 1)`),
  and the false claim FAILS there. That is control 1797.

## The refusal, and the two placement mistakes

Blast radius measured across all four populations BEFORE landing it (lesson (d3)):
`f[T](...)` on a locally-defined function occurs **2 times in the corpus** (both inside
witness 1783) and **ZERO times** in the mirror, the live tree and `src/pycsl_lib`. The
refusal sits at `_run_pipeline`, whose mirror twin is `#@ \trusted` — no marker, no mirror
edit, no re-proof (the choke-point rule).

1. **Wrong AST family.** The first scan imported the stdlib `ast`; the pipeline parses with
   `frontend.pure_ast`, so it matched nothing. That is route #209 exactly — a matcher asked
   about nodes of the wrong family — and the carrier caught it, not the diff.
2. **Wrong order: it RETIRED another refusal.** Landed before Module 5 it fired before the
   TY3 checks, and GT4 keys on a recursive call whose type ARGUMENT is the generic's own
   TypeVar — only the subscripted spelling can express that. Refusing the spelling first
   made GT4 permanently unreachable. Witness 1783 stopped witnessing GT4, which is how it
   was caught. It now runs after `_ir_resolve`, so GT1/GT3/GT4/BOUND fire first and only a
   call that SURVIVED them is refused. Banked as wall-lesson (n3).

## What is still open here

The underlying erasure defect — **a per-NAME opaque constant that is not refreshed when the
name is REBOUND** — is only closed for THIS trigger. Route #41's device is used for erased
generator/set/tuple locals and route #44's for `None`-bound locals, and the same collapse
shape exists there; those cases were not shown to produce a false PROOF because the values
are not ints and CPython raises on the arithmetic. Priced: keying the constant per
(name, binding) would move the emission of 6 corpus files, 20 mirror functions, 157 live
functions and 6 `pycsl_lib` functions — measured, and the reason this route was closed at
the trigger rather than at the device.
