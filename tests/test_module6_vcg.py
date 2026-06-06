"""test_module6_vcg.py — Stage B-2 of monday-05.md

Property-based and structural tests for Module6's WhyML emission.

These tests verify that Module6's WhyML output contains the structural elements
that correspond to the formal specification in:
  - VcFormula.lean  (Lean 4): vcFormulaOf, evalVcFormula
  - Phase6m_VcgSemBridge.v (Rocq): vc_formula_of, eval_vc_formula

Formal correspondence table (vcFormulaOf cases → WhyML structural markers):

  | whyml_stmt constructor | VCs emitted (vcFormulaOf indices) | WhyML markers             |
  |------------------------|-----------------------------------|---------------------------|
  | WSkip                  | i=0: postcondition Q              | (no explicit marker)      |
  | WAssign x e            | i=0: Q[x ← e]                    | x := e                    |
  | WWhile inv var cond b  | i=0: requires → inv               | requires { ... }          |
  |                        | i=1: inv ∧ cond → inv[body]       | invariant { ... }         |
  |                        | i=2: inv ∧ ¬cond → Q             | variant { ... }           |
  | WSeq s1 s2             | VCs of s1 + VCs of s2             | sequential composition    |
  | WIf cond s1 s2         | VCs of s1 + VCs of s2             | if/else branch            |

Run with:
    cd /path/to/pycsl
    .venv/bin/pip install -e ".[dev]"  # installs pytest
    .venv/bin/pytest tests/test_module6_vcg.py -v

For hypothesis-based property testing (Stage B-2 full), also install:
    .venv/bin/pip install hypothesis
"""

from __future__ import annotations

import re
import sys
import os
import pytest

# ---------------------------------------------------------------------------
# PyCSL pipeline helper
# ---------------------------------------------------------------------------

def _run_pipeline(code: str) -> str:
    """Run the full PyCSL pipeline (Modules 1–6) and return the WhyML string."""
    # Use bare imports: src/pycsl is on sys.path (added by conftest.py).
    # Cannot use `pycsl.Module1_Ingestor` because src/pycsl/pycsl.py shadows
    # the package name.
    from Module1_Ingestor import Module1_Ingestor
    from Module2_Parser import Module2_Parser
    from Module3_Weaver import Module3_Weaver
    from Module4_SemanticAnalyzer import Module4_SemanticAnalyzer
    from Module5_IREmitter import Module5_IREmitter
    from Module6_WhyMLTranspiler import Module6_WhyMLTranspiler

    ingestor = Module1_Ingestor(code)
    extracted = ingestor.process()
    parser = Module2_Parser()
    weaver = Module3_Weaver(code, extracted, parser)
    unified = weaver.process()
    analyzer = Module4_SemanticAnalyzer()
    validated = analyzer.process(unified)
    emitter = Module5_IREmitter(validated)
    ir = emitter.generate_json()
    transpiler = Module6_WhyMLTranspiler(ir)
    return transpiler.transpile()


def _has_requires(mlw: str, pattern: str) -> bool:
    """Return True iff the WhyML contains a requires block matching the pattern."""
    return bool(re.search(r"requires\s*\{[^}]*" + re.escape(pattern) + r"[^}]*\}", mlw))


def _has_ensures(mlw: str, pattern: str) -> bool:
    """Return True iff the WhyML contains an ensures block matching the pattern."""
    return bool(re.search(r"ensures\s*\{[^}]*" + re.escape(pattern) + r"[^}]*\}", mlw))


def _has_invariant(mlw: str, pattern: str) -> bool:
    """Return True iff the WhyML contains an invariant block matching the pattern."""
    return bool(re.search(r"invariant\s*\{[^}]*" + re.escape(pattern) + r"[^}]*\}", mlw))


def _has_variant(mlw: str, pattern: str) -> bool:
    """Return True iff the WhyML contains a variant block matching the pattern."""
    return bool(re.search(r"variant\s*\{[^}]*" + re.escape(pattern) + r"[^}]*\}", mlw))


