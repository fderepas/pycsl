---
name: pycsl-exception-model
description: Documents the PyCSL exception trigger model — the central mapping from IR operations to the implicit Python exceptions they may raise, and the WhyML trigger conditions that prevent them. Consulted by Module 4 (semantic validation of `no_exception`) and Module 6 (`module6_whyml/expressions.py`, `statements.py`, `preamble.py` — VC injection and predicate library). Use this skill whenever extending the `no_exception` contract directive, adding new exception triggers, or designing tests under `test-suite/corpus/pycsl-reference/` that exercise implicit-exception proof obligations.
---

# PyCSL Exception Trigger Model

## Purpose and scope

This skill is the single source of truth for the contract:

> *"Which IR operations raise which implicit Python exceptions, and which
> WhyML side condition is sufficient to prevent each one?"*

It governs the `no_exception E1, E2, …` (and `no_exception \all`)
contract directive (§2.1.13 of `docs/pycsl-concrete-syntax-reference.md`).
The implementation lives in `src/pycsl/exception_model.py`. The two
artefacts are kept in sync — any change to the trigger table requires
updates here, in the implementation, and in the corpus.

## Why a separate skill

The exception model is part of PyCSL's verification semantics — it
defines what "PyCSL guarantees about implicit Python exceptions" means
in practice. Burying it inside a Python source file would put the
contract under code-review rules rather than CCB review. Promoting it
to its own skill makes the contract auditable.

---

## Phase 1 — Trigger table

| Operation | IR shape | Exception | Trigger condition |
|---|---|---|---|
| `a / b` | `BinOp("/", a, b)` | `ZeroDivisionError` | `no_div_zero b` (i.e. `b <> 0`) |
| `a // b` | `BinOp("//", a, b)` | `ZeroDivisionError` | `no_div_zero b` |
| `a % b` | `BinOp("%", a, b)` | `ZeroDivisionError` | `no_div_zero b` |
| `divmod(a, b)` | `Call("divmod", [a, b])` | `ZeroDivisionError` | `no_div_zero b` |
| `arr[i]` (read) | `Subscript(arr, i, read)` | `IndexError` | `in_bounds (\length(arr)) i` |
| `arr[i] = v` (write) | `ArraySet(arr, i, v)` | `IndexError` | `in_bounds (\length(arr)) i` |
| `d[k]` | `MapGet(d, k)` | `KeyError` | `has_key d k` |
| `d.pop(k)` | `AttrCall(d, "pop", [k])` | `KeyError` | `has_key d k` |
| `1 << n`, `1 >> n` | `BinOp("<<"\|">>", a, n)` | `ValueError` | `non_neg_shift n` (i.e. `n >= 0`) |
| `s.index(x)` | `AttrCall(s, "index", [x])` | `ValueError` | placeholder `true` (Phase 2: `mem x s`) |
| `next(it)` | `Call("next", [it])` | `StopIteration` | placeholder `true` (Phase 2: iterator model) |

The authoritative encoding lives in `src/pycsl/exception_model.py` —
`KNOWN_EXCEPTIONS`, `TRIGGERS`, `PREDICATE_LIBRARY`. **Do not duplicate
the table into other files**; consult `triggers_for()` from
Module 4 and Module 6 instead.

## Rules for extending the table

A new entry is admissible when **all** of the following hold:

1. **Clean mathematical trigger.** The side condition is expressible in
   PyCSL's existing contract grammar (arithmetic + comparison + the
   bounded-by-length idiom). If the trigger depends on string content,
   unbounded heap, or a missing dataflow analysis, defer to Phase 2.
2. **Present in the PyCSL IR.** The operation must already be lowered
   to a concrete IR shape that Module 6 dispatches on. If the operation
   currently passes through Module 6 unchanged or via the auto-trust
   path, the IR has to gain a dedicated handler before the trigger is
   useful.
3. **Corpus coverage.** A new entry must ship with three corpus tests
   under `test-suite/corpus/pycsl-reference/`: baseline proves
   (no annotation), annotated_fails (annotation present, no
   precondition), annotated_with_precond (precondition strong enough
   to discharge). The numbering reservation for Phase 1 is
   `0353`–`0420`; new exceptions extend forward.

A new entry is **not** admissible when:

- The trigger requires modelling string content (`int("abc")` →
  `ValueError`). Defer to Phase 2 once string predicates exist.
- The trigger depends on type information PyCSL discards
  (`AttributeError` from a misspelled attr is largely pre-excluded by
  PyCSL's type checker today).
- The exception is system-level (`MemoryError`,
  `KeyboardInterrupt`, `SystemExit`). These are excluded by design and
  never modelled.

## WhyML predicate vocabulary

Emitted into the preamble when any function in the file declares a
`no_exception` clause (`PreambleEmissionMixin._emit_preamble_no_exception_predicates`):

```why3
predicate no_div_zero (b: int) = b <> 0
predicate in_bounds (n: int) (i: int) = 0 <= i /\ i < n
predicate non_neg_shift (n: int) = n >= 0
```

Predicate names are stable: changing one changes the meaning of every
proof obligation that references it. Treat additions as CCB-level
changes (extend the dict in `exception_model.PREDICATE_LIBRARY` and
document the addition here in the same PR).

The `has_key` predicate is **not** in this library — it is provided by
the existing ghost-dict vocabulary (`\has_key`, `\map_get`, `\map_set`),
so the `KeyError` trigger reuses that machinery rather than introducing
a parallel predicate.

## Inter-procedural rules

Default behaviour (workplan §1.4): unannotated callees are treated as
ambient — no implicit exceptions propagate to the caller's obligation.
Annotated callees flow as follows:

- Callee declares `no_exception E` (proved): the call site is safe with
  respect to `E`. No VC at the caller.
- Callee declares `raises { E -> P }`: the call site may raise `E` when
  `P` holds. If the caller declares `no_exception E`, Module 6 must
  emit `assert { not P }` at the call site.
- Callee declares neither (ambient): no VC at the call site, even if
  the caller has `no_exception E`. The `--strict-no-exception-propagation`
  CLI flag flips this conservative default to pessimistic.

The strict flag is **off by default** — preserving backward
compatibility for unannotated corpora.

## Test-corpus cross-references

Numbering blocks under `test-suite/corpus/pycsl-reference/` (reserved in
`test-suite/traceability-pycsl.md`):

| Block | Coverage |
|---|---|
| `0353`–`0357` | Parser support (recognition, rejection, unknown names) |
| `0358` | Preamble predicate emission |
| `0359`–`0365` | `ZeroDivisionError` trigger |
| `0366`–`0370` | `IndexError` trigger |
| `0371`–`0373` | `KeyError` trigger |
| `0374`–`0375` | `ValueError` trigger (shift, list.index) |
| `0376`–`0380` | Composite + edge cases |
| `0381`–`0390` | Inter-procedural propagation |
| `0391`–`0395` | `\all` form |

## Related skills and docs

- `config/skills/pycsl-annotate/SKILL.md` — annotator guidance for
  generating `no_exception` clauses.
- `config/skills/contract-writer/SKILL.md` — contract-writer agent's
  triggering rules for emitting `no_exception` (PR 3+).
- `docs/pycsl-concrete-syntax-reference.md` §2.1.13 — grammar.
- `docs/pycsl-static-semantics-reference.md` — formal proof obligation
  (added by PR 3).
- `docs/pycsl-translational-reference.md` §T.8 — WhyML emission rules
  (extended by PR 3).
