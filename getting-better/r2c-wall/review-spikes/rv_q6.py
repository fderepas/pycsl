from typing import Any, Dict, List, Tuple

PyVal = Any

#@ \trusted
#@ assigns \nothing
def _rewrite_annotation_str(s: str, rename_map: Dict[Tuple[str, str], str]) -> str:
    return s

#@ assigns ir_data
def _rewrite_annotations(
    ir_data: Dict[str, PyVal], rename_map: Dict[Tuple[str, str], str]
) -> None:
    for func in ir_data.get("functions", []):
        st = func.get("symbol_table") or {}
        new_st = {}
        for k, v in st.items():
            new_st[k] = _rewrite_annotation_str(v, rename_map)
        func["symbol_table"] = new_st
        ra = func.get("return_annotation")
        if isinstance(ra, str):
            func["return_annotation"] = _rewrite_annotation_str(ra, rename_map)
