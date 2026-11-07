# The FIELD value model already landed — what is left is three one-line rules

Generation #31, 2026-09-25T21:20Z. Written forty minutes after
`finding-the-whole-conversion-frontier-measured.md`, which sized the largest of the four
walls like this:

| wall | witnesses | what retires it |
|---|---|---|
| the **FIELD value model** (`str` and `list` as record fields) | ~174 | a faithful string/list field carrier |

**The faithful string field carrier is already built.** It was measured, not argued:

    $ grep 'type pycslerror' errors.mlw
    type pycslerror = { mutable pycslerror_filename: string; mutable pycslerror_line: int;
                        mutable pycslerror_stage: string; mutable pycslerror_code: string }

Two separate repairs put it there. `preamble.py`'s `elif ftype in ("string", "str")` (07-2333-rev2
TP-3, Gap 6) makes a `str`-ANNOTATED field a Why3 `string`, ungated; and `eca4b0c8`, landed
EARLIER IN THIS SESSION, gives an UN-annotated `self.f = <annotated __init__ param>` the type the
parameter declares. Between them, `errors.py`'s three string fields are strings.

So the marker comment on `PyCSLError.__str__` — the one the frontier note quoted as naming the
capability —

> the string-typed self fields (`filename`, `stage`) are carried as ints in the record model

**is stale.** They are not. The comment described the emitter of the day it was written, and the
emitter moved underneath it. That is lesson (d4) yet again, in the cheapest possible direction:
a REASON recorded on a marker is a measurement with a timestamp, and re-measuring it costs one
emit.

## What actually blocked the conversion: three rules, each measured necessary

Emitting `__str__` with its marker deleted produces `string`-vs-`int` at three DIFFERENT places,
and no two of them are the same defect:

**(A) A string-typed record field has no TRUTHINESS rule.** `if self.stage:` lowered to the int
coercion `self.pycslerror_stage <> 0`. `_to_bool` in `expressions.py` already owns the
ARRAY-field case one line above (`Array.length (…) <> 0`, "the record-field counterpart of the
array-VAR truthiness rule"); the STRING-field counterpart of the string-VAR rule sixty lines up
was simply never written.

**(B) `<x>.__str__()` is not classified as a string expression.** It LOWERS correctly —
`val str_dunder_op () : string` — but `_is_string_expr` never says so, so `msg =
super().__str__()` gets the integer `ref 0` pre-declaration and `msg := (str_dunder_op ())`
mistypes. The lowering and the classifier disagreed about a value they both describe.

**(C) The string-local fixpoint runs BEFORE the classifier that feeds it.** In
`statements.py`, `_collect_string_valued_locals` (the "#31 fixpoint generalisation": a local
whose EVERY assignment RHS is string-typed is a string local) runs at the top of the block;
`_mark_string_seq_locals` — which is what makes `parts` a `seq string` and hence makes
`" ".join(parts)` a string — runs FIFTY LINES LATER. So `header = " ".join(parts)` was
evaluated against a symbol table that did not yet know what `parts` was, and the answer was
"not a string". This is wall-lesson (k6) in a new dress: two passes over one population, one of
them looking at a table the other has not filled in yet.

## The ablation: all three are load-bearing

Four trees, one witness, `--no-proof` (L3-tc is the question):

| patch | L3-tc |
|---|---|
| A only | ✗ `string` vs `int` |
| A + B | ✗ |
| A + C | ✗ |
| B + C | ✗ |
| **A + B + C** | **✓** |

and with all three, `errors.py` PROVES — `[+] Verification SUCCESS! All contracts formally
proven.` The emitted body is faithful, not a facade:

    if (str_length_op (self.pycslerror_stage) <> 0) then begin
      parts := Seq.snoc !parts (str_concat_op (str_concat_op "[" self.pycslerror_stage) "]")
    end;
    …
    let header = ref (str_join_seq " " !parts) in
    let msg = ref (str_dunder_op ()) in
    (if (str_length_op !header <> 0) then (str_concat_op (str_concat_op !header ": ") !msg) else !msg)

## Blast radius, measured before landing

All 53 mirror `.mlw` files, emitted from PRISTINE mirror sources under the patched emitter, are
**byte-identical** to the unpatched emission. The patch changes nothing that is emitted today; it
only decides what happens the first time a marker comes off. Corpus byte-inertness is the gate's
job and is measured there, not predicted here.

## What this does to the frontier number

The "~174 FIELD value model" bucket was a bucket of SYMPTOMS (`string` where `int` was wanted and
the reverse), attributed to a single cause by inspection. One witness taken apart says the cause
is not one capability but a SPRAY of small rules, each of which knows about strings in one
context and not another — a truthiness here, a classifier there, a pass ordering. The honest
restatement is: **the value model is built; what is missing is its closure.** The number of
witnesses that number retires is unknown until the screen is re-run, and it will be re-run.
