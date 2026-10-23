# Ghost-Handler wall — independent reviewer response

*Independent external review, 2026-07-12. Basis: `ghost-handler-wall.md` + the Why3 oracle only
(syntax references: the repo's proven `getting-better/composition-wall/*.mlw` spikes). No sub-loop
working files were read. The evidence is two hand-written spike files, RUN, not re-reasoned prose:*

- **`gh-spike.mlw`** — the positive spike. 22 goals, **ALL Valid** (Alt-Ergo 2.6.2, `-t 30`).
- **`gh-spike-controls.mlw`** — the negative controls. The 3 must-fail goals **fail under BOTH
  provers**; the 2 setup goals prove.
- `grep -c '^axiom ' gh-spike.mlw` = **0**; `grep -c '^axiom ' gh-spike-controls.mlw` = **0**.

Commands: `why3 prove -P alt-ergo -t 30 gh-spike.mlw`, cross-checked `why3 prove -P z3 -t 15`.
Provers installed: Alt-Ergo 2.6.2, Z3 4.13.3 (`why3 config list-provers`).

---

## 1. Q1 VERDICT (the crux): **SPLIT — SWAPPED is SOUND-AND-LEGITIMATE; SENTINEL is UNSOUND-AS-A-REDUCTION (a false reduction at the masked site)**

The single question "is a value-unfaithful projection sound?" has **two different answers**, because
the swap and the sentinel are not the same defect. The spike separates them empirically.

### 1.1 What the spike models

`gh-spike.mlw::Q1Projections`: the emit_ir ADT exactly as the report describes it —
`IrVar | IrStr | IrOther | IrBin string term term | IrSub term term`, a `size` measure
(`let rec function`, `ensures { result >= 1 }`), the three projectors verbatim (`left_of`,
`right_of`, `svalue_of`, each with the `IrOther ""` sentinel fall-through), and the decrease lemmas
as **proved** `lemma`/`let lemma` (never `axiom`). Then the handler shape, four ways, all under the
campaign's fixed contract `requires { true } / ensures { true } / variant { size t }`:

| Goal | Models | Alt-Ergo | Z3 |
|---|---|---|---|
| `size'vc` | measure well-defined, `>= 1` | Valid 0.10s | Valid 0.02s |
| `left_dec` | `is_bin t -> size (left_of t) < size t` | Valid 0.78s | Valid 0.01s |
| `right_dec'vc` | same, right child | Valid 0.06s | Valid 0.01s |
| `sentinel_dec'vc` | `is_bin t -> size (svalue_of t) < size t` | Valid 0.07s | Timeout 15s |
| `h_faithful'vc` | (a) recurse on real left, real right | **Valid** 0.05s | Valid 0.02s |
| `h_swapped'vc` | (b) recurse right-then-left (wrong table) | **Valid** 0.06s | Valid 0.02s |
| `h_sentinel'vc` | (c) one recursion on `svalue_of` = constant `IrOther ""` | **Valid** 0.05s | Valid 0.01s |
| `h_opaque'vc` | (d) no recursion at all — bare stub | **Valid** 0.04s | Valid 0.00s |

**Direct answer to the report's first sub-question: yes, (b) and (c) both DISCHARGE fully under
`ensures true` — and so does (d), the opaque stub.** The termination `variant` holds for the
sentinel because `size (IrOther "") = 1 < size t` whenever `is_bin t` (size ≥ 3): goal
`sentinel_dec'vc` is *Valid*. Prover output alone therefore cannot adjudicate Q1: everything on the
spectrum proves. The verdict has to come from **which termination obligation each variant
discharges**, and whether that obligation is the real handler's obligation or a substituted one.

### 1.2 The soundness argument — does the model's proof transfer to the real handler?

Under the fixed contract class, the entire non-trivial content of a handler conversion is its
per-recursion-site obligation: *"the argument passed to the recursive call is smaller than the
node."* (Everything else — match exhaustiveness, string building via total operations — is
discharged even by the opaque stub `h_opaque`, which is Valid at 6 prover steps.) So transfer of
the model's proof to the live handler reduces to: **does the model discharge, at every site where
the live handler recurses, the decrease obligation for the subtree the live handler actually
recurses into?**

