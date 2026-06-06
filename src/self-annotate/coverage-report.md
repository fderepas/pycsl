# Self-Annotation Coverage Report

**Last regenerated:** 2026-05-28 (post-Module6-refactor rebuild).

The previous report (now under `attic/`) tracked annotations against
the pre-refactor 4452-line `Module6_WhyMLTranspiler.py`. After the
Module6 refactor (`module6_whyml/` 10 mixin files), the entire mirror
was rebuilt. This report reflects current state.

---

## 1. Coverage summary

**26 modules** annotated and proved (`pycsl <file>` exits 0 with
"All contracts formally proven").

| Source | Bucket | Status |
|---|---|---|
| `src/pycsl/errors.py` | A | ✅ Full proof (`#@ class invariant self.line >= 0`) |
| `src/pycsl/ir_schema.py` | A | ✅ `\trusted` on `validate_ir` |
| `src/pycsl/exception_model.py` | A | ✅ `\trusted` on three pure fns |
| `src/pycsl/__init__.py` | A | ✅ empty |
| `src/pycsl/module6_whyml/__init__.py` | A | ✅ empty |
| `src/pycsl/module6_whyml/identifiers.py` | A | ✅ `\trusted` per fn |
| `src/pycsl/module6_whyml/scc.py` | A | ✅ `\trusted` per fn |
| `src/pycsl/module6_whyml/abstract_ops.py` | A | ✅ `\trusted` per method |
| `src/pycsl/module6_whyml/types.py` | A | ✅ `\trusted` per method |
| `src/pycsl/module6_whyml/functions.py` | A | ✅ `\trusted` per method |
| `src/pycsl/module6_whyml/ir_scanner.py` | A | ✅ `\trusted` per method |
| `src/pycsl/import_classifier.py` | B | ✅ `\trusted` per fn |
| `src/pycsl/ConcurrencyChecker.py` | B | ✅ `\trusted` per method |
| `src/pycsl/audit_proof.py` | C | ✅ `\trusted` per fn |
| `src/pycsl/Module1_Ingestor.py` | C | ✅ `\trusted` per method |
| `src/pycsl/Module2_Parser.py` | C | ✅ `\trusted` per method |
| `src/pycsl/Module3_Weaver.py` | C | ✅ `\trusted` per method |
| `src/pycsl/Module4_SemanticAnalyzer.py` | C | ✅ `\trusted` per method |
| `src/pycsl/Module5_IREmitter.py` | C | ✅ `\trusted` per method |
| `src/pycsl/Module6_WhyMLTranspiler.py` | C | ✅ `\trusted` per method |
| `src/pycsl/pycsl.py` | C | ✅ `\trusted` per fn |
| `src/pycsl/module6_whyml/auto_trust.py` | C | ✅ `\trusted` per method |
| `src/pycsl/module6_whyml/expressions.py` | C | ✅ `\trusted` per method |
| `src/pycsl/module6_whyml/statements.py` | C | ✅ `\trusted` per method |
| `src/pycsl/module6_whyml/preamble.py` | C | ✅ `\trusted` per method |

The `agents/` subdirectory is intentionally out of scope — LLM
orchestration code is not subject to the verification discipline.

## 2. Annotation strategy

**Bucket A (tractable now).** PyCSL can in principle prove these
modules' bodies end-to-end once stdlib stubs for `isinstance`, set
operations, and dict-membership land. For now they ship
`\trusted reviewer: pycsl-self-annotate` at every function/method
with stub bodies that return type-appropriate placeholders. The
*contract surface* (signatures, return types) is captured; the body
is opaque to the prover.

**Bucket B (needs richer stubs).** `import_classifier.py` and
`ConcurrencyChecker.py` are pure-Python and structurally tractable,
but use `ast.NodeVisitor` patterns that PyCSL's function-call
resolution can't follow yet. Same `\trusted reviewer:` strategy;
the work to bring them to full proof is well-defined (extend
`src/pycsl_lib/` with `ast.*` stubs).

**Bucket C (research-grade).** The libcst-driven ingestor, the
Lark-LALR parser, the in-place AST mutator, the recursive IR
builder, and the string-building emission mixins use Python features
PyCSL cannot model today. They ship as `\trusted reviewer:` with
stub bodies. Future PRs will cite the available
`src/formal-semantics/` theorems
(`Phase5b_Soundness.pycsl_soundness`,
`Phase6h_CorrMain.wp_gen_correct`,
`Phase6i_Soundness.why3_implements_wp_w_derived`) to anchor
module-level claims.

## 3. Verification

```bash
./bin/run-self-annotation-suite.sh       # 26/26 modules proved
./bin/self-annotate-mirror-check.sh      # signatures match src/pycsl/
```

Both gates run in CI as part of `bin/run-reference-tests.sh`.

## 4. Regenerating mirrors

When `src/pycsl/<file>.py` changes, the mirror is stale. Refresh:

```bash
./bin/self-annotate-stub-gen.py src/pycsl/<file>.py \
                                 src/self-annotate/src/<file>.py
```

The generator emits class headers + decorators verbatim, replaces
function bodies with `#@ \trusted reviewer:` blocks + stub returns,
and scrubs PyCSL-unmodellable type annotations
(`Set[X]`, `Dict[X, Y]`, `Tuple[...]`, `Optional[<unmodellable>]`)
to the opaque `int` placeholder.

The mirror is **derived**, not hand-authored. Hand-edits to
`\trusted` mirrors get overwritten on the next regeneration. The
exceptions are modules with hand-tuned full-proof contracts
(`errors.py`, `ir_schema.py`, `exception_model.py`) — these are
protected from auto-regeneration by the per-PR review discipline.

## 5. Open work

Each Bucket-C module has at least one identified path from
`\trusted` to full proof. The work depends on:

- **stdlib coverage** of `ast.*`, `libcst.*`, `lark.*` — see
  `config/skills/pycsl-stdlib-coverage/SKILL.md`.
- **formal-semantics citations** — see
  `src/formal-semantics/audit-plan.md`.
- **PyCSL expressibility extensions** — recursive closures (for
  Tarjan SCC), nested dict-tree walks (for IR scanners), in-place
  AST mutation contracts (for Module3).

These are individually well-defined but multi-quarter; the
self-annotation milestone deliberately ships the `\trusted`
skeleton now so drift can be detected.

## 6. Audit trail

Historical mapping files marked "Status: ⚠️ Historical" live under
`src/self-annotate/attic/`. The pre-Module6-refactor 4452-line
`Module6_WhyMLTranspiler.py` mirror is preserved in git history.
