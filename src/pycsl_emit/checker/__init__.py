"""checker — verification round-trip via the pycsl CLI.

pycsl_runner.py invokes the existing pycsl entry point as a subprocess
and captures its goal-by-goal verdict. verdict.py is the structured
result type the rest of the system consumes.
"""

from .verdict import Verdict, ObligationStatus, ObligationResult
from .pycsl_runner import run_pycsl

__all__ = ["Verdict", "ObligationStatus", "ObligationResult", "run_pycsl"]
