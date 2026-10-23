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

## THE DIAGNOSIS ABOVE WAS INCOMPLETE — THE REAL CAUSE IS THE STRING REPRESENTATION

Widening the `val`'s bound to `[0, 0x110000)` was tried FIRST and **DID NOT FIX IT**, which
is what exposed the real mechanism. The emitted body is:

```whyml
  val ord_op (c: string) : int
    ensures { result = Char.code (Char.get c 0) }
  ...
    (ord_op "\xe2\x82\xac")
```

**THE LITERAL `"€"` IS EMITTED AS ITS UTF-8 BYTES** — a THREE-byte string — and Why3's
`Char.code` is 0..255 by that theory's own axioms. So `result < 256` follows from the SECOND
`ensures` no matter what the first one says. `ord` is reading the first BYTE (`0xe2` = 226).

**AND THE MODEL IS INTERNALLY INCONSISTENT ABOUT IT.** Measured:

  * `len("€") == 1` — **PROVES.** That is CPython's answer, folded from the Python literal.
  * `ord("€") == 226` (the first byte) — does NOT prove.
  * `ord("€") < 256` — **PROVES.** CPython answers 8364.

So `len` uses Python's code-point semantics while `ord` uses the byte string. One operation
is right, the other is wrong, on the same literal in the same function.

## THE REPAIR — AND THE GAP THE FIRST VERSION LEFT

REFUSE `ord` over a non-ASCII string. Widening the bound cannot work (`Char.code` re-derives
it), and refusing the LITERAL outright would lose `len`, which is already correct.

**THE FIRST VERSION REFUSED ONLY `ord(<non-ASCII literal>)` AND WAS DEFEATED BY ONE
BINDING** — both `s = "€"; ord(s)` and `s = "€"; ord(s[0])` still proved. That is the FIFTH
time this generation a guard keyed on a syntactic LOCATION has been stepped around (#59's
carrier 7, #60's loop, #61's names, #62's call boundary, #63's local). The landed guard is
keyed on the BINDING: it collects locals bound to non-ASCII literals in the `\trusted`
pre-pass and refuses `ord` of any of them, however spelled.

## STATUS: **CLOSED**

All 32 planes green; mirror 53/53 type-clean and byte-inert; both corpora byte-inert; metric
unchanged at 459. Witnesses `1166` (direct), `1167` (one binding away) — both
anti-vacuity-verified in each direction — and `1168` (positive control: ASCII `ord` keeps its
TRUE bound; note `ord("a") == 97` is NOT derivable because Why3 does not compute `Char.code`
of a literal, so the control claims the bound).

## THE OLD "REPAIR SHAPE" NOTE, KEPT BECAUSE IT WAS WRONG AND THAT IS INSTRUCTIVE

Change the bound to the true one, `0 <= result < 1114112`, in BOTH `ord_op` and
`char_code_at`. **This will NOT be byte-inert** — the preamble changes for every unit that
uses `ord` — so the cost must be measured rather than assumed, and any driver that was
leaning on `< 256` has to be found and inspected rather than re-baselined. If some driver
genuinely needs a byte bound, the honest way to get it is from the BYTES path, which really
does guarantee it, not from `ord`.