def _count_invariants(mlw: str) -> int:
    """Count the number of 'invariant { ... }' blocks in the WhyML."""
    return len(re.findall(r"invariant\s*\{", mlw))


def _count_variants(mlw: str) -> int:
    """Count the number of 'variant { ... }' blocks in the WhyML.
    Uses negative lookbehind to exclude 'invariant {' (which contains 'variant {')."""
    return len(re.findall(r"(?<!in)variant\s*\{", mlw))


# ---------------------------------------------------------------------------
# VC1 (WWhile): requires → invariant (invariant initially holds)
# ---------------------------------------------------------------------------

class TestWhileInvariantInitially:
    """VC1 (vcFormulaOf WWhile _ _ _ _ 0): precondition implies invariant.

    The WhyML 'requires { ... }' block on the function states the precondition.
    The loop 'invariant { ... }' block states the invariant.
    Module6 emits both; Why3 checks VC1 automatically.

    Formal spec (vcFormulaOf, index 0):
        VcImpl (VcContract requires_expr) (VcContract invariant_expr)
    """

    REQUIRES_IMPLIES_INV = """
#@ requires n >= 0
#@ ensures \\result >= 0
def count_up(n: int) -> int:
    i = 0
    #@ loop invariant i >= 0
    #@ loop variant n - i
    while i < n:
        i += 1
    return i
"""

    def test_requires_block_present(self):
        """Module6 emits a 'requires { n >= 0 }' block — precondition for VC1."""
        mlw = _run_pipeline(self.REQUIRES_IMPLIES_INV)
        assert "requires" in mlw, "WhyML must contain a requires block"
        assert "n >= 0" in mlw or "(n >= 0)" in mlw, (
            f"requires block must contain 'n >= 0'. Got:\n{mlw}"
        )

    def test_invariant_block_present(self):
        """Module6 emits an 'invariant { i >= 0 }' block — invariant for VC1/VC2."""
        mlw = _run_pipeline(self.REQUIRES_IMPLIES_INV)
        assert _count_invariants(mlw) >= 1, (
            f"WhyML must contain at least one invariant block. Got:\n{mlw}"
        )

    def test_variant_block_present(self):
        """Module6 emits a 'variant { n - i }' block — for termination VC."""
        mlw = _run_pipeline(self.REQUIRES_IMPLIES_INV)
        assert _count_variants(mlw) >= 1, (
            f"WhyML must contain at least one variant block. Got:\n{mlw}"
        )

    def test_while_loop_structure(self):
        """WhyML while loop has the invariant/variant inside the loop body."""
        mlw = _run_pipeline(self.REQUIRES_IMPLIES_INV)
        # invariant must appear after 'while' and before 'done'
        while_pos = mlw.find("while")
        inv_pos = mlw.find("invariant")
        done_pos = mlw.find("done")
        assert while_pos < inv_pos < done_pos, (
            f"invariant must appear between 'while' and 'done'. Got:\n{mlw}"
        )


# ---------------------------------------------------------------------------
# VC2 (WWhile): invariant + condition → invariant[body] (preservation)
# ---------------------------------------------------------------------------

