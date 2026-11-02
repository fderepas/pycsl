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

## Trigger table

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
| `s.index(x)` | `AttrCall(s, "index", [x])` | `ValueError` | placeholder `true` (deferred: `mem x s`) |
| `next(it)` | `Call("next", [it])` | `StopIteration` | placeholder `true` (deferred: iterator model) |
| `str(x)` / `repr(x)` / `print(x)` / `f"{x}"` / `"%d" % x`, `x` an int | `("call", "int_str")` at each decimal conversion site | `ValueError` | `-10**4300 < x < 10**4300` (CPython 3.11+ 4300-digit limit, route #281; asserted on the operand). An f-string part with a literal spec owes it when the spec's presentation type is none/`d`/`n` (`:d`, `:5`, `:05d`, `:n`, `:,`, `:>10`) or a `!s`/`!r`/`!a` conversion is present (route #284) |
| `f"{v:spec}"` with a spec INVALID for `v`'s type (`f"{x:s}"`, `f"{x:.2}"` on an int, `f"{s:d}"` on a str), a COMPUTED spec `f"{x:{w}}"`, `"%q" % x` (any `%` format CPython's `%` rejects, or a non-literal format) | `("call", "format_spec")` | `ValueError` | `false` — validity of a literal spec/format is decided at emit time by CPython's own `format()` / `%` on a sample of the operand's type (value-independent for int and str; an operand not shown to be an int must satisfy both int and str); invalid or undecidable owes `false` (route #284) |

**Comprehension census (route #285).** A comprehension / generator expression is lowered as an
opaque value, so none of the rows above is injected for its element, key, value, condition or
iterable. `exception_model.TRIGGER_EXPR_SHAPES` records, for EVERY `TRIGGERS` row, the expression
shapes that reach it (`("BinOp", op)`, `("Subscript", "")`, `("Call", name)`, `("Method", name)`,
`("FString", "")`, `("FormattedValue", "")`; an empty list = statement-only: element store,
`del`). Under an active `no_exception`, `_reset_function_state` refuses a comprehension containing
a shape of a row whose exception is active, and a `TRIGGERS` row with NO census entry refuses every
comprehension under its exceptions — so a row added later is fail-closed until it is censused.
**Adding a row therefore also means adding its `TRIGGER_EXPR_SHAPES` entry.**

**Site census (route #506).** The rows are injected by the operation's expression HANDLER
(`_handle_binop` / `_handle_subscript` / `_handle_call_expr` / `_handle_fstring_expr`), so an
enclosing expression the emitter models by size or truth only (a set / tuple / starred display,
`len(<display>)`, `isinstance(...)`, an `assert` test under a named claim) silently dropped them —
and, in an un-claimed body, dropped the raising `pycsl_div` / bounds VC a caller's handler relies on.
`pycsl._run_pipeline` observes those handlers during `transpile()` and refuses
(`PYCSL-R506-TRIGGER-SITE-UNLOWERED`) any `TRIGGER_EXPR_SHAPES` site of a verified body whose
exception is claimed (declared / reached) or catchable in the file (a handler that catches it, a
bare / unknown handler, `finally`, `with`) and whose lowered text is absent from the def's emitted
block. The same table drives it: **a new row's shapes are censused there too.**

**OverflowError sites of `\all` (routes #507 / #508 / #509).** The OverflowError obligations that
`no_exception \all` alone carries are NOT `TRIGGERS` rows: route #414 (`s * n`, `[x] * n`,
`len(range(..))`) and route #417 (`list` / `sorted(range(..))`, `float(<int>)`) are inline asserts
in `_handle_binop` / `_handle_call_expr`. Right after #506's census, `_run_pipeline` reads every
operand of a `\all` body (declared or reached) at a numeric kind (small int literal / int / float /
non-number / unknown: IR symbol table + SOURCE annotations + comprehension targets + single-kind
locals) and refuses: an arithmetic op mixing a float with an int / unknown operand, anywhere
(`PYCSL-R508-INT-FLOAT-PROMOTION-UNMODELLED`: the int -> float conversion owes |n| <= DBL_MAX and
has no lowering); such a site inside a comprehension / generator / lambda
(`PYCSL-R509-COMPREHENSION-OVERFLOW-SITE`); elsewhere, a site whose handler text (or #417 tag) is
absent from the def's block (`PYCSL-R507-OVERFLOW-SITE-UNLOWERED`). **A new `\all`-only obligation
attached inline by a handler needs its site shape added to that table too.**

**Refuse by default (routes #512-#516).** That table reads values, not spellings: a
`len` / `list` / `sorted` / `bytes` of ANY value that may be a range (bound to a name, through a walrus /
if-expression / container element, a `Sequence` / `Iterable` / undeclared parameter) and a `*`
unpacking of one are sites; `bytes(x)` / `bytearray(x)` (count or list) are sites; a repetition /
range-length / byte-count site is credited only by a lowering that STATES the Py_ssize_t bound. Kinds
come from the TOP-LEVEL type arguments (a mapping iterates its keys), the receiver's class (method
results, fields) and imported user modules; an operand of unknown kind that is OPAQUE (a call / field /
loop-target / unpacked value) beside an int or another unknown is refused like a float (R508); an
immediately-invoked lambda under `\all` is `PYCSL-R515-IMMEDIATELY-INVOKED-LAMBDA`; route #315 no longer
counts `bytes(x)` / `len(range(<non-literal>))` as total in a constructor. annotations §7.512.

The authoritative encoding lives in `src/pycsl/exception_model.py` —
`KNOWN_EXCEPTIONS`, `TRIGGERS`, `PREDICATE_LIBRARY`. **Do not duplicate
the table into other files**; consult `triggers_for()` from
Module 4 and Module 6 instead.

## Rules for extending the table

A new entry is admissible when **all** of the following hold:

1. **Clean mathematical trigger.** The side condition is expressible in
   PyCSL's existing contract grammar (arithmetic + comparison + the
   bounded-by-length idiom). If the trigger depends on string content,
   unbounded heap, or a missing dataflow analysis, defer it.
2. **Present in the PyCSL IR.** The operation must already be lowered
   to a concrete IR shape that Module 6 dispatches on. If the operation
   currently passes through Module 6 unchanged or via the auto-trust
   path, the IR has to gain a dedicated handler before the trigger is
   useful.
3. **Corpus coverage.** A new entry must ship with three corpus tests
   under `test-suite/corpus/pycsl-reference/`: baseline proves
   (no annotation), annotated_fails (annotation present, no
   precondition), annotated_with_precond (precondition strong enough
   to discharge). The numbering reservation is `0353`–`0420`; new
   exceptions extend forward.

A new entry is **not** admissible when:

- The trigger requires modelling string content (`int("abc")` →
  `ValueError`). Defer it until string predicates exist.
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

Default behaviour: unannotated callees are treated as ambient — no
implicit exceptions propagate to the caller's obligation. Annotated
callees flow as follows:

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

"Ambient" covers IMPLICIT exceptions only. An EXPLICIT `raise` the
callee does not declare is refused at a `no_exception` caller when the
call cannot see it (route #272, `PYCSL-SEM-UNDECLARED-CALLEE-RAISE`,
inline in `pycsl._run_pipeline`): method calls lower to a stub carrying
declared `raises` only (and only for `self.`/class-bound variable
receivers — not `C.m()` / `C().m()`), and the hidden set propagates
transitively through methods and module functions.

The function's OWN explicit `raise` is not ambient either (route #304):
an escaping `raise E` covered by the function's declared `no_exception`
(`\all`: any class; named: the class or an ancestor, user class bases
included) is a reachability obligation at the raise (`try ... with E ->
assert false; absurd`), never an inferred `raises { E }` on its own `let`.
Corpus 3720-3732 (FAIL), 3733 (controls).

Exception classes are identified by NAME (the WhyML tag is the bare name and
`handler_catches` reads `EXCEPTION_BASES` by name), so a program may not BIND
a builtin exception name itself (route #305): a user `class KeyError(Exception)`
(any depth), or a def / import / assignment / parameter / `except ... as`
binding of a name in `EXCEPTION_BASES ∪ KNOWN_EXCEPTIONS ∪ {EnvironmentError,
IOError}`, in the main file or an imported module, is refused
(`PYCSL-R305-BUILTIN-EXCEPTION-NAME-SHADOWED`). Corpus 3780-3786 (refused),
3787-3789 (controls).

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
  triggering rules for emitting `no_exception`.
- `docs/pycsl-concrete-syntax-reference.md` §2.1.13 — grammar.
- `docs/pycsl-static-semantics-reference.md` — formal proof obligation.
- `docs/pycsl-translational-reference.md` §T.8 — WhyML emission rules.
