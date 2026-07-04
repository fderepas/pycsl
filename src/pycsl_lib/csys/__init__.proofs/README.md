# __init__.proofs/ — cross-validated proofs for `../__init__.py` (csys / colorsys)

De-trusts `rgb_to_hsv` (non-lin-int-div-fixed.md S5). The two nonlinear
integer-division bounds SMT (Alt-Ergo/Z3) times out on are stated as WhyML
axioms in `src/pycsl/module6_whyml/preamble.py::_AXIOM_REGISTRY`
(`Pycsl.Csys.Colorsys.{sat_bound,hue_bound}`), cited by `#@ proof rocq|lean`
directives above the leaf helpers `_hsv_saturation` / `_hue_offset`, and
anchored by the Rocq + Lean theorems here.

- `sat_bound`: `0 ≤ d ≤ m, m > 0 ⟹ (d*1000)/m ≤ 1000` (HSV saturation ≤ 1000).
- `hue_bound`: `d > 0, |n| ≤ d ⟹ -167 ≤ (n*1000)/(6*d) ≤ 167` (hue offset range).

Division is Euclidean (Coq `Z.div`, Lean `Int./`), matching Why3
`int.EuclideanDivision` for the positive divisors used here.

## Re-check externally
```bash
cd rocq && coqc Colorsys.v          # Coq 8.20.1 — exits 0, no Admitted/Axiom
cd lean && lean Colorsys.lean       # Lean 4.31 core (no Mathlib) — exits 0, no sorry
```

## Audit
`pycsl --audit-proof ../__init__.py` — verifies each `#@ proof` qualname resolves
to a theorem inside the matching `Pycsl.Csys.Colorsys` namespace, no admits.
The library then verifies under full proof (default non-vacuity gate) with
`rgb_to_hsv` body-proven (`\trusted` count 4 → 3).
