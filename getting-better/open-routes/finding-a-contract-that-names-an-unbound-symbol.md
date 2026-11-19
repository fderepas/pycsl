# FINDING (gen #33, 2026-09-29) — AN ABSTRACT OP'S CONTRACT NAMES A SYMBOL THE PREAMBLE NEVER `use`s

**Four lines of entirely ordinary Python emit ill-typed WhyML. FAIL-CLOSED (L3-tc rejects it), and
NO corpus file tests the construct — which is why it survived.**

    #@ ensures True
    def f() -> int:
        s = "a" + "b"
        return len(s)

    File "cc1.mlw", line 9, characters 24-30:
    unbound function or predicate symbol 'concat'

## THE CAUSE, EXACTLY

The emitted preamble declares

    val str_concat_op (a: string) (b: string) : string
      ensures { result = (concat a b) }
      ensures { String.length result = String.length a + String.length b }

while that file's `use` list is only

    use int.Int
    use int.EuclideanDivision
    use ref.Ref

`concat` comes from Why3's `string.String`. **The DECLARATION and the `use` it needs are decided
independently**, so a path that emits the op without triggering whatever feature-detection adds
`use string.String` produces a contract naming an unbound symbol.

>>> **A DECLARATION'S CONTRACT IS PART OF ITS DEPENDENCIES. Here the op's TYPE needs nothing but
>>> `string`, and only its `ensures` needs `concat` — so a dependency computed from the op's
>>> SIGNATURE, or from a feature flag, misses it entirely.**

## THE CONTROL DISCRIMINATES, SO THIS IS A PATH AND NOT "STRINGS ARE BROKEN"

| program | verdict |
|---|---|
| `s = "a" + "b"` — two LITERALS (`finding-concat-unbound-witness.py`) | **L3-tc ✗, `unbound … 'concat'`** |
| `s = x + "b"` — a str PARAM and a literal (`finding-concat-unbound-control.py`) | **L3-tc ✓, verifies** — and it emits no `str_concat_op` at all |

And the 14 corpus emissions that DO carry `concat a b` all have `use string.String` on line 5. So the
`use` is emitted on some paths and not on this one.

## THE POPULATION IS EMPTY IN THE CORPUS, AND THAT IS THE POINT

Measured over both emitted trees from the gen #33 battery: **0 of 1379 pycsl-reference and 0 of 2199
python-reference** emissions carry `concat a b` without `use string.String`. So nothing is currently
broken — **the corpus simply has no test that concatenates two string literals in isolation.** A
four-line program of completely unremarkable Python is outside the corpus, and the gap is exactly
where the bug lives.

## HOW IT WAS FOUND, because the route matters more than the bug

Not by looking for it. It fell out of auditing my OWN deferred note: when I scoped route #64's
same-arity clash fix to declaration HEADS, I wrote into `abstract_ops.py` that a CONTRACT difference
under an equivalent head is "a deliberate choice, not an oversight" — and then never measured it.
Censusing that population turned up four contract-differing ops (`str_concat_op`, `str_eq_op`,
`str_split_op`, `str_sub_op`), and `str_concat_op`'s contract-bearing spelling is the one that names
`concat`.

**AND MY FIRST CENSUS SAID THE POPULATION WAS ZERO.** Its placeholder filter (`"%" in v or "{" in v`)
was applied to the WHOLE declaration text rather than to its head line — so it discarded every
declaration carrying an `ensures { … }`, which is precisely the population it existed to find. A
FALSE NEGATIVE, and worse than the four false positives this generation produced, because a zero
reads as an answer. **Apply a placeholder filter to the HEAD, never to the body.**

## REPAIR, SCOPED NOT BUILT

Tie the `use` to the DECLARATION: when an abstract op whose contract references `concat` (or
`String.length`, or any `string.String` symbol) is registered, require `use string.String` in the
same emission. Predicted byte-inert on both corpora, since 0 files are in the affected state, and it
turns a currently-ill-typed construct into a working one.

**It also owes a corpus test for `"a" + "b"` alone** — the absence of which is the reason this
survived, and adding it is worth more than the fix.
