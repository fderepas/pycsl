# Implementation plan: map Python `str` to Why3 `string` (real string semantics)

## Context

PyCSL currently has a **dual, half-real string model**:

- **Runtime `str` variables/parameters/returns** → modeled as `int` (a `hash(s) % 2147483647`).
  Opaque: no content, no length, no characters, no content-equality (only identity-by-hash,
  with theoretical collisions). `τ(str) = int` (docs/pycsl-static-semantics-reference.md §1.4).
- **Ghost strings** (`#@ ghost s : string = …`) + string literals *in a string context* →
  real Why3 `string` (`ref string`; literals `"..."`). The operators `\str_length` /
  `\str_sub` / `^` lower to `String.length` / `String.substring` / `concat` and **already prove
  under SMT** (corpus `0292`/`0298`/`0304`/`0321`/`0329`/`0336`; `0292` discharges
  length+concat over a loop, Valid in 0.01s).

So the machinery for *real* strings exists and is proven — it is just walled off in the ghost
world. The gap: a runtime `str` parameter is an int hash, so you cannot compute `len(s)`,
`s + t`, `s[i]`, `s[a:b]`, or content `s == t` on it; there is no character extraction at all.

**Goal:** promote the runtime `str` type to the *same* Why3 `string.String` model the ghost
layer already uses — collapsing the dual model into one — so `str` parameters/locals/returns
carry real content and the core string operations are verifiable.

This is a **feature**, not a refactor: by design it **changes emission** for every `str`-using
file (a `str` literal stops being an int hash, a `str` param becomes `string`). The
emission-identical differential therefore does **not** apply as a gate; it is used in reverse —
to *enumerate* exactly which files change and confirm each still proves.

## Gating — do not build until BOTH hold (folded-in self-critique)

A first review of this plan exposed that it was gated on the *wrong* thing (technical
feasibility alone). Per the project's own demand-driven discipline (from `act`/HAPPY:
*"demand-driven and measurable, not justified by the category"*), two gates must pass before
any implementation:

- **Gate A — a named demand-driver.** A concrete program PyCSL cannot verify today *because*
  runtime strings are opaque. The driver is **substring / pattern search**, captured as the
  key reference test **`test-suite/corpus/pycsl-reference/0471.py`** (`find_pattern(haystack,
  needle)` — return a matching index or −1, with a `\str_sub(...)==needle` postcondition). It is
  committed **`# pycsl-expected: FAIL`** (today it errors: runtime `str` slicing emits
  `unbound type symbol 'array'`). The feature is "done enough to justify itself" precisely when
  `0471` flips to PASS. The full per-operation acceptance suite is `0471`–`0489` (see
  "Reference-test suite" below). *If no real program needs string-content reasoning, do not
  build this — the original trigger was a docs confusion (`τ(str)=int`), fixable as a docs problem.*
- **Gate B — content-level SMT proof, probed first.** `0292` shows *length algebra* proves, but
  that is the SMT-easy 20%. The make-or-break is **content reasoning** — substring equality, the
  `0471` postcondition `\str_sub(haystack, r, r+\str_length(needle)) == needle`. Stage 0 must
  prove *that* (by hand, in WhyML) **before** anything else, so the plan fails fast rather than
  greenlighting on length algebra and discovering content reasoning needs a full Rocq/Lean
  theory (Stage 4). If content-equality won't discharge without heavy hand-proof and there is no
  Gate-A driver, **keep the dual model and just document it**.

## Reference-test suite — per-operation demand drivers (`test-suite/corpus/pycsl-reference/`)

The plan must be backed by **more reference tests than the single driver** — one per string
operation the feature is meant to enable, so the corpus *is* the acceptance suite (and Gate A
is satisfied operation-by-operation as each flips PASS). These are committed
`# pycsl-expected: FAIL` today (runtime `str` is an int hash) and each flips to PASS exactly
when its operation lands and proves. Per the PyCSL new-feature discipline, **every operation
that ships in a later stage must add/repurpose its corpus test here, plus a negative** (e.g. an
out-of-range `s[i]`).

