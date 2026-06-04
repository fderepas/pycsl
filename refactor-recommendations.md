# Refactoring recommendations — `src/pycsl/*.py` + `src/pycsl/module6_whyml/*.py`

> Derived from a read-only review of the PyCSL pipeline modules and the WhyML backend
> package. Opportunities are grouped by recurring theme and tiered by payoff-vs-risk.

## Implementation status

Each landed item is validated **emission-identical** to its baseline (PYTHONHASHSEED=0,
`--no-proof` differential over all 382 tracked `pycsl-reference` corpus files, 0 diffs).

- ✅ **Tier 1** — all five quick wins landed (`abfaf0e`): `_deref` (29 sites),
  `_binop` alias collapse, `_emit_ghost_assign`, `_inject_functions`,
  `_attach_loop_contracts`.
- ✅ **Tier 3 (god-functions, partial)** — `_handle_call_expr` split into
  `_call_named_builtins`/`_call_record_constructor`/`_call_bytes_methods` (`2b0fca0`);
  `_handle_dotted_call` split into `_resolve_dotted_signature`/`_coerce_dotted_args`/
  `_dotted_ensures_suffix` (`781c24f`).
- ⏸ **Deferred, with rationale** (kept as roadmap):
  - *Tier 2 `statements.py` `s_type` dispatch table* — a 20-branch chain mixing
    early-return and fall-through; a safe table conversion needs ~20 inline-body
    extractions, which is high transcription-risk for a readability-only gain. Defer to a
    focused effort.
  - *Tier 3 `pycsl.py` `main()`/argparse restructure* — changes CLI control flow, **not**
    WhyML emission, so the emission-identical oracle does not cover it; it needs a separate
    CLI-behavior test harness before it can be done safely.
  - *Tier 3 `_handle_for_stmt` split* — only ~90 lines with clear phases, **and** it carries
    PyCSL self-annotation `#@ loop invariant`/`variant` comments (a separate self-
    verification effort); low marginal value, extra risk. Skip.
  - *Tier 2 `Module5._py_stmt_assign` dispatch dict* — already 4 clear branches; a dict adds
    indirection for no real gain. Skip.
  - *Tier 2 `Module3._dispatch_function_contracts` table* — the special cases (Trusted
    warning, NoException) make a half-table/half-elif hybrid less readable than the current
    uniform chain. Skip.
  - *Tier 4 "unify write-site discovery across Module3/4/5"* — on close reading these are
    three **different** operations (per-field write-sites vs written-field-names vs
    field-types); unifying would be a false abstraction. Skip.
- 🚪 **Tier 5 (architectural bets)** — still gated; unchanged below.

## Scope & worst offenders

Reviewed: `src/pycsl/Module1_Ingestor.py`, `Module2_Parser.py`, `Module3_Weaver.py`,
`Module4_SemanticAnalyzer.py`, `Module5_IREmitter.py`, `pycsl.py`, and the
`src/pycsl/module6_whyml/` package.

By size/complexity the hot spots are: `expressions.py` (1523), `statements.py` (1416),
`Module5_IREmitter.py` (1374), `Module2_Parser.py` (1088), `pycsl.py` (1070).

**Leave alone:** `pure_ast.py` (a faithful CPython `ast`/unparser port — refactoring it
would diverge from upstream for negative value), `scc.py`, `identifiers.py`,
`struct_format.py`, `ir_scanner.py` (all small, cohesive, single-purpose).

## Validation rule (non-negotiable — this is a verifier)

Every item below is behavior-preserving *by intent*, but PyCSL emits proof obligations:
a subtle change in IR/WhyML emission can silently change provability. Validate each
refactor with the discipline the codebase already uses, **not** with "it's obviously
equivalent":

1. **Module1 differential** — old-vs-new harvest byte-identical on the corpus.
2. **Emission-identical** — generated WhyML identical (old vs new) for the
   `pycsl-reference` corpus under `--no-proof` (currently 416/416).
3. **Proof spot-check** — a representative proof run (`PYTHONHASHSEED=0`), plus the full
   `bin/run-reference-tests.sh` before merging anything in Tier 5.

*The corpus is the test suite.* Treat "no tests needed" as false for this package.

---

## Tier 1 — Quick wins (high payoff, near-zero risk, pure refactor)

