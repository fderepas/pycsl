# The canonical example: Euclidean GCD across three artifacts

This is PyCSL test 0342, the worked example that demonstrates the *CSL
philosophy in concrete form. When in doubt about a design choice, ask
"does it make 0342 read more or less coherently?"

The example consists of three files in three languages, connected by
qualified names and `proof` directives.

## File 1 — the Python source (PyCSL annotations)

```python
"""Test 0342 — PyCSL Euclidean GCD (cross-validated Rocq + Lean axioms)."""

#@ proof rocq Pycsl.Reference.Gcd.gcd_result_nonneg
#@ proof rocq Pycsl.Reference.Gcd.gcd_result_positive
#@ proof rocq Pycsl.Reference.Gcd.gcd_divides_a
#@ proof rocq Pycsl.Reference.Gcd.gcd_divides_b
#@ proof rocq Pycsl.Reference.Gcd.gcd_0
#@ proof rocq Pycsl.Reference.Gcd.gcd_step
#@ proof rocq Pycsl.Reference.Gcd.gcd_greatest
#@ proof lean Pycsl.Reference.Gcd.gcd_result_nonneg
# ... (paired Lean directives for each)
#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= 0
#@ ensures (a > 0 or b > 0) ==> \result > 0
#@ ensures (a > 0 or b > 0) ==> a % \result == 0
#@ ensures (a > 0 or b > 0) ==> b % \result == 0
#@ ensures \result == gcd(a, b)
#@ ensures (a > 0 or b > 0) ==>
           (\forall k; (k > 0 and a % k == 0 and b % k == 0) ==> k <= \result)
#@ assigns \nothing
def gcd(a: int, b: int) -> int:
    x = a
    y = b
    #@ loop invariant x >= 0
    #@ loop invariant y >= 0
    #@ loop invariant gcd(x, y) == gcd(a, b)
    #@ loop invariant (a > 0 or b > 0) ==> (x > 0 or y > 0)
    #@ loop variant y
    while y != 0:
        r = x % y
        x = y
        y = r
    return x
```

## File 2 — the Rocq proof (`0342.proofs/rocq/gcd.v`)

```coq
Require Import Coq.Init.Nat.
Require Import Coq.Arith.PeanoNat.
Require Import Lia.

Module Pycsl.
Module Reference.
Module Gcd.

Theorem gcd_result_nonneg : forall a b : nat, Nat.gcd a b >= 0.
Proof. intros. lia. Qed.

Theorem gcd_result_positive : forall a b : nat,
  a > 0 \/ b > 0 -> Nat.gcd a b > 0.
Proof.
  intros a b H.
  destruct (Nat.gcd a b) eqn:Hg.
  - apply Nat.gcd_eq_0 in Hg. lia.
  - lia.
Qed.

(* ... gcd_divides_a, gcd_divides_b, gcd_0, gcd_step, gcd_greatest ... *)

End Gcd.
End Reference.
End Pycsl.
```

## File 3 — the Lean proof (`0342.proofs/lean/Gcd.lean`)

Mirrors the Rocq file with the same qualified names under
`namespace Pycsl.Reference.Gcd`, proving the same statements with
mathlib's `Nat.gcd`.

## What this example demonstrates

**Shared qualified names.** `Pycsl.Reference.Gcd.gcd_step` is the
actual identifier in Rocq (via nested `Module` declarations), the
actual identifier in Lean (via `namespace`), and the address cited
from Python. The same string works as a name in all three systems.
No translation table.

**Three audiences read the same file.**

- A Python programmer reads the `def` and the loop and understands
  Euclidean GCD.
- A verification engineer reads the contracts, sees the loop invariant
  `gcd(x, y) == gcd(a, b)`, and recognizes the textbook Hoare-logic
  proof of GCD correctness.
- A formal methods researcher reads the `proof` directives and
  knows there are real kernel-checked proofs in `0342.proofs/`.

**The contracts state the algebra cleanly.** Read top-to-bottom: "we
will use these GCD facts (proof cluster), here is what we promise
(requires/ensures), here is the invariant that makes the loop work,
here is why it terminates." Nothing is ceremonial.

**The Rocq file is a normal Rocq file.** No tool-specific tactics, no
embedded DSL, no PyCSL plugin. Uses stdlib `Nat.gcd` and `lia`. Ends
each proof with `Qed`. The only sign it serves a larger system is a
brief comment noting which WhyML axiom each theorem corresponds to.

**The `proof` cluster is a proof outline, not a checklist.** The
seven theorems form a coherent algebraic theory of GCD: identity at
zero (`gcd_0`), Euclidean step (`gcd_step`), divisibility
(`gcd_divides_a/b`), positivity (`gcd_result_*`), and maximality
(`gcd_greatest`). Why3's stdlib `number.Gcd` defines GCD via the same
axioms — your proofs and Why3's stdlib are the same theory expressed
two ways.

**The line `ensures \result == gcd(a, b)` shows the symbol overload.**
In contract context, `gcd(a, b)` is the mathematical function imported
via `proof`. In executable context, `gcd` is the Python function
being defined. Same name, two distinct objects, distinguished by
context. The contract asserts that the Python implementation computes
the same value as the mathematical specification — the deepest kind of
bridge.

## How to use this example

When designing a new feature, write what 0342 would look like with
that feature included. If the file still reads coherently to all three
audiences, the feature is probably aligned with the philosophy. If the
file starts to feel like it's serving the tool rather than the reader,
reconsider.

## A second example — the extreme-rigor bar

0342 (GCD) is the *minimal* example — one function, seven theorems,
two languages. The *extreme-rigor* example is
`unix-filesystem/UnixInodeFileSystem.py` (666 lines, a Unix-like
inode filesystem). It demonstrates what stdlib-grade annotation looks
like: Coq-anchored bitwise lemmas (the
`#@ proof rocq UnixFs.Bitmap.bit_and_one_in_zero_one` pattern that
turns a 3.4B-step Z3 timeout into a zero-step axiom dispatch),
round-trip axioms for `struct.pack`/`unpack`, loop invariants and
variants on every loop, and each `\trusted reviewer:` paired with a
named feature-plan gap.

When the question is "is THIS philosophical instinct already named?",
read 0342. When the question is "what bar does the stdlib pass have
to clear?", read UnixInodeFileSystem.py. The full case study lives
in
[`csl-from-scratch/references/stdlib-extreme-rigor.md`](../../csl-from-scratch/references/stdlib-extreme-rigor.md).