Committed driver suite (Python string magic methods that have *verifiable string-content*
semantics):

| Test | Dunder | Operation |
|---|---|---|
| `0471` | (search) | substring/pattern search — the flagship driver |
| `0472` | `__len__` | `len(s)` → `\str_length` |
| `0473` | `__getitem__` | slice `s[a:b]` → `\str_sub` |
| `0474` | `__contains__` | `needle in haystack` (bool; existential — hard SMT goal) |
| `0475` / `0476` | `__eq__` / `__ne__` | content `==` / `!=` |
| `0477`–`0480` | `__lt__`/`__le__`/`__gt__`/`__ge__` | lexicographic — **stretch** (no code points ⇒ may stay unsupported) |
| `0481` | `__add__` | concat `s + t` (length additive) |
| `0482` / `0483` | `__mul__` / `__rmul__` | repetition `s * n` / `n * s` |
| `0484` | `__mod__` | `s % x` formatting (content opaque — boundary marker) |
| `0485` | `__hash__` | `hash(s)` |
| `0486` | `__str__` | `str(s)` (identity) |
| `0487` | `__repr__` | `repr(s)` (content opaque — boundary marker) |
| `0488` | `__format__` | `format(s)` (identity; f-strings desugar here) |
| `0489` | `__iter__` | `for c in s` (visits each char; count == length) |

**Deliberately NOT given tests** (no verifiable string-content semantics in PyCSL — they are
object/attribute/class machinery, not string operations; some raise at runtime): `__new__`,
`__init__`, `__getattribute__`, `__setattr__`, `__delattr__`, `__dir__`, `__init_subclass__`,
`__subclasshook__`. (Also excluded per the source list's own "Notable Omissions": `__bool__`,
`__iadd__`, `__reversed__`, `__int__`/`__float__` — these are fallbacks/conversions, not string
ops.) `__rmod__` is excluded too: it only returns `NotImplemented` (an internal fallback), so
there is nothing to verify.

## Disciplines applied (from `csl-from-scratch` / how-to-develop)

- **Verify the target primitive's real semantics first** (Stage 0): before lowering `str` onto
  `string.String`, confirm Why3 + the SMT backend can actually discharge the goals we will
  generate. `0292` proves length+concat; the spike extends this to substring/index/equality.
- **Value-semantic ⇒ memory-model-independent.** Python strings are immutable values and Why3
  `string` is a value type — no heap, no aliasing. So `str` handling is identical across
  hoare/concurrent/typed/store (unlike arrays). One code path, not four.
- **Desugar to existing primitives; 0 `\trusted`.** Reuse the existing string-context emitter,
  `_ghost_string_vars`, and the `\str_*` lowerings; do not add a new backend theory beyond
  Why3's `string.String` (+ possibly `string.Char`, gated on Stage 0).
- **Demand-driven scope.** Ship the core (len/==/+/slice/index/substring) first; add string
  *methods* only as concrete corpus demand appears.
- **5-surface doc-coherency + reference corpus + determinism** on every change.

## Stage 0 — SMT-feasibility spike (the gate)

A read/measure step producing a written go/no-go + the supported-operation set. **Probe the
content-level goals FIRST** (item 4 + the `0471` substring-equality postcondition) — those are
the make-or-break per Gate B; `0292`'s length+concat are already known-easy, so leading with
them would manufacture false confidence. If content equality needs a heavy hand-proof, stop here
(Gate B fail). Then, in order of decreasing risk, hand-write `.mlw` (and tiny PyCSL files)
exercising each operation we intend to lower and record what Alt-Ergo/Z3 discharge vs time out:

1. `String.length`, `concat` — **confirmed provable** (0292). Re-confirm `length (concat a b) =
   length a + length b` and `length "" = 0`.
2. `String.substring s lo (hi-lo)` — prove a bounds-guarded substring length:
   `0 <= lo <= hi <= length s ==> length (substring s lo (hi-lo)) = hi - lo`.