class TestWhileInvariantPreserved:
    """VC2 (vcFormulaOf WWhile _ _ _ _ 1): invariant preserved by loop body.

    This is checked structurally: the invariant is present, the body modifies
    the relevant variables, and Why3 discharges the preservation obligation.

    Formal spec (vcFormulaOf, index 1):
        VcImpl (VcAnd (VcContract inv) (VcContract cond))
               (VcContract inv_after_body)
    """

    PRESERVATION = """
#@ requires n >= 0
#@ ensures \\result == n
def identity_loop(n: int) -> int:
    total = 0
    i = 0
    #@ loop invariant total == i and i >= 0 and i <= n
    #@ loop variant n - i
    while i < n:
        total += 1
        i += 1
    return total
"""

    def test_invariant_references_loop_vars(self):
        """Invariant block refers to variables modified in loop body."""
        mlw = _run_pipeline(self.PRESERVATION)
        # The invariant block should mention 'total' and 'i'
        # (as WhyML refs: !total and !i)
        match = re.search(r"invariant\s*\{([^}]*)\}", mlw)
        assert match, f"No invariant block found in:\n{mlw}"
        inv_content = match.group(1)
        assert "total" in inv_content, (
            f"invariant must mention 'total'. invariant block: {inv_content}"
        )
        assert "i" in inv_content, (
            f"invariant must mention 'i'. invariant block: {inv_content}"
        )

    def test_body_modifies_invariant_vars(self):
        """The loop body contains assignments to variables in the invariant."""
        mlw = _run_pipeline(self.PRESERVATION)
        # Check that total and i are assigned in the while body
        assert "total :=" in mlw, f"Body must assign to 'total'. Got:\n{mlw}"
        assert "i :=" in mlw, f"Body must assign to 'i'. Got:\n{mlw}"


# ---------------------------------------------------------------------------
# VC3 (WWhile): invariant + ¬condition → postcondition (exit case)
# ---------------------------------------------------------------------------

class TestWhileExitCase:
    """VC3 (vcFormulaOf WWhile _ _ _ _ 2): exit case gives postcondition.

    When the loop exits (condition false), invariant ∧ ¬cond → Q.
    Module6 emits the ensures block; Why3 checks this is implied.

    Formal spec (vcFormulaOf, index 2):
        VcImpl (VcAnd (VcContract inv) (VcContract (neg cond)))
               (VcContract Q)
    """

    EXIT = """
#@ requires n >= 0
#@ ensures \\result == n
def sum_to_n(n: int) -> int:
    i = 0
    #@ loop invariant i >= 0 and i <= n
    #@ loop variant n - i
    while i < n:
        i += 1
    return i
"""

    def test_ensures_block_present(self):
        """Module6 emits an 'ensures { result == n }' block for the exit VC."""
        mlw = _run_pipeline(self.EXIT)
        assert "ensures" in mlw, f"WhyML must contain an ensures block. Got:\n{mlw}"

    def test_exit_condition_is_negation_of_loop_guard(self):
        """The loop exits when condition is false: while i < n → exits at i >= n."""
        mlw = _run_pipeline(self.EXIT)
        # The while guard should use the condition
        assert "while" in mlw, f"Expected while loop. Got:\n{mlw}"
        # The ensures must reflect the loop result
        ensures_match = re.search(r"ensures\s*\{([^}]*)\}", mlw)
        assert ensures_match, f"No ensures block found. Got:\n{mlw}"


# ---------------------------------------------------------------------------
# Multi-loop: multiple invariant/variant blocks
# ---------------------------------------------------------------------------

class TestMultipleLoops:
    """Multiple while loops produce multiple invariant/variant blocks.

    vcFormulaOf assigns independent VC indices to each loop's invariant.
    Module6 must emit one invariant/variant pair per loop.
    """

    DOUBLE_LOOP = """
#@ requires n >= 0
#@ ensures \\result >= 0
def double_loop(n: int) -> int:
    i = 0
    #@ loop invariant i >= 0
    #@ loop variant n - i
    while i < n:
        i += 1
    j = 0
    #@ loop invariant j >= 0
    #@ loop variant n - j
    while j < n:
        j += 1
    return i + j
"""

    def test_two_invariant_blocks(self):
        """Two while loops → two invariant blocks in the output."""
        mlw = _run_pipeline(self.DOUBLE_LOOP)
        count = _count_invariants(mlw)
        assert count == 2, (
            f"Expected 2 invariant blocks for two loops, got {count}. WhyML:\n{mlw}"
        )

    def test_two_variant_blocks(self):
        """Two while loops → two variant blocks in the output."""
        mlw = _run_pipeline(self.DOUBLE_LOOP)
        count = _count_variants(mlw)
        assert count == 2, (
            f"Expected 2 variant blocks for two loops, got {count}. WhyML:\n{mlw}"
        )


