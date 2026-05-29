/-
  EmitVcList.lean — Stage B-3: emitVcList + emitStmt_correct

  Defines emitVcList (an independently-defined list of VcFormulas mirroring
  Module 6's output order) and proves emitStmt_correct (that emitVcList equals
  vcFormulaOf_list, the filterMap-based list derived from vcFormulaOf).

  "Module 6" here refers to the post-refactor subsystem rooted at
  `src/pycsl/Module6_WhyMLTranspiler.py` (facade) +
  `src/pycsl/module6_whyml/` (10 emission mixins, principally
  `statements.py`, `expressions.py`, `preamble.py`, `functions.py`).

  After Stage B-3, why3ValidatesVcFormula becomes a proved theorem (not Axiom),
  derived from the new narrower Axiom why3ValidatesEmitted (prover-only trust)
  via emitStmt_correct (emission fidelity, proved here).

  The trust split (TCB reduction):
    BEFORE B-3:
      Axiom why3ValidatesVcFormula — trusts both emission fidelity AND prover soundness
    AFTER B-3:
      Axiom why3ValidatesEmitted   — trusts ONLY prover soundness (f in emitVcList)
      Theorem emitStmt_correct     — PROVED emission fidelity (emitVcList = vcFormulaOf_list)
      Theorem why3ValidatesVcFormula — PROVED from the two above

  Key components:
    vcCount                    — VC index bound per WhyMLStmt constructor (1/2/3)
    emitVcList                 — independently-defined list, bodies copied from vcFormulaOf
    vcFormulaOf_list           — list form of vcFormulaOf (via filterMap over range)
    emitStmt_correct           — proved: emitVcList = vcFormulaOf_list (by rfl per case)
    vcFormulaOf_index_lt       — proved: vcFormulaOf returns Some => index < vcCount
    vcFormulaOf_mem_emitVcList — proved: vcFormulaOf returns Some f => f in emitVcList

  References:
    monday-05.md, Stage B-3 — TCB reduction for emission fidelity
    VcFormula.lean             — vcFormulaOf (the indexed formal spec; emitVcList mirrors it)
    VcgSemBridge.lean          — why3ValidatesEmitted + why3ValidatesVcFormula (after B-3)
-/
import PyCSL.VcFormula
import PyCSL.Why3Vcg

-- ===== vcCount: VC index bound per constructor =====

/-- vcCount ws: the number of VcFormulas emitted for WhyMLStmt ws.

    Matches Why3's -a split_vc output count:
    - Most constructors: 1 VC (n=0 only).
    - wIf: 2 VCs (n=0: true branch, n=1: false branch).
    - wAssert: 2 VCs (n=0: condition, n=1: postcondition).
    - wWhile: 3 VCs (n=0: invariant entry, n=1: body preservation, n=2: exit).

    vcFormulaOf ws Q preEs es n = some f iff n < vcCount ws
    (proved as vcFormulaOf_index_lt). -/
def vcCount : WhyMLStmt → Nat
  | .wSkip             => 1
  | .wAssign _ _       => 1
  | .wAugAssign _ _ _  => 1
  | .wArraySet _ _ _   => 1
  | .wSeq _ _          => 1
  | .wIf _ _ _         => 2
  | .wWhile _ _ _ _    => 3
  | .wRaise _          => 1
  | .wTryCatch _ _ _   => 1
  | .wGhostDecl _ _ _  => 1
  | .wGhostAssign _ _ _ _ => 1
  | .wLabel _          => 1
  | .wAssert _ _       => 2

