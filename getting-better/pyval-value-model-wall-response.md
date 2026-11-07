# pyval-value-model-wall-response.md — Gate R independent review

**Reviewer:** independent (Gate R). Inputs: the report `pyval-value-model-wall.md` + repo/Why3 oracle access ONLY.
I did not read the driver rationale and did not edit `src/`. Verdict is backed by a run oracle, not prose.

**Environment:** Why3 1.8.2; provers Alt-Ergo 2.6.2, Z3 4.13.3.

**Oracle artifacts (in `getting-better/`):**
- `pyval-oracle.mlw` — the make-or-break spike (pyval variant + size measure + `map string (option pyval)`
  dict + the `{"pattern","ctor":<var>,"captures"}` build + field-read goals + evil twin).
- `pyval-probe-positivity.mlw` — the four recursion-arm positivity probes (A_seq / B_cons / C_map / D_assoc).
- `pyval-fold-structural.mlw` — a real mutual-recursive fold over pyval proving structural well-foundedness.

---

## VERDICT: CONFIRM (build is viable) — REFINED by one hard structural rule.

The §7 make-or-break claim is **CONFIRMED**: a faithful `pyval` value variant + a `map string (option pyval)`
heterogeneous dict + a typed field read **typechecks, proves the string-VARIABLE read Valid non-vacuously
(evil twin fails), and adds no axiom/abstract val**. The build is viable.