| # | Location | Smell | Change |
|---|---|---|---|
| 1 | `module6_whyml/expressions.py` — `!{x.lstrip('!')}` ternary repeated **30+×** (set/list/map handlers, ~lines 1316–1407) | Duplication | Extract `_deref(expr)`; ~100 LOC removed. Highest LOC payoff in the package. |
| 2 | `Module2_Parser.py:994–1000` — 7 identical `def logical_or/logical_and/equality/comparison/term/factor/implication: return BinOp(left, str(op), right)` | 1:1 boilerplate | Collapse to one generic binary-op handler (or `@v_args` table). ~70 LOC. |
| 3 | `Module5_IREmitter.py:700–730` — ghost-assign IR dict built verbatim in the leading and trailing loops | Copy-paste | Extract `_emit_ghost_assign(ga)`. |
| 4 | `pycsl.py:196–300` — `_resolve_direct_imports` / `_resolve_wildcard_imports` / `_resolve_module_imports` share a near-identical inject loop | Duplication | Extract `_inject_functions(dep_funcs, ir_data) -> Set[str]`. ~30 LOC. |
| 5 | `Module3_Weaver.py:270–307` — `visit_While` and `visit_For` repeat the `LoopInvariant`/`LoopVariant`/ghost-assign attach | Duplication | Extract `_attach_loop_contracts(node, contracts)`. **Note:** `visit_While` correctly omits `allow_iteration_mutation` (a `for`-only, container-iteration concern) — do *not* "add" it. |

~250 LOC net reduction; each independently shippable.

## Tier 2 — Dispatch-table conversions (high payoff, low risk)

The same `isinstance`/`elif` (or `== "..."`) chain recurs in three places. Convert each to
a `{type-or-str → handler}` table — the established idiom in this codebase
(`Module6_WhyMLTranspiler._EXPR_DISPATCH`):

- **`module6_whyml/statements.py:1153–1241`** — the 20-branch `s_type == …` god-dispatcher
  (~105 lines). Biggest single win. Some arms return early, others set `code` and fall
  through — split the table into "early-return" vs "code-producing" handlers, or normalize
  all handlers to return the emitted string.
- **`Module3_Weaver.py:132–170`** — `_dispatch_function_contracts` (39-line node→`csl_*`
  chain). Bonus: drive `_init_function_csl_fields` (Module3:39–59, 16 hand-written inits)
  from the **same** schema dict, so a new contract type is one table entry instead of edits
  in three spots.
- **`Module5_IREmitter.py:733–764`** — `_py_stmt_assign` target dispatch (Name / Attribute /
  Subscript / Tuple → Assign / FieldAssign / ArraySet+ArraySliceSet / TupleUnpack). Extract
  `_assign_var/_assign_field/_assign_subscript/_assign_tuple`; keep the slice-vs-index branch
  carefully (it has real logic).

## Tier 3 — Break up the god functions (medium payoff, low risk)

- **`module6_whyml/expressions.py:581–770`** — `_handle_call_expr` (**190 lines**, the largest
  function in the package): a cascade of `if func_name == "len"/"min"/"isinstance"/…`. Split
  into `_dispatch_builtin_call` / `_dispatch_collection_call` / `_dispatch_bytes_call`.
- **`module6_whyml/expressions.py:850–1005`** — `_handle_dotted_call` (~155 lines, 40+ method
  patterns): extract `_emit_method_call(receiver_type, method, args, …)` for the repeated
  "register abstract op → emit call" shape.
- **`module6_whyml/statements.py`** — `_handle_for_stmt` (~92 lines, 3–4 levels of nesting):
  push iterable-classification handling into a dedicated `_emit_for_iterable` helper.
- **`pycsl.py`** — `main()` + a 21-flag `argparse` mix CLI parsing, file IO, proving, and
  reporting. Group flags by concern (prover / proof-mode / strictness / debug) and split
  `main()` into `_run_verify` / `_run_audit`. Medium risk (entry point) — do last, gated.

## Tier 4 — HAPPY-specific cleanup (the recently-added code)

- **Unify write-site discovery.** Three sites independently re-implement "walk the AST for
  `self.<field>[…]` writes": `Module3_Weaver._field_write_site`/`_collect_field_sites` (the
  HAPPY meta-pass), `Module4_SemanticAnalyzer._validate_happy`, and `Module5_IREmitter`'s
  `__init__` field-discovery. Extract one `ast_writes.collect_self_field_writes(node, field)`
  and have all three call it. **Highest-value HAPPY cleanup** — removes duplication introduced
  by the meta-pass.
- **`module6_whyml/statements.py:1198` (ProofAssert)** — replace the manual
  `self._in_spec = True … self._in_spec = False` toggle with a `with self._spec_context():`
  context manager (nesting-safe; the flag is shared global state).
- **`Module5_IREmitter._csl_field_subscript`** — extract
  `_lower_field_subscript(obj, field, index_ir)` so `"self"` isn't hardcoded into the dict
  shape, easing any future non-`self` field-subscript.

## Tier 5 — Architectural bets (high long-term payoff, real cost — gate behind a decision)

These are **not** quick wins. Each is a multi-hundred-line change that should be its own
explicitly-scoped initiative with a **full `run-reference-tests.sh` proof-sweep budget**
(~1–2 hr) as the acceptance gate — not folded into routine cleanup. Recommend only if you
are deliberately investing in the backend's long-term maintainability.

