"""Test 0800 — List[Dict[str,int]] element read composes with cleared-hash.

nested-list.md S3. A `List[Dict[str, int]]` param lowers to
`array (map string (option int))` — the outer `array` holds the PURE
`map string (option int)` cleared-hash dict model. So `a[i]` is a real
string-keyed map and `a[i][key]` is a faithful native-string `Map.get` (the
missing-key default is the ambient `0`, matching the flat-dict read convention;
faithful KeyError needs `#@ no_exception KeyError` as for any dict). No new axiom.
"""
_ = 0  # anchor
from typing import List, Dict

#@ requires 0 <= i and i < len(a)
#@ ensures \result == a[i][key]
def read_row_key(a: List[Dict[str, int]], i: int, key: str) -> int:
    return a[i][key]

if __name__ == "__main__":
    assert read_row_key([{"a": 1}, {"b": 2}], 1, "b") == 2
