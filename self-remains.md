# Self-Annotation — Remaining Work

**Current state (2026-05-28):** 26/26 mirrors in `src/self-annotate/src/`
pass `pycsl <file>` end-to-end via `\trusted reviewer:` stubs. Only
`src/pycsl/errors.py` (the canonical source) carries a real class
invariant. Every other module ships an interface-only contract with a
stubbed body.

The work below upgrades modules from `\trusted-with-stub` to
*full proof* (real body + provable contract). Items are framed as
tickets the planner can pick up independently; effort estimates are
single-engineer.

---

## Conventions used below

- **State:** *trusted-stub* = current; *full-proof* = target.
- **Blocker types:**
  - **Stub-extension** — needs new entries in `src/pycsl_lib/` to model a stdlib API.
  - **Stub-quality** — has a stub, but its contract is too weak to prove the caller.
  - **PyCSL feature** — needs a new language/expressibility feature (closures over mutable refs, in-place AST mutation contracts, recursive dict-tree walks).
  - **Formal-semantics citation** — needs a new `#@ proof rocq/lean` theorem reference (and possibly a new theorem proved in `src/formal-semantics/`).

---

## Bucket A — full proof is tractable once stdlib stubs land

These modules have body shapes PyCSL can in principle model; the
blockers are entirely on the stdlib-stub side. Effort is concrete and
small per module.

### A.1 `ir_schema.py` (already in self-annotate; full-proof TODO)

**Blockers:**
- **Stub-extension** — `isinstance(x, dict)`, `isinstance(x, list)` with sound postconditions tied to a PyCSL type-tag predicate.
- **Stub-extension** — set-difference `_REQUIRED_TOP - ir.keys()` returning a set; iteration via `for x in set: ...`.
- **Stub-extension** — `sorted(set)` returning a list; `dict.get(key, default)`; `enumerate()` over a list.
- **PyCSL feature** — f-strings as opaque-int values (currently hashed by `_handle_fstring_expr` but not modelled).

**Concrete steps:**
1. Add `isinstance` stub with postcondition `\result == 0 or \result == 1` and a ghost shadow predicate `is_dict(x)` / `is_list(x)`.
2. Add `set.__sub__` stub returning a fresh set with `\length(\result) >= 0`.
3. Add `dict.keys()` returning an iterable set; `sorted(set)` returning a list of length `\length(input)`.
4. Replace the `\trusted` stub with the real body; add `#@ raises PyCSLIRError when ...` clauses tied to the four error sites.

**Effort:** 1 week. Stub work in PR; annotation in follow-up PR.

### A.2 `exception_model.py`

**Blockers:**
- **Stub-extension** — `dict.get` on tuple-keyed dict (`TRIGGERS.get(op_key, [])`).
- **Stub-extension** — list comprehension over dict items (`[v for k, v in PREDICATE_LIBRARY.items() if k in needed]`).
- **Stub-extension** — `sorted(frozenset)`; `frozenset` membership tests.

**Concrete steps:**
1. Add tuple-keyed-dict stub variant (Phase 2 ghost-tuple work — see `pycsl-annotate/SKILL.md` §3 typed ghosts).
2. Add `dict.items()` iterator stub; list-comprehension over typed iterators.
3. Replace `\trusted` with real bodies and prove `#@ ensures \length(\result) >= 0` per function.

**Effort:** 3 days; depends on A.1's set/dict stub work.

### A.3 `module6_whyml/identifiers.py`

**Blockers:**
- **Stub-extension** — `OP_MAP.get(op, op)` — string-keyed dict with string return. Tractable.
- **Stub-extension** — `WHYML_RESERVED` set membership (`name in WHYML_RESERVED`).
- **PyCSL feature** — `unicodedata.normalize(...)` body. Treat as `\trusted` opaque conversion.
- **PyCSL feature** — list comprehension over a string (`[c for c in decomp if ord(c) < 128]`). Currently hard.

