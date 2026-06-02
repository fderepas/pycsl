"""IR canonicalization (pycsl-bridge-plan §3.2).

The canonicalizer maps any IR node to a unique representative of its
equivalence class under stylistic differences between Rocq and Lean
spec sources. Operates per pycsl-bridge-plan §3.2:

  1. Alpha-normalize bound variables (v0, v1, ...).
  2. AC-flatten and sort and/or/+/* operand lists by structural hash.
  3. Apply a small confluent rewrite set:
       a + 0 → a,  0 + a → a,  a * 1 → a,  1 * a → a
       not (not a) → a
       a == a → True
  4. Rewrite `Divides` to a canonical operational form so that
     existential-vs-operational style choices don't cause spurious
     disagreements.

Confluence is not formally proven; it's checked empirically against
the test corpus.
"""

from .normalize import canonicalize, structural_hash

__all__ = ["canonicalize", "structural_hash"]
