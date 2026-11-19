from typing import Any, Dict
PyVal = Any

#@ ensures \result == "Valid"
#@ assigns \nothing
def answer_hit() -> str:
    rec: Dict[str, PyVal] = {"prover-result": {"answer": "Valid"}}
    return (rec.get("prover-result") or {}).get("answer", "") or ""

#@ ensures \result == "Valid"
#@ assigns \nothing
def top_hit() -> str:
    rec: Dict[str, PyVal] = {"answer": "Valid"}
    return rec.get("answer", "") or ""

#@ ensures \result == "Valid"
#@ assigns \nothing
def second_key_hit() -> str:
    rec: Dict[str, PyVal] = {"answer": "Valid", "time": 3}
    return rec.get("answer", "") or ""

#@ ensures \result == "Invalid"
#@ assigns \nothing
def top_twin() -> str:
    rec: Dict[str, PyVal] = {"answer": "Valid"}
    return rec.get("answer", "") or ""