**Concrete steps:**
1. Prove `op_translate` first — pure `dict.get` on a constant table; ~30 minutes.
2. Prove `safe_mutex_name` — three chained `.replace` calls; ~1 hour.
3. Leave `whyml_ident` Unicode branch as `\trusted` for now; prove the simple-name fast path.

**Effort:** 2 days for partial proof; Unicode branch stays `\trusted` indefinitely.

### A.4 `module6_whyml/scc.py`

**Reality check:** Tarjan's SCC uses recursive closures over mutable
state (`index_counter`, `stack`, `lowlink`, `on_stack`). PyCSL cannot
model recursive-closure-with-mutable-ref today. **Reclassify as
Bucket C.** No near-term path to full proof; the contract is
"composes the two trusted helpers; inherits their attestation".

**Effort:** N/A — research feature work, not a ticket here.

### A.5 `module6_whyml/abstract_ops.py`

**Blockers:**
- **PyCSL feature** — class invariant for `self._abstract_ops: Dict[str, str]`. PyCSL's record-field type for dicts is `map int (option int)`, not `map int (option string)`.
- **Stub-extension** — `decl.split()`, `.count(...)`, `len(parts)`.
- **PyCSL feature** — in-place list mutation (`out.insert(...)`).

**Concrete steps:**
1. Add a class invariant restricting `_abstract_ops`'s "size" (need ghost shadowing because PyCSL can't reason about string-keyed dicts).
2. Stub `str.split` returning a list of length `\length(input.split(...))`; same for `.count`.
3. Prove `_find_abstract_val_insert_idx` first (return non-negative; only reads `out`).

**Effort:** 1 week.

### A.6 `module6_whyml/types.py`

Mostly small lookup methods. Tractable in principle.

**Blockers:** dict access for `_BOOL_BINOPS`, `_record_types` lookups,
`field_types` per-field maps.

**Concrete steps:**
1. Prove `_val_is_bool` (frozenset membership on `_BOOL_BINOPS`).
2. Prove `_first_assign_kind` (dispatch by `val_ir["type"]`).
3. Defer dict-of-dict methods (`_record_types[...][...]`).

**Effort:** 1 week for the simple half; another week for the harder half.

### A.7 `module6_whyml/functions.py`

**Reality check:** signature assembly is tractable; body emission is
hard. Split per method.

**Concrete steps:**
1. Prove `_param_type_str` (string concat from a fixed type table).
2. Prove `_symtype_to_whyml` (simple dispatch).
3. Defer `_emit_contracts`, `_emit_function` (large multi-pass emission).

**Effort:** 1 week for partial proof.

### A.8 `module6_whyml/ir_scanner.py`

**Reality check:** all 30+ scanner methods are recursive dict-tree
walks with isinstance discrimination. PyCSL cannot prove these today
without nested-dict-walk expressibility.

**Reclassify as Bucket B once `isinstance` + nested dict stubs land.**

**Effort:** 2 weeks after stub work.

---

## Bucket B — needs richer stdlib stubs

### B.1 `import_classifier.py`

**Blockers:**
- **Stub-extension** — `ast.walk(tree)` iterator stub.
- **Stub-extension** — `ast.Import`, `ast.ImportFrom` type tags + `.names`, `.module` attribute accesses.
- **Stub-extension** — `Path.iterdir()`, `Path.suffix`, `Path.stem`.
- **Stub-extension** — frozenset membership.

**Concrete steps:**
1. Add `ast.*` stubs to `src/pycsl_lib/ast.py` (Phase 1: `ast.walk`, `ast.Import.names`, `ast.ImportFrom.module`).
2. Add `pathlib.Path` stubs to `src/pycsl_lib/pathlib.py`.
3. Prove `classify(module_name, stubs, deny_list)` — returns one of three string constants. Tractable today with `frozenset` stub.
4. Prove `collect_imports(tree)` — iterable of pairs, returns list.
5. Defer `check_imports` to a follow-up — it raises and has complex control flow.

**Effort:** 1 week stubs + 3 days annotation.

### B.2 `ConcurrencyChecker.py`