It carries ONE non-negotiable structural refinement the report must adopt (the report half-anticipates it in
§6(a)/R0, and it matches the campaign's own `irlist`/`stmt_list` bespoke-cons precedent):

> **The `PArr` arm MUST recurse through a bespoke cons-list, NOT `seq pyval`.**
> `PArr (seq pyval)` is **TYPE-REJECTED** by Why3: *"Constructor PArr contains a non strictly positive
> occurrence of type pyval"* — `seq` is an abstract polymorphic type, so recursion through it fails the
> strict-positivity check (the same class of wall as the already-recorded `array (array τ)` rejection).

With that one change the entire §7 shape goes through.

---

## Oracle output — goal by goal

### Positivity probes (`pyval-probe-positivity.mlw`, typecheck only)
| Arm | Shape | Why3 result |
|-----|-------|-------------|
| A_seq  | `PArr (seq pyval)` | **REJECT** — "non strictly positive occurrence of type pyval" |
| B_cons | `PArr pyval_list` (bespoke `PNil`/`PCons`) | **ACCEPT** |
| C_map  | `PMap (map string (option pyval))` | **ACCEPT** (`map a b = a->b`; pyval sits in the positive arrow codomain) |
| D_assoc| `PMap assoc` (bespoke `ANil`/`ACons`) | **ACCEPT** |

Finding: `seq` is the *only* rejected arm. `PMap` through `map` typechecks fine — the positivity worry in §6(a)
about `PMap` is **unfounded**; the real hazard is `seq`.

### Make-or-break goals (`pyval-oracle.mlw`, `why3 prove`)
Typecheck: **exit 0** (whole file, with `PArr pyval_list` + `PMap (map string (option pyval))` + `PNode pyval`).

| Goal | Alt-Ergo (10s) | Z3 (15s) | Meaning |
|------|----------------|----------|---------|
| `read_variable_faithful` — `get (build a) "ctor" = Some (PStr a)` | Timeout | **Valid** (0.03s) | **THE make-or-break: string VARIABLE projects faithfully, no int-erasure** |
| `read_literal_faithful` — `get (build a) "pattern" = Some (PStr "Constructor")` | Timeout | **Valid** (0.03s) | literal key reads back the literal |
| `keys_distinct` — `ctor` value ≠ `pattern` value when `a≠"Constructor"` | Timeout | **Valid** (1.68s) | distinct keys stay distinct |
| `read_list_faithful` — `get (build a) "captures" = Some (PArr [PStr "x"])` | **Valid** (0.05s) | **Valid** (0.02s) | list-of-value arm projects faithfully |
| `evil_wrong_literal` — `get (set … "ctor" (PStr a)) "ctor" = Some (PStr "wrong")` | (n/a) | **Unknown** (0.31s) | **NON-VACUITY CONFIRMED — evil twin does NOT prove** |

Z3 discharges every real goal instantly and refuses the evil twin. Alt-Ergo times out on the map-select goals
(quantified array/select reasoning) but proves the pure-ADT one; **Z3 is the correct primary prover for this
value-model class** (the report's `-P z3` fallback is not a fallback here — it is the primary).

### Well-foundedness of the `size` measure
- The plain logic `function size` / `list_size` (mutually recursive over `pyval`/`pyval_list`) is **accepted by
  Why3's termination checker at typecheck** (`pyval-oracle.mlw` typechecks). That acceptance *is* the
  well-foundedness of the structural measure.
- A real mutual-recursive fold `count_strs`/`count_strs_list` **with no `variant` clause** typechecks and its
  run-goal proves **Valid** (Z3, 0.10s) in `pyval-fold-structural.mlw` — Why3 infers the structural descent on
  the bespoke ADT and emits *no* termination VC. This is the clean, campaign-matching well-foundedness path
  (the `irlist`/`stmt_list` fold shape). **Use structural recursion, not an explicit `size` variant.**
- Caveat (honest): the *derived* lemma `size v >= 1` needs mutual structural induction and does NOT fall to
  SMT alone (Alt-Ergo/Z3 Timeout); paired with `induction_ty_lex` and its companion `list_size_nonneg` it
  proves Valid, but the pair is truly mutually dependent and wants a one-shot mutual induction (a 3-line Coq
  realization in the side-car cert — the campaign's normal Phase2x pattern). This does not affect viability:
  a fold never needs `size>=1`; structural recursion supplies the well-founded order directly.

### Axiom check (analogue of `Print Assumptions`)
`grep` of `pyval-oracle.mlw` for `axiom`/abstract `val`: **NONE** (only the header comment matches). Every
construct is a constructive `type` / `function` / `let rec function` / proved `lemma` / `goal`. Imports are the
standard trusted stdlib (`int.Int`, `option.Option`, `map.Map`, `string.String`) that the project already
depends on — they add nothing to the project's 3-axiom cited-proof ledger. **The model is axiom-free; ledger
stays 3.**

---

## Refinements the impl plan MUST adopt (all oracle-proven)

1. **`PArr` → bespoke cons-list `pyval_list` (`PNil`/`PCons`), never `seq pyval`.** Hard Why3 type wall
   otherwise. (probe A_seq REJECT vs B_cons ACCEPT.)
2. **Outer dict = `map string (option pyval)`** (or `map string pyval` with a sentinel) — both typecheck; the
   `option` form is proved here and gives a faithful "absent key" = `None`.
3. **`PMap` via `map string (option pyval)` is admissible** (positivity is fine), BUT its `size` cannot fold an
   infinite map domain — `size (PMap _) = 1` (constant). **Consequence / REFINE boundary:** a fold that must
   structurally recurse *into* nested-map VALUES is not covered by this measure; use the `D_assoc` bespoke
   association-list form for that case, or restrict PMap reads to key-projection (which the report's actual
   frontier target `_render_match_pattern` does — it reads keys, it does not fold into nested maps). For the
   stated frontier (`PStr | PInt | PArr | PNode` + key-projected `PMap`), **`PArr (pyval_list)` alone
   suffices** and `PMap` is a safe, positivity-clean addition.
4. **Prover: Z3 primary** for the heterogeneous-dict read VCs (Alt-Ergo times out on map-select).
5. **Cert (`Phase2f`): axiom-free is achievable**; include the 3-line mutual-induction proof of `size`
   non-negativity in Coq/Lean if the emitter ever emits an explicit `variant { size v }` — otherwise structural
   recursion needs no such lemma.

## Bottom line
§7 is answered **YES**: the faithful `pyval` + `map string (option pyval)` + typed field read is an axiom-free
WhyML shape that typechecks and proves the string-variable read Valid non-vacuously. The single hard constraint
is `PArr` must use a bespoke cons-list (`seq` is Why3-rejected). No fundamental Why3 wall stands in the build's
way; proceed with the bespoke-cons refinement baked in.

**Oracle path:** `getting-better/pyval-oracle.mlw` (+ `pyval-probe-positivity.mlw`, `pyval-fold-structural.mlw`).
