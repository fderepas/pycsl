r"""Test 9891 -- W-hash (dict-value-model-r4 §2.5, expected PASS): the s362 SHAPE (report H4): `_record_key` returns `Tuple[PyVal, ...]` and the un-claimed caller `_merge_records_best_of_n` hashes it (`occ.get(k, 0)`, `occ[k]`, `key not in best`, `best[key]`; the loops of the mirror body are unrolled so the trusted body terminates trivially). The tuple's slots are TAGGED values, so the un-claimed sites are ADMITTED (ambient TypeError); at base every one was denied ("may be a list / dict / set", unconditional). Both are `\trusted`, as in the mirror (`src/self-annotate/src/pycsl.py`), so only the hashing pass judges the bodies; `main` PROVES.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ \trusted reviewer: wh4-witness
#@ assigns \nothing
def _record_key(rec: Dict[str, PyVal]) -> Tuple[PyVal, ...]:
    term = rec.get("term") or {}
    return (term.get("goal_name"), tuple(term.get("explanations") or []))


#@ \trusted reviewer: wh4-witness
#@ assigns \nothing
def _merge_records_best_of_n(rec: Dict[str, PyVal], other: Dict[str, PyVal]) -> Dict[str, PyVal]:
    order: List[Tuple[PyVal, ...]] = []
    best: Dict[Tuple[PyVal, ...], Dict[str, PyVal]] = {}
    occ: Dict[Tuple[PyVal, ...], int] = {}
    k = _record_key(rec)
    nseen = occ.get(k, 0)
    occ[k] = nseen + 1
    key = (k, nseen)
    if key not in best:
        order.append(key)
        best[key] = rec
    k2 = _record_key(other)
    key2 = (k2, occ.get(k2, 0))
    if key2 not in best:
        best[key2] = other
    return best[key]


#@ ensures \result == c + 1
def main(c: int) -> int:
    return c + 1


if __name__ == "__main__":
    r = {"term": {"goal_name": "g", "explanations": ["e"]}}
    print(_merge_records_best_of_n(r, r), main(0))
