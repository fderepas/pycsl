# lvA chain census: proof2why3 cluster (run #5, batch lvA)

Base f10176e85. Method: port the verbatim live body into a scratch copy of the mirror
(`bin/port-one-mirror-body.py --convert [--replace]`), emit `--no-proof` (incl. the Why3 type-check)
on QUICK, read the first blocker; then either hand-patch it in the scratch copy (r2 specs) or build
the candidate capability in a scratch emitter (`st`, `st2`) and re-emit the VERBATIM body, until
TC-OK; then `--fun` (NORMAL) and an honesty read of the emitted body. Probe outputs:
`r1/` (first links, 22 emissions), `r3/` (verbatim bodies on the capability emitter), `f2/`-`f4/`
(`--fun` on `st2`). Witness drafts: `wit/`.

## Chain table

| stub | file | link 1 (cv8 first blocker) | link 2 | link 3 | link 4 | end state |
|---|---|---|---|---|---|---|
| `normalize_prover_output` | normalize | R325: `re.sub(.., count=1)` and `re.sub(<pat>, <lambda>, ..)` are opaque ints (cap-re-count, cap-re-callable) | L3-TC: `for u, a in _UNICODE_OPS.items()` / `for src, dst in _PREFIX_STRIPS` targets are `any int` (cap-pair-unroll) | TC-OK | -- | **CONVERTED** (`--fun` 9/9 Valid on st2) |
| `normalize_whyml_axiom` | normalize | R325 (callable lambda + `count=1`) (cap-re-callable, cap-re-count) | TC-OK | -- | -- | **CONVERTED** (`--fun` 4/4 Valid on st2) |
| `_expand_anon_binders` | normalize | R325: `pattern.sub(<lambda>, s, count=1)` on `pattern = re.compile(<lit>)` (cap-re-compiled + callable + count) | L3-TC: unbound `Return` -- the `while` arm wraps an int-payload `Return` catch inside a `-> str` function (emitter defect, VERIFIED twin `_handle_while_stmt`; fix spiked) | L3-TC: `while True:` with no tail has type `unit` (fix spiked: end in `absurd`, its own VC) | TERMINATION goal Unknown: a fixpoint `while True` over a law-free `re` op has no variant | **REFUSED** -- needs `#@ \diverges` (a contract weakening that propagates to its verified caller `normalize_prover_output`); left `\trusted` |
| `_nat_to_int_with_sidecond` | normalize | L3-TC int vs string: `pattern.sub(repl, s)`, `repl` a nested `def` (cap-re-compiled + named-def callable, spiked) | L3-TC: `val constant repl` vs the lifted `let repl` (fixed: callable arg never lowered) | `--fun` 1/1 Valid | honesty: the LIFTED `repl` becomes a verified `let` whose body is a facade (`m: re.Match` erased to int, `m_group_1 1` ignores `m`) | **REFUSED** (honesty: would put an input-blind lifted helper in the verified perimeter; needs a `re.Match` model) |
| `_alpha_rename` | normalize | `sorted(.., key=<lambda with a len call>)` | (sorted patched away) `re.match` -> opaque `Optional[Match]`, `.group(1).split()`, dict comprehension, `.items()` loop with str targets, `re.escape` in an f-string pattern | -- | -- | **REFUSED** (5+ links: Match/Optional, list-of-str split, dict model, sorted-key) |
| `normalize_surface` | parser | L3-TC: `_UNICODE_OPS.items()` / `_LIBRARY_PREFIX_STRIPS` targets `any int` (cap-pair-unroll) | L3-TC: `prev = None` then `prev = out` (int vs string) (cap-optstr-sentinel, spiked) | TERMINATION: fixpoint `while prev != out` over a law-free `re_sub_op` has no variant | -- | **REFUSED** -- needs `#@ \diverges` (weakening; its caller `parse_type_expr` is `\trusted`) |
| `_sexp_tokens` | sertop | TC-OK (a generator: each `yield` lowers to a discarded value) | needs loop variants (`n - i`; `n - j` x2 with `i + 1 <= j` / `i <= j`): `--fun` 20/20 Valid, whole-file sertop 41/41, mutation `i = j` -> `i = i` caught (variant) | plane `check-yield-erasure` RED (max 0 converted generators dropping yielded values) | -- | **REFUSED** (yield-erasure: needs a generator-sequence model; the annotated port is in this file's history) |
| `CrossCheckResult.diagnostic` | crosscheck | L3-TC: `for label, ok in self.pairwise.items()` over a property `Dict[str, bool]` lowered `map int (option int)` (no domain to iterate) | -- | -- | -- | REFUSED (vm-seam dict iteration) |
| `_load_axiom_registry` x2 | crosscheck, crosscheck_ir | L3-TC str erasure | body = `Path.read_text` + `ast.parse` / `ast.walk` / `literal_eval`: all opaque | -- | -- | REFUSED (honesty: input-blind facade) |
| `crosscheck_file` / `crosscheck_file_ir` | crosscheck, crosscheck_ir | `sorted(key=)` | subprocess-driven extractors, `Path.glob`, dict-of-str model | -- | -- | REFUSED (cost + honesty) |
| `IRCrossCheckResult.diagnostic` | crosscheck_ir | R489 implicit dunder (`.pp()` / `Token.__repr__`) | -- | -- | -- | REFUSED (frame of an implicit dunder) |
| `extract_rocq_statements` / `extract_lean_statements` | extract | definite assignment through `with ... as tf` | `subprocess.run` / `tempfile` / `Path.unlink`: all opaque | -- | -- | REFUSED (context-manager model, then honesty) |
| `from_sexp` x4, `from_lean_json` x3 | from_sexp, from_lean_json | vm-seam on `Any`-typed s-expression tuples / dicts; `args.insert` mutator; nested param rebind | -- | -- | -- | REFUSED (vm-seam family, cv8 rows unchanged) |

## Set cover

Capabilities built (all emitter-local, law-free, axiom-free):

- **cap-re-count** -- `re.sub(<pat>, <str repl>, <str>, count=<int literal>)` -> `val function
  re_sub_count_op (pat rep s: string) (count: int) : string` (deterministic, no content law).
- **cap-re-callable** -- `re.sub(<pat>, <closed pure 1-param lambda>, <str> [, count=k])` -> PLAIN
  `val re_sub_callable_op (pat s: string) : string` (no determinism, no content law); the lambda
  body is dropped exactly as the `sorted(key=<lambda>)` body (route #275), and it is never lowered.
- **cap-re-compiled** -- `<v>.sub(..)` where `<v>` is bound exactly once, by `<v> = re.compile(<str
  literal>)`, and its name occurs nowhere else in the function.
- **cap-pair-unroll** -- `for k, v in NAME.items()` / `for a, b in NAME` over a module-constant
  str->str dict literal / list-tuple of str 2-tuples, never aliased / mutated / rebound and read only
  as that iterable (Module 5 `module_const_str_pair_loops`), UNROLLED over the real pairs.

Cover: {re-count, re-callable, pair-unroll} covers `normalize_prover_output` + `normalize_whyml_axiom`
completely (cap-re-compiled is built and witnessed but its only consumers here are blocked further
down). 2 conversions. `_sexp_tokens` (no capability, loop variants only) proved but is refused by the
yield-erasure plane.

Spiked but NOT landed (no conversion consumes them in this batch): the `_handle_while_stmt`
`Return_str` / `absurd` fix (VERIFIED twin: would owe the stmt_control_flow whole-file proof),
the Optional[str] sentinel local, the named-`def` callable repl. Their only consumers
(`_expand_anon_binders`, `normalize_surface`, `_nat_to_int_with_sidecond`) are blocked by
termination (`\diverges`) or honesty, recorded above. Patch: `scratchpad/lvA/unlanded.patch`.

Side finding: `--fun` on the parser.py mirror fails at the Why3 parse (`unexpected 'variant'
clause`: a `val _parser__parse_quant` stub emitted with a `variant`), independent of this batch.
