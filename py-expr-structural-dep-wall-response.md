# Oracle response: the `_py_expr_*` structural-dependency wall

*Independent external review (fable oracle), 2026-07-14. Blind to the sub-loop's internals; adjudicated from
`py-expr-structural-dep-wall.md` §3 plus my own Why3 spikes (Why3 1.8.2, Alt-Ergo 2.6.2, Z3 4.13.3). All spikes live
under the session scratchpad (`spike1_positive.mlw`, `spike2_negative_stripped.mlw`, `spike2_negative_faithful.mlw`,
`spike3_immunity.mlw`); their full text and prover output are pasted below. I tried to REFUTE soundness first — the
negative control below is a real, prover-confirmed unsoundness of shape-only import in the wrong regime — and only
then checked which side of the line the pure_ast case sits on.*

## Verdict

**BREAKABLE.**

Structural-only shape-import is sound for the pure_ast case, under the three-part criterion in §4 below (which the
pure_ast setup satisfies). It is NOT unconditionally sound — spike 2 exhibits a shape-only import that lets the
importer prove `false` with both Alt-Ergo and Z3 — so the criterion is load-bearing and must be enforced by the mode's
design, not by convention.

---

## 1. Positive spike: the exact two-unit setup, proven

`spike1_positive.mlw` — "unit B" material harvested WITHOUT verifying B (record shape + abstract vals, signatures
only); "unit A" is the `_py_expr_binop` mirror shape, construct-only, `requires True / ensures True`:

```
(* POSITIVE SPIKE: structural-only shape-import, type-safety-only importer.
   "Unit B" material is harvested WITHOUT verifying B: a record SHAPE and
   abstract vals (type signatures + trivial contracts only).
   "Unit A" is the _py_expr_binop mirror shape: construct-only, ensures True. *)

module HarvestedShapes
  (* the IR-node sum the emitter targets *)
  type emit_ir =
    | IrInt int
    | IrBinOp string emit_ir emit_ir

  (* B's record SHAPE: field names + WhyML field types ONLY (no invariant) *)
  type binop = { left: emit_ir; op: int; right: emit_ir }

  (* abstract ops, trusted/verified elsewhere; signatures only *)
  val op_to_str (o: int) : string
  val to_ir (e: emit_ir) : emit_ir
end

module UnitA
  use HarvestedShapes

  let a (b: binop) : emit_ir
    requires { true }
    ensures  { true }
  = IrBinOp (op_to_str b.op) (to_ir b.left) (to_ir b.right)
end
```

Prover output (verbatim):

```
$ why3 prove -P alt-ergo spike1_positive.mlw
File spike1_positive.mlw:
Goal a'vc.
Prover result is: Valid (0.03s, 0 steps).

$ why3 prove -P z3 spike1_positive.mlw
File spike1_positive.mlw:
Goal a'vc.
Prover result is: Valid (0.01s, 6 steps).

$ grep -c '^\s*axiom ' spike1_positive.mlw
0
```

Both provers, Valid, **`^axiom` count 0**. The importer's type-safety VC discharges against the bare declaration; no
axiom, no assumed lemma, nothing borrowed from B's (unrun) verification.

## 2. Negative control: where shape-only import IS unsound — prover-confirmed

The trap named in wall §3 ("a field type that B only accepts under an invariant") is real. I built it both ways.

**Stripped world** (`spike2_negative_stripped.mlw`): B's type carries a B-side invariant `v >= 0`; the shape-only
harvest DROPS it; B's operation contract — a theorem *under* that invariant — is imported as a bare `val`:

```
module StrippedB
  use int.Int

  (* shape-only harvest of an invariant-bearing type: invariant LOST *)
  type pos = { v: int }

  (* B-side contract: sound in B's world ONLY because every pos satisfies
     v >= 0 there. Imported bare. *)
  val get (p: pos) : int ensures { result = p.v /\ result >= 0 }
end

module UnitA_stripped
  use int.Int
  use StrippedB

  let a () : unit
    ensures { true }
  = let p = { v = (-1) } in   (* legal: stripped shape has no invariant VC *)
    let x = get p in          (* x = -1 /\ x >= 0 *)
    assert { false }          (* PROVES => unsound *)
end
```

```
$ why3 prove -P alt-ergo spike2_negative_stripped.mlw
Goal a'vc.
Prover result is: Valid (0.03s, 1 steps).

$ why3 prove -P z3 spike2_negative_stripped.mlw
Goal a'vc.
Prover result is: Valid (0.01s, 18 steps).
```

