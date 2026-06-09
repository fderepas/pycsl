# References

## Within this family

- [`config/skills/csl-philosophy/SKILL.md`](../../csl-philosophy/SKILL.md)
  — the family thesis this skill operationalizes.
- [`config/skills/pycsl-software-architecture/SKILL.md`](../../pycsl-software-architecture/SKILL.md)
  — concrete PyCSL architecture (cite as the worked example).
- [`config/skills/pycsl-how-to-develop/SKILL.md`](../../pycsl-how-to-develop/SKILL.md)
  — PyCSL-specific tactical guide.

## Formal semantics worked examples

- `src/formal-semantics-go/rocq/` — GoCSL Rocq formalization
  (Phase1–Phase8b). `gocsl_soundness` proved (Qed);
  `go_vcg_sound` proved (Qed). 6 Admitted across helper lemmas.
- `src/formal-semantics-go/lean/GoCSL/` — GoCSL Lean 4 mirror.
  All files compile with `lake build`.
- `go-self-annot.md` — GoCSL formal semantics plan (G1-G8
  phases with rationale, scope decisions, effort estimates).

## Architectural docs

- [`docs/cross-validated-spec-sources.md`](../../../../docs/cross-validated-spec-sources.md)
  — dual-prover architecture sketch.
- [`docs/pycsl-concrete-syntax-reference.md`](../../../../docs/pycsl-concrete-syntax-reference.md)
  — concrete syntax reference template.
- [`docs/pycsl-static-semantics-reference.md`](../../../../docs/pycsl-static-semantics-reference.md)
  — static semantics reference template.
- [`docs/glossary/trusted-computing-base.md`](../../../../docs/glossary/trusted-computing-base.md)
  — TCB tier glossary.

## Operational references

- [`working-with-two-sources-of-truth.md`](../../../../working-with-two-sources-of-truth.md)
  — operational reference for the cross-check pipeline.
- [`0342_explanation.md`](../../../../0342_explanation.md)
  — GCD worked example end-to-end.
- [`closer-to-code-execution-status.md`](../../../../closer-to-code-execution-status.md)
  — public ledger of TCB-reduction steps.
- [`bin/proof2why3-emit.py`](../../../../bin/proof2why3-emit.py)
  — IR → WhyML axiom-body emitter with `--check` round-trip
  mode.
- [`bin/proof2why3-merge-registry.py`](../../../../bin/proof2why3-merge-registry.py)
  — drift-aware registry merge tool; dry-run by default,
  `--write` to apply.
- Makefile targets: `check-axiom-registry-emittable` (round-trip
  verification), `check-axiom-registry-drift` (kept/added/
  replaced/orphan report), `sync-axiom-registry` (apply rewrite).

## Reference test corpus

- [`test-suite/annotations.md`](../../../../test-suite/annotations.md)
  — authoritative annotation reference (numbered, never
  renumbered).
- [`test-suite/corpus/pycsl-reference/`](../../../../test-suite/corpus/pycsl-reference/)
  — the reference test corpus shape.

## External prior art

- Frama-C / ACSL — <https://frama-c.com/>.
- Creusot / Pearlite — <https://github.com/xldenis/creusot>.
- Dafny — <https://github.com/dafny-lang/dafny>.
- Why3 — <https://why3.lri.fr/>.
- F* — <https://www.fstar-lang.org/>.

## End-to-end trust chain (gocsl reference)

The proven trust chain for a *CSL follows this shape:

```
why3_certificate
  →(module6_encodes_mlw, Axiom)→  vc_prop
  →(vcg_sound, Qed)→             wp_w
  →(wp_gen_correct, Admitted*)→   wp
  →(<lang>csl_soundness, Qed)→   outcome_satisfies
```

\* `wp_gen_correct` may have irreducible Admitted cases for
constructs with abstraction gaps. The two Axioms
(`why3_certificate` and `module6_encodes_mlw`) are the
irreducible trust assumptions: one trusts Why3, the other
trusts the emitter.