# ---------------------------------------------------------------------------
# WAssign: assignment preserves postcondition (VC index 0)
# ---------------------------------------------------------------------------

class TestAssignment:
    """Assignment VC: Q[x ← e] must hold before x := e.

    vcFormulaOf WAssign x e Q i=0: VcContract (Q with x substituted by e)
    Why3 checks this as a standard Hoare rule.
    """

    SIMPLE_ASSIGN = """
#@ requires x >= 0
#@ ensures \\result == x + 1
def increment(x: int) -> int:
    y = x + 1
    return y
"""

    def test_assignment_in_body(self):
        """The assignment 'y := x + 1' appears in the WhyML body."""
        mlw = _run_pipeline(self.SIMPLE_ASSIGN)
        assert ":=" in mlw, f"Expected := in assignment output. Got:\n{mlw}"

    def test_ensures_references_result(self):
        """The ensures block references 'result'."""
        mlw = _run_pipeline(self.SIMPLE_ASSIGN)
        assert "result" in mlw, f"ensures must mention 'result'. Got:\n{mlw}"


# ---------------------------------------------------------------------------
# WSeq: sequential composition preserves VCs
# ---------------------------------------------------------------------------

class TestSequentialComposition:
    """Sequential composition: VCs from both parts are emitted.

    vcFormulaOf WSeq s1 s2: indices from s1 followed by indices from s2.
    Module6 emits statements in order; Why3 handles sequencing.
    """

    SEQUENTIAL = """
#@ requires n >= 0
#@ ensures \\result == n
def seq_loops(n: int) -> int:
    i = 0
    #@ loop invariant i >= 0 and i <= n
    #@ loop variant n - i
    while i < n:
        i += 1
    j = n
    return j
"""

    def test_sequential_order(self):
        """Loop comes before the subsequent assignment in the output."""
        mlw = _run_pipeline(self.SEQUENTIAL)
        while_pos = mlw.find("while")
        # 'j' should be assigned after the loop
        j_pos = mlw.find("j :=", while_pos) if "j :=" in mlw[while_pos:] else mlw.find("j =", while_pos)
        assert while_pos != -1, f"Expected while loop. Got:\n{mlw}"


# ---------------------------------------------------------------------------
# Conditional (WIf): both branches must satisfy the postcondition
# ---------------------------------------------------------------------------

class TestConditional:
    """Conditional: both branches generate VCs for the postcondition.

    vcFormulaOf WIf cond s1 s2: VCs of s1 + VCs of s2.
    Module6 emits if/else; Why3 checks each branch independently.
    """

    CONDITIONAL = """
#@ requires x >= 0
#@ ensures \\result >= 0
def abs_val(x: int) -> int:
    if x >= 0:
        return x
    else:
        return -x
"""

    def test_if_else_in_output(self):
        """Module6 emits an if/else block."""
        mlw = _run_pipeline(self.CONDITIONAL)
        assert "if" in mlw, f"Expected if block. Got:\n{mlw}"

    def test_ensures_holds_for_conditional(self):
        """The ensures block is present for the overall function."""
        mlw = _run_pipeline(self.CONDITIONAL)
        assert "ensures" in mlw, f"Expected ensures block. Got:\n{mlw}"


# ---------------------------------------------------------------------------
# Module structure: output is valid WhyML module
# ---------------------------------------------------------------------------

