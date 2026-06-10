# c-front.md — CCSL: an LLVM/Clang-based C front-end for the PyCSL core (rev. 6)

**Date:** 2026-06-10 (rev. 6)
**Status:** High-level specification (for review — no code changed)
**Owner:** [FRONTEND-C] (`src/ccsl/`) + **[CORE]/[FRONTEND-PY] for the §13 prerequisites** — rev. 5 is
the first revision in which the C front-end deliberately asks for core/PyCSL changes (decided below).
**Origin:** `refactor.md` (the seam + laws); `ir.md` (the wire contract).
**Rev. 5 changes — the §12 choices are decided (user review):**
`loop assigns` → **core feature** (12.1b); annotation macros → **full preprocessing** (12.2c);
unsigned → **per-function pragma** (12.3); `\at` → **user C labels** (12.4); binders → **typed, in
BOTH dialects** (12.5 ***); trailing `;` → **warn-accept** (12.6); out-params → **borrow-shaped
model as the end state** (12.7 ***); division → **non-negative guard, status quo** (12.8);
invocation → **`compile_commands.json`** (12.9); uninitialized locals → **taint-style ghost flag**
(12.13); UB source of truth → **the Earnestly C-UB list** (12.14); target-model JSON → **full schema
now — endianness, sizes, padding — because low-level code uses them** (remark 16). A new **§13**
lists what must change in PyCSL **before** (or alongside) the C front-end.

**Rev. 6 change:** **O-1…O-4 are resolved by adopting Frama-C/ACSL practice:** strings stay
char/byte arrays with `\valid_string` + an axiomatized logic `strlen` (no abstract string type);
`\valid` takes ACSL's `p+(lo..hi)` range form — *total* under the whole-array model, dissolving the
rev. 4 partial-sugar objection; quantifier binders are always typed, with ACSL's mathematical
`integer`; and uninitialized reads surface as ACSL's `\initialized`, generated RTE-style —
uniformly, never suppressed (no peephole).

---

## 1. Goal, and the one-line architecture

