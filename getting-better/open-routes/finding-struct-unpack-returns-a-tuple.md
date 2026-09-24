# FINDING (#49, gen #31) — `struct.unpack` returns a TUPLE, and two proof-cited corpus drivers certify `\result == x`

```python
#@ requires 0 <= x and x <= 65535
#@ assigns \nothing
#@ ensures \result == x
#@ proof rocq Pycsl.Struct.Std.round_trip_u16
#@ proof lean Pycsl.Struct.Std.round_trip_u16
def roundtrip_u16(x: int) -> int:
    packed = struct.pack('>H', x)
    return struct.unpack('>H', packed)
```

    [+] Verification SUCCESS! All contracts formally proven.

CPython:

    >>> struct.unpack('>H', struct.pack('>H', 7))
    (7,)
    >>> _ == 7
    False

`struct.unpack` **returns a tuple even when it contains exactly one item** — the shim's own
docstring in `src/pycsl_lib/strct/__init__.py` quotes that sentence from the RST and then
models the call as returning the unpacked SCALAR. The corpus driver's postcondition is true
of the model and false of the program.

FIVE FUNCTIONS, TWO FILES, BOTH `# pycsl-expected: PASS`:

    test-suite/corpus/pycsl-reference/0753.py   roundtrip_u16, roundtrip_u32
    test-suite/corpus/pycsl-reference/0778.py   roundtrip_i16, roundtrip_i32, roundtrip_i64

## What discharges it, measured rather than assumed

Deleting the `#@ proof` lines from 0753 makes it **FAIL**. So the false postcondition is
discharged by the CITED EXTERNAL PROOF, not by the emitter's own reasoning, and the trust
surface is the `#@ proof` opt-in rather than ordinary verification. That is why this is
filed as a FINDING and not as a SEV-1 route: annotations.md is explicit that `#@ proof
rocq|lean` means *proved elsewhere, audited*.

**It is still a defect in a CHECKED surface.** The registered axiom is

    Pycsl.Struct.Std.round_trip_u16 :
      forall fmt x0 : int. 0 <= x0 < 65536 ->
        struct_unpack_fu16 fmt (struct_pack_fu16 fmt x0) = x0

which is a true theorem about a big-endian byte codec returning an INT, cross-validated in
Rocq and Lean (the registry comment records `coqc` exit 0, no `Admitted`/`Axiom`; Lean 4.31
with `#print axioms` ⊆ the three standard ones). The theorem is not wrong. **The
ATTRIBUTION is**: the Python function it is attached to returns `(x,)`, and nothing in the
3-way cross-check compares the Rocq result TYPE with the Python return type.

## How it was found, and why nothing had found it before

`bin/check-corpus-contract-truth-args.py` exists to catch exactly this — its header calls a
failure "a route witness hiding inside a green test". It has a skip list:

```python
# CSL tokens this oracle cannot evaluate as Python. A contract carrying one is skipped
# whole — an oracle that guesses at `\forall` reports its own bugs as corpus defects.
SKIP_TOKENS = ("\\forall", "\\exists", "\\old", "\\at", "\\length", "\\separated",
               "\\valid", "\\sum", "\\is_sorted", "\\permutation", "\\array_eq",
               "==>", "\\result[", "\\nothing", "\\let")
```

and the filter is `any(t in " ".join(ann) for t in SKIP_TOKENS)` over the WHOLE annotation
block. **`\nothing` can only ever appear in `#@ assigns \nothing`** — a clause this oracle
never evaluates, since it reads only `requires` and `ensures`. So one token in a list whose
stated purpose is "tokens this oracle cannot evaluate" silently excluded every function that
declares an empty frame, which is most pure functions in the corpus:

    with `\nothing` in the list    416 functions, 4367 evaluations, 0 disagree
    with it removed                518 functions, 5573 evaluations, **44 disagree**

+96 functions, +1076 evaluations, and five real ones among them. The oracle was right; its
own population rule hid the answer.

## The sixth disagreement is the ORACLE's bug, not the corpus's

`multi_file_lib/r119_rebindlib.py::inc` reports a disagreement because the module ends with

    inc = dec

so `ns["inc"]` is `dec` and the oracle calls a different function from the one whose
contract it read. That is route #119's own witness library, and the oracle should skip a
function whose name is REBOUND at module level rather than report it — the fix is a
correctness fix, not an exclusion.

## Status

The skip-list repair, the rebinding fix and the method extension are one increment; the five
struct disagreements need a named, reasoned baseline set pointing at this file, the way
`TRUST_INHERITED_BASELINE` already works in the same plane. Measured 2026-09-24.