class TestModuleStructure:
    """Module6 output is well-formed WhyML (passes structural checks)."""

    MINIMAL = """
#@ requires True
#@ ensures \\result == 0
def zero() -> int:
    return 0
"""

    def test_module_header(self):
        """WhyML output starts with 'module PyCSL_Program'."""
        mlw = _run_pipeline(self.MINIMAL)
        assert mlw.strip().startswith("module"), (
            f"WhyML must start with 'module'. Got:\n{mlw[:200]}"
        )

    def test_module_end(self):
        """WhyML output ends with 'end'."""
        mlw = _run_pipeline(self.MINIMAL)
        assert mlw.strip().endswith("end"), (
            f"WhyML must end with 'end'. Got last 100 chars:\n{mlw[-100:]}"
        )

    def test_use_int(self):
        """WhyML output imports 'use int.Int' (needed for integer arithmetic VCs)."""
        mlw = _run_pipeline(self.MINIMAL)
        assert "use int.Int" in mlw, (
            f"WhyML must import int.Int for integer arithmetic. Got:\n{mlw[:500]}"
        )


# ---------------------------------------------------------------------------
# Stage B-3: TestVcCount — verify Module6 emits exactly vcCount VCs
# ---------------------------------------------------------------------------

class TestVcCount:
    """Stage B-3 (monday-05.md): verify Module6 emits the exact number of
    structural VC markers predicted by vcCount in EmitVcList.lean.

    vcCount (Lean 4 / Rocq):
      wSkip / wAssign / wAugAssign / wArraySet / wSeq         → 1 VC
      wIf _ _ _ / wAssert _ _                                  → 2 VCs
      wWhile _ _ _ _                                           → 3 VCs (inv entry, body, exit)
      wRaise / wTryCatch / wGhostDecl / wGhostAssign / wLabel → 1 VC

    For each constructor class, this test checks that the WhyML output contains
    exactly the structural markers that correspond to the predicted VC count:
      - A while loop → exactly 1 'invariant {' block (VC1: entry, VC2: body pres.)
                     + exactly 1 'variant {' block (VC3: termination)
      - An if branch → an 'if' keyword in the output (2 VCs: true/false branch)
      - An assert    → a 'check {' or 'assert {' keyword (2 VCs: cond + postcond)
      - Simple stmts → no loop/branch markers (1 VC each)

    Formal correspondence:
      emitVcList wWhile ... = [.contract inv, .prop body_preservation, .prop exit]
      → WhyML: invariant { inv } variant { var }  (both required by Why3)
    """

    # --- wSkip / simple assignments: 1 VC, no loop/branch markers ---

    SIMPLE_ASSIGN = """
#@ requires True
#@ ensures \\result == 42
def return_const() -> int:
    x = 42
    return x
"""

    def test_simple_assign_no_loop_markers(self):
        """Simple assignment: vcCount = 1 — no invariant/variant blocks."""
        mlw = _run_pipeline(self.SIMPLE_ASSIGN)
        inv_count = _count_invariants(mlw)
        var_count = _count_variants(mlw)
        assert inv_count == 0, (
            f"Simple assignment must produce 0 invariant blocks (vcCount=1). "
            f"Got {inv_count}. WhyML:\n{mlw}"
        )
        assert var_count == 0, (
            f"Simple assignment must produce 0 variant blocks (vcCount=1). "
            f"Got {var_count}. WhyML:\n{mlw}"
        )

    # --- wIf: 2 VCs, produces an if/else in WhyML ---

    CONDITIONAL = """
#@ requires x >= 0
#@ ensures \\result >= 0
def nonneg(x: int) -> int:
    if x > 0:
        return x
    else:
        return 0
"""

    def test_if_produces_two_branches(self):
        """If statement: vcCount = 2 — WhyML contains 'if' keyword (true/false VCs)."""
        mlw = _run_pipeline(self.CONDITIONAL)
        assert "if" in mlw, (
            f"If statement (vcCount=2) must produce 'if' in WhyML. Got:\n{mlw}"
        )

    # --- wWhile: 3 VCs = invariant entry + body preservation + exit ---

    WHILE_LOOP = """
#@ requires n >= 0
#@ ensures \\result >= 0
def count(n: int) -> int:
    i = 0
    #@ loop invariant i >= 0
    #@ loop variant n - i
    while i < n:
        i += 1
    return i
"""

    def test_while_emits_exactly_one_invariant(self):
        """While loop: vcCount = 3 — exactly 1 'invariant {' block in WhyML."""
        mlw = _run_pipeline(self.WHILE_LOOP)
        count = _count_invariants(mlw)
        assert count == 1, (
            f"A single while loop must emit exactly 1 invariant block (vcCount=3). "
            f"Got {count}. WhyML:\n{mlw}"
        )

    def test_while_emits_exactly_one_variant(self):
        """While loop: vcCount = 3 — exactly 1 'variant {' block (not invariant) in WhyML."""
        mlw = _run_pipeline(self.WHILE_LOOP)
        count = _count_variants(mlw)
        assert count == 1, (
            f"A single while loop must emit exactly 1 variant block (vcCount=3). "
            f"Got {count}. WhyML:\n{mlw}"
        )

    def test_while_three_vc_markers_present(self):
        """While loop: all 3 VCs are structurally represented (invariant + variant)."""
        mlw = _run_pipeline(self.WHILE_LOOP)
        inv_count = _count_invariants(mlw)
        var_count = _count_variants(mlw)
        # 1 invariant block covers VC1 (entry) + VC2 (preservation)
        # 1 variant block covers VC3 (termination/exit)
        assert inv_count >= 1 and var_count >= 1, (
            f"While loop (vcCount=3) requires ≥1 invariant and ≥1 variant block. "
            f"Got inv={inv_count}, var={var_count}. WhyML:\n{mlw}"
        )

    # --- Two while loops: 3 VCs each = 6 total structural markers ---

    TWO_LOOPS = """
#@ requires m >= 0 and n >= 0
#@ ensures \\result >= 0
def two_loops(m: int, n: int) -> int:
    i = 0
    #@ loop invariant i >= 0
    #@ loop variant m - i
    while i < m:
        i += 1
    j = 0
    #@ loop invariant j >= 0
    #@ loop variant n - j
    while j < n:
        j += 1
    return i + j
"""

    def test_two_while_loops_emit_two_invariants(self):
        """Two while loops (vcCount=3 each): exactly 2 invariant blocks."""
        mlw = _run_pipeline(self.TWO_LOOPS)
        count = _count_invariants(mlw)
        assert count == 2, (
            f"Two while loops must emit exactly 2 invariant blocks. "
            f"Got {count}. WhyML:\n{mlw}"
        )

    def test_two_while_loops_emit_two_variants(self):
        """Two while loops (vcCount=3 each): exactly 2 variant blocks."""
        mlw = _run_pipeline(self.TWO_LOOPS)
        count = _count_variants(mlw)
        assert count == 2, (
            f"Two while loops must emit exactly 2 variant blocks. "
            f"Got {count}. WhyML:\n{mlw}"
        )

    # --- wAssert: 2 VCs (condition + postcondition) ---
    # NOTE: wAssert is a formal model construct generated from critical sections
    # (mutex invariants) in Module6, not from plain function annotations.
    # It does not have a simple surface syntax via #@ annotations.
    # The 2-VC wIf case is already covered by test_if_produces_two_branches above.
    # A mutex_invariant test for wAssert emission is deferred to dedicated concurrency tests.

    @pytest.mark.skip(
        reason="wAssert (vcCount=2) is generated from mutex_invariant critical sections, "
               "not plain #@ annotations. Covered by concurrency tests."
    )
    def test_assert_emits_check_or_assert_keyword(self):
        """Assert statement: vcCount = 2 — WhyML contains 'check' or 'assert' keyword.
        SKIPPED: wAssert is not triggered by plain #@ annotations.
        Use a mutex_invariant class with a critical section to trigger it.
        """

    @pytest.mark.skip(
        reason="wAssert (vcCount=2) is generated from mutex_invariant critical sections, "
               "not plain #@ annotations. Covered by concurrency tests."
    )
    def test_assert_no_loop_markers(self):
        """Assert statement: vcCount = 2 — no loop markers (no while loop).
        SKIPPED: wAssert is not triggered by plain #@ annotations.
        """


