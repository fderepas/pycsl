# set-value-model-wall-response.md — Gate R independent oracle review

**Reviewer:** independent Gate-R reviewer (report + repo/oracle access only; did not read any
driver/executor rationale; committed source untouched).
**Subject:** `getting-better/set-value-model-wall.md` §7 — model an emitter-local `Set[str]`
(`s=set(); s.add(x); x not in s`) as a Why3 finite set of strings, axiom-free (ledger 3).
**Oracle files (scratchpad):**
- `…/scratchpad/set-oracle.mlw` (primary — logic plane + executable clone + driver)
- `…/scratchpad/set-oracle-driver-hinted.mlw`, `set-oracle-map.mlw`, `map-probe.mlw`, `evil-check.mlw` (probes)
**Tools:** Why3 1.8.2, z3, alt-ergo (all present).

---

## VERDICT: CONFIRM — build viable — with one MANDATORY emission rule (a REFINE-grade gotcha)

`set.Fset` over `string` typechecks and the membership/dedup goals prove **Valid, non-vacuously**,
**axiom-free / ledger-neutral**. The report's core §7 claim holds. BUT the report's §3 *lowering* as
literally written ("hold `fset string` in a ref, `x in s → Fset.mem x s`") does **NOT** lower — `set.Fset`
is a pure **logic** theory (its `mem` is a *predicate*, `empty` a logic symbol), so it cannot drive a
program `if`. The emitter must respect a specific split rule (below).

---

## 1. Logic plane — the §7 make-or-break goals (CONFIRMED Valid, non-vacuous)

`module SetStrLogic` = `use string.String` + `use set.Fset`, `fset string` local.
`why3 prove -P z3 -t 5 set-oracle.mlw -T SetStrLogic`:

| goal | claim | result |
|---|---|---|
| `mem_after_add` | `forall x. mem x (add x empty)` | **Valid** (0.03s, 38303 steps) |
| `not_mem_other` | `forall x y. x<>y -> not (mem y (add x empty))` (dedup crux, over string **variables**) | **Valid** (0.02s, 38487 steps) |
| `dedup_sequence` | `let s=add "a" (add "b" empty) in mem "a" s /\ mem "b" s /\ not (mem "c" s)` | **Valid** (0.05s, 86146 steps) |
| `evil_twin_must_fail` | `forall x y. mem y (add x empty)` (universally false) | **Timeout** (5.00s) — correctly does NOT prove |

`fset string` typechecks with no issue — no fallback to `set.Set` or `map string bool` was needed at the
logic level.

## 2. Non-vacuity — SEALED

- Evil twin does not prove under **either** solver: z3 Timeout (5.00s), alt-ergo Timeout (3.00s).
- Its negation is **Valid**: `not (forall x y. mem y (add x empty))` →
  `why3 prove -P z3 evil-check.mlw` = **Valid (0.12s, 292877 steps)**. A genuine counterexample exists,
  so the theory is consistent and the model truly separates members from non-members. The Valid goals
  are not vacuous.

## 3. Axiom / ledger check — CLEAN (ledger stays 3)

- `set.Fset` is stdlib (`.../share/why3/stdlib/set.mlw`). Its `axiom add_def`, `is_empty_empty`, etc. are
  **Why3 standard-theory axioms** — trusted stdlib, **not** entries in PyCSL's project
  `_AXIOM_REGISTRY`. Using `set.Fset` introduces **no project axiom**: the 3-axiom ledger is untouched.
- The logic plane (§1) adds **zero** `val`/`axiom` of its own — pure constructive stdlib. Ledger-neutral,
  exactly as the report claims.

## 4. THE GOTCHA — executable control flow (the mandatory emission rule)

`_collect_class_fields`'s `if name not in field_names_seen:` is real program control flow; the guard needs
a program **bool**. `Fset.mem` is a logic **predicate**, `Fset.empty` a logic symbol — using them in a
program `let`/ref fails typechecking (`why3 prove set-oracle.mlw` initial attempt:
`"Logical symbol empty is used in a non-ghost context"`). So §3's literal recipe does not lower.

Two consequences the emitter MUST respect:

**(a) Use the executable clone `set.SetApp`, and supply a program-level string-equality `val`.**
`module StrSetApp` = `clone export set.SetApp with type elt = string, val eq = eq_str, axiom .`,
where `val eq_str (x y:string):bool ensures { result <-> x = y }`. Its refinement VC discharges:
`-T StrSetApp` → `Goal eq'refn'vc. Valid (0.01s, 2312 steps)`. `eq_str` is a total, decidable primitive
(Python `s1 == s2`), **not** a ledger axiom; if PyCSL already models Python string `==` as a program
bool (it must), this is not even a *new* `val`.

**(b) Keep the method's proof obligation to type-safety + frame; do NOT demand proving set
NON-membership through the executable layer.** Positive membership and the guards are cheap, but
`assert { not (Fset.mem "c" !s) }` after a sequence of conditional `SetApp.add`s is SMT-hard:
`why3 prove -P z3 set-oracle.mlw` → `Goal dedup_driver'vc. Timeout (5.00s)`. With `-a split_vc`,
**34 sub-goals Valid**, and the lone survivor is exactly that negative-membership assertion
(`Sub-goal Assertion … line 60 … Timeout`). It is hard because `SetApp`'s abstract `set`/`to_fset`
coercion + 4-way branch split + string-literal disequality defeat the prover; a hint pinning the concrete
fset does not rescue it (`set-oracle-driver-hinted.mlw` still Timeout). This is fine **as long as the
report's "fixed type-safety + frame contract shape" does not require set non-membership** — the faithful
lowering of the dedup emits the `if not mem …` *guard* (cheap), not a `not mem` *proof obligation*.

## 5. On the R0 fallback (`map string bool`) — it does NOT dodge the gotcha

`map.Map` is **also** a pure logic theory: `map-probe.mlw` (a program `let` using `Map.set`/`Map.get`)
fails with `"Function test must be explicitly marked ghost"` / `"ghost modification in a non-ghost
variable"`. So `map string bool` is not a cleaner *executable* escape than `Fset` — it too needs an
executable wrapper (array/hashtable/abstract `val`). Recommendation: use `set.Fset` for the spec plane
and `set.SetApp` for the executable plane; do not switch to `map string bool` expecting free
executability.

---

## Bottom line for the executor

- **Modeling is sound and axiom-free** — build the `Set[str]` value model on `set.Fset` (spec) +
  `set.SetApp[string]` (executable). Ledger stays 3.
- **Two rules the emitter MUST honor:** (1) supply/reuse a program string-equality `val` for the
  `SetApp` clone; (2) confine `_collect_class_fields`'s contract to type-safety + frame — do **not** let
  the VC require proving set non-membership through the abstract set layer, or it will time out.
- If a future contract genuinely needs the non-membership fact, discharge it at the **`Fset` logic
  level** (where `not_mem_other`/`dedup_sequence` prove in <0.1s), e.g. via a ghost `fset` shadow pinned
  by an invariant — not through repeated `SetApp.mem` case-splits.

**Oracle path of record:** `…/scratchpad/set-oracle.mlw` (+ probes listed at top).
