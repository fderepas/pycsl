"""Evaluator — compares static and dynamic oracle results to classify outcomes."""

from dataclasses import dataclass
from typing import List


@dataclass
class Verdict:
    """Final verdict for one test file."""
    filepath: str
    static_result: str   # PASS, FAIL, ERROR, SKIP
    dynamic_result: str   # PASS, FAIL, ERROR, SKIP
    classification: str   # See below
    detail: str = ""


# Classification truth table:
#
# Static \ Dynamic |  PASS              |  FAIL              |  ERROR
# ─────────────────┼────────────────────┼────────────────────┼───────────
# PASS              |  SUCCESS           |  SOUNDNESS_BUG     |  DYNAMIC_ERROR
# FAIL              |  FALSE_POSITIVE    |  EXPECTED_FAIL     |  DYNAMIC_ERROR
# ERROR             |  STATIC_ERROR      |  STATIC_ERROR      |  BOTH_ERROR
# SKIP              |  SKIP              |  SKIP              |  SKIP


def classify(static_result: str, dynamic_result: str) -> str:
    """Classify the outcome based on static and dynamic results."""
    # Single-oracle modes: report PASS/FAIL directly
    if static_result == "SKIP" and dynamic_result == "SKIP":
        return "SKIP"
    if static_result == "SKIP":
        # Dynamic-only mode
        return {"PASS": "DYNAMIC_PASS", "FAIL": "DYNAMIC_FAIL",
                "ERROR": "DYNAMIC_ERROR"}.get(dynamic_result, "UNKNOWN")
    if dynamic_result == "SKIP":
        # Static-only mode
        return {"PASS": "STATIC_PASS", "FAIL": "STATIC_FAIL",
                "ERROR": "STATIC_ERROR"}.get(static_result, "UNKNOWN")

    table = {
        ("PASS", "PASS"): "SUCCESS",
        ("PASS", "FAIL"): "SOUNDNESS_BUG",
        ("PASS", "ERROR"): "DYNAMIC_ERROR",
        ("FAIL", "PASS"): "FALSE_POSITIVE",
        ("FAIL", "FAIL"): "EXPECTED_FAIL",
        ("FAIL", "ERROR"): "DYNAMIC_ERROR",
        ("ERROR", "PASS"): "STATIC_ERROR",
        ("ERROR", "FAIL"): "STATIC_ERROR",
        ("ERROR", "ERROR"): "BOTH_ERROR",
    }
    return table.get((static_result, dynamic_result), "UNKNOWN")


def evaluate(filepath: str, static_result, dynamic_result) -> Verdict:
    """Create a verdict from static and dynamic results."""
    classification = classify(static_result.overall, dynamic_result.overall)

    detail = ""
    if classification == "SOUNDNESS_BUG":
        detail = (f"CRITICAL: Static says PASS but dynamic says FAIL. "
                  f"Assertion: {dynamic_result.assertion_msg}")
    elif classification == "FALSE_POSITIVE":
        detail = "Static cannot prove contracts but dynamic execution succeeds."
    elif classification == "STATIC_ERROR":
        detail = f"Static oracle error: {static_result.error_msg}"
    elif classification == "DYNAMIC_ERROR":
        detail = f"Dynamic oracle error: {dynamic_result.error_msg}"

    return Verdict(
        filepath=filepath,
        static_result=static_result.overall,
        dynamic_result=dynamic_result.overall,
        classification=classification,
        detail=detail,
    )
