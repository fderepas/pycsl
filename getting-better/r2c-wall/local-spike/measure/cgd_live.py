from typing import Any, Dict, List, Optional, Tuple

PyVal = Any


#@ requires True
#@ ensures True
#@ assigns \nothing
def _collect_generic_decls(ir_data: Dict[str, PyVal]) -> Dict[str, PyVal]:
    """Return `{generic_name: {"type_params": [...], "decl": type_decl_or_None,
    "methods": [function_ir, ...]}}` for every class/function carrying
    `type_params`. A generic class's methods are collected by `self_type`."""
    generics: Dict[str, PyVal] = {}
    for decl in ir_data.get("type_decls", []):
        # A5d / IR-key collision: `type_params` is written by TWO producers under
        # ONE key with TWO INCOMPATIBLE SHAPES. A PEP 484/695 generic class writes
        # `[{"name","bound","kind"}, ...]` (the ir_schema v1.4 shape monomorphization
        # is defined over); a `#@ datatype Option[T]` variant decl writes the BARE
        # NAMES `["T", ...]` (Module5_IREmitter, `kind == "variant"`). Reading a
        # variant's list as the dict shape crashed `_check_gt3_schema_only` with
        # `'str' object has no attribute 'get'` — an INTERNAL CRASH on what the
        # corpus (pycsl-reference/0540) documents as a clean refusal path.
        # A `#@ datatype`'s parametricity is NOT monomorphized: Module 6 lowers it
        # directly to a POLYMORPHIC Why3 variant (`type option 'a = Nothing | Just 'a`,
        # `preamble._fmt_variant`), so a variant decl is not a monomorphization
        # candidate at all and is skipped here rather than mis-read.
        if decl.get("kind") == "variant":
            continue
        tparams = decl.get("type_params")
        if tparams:
            generics[decl["name"]] = {
                "type_params": tparams, "decl": decl, "methods": [],
                "kind": "class",
            }
    for func in ir_data.get("functions", []):
        tparams = func.get("type_params")
        if tparams:
            generics[func["name"]] = {
                "type_params": tparams, "decl": None,
                "methods": [func], "kind": "function",
            }
    # Attach methods to their enclosing generic class.
    for func in ir_data.get("functions", []):
        self_type = func.get("self_type") or ""
        if self_type in generics and generics[self_type]["kind"] == "class":
            if func not in generics[self_type]["methods"]:
                generics[self_type]["methods"].append(func)
    return generics