**`assert { false }` is Valid on both provers.** Note the importer's *contract* is still `ensures { true }` — the
"importer asserts no value property in its contract" clause of the candidate criterion did NOT protect it. Mere
*construction* of `{ v = -1 }` (perfectly legal against the stripped shape) plus one invariant-dependent B contract
makes the importer's verification context inconsistent; everything downstream of it proves vacuously.

**Faithful world** (`spike2_negative_faithful.mlw`): identical code, invariant KEPT
(`type pos = { v: int } invariant { v >= 0 } by { v = 0 }`):

```
$ why3 prove -P alt-ergo spike2_negative_faithful.mlw
Goal pos'vc.
Prover result is: Valid (0.03s, 0 steps).        (* the `by { v = 0 }` witness *)
Goal a'vc.
Prover result is: Unknown (unknown) (0.03s, 3 steps).   (* -1 >= 0 blocks: B-side REJECTS *)
```

So the same importer body that "verifies" against the stripped harvest is **rejected** when B's real declaration is
in force — precisely the wall's feared scenario: A proving against a construct that has no sound B-side meaning.
Shape-only import is therefore NOT trivially sound; the criterion below is what separates the two regimes.

**Immunity check** (`spike3_immunity.mlw`): is a *plain* (invariant-free) shape immune even against a hostile
importer? A imports a bare record and a `val f (b: binop) : int ensures { true }`, constructs arbitrary field values,
and tries `assert { false }`:

```
module StrippedPlain
  type binop = { left: int; op: int; right: int }
  val f (b: binop) : int ensures { true }
end

module UnitA_hostile
  use StrippedPlain
  let a () : unit
    ensures { true }
  = let b = { left = (-1); op = (-1); right = (-1) } in
    let _x = f b in
    assert { false }   (* must NOT prove *)
end
```

```
$ why3 prove -P alt-ergo spike3_immunity.mlw
Goal a'vc.
Prover result is: Unknown (unknown) (0.03s, 2 steps).

$ why3 prove -P z3 spike3_immunity.mlw
Goal a'vc.
Prover result is: Unknown (sat) (0.01s, 7 steps).
```

Z3's **`Unknown (sat)`** is the strong form of the answer: it exhibited a *model* of the harvested theory in which
the goal's negation holds — the plain-shape harvest is consistent, and no importer, however adversarial, can derive
`false` from it. (`grep -c '^\s*axiom '` = 0 on all four spike files.)

## 3. Why the positive case is sound (the argument, not just the run)

With a plain record shape and signature-only vals, the harvested material is a **conservative extension** of the
importer's theory: a free algebraic type declaration plus uninterpreted function symbols always admit a model — the
record's value space is exactly the cartesian product of its field types, and the vals are arbitrary total functions.
Every model of A-without-B extends to a model of A-with-harvest, so A can prove nothing it could not already prove;
in particular, never `false`. This is exactly the module-boundary discipline of Why3 `use`/`clone`, Dafny/Viper
imports, and F* interfaces, and it is direction-safe both ways:

- **B → A**: the declaration carries no proof content, so nothing unproven about B is assumed by A.
- **A → B**: because the type has no invariant, B's value space for the type IS the full product space; any value A
  constructs is a legitimate B-side value, so A's outputs flowing into B's separately-verified code violate none of
  B's proof assumptions. (This second direction is what the negative control breaks: with an invariant, A can mint
  values outside B's proven value space.)

## 4. The criterion (derived from the spikes, refining the candidate)

Structural-only shape-import — A harvests B's `type_decl` without running B's verification — is **sound iff all
three hold**:

- **C1 — Verification-independence of the harvested declaration.** The harvested `type_decl` is a plain algebraic
  record/sum: field names + field types only, with NO attached type invariant, refinement predicate, constructor
  guard, or ghost-restricted constructor. Equivalently: B's verification pass can only ACCEPT or REJECT B — it can
  never ALTER what the declaration *means*. (Spike 2 is exactly a C1 violation: the harvest changed the type's value
  space by dropping the invariant, and both provers signed `false`.)
