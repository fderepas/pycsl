from typing import Any, Dict, List, Tuple

PyVal = Any

#@ \trusted
#@ assigns \nothing
def _rewrite_annotation_str(s: str, rename_map: Dict[Tuple[str, str], str]) -> str:
    return s

#@ assigns \nothing
def _rewrite_reads(
    ir_data: Dict[str, PyVal], rename_map: Dict[Tuple[str, str], str]
) -> int:
    n = 0
    for func in ir_data.get("functions", []):
        st = func.get("symbol_table") or {}
        new_st: Dict[str, str] = {}
        for k, v in st.items():
            new_st[k] = _rewrite_annotation_str(v, rename_map)
        ra = func.get("return_annotation")
        if isinstance(ra, str):
            n = n + 1
    return n
