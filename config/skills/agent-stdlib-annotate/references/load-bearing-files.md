# Load-bearing files — supervisor deny-list

Files in this list **always raise the `human-needed` signal** when a
feature-plan phase declares them as a modification target. The
supervisor will never attempt to edit them autonomously (even under
coding-LLM delegation), because their incorrect modification produces
silent unsoundness in the proof pipeline.

## Deny-list

The supervisor matches by **path suffix** (case-sensitive). A
feature plan listing any file whose path ends with one of these
entries causes that phase to halt with exit 75.

```
src/pycsl/Module2_Parser.py
src/pycsl/Module3_Weaver.py
src/pycsl/Module4_SemanticAnalyzer.py
src/pycsl/Module5_IREmitter.py
src/pycsl/Module6_WhyMLTranspiler.py
src/pycsl/ir_schema.py
src/pycsl/exception_model.py
src/pycsl/module6_whyml/types.py
src/pycsl/module6_whyml/expressions.py
src/pycsl/module6_whyml/statements.py
src/pycsl/module6_whyml/preamble.py
src/pycsl/module6_whyml/functions.py
src/pycsl/module6_whyml/identifiers.py
src/pycsl/module6_whyml/auto_trust.py
src/pycsl/module6_whyml/abstract_ops.py
src/pycsl/csl.lark
src/formal-semantics/
docs/pycsl-concrete-syntax-reference.md
docs/pycsl-static-semantics-reference.md
docs/pycsl-translational-reference.md
test-suite/annotations.md
test-suite/traceability-pycsl.md
```

## Rationale

- **Module 2–6 + grammar (`csl.lark`)**: the parser/IR/emitter
  pipeline. Wrong edits silently produce unsound WhyML.
- **`ir_schema.py`**: the Module 5 ↔ 6 contract; squeezes S6.
- **`exception_model.py`**: the trigger table for `no_exception`;
  wrong edits add or remove exception predicates from VCs.
- **`formal-semantics/`**: the Rocq + Lean proof corpus; squeeze S2.
- **3 normative `docs/pycsl-*-reference.md`**: the three-layer
  validation stack; structural correctness is enforced by
  `bin/doc-coherency.py` but the *content* needs human judgement
  for any new rule.
- **`annotations.md`, `traceability-pycsl.md`**: paragraph-stable,
  append-only — automated edits risk renumbering.

## How to add an entry

Append the path suffix on its own line in the deny-list block above.
Do NOT remove entries without a corresponding `better-agent.md`
update — entries here are CCB-controlled per Profile-P
(single-developer CCB; commit SHA = CR-ID).
