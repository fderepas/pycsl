# Gate-R oracle response — emit_ir Call-internals value model

**Reviewer:** independent (Gate-R / make-or-break spike). Did NOT read the driver
rationale; did NOT edit `src/`. Verdict backed by a RUN Why3 oracle.

**Oracle .mlw (scratchpad):**
`/tmp/claude-1346829620/-home-fabrice-derepas-canonical-com-git-pycsl/9dd932d0-43ec-4eaf-b2b4-3686bbb5f588/scratchpad/callinternals-oracle.mlw`
**Composition probe:**
`/tmp/claude-1346829620/-home-fabrice-derepas-canonical-com-git-pycsl/9dd932d0-43ec-4eaf-b2b4-3686bbb5f588/scratchpad/callinternals-composition-probe.mlw`

Environment: Why3 1.8.2, Z3 4.13.3, Alt-Ergo 2.6.2.

---

## VERDICT: **CONFIRM — build viable.**

The keyword-node list + kwval Name/Attribute distinction typechecks, the faithful
`extract_bound` bound-extraction proves the string-VARIABLE projection **Valid and
non-vacuous** (both evil twins behave correctly), terminates (program `let rec` +
`variant { kws }` VC Valid), and is **axiom-free / abstract-val-free** on the
constructive path (ledger 3 stays clean). The keyword_list + kwval **compose
cleanly with the existing emit_ir ADT as a SEPARATE standalone type** — no
positivity issue.

---

## The model (what was built)

1. `kwval = KwName string | KwAttr string` — the minimal Name/Attribute
   distinction emit_ir currently collapses to a bare string. Discriminant
   `is_name` / `kwval_kind`; projectors `name_id` (`.id`) / `attr_of` (`.attr`).
2. `keyword = { kw_arg: string; kw_value: kwval }` and the bespoke cons-list
   `keyword_list = KWNil | KWCons keyword keyword_list` (NOT seq — respects the
   recorded seq non-strict-positivity wall).
3. `call_repr = { call_kws: keyword_list }` + projector `call_keywords`.
4. `extract_bound : keyword_list -> option string` — iterates, matches
   `kw_arg = "bound"`, returns `Some (name_id ...)` for a KwName / `Some (attr_of
   ...)` for a KwAttr. Provided TWICE: a recursive **logic `function`** (fully
   constructive — native string `=`, auto structural-termination) carrying the
   goals, and a **program `let rec`** with `variant { kws }` + an `ensures`
   (honors the "let driver + variant discharges" requirement).

---

## Why3 output — goal by goal (`why3 prove -P z3 -t 15`)

| Goal | Meaning | Result |
|------|---------|--------|
| `G1_name_projects` | Name arm: `∀v. extract_bound([bound=KwName v]) = Some v` (string VARIABLE) | **Valid** (0.01s, 8946 steps) |
| `G2_attr_projects` | Attribute arm: `∀a. …([bound=KwAttr a]) = Some a` | **Valid** (0.02s, 8947 steps) |
| `G3_no_bound_none` | evil twin #1: no "bound" keyword ⇒ `None` (real discrimination) | **Valid** (0.09s, 287990 steps) |
| `G4_iterate_finds` | real iteration: "bound" found AFTER a non-bound head | **Valid** (0.01s, 9423 steps) |
| `G5_evil_wrong_value` | evil twin #2: `∀v. …(KwName v) = Some "wrong"` — genuinely FALSE | **Timeout** (correctly NOT Valid = non-vacuous) |
| `G6_concrete_discriminates` | `…(KwName "aaa") = Some "aaa" ∧ ≠ Some "bbb"` | **Valid** (0.02s, 9105 steps) |
| `extract_bound'vc` | program `let rec`: `variant { kws }` termination + `ensures` postcondition | **Valid** (0.02s, 18935 steps) |

**Non-vacuity is established two ways:** G5 (a wrong-value claim) is unprovable
(Timeout, not an instant Valid — a vacuous theory would prove it), and G6 proves
a specific value distinguishable from a wrong constant (Valid). The variable
projection G1/G2 (universally-quantified `v`/`a`, not ground constants) is a
genuine value-carrying proof.

**Termination:** the program `let rec` `variant { kws }` VC discharges Valid —
bespoke cons-list structural recursion, exactly the irlist precedent. The logic
function needs no variant (Why3 auto-accepts structural descent).

**Axiom-free:** `grep` finds NO `axiom` declaration and NO abstract `val` in the
constructive module `CallInternalsOracle` (only comment text). A cert built from
this stays axiom-free. (The secondary `…Prog` module pulls `string.OCaml`'s
spec'd `val (=)` for program-level string comparison — that val is NOT on the
constructive proof path; the logic-function goals G1–G6 use none of it.)

---

## Composition with the existing emit_ir ADT (probed)

Reconstructed a structurally-faithful minimal emit_ir carrying the real
`with irlist = ILNil | ILCons emit_ir irlist` mutual recursion from
`preamble.py`, then attached the keyword machinery:

- **Probe A (the model's shape): CLEAN.** `keyword_list` is a **standalone type
  defined before emit_ir** (kwval is a leaf string, carries no emit_ir), used in a
  new ctor `IrCallKw string keyword_list emit_ir int`. The whole ADT — including
  the `with irlist` mutual recursion and the `size`/`isize` measure — **typechecks
  with exit 0, empty stderr, NO positivity error, NO termination error.**
  (`G_size_nonneg` itself Timeouts because SMT lacks native induction over the
  recursive ADT — an SMT artifact, not a well-formedness failure; the real
  preamble discharges size facts with explicit induction lemmas, per its own
  comments.)

- **Probe B (stress case — NOT needed by the model): WALLED, but not positivity.**
  If a keyword VALUE were a *full emit_ir node* (making `keyword`/`kw_list`
  mutually recursive with emit_ir via a RECORD field), Why3 reports
  `Cannot prove termination for size` — the termination checker cannot see
  structural descent through a record-field projection (`size k.kw_value`) in a
  mutual recursion. This is a **termination-measure limitation, not a positivity
  failure**, and it reinforces the design: **keep kwval a leaf** so keyword_list
  stays standalone (Probe A).

**Composition guidance:** attach the keyword_list to emit_ir as a **SEPARATE
standalone type** (define `kwval` / `keyword` / `keyword_list` BEFORE the emit_ir
sum; reference `keyword_list` from a new `IrCallKw` ctor field). Do NOT fold it
into the `with irlist` mutual-recursion block, and do NOT model the keyword value
as a full emit_ir node — the leaf `kwval` (KwName/KwAttr) captures the faithful
`.id`/`.attr` distinction and avoids the Probe-B measure wall.

---

## Bottom line

The make-or-break is **CONFIRMED**. The keyword-node list + Name/Attribute-
distinguishing kwval is a viable, axiom-free, terminating, non-vacuous value-model
extension that composes cleanly (as a standalone type) with the existing emit_ir
ADT. The `_collect_typevar_registry` bound-extraction lowers faithfully. Build
viable — proceed.
