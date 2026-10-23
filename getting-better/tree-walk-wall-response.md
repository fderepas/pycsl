# tree-walk-wall-response.md — independent review of tree-walk-wall.md §7

Independent reviewer. Inputs: `getting-better/tree-walk-wall.md` + the repository + Why3 1.8.2
(Alt-Ergo 2.6.2, Z3 4.13.3). No access to the authoring agents' transcripts. Gate R satisfied:
three hand `.mlw` spikes written and proved (§1 below), commands + outputs cited verbatim.

## Verdict up front

**CONFIRM §7 — R1 is feasible. Proceed to an impl plan**, with four REFINEs that the plan must
absorb (§1.3, §1.4) and one REFUTE inside R2's scope (§3.2). The recursive ∨-existence-fold over
the stmt_ir/emit_ir tree discharges its termination VCs, proves the has-Raise/evil-twin pair
non-vacuously on BOTH provers, and is axiom-free. The report's prime suspect — mutual stmt↔expr
descent termination — is a **non-issue**, because the reference is one-directional (§2.2). The
real termination subtlety, found by oracle and not named in the report, is elsewhere: **the
certified Phase2d size measure ALONE does not discharge the fold's variant** (§1.3).

---

## 1. Gate R — the hand `.mlw` spikes (mandate item 1)

Three spikes, identical except for the `variant` style, in the session scratchpad
(`spike_A_single.mlw`, `spike_B_lex.mlw`, `spike_C_structural.mlw`). Faithful miniature of the
emitted theory:

- `eir/el` mutual expr ADT (mirrors `emit_ir`/`irlist`, preamble.py:3397/3463), with
  `kind_of`, `size_e`/`size_el`;
- `sir/sl` mutual stmt ADT (mirrors `stmt_ir`/`stmt_list`, preamble.py:4096-4115), with
  `stmt_kind_of`, and `size_s`/`size_sl` mirroring the emitted `size_stmt`/`size_slist`
  **exactly**: `size_sl (SLCons h t) = size_s h + size_sl t` (NO `+1`, preamble.py:4167-4168 /
  Phase2d_StmtIR.v:218), and `size_s` does NOT descend into `eir` (Phase2d header (d));
- `sir` carries `eir` children; `eir` never mentions `sir` (one-directional, as in the real block);
- `tree_has_raise`/`sl_has_raise`: the mutual recursive ∨-existence-fold (the `_body_has_raise`
  discriminant); `tree_has_call`/`sl_has_call` + a PRIOR standalone `eir_has_call`/`el_has_call`:
  the `_body_has_diverging_construct` expr-descent leg;
- drivers: `tree1` with an `SRaise` 3 levels deep (While → If → body), `tree2` the evil twin
  (same shape, `SPass` in place of `SRaise`), `tree3`/`tree4` the Call-in-While-test pair, and a
  `VacuityCanary` module whose goal (`tree_has_raise tree2 = True`) must stay unprovable.

Full source of the decisive spike (B) is inlined in Appendix A for reproducibility.

### 1.1 Spike B (lexicographic `variant { size, tag }`) — **all Valid, both provers**

```
$ why3 prove -P alt-ergo spike_B_lex.mlw
Goal size_e'vc.            Valid (0.06s, 180 steps)
Goal size_el'vc.           Valid (0.03s,  50 steps)
Goal eir_has_call'vc.      Valid (0.04s,  32 steps)
Goal el_has_call'vc.       Valid (0.04s,  30 steps)
Goal size_s'vc.            Valid (0.05s, 223 steps)
Goal size_sl'vc.           Valid (0.04s,  59 steps)   [z3 run; alt-ergo likewise]
Goal tree_has_raise'vc.    Valid (0.05s,  72 steps)
Goal sl_has_raise'vc.      Valid (0.04s,  45 steps)
Goal tree_has_call'vc.     Valid (0.04s,  72 steps)
Goal sl_has_call'vc.       Valid (0.04s,  45 steps)
Goal has_raise_deep.       Valid (0.04s,  22 steps)   tree_has_raise tree1 = True
Goal evil_twin_no_raise.   Valid (0.03s,  22 steps)   tree_has_raise tree2 = False
Goal has_call_in_test.     Valid (0.04s,  22 steps)   tree_has_call tree3 = True
Goal evil_twin_no_call.    Valid (0.03s,  20 steps)   tree_has_call tree4 = False
Goal recognizer_matches_kind. Valid (0.06s, 229 steps)
Goal canary_must_fail.     Timeout (5.00s)            <-- MUST not prove; correct
```