3. **Indexing** `s[i]` modeled as `substring s i 1` (a length-1 string — Python returns a 1-char
   `str`, *not* a char, so **avoid a `char` type entirely**). Prove `i < length s ==> length (s[i]) = 1`.
4. **Content equality** `s == t` → `s = t` (Why3 structural `=` on `string`). Confirm the SMT
   backend reasons about it (reflexivity, `concat`/`substring` rewrites).
5. Identify which Why3 string library is available (`string.String` substring/length/concat are
   in use; check whether `string.Char`/`get`/`code` exist in this Why3 version — only needed if
   we ever expose code points, which the 1-char-substring model avoids).

**Outcome:** the set of operations that prove directly defines Stage 2's surface. Anything that
does **not** prove under SMT is either (a) deferred, or (b) backed by a cited Rocq/Lean string
lemma (Stage 4), exactly like the gcd cross-validated-spec pattern. **YAGNI exit:** if only the
already-working ghost subset proves and nothing new does, do *not* promote runtime `str` — keep
the dual model and just document it.

## Stage 1 — Type runtime `str` as Why3 `string`

Collapse the dual model: a `str` value is a Why3 `string` everywhere (no int hash).

- **Type mapping** `τ(str) = string` (a real universe member):
  - `Module4_SemanticAnalyzer._get_type_name` already returns the raw `str` tag; add `string` to
    the recognised value types.
  - `module6_whyml/functions.py`: `_param_type_str` / `_symtype_to_whyml` / `_return_type` map
    `str` → `string` (today they fall through to `int`). A `str` return is `: string`.
- **String literal in body/value context** → `"<raw>"` (real Why3 string), **not** the int hash.
  Unify the two `_expr_to_whyml` String branches (`expressions.py:~1496` body-hash vs
  `_expr_to_whyml_string_ctx` literal) into one literal emission. The "string context" notion
  largely disappears — every `str` expression is a string.
- **Preamble:** emit `use string.String` whenever any `str` is present (extend the existing
  `needs_string` trigger to runtime `str`, not just ghost strings).
- **Collapse `_ghost_string_vars`:** runtime `str` params/locals join the same "is-a-string"
  set, so the existing string-context emission (deref/literal/concat) applies uniformly.
- **Ghost-tainting:** with `str` value-typed (not the ghost heap), a `str`-returning function is
  a normal value function — no `must be marked ghost` issue (contrast the typed/store heap).

## Stage 2 — Core operations on runtime strings

Each gated on Stage 0 proving it. Lower in Module5 (IR) + Module6 (WhyML), reusing the ghost
lowerings:

| Python | IR | WhyML | Notes |
|---|---|---|---|
| `len(s)` (s:str) | `StrLength`/`ArrayLen`→str | `(String.length s)` | unify with `\str_length` |
| `s == t` / `s != t` | `BinOp ==`/`!=` over str | `(s = t)` / `(not (s = t))` | content equality (replaces hash) |
| `s + t` (str+str) | `StrConcat` | `(concat s t)` | detect str-typed operands; today `+` on str is int-add (wrong) |
| `s[a:b]` | `StrSub`/`Slice` | `(String.substring s a (b - a))` | half-open; bounds obligation |
| `s[i]` | `StrIndex` (new) | `(String.substring s i 1)` | length-1 string (Python semantics; no char type) |
| `"…"` literal | `String` | `"…"` | Stage 1 |
| `\str_length`/`\str_sub`/`^` | (existing) | (existing) | now also valid on runtime `str`, not only ghost |