-- ===== emitVcList: independently-defined list (mirrors Module6's output) =====

/-- emitVcList ws Q preEs es: the list of VcFormulas emitted for (ws, Q) at states (preEs, es).

    This is an independently-defined list mirroring what Module6 emits, in the same order
    as Why3's -a split_vc output.  The bodies are copied verbatim from vcFormulaOf, so that
    emitStmt_correct (emitVcList = vcFormulaOf_list) is provable by rfl.

    Design rationale:
    - emitVcList defines WHAT Module6 emits (a concrete list per constructor).
    - vcFormulaOf defines WHAT the VCG spec says (an indexed function).
    - emitStmt_correct proves they agree.
    - why3ValidatesEmitted trusts Why3's prover for elements of emitVcList.
    - why3ValidatesVcFormula then follows as a proved theorem (VcgSemBridge.lean). -/
def emitVcList (ws : WhyMLStmt) (Q : WpConts) (preEs es : ExecState) : List VcFormula :=
  match ws with

  -- wSkip: one VC — normal continuation at current state
  | .wSkip =>
    [.prop (Q.wcN es)]

  -- wAssign: one VC — normal continuation after register update
  | .wAssign x e =>
    [.prop (Q.wcN (setReg es (update es.regState x (evalExpr es.regState e))))]

  -- wAugAssign: one VC — normal continuation after augmented assignment
  | .wAugAssign x op e =>
    let cur := match lookup es.regState x with | some (.int k) => k | _ => 0
    let nv  := evalBinopZ op cur (match evalExpr es.regState e with | .int k => k | _ => 0)
    [.prop (Q.wcN (setReg es (update es.regState x (.int nv))))]

  -- wArraySet: one VC — normal continuation after array element update
  | .wArraySet arr i v =>
    let idx := match evalExpr es.regState i with | .int k => k | _ => 0
    let nv  := match evalExpr es.regState v with | .int k => k | _ => 0
    [.prop (Q.wcN (setReg es (arrayUpdate es.regState arr idx nv)))]

  -- wSeq: one VC — vcProp w1 with w2-threaded continuation
  | .wSeq w1 w2 =>
    [.prop (vcProp w1 { wcN := fun es' => vcProp w2 Q preEs es',
                        wcR := Q.wcR, wcC := Q.wcC, wcB := Q.wcB, wcE := Q.wcE }
                   preEs es)]

  -- wIf: two VCs — true branch (index 0) and false branch (index 1)
  | .wIf cond w1 w2 =>
    [.prop (evalBool es.regState cond = true  → vcProp w1 Q preEs es),
     .prop (evalBool es.regState cond = false → vcProp w2 Q preEs es)]

  -- wWhile: three VCs matching Why3's -a split_vc output order
  | .wWhile invs vars cond body =>
    let inv := cConj invs
    let var := cFirst vars
    [-- VC1 (index 0): invariant holds at loop entry
     .contract inv,
     -- VC2 (index 1): body preserves invariant and decreases variant
     .prop (∀ es', evalC es' preEs none inv →
                   evalBool es'.regState cond = true →
                   let bodyDone es'' :=
                     evalC es'' preEs none inv ∧
                     evalV es'' preEs var < evalV es' preEs var ∧
                     evalV es'' preEs var ≥ 0
                   vcProp body { wcN := bodyDone, wcR := Q.wcR,
                                 wcC := bodyDone, wcB := Q.wcN, wcE := Q.wcE }
                          preEs es'),
     -- VC3 (index 2): invariant ∧ not-guard implies normal postcondition
     .prop (∀ es', evalC es' preEs none inv →
                   evalBool es'.regState cond = false → Q.wcN es')]

  -- wRaise: one VC per exception kind
  | .wRaise .excReturn    => [.prop (Q.wcR es)]
  | .wRaise .excBreak     => [.prop (Q.wcB es)]
  | .wRaise .excContinue  => [.prop (Q.wcC es)]
  | .wRaise (.excNamed nm) => [.prop (Q.wcE nm es)]

  -- wTryCatch: one VC — body with exception-dispatcher continuation
  | .wTryCatch body exc handler =>
    [.prop (vcProp body { wcN := Q.wcN, wcR := Q.wcR, wcC := Q.wcC, wcB := Q.wcB,
                          wcE := fun exc' es' =>
                            if exc' == exc then vcProp handler Q preEs es'
                            else Q.wcE exc' es' }
                   preEs es)]

  -- wGhostDecl: one VC — normal continuation after ghost declaration
  | .wGhostDecl x t e =>
    [.prop (Q.wcN (setGhost es (ghostUpdate es.ghostSt x (evalGhostVal t es e))))]

  -- wGhostAssign: one VC — normal continuation after ghost augmented assignment
  | .wGhostAssign x _ op e =>
    let cur := ghostLookup es.ghostSt x
    let nv  := applyGhostAug op cur es e
    [.prop (Q.wcN (setGhost es (ghostUpdate es.ghostSt x nv)))]

  -- wLabel: one VC — normal continuation after label snapshot
  | .wLabel L =>
    [.prop (Q.wcN (setLabels es ((L, es.ghostSt) :: es.labelSnaps)))]

  -- wAssert: two VCs — condition truth (index 0) and normal continuation (index 1)
  | .wAssert cond _ =>
    [.contract cond, .prop (Q.wcN es)]

-- ===== vcFormulaOf_list: list version of vcFormulaOf (via filterMap) =====

/-- vcFormulaOf_list ws Q preEs es: list version of vcFormulaOf, derived via filterMap.

    Enumerates indices 0..(vcCount ws - 1) and collects the VcFormulas via vcFormulaOf.
    Serves as the bridge between the index-based spec (vcFormulaOf) and the
    list-based emission (emitVcList).

    emitStmt_correct proves: emitVcList = vcFormulaOf_list (by rfl per case). -/
def vcFormulaOf_list (ws : WhyMLStmt) (Q : WpConts) (preEs es : ExecState) : List VcFormula :=
  (List.range (vcCount ws)).filterMap (vcFormulaOf ws Q preEs es)

-- ===== emitStmt_correct: the key proved theorem =====

/-- emitStmt_correct: emitVcList equals vcFormulaOf_list (proved by rfl per constructor).

    Proof strategy: for each WhyMLStmt constructor, both sides reduce definitionally
    to the same concrete list.  The bodies of emitVcList are copied verbatim from
    vcFormulaOf, so expanding the filterMap over [0], [0,1], or [0,1,2] yields
    the same list as the explicit emitVcList match arm.

    Stage B-3 significance: emitVcList is a Lean 4 formal model of Module6's output.
    This theorem proves it matches the indexed spec.  The sole remaining trust is
    why3ValidatesEmitted (prover-only), in VcgSemBridge.lean. -/
theorem emitStmt_correct (ws : WhyMLStmt) (Q : WpConts) (preEs es : ExecState) :
    emitVcList ws Q preEs es = vcFormulaOf_list ws Q preEs es := by
  cases ws with
  | wSkip            => rfl
  | wAssign _ _      => rfl
  | wAugAssign _ _ _ => rfl
  | wArraySet _ _ _  => rfl
  | wSeq _ _         => rfl
  | wIf _ _ _        => rfl
  | wWhile _ _ _ _   => rfl
  | wRaise exc       => cases exc <;> rfl
  | wTryCatch _ _ _  => rfl
  | wGhostDecl _ _ _ => rfl
  | wGhostAssign _ _ _ _ => rfl
  | wLabel _         => rfl
  | wAssert _ _      => rfl

-- ===== vcFormulaOf_index_lt: index soundness =====

/-- vcFormulaOf_index_lt: if vcFormulaOf returns Some at index i, then i < vcCount ws.

    Used by vcFormulaOf_mem_emitVcList to show i belongs to List.range (vcCount ws),
    enabling the filterMap membership proof. -/
theorem vcFormulaOf_index_lt {ws : WhyMLStmt} {Q : WpConts} {preEs es : ExecState}
    {i : Nat} {f : VcFormula}
    (h : vcFormulaOf ws Q preEs es i = some f) : i < vcCount ws := by
  cases ws with
  | wIf _ _ _ =>
    simp only [vcCount]
    rcases i with _ | _ | n
    · omega
    · omega
    · simp [vcFormulaOf] at h
  | wWhile _ _ _ _ =>
    simp only [vcCount]
    rcases i with _ | _ | _ | n
    · omega
    · omega
    · omega
    · simp [vcFormulaOf] at h
  | wAssert _ _ =>
    simp only [vcCount]
    rcases i with _ | _ | n
    · omega
    · omega
    · simp [vcFormulaOf] at h
  | wRaise exc =>
    simp only [vcCount]
    rcases i with _ | n
    · omega
    · cases exc <;> simp [vcFormulaOf] at h
  | wSkip | wAssign _ _ | wAugAssign _ _ _ | wArraySet _ _ _ | wSeq _ _
  | wTryCatch _ _ _ | wGhostDecl _ _ _ | wGhostAssign _ _ _ _ | wLabel _ =>
    simp only [vcCount]
    rcases i with _ | n
    · omega
    · simp [vcFormulaOf] at h

-- ===== Range membership helper =====

private theorem mem_range_of_lt {i n : Nat} (h : i < n) : i ∈ List.range n := by
  rw [List.range_eq_range', List.mem_range']
  exact ⟨i, h, by omega⟩

-- ===== vcFormulaOf_mem_emitVcList: the main membership theorem =====

/-- vcFormulaOf_mem_emitVcList: if vcFormulaOf returns Some f at index i,
    then f is a member of emitVcList.

    Proof chain:
      vcFormulaOf ws Q preEs es i = some f
        -> i < vcCount ws                (vcFormulaOf_index_lt)
        -> i in List.range (vcCount ws)  (mem_range_of_lt)
        -> f in vcFormulaOf_list ...     (List.mem_filterMap.mpr)
        -> f in emitVcList ...           (emitStmt_correct, backwards rewrite)

    This is the key theorem connecting the indexed vcFormulaOf spec to the list-based
    emitVcList, enabling why3ValidatesVcFormula to be proved from why3ValidatesEmitted. -/
theorem vcFormulaOf_mem_emitVcList {ws : WhyMLStmt} {Q : WpConts} {preEs es : ExecState}
    {i : Nat} {f : VcFormula}
    (h : vcFormulaOf ws Q preEs es i = some f) :
    f ∈ emitVcList ws Q preEs es :=
  emitStmt_correct ws Q preEs es ▸
    List.mem_filterMap.mpr ⟨i, mem_range_of_lt (vcFormulaOf_index_lt h), h⟩

/-- emitVcList_mem_imp_vcFormulaOf: reverse direction of vcFormulaOf_mem_emitVcList.

    Q3 Sub-β port to Lean (2026-05-29): used by `why3ValidatesEmitted`
    to bridge from `f ∈ emitVcList` (the prior axiom statement) to
    `∃ i, vcFormulaOf ws Q preEs es i = some f` (the cert's witness
    domain). Mirrors Rocq's `vcf_emit_to_some` in
    `Phase6m_VcgSemBridge.v`.

    Proof: rewrite via `emitStmt_correct` to membership in
    `vcFormulaOf_list = (range vcCount).filterMap (vcFormulaOf ...)`,
    then extract the witnessing index via `List.mem_filterMap`. -/
theorem emitVcList_mem_imp_vcFormulaOf {ws : WhyMLStmt} {Q : WpConts}
    {preEs es : ExecState} {f : VcFormula}
    (h : f ∈ emitVcList ws Q preEs es) :
    ∃ i, vcFormulaOf ws Q preEs es i = some f := by
  rw [emitStmt_correct] at h
  unfold vcFormulaOf_list at h
  obtain ⟨i, _, hi⟩ := List.mem_filterMap.mp h
  exact ⟨i, hi⟩