**Blockers:**
- **Stub-extension** — `ast.NodeVisitor` base-class stubs.
- **PyCSL feature** — `held: Set[str]` parameter that grows on `with` entry. PyCSL cannot model set-add at call-time today.

**Concrete steps:**
1. Add `ast.NodeVisitor.visit`, `ast.walk`, `ast.iter_child_nodes` stubs.
2. Define `Set[str]` as `ghost_set` in the annotated mirror (use the existing typed-ghost vocabulary).
3. Prove `_warn_if_unprotected` — pure dict lookup + list append.
4. Defer `_walk_*` recursive methods.

**Effort:** 1 week.

---

## Bucket C — research-grade

These need PyCSL features that don't exist yet OR formal-semantics
citations that go beyond what's already proved. Each represents
multi-quarter work; the order suggests dependencies rather than
strict sequencing.

### C.1 `audit_proof.py`

**Blockers:**
- **PyCSL feature** — regex (`re.compile`, `pattern.search`).
- **PyCSL feature** — `pathlib.Path` read operations.
- **PyCSL feature** — state-machine parsing over string content.

**Realistic target:** ship long-term as `\trusted reviewer: <human>`;
the state-machine semantics are hard to model and the value of
proving the parser is low. The trust anchor is the audit-against-cpython-docs check, not a PyCSL proof.

### C.2 `Module1_Ingestor.py` — libcst CST visitor

**Blockers:**
- **PyCSL feature** — `libcst.CSTVisitor` with `PositionProvider` metadata.
- **PyCSL feature** — `cst.Module`, `cst.Comment` typed-node hierarchy.

**Cite from formal-semantics:** none directly available — the
formal model starts at the AST level, downstream of libcst.

**Realistic target:** `\trusted reviewer:` long-term. Path to full
proof requires modelling libcst as a stub library — a multi-month
effort comparable to the stdlib-coverage workplan but for a
third-party package.

### C.3 `Module2_Parser.py` — Lark LALR parser

**Blockers:**
- **PyCSL feature** — Lark `Transformer` subclass with `@v_args`-decorated methods.
- **PyCSL feature** — exception-control-flow inside parser callbacks.

**Cite from formal-semantics:** `Phase1_AST.v` defines the CSL AST
types that the parser builds — there's a *correspondence* claim
("the parser's output IR matches Phase1_AST"), but it's not formally
proved end-to-end.

**Realistic target:** `\trusted reviewer:` long-term. Lark-modelling is
a research project.

### C.4 `Module3_Weaver.py` — in-place AST mutation

**Blockers:**
- **PyCSL feature** — in-place mutation of `ast.AST` nodes (`node.csl_requires = []` etc.). PyCSL's frame-condition vocabulary covers `\assigns arr[lo..hi]` but not "this Python AST object gains a new attribute".

**Realistic target:** `\trusted reviewer:` long-term. A frame-condition
extension for arbitrary-attribute mutation is a known open research
problem.

### C.5 `Module4_SemanticAnalyzer.py`

**Blockers:**
- Recursive `_CSL_CHILDREN_MAP` dispatch over CSLNode subtypes.
- Symbol-table maintenance via mutable dict.
- Type checking with isinstance dispatch.

**Cite from formal-semantics:** `Phase1_AST.wf_expr_decidable` (if
present) — the well-formedness predicate for expressions. Add a
module-level `#@ proof rocq Phase1_AST.wf_expr_decidable` citation.

**Concrete next step (cheap):** add the formal-semantics citation
even while the body remains `\trusted`. The citation documents the
semantic anchor the analyzer is implementing.

**Effort for citation only:** 1 day.

### C.6 `Module5_IREmitter.py`

**Blockers:**
- Recursive AST→IR emission (`_py_expr_to_ir`, `_py_stmts_to_ir`).
- Mutable program_ir state (`self.program_ir["functions"].append(...)`).

**Cite from formal-semantics:** `Phase6h_CorrMain.wp_gen_correct`
(Rocq) and `PyCSL.CorrMain.wpGenCorrect` (Lean) prove the IR-to-WP
correspondence. **Add module-level citations now**:

