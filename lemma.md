# Plan: `#@ lemma` functions — implementation plan derived from `lemma-spec.md`

Companion to `lemma-spec.md`. The spec is the **normative "what must hold"** (surface syntax §3,
soundness rules §7–§8, lowering §6, validation §12). This plan is the **"how we build it, in what
order, behind which gates"** — it does not restate the spec's semantics; read both together. The spec
owns the *contract*, this owns the *construction*.

The headline finding from grounding the spec in the codebase: **lemma functions are ~75% reuse.** The
recursion/`\variant`/termination machinery, the `let [rec] function` logic-emission, the SCC
mutual-recursion grouping, `#@ datatype` + `match`, and `#@ assert`/`#@ check`/`#@ ghost` proof-body
statements **already exist and already lower correctly**. The genuinely new work is (1) one keyword in
Module 6 (`let [rec] lemma`), and (2) the **Module 4 soundness pass** that makes a lemma a *checked*
fact rather than an unsound back-door. The soundness pass is the heart and carries all the risk
(spec §7 can prove `False` if mis-enforced); everything else is plumbing or reuse.

---

## §0 — Reuse map (why this is code-ready, not green-field)

| Spec demand | Already in the tree (file:line) | New work? |
|---|---|---|
| `let [rec] function` for pure recursive defs usable in contracts | `module6_whyml/functions.py:317-322` keyword decision; `pure` flagged in `module5/memoization_rt.py:50-57` | **No** — add a `lemma` keyword string at the same site |
| `#@ \variant <expr>` and `#@ \variant (<expr>, <order>)` termination measure | parse `Module2_Parser.py:795` (`FunctionVariant` :217); weave `Module3_Weaver.py:201`; validate `Module4:746`; IR `Module5:291,1383`; **emit** `functions.py:199-204` (`variant { e }` / `… with <order>`) | **No** — recursive lemmas reuse it verbatim; §7.2 only makes it *mandatory-on-recursion* |
| `\variant` ⊥ `\diverges` conflict already rejected | `Module3_Weaver.py:252-257` | **No** — extend to "`lemma` ⊥ `\diverges`" (spec §7.3) |
| Mutual recursion `let rec … with …` (SCC) | `module6_whyml/scc.py` (`compute_sccs`, `sort_functions_by_scc`); continuation kw `functions.py:310-321`; corpus **0534** | **Minor** — P3 mutual lemma groups need the `with lemma` continuation kw |
| `#@ datatype` + `match`/case (proof-body case split, spec §5) | parse `Module2_Parser.py:621,942`; IR `Module5:77-87`; type emit `preamble.py:635-660`; native `match…with` `stmt_control_flow.py:433-508`; corpus **0520/0521/0542** | **No** — proof bodies reuse native match lowering |
| `#@ assert P` / `#@ check P` proof obligations (spec §5) | parse `Module2_Parser.py:187` (`CheckPoint`); IR `Module5:745-753`; emit `statements.py:737-746` (`assert { }` / `check { }`); corpus **0457-0459** | **No** |
| `#@ ghost` proof-local witnesses (spec §5) | parse `Module2_Parser.py:317` (`GhostAssignDecl`); IR `Module5:754-755`; corpus **0207/0292/0293** | **No** |
| `#@ proof rocq\|lean` → `axiom` (the *contrast*, spec §2/§10) | `preamble.py:482-537` (`axiom pycsl_axiom_<q> : …`); corpus **0342/0420/0542** | **No** — lemma deliberately **bypasses** this path (spec §9 last row) |
| Function-level marker directive wiring (the `lemma` flag itself) | template = `#@ \trusted`/`#@ abstract`: M1 needs nothing (generic `#@` harvester `Module1_Ingestor.py:100`); M2 grammar+decl+transformer; M3 `_init_function_csl_fields`+dispatch; M4 validate; M5 IR flag | **Yes** — mechanical, mirror `\trusted` |

**Net new code:** a `lemma` keyword case in `functions.py`, the IR `"kind":"lemma"` flag, the Module 4
soundness pass (§3 below), and the `let lemma`/`let rec lemma` Why3-syntax confirmation spike.

---

## §1 — R0 pre-flight: write the Gate-A FAIL drivers FIRST (demand-driver discipline)

The literal step 0. No source change until the drivers exist and fail *for the right reason* (today:
`#@ lemma` does not parse → a parse/weave error, not an unrelated failure). Drivers go in
`test-suite/corpus/pycsl-reference/` at the next free numbers (**0554+** at time of writing), in the
existing docstring + `# pycsl-flags:` style. The spec §11/§12 dictate the set:

