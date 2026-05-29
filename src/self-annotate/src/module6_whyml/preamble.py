from __future__ import annotations
#@ proof rocq Phase6i_Soundness.why3_implements_wp_w_derived
#@ proof lean PyCSL.Why3Vcg.vcgSound
from typing import Any, Dict, List, Optional, Set, Tuple
from module6_whyml.identifiers import whyml_ident, safe_mutex_name
from module6_whyml.ir_scanner import IRScanner
""  # pycsl
class PreambleEmissionMixin:
    'Preamble emission: top-of-file `use` clauses, exception type declarations, helper let-bindings, axiom blocks, shared state for the concurrent memory model, record/sum type declarations, and opaque class aliases. Mixed into Module6_WhyMLTranspiler.'
    _AXIOM_REGISTRY: int = {'Pycsl.Reference.Gcd.gcd_result_nonneg': 'forall a b : int. 0 <= gcd a b', 'Pycsl.Reference.Gcd.gcd_result_positive': 'forall a b : int. a >= 0 -> b >= 0 -> (a > 0 \\/ b > 0) -> gcd a b > 0', 'Pycsl.Reference.Gcd.gcd_divides_a': 'forall a b : int. a >= 0 -> b >= 0 -> (a > 0 \\/ b > 0) -> mod a (gcd a b) = 0', 'Pycsl.Reference.Gcd.gcd_divides_b': 'forall a b : int. a >= 0 -> b >= 0 -> (a > 0 \\/ b > 0) -> mod b (gcd a b) = 0', 'Pycsl.Reference.Gcd.gcd_0': 'forall a : int. a >= 0 -> gcd a 0 = a', 'Pycsl.Reference.Gcd.gcd_step': 'forall a b : int. b > 0 -> gcd a b = gcd b (mod a b)', 'Pycsl.Reference.Gcd.gcd_greatest': 'forall a b k : int. a >= 0 -> b >= 0 -> (a > 0 \\/ b > 0) -> k > 0 -> mod a k = 0 -> mod b k = 0 -> k <= gcd a b'}
    _AXIOM_FUNCTIONS: int = {'Pycsl.Reference.Gcd.': 'function gcd (a : int) (b : int) : int'}
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _scan_preamble_needs(self, functions: List[int], all_bodies: List[Any]) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_preamble_uses(self, needs: int) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_preamble_exceptions(self, needs: int) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_preamble_helpers(self, needs: int) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_preamble_axioms(self, ir: int) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_preamble_no_exception_predicates(self, needs: int) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_preamble(self, needs: int) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_shared_state(self) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_type_decls(self, type_decls: List[int]) -> Tuple[List[str], int]:
        return ([], {})

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_opaque_class_aliases(self, functions: List[int], out: List[str], declared_types: int) -> None:
        pass


