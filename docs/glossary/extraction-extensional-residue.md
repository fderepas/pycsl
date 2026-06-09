**Extraction-extensional residue** is the meta-level claim that
the Rocq-extracted pretty-printer for `whyml_stmt` produces
byte-equivalent output to the Python `Module6_WhyMLTranspiler`
implementation on PyCSL's reference corpus.

It is NOT an Axiom in the Rocq/Lean kernel sense (no
`Axiom`/`Parameter` declaration assumes it). It is a claim
relating two implementations of the same specification:
empirically validated by the byte-diff harness, not proved by
the proof assistant.

---

## Why it exists

The offline Rocq + Lean formalization defines
`emit_stmt : whyml_stmt → string` and proves, per construct, that the
output lies in an `acceptable_emit` set of surface-syntactic
alternatives. The proof anchors at the formal `whyml_stmt` AST and the
Rocq pretty-printer's output.

The Python Module 6 is a separately-written pretty-printer
(string-building code across
`src/pycsl/module6_whyml/{expressions,statements,preamble,
functions}.py`). The formal correspondence theorem
(`emit_stmt_full_complete_sound`, `Phase6L_EmitComposition.v`)
discharges the per-construct `module6_encodes_mlw` decomposition
only modulo this extraction-extensional residue: the two
implementations must agree byte-for-byte on the slice of inputs
covered by the byte-diff test corpus.

The offline correspondence proof eliminates every *named axiom* from
the WP correspondence chain; the residue is what's left, and it lives
at the meta-level between the formal model and the Python
implementation.

## How it is validated

The validation harness is
`bin/extraction-byte-diff-upward.sh`. The pipeline
per `.py` source:

1. `bin/pycsl-ir-dump.py` extracts Module 5's IR JSON from the
   Python source.
2. The extracted Rocq `ir_to_stmt` (via OCaml `ir_driver`)
   consumes the JSON and produces a formal `stmt`.
3. The Rocq-extracted `emit_stmt` is applied to the
   corresponding `whyml_stmt = gen s`.
4. The output is compared byte-for-byte against the Python
   Module 6's actual `.mlw` output.

Empirical state: on the reference corpus the simple-subset
byte-diff scores 23/23 PASS (synth-001..004 + 19 real-corpus
tests fitting the formal expression subset). The full PASS rate
on `test-suite/corpus/pycsl-reference/*.py` is 346/386 = 89.6%,
with the 24 SKIP cases lying outside the formal `expr` / `stmt`
subset and the 16 FAIL_M5 cases reflecting Module 5 limitations
rather than extraction disagreement.

## Why it is acceptable

Eliminating the residue entirely would require either:

- **Rewriting Module 6 in Rocq and extracting its Python**.
  This collapses the two implementations into one (the Python
  side becomes the extracted artifact). Multi-quarter effort;
  trades extension velocity for trust-seam reduction.
- **Mechanically lifting the Python AST to the formal AST and
  diffing the two pretty-printer outputs at every CI run**.
  Already done at the byte-diff level. The "residue" is the
  gap between "byte-diff PASSes on the test corpus" and "byte-
  diff PASSes on every conceivable input".

The residue is accepted, documented explicitly, and the test
corpus is its operational guarantee.

## How it differs from an Axiom

A named Axiom (e.g., the former `module6_encodes_mlw`) is a
formal assumption inside the Rocq kernel — `Print Assumptions
<thm>` lists it. The extraction-extensional residue is
*outside* the kernel: no `Print Assumptions` query mentions
it, no `Closed under the global context` verdict is weakened
by it. It is an engineering assertion about the relationship
between the formal model and the Python codebase.

For a soundness reviewer: the residue is what makes the
Rocq + Lean proof an honest engineering deliverable rather
than a complete formal closure. Closing the IR boundary
shifts the trust line so the residue covers only the
last-mile string-emission gap, not the algorithmic core.

## See also

- [Trusted Computing Base](trusted-computing-base.md) — where
  this residue sits (Tier-3 meta-level).
- [Trust seam](trust-seam.md) — the formally-proved vs
  trusted boundary; the residue is right at the boundary.
- [Verification condition](verification-condition.md) — what
  the extracted vs Python pretty-printers ultimately produce.
- `bin/extraction-byte-diff-upward.sh` — the validation
  harness.