`why3 prove -P z3 spike_B_lex.mlw`: **all 15 obligations Valid** (0.01-0.02s each), canary
Timeout. Canary hardening: `-t 30` → Z3 `Timeout (30.00s, 97,738,694 steps)`; Alt-Ergo
non-Valid ("High failure" resource-out — not Valid, which is what matters). The evil twin's
`= False` goal being Valid while its `= True` canary is unprovable is the non-vacuity witness:
the fold genuinely distinguishes has-raise from no-raise, at depth, including a Call buried
inside a While TEST expression on the expr-descent leg.

**Axiom-free:** `grep -c 'axiom\|val ' spike_B_lex.mlw` → `0`. Pure inductive types +
`let rec function` only. No new axiom; ledger untouched.

### 1.2 Spike C (structural `variant { s }` / `{ l }`) — **all Valid**

Same 15 obligations Valid with alt-ergo (canary Timeout). This is the emitter's own native
idiom — the emitted `size`/`size_stmt` functions themselves use structural variants and the
preamble says so explicitly (preamble.py:3738-3742 "`variant { e }` is STRUCTURAL … discharges
natively"). Cheapest option.

### 1.3 Spike A (the report's literal claim: `variant { size_s s }` alone) — **FAILS**

```
$ why3 prove -P alt-ergo spike_A_single.mlw     (variant { size_s s } / { size_sl l })
Goal el_has_call'vc.       Timeout (5.00s)
Goal sl_has_raise'vc.      Timeout (5.00s)
Goal sl_has_call'vc.       Timeout (5.00s)
(all other obligations Valid)
$ why3 prove -P z3 spike_A_single.mlw           — same three Timeout
```

This is not prover weakness — the obligation is **mathematically false**. The list→head call
`sl_has_raise (SLCons h t) → tree_has_raise h` needs `size_s h < size_sl (SLCons h t)
= size_s h + size_sl t`, i.e. `size_sl t ≥ 1`, which fails for `t = SLNil`
(`size_sl (SLCons h SLNil) = size_s h` — EQUAL, not less). The no-`+1` cons is faithful to the
certified measure (Phase2d_StmtIR.v:218, preamble.py:4168), so **"terminating on the Phase2d
`size` measure", read literally as a single-component WhyML variant, is REFUTED**. Two proven
fixes, both spiked Valid on both provers:
- **(recommended) structural** `variant { s }` / `{ l }` (spike C) — the emitter's native idiom;
  the Phase2d size measure remains the CERTIFICATE-side (Rocq/Lean) termination witness, which
  is where it belongs;
- **lexicographic** `variant { size_s s, 0 }` / `{ size_sl l, 1 }` (spike B) — if the impl
  insists on the size measure, a constructor-class tag must break the tie. Note this leans on
  `size_s`'s `ensures { result >= 1 }` (already emitted, preamble.py:4152).

Note the asymmetry: the **expr side does not have this problem in the real theory** — the real
`emit_ir` `size` puts `+1` on every constructor including `IrCons` (preamble.py:3780), and the
strict-decrease lemmas already exist (`size_left_dec` etc., preamble.py:3809). My miniature gave
`el` the stmt-style no-`+1` measure deliberately, which is why `el_has_call'vc` fails in spike A
too — it reproduces the same non-strictness. Against the REAL emit_ir size, a single-measure
expr-side variant would discharge.

### 1.4 Two further shape corrections the spike surfaced

- **`ir_children : node → list node` (report §3 item 1) is not directly typeable.** A stmt
  node's children are heterogeneous (`stmt_list` bodies AND foreign `emit_ir` exprs); a single
  `list node` needs a wrapper sum (`NStmt sir | NExpr eir | …`) plus a list-sum measure and
  child-smaller-than-parent lemmas — pointless apparatus. The workable shape (spiked) is
  **inline per-constructor recursion**, which the report itself allows parenthetically. Drop
  the enumerator from the plan.
- **The string-keyed generic `tree_has_kind : string → ir → bool` hits a program-position
  string-equality gap.** `if stmt_kind_of s = k` fails to parse in a `let rec function` body:
  Why3's `string.String` has NO program `(=)` (only `string.OCaml`, an extraction module), and
  the project itself avoids `eq_string` (E-matching explosion, preamble.py:1191) and avoids
  `kind_of e = "K"` in program positions in favour of match-based recognizers
  (preamble.py:3631). The emitter-faithful shape is therefore **one specialized recognizer-fold
  per discriminant** (`tree_has_raise`, `tree_has_return`, …) with an `ensures`/lemma tying it
  to the `stmt_kind_of` spec — which also matches the Python source, where each stub has its own
  walker. Same conclusion kills the higher-order `tree_has : (node → bool) → node → bool` as a
  program function. The spike's `recognizer_matches_kind` goal (Valid, 229 steps) shows the
  kind_of-spec linkage proves fine.

## 2. Reality check on the reuse claim (mandate item 2)

### 2.1 CONFIRMED: the certified artifacts exist

- `src/formal-semantics/rocq/Phase2d_StmtIR.v`: `stmt_kind_of` at line 174 ("The tag
  discriminant — verbatim image of the WhyML `stmt_kind_of`"); the MUTUAL well-founded measure
  `size_stmt`/`size_slist` (+ `size_hlist`/`size_handler`/`size_mclist`/`size_mcase`) at lines
  204-236; positivity + strict-decrease lemmas (`size_stmt_pos`, `size_slist_lt_swhile`, the
  STry family) at lines 240-266.
- Lean twin: `src/formal-semantics/lean/PyCSL/StmtIR.lean` (`stmt_kind_of` at :121, mutual size
  at :146).
- The **WhyML twins are already emitted**: `stmt_kind_of` (preamble.py:4122) and
  `size_stmt`/`size_slist`/… with `ensures { result >= 1 } / >= 0` (preamble.py:4151-4186), plus
  `kind_of`/`size` + decrease lemmas on the emit_ir side (preamble.py:3561/3743/3809). The reuse
  claim is, if anything, understated — the fold needs no new theory scaffolding at all.

### 2.2 REFINE: "the MUTUAL stmt_ir/emit_ir tree" over-claims — and that's GOOD news

Phase2d_StmtIR.v header clause (d) (lines 40-47) states explicitly: **"NO MUTUAL RECURSION WITH
emit_ir"** — `emit` is an abstract Section variable, "neither `size_stmt` nor `size_slist`
descends into `emit`", and the emitted comment repeats it (preamble.py:4149-4150 "Does NOT
descend into the FOREIGN emit_ir expr children (one-directional)"). Consequences:

- The report's §6/§7 prime suspect — "the mutual stmt_ir↔emit_ir descent's termination" —
  **does not exist**. The expr-side fold is a PRIOR, standalone, separately-terminating
  definition; the stmt-side fold calls it as an already-total function. No cross-boundary
  variant is needed (spiked exactly so: `eir_has_call` defined first, `tree_has_call` calls it;
  all Valid).
- Conversely, the certified size measure does NOT cover expr descent — discriminants on the expr
  side (`Call`, `Result`, `Var`-name) rely on emit_ir's own `size`/structural variant, which
  exists (preamble.py:3743) but is a SEPARATE certificate lineage (Phase2c/tier3), not Phase2d.
  The report's single-sentence "reused from the certified ADTs" conflates the two; the impl plan
  should cite both.

## 3. Scope check (mandate item 3)

### 3.1 `_body_has_raise` as first target — CONFIRM, with one sharpening and one rival

Read at `src/pycsl/core_ir_semantic.py:748-766`: bool result, single stmt-side discriminant
(`node.get("stmt") == "Raise"`), no value extraction. Confirmed simplest of the stmt-side
walkers. Mirror stub confirmed `\trusted` at `src/self-annotate/src/core_ir_semantic.py:234-239`
(note: mirror path is `src/core_ir_semantic.py`, not `src/frontend/`). Sharpening the report
misses: because the reference is one-directional, a Raise can NEVER sit inside an emit_ir
subtree, so the faithful fold for `_body_has_raise` **needs no expr descent at all** — skipping
`eir` children is observationally identical to the Python walker descending into expr dicts and
finding no `"stmt"` key. First increment = stmt-side fold only.

Rival candidate: `_contains_result` (core_ir_semantic.py:644-651) is in PYTHON form already the
cleanest — a pure top-level `any()` recursion, no `found[0]` closure cell, no nested `def`. Its
discriminant is expr-side (`type == "Result"`) and its inputs are contract-clause/ProofAssert
expr trees (call sites :482, :631, :1065), so it is a SINGLE standalone eir-fold with no mutual
stmt block at all — simpler WhyML, but its param retype requires the contract-expr IR to be
covered by the emit_ir ctor set (Result/Old etc.), which is an extra check the report never
makes. Either order is defensible; if the emit_ir ctor coverage check passes, `_contains_result`
is the smaller first bite.

### 3.2 R2 "same fold, different discriminant" — CONFIRM for three, REFINE one, REFUTE one

- `_body_has_return` (:769-789): identical shape, `SReturn` recognizer. **CONFIRM.**
- `_body_has_diverging_construct` (:693-717): stmt-recognizer `∈ {While, For, CriticalSection}`
  **plus** the expr leg (`type == "Call"`), so it needs the standalone eir fold composed in —
  exactly the spiked `tree_has_call` shape (Valid). **CONFIRM**, one extra leg, already proven.
- `_contains_result`: single-sided eir fold. **CONFIRM** (see 3.1 caveat on ctor coverage).
- `_lemma_returns_value` (:913-937): **REFINE — a real second blocker, but shallow.** The
  discriminant is not a kind test: it matches `SReturn` then reads the VALUE and checks its kind
  `∉ {"None", "CSLNone"}` — in ADT terms a depth-2 pattern `SReturn (IrOSome v)` + a kind check
  on `v`. Same fold skeleton, but the recognizer inspects constructor ARGUMENTS (`iropt_ir` +
  emit_ir None-ctors). The report lists it BOTH in R2 ("cheap follow-on") and in Deferred —
  internally inconsistent; it belongs one notch above the pure-kind four, below the next item.
- `_lemma_calls_trusted` (:940-962): **REFUTE "same fold".** Three extra capabilities: (1) it
  returns a **string** (the callee name), not bool — a value-EXTRACTING fold with an
  option/string accumulator; (2) it returns the **FIRST** hit, so traversal ORDER is observable
  whenever two trusted calls coexist — ∨ is commutative, first-match is not, and the ADT's
  constructor-field order must be shown to match Python's `dict.values()` order (a fidelity
  obligation none of the bool folds have); (3) the `trusted` set param needs a set-of-strings
  model with membership. Move it to Deferred.
- `_union_c8_test_references_union_var` (:1617-1627): bool + `any()` (order-immaterial),
  expr-side, but needs the `union_vars` set-membership parameter — same fold + capability (3)
  only. Mildly deferred, as the report already says.

Net honest yield of the pure R1-shape fold: **4 stubs** (`_body_has_raise`, `_body_has_return`,
`_body_has_diverging_construct`, `_contains_result`), +1 with a depth-2 recognizer
(`_lemma_returns_value`), +2 more behind set-param / first-hit-order machinery. The report's
"~6 from one fold" is mildly optimistic but directionally right.

## 4. Honest limits of this review

- The spikes are miniatures (6 stmt ctors vs the real 21 + handler/match-case mutuals). The §6
  E-matching-explosion risk at FULL theory scale is not settled by a miniature; mitigating
  evidence: alt-ergo discharges every spike VC in 20-229 steps, and the full-scale theory
  already carries same-shaped mutual recursive functions (`size_stmt`, `sl_len`, `seq_to_sl`)
  plus the tier-3 decrease lemmas. Residual risk: real, small, and exactly what the impl plan's
  own Gate-B full-preamble spike must retire.
- I did not run the corpus byte-diff or the pipeline on a converted stub (no source edits
  allowed); byte-diff-0 neutrality of the eventual emitter change is asserted by the report, not
  verified here.
- Canary unprovability is evidenced by Timeout at 5s and 30s on both provers (plus the Valid
  `= False` twin), not by a countermodel; alt-ergo at 30s returned a resource-out
  ("High failure"), which is non-Valid but ugly.
- All prover runs used Why3 1.8.2 / Alt-Ergo 2.6.2 / Z3 4.13.3 as configured in this repo's
  environment. No oracle I needed was unavailable.

## 5. Bottom line for §7

- (a) "fail to discharge its `variant` at full theory scale" — **the variant discharges**, but
  NOT on the bare Phase2d size measure (spike A refutes that literal reading; proven
  mathematically non-strict at `SLCons h SLNil`). Structural or lexicographic-with-tag variants
  discharge on both provers (spikes B, C). Full-scale residual is E-matching volume, not
  well-foundedness.
- (b) "force a new axiom" — **no**: spike is axiom-free (`grep` 0; pure ADTs +
  `let rec function`).
- (c) "Why3 positivity/type wall on `ir_children`" — the ENUMERATOR as specified is ill-typed
  (heterogeneous children), but that is a formulation bug, not a wall: inline per-constructor
  recursion (also sanctioned by the report) has no positivity or type issue.
- Non-vacuity — **proven**: has-Raise-deep Valid, evil-twin-False Valid, evil-twin-True canary
  unprovable, on both provers; ditto the Call-in-test expr leg.

**R1: PROCEED to the impl plan**, shaped as: per-discriminant match-based recognizer folds
(not string-keyed, not higher-order), inline constructor recursion (no `ir_children`),
structural variants in WhyML (Phase2d size stays the Rocq/Lean-side witness — or lexicographic
`(size, tag)` if the size measure must appear in the WhyML variant), stmt-side-only fold for
`_body_has_raise`/`_body_has_return`, + the standalone eir fold for
`_body_has_diverging_construct`/`_contains_result`. Carve `_lemma_calls_trusted` (and the set-
param pair) OUT of the one-fold claim. No CERTIFIED-BOUNDARY verdict is warranted anywhere in
this scope.

---

## Appendix A — spike_B_lex.mlw (verbatim, for reproduction)

```
(* spike_B_lex.mlw — Gate R oracle for tree-walk-wall.md §7. *)
module TreeWalkSpike
  use int.Int
  use bool.Bool

  type eir = EVar string | EConst int | ECall string el | EBin eir eir
  with el = ELNil | ELCons eir el

  let function kind_of (e: eir) : string =
    match e with
    | EVar _ -> "Var" | EConst _ -> "Const"
    | ECall _ _ -> "Call" | EBin _ _ -> "BinOp"
    end

  let rec function size_e (e: eir) : int
    ensures { result >= 1 }
    variant { e }
  = match e with
    | EVar _ | EConst _ -> 1
    | ECall _ args -> 1 + size_el args
    | EBin a b -> 1 + size_e a + size_e b
    end
  with function size_el (l: el) : int
    ensures { result >= 0 }
    variant { l }
  = match l with ELNil -> 0 | ELCons h t -> size_e h + size_el t end

  let rec function eir_has_call (e: eir) : bool
    variant { size_e e, 0 }
  = match e with
    | EVar _ | EConst _ -> False
    | ECall _ _ -> True
    | EBin a b -> orb (eir_has_call a) (eir_has_call b)
    end
  with function el_has_call (l: el) : bool
    variant { size_el l, 1 }
  = match l with
    | ELNil -> False
    | ELCons h t -> orb (eir_has_call h) (el_has_call t)
    end

  type sir = SPass | SRaise | SExpr eir | SReturn eir
           | SWhile eir sl | SIf eir sl sl
  with sl = SLNil | SLCons sir sl

  let function stmt_kind_of (s: sir) : string =
    match s with
    | SPass -> "Pass" | SRaise -> "Raise" | SExpr _ -> "Expr"
    | SReturn _ -> "Return" | SWhile _ _ -> "While" | SIf _ _ _ -> "If"
    end

  (* mirrors emitted size_stmt/size_slist: NO eir descent, cons has NO +1 *)
  let rec function size_s (s: sir) : int
    ensures { result >= 1 }
    variant { s }
  = match s with
    | SPass | SRaise | SExpr _ | SReturn _ -> 1
    | SWhile _ b -> 1 + size_sl b
    | SIf _ b o -> 1 + size_sl b + size_sl o
    end
  with function size_sl (l: sl) : int
    ensures { result >= 0 }
    variant { l }
  = match l with SLNil -> 0 | SLCons h t -> size_s h + size_sl t end

  let rec function tree_has_raise (s: sir) : bool
    variant { size_s s, 0 }
  = match s with
    | SRaise -> True
    | SPass | SExpr _ | SReturn _ -> False
    | SWhile _ b -> sl_has_raise b
    | SIf _ b o -> orb (sl_has_raise b) (sl_has_raise o)
    end
  with function sl_has_raise (l: sl) : bool
    variant { size_sl l, 1 }
  = match l with
    | SLNil -> False
    | SLCons h t -> orb (tree_has_raise h) (sl_has_raise t)
    end

  let rec function tree_has_call (s: sir) : bool
    variant { size_s s, 0 }
  = match s with
    | SPass | SRaise -> False
    | SExpr e | SReturn e -> eir_has_call e
    | SWhile e b -> orb (eir_has_call e) (sl_has_call b)
    | SIf e b o -> orb (eir_has_call e)
                       (orb (sl_has_call b) (sl_has_call o))
    end
  with function sl_has_call (l: sl) : bool
    variant { size_sl l, 1 }
  = match l with
    | SLNil -> False
    | SLCons h t -> orb (tree_has_call h) (sl_has_call t)
    end

  constant tree1 : sir =
    SWhile (EVar "c")
      (SLCons SPass
        (SLCons (SIf (EConst 0) (SLCons SRaise SLNil) SLNil)
          SLNil))
  constant tree2 : sir =
    SWhile (EVar "c")
      (SLCons SPass
        (SLCons (SIf (EConst 0) (SLCons SPass SLNil) SLNil)
          SLNil))
  constant tree3 : sir =
    SWhile (EBin (EVar "x") (ECall "f" (ELCons (EConst 1) ELNil)))
      (SLCons SPass SLNil)
  constant tree4 : sir =
    SWhile (EBin (EVar "x") (EVar "y")) (SLCons SPass SLNil)

  goal has_raise_deep:      tree_has_raise tree1 = True
  goal evil_twin_no_raise:  tree_has_raise tree2 = False
  goal has_call_in_test:    tree_has_call tree3 = True
  goal evil_twin_no_call:   tree_has_call tree4 = False

  goal recognizer_matches_kind:
    forall s: sir. tree_has_raise s = True -> stmt_kind_of s = "Raise"
                   \/ (exists e: eir, b: sl. s = SWhile e b)
                   \/ (exists e: eir, b o: sl. s = SIf e b o)
end

module VacuityCanary
  use TreeWalkSpike
  goal canary_must_fail: tree_has_raise tree2 = True
end
```

Spike A = spike B with every `variant { X, n }` replaced by `variant { X }` (single measure) —
fails `sl_has_raise'vc`/`sl_has_call'vc`/`el_has_call'vc` on both provers. Spike C = structural
`variant { s }` / `{ l }` / `{ e }` — all Valid on alt-ergo.