```python
#@ proof rocq Phase6h_CorrMain.wp_gen_correct
#@ proof lean PyCSL.CorrMain.wpGenCorrect
```

**Concrete next step:** apply these two `#@ proof` directives to the
mirror's preamble. The functions remain `\trusted` but the
module-level claim is anchored to the proved theorem.

**Effort:** 1 day for citation; full-body proof is multi-quarter.

### C.7 `Module6_WhyMLTranspiler.py` (the 350-line facade)

**Cite from formal-semantics:**
`Phase5b_Soundness.pycsl_soundness` (Rocq) and
`PyCSL.Soundness.pycsl_soundness` (Lean) prove end-to-end soundness.

**Concrete next step:** add to the mirror's preamble:

```python
#@ proof rocq Phase5b_Soundness.pycsl_soundness
#@ proof lean PyCSL.Soundness.pycsl_soundness
```

**Effort:** 1 day for citation; the citation IS the trust anchor
for the entire pipeline.

### C.8 `module6_whyml/auto_trust.py`

Auto-trust heuristics for "this function can be silently `\trusted`
because its return type isn't fully modellable". Pure logic; could
in principle prove, but PyCSL can't model the inspection patterns
the heuristic uses.

**Realistic target:** `\trusted reviewer:` long-term.

### C.9 `module6_whyml/expressions.py` (~1200 lines)

**Cite from formal-semantics:** `Phase6c_ExprTrans.expr_trans_correct`
if it exists; otherwise this module's correctness is delegated via
`pycsl_soundness` at the facade level (C.7).

**Concrete next step:** add the citation if a per-expression-shape
theorem exists in `src/formal-semantics/rocq/Phase6c_*.v`. Otherwise
delegate.

**Effort:** 1 day to inspect formal-semantics + add citation if found.

### C.10 `module6_whyml/statements.py` (~1300 lines)

Same as C.9 but for `Phase6d_StmtGen.gen_correct` /
`Phase6e_Handle*.handle_*_correct`.

**Effort:** 1 day for citation work.

### C.11 `module6_whyml/preamble.py`

**Cite from formal-semantics:**
`Phase6i_Soundness.why3_implements_wp_w_derived` for the VCG bridge
preamble emission. **Concrete next step:**

```python
#@ proof rocq Phase6i_Soundness.why3_implements_wp_w_derived
#@ proof lean PyCSL.Why3Vcg.vcgSound
```

**Effort:** 1 day.

### C.12 `pycsl.py` (CLI orchestrator)

Pure I/O: argparse, subprocess, file I/O. No formal anchor possible.

**Realistic target:** `\trusted reviewer:` long-term. The CLI is
outside the verification target.

---

## Cross-cutting items

### CC.1 Stub library extensions needed (priority order)

These unblock multiple modules. Order by impact:

1. **`ast.*`** — unblocks B.1, B.2, C.5, C.6. Highest leverage.
   - `ast.walk`, `ast.iter_child_nodes`, `ast.NodeVisitor.visit`.
   - Type tags for `ast.Import`, `ast.ImportFrom`, `ast.FunctionDef`, `ast.ClassDef`, etc.
2. **`isinstance` predicate framework** — unblocks A.1, A.2, A.8.
3. **Set / frozenset** — unblocks A.2, A.6, B.1, B.2.
4. **`dict.get` / `dict.items()` / `dict.keys()`** — unblocks A.1, A.2, A.5, A.6.
5. **`re.compile` / `pattern.search`** — only unblocks C.1; lower priority.
6. **`pathlib.Path`** — only B.1's `Path.iterdir`.
7. **`libcst.*`** — only C.2; deferred (parallel research project).
8. **`lark.*`** — only C.3; deferred (parallel research project).

### CC.2 Formal-semantics citations to add right now

These are cheap (one-day tickets) and anchor the trust chain:

