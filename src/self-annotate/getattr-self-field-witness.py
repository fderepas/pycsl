"""getattr-self-field-witness.py — typed-ir-for-b-ceiling.md §14 (getattr recognizer).

`getattr(self, "<field>", <default>).get(key)` — the emitter's DEFENSIVE self-field
access — is recognized as `self.<field>.get(key)` and routes to the real record map
field (self-field dict reflection §12), returning a `string` for a `dict[str,str]`
field. Not the opaque `get_1` over a dropped receiver. This is what
`_handle_assign_stmt`'s `getattr(self, "_current_symbol_table", {}).get(target)` needs.

Run: PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/self-annotate/getattr-self-field-witness.py
"""
from dataclasses import dataclass
from typing import Dict
def mutable_state(cls): return cls

@mutable_state
@dataclass
class Emitter:
    types: Dict[str, str]

    #@ ensures True
    def is_str_typed(self, name: str) -> int:
        if getattr(self, "types", {}).get(name) == "str":   # getattr-then-get idiom
            return 1
        return 0