- **C2 — Nothing proof-bearing rides along in the unverified pass.** The structural pass harvests `type_decls` and
  raw signatures ONLY. It must not import B-side `ensures` clauses whose truth depends on B-side invariants (or on
  B's verification at all) — those are theorems of B's world and may be false in the stripped one. Spike 2 needed
  BOTH the stripped invariant AND the imported invariant-dependent `get` contract; spike 3 shows that with C2 held
  (trivial contracts), even a C1-plain shape resists a hostile importer. Any B-side contracts A does rely on must
  come from B's own verified pass or from the campaign's existing, ledger-accounted trust surface.
- **C3 — B is verified as a first-class unit elsewhere, from the same source of truth.** C1+C2 already make A's
  *local* proofs sound (conservative extension), so C3 is not about A's VCs — it is about the composed system's
  guarantee and the campaign's accounting: B's own obligations must be discharged in a separate pass, and the
  harvested shape must be derived from the same declaration source B's own verification uses, so the two passes
  cannot silently diverge.

**Refinement of the candidate criterion:** the candidate's second clause — "the importer's contract asserts no value
property of the imported fields" — is *neither necessary nor sufficient* and should be dropped as a soundness
condition. Not sufficient: spike 2's unsound importer had `ensures { true }` (construction alone poisoned it). Not
necessary: under C1+C2 the harvest is a conservative extension, so even a value-asserting importer contract could
not prove anything false (spike 3). `ensures True` remains good campaign hygiene (it keeps the scope cut honest),
but the load-bearing line is C1: **is the declaration's meaning independent of B's verification outcome?**

## 5. The pure_ast case against the criterion

Checked against the actual source (`src/pycsl/frontend/pure_ast.py`), not just the wall's description:

- **C1: holds.** `_NODE_SPEC` is a static dict literal (`'BinOp': ('expr', ('left','op','right'), None)`, line 190);
  the synthesized classes are plain field-bags. `AST.__init__` (lines 111–122) does bare `setattr` with only a
  positional-arity `TypeError` guard — no value validation, no `__post_init__`, no invariant anywhere. The harvested
  record `type binop = { left: emit_ir; op: int; right: emit_ir }` means the same thing whether or not Module3 ever
  runs on the file. The UB-7.6-rejected `Num`/`Str` compat shim is a *different* construct; the harvested decls do
  not derive from it, so skipping the check that rejects it does not touch their meaning.
- **C2: holds by construction** — IF the mode is built as specified: harvest `type_decls` only. The abstract ops the
  handlers call (`_py_op_to_str`, `_py_expr_to_ir`) enter as the mirror's own vals under the existing type-safety
  contract shape and existing trust accounting, not as contracts smuggled out of the unverified pass.
- **C3: holds, conditioned on one report claim.** The harvest and any future B-side verification both derive the
  node shapes from the one `_NODE_SPEC` table, so no divergence channel exists. The wall asserts pure_ast "is in the
  35-file suite and proves standalone" — I could not independently re-run that here, and note the surface tension
  with §3's statement that the full pipeline *crashes* on the compat shim in Module3; the verdict assumes the suite
  claim is true in whatever form the 35-file gate enforces (e.g. the shim is out of the mirrored perimeter). If
  pure_ast were in fact never verified anywhere, A's local proofs would still be sound, but the composed guarantee
  would silently weaken — C3 must stay a tracked suite fact, not folklore.

The importer side matches the positive spike exactly: `_py_expr_binop` and its ~20 siblings only CONSTRUCT
(`IrBinOp (op_to_str b.op) (to_ir b.left) (to_ir b.right)` shape), `requires True / ensures True`. **The pure_ast
case sits on the sound side of the criterion.**

## 6. Obligations the BREAKABLE verdict is conditioned on

1. **The mode must enforce C1/C2 mechanically, not by convention.** The structural pass should emit *only* record
   `type_decls` (and it should refuse — or at minimum flag — any decl that would carry an invariant/refinement if
   PyCSL ever grows type invariants). It must not harvest contract clauses from B in the same unverified pass.
   Spike 2 is the regression test for what happens otherwise.
2. **The hand-mapped per-node field-type table joins the fidelity surface.** A wrong field type cannot make the
   WhyML side inconsistent (still a conservative extension), but it is a mirror-fidelity bug (L1 plane). At minimum,
   cross-check the table's field *names/arity* mechanically against `_NODE_SPEC`; the byte-diff-0 and Why3 planes
   police the rest.
3. **Field-totality caveat (pre-existing, not introduced by this mode).** `AST.__init__` permits partially
   initialized nodes (unset field ⇒ `AttributeError` on read); the WhyML record model is total. This is the same
   modeling stance as the already-landed `@dataclass` conversions, but strictly weaker here (dataclasses force all
   fields; pure_ast does not). Under type-safety-only contracts on parser-produced nodes this is acceptable, and it
   applies identically whether the decl is declared in-file or harvested cross-file — flagged for the record, not a
   blocker for this question.
4. **C3 stays a suite-tracked fact**: pure_ast's own first-class verification status must remain visible in the
   35-file gate; the structural mode must never become the only pass that ever touches a dependency.

## 7. One-word verdict

**BREAKABLE** — structural-only shape-import is sound for the ~20 non-list `_py_expr_*` handlers, under criterion
C1–C3 (§4), all of which the pure_ast `_NODE_SPEC` setup satisfies; the negative control (§2) shows the criterion
is real and must be enforced by the mode's design.