**Positive (flip to PASS as each phase lands):**
1. **P1 flagship** — non-recursive lemma, empty body, SMT discharges directly (spec §4 `abs_sum_nonneg`).
2. **P2 flagship** — recursive lemma `sum_matches_spec` proving `sum_numbers(x) == json_sum(x)` over a
   `#@ datatype Json`, **removing** a `#@ proof rocq` import (spec §1/§4). This is the marquee demand:
   an inductive fact discharged in-toolchain.
3. **P2 second** — predicate-guarded `sum_nonneg` (`all_nonneg(x) ⇒ sum_numbers(x) >= 0`, spec §4).
4. **Call-site** — `sum_numbers_checked` instantiating a lemma explicitly (spec §4 last block).

**Negative / anti-soundness (commit `# pycsl-expected: FAIL`, STAY failing — these are the soundness
proof, spec §12):**
5. Recursive "lemma" **missing `#@ \variant`** → must be **rejected** (spec §7.2). The lynchpin.
6. Recursive lemma **recursing on a non-smaller argument** (variant not strictly decreasing) → rejected.
7. Lemma with a **false `#@ ensures`** → body fails to discharge (hard error, spec §7.1).
8. `#@ lemma` + `#@ \diverges` → rejected (spec §7.3).
9. Lemma body calling a `\trusted` function **without** `#@ lemma \trusted` → rejected (spec §7.5).
10. Lemma invoked **inside a `#@ requires`/`#@ ensures` expression** → rejected (spec §8 call-position).

**Advisory:**
11. Vacuous-`requires` lemma → **warns** but still verifies (spec §7.6) — a PASS-with-warning driver.

**Exit:** 8+ committed drivers; positives FAIL at parse today, negatives FAIL and will *stay* failing.
No source behaviour changed yet.

---

## §2 — Code-ready staged plan (supersedes spec §11 for execution)

Each stage: **entry** = prior exit + its driver committed; **exit** = driver flips/holds + full
reference sweep clean + **byte-identical non-mixin corpus** (the emission-identical gate, run exactly
as in `docs/glossary/emission-identical-gate.md` — `PYTHONHASHSEED=0`, all four memory models) + the
5-surface doc-coherency check (`bin/doc-coherency.py --check`) green.

### S0 — surface + parse the `#@ lemma` marker (mechanical, mirror `\trusted`)
- *First files:* `Module2_Parser.py` — add `class Lemma(CSLNode)` (after `Trusted`/`Abstract`, ~:228),
  a `lemma_decl: "lemma" ("\\trusted")?` grammar rule (~:798) wired into the `?contract`
  alternatives, and a `lemma_decl` transformer (~:1037). `Module3_Weaver.py` — init
  `node.csl_lemma=False`/`node.csl_lemma_trusted=False` in `_init_function_csl_fields` (~:49) and a
  dispatch branch `isinstance(c, Lemma)` (~:201). `Module1_Ingestor.py` — **no change** (generic
  harvester :100).
- *Exit:* a `#@ lemma` def reaches `--no-proof` without a parse error; the P1 flagship parses.

### S1 — IR + Module 6 emission: `let [rec] lemma … : unit … = body` (the new keyword)
- *First files:* `Module5_IREmitter.py` — emit `"kind":"lemma"` + `"lemma_trusted"` on the function IR
  dict (`_build_function_ir`, ~:1383, beside `function_variants`/`diverges`). `module6_whyml/functions.py`
  — at the keyword-decision site (:317-322) add the lemma branch: `let lemma` / `let rec lemma`
  (recursive — `use_rec` is already `bool(func_variants) or is_recursive`, :298), return type forced to
  `unit` for a `-> None` lemma. Contracts/variant emission (`_emit_contracts` :175-204) is reused
  **unchanged**.
- **Gate-B feasibility spike (do before writing the branch):** hand-write the *target* `.mlw` for the
  P1 flagship (`let lemma abs_sum_nonneg (a b: int): unit requires {…} ensures {…} = ()`) and run it
  through the installed Why3 to **confirm `let lemma` / `let rec lemma … variant {…}` is accepted by
  this Why3 version** and that the verified conclusion is usable downstream. This is the one external
  unknown; everything else is mechanical. (Why3 supports lemma functions, but pin the exact syntax.)
- *Exit:* P1 flagship PASSES (lemma body verifies, conclusion usable at a call site).

### S2 — the soundness pass (Module 4) — **the heart** (see §3)
- *First file:* `Module4_SemanticAnalyzer.py` — a new `_validate_lemma` invoked from `visit_FunctionDef`.
- *Exit:* negatives 5–10 are **rejected with distinct, on-point errors**; positives still pass.