### 5a. Emission-context object — *recommended first of the two*

**Smell.** ~70 handlers thread the same context by hand:
- expressions: `_handle_*_expr(expr, local_refs, invariant_ctx=False, subst=None)`
- statements: `_handle_*_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop=False)`

plus the global `self._in_spec` flag toggled in/around several handlers. Every call site
re-passes 3–6 parameters; adding a new piece of context (as the HAPPY `origin` threading
just showed) means touching every signature.

**Change.** Introduce two dataclasses and pass one object:

```python
@dataclass
class ExprCtx:
    local_refs: Set[str]
    invariant_ctx: bool = False
    subst: Optional[Dict[str, str]] = None
    in_spec: bool = False           # subsumes the self._in_spec flag

@dataclass
class StmtCtx:
    local_refs: Set[str]
    declared_refs: Set[str]
    indent: str
    in_loop: bool = False
```

Handlers become `_handle_*_expr(expr, ctx)` / `_handle_*_stmt(stmt, rest, ctx)`; a child
context is a cheap `dataclasses.replace(ctx, …)`. This also retires the `_in_spec`
side-effect flag (Tier 4) by making spec-mode a context field.

**Cost / risk.** ~200 lines of signature churn across `expressions.py` + `statements.py`;
mechanical but broad. **Behavior-preserving**, but must be validated emission-identical on
the full corpus. **Payoff:** the largest readability/extensibility win in the backend; future
context additions become one field instead of 70 signature edits.

### 5b. Memory-model strategy — *highest payoff, highest risk*

**Smell.** ~18 scattered branches of the form
`if self.memory_model in ("hoare", "concurrent"): … else: …` with model-specific emission,
across `expressions.py` (≥12: e.g. `_handle_arraylen_expr` ~1057, subscript ~799, old ~958),
`statements.py` (≥4: `_handle_for_stmt` ~184, array-set ~206/222, ~688), `functions.py`
(~29, ~128), `preamble.py` (~146, ~278). The hoare/concurrent vs typed/store split is a
single concept duplicated 18×, and is drift-prone (a change to one branch can silently
diverge from its siblings).

**Change.** Introduce a strategy object selected once in `__init__`:

```python
class MemoryModelStrategy:           # interface
    def array_length(self, name: str) -> str: ...
    def for_loop_var(self, var: str) -> str: ...
    def element_read(self, base: str, index: str) -> str: ...
    def element_write(self, base: str, index: str, value: str) -> str: ...
    # … one method per current branch site

class HoareConcurrent(MemoryModelStrategy): ...   # value-semantic arrays
class TypedStore(MemoryModelStrategy): ...        # int_mem / Map heap

self._mem = HoareConcurrent() if memory_model in ("hoare", "concurrent") else TypedStore()
```

Replace each `if memory_model in (...)` block with a `self._mem.<op>(...)` call.

**Cost / risk.** ~1–2 days; ~15 strategy methods; touches the most proof-sensitive code in
the toolchain. **Highest risk** of accidentally changing emission. **Must** be validated on
**all four** models (hoare, typed, store, concurrent) with full proof sweeps, not just
`--no-proof`. **Payoff:** the model logic stops being duplicated/drift-prone; adding a model,
or fixing a model-specific bug, becomes localized to one class.

**Sequencing note.** Do **5a before 5b** — once handlers take a context object, the strategy
calls thread cleanly through it, and the two refactors don't fight over the same signatures.

### Explicitly *not* recommended

- **Collapsing the ~90 `CSLNode` dataclasses** (`Module2_Parser.py:13–599`). The per-grammar-
  rule node types are correct for a Lark transformer and enable precise pattern-matching
  downstream; merging them (`base1/base2 → bases: list`, etc.) trades clarity for nothing and
  breaks consumers. Leave as-is.
- **A general WhyML builder/AST** to replace f-string emission. Tempting for safety, but it is
  a large rewrite of the backend's output layer for marginal gain over the current readable
  f-strings; only revisit if paren-matching bugs become a recurring source of defects.

---

## Suggested sequencing

1. **Tier 1** — one small PR (mechanical, ~250 LOC out), corpus `--no-proof` gate.
2. **Tier 2** — dispatch tables, one PR per site, corpus gate.
3. **Tier 4** — HAPPY-duplication cleanup (the `ast_writes` extraction + `_spec_context`).
4. **Tier 3** — god-function splits.
5. **Tier 5** — only as a deliberate, separately-scoped initiative: **5a then 5b**, each with
   a full `run-reference-tests.sh` acceptance run across all memory models.

Each PR carries the differential evidence (Module1 byte-identical + emission-identical +
proof spot-check) in its description.
