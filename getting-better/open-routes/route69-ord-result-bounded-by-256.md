# OPEN ROUTE #69 — `ord()` IS AXIOMATISED AS RETURNING A BYTE, AND IT DOES NOT
# (found 2026-09-11 by relaunch #55, at `8b8f690c`)

## THE HEADLINE — NO `no_exception`, NO EXCEPTION, NO OPT-IN OF ANY KIND

```python
#@ ensures \result < 256
#@ assigns \nothing
def f() -> int:
    return ord("€")        # CPython: 8364
```

**`[+] Verification SUCCESS! All contracts formally proven.`**
The TRUE claim (`\result == 8364`) does **not** prove.

**THIS IS MORE SERIOUS THAN ROUTES #64-#68.** Every one of those required the user to opt in
to `#@ no_exception`. This one does not. It is a FALSE POSTCONDITION proved about an
ordinary, TOTAL Python expression — `ord` of a perfectly valid one-character string — and it
is available to every proof in any unit that mentions `ord`.

## THE CAUSE — A FALSE AXIOM IN THE PREAMBLE

`module6_whyml/expressions.py`:

```whyml
  val ord_op (c: string) : int
    ensures { 0 <= result < 256 }
    ensures { result = Char.code (Char.get c 0) }
```

and the sibling used for `ord(s[i])`:

```whyml
  val char_code_at (s: string) (i: int) : int
    ensures { 0 <= result < 256 }
    ensures { result = Char.code (Char.get s i) }
```

**`ord` RETURNS A UNICODE CODE POINT, NOT A BYTE.** Its range is `[0, 0x110000)`, not
`[0, 256)`. `ord("€")` is 8364, `ord("あ")` is 12354. The `< 256` bound is not a conservative
approximation — it is FALSE, and an `ensures` on an abstract `val` is an AXIOM, so anything
downstream may use it. A proof can conclude `ord(c) < 256` for a character where Python
says otherwise, and from a false hypothesis the rest follows.

## HOW IT SURVIVED

The bound is right for the operation the model was probably thinking of — a BYTE read,
`bytes[i]`, which really is in `[0, 256)`. `ord` was given the byte's contract. Every corpus
driver that exercises `ord` appears to use ASCII, where the claim happens to hold, so nothing
ever contradicted it.

## FOUND BY AUDITING THE ABSTRACT-`val` SURFACE, WHICH IS THE REAL LESSON

Routes #66 and #67 each noticed, in passing, that a `val` carried `ensures` clauses
UNCONDITIONAL in an argument Python constrains, and the handoff promoted "audit every
abstract `val`" to a named follow-up. Doing that audit found this — and this one is not even
a partiality defect: **the bound is false on a TOTAL input.** An abstract `val`'s `ensures`
is the single most dangerous line in this compiler, because it is an axiom the solver may
use anywhere, with no corresponding obligation on anyone.

## THE REPAIR SHAPE

Change the bound to the true one, `0 <= result < 1114112`, in BOTH `ord_op` and
`char_code_at`. **This will NOT be byte-inert** — the preamble changes for every unit that
uses `ord` — so the cost must be measured rather than assumed, and any driver that was
leaning on `< 256` has to be found and inspected rather than re-baselined. If some driver
genuinely needs a byte bound, the honest way to get it is from the BYTES path, which really
does guarantee it, not from `ord`.