### S3 — recursive (inductive) lemmas over `#@ datatype`
- *First files:* none new — recursion detection (`ir_scanner.py:451`), `let rec`, `\variant` emission,
  and `match` lowering all exist. Work is making the **variant mandatory-on-recursion** check
  (Module 4, §3) bite, and proving the P2 flagship discharges.
- *Exit:* P2 flagship (`sum_matches_spec`) + `sum_nonneg` PASS **without** a `#@ proof` import; negatives
  5–6 stay rejected.

### S4 — mutual lemma groups + triggers (spec §11 P3)
- *First files:* `module6_whyml/functions.py` keyword site — add the `with lemma <name>` continuation
  for an SCC of lemmas (Why3's mutual form is `let rec lemma f … with lemma g …`, spec §6; today the
  continuation kw is `and`/`with function` at :310-316). `module6_whyml/scc.py` already groups them.
  `#@ trigger` steering rides the companion quantification proposal.
- *Exit:* a mutually-recursive datatype lemma pair (the 0534 shape, but as lemmas) PASSES.

### S5 — integration & ergonomics + docs (spec §11 P4)
- `#@ lemma \trusted` shim (assumed, **warned** — emits `val` not `let lemma`, like `\trusted`);
  optional `#@ by induction on x` (Why3 `induction` transformation, empty body — spec §13.1) gated on a
  driver that needs it; the migration step (re-internalise a `#@ proof` fact as `#@ lemma`, spec §10.3).
- 5-surface doc-coherency: add `#@ lemma` to `README.md`, `docs/pycsl-concrete-syntax-reference.md`,
  `docs/pycsl-static-semantics-reference.md`, `docs/pycsl-translational-reference.md`,
  `test-suite/annotations.md`, and the relevant skill (`config/skills/` — `contract-writer` /
  `pycsl-annotate`), with `bin/doc-coherency.py --check` wired green.

**YAGNI exit:** stop at any stage no committed driver needs. P3/P4 (mutual groups, `\trusted` shim,
`by induction`, cross-module export — spec §13.3) start only on a real driver demanding them.

---

## §3 — The soundness pass (Module 4) — detailed, because it can prove `False`

A lemma is a *checked axiom*; if Module 4 mis-enforces, lemma functions become an unsound back-door
(spec §7). This pass is to lemmas what the composition check was to mixins. A lemma def is **well-formed
iff** (spec §7–§8), each a hard `PyCSLSemanticError` with a distinct message (negatives 5–10 prove the
teeth):

1. **Shape:** carries `#@ lemma`; ≥1 `#@ ensures`; `assigns \nothing`; return annotation is `None`.
2. **Variant-on-recursion (the lynchpin, §7.2):** if the body contains a self-call (reuse
   `IRScanner.is_recursive`, `module6_whyml/ir_scanner.py:451`) then a `#@ \variant` **must** be present;
   absence ⇒ reject (negative 5). The *strictly-decreasing* check is discharged by Why3's own
   termination VC from the emitted `variant {…}` (negative 6 fails there) — Module 4 enforces
   *presence*, Why3 enforces *decrease*. State this division explicitly in the pass.
3. **`\diverges` forbidden (§7.3):** `lemma` + `\diverges` ⇒ reject (negative 8). Extend the existing
   variant⊥diverges check at `Module3_Weaver.py:252`.
4. **Ghost discipline (§7.4):** `assigns \nothing`, return `None`; reject any non-ghost mutation in the
   body (it may not affect a runtime value — erased at extraction).
5. **No trust leakage (§7.5):** a plain `#@ lemma` body may call only verified facts (pure functions or
   already-declared lemmas). A call to a `\trusted` function is allowed **only** when the lemma is
   `#@ lemma \trusted` (negative 9). Walk the body's `Call` nodes; cross-check each callee's
   `pure`/`trusted`/`lemma` flag.
6. **Body-statement whitelist (§5):** admit only {recursive self-call, call to a verified lemma, `match`
   over a `#@ datatype`, `#@ assert`/`#@ check`, `#@ ghost`, `if/else` with a statement per branch,
   `pass`}. Reject `return <value>`, I/O, impure calls.
7. **Call-position (§8):** an explicit `lemma_name(args)` is admissible only in ghost/proof statement
   position, **never** inside a `#@ requires`/`#@ ensures` expression (negative 10) — lemmas are
   *invoked*, not referenced as terms; their conclusions enter contracts via the pure functions they
   mention.