## The OTHER instrument that should have seen it, and why it did not

`bin/check-stdlib-contract-fidelity.py` exists to catch exactly a shim whose contract is
"perfectly proven of its own body and FALSE OF THE FUNCTION IT CITES" — its own words. It
maps `strct` to `struct` (line 88), so the package is in scope. It does not report
`unpack`, for two independent reasons and both are population boundaries rather than
judgements:

  1. **`\length` is in its SKIP_TOKENS**, and the shim's contract is
     `#@ requires \length(buffer) >= fmt`. A contract carrying one skipped token is skipped
     whole. (`\length(x)` is `len(x)` and IS evaluable — `check-class-invariant-establishment`
     translates exactly that — so this entry is a candidate for the same narrowing the args
     oracle just received.)
  2. **The shim's PARAMETER MODEL is not the stdlib's.** It declares
     `def unpack(fmt: int, buffer: list) -> int` where CPython's is
     `unpack(format: str, buffer: bytes) -> tuple`. Calling the real function with the
     shim's int `fmt` raises, so even with the token skip removed the oracle has nothing to
     compare — the divergence is in the SIGNATURE, one level above the contract.

So the shape is: one plane could not read the clause, the other could not call the function,
and the third (`check-corpus-contract-truth-args`) could do both and was excluding the whole
function over a token that appears only in a clause it never reads. Three instruments, three
different population boundaries, one defect sitting in the intersection.

THE CHEAPEST NEXT STEP, recorded not taken: narrow `check-stdlib-contract-fidelity`'s
SKIP_TOKENS the same way (apply it to what is evaluated, and translate `\length` to `len`),
and then decide separately what to do about shims whose SIGNATURE does not match the
function they cite — that is a different and larger question, and `unpack` is not the only
one that models a format string as an int.

## A SIXTH INSTANCE the oracle cannot see, found by grepping for the shape

`0779.py::roundtrip_s4` is the same defect one type over:

```python
#@ requires \length(d) == 4
#@ ensures \result == d
#@ proof rocq Pycsl.Struct.Std.round_trip_s4
def roundtrip_s4(d: bytes) -> bytes:
    packed = struct.pack('>4s', d)
    return struct.unpack('>4s', packed)
```

    >>> struct.unpack('>4s', struct.pack('>4s', b'abcd'))
    (b'abcd',)          # a tuple; `== b'abcd'` is False

`# pycsl-expected: PASS` (no marker), same `#@ proof` discharge. The args oracle does not
report it because its parameter is `bytes` and its return is `bytes` — outside the int/bool
population, and outside the `\length` skip as well.

So the family is **SIX functions across THREE files** — 0753 (2), 0778 (3), 0779 (1) — and
`KNOWN_DIVERGENT` names only the five the oracle can actually reach, deliberately: putting
0779 in a set that is asserted EXACTLY would make the plane demand a report it can never
produce. The sixth is recorded here instead, which is the honest place for a defect that no
instrument currently measures.

ELEVEN corpus files use `struct.unpack`; the other five either do not return its result or
are `# pycsl-expected: FAIL`.

## How far the shim shape goes — censused

Scanning every `src/pycsl_lib` shim whose DOCSTRING mentions a tuple while its return
annotation does not:

    8 hits, and only ONE is this shape:
      strct/__init__.py  unpack  -> int   "…The result is a tuple even if it contains
                                           exactly one item."
    the others are honest:
      htmlm  getpos_line / getpos_col -> int   deliberately DECOMPOSE the tuple, and say so
      json   dump/dumps/py_scanstring/raw_decode/JSONEncoder.__init__ -> None  (stubs)

But the docstring scan under-counts the shim family itself: `strct` has THREE entry points
that model CPython's tuple-returning unpack as a scalar —

    def unpack(fmt: int, buffer: list) -> int          "Returns number of values unpacked."
    def unpack_from(fmt: int, buffer: list, offset: int) -> int
    def Struct.unpack(self, buffer: list) -> int

and only the first quotes the RST sentence that contradicts it. So the defect is one
MODEL used three times, not three independent mistakes — which matters for the repair:
changing the model changes all three, and the corpus drivers that lean on it are the six
listed above.

Checked and NOT in this shape: `divmod`, which also returns a tuple in CPython —
`return divmod(7, 2)` under `#@ ensures \result == 3` FAILS (fail-closed), so the builtin
path does not share the shim's erasure.
