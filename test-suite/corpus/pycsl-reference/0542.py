"""Test 0542 — an INDUCTIVE property over a RECURSIVE datatype, via an imported
lemma (A4 generalization demo, no-more-int-7 §B).

The framing-lemma demonstrations so far (0537–0539) proved a *flat* structural
property (list permutation). This driver tests whether the `axiom_from`-for-
framing mechanism **generalizes to inductive/compositional properties over a
recursive datatype** — the question rq.md flagged as the one most worth knowing.

`Json = JNull | JInt(int) | JPair(Json, Json)` is a recursive datatype (A5a).
`json_mirror` swaps the two children of every `JPair`; mirroring twice is the
identity — `mirror(mirror(x)) == x` — an INVOLUTION proved BY STRUCTURAL
INDUCTION over the recursive structure (not derivable by SMT). The imported lemma
`mirror_involution : forall x. json_mirror (json_mirror x) = x` — proved once in
Rocq and Lean by induction on `Json`, cross-validated, cited via `#@ proof` —
discharges the postcondition.

This is the same bridge shape as 0539 (reversal) but over an *inductive* property
rather than a flat one, confirming the mechanism scales. (A full json round-trip
`loads(dumps(x)) == x` is the same shape with a harder, Narcissus-grade verified-
parsing proof — a documented follow-on, not this demo.)

Fails without the axiom (uninterpreted `json_mirror` — the involution is not
first-order derivable); flips to PASS once `#@ proof` imports `mirror_involution`.
"""
#@ datatype Json = JNull | JInt(int) | JPair(Json, Json)
_ = 0  # anchor


#@ proof rocq Pycsl.Reference.Json.mirror_involution
#@ proof lean Pycsl.Reference.Json.mirror_involution
#@ ensures \result == x
#@ assigns \nothing
def mirror_twice(x: Json) -> Json:
    return json_mirror(json_mirror(x))