8. **Vacuity (advisory, §7.6):** warn (don't reject) when `requires` is unsatisfiable — mirror the
   existing non-vacuity-witness warning shape.

Open during S2 (resolve against the P2 flagship, not blocking start): whether the body-whitelist is a
syntactic AST walk or needs the IR (start syntactic — the admissible set is structural).

---

## §4 — Effort sizing (P1–P3; P4 gated)

| Stage | Scope | Size |
|---|---|---|
| **R0 pre-flight** | 8+ FAIL drivers (positives + anti-soundness twins) | ~1 day |
| **S0 surface+parse** | mirror `\trusted` through M2/M3 | ~1–2 days |
| **S1 IR + emit + Why3 spike** | `kind:lemma` IR, `let [rec] lemma` keyword, confirm Why3 accepts the syntax | ~2–3 days |
| **S2 soundness pass** (the heart) | Module 4 `_validate_lemma`: shape, variant-on-recursion, diverges, ghost, trust-leakage, whitelist, call-position, vacuity | ~1–1.5 weeks |
| **S3 recursive lemmas** | make variant mandatory-on-recursion bite; P2 flagship discharges (mostly proving, little new code) | ~3–5 days |
| **S4 mutual + triggers** | `with lemma` continuation; trigger steering | ~3–5 days |
| **S5 ergonomics + 5-surface docs** | `lemma \trusted` shim, doc-coherency | ~2–3 days |

**P1–P3 total: ~3–4 weeks.** S2 dominates and owns the soundness risk; S1's only external unknown is
the Why3-syntax spike (cheap, do it first in S1).

---

## §5 — Reference corpus additions (mandatory)

Every phase ships drivers in the existing numbering (`test-suite/corpus/pycsl-reference/`), per the
project's reference-corpus discipline. Concretely (numbers indicative, next-free at authoring):

- **0554** P1 non-recursive lemma (empty body, SMT) — PASS.
- **0555** P2 recursive `sum_matches_spec` over `#@ datatype Json`, **drops a `#@ proof` import** — PASS.
- **0556** P2 predicate-guarded `sum_nonneg` — PASS.
- **0557** call-site instantiation (`sum_numbers_checked`) — PASS.
- **0558** recursive lemma **missing `\variant`** — FAIL (rejected).
- **0559** recursion on **non-smaller arg** — FAIL (rejected).
- **0560** **false `ensures`** — FAIL (body fails).
- **0561** `lemma` + `\diverges` — FAIL (rejected).
- **0562** trusted-leak without `lemma \trusted` — FAIL (rejected).
- **0563** lemma used **inside a contract expression** — FAIL (rejected).
- **0564** vacuous `requires` — PASS with warning.

Plus the spec §12 **erasure check** (lemma calls/bodies vanish under extraction) and the **regression
vs `#@ proof`** check (files that re-express an imported lemma as `#@ lemma` still verify). The
involution `0542.py` is the natural migration witness for §10.3.

---

## §6 — Decided vs still open (maps spec §13)

**Decided by this plan (was open in the spec):**
- Lemmas are modelled as functions with `"kind":"lemma"` in the IR, reusing the whole function
  pipeline (recursion/variant/SCC/contracts) — not a separate construct.
- Module 4 enforces variant *presence* on recursion; Why3 enforces *decrease* via the emitted
  termination VC. Clean division, no new prover support.
- `#@ lemma \trusted` lowers like `\trusted` (a `val`, warned), not a `let lemma`.

**Still open (resolve during the named phase, not blocking start):**
- **§13.1 `induction` transformation vs explicit recursion** — S5; offer `#@ by induction on x` only if a
  driver needs an empty-body inductive proof.
- **§13.2 custom well-founded orders** — already representable via `#@ \variant (expr, <order>)`
  (`functions.py:201`); the *vocabulary* of built-in orders is an S3 follow-on.
- **§13.3 cross-module lemma libraries / theory export** — P4+, gated on a real cross-file driver.
- **§13.4 lemmas over machine arithmetic** (`#@ assumes bounded_int(N)`) — verify IH availability under
  overflow guards during S3.
- **§13.5 quantified lemma conclusions** (`ensures \forall y:T; …`) — unify with the typed-quantifier
  companion proposal when it lands.

## §7 — Net
The spec is implementable now: the inductive-proof machinery PyCSL needs (recursion, `\variant`,
`match` over datatypes, `assert`/`ghost`, SCC grouping) **already exists and already lowers**. The two
things that turn "spec" into "code-ready" are (1) recognising that a lemma is a `"kind":"lemma"`
function reusing that machinery with **one new keyword** (`let [rec] lemma`), and (2) concentrating the
real risk in a single **Module 4 soundness pass** (§3) whose negatives (anti-soundness drivers 5–10)
are the proof that lemma functions cannot be used to derive `False`. First action: **R0** — write the
Gate-A FAIL drivers (also the cheapest), then the S1 Why3-syntax spike, then S0→S2.
