"""WL-05c (T7) — a LOCAL dict `del d[k]` is now modelled FAITHFULLY (verdict PROVEN).

`del d[k]` on a body-LOCAL dict lowers to the existing `map_update_none` op
(= `Map.set m k None`), so the key is genuinely CLEARED: after `d["a"]=7; del d["a"]`
the sound observation `"a" not in d` holds and this function returns 0. (Was a silent
no-op that unsoundly proved the key survived; now the deletion is real.)"""
_ = 0
from typing import Dict
#@ ensures \result == 0
def f() -> int:
    d: Dict[str, int] = {}
    d["a"] = 7
    del d["a"]
    if "a" in d:
        return 1
    return 0