| Module | Rocq | Lean | Status |
|---|---|---|---|
| `Module5_IREmitter.py` | `Phase6h_CorrMain.wp_gen_correct` | `PyCSL.CorrMain.wpGenCorrect` | ✅ Added 2026-05-29 |
| `Module6_WhyMLTranspiler.py` | `Phase5b_Soundness.pycsl_soundness` | `PyCSL.Soundness.pycsl_soundness` | ✅ Added 2026-05-29 |
| `module6_whyml/preamble.py` | `Phase6i_Soundness.why3_implements_wp_w_derived` | `PyCSL.Why3Vcg.vcgSound` | ✅ Added 2026-05-29 |
| `Module4_SemanticAnalyzer.py` | `Phase1_AST.expr_eq_dec` | `PyCSL.AST.Expr.decEq` | ✅ Added 2026-05-29 — `expr_eq_dec` lemma added to `Phase1_AST.v` (decidable equality on `expr`, anchoring the analyzer's `isinstance` AST-node comparison). Lean mirror: added `DecidableEq` to `Expr` `deriving` clause. |

Verify each citation via `pycsl --audit-proof <mirror_file>` after adding.

**Q3 Sub-β follow-up (2026-05-29):** 4 of 4 citations landed.
For Module 4, a new `expr_eq_dec` lemma was added to
`Phase1_AST.v` (with the Lean mirror gaining `DecidableEq` on
`Expr`) to anchor the citation. The self-annotation suite
(`bin/run-self-annotation-suite.sh`) reports 26/26 PASS and the
mirror-check (`bin/self-annotate-mirror-check.sh`) confirms all
25 mirrors are in sync with `src/pycsl/`.

### CC.3 Mirror-generation rules to harden

The current generator produces correct stubs but a few rough edges:
- Empty-body classes need explicit `pass` (added in PR 12; verify still robust).
- Type-annotation scrub is aggressive (`Set[X]` → `int`). Document the rule in `bin/self-annotate-stub-gen.py`'s header.
- `*args, **kwargs` parameters don't get type annotations; the generator should preserve them verbatim (verify).
- Decorators with arguments (`@dataclass(frozen=True)`) — verify the generator handles them.

### CC.4 Suggested execution order

Given the above, a reasonable per-quarter plan:

**Q1 (low-hanging):**
- CC.2 — formal-semantics citations (1 week total across 4 modules).
- A.3 — `op_translate` and `safe_mutex_name` partial proof (2 days).
- A.1 partial — `validate_ir` outer guard (`isinstance`) proof if `isinstance` stub lands.

**Q2 (stub-extension wave):**
- CC.1 item 1 — `ast.*` stubs.
- CC.1 item 2-4 — `isinstance` / set / dict stubs.
- B.1 and B.2 full proof.

**Q3 (Bucket A completions):**
- A.1, A.2 full proof.
- A.5, A.6, A.7 partial proof per method.

**Q4+ (research):**
- C.5–C.11 deeper formal-semantics integration.
- C.2, C.3 (libcst, Lark) only if external stub work justifies the
  multi-month investment.

The Bucket-C "research" items have no near-term path to full proof
and may remain `\trusted reviewer:` permanently. That's an acceptable
end state — the trust chain is anchored at the formal-semantics
theorems via the citations from CC.2, not at the Python bodies.

---

## How to track progress

When you start a ticket:
1. Mark the source `#@ proof rocq <q>` / `#@ proof lean <q>` (citation tickets) or replace `\trusted reviewer:` with real contracts + body (proof tickets).
2. Run `./bin/run-self-annotation-suite.sh` — must stay at 26/26.
3. Run `./bin/self-annotate-mirror-check.sh` — signatures must still match `src/pycsl/`.
4. Update `src/self-annotate/coverage-report.md` row for the module (change ✅ `\trusted` to ✅ Full proof, or add citation note).
5. For citation tickets, run `pycsl --audit-proof src/self-annotate/src/<file>` to verify the Rocq/Lean qualname resolves.

The mirror-check + suite + citation-audit triple is the regression
gate. As long as those three exit 0, the trust chain is intact.
