Files in this directory have been used to define the semantics of Why3. They come from Cohen & Johnson-Freyd (POPL 2024) and associated git repository https://github.com/joscoh/why3-semantics.

- `formula_rep` (`proofs/core/Denotational.v`) — the denotational semantics for
  Why3 formulas.  This is the definition of what a Why3 `ensures`/`requires`
  formula *means*: `formula_rep γ pd pf vt vv f = Bool`.  This corresponds in PYCSL to `evalC es preEs result e = True/False`.


- `valid_task` (`proofs/core/Logic.v`) — `satisfies pd pdf pf pf_full f` — what
  it means for a Why3 formula to be valid. `satisfies/valid` from `Logic.v` is the formal definition of what Why3 means when it says "Valid" — and closed_satisfies_rep is the theorem that collapses that definition, for PyCSL's closed integer VCs, to a simple boolean evaluation, making Sub-lemma β a finite case analysis rather than a universal quantifier problem.

- `src/proofs/Gen/Relations.v` — the bridge between the stateful OCaml API
  model and the stateless semantics.  Useful as an architectural pattern for
  connecting our `.mlw` emission to formal semantics.