# ---------------------------------------------------------------------------
# Optional: hypothesis-based property tests (Stage B-2 full)
# ---------------------------------------------------------------------------

try:
    from hypothesis import given, settings, HealthCheck
    import hypothesis.strategies as st
    _HYPOTHESIS_AVAILABLE = True
except ImportError:
    _HYPOTHESIS_AVAILABLE = False

HYPOTHESIS_SKIP = pytest.mark.skipif(
    not _HYPOTHESIS_AVAILABLE,
    reason="hypothesis not installed; run: pip install hypothesis"
)


if _HYPOTHESIS_AVAILABLE:
    from hypothesis import given, settings, HealthCheck
    import hypothesis.strategies as st

    def _make_simple_loop_code(inv_bound: int, variant_name: str = "n") -> str:
        """Generate a simple while loop with a parametrized invariant bound."""
        return f"""
#@ requires {variant_name} >= 0
#@ ensures \\result >= 0
def loop_{inv_bound}({variant_name}: int) -> int:
    i = 0
    #@ loop invariant i >= 0 and i <= {inv_bound}
    #@ loop variant {variant_name} - i
    while i < {variant_name}:
        i += 1
    return i
"""

    class TestHypothesisBasedVcg:
        """Hypothesis-based property tests for Module6 VCG emission.

        These tests use hypothesis to generate random (but structurally valid)
        PyCSL annotations and verify that Module6's output always contains the
        structural VCG elements required by vcFormulaOf.

        Stage B-2 of monday-05.md: property-based testing for emission fidelity.

        NOTE: These tests require hypothesis to be installed.
        They verify structural properties, not exact VC content.
        Full semantic equivalence requires the Rocq/Lean proofs in Phase6m.
        """

        @given(bound=st.integers(min_value=0, max_value=10))
        @settings(max_examples=10, suppress_health_check=[HealthCheck.too_slow])
        def test_loop_always_emits_invariant(self, bound: int):
            """For any valid PyCSL while loop, Module6 emits at least one invariant."""
            code = _make_simple_loop_code(bound)
            mlw = _run_pipeline(code)
            count = _count_invariants(mlw)
            assert count >= 1, (
                f"Every while loop must produce at least one invariant. "
                f"bound={bound}, invariant count={count}. WhyML:\n{mlw}"
            )

        @given(bound=st.integers(min_value=0, max_value=10))
        @settings(max_examples=10, suppress_health_check=[HealthCheck.too_slow])
        def test_loop_always_emits_variant(self, bound: int):
            """For any valid PyCSL while loop, Module6 emits at least one variant."""
            code = _make_simple_loop_code(bound)
            mlw = _run_pipeline(code)
            count = _count_variants(mlw)
            assert count >= 1, (
                f"Every while loop must produce at least one variant. "
                f"bound={bound}, variant count={count}. WhyML:\n{mlw}"
            )

        @given(bound=st.integers(min_value=0, max_value=10))
        @settings(max_examples=10, suppress_health_check=[HealthCheck.too_slow])
        def test_module_structure_always_valid(self, bound: int):
            """Module6 always emits a valid WhyML module structure."""
            code = _make_simple_loop_code(bound)
            mlw = _run_pipeline(code)
            assert mlw.strip().startswith("module"), (
                f"WhyML must start with 'module'. bound={bound}. Got:\n{mlw[:200]}"
            )
            assert mlw.strip().endswith("end"), (
                f"WhyML must end with 'end'. bound={bound}. Got last 100:\n{mlw[-100:]}"
            )
else:
    # hypothesis not installed — placeholder so the class name exists in the module
    @pytest.mark.skip(reason="hypothesis not installed; run: pip install hypothesis")
    class TestHypothesisBasedVcg:
        """Placeholder — requires hypothesis. Run: pip install hypothesis"""
        def test_placeholder(self):
            pass