**SWAPPED (b): yes — the obligation set is permuted, not substituted.** The live
`_handle_set_mem_expr` recurses on the node's two real children; `h_swapped` recurses on the node's
two real children. The multiset of subtrees entered is *identical* (`{left, right}` = `{right,
left}`); the lemma instances consumed (`left_dec`, `right_dec`) are exactly the two the faithful
handler needs, and the spike shows the faithful version proves with the same machinery
(`h_faithful'vc` and `h_swapped'vc`: Valid at the *same* step count, 98 steps — literally the same
proof, permuted). Every safety/termination fact the live handler needs is a fact the model's proof
established. The conversion **genuinely proves the live handler type-safe + terminating**. It
remains a *fidelity* defect (the mirror denotes a different value function), but under a contract
that never speaks about values, the theorem proved is the same theorem. Sound, legitimate — though
since §2 shows the faithful table is free, there is no reason to keep the swap.

**SENTINEL (c): no — the obligation is substituted, and the substitution is strictly weaker.**
The live `_handle_map_set` recurses (via `self._e(node.value)`) into the node's **real value
subtree**; its termination needs `size(value_child) < size(node)`. The model `h_sentinel` recurses
into the constant `IrOther ""`; its termination VC is `size (IrOther "") = 1 < size(node)` — a
tautology about a fresh leaf, **not the same obligation**. The model proves termination of a
function that *skips the recursion the live code performs*. That this is a genuine soundness gap —
not a pedantic one — is demonstrated by the runnable refutation in `gh-spike-controls.mlw`:

| Control goal | Models | Alt-Ergo | Z3 |
|---|---|---|---|
| `SentinelMasksNonTermination.live_bug'vc` | a live handler that, at the very position the table lowers to `svalue_of`, recurses on the (rebuilt) node ITSELF — non-terminating | **Timeout** 15s | **Timeout** 15s |
| `LeafProjectorNoGuard.no_guard'vc` | projector recursion without the shape guard (decrease false on leaves) | **Timeout** 15s | **Timeout** 15s |

(`live_bug`'s variant VC is `size t < size t` — analytically false by irreflexivity; the Timeout is
the prover correctly refusing, not weakness. `no_guard` shows the main spike's Valids depend on the
real shape-guard + child decrease — the provers are not rubber-stamping `variant { size t }`.)

The point: **`live_bug` (non-terminating) and the real `_handle_map_set` (terminating) both lower,
under the sentinel fall-through, to the SAME model `h_sentinel` — which is Valid.** A proof that
cannot distinguish a terminating live handler from a non-terminating one at the masked site is not
evidence about the live handler's termination at that site. The `\trusted` removal is therefore
**not justified by the proof performed**: it is a false reduction — the marker went away, but the
obligation it stood for was never discharged, it was replaced by an easier one. This is unsoundness
of the *reduction claim* (model→live transfer), not of Why3; Why3 correctly proved exactly what it
was given.

