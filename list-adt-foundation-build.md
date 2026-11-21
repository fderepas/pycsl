# list-adt-foundation-build.md — the shared `list <T>` ADT foundation (unblocks BOTH breakable walls)

*Consolidated next-session build spec, 2026-07-11. Synthesizes the fully-measured findings of driver run #3
(`getting-better/wall-lessons.md`, `stmt-walker-wall-impl.md`, `term-rewriter-wall-impl.md`). The campaign's
two remaining BREAKABLE walls — the **stmt-walker** wall (34 recursive statement-tree readers) and the
**term-rewriter** wall (`proof2why3/canonical.py` `Term → Term` rewriters) — do NOT have two problems; they
share ONE foundation: **a `list <T>` ADT-child type family + list-structural recursion, over a typed-node sum
emitted safely into the mirror.** Build this once; both walls unlock. Every gap below is oracle-pinned this
run — this is a build spec, not a survey.*

## 0. Why one foundation

| | stmt-walker wall | term-rewriter wall |
|---|---|---|
| operation | READ a stmt tree → scalar | CONSTRUCT a transformed `Term` |
| ADT | `stmtir` sum, `list stmtir` children | `term` sum, `App (list term)` child |
| target proven? | YES — `stmt-walker-spike.mlw` 14/14, 0 axioms | YES — `term-rewriter-spike.mlw` 6/6, 0 axioms |
| shared need | **`list <T>` param/field type + `size_list` + element-decrease lemma + `Cons`/`Nil` body recursion** | same, plus a recursive CONSTRUCTOR emission |

Both spikes prove the *targets* discharge axiom-free with pure `list`/`seq` children (`array <elem>` is
Why3-TYPE-REJECTED for a recursive-type field — the root cause of the live `int` vs `array int` failure). The
residual for both is the classic M2 gap: the **emitter must GENERATE** the proven shape. The generation
machinery is 80% shared.

## 1. The build, in dependency order (each spike-gated, byte-diff-0, ledger-3, SUITE-safe)

### F1 — the `list <T>` parameter/field type family  *(BOUNDED + byte-inert, PROVEN this run)*
`functions.py:68-97` (`_param_type_str`) routes EVERY `List[T]` param into the `array <T>` family; there is
NO `list <T>` exit. Add one (measured ~185 lines, 4 files, corpus-byte-identical on 5 files):
- `Module5_IREmitter.py`: `_m5_get_ir_node_list_elem(annotation)` (narrow — literal `"StmtIR"`/`"Term"` inside
  `List[...]`), threaded into the func IR as `param_ir_list_elem`.
- `functions.py`: `_param_type_str` checks it FIRST (before the `array` machinery) → `(safe: list <elem>)`.
- The same for record/local FIELDS of type `List[<node>]` (the term-rewriter's `args`).

### F2 — the typed-node theory emission, SUITE-SAFE  *(the §2quater blocker — MUST fix G1+G2)*
S-C1 `_emit_stmtir_theory` (and a `_emit_termir_theory` twin) emit the proven spike theory (variant +
`size`/`size_list` + element-decrease `let rec lemma`). Both are PROVEN to emit + discharge axiom-free
(9/9, 6/6) and are corpus-byte-inert — BUT the self-annotation suite showed the naive `@mutable_state` gate
BREAKS the mirror (the mirror IS `@mutable_state`). Two mandatory guards:
- **G1 — narrow the trigger.** Emit the theory into a module ONLY when that module actually contains a
  `List["StmtIR"]`/`List["Term"]` param/field. NOT all `@mutable_state`.
- **G2 — collision guard + LEAN theory.** Three mirrors already declare their own `type stmtir`/`stmt_ir`/`SIf`
  (`stmt_control_flow.py`, `statements.py`, `expressions.py`) → reserve a prefix (e.g. `_sw_stmtir`) or
  suppress-when-declared; and emit ONLY the lemmas a present walker needs (the full 5-lemma bundle OOM'd
  `Module6_WhyMLTranspiler.py`, PASS→FAIL — a large shared module cannot absorb it).
- **GATE:** after F2, `bin/run-self-annotation-suite.sh` must be GREEN (no collision, no new OOM) — corpus
  byte-diff-0 is necessary but NOT sufficient; the mirror-suite is the real gate.

### F3 — list-structural recursion body form  *(S-C2, stmt-walker)*
Lower `if not stmts: …; last = stmts[-1]` / `for s in stmts` / `s["body"]` recursion to the spike's
`match … | Nil -> … | Cons x rest -> …` form (Why3 `list.List` is NOT indexable — no `[-1]`/`[i]`). Plus
`variant { size_list … }` synthesis for the recursive call against F2's theory. (S-C3.)

### F4 — recursive-constructor emission  *(term-rewriter T-C1/T-C2 only)*
For the rewriter side: emit a Python `App(head=h, args=a)` / `BinOp(op,l,r)` dataclass-ctor call as the WhyML
constructor application, and lower `tuple(f(a) for a in t.args)` (comprehension over the recursive ADT) to a
`let rec flip_list (l: list term): list term` with its own `variant { size_list l }`. Reuses F1's `list term`
field + F2's `size_list`.

## 2. Build order & first landed −1

`F1 → F2 (with G1+G2, suite-green) → F3 → convert the FIRST bool stmt-walker
(`ir_scanner.ends_with_return`/`has_continue`) as ONE count-reducing increment` — the minimal witness proving
the whole chain. THEN the rest of the 34-reader cluster, THEN `F4 →` the term-rewriter `_flip_comparisons`.
All-or-nothing per method (one commit at the conversion; no facade).

## 3. Gates (unchanged, per converted method)
fidelity (52/52 + sync) · `--fun` + WHOLE-FILE proof · **`run-self-annotation-suite.sh` GREEN (the F2 lesson:
mirror-suite, not just corpus byte-diff)** · byte-diff-0 (or sanctioned reset) · ledger==3 (theories are
match-based/axiom-free — no certificate fires for a read-only walker; the constructor side F4 needs the
coupling-rule check that a CONSTRUCTED term value is covered by the existing/side-car certificate) · non-vacuity
· count strictly down.

## 4. What is proven vs pending (honest ledger)
- **Proven this run:** both targets discharge axiom-free (14/14, 6/6); F1 bounded + byte-inert; F2 emits +
  discharges + byte-inert on corpus; `array <elem>` type-rejection confirmed (→ pure `list`/`seq`).
- **Pending (the build):** F2's G1+G2 (trigger-narrow + collision/OOM guard, suite-green) · F3 body recursion
  · F4 constructor emission · the per-method conversions. All bounded, all pinned; no oracle-unknown remains —
  this is generation work, not research.