Operand-type detection (str vs int) for `+`, `==`, `len`, subscript reuses the symbol-table type
tags (`str` now flows through Module5's type tracking). Bounds side-conditions for
`substring`/index follow the `\valid`/no_exception pattern (a guarded obligation).

## Stage 3 — String methods (scoped, demand-driven)

- **Keep uninterpreted-bool** (already correct): `s.startswith`/`endswith`/`islower`/… stay
  `*_check : bool` abstract ops — unless a corpus case needs a *content* spec, in which case
  model e.g. `startswith` via `substring`.
- **Defer** `upper`/`lower`/`find`/`replace`/`split`/`strip` to abstract ops until demanded;
  document them as opaque. Do not block the core feature on the full method surface.

## Stage 4 — Proof / axiom layer (only if Stage 0 found gaps)

For any string property the SMT backend cannot discharge directly (e.g. nontrivial
`substring`/`concat` algebra), add a cited lemma via `#@ proof rocq|lean <qualname>` against
`<file>.proofs/{rocq,lean}/`, reusing the **Rocq+Lean cross-validated spec sources** mechanism
(annotations.md §2.1.12; the gcd template `0342`). The string lemmas live in a small reusable
theory. 0-`\trusted` preserved.

## Stage 5 — Docs, corpus, gates

- **Type-mapping reversal:** update `τ(str)` from `int` to `string` across the normative
  surfaces — `docs/pycsl-static-semantics-reference.md` §1.4 (the row we just added) and the
  `docs/pycsl-translational-reference.md` τ-table; document the new string operations in
  `test-suite/annotations.md` (§3 expression language — `len`/`+`/`[]`/`==` on str, the `\str_*`
  unification) and `docs/pycsl-concrete-syntax-reference.md`. Refresh the string limitations text
  in `config/skills/pycsl-annotate/` (the no-char-extraction caveat softens to "`s[i]` = 1-char
  substring"). `bin/doc-coherency.py --check` green.
- **Reference corpus** (`test-suite/corpus/pycsl-reference/`, per the new-feature requirement):
  add proving demos — string length (`len(s)` / `\str_length`), concat (`s + t` length algebra),
  slice/index (`s[a:b]`, `s[i]` length), content equality (`s == "foo"`), and a **negative**
  (e.g. an out-of-range `s[i]` whose bounds obligation fails). Keep the existing ghost-string
  tests (0292 etc.) passing under the unified model.
- **Emission re-baseline:** because `str` emission changes by design, run the corpus WhyML
  differential to **enumerate** the changed files (they will be exactly the `str`-using ones),
  and re-prove each under the new model. No surprises outside `str` users.
- **Per-feature gates:** `audit-pycsl-language --quick`; SY3 mod-index regen; `make rag-build` +
  `rag-verify`; full `run-reference-tests.sh` (PYTHONHASHSEED=0). Cross-validation proofs
  re-audited (`pycsl --audit-proof`) if Stage 4 adds any.

## Critical files

- `src/pycsl/Module4_SemanticAnalyzer.py` — `τ(str)=string` in `_get_type_name`; any str scope/
  validation.
- `src/pycsl/Module5_IREmitter.py` — str type tracking; literal IR; new `StrIndex`; `+`/`==`/
  `len`/subscript over str-typed operands.
- `src/pycsl/module6_whyml/functions.py` — `_param_type_str` / `_symtype_to_whyml` / `_return_type`
  → `string`.
- `src/pycsl/module6_whyml/expressions.py` — unify the String-literal branches; `_handle_strconcat`/
  `_handle_str_length`/`_handle_str_sub` now reachable from runtime str; new index handler;
  str-aware `+`/`==`/`len`.
- `src/pycsl/module6_whyml/preamble.py` — `use string.String` triggered by runtime str.
- `test-suite/corpus/pycsl-reference/` — new string demos + negative.
- 5 doc surfaces + `config/skills/pycsl-annotate/`.

## Verification (end-to-end)

1. **Stage 0 written verdict**: each intended op proves by hand under Alt-Ergo/Z3, or is routed
   to Stage 4 / deferred. (0292 already covers length+concat.)
2. **Core ops**: corpus demos for `len`/`+`/`[a:b]`/`[i]`/`==` prove; the negative (bad index)
   fails at its bounds obligation; ghost-string tests (0292 …) still prove under the unified model.
3. **Differential**: the set of files whose WhyML changed = exactly the `str`-using set; every one
   re-proves. Non-`str` corpus byte-identical.
4. **Gates**: doc-coherency (5 surfaces incl. the `τ(str)` reversal), audit-pycsl-language, SY3
   mod-index, rag-build/verify, full run-reference-tests.

## Risks & open decisions

- **SMT string-theory depth (primary risk).** Basic ops prove (0292), but `substring`/`concat`
  algebra may exceed Alt-Ergo/Z3 — Stage 0 measures this, Stage 4 (Rocq/Lean lemmas) backstops it.
  If even the core won't prove, take the YAGNI exit and keep the dual model.
- **Backward compatibility / semantics change.** Content equality replaces hash-identity: this
  *fixes* the latent hash-collision unsoundness but changes behavior for any test that leaned on
  the int-hash model (e.g. using a string as an int). The differential enumerates the blast
  radius; each must be re-proved or migrated.
- **Character model.** Recommended: `s[i]` ≜ `substring s i 1` (a length-1 string), **no `char`
  type, no code points** — matches Python (`s[i]` is a `str`) and avoids `string.Char`. Only
  revisit if a use case needs numeric code points (`ord`).
- **`bytes`/`bytearray` stay separate** (array-int byte buffers); `str.encode()` → bytes is the
  bridge and remains the existing abstract op. Do not fold bytes into the string type.
- **Immutability.** No string-mutation ops (Python strings are immutable) — keeps the value model
  clean; any `s += t` is `s = concat s t` (rebinding), not in-place.
- **Doc reversal.** This plan reverts the recently-documented `τ(str) = int`; that row described
  *current* reality and is correct until Stage 1 lands. Update it as the final doc step, not before.
- **Proof-time regression (unbudgeted).** String theory is far heavier for SMT than integer
  arithmetic; files that prove in ~0.01 s as int-hashes may slow sharply or time out as real
  strings, worsening the already ~1–2 h `run-reference-tests` sweep. Stage 0 should also record
  *timing*, not just Valid/Invalid, and the differential re-proof must watch for new timeouts.
- **"Good enough" today for the common case.** Most string use is opaque tokens/keys where only
  identity matters — int-hash serves that cheaply, and real strings tax SMT even for programs
  that never reason about content. The win (content soundness + verifiability) must outweigh this
  tax — which is exactly what Gate A (a real content-reasoning driver) tests.
- **Missed interaction — string dict keys.** Dicts are modeled `map int (option int)` with int
  keys; a string-keyed dict (`d["foo"]`) currently keys on the int hash. If `str` becomes Why3
  `string`, string-keyed dicts need `map string …` (or to keep hashing keys) — a lowering
  decision this plan must settle before Stage 1, not discover during it.
- **`s[i]`-substring model is still limited (may oversell "real strings").** With no code points:
  no `ord`, no character ordering (`s[i] < "b"`), no char-frequency/parsing-by-codepoint
  algorithms. So even after the feature, character-level reasoning stays out of reach — set
  expectations accordingly in the docs.
- **Scope-creep gravity.** Once `str` looks real, demand follows for `.split`/`.find`/`.replace`/
  `.format`, f-strings, Unicode, regex — each SMT-hostile and a mini-project. f-strings/format in
  particular are ubiquitous in real Python and out of scope, capping adoption. Hold the line on
  demand-driven scope (Stage 3).
- **Opportunity cost / the docs-fix alternative.** This is a multi-week, Module4/5/6 + docs +
  corpus (+ possibly a verified string theory) effort. The issue that *triggered* it was a docs
  confusion (`τ(str)=int`), which a clear "string model" doc subsection fixes in an hour. If Gate
  A has no driver, prefer the docs fix over the backend rewrite.

## Out of scope (deferred)

Full `str` method library (`find`/`replace`/`split`/`format`/case ops) beyond uninterpreted
predicates; regex; Unicode/code-point reasoning; `bytes`↔`str` codec content modeling; f-strings.
