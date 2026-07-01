"""self-field-dict-witness.py — typed-ir-for-b-ceiling.md §12 (self-field dict reflection).

`self.<dict[str,str]-field>.get(key)` reads the DECLARED record map field via
`Map.get self.<field> (str_hash_op key)` returning a `string`, so `self.types.get(name)
== "str"` routes through `str_eq_op` — not the opaque `get_types` over an int-coarsened
field. This is what `_handle_assign_stmt`'s `self._current_symbol_table.get(target)` needs.

Run: PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/self-annotate/self-field-dict-witness.py
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
        if self.types.get(name) == "str":     # self.<dict[str,str]-field>.get -> Map.get, str value
            return 1
        return 0