**Goal.** A thin C front-end that ingests annotated C (preprocessed as configured, §9) and emits the
**resolved PyCSL IR** (`ir.md`; v1.2 once §13's additive fields land), such that the shared core
lowers it to WhyML and proves it. Success = `ir.md` §9's obligations checklist + the Phase-E pattern:
a `c-source → expected-IR` corpus passing with **no core imported**, plus end-to-end drivers through
the real core.

```
 C source + compile_commands.json + target-model JSON
   ──▶ C1 Ingest (libclang TU per compile-commands entry; target-model consistency check)
   ──▶ C2 Annotation extraction (//@ runs, 4-space blocks, positions; skipped-#if regions dropped)
   ──▶ C3 Clause parsing (act vocabulary; C-expression grammar; annotation text PREPROCESSED §9)
   ──▶ C4 Weave (attach runs by source position; FAIL-LOUD on orphans)
   ──▶ C5 IR construction (cursor-kind visitor; default = loud reject; UB policy §6; taint §6)
   ──▶ validate_ir + canonical JSON  ──▶  THE CORE (with the §13 additions)
```

**Reuse picture:** shared — the carrier protocol, the IR-construction patterns, the target IR
(`&&` → `BinOp "and"`, `\at` → `At`, acts → `acts`/`act_name`). Forked — C3's expression grammar is
C. **New in rev. 5:** the front-end is no longer required to leave the core byte-frozen; instead the
§13 prerequisites land **first, gated in the PyCSL repo by its own corpus rules**, and the C
front-end then targets the upgraded core. (Acceptance #1 is restated accordingly: the core changes
are §13's and *only* §13's.)

## 2. The annotation language — act vocabulary, C expressions, PyCSL carrier

| Surface | Lowering target |
|---|---|
| `requires E` / `ensures E` / `assigns L` | `contracts.*` |
| `act name:` + indented `given E` / `ensures E` / `assigns L`; `complete`/`disjoint n1, n2` | `acts` entries; `act_name`-tagged clauses |
| `loop invariant E` / `loop variant E` | `While/For.invariants/variants` |
| `loop assigns L` | **the IR's loop-`assigns` field (§13 P-3)**; Module 6 synthesizes the preservation reasoning — a platform feature, not a C-side desugar |
| `assert E` / `check E` / `ghost …` | `ProofAssert` / `GhostAssign`/`GhostArraySet` |
| `\result`, `\old(E)`, `\at(E, L)` with **L ∈ {Pre, Old, Here, LoopEntry} ∪ user C labels** (§13 P-4) | `Result`, `Old`, `At` (+ `Label` nodes emitted at C label positions) |
| **`\valid(p+(lo..hi))`** (ACSL range form; `\valid(a, n)` kept as the `0..n-1` alias; `\valid_read` an alias — writes are `assigns`'s job), `\length(a)`, `\separated`, … | total under the whole-array model: `0 <= lo && lo <= hi && \length(a) >= hi+1` → `Valid`/`ArrayLen`; the rev. 4 partial-sugar objection dissolves |
| **`\valid_string(s)`**, logic **`strlen(s)`** (Frama-C libc style) | desugared over the byte array: a NUL exists, none before it (`Exists`/`Forall` + `Valid`); `strlen(s)` denotes that index |
| **`\initialized(x)`** (ACSL) | the §6 taint flag: `x__init == 1` |
| **typed binders — mandatory, ACSL-style**: `\forall integer k; E` (mathematical) / `\forall int k; E` (C type → desugars to `integer` + the type's range as `domain`) | `Forall/Exists`, `binder_type` always filled; `integer` ↦ IR `"int"` (§13 P-1 aligns PyCSL) |
| markers: `trusted`, `abstract`, `no_inline`, `lemma`, `uses`, `interface`, `reveal`, `bounded_int N`, **`unsigned wrap|strict`** (§5) | `FunctionIR` fields |
| **expressions** | C syntax: `&& \|\| ! == != < <= > >= + - * / % << >> & \| ^ ?: ==>`; `p->f`/`s.f`; hex/suffixed literals; **macros usable (§9)** |

**Carrier rules:** `//@` only (`/*@` warns as ordinary comment); content = text after `//@` minus one
space; consecutive lines = a run; 4-space levels = nesting; tabs hard-error; **orphaned runs
hard-error** (the blank-line silent-drop is structurally impossible); **one trailing `;` per clause
is accepted with a warning** (12.6 resolved — silent acceptance remains forbidden); annotations only
in the main file's own text; **annotation lines inside preprocessor-inactive regions (`#if 0`…) are
dropped** using the TU's skipped-region record — raw lexing would otherwise see them (§9).

## 3. Why LLVM/Clang (binding)

Typed AST (canonical types, sizes, **per-record field offsets and alignments — §7's consistency
check needs them**, target widths) via `clang.cindex`; comments as positioned COMMENT tokens from the
main-file extent; the detailed preprocessing record for macros (§9) and skipped regions (§2). Never
the Doxygen comment API; never an external `cpp` pass.

## 4. The C subset → IR mapping (C5)

Visitor keyed on cursor kind; **default = located "unsupported construct" error**. Types: integers →
`"int"` with width/signedness tracked (§5); array-used `T*`/`T[]` params → `"list"` (incl.
`char*`/`char[]` as byte arrays — the Frama-C model; `\valid_string`/`strlen` per §2); `struct S` →
record `type_decls`; `enum` → `"int"` + `module_constants`; floats, unions, function pointers,
`void*`, pointer casts → reject v1 (load-bearing for §6's strict-aliasing row). Statements as rev. 3
(`for` → `While` desugar; `switch` → `Match`; `goto`/VLAs reject). Locals **may** be declared without
an initializer — reads are guarded by the §6 taint mechanism (12.13 resolved; the initializer
*requirement* is dropped). **Scalar out-params:** the resolved end state is the **borrow-shaped
model** (12.7 ***) — `int *out` becomes a borrowed mutable cell, the same IR machinery as Rust
`&mut` and the seq/ref/view model; until §13 P-2 lands, C5 rejects them with a hint naming that
future. Division: **non-negative-operands guard, status quo** (12.8 resolved — frontend-only check
per `/`/`%`; `ComputerDivision` consciously not pursued, avoiding the two-semantics precedent).

## 5. The integer model — bounded; unsigned mode is per-function (12.3 resolved)

Signed: per-operation `ProofAssert(check, MIN_N <= e <= MAX_N)` — overflow is UB, the check is
mandatory (widths from §7). **Unsigned: a per-function marker** `//@ unsigned wrap` (default;
faithful `mod 2^N`) or `//@ unsigned strict` (no-wrap checks; surfaces unintended wrap as unproven).
A file-level CLI default may set the absent-marker mode. **Consequence accepted and enforced: the
manifest records the mode per function** — a "proved" claim names its unsigned semantics.
Conversions: widenings transparent; narrowing/sign-change → range check (signed) or `mod` (unsigned,
per the function's mode). `--int-model unbounded` survives as a ledgered prototyping opt-out.

## 6. Undefined behavior — the general policy, now with a source of truth (12.13/12.14 resolved)

**Rule:** every UB class expressible in the subset has exactly one disposition — **(I)** structurally
impossible, **(C)** checked (`ProofAssert`; undischargeable ⇒ correctly unproven), **(R)** rejected —
and is never silent.

**Source of truth (12.14):** the consolidated C-UB list at
`https://gist.github.com/Earnestly/7c903f481ff9d29a3dd1` (the Annex-J.2-derived enumeration). The
**registry** (the mechanized 12.14 instrument) maps **every entry** of that list to a disposition,
with **(O) out-of-subset** — "the construct that could exhibit it is rejected by C5's default" — as
the fourth, bulk category. CI fails if a list entry is unmapped, or if C5 admits a cursor kind with
no registry rows. The table below is the *representative* selection; the registry is *exhaustive*.

| UB class | Disposition | How |
|---|---|---|
| Signed overflow; `INT_MIN / -1` | **C** | §5 range checks |
| Division/modulo by zero | **C** | `check divisor != 0` |
| Shift by negative/≥ width; signed `<<` overflow | **C** | `check 0 <= s && s < N` + §5 |
| Out-of-bounds access | **C** | the core's `\valid`-driven bounds VCs |
| **Read of an uninitialized object** | **C** (rev. 5 — the taint mechanism) | see below |
| Strict aliasing | **I** | casts/unions/`void*` rejected; revisit on any subset growth (registry-enforced) |
| Modifying a string literal; null/dangling deref | **I** | no writable literal pointers; no pointer arithmetic/`malloc`/address-of |
| Unsequenced side effects (`i = i++`) | **R** | `++`/assignment inside expressions rejected |
| Uncontracted library call | **R** | §8 |

**The uninitialized-read taint (12.13 resolved).** Each local declared without an initializer gets a
**ghost taint flag**: C5 emits `GhostAssign x__init = 0` at the declaration, `GhostAssign x__init = 1`
alongside every assignment to `x`, and `ProofAssert(check, x__init == 1)` before every read of `x`.
The local itself receives a defined dummy value (0) so the core's model stays total; **the ghost
check carries the semantics**. Consequences: the `int x; if (c) x=1; else x=2; use(x);` idiom now
**proves** (both branches set the flag — definite assignment by *proof*, not by dataflow, so there is
no soundness-critical analysis to trust); a genuinely-maybe-uninitialized read is an undischargeable
check — a real finding; the cost is ghost state + one tiny ground goal per read. Note the honest
mapping of the user's "special value": a *value-level* poison would require a core value-domain
change; the ghost **flag** realizes the same property ("never read before write") **frontend-only**,
with existing IR nodes. **Frama-C alignment (closes O-4):** the surface form is ACSL's **`\initialized(x)`** predicate —
the synthesized read-checks are RTE-style `check \initialized(x)` that a user can also write or
strengthen manually, and the ghost flag is merely their *lowering*. Frama-C's workflow also answers
the peephole question: RTE **generates uniformly** and the analyzers **discharge** — generation is
never suppressed. O-4 is therefore closed as: no peephole; every read check is emitted, and
dischargeability is the prover's job (a later analysis may pre-*discharge*, never pre-*suppress*).

## 7. Implementation-defined characteristics — the FULL target-model JSON (remark 16 resolved)

Rev. 3 declared endianness/padding "unobservable"; rev. 5 corrects the posture: **low-level code uses
them**, so the schema specifies them concretely from day one, and features that observe them consume
the fields when they land (the package rule still governs *when*, §12).

```json
{ "target_model_version": "2",
  "triple": "x86_64-unknown-linux-gnu",
  "endianness": "little",
  "char_signed": true,
  "int_widths":  {"char": 8, "short": 16, "int": 32, "long": 64, "long long": 64, "pointer": 64},
  "alignments":  {"short": 2, "int": 4, "long": 8, "long long": 8, "pointer": 8, "max_align": 16},
  "struct_layout": {"rule": "itanium", "pragma_pack_supported": false} }
```

- **Consistency check (C1, hard error):** widths/alignments — and, per declared struct, the **field
  offsets the layout rule implies** — are checked against Clang's own answers
  (`type.get_size/get_align/get_offset`) under the TU's command line. The JSON is the auditable
  declaration; clang is the mechanism; divergence is a stopped build, not a footnote.
- **Consumed today:** `int_widths`, `char_signed` (§5). **Consumed by the low-level package** (byte
  views / `memcpy` / serialization, when it lands): `endianness`, `alignments`, `struct_layout` —
  and that landing simultaneously re-opens the strict-aliasing row and padding-contents
  unspecifiedness, so it ships as a package with its registry rows (§12).
- Unspecified behavior proper (evaluation order, padding contents) remains *unobservable by
  construction* until that package; the registry carries the audit.
- The model file + per-TU command lines are manifest/ledger entries: "proved **for this platform
  model**" is a checkable artifact.

## 8. The resolved-IR obligation

TU = the verification unit. Every call resolves in-TU or to a contract-carrying `trusted`/`abstract`
prototype; uncontracted externals are a hard error. **With `compile_commands.json` (§9) the
prototype↔definition drift check becomes implementable and mandatory:** when the defining TU is in
the database, CCSL locates it and **asserts contract equality** between the prototype and the
definition — the cross-TU O2 check; a mismatch is a hard error, because a drifted prototype is a
proof resting on a contract nobody proves.

## 9. Preprocessing & invocation (12.2c, 12.9 resolved)

```
ccsl --target-model x86_64-linux.json --compile-commands compile_commands.json --tu src/fs.c
```

- **`compile_commands.json` is the invocation source (12.9):** the TU's entry supplies the clang
  arguments (handed verbatim to libclang); per-entry target consistency (§7) is checked; the
  manifest records **per-TU configuration** (a file proved under `-DFOO` and one without are
  different proofs). The bare `ccsl file.c -- <args>` form remains for single files.
- **Annotations are fully preprocessed (12.2c):** clause text runs through the preprocessor with the
  TU's macro table — object-like *and* function-like macros work (`INT_MAX`, `BOUND(x)`,
  user contract macros). Consequences, accepted and engineered: C3 keeps an **expansion map** so
  every diagnostic shows the *written* and the *expanded* form side by side; C4's attachment uses
  the **raw** positions (attachment happens before expansion, so the mapping layer is
  per-clause-text, not per-file); a macro expanding to malformed clause text reports through the
  map. **Skipped regions:** C2 consults the TU's inactive-`#if` ranges and drops annotation lines
  inside them — raw lexing would otherwise resurrect `#if 0`-ed contracts (a soundness bug, not a
  nicety; a driver tests it).
- A `//@` generated *by* a macro body is still rejected (positions don't survive); comments survive
  preprocessing because C2 reads the main-file token stream — the external-`cpp` route stays out.

## 10. Seam discipline & determinism

No WhyML knowledge, no Why3 invocation, no duplicated core checks. TCB adds: libclang, the fidelity
claim, the target-model file, the per-TU command lines (all ledgered). Canonical JSON, source order,
sorted set→list boundaries, `source_language:"c"`, `ir_version` = the §13-bumped version;
self-check with the core's `validate_ir`; 4–5× regeneration → one hash.

## 11. Phasing (rev. 5 — §13 prerequisites run as their own gated track)

| Phase | Delivers | Gate |
|---|---|---|
| **P0** | spike: libclang TU + `//@` extraction + target-model v2 consistency (incl. struct offsets) + **the §13 P-4 label probe** | golden round-trip; mismatched JSON/triple errors; probe verdict recorded |
| **P1** | C2–C4: runs/indentation/fail-loud; **typed binders** (with §13 P-1 landed in PyCSL); **annotation preprocessing + expansion map + skipped-region drop**; `;` warn-accept | clause goldens; negatives: orphans, blank-line, tabs, `/*@`, `behavior`, macro-to-malformed-clause, `#if 0`-ed annotation ignored |
| **P2** | C5 subset + §5 bounded ints + per-function `unsigned` pragma + **the §6 taint mechanism** + `compile_commands.json` invocation | frontend-only conformance (no core imported, hash-seed-varied); one driver per §6 table row; taint drivers: if/else idiom **proves**, missing-branch **fails**; manifest shows per-function unsigned mode |
| **P3** | end-to-end through the core **with §13 P-3 (`loop assigns`) landed**; ~10 ported drivers; the §8 cross-TU drift check on a two-TU example; measure check-goal cost | drivers prove; the PyCSL corpus remains green under the §13 core changes (their own gate); drift-check negative errors |
| **P4** | cross-language demo: the uint16/32 codec leaves in C (bounded ints; endian-independent byte arithmetic) | leaves prove standalone through the shared core |
| **P5** | subset growth: `do/while`, **out-params on the §13 P-2 borrow model**, the low-level package (§7), strings — each landing its registry rows first | per-feature drivers + corpus clean; registry completeness vs the §6 source-of-truth list |

## 12. Design decisions — resolved register & remaining open

**Resolved (rev. 5) — decision → owning section:**
12.1 → **(b)** core `loop assigns` (§2, §13 P-3) · 12.2 → **(c)** full annotation preprocessing (§9)
· 12.3 → **per-function pragma** (§5) · 12.4 → **user C labels** (§2, §13 P-4) · 12.5 *** →
**typed binders in both dialects** (§2, §13 P-1) · 12.6 → **warn-accept `;`** (§2) · 12.7 *** →
**borrow-shaped model** (§4, §13 P-2) · 12.8 → **non-negative guard** (§4) · 12.9 →
**`compile_commands.json`** (§8, §9) · 12.11 → `act` (rev. 3) · 12.13 → **ghost-taint** (§6) ·
12.14 → **Earnestly list + exhaustive registry** (§6) · 12.15/16 → **full-schema JSON + package
rule + registry audit** (§7).
**Rev. 6 (Frama-C/ACSL alignment):** O-1 → **char arrays + `\valid_string` / logic `strlen`**
(§2, §4) · O-2 → **ACSL `\valid(p+(lo..hi))`**, total under the whole-array model; `\valid(a,n)`
the `0..n-1` alias, `\valid_read` an alias (§2) · O-3 → **typed binders mandatory, `integer`
included** (§2, §13 P-1) · O-4 → **`\initialized` + RTE-style uniform generation, no peephole**
(§6).

**Still open:**
- **O-5 borrow-model design choices** *(P-2's own spec)* — surface (`&mut`-like marker vs inferred),
  IR node shapes, reborrow/alias rules; explicitly out of this document's scope.
- **O-6 untyped-binder horizon in PyCSL** *(with P-1)* — rev. 6 fixed the *direction* (typed is the
  rule; ACSL has no untyped binder); what remains is only the schedule: how long the inferred
  untyped form survives, and when the corpus migrates.

## 13. What must change in PyCSL BEFORE (or alongside) the C front-end (new — the *** items)

> **Detailed specification: `pycsl-prereqs-spec.md`** — this section remains the summary; the
> dedicated spec carries the per-item design, IR-version impact, gates, and the dependency graph.

Each prerequisite lands in the PyCSL repo under its own gates (corpus byte-clean, `os` proven,
doc-coherency, determinism 4–5×), *before* the C phase that consumes it. P-2/P-3 are **additive** IR
changes → **IR v1.2** (minor bump per the compatibility policy; a 1.1 document stays ingestable).

- **P-1 — Typed quantifier binders in the PyCSL CSL** *(from 12.5 ***; consumed by C P1).*
  Module 2 grammar gains typed binders **with ACSL's `integer`** — the mathematical type, which is
  PyCSL's native int — alongside concrete C types: PyCSL `\forall integer k. E`, C
  `\forall integer k; E` (per-dialect separator, same semantics); a C-typed binder
  (`\forall int k;`) desugars to `integer` + that type's range as the binder `domain`. Module 5
  fills `binder_type` directly. Untyped binders remain accepted via inference for now — rev. 6
  fixes their *fate* (deprecated; ACSL has no untyped binder), leaving only the horizon (O-6).
  **Why first:** one binder convention across front-ends, and the core's typed-binder check stops
  depending on per-frontend inference quality.
- **P-2 — The borrow-shaped mutable-reference model** *(from 12.7 ***; consumed by C P5 out-params,
  and by the Rust front-end).* Its own design spec (O-5), explicitly generalizing the
  seq/ref/view model already validated (`07-1705-spec-rev4`: value = immutable view, mutation =
  region-free ref rebind — the Creusot shape): additive IR nodes for a borrowed mutable cell +
  Module 6 lowering. **Why now (design) / later (code):** it is the single model that C out-params,
  Go slices/pointers, and Rust `&mut` all need — designing it once before two front-ends exist
  prevents two incompatible ad-hoc answers; implementation is gated by its own probes and is *not*
  on the C v1 critical path (C v1 rejects out-params with a hint).
- **P-3 — `loop assigns` as a core feature** *(from 12.1b; consumed by C P3).* Additive
  `assigns` field on `While`/`For` IR nodes; Module 6 synthesizes the preservation reasoning
  (internally the `\at(·, LoopEntry)` encoding) once, for every front-end; the Python front-end may
  surface `#@ loop assigns` in the same change (the platform payoff that justified choosing (b)).
  Gated by PyCSL drivers before C ever emits it.
- **P-4 — Arbitrary `\at` label anchors in Module 6** *(from 12.4; probe at C P0).* Probe whether
  `At{label}` beyond the built-ins + `Label` anchors already lower; if not, add it (small, additive).
  `LoopEntry` support is also what P-3's encoding uses — order P-4's probe before P-3's
  implementation.
- **Explicit reliefs (decided items needing NO core change):** the taint mechanism (12.13 — existing
  `GhostAssign`/`ProofAssert`), the per-function unsigned pragma (12.3 — emission-side, manifest
  records it), full annotation preprocessing (12.2c — frontend), `compile_commands.json` + the
  cross-TU drift check (12.9 — frontend tooling), the division guard (12.8 — status quo). The C
  front-end's core footprint is exactly P-1…P-4, nothing else.

## 14. Worked example (rev. 5)

```c
//@ act small:
//@     given x >= 0 && x < BOUND          // BOUND from #define BOUND 100 — preprocessed (§9)
//@     ensures \result == x + 1
//@ act any_valid:
//@     given x >= 0 && x <= INT_MAX - 1;  // trailing ';' → warning, accepted
//@     ensures \result >= 1
//@ complete small, any_valid
//@ unsigned wrap
int test_precondition(int x) {
    int y;                                  // no initializer → ghost taint y__init = 0
    if (x % 2 == 0) y = x + 1;              // taint cleared on both branches…
    else            y = x + 1;
    return y;                               // check y__init == 1 → proves
}
```
Lowers to: two `acts`, the §5 overflow check on `x + 1` (discharged by the `given` bounds — note
`INT_MAX` resolved by preprocessing), the §6 taint ghost + read check (discharged by the if/else),
and `\forall int k; …`-style binders wherever quantifiers appear. Drop the `else` branch and the
taint check is correctly unproven; drop the upper bounds and the overflow check is.

## 15. Acceptance criteria (rev. 5)

1. **Core footprint = §13 exactly:** the only core/PyCSL changes are P-1…P-4, each landed under
   PyCSL's own gates with the Python corpus green — **[byte-diff there, inspect here]**.
2. §14 proves end-to-end; the missing-`else` and missing-bound twins are **reported unproven** —
   **[PROVE / PROVE-neg]**.
3. Frontend-only conformance green, no core imported, deterministic — **[measure]**.
4. **Registry completeness:** every entry of the §6 source-of-truth UB list mapped to
   {I, C, R, O}; CI fails on an unmapped entry or an admitted construct without rows; one driver per
   representative table row — **[measure / PROVE-neg]**.
5. **Taint / `\initialized`:** if/else idiom proves; maybe-uninitialized read fails; the
   dummy-value never carries semantics; the surface predicate `\initialized(x)` is writable in
   contracts and lowers to the same flag — **[PROVE / PROVE-neg]**.
6. **Target model v2:** JSON↔clang divergence (widths, alignments, per-struct offsets) is a hard
   error; manifest references model + per-TU command lines + per-function unsigned mode —
   **[PROVE-neg / ledger]**.
7. **Preprocessed annotations:** function-like macros work; diagnostics show written + expanded
   forms; a `#if 0`-ed `//@` is ignored (driver) — **[PROVE / inspect]**.
8. **Cross-TU drift check:** a prototype whose contract diverges from its definition's (both TUs in
   `compile_commands.json`) is a hard error — **[PROVE-neg]**.
9. Fail-loud totality as before (orphans, tabs, `/*@`, `behavior`, uncontracted externals) —
   **[PROVE-neg]**.

> **In one line (rev. 6):** the open choices are decided — `loop assigns` becomes a **core** feature,
> annotations are **fully preprocessed** (with an expansion map and `#if`-skipped-region hygiene),
> unsigned semantics are a **per-function pragma** recorded in the manifest, `\at` accepts **user C
> labels**, quantifier binders are **typed in both dialects**, out-params await the **borrow-shaped
> model**, invocation reads **`compile_commands.json`** (which finally makes the cross-TU
> prototype↔definition drift check enforceable), uninitialized locals carry a **ghost taint flag**
> checked at every read (definite assignment by proof, frontend-only), the UB registry is exhaustive
> against the **Earnestly Annex-J.2 list**, and the target-model JSON specifies **endianness, sizes,
> alignments, and struct layout in full** because low-level code uses them — with the new §13 naming
> the exact PyCSL prerequisites (typed binders, the borrow model, core `loop assigns`, `\at` label
> anchors) that land first, under PyCSL's own gates, so the C front-end's core footprint is those
> four items and nothing else. Rev. 6 closes O-1…O-4 the Frama-C/ACSL way: `\valid_string` + logic
> `strlen` over char arrays, ACSL `\valid(p+(lo..hi))` ranges (total under the whole-array model),
> always-typed binders with `integer`, and `\initialized` with uniformly generated,
> never-suppressed read checks.