Note the sharp irony in the per-goal table: `sentinel_dec'vc` is the **hardest goal in the file**
(Z3 times out on it; only Alt-Ergo's case-split proof lands). The prover works hardest to establish
precisely the lemma whose truth is the problem.

### 1.3 The exact non-vacuity criterion (machine-checkable, spiked)

> **A projection-table conversion is a sound type-safety+termination reduction iff at EVERY
> recursion site of the live handler, the projector used, applied to the node shape this handler is
> dispatched on, returns a REAL structural child of the node — witnessed by a proved per-(shape,
> projector) CHILD-HOOD lemma — with the decrease lemma consumed at the site being that child's.**
> Permutation of children (swap) satisfies this. A projector that on the dispatch shape returns the
> sentinel constant violates it. An opaque stub violates it at every site.

This is not prose — it is checkable per site, and the spike checks it:

| Discriminator goal | Statement | Alt-Ergo | Z3 |
|---|---|---|---|
| `left_is_child_on_bin` | `left_of (IrBin op l r) = l` | Valid | Valid |
| `right_is_child_on_bin` | `right_of (IrBin op l r) = r` | Valid | Valid |
| `svalue_is_NOT_child_on_bin` | `svalue_of (IrBin op l r) = IrOther ""` | Valid | Valid |

`left_of`/`right_of` on `IrBin` can prove the child-hood witness; `svalue_of` on `IrBin` can only
prove that it returns the **constant** — i.e. it provably fails the criterion. A one-lemma-per-site
gate mechanically separates the ~21 sound conversions from the facade sites.

### 1.4 Consequences for the committed spectrum

- The **swap family** (~7 handlers incl. `set_mem`/`set_add`): convertible **now** — soundly even
  with the wrong-order table, and faithfully for free (§2). Not a facade.
- **`map_get`** (`dict→left_of, key→right_of`): passes the criterion (both sites hit real children).
  Sound.
- **`map_set`** (commit `5221ef3d` per the report), and any other conversion whose live handler
  recurses through an attr that falls through to the sentinel on that handler's dispatch shape:
  **false reduction at that site**. It should be re-done with a real third-child projector — which
  the spike shows is cheap and axiom-free (`Q1FaithfulThirdChild`: ternary constructor `IrTer` +
  `fst_of/snd_of/thd_of` + proved `fst_dec/snd_dec/thd_dec`; the fully faithful 3-recursion
  `h_map_set_faithful'vc` is **Valid**, both provers) — or reverted to `\trusted` until then.
  Sentinel projections that the live handler does **not** recurse through (a genuinely absent/unused
  attr) mask nothing and are harmless.

---

## 2. Q2 — faithful mechanism for the swap: **BOUNDED-FEATURE**

Oracle evidence: `h_faithful'vc` and `h_swapped'vc` are BOTH Valid (identical step counts). The
WhyML/prover side needs *nothing new* to accept either orientation — the entire swap problem lives
in the lowering table, not in the proof theory. And the disambiguating key is statically available:
the report itself states each live handler handles exactly one `ExprIR` subclass
(`_handle_set_mem_expr` ↔ `SetMemExpr`). So the fix is to key the name→projector table by the
**enclosing handler** (equivalently, by subtype, derived from the ExprIR schema's field order):
`(_handle_set_add_expr, "elem") → right_of` vs `(_handle_set_mem_expr, "elem") → left_of`. No new
axiom (the same two proved decrease lemmas serve both), no live-source change (the live code is
untouched; only the mirror's lowering table gains a key). For ≥3-child nodes the same move needs one
real constructor + projector + proved lemma each — `Q1FaithfulThirdChild` proves the whole pattern
Valid, axiom-free. Nothing here is a boundary; it is table engineering plus the §1.3 gate.

## 3. Q3 — the two singletons

**Q3a `_handle_ctor_test_expr` (`Array.make !arity "_"`): BOUNDED.**
Spike `Q3Arity`: abstract getter `val get_arity_safe … ensures { result >= 0 }`, then
`Array.make (get_arity_safe ()) "_"` under `requires true / ensures true` →
`mk_ctor_test'vc` **Valid** (Alt-Ergo 0.03s, Z3 0.01s), zero axiom declarations. The failing twin
(control `ArityNoContract`, getter with NO ensures) fails both provers (Timeout; correctly — an
unconstrained `int` can be negative). So one nonneg-safe contract on the getter discharges it.
*Caveat, stated honestly:* an `ensures` on an abstract `val` is an **assumed contract** — axiom-free
in the ledger sense (`grep '^axiom '` = 0) but trusted-stub-shaped; the clean closure is to
body-verify the getter (an arity count is plausibly nonneg-provable). Either way: bounded, not a
boundary.

**Q3b `_handle_mktuple_expr` (variadic `node.elts` fold): BOUNDED.**
Spike `Q3Mktuple`: `IrTuple (list term)`, a *list* projector `elts_of` (with the same Nil sentinel
fall-through discipline), mutual `size`/`size_list`, proved `elts_dec`, and the mutually recursive
`h_mktuple`/`fold_elts` under `ensures true` with `variant { size t } / { size_list l }` — all five
goals **Valid** under both provers, 0 axioms. (Consistent with the repo's own proven
`term-rewriter-spike.mlw`/`stmt-walker-spike.mlw`, which already prove list-child folds of this
shape.) The §1.3 criterion applies unchanged: `elts_of` on `IrTuple` returns the real child list,
and the fold enters only its members.

---

## 4. Exact per-goal results (the record)

`why3 prove -P alt-ergo -t 30 gh-spike.mlw` — **22/22 Valid**:
`size'vc` 0.10s · `left_dec` 0.78s · `right_dec'vc` 0.06s · `sentinel_dec'vc` 0.07s ·
`right_is_child_on_bin` 0.05s · `left_is_child_on_bin` 0.04s · `svalue_is_NOT_child_on_bin` 0.05s ·
`h_faithful'vc` 0.05s · `h_swapped'vc` 0.06s · `h_sentinel'vc` 0.05s · `h_opaque'vc` 0.04s ·
`size'vc`(Ter) 0.06s · `fst_dec` 0.46s · `snd_dec'vc` 0.05s · `thd_dec` 0.05s ·
`h_map_set_faithful'vc` 0.05s · `mk_ctor_test'vc` 0.03s · `size'vc`(Tuple) 0.05s ·
`size_list'vc` 0.04s · `elts_dec` 0.04s · `h_mktuple'vc` 0.04s · `fold_elts'vc` 0.03s.

`why3 prove -P z3 -t 15 gh-spike.mlw` — **21/22 Valid**, 1 Timeout: `sentinel_dec'vc`
(Alt-Ergo-Valid; prover-complementarity only, the goal is proved).

`why3 prove -P {alt-ergo,z3} -t 15 gh-spike-controls.mlw` — setup goals (`size'vc` ×2) Valid under
both; must-fail goals `live_bug'vc`, `no_guard'vc`, `mk_ctor_test_unsafe'vc` **Timeout under both**
(as required for non-vacuity of the whole spike).

Axiom audit: `grep -c '^axiom ' gh-spike.mlw` → `0`; `grep -c '^axiom ' gh-spike-controls.mlw` → `0`.
Every decrease fact is a proved `lemma`/`let lemma`. Abstract symbols carrying **no** assumptions:
`val cat` (string builder, contract-free). The single assumed contract is Q3a's
`ensures { result >= 0 }`, discussed above.

## 5. Honest limits

1. **The transfer argument is meta-level.** Why3 adjudicated each model; the claim "the swapped
   model's proof entails the live handler's type-safety+termination" rests on the obligation-multiset
   permutation argument (§1.2), which is a reviewer's argument about VC generation, not itself a
   machine-checked meta-theorem. The sentinel side, by contrast, is settled by a *runnable*
   refutation (Valid model vs failing faithful model of the same lowering), which is why I state the
   sentinel verdict with more force than the swap verdict.
2. **Hand model, not the mirror's actual emission.** I modeled the report's description of
   `_EMIT_IR_NODE_ATTRS`, the projectors and the handler shape; if the real emitted WhyML differs
   materially (e.g. handlers carry a `requires is_binop node` dispatch precondition, or `self._e` is
   an abstract non-recursive `val` in the mirror), the termination analysis shifts — though the
   criterion in §1.3 is shape-independent and still applies.
3. **Controls "fail" as Timeout, not as disproof** — Why3 does not refute. But both control VCs are
   analytically false (`size t < size t`; unconstrained `int` vs `0 <= n`), and both fail under two
   independent provers.
4. Z3 4.13.3 times out on `sentinel_dec'vc` where Alt-Ergo proves it in 0.07s (and pre-fix,
   Alt-Ergo timed out on two quantified lemmas Z3 proved instantly). One-prover results on
   quantified ADT lemmas here are prover-idiosyncratic; the reported record uses the union, with
   Alt-Ergo alone covering 22/22 on the final file.
5. I did not measure the blast radius over the ~21 committed conversions (which of them recurse
   through a sentinel-returning site on their dispatch shape); §1.3 gives the mechanical per-site
   test the team can run over its own table.

## 6. Recommendation in one line each

- **Swap family:** convert now; fix the table per-handler (§2) since it is free — accept-as-is is
  defensible but pointless when faithful costs nothing.
- **Sentinel sites where the live handler recurses through the attr:** treat as NOT reduced;
  re-convert on a real projector (`Q1FaithfulThirdChild` pattern) or restore `\trusted`.
- **Adopt the child-hood-witness lemma (§1.3) as a per-site gate** — it turns the campaign's
  "reads real accessors" prose rule into a provable obligation, and it is exactly the line that
  separates `h_swapped` (sound) from `h_sentinel` (facade) in this spike.
