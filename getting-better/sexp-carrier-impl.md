# sexp-carrier-impl.md — the tuple/sexp value carrier (backlog item-3 reopening cap, count-moving)

Unblocks the `proof2why3/from_sexp.py` cluster (`_const_name`, `_ind_short_name`, `_binder_name` +
their recursive `_find_kername_components`-style helpers) — Python heterogeneous NESTED TUPLES
(sertop s-expressions), which NO existing carrier reaches (pyval's `PArr` is a homogeneous list, not
a positional heterogeneous sexp; lesson-p census confirmed). NECESSARY (unlike R3, which was
redundant with the pre-existing pydict).

## §GATE-S — BOTH make-or-break spikes PASS (oracles in getting-better/sexp-carrier-oracles/)
- **Value model** (`sexp.mlw`): `sexp = SAtom string | SList slist` (recursive), a `last_atom`
  recursive walk (the `_find_kername_components` shape), and total positional `snth` (the `t[i]`
  shape). Positive `pos` Valid (extracts "ker"), evil twin Timeout (non-vacuous), `nth1` Valid,
  axioms 0. z3.
- **Certificate** (`SexpCert.v`): the soundness core — `ssize`/`lsize` measures, `ssize_pos`/
  `lsize_nonneg` well-foundedness, `tail_lt` fold-termination witness, `satom_inj`/`atom_neq_list`
  observability. `coqc` clean; `Print Assumptions` = "Closed under the global context" (AXIOM-FREE)
  for all three load-bearing theorems. Ledger stays 3.

**Disposition: BUILD authorized (spike-proven, axiom-free).** Provability is NOT the wall; the
remaining risk is EMITTER RECOGNITION — can the recognizer lower `isinstance(t,tuple)` → `is_slist`,
`t[i]` → `snth`, and the recursive `_find_kername_components` walk → a `last_atom`-style fold over
the sexp ADT? That is the build's make-or-break falsifier (refutation exit if it walls).

## Build sequence (each its own gate battery; ledger 3; count STRICTLY DOWN per conversion)
1. Certificate: port `SexpCert.v` into a real `Phase2*_Sexp.v` + a `Sexp.lean` (both provers,
   `Print Assumptions`/`#print axioms` clean); wire into `_CoqProject`. Do NOT commit `.vo`/`.olean`.
2. Emitter: sexp theory in `preamble.py` (the `sexp`/`slist` ADT + `snth`/`last_atom`/`is_slist`/
   `atom_of` projectors), gated on a corpus-absent sentinel (byte-inert).
3. Recognizer: lower the from_sexp tuple-walk shape (isinstance-tuple dispatch + positional index +
   recursive helper walk) onto the sexp ADT. Convert the from_sexp cluster (the 3 + helpers) that
   the recognizer reaches; count DOWN.
Refutation exit: if the emitter cannot lower the tuple-walk onto the ADT → CERTIFIED-BOUNDARY,
record the exact recognizer blocker, revert clean, fall through to the next backlog item.
