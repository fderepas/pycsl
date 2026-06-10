"""PyCSL front-end package (Modules 1-5 + front-end helpers).

Relocated from the top-level src/pycsl package (refactor Phase C2a). This is a
pure relocation: no logic changed. Modules 6 / core_ir_semantic / ir_schema /
errors / exception_model remain top-level shared/core leaves.

Public pipeline classes are re-exported here for orchestrator convenience.
"""
from frontend.Module1_Ingestor import Module1_Ingestor
from frontend.Module2_Parser import Module2_Parser
from frontend.Module3_Weaver import Module3_Weaver
from frontend.Module4_SemanticAnalyzer import Module4_SemanticAnalyzer
from frontend.Module5_IREmitter import Module5_IREmitter
from frontend.ConcurrencyChecker import ConcurrencyChecker

__all__ = [
    "Module1_Ingestor",
    "Module2_Parser",
    "Module3_Weaver",
    "Module4_SemanticAnalyzer",
    "Module5_IREmitter",
    "ConcurrencyChecker",
]
