from typing import Any, Dict, List, Optional, Set
PyVal = Any

#@ requires True
#@ ensures True
#@ assigns \nothing
def _record_answer(rec: Dict[str, PyVal]) -> str:
    return (rec.get("prover-result") or {}).get("answer", "") or ""

#@ requires True
#@ ensures True
#@ assigns \nothing
def _record_is_valid(rec: Dict[str, PyVal]) -> bool:
    return _record_answer(rec) == "Valid"

#@ requires True
#@ ensures True
#@ assigns \nothing
def rsr(holder: Dict[str, PyVal]) -> Optional[List[str]]:
    sels: "List[str]" = []
    seen: "Set[str]" = set()
    for rec in holder.get("records", []):
        if _record_is_valid(rec):
            continue
        loc = (rec.get("term") or {}).get("loc") or {}
        fn, ln = loc.get("file-name"), loc.get("start-line")
        if fn is None or ln is None:
            return None
        s = f"{fn}:{ln}"
        if s not in seen:
            seen.add(s)
            sels.append(s)
    return sels
