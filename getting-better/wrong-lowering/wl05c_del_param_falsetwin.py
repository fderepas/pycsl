"""WL-05c (T7) SOUNDNESS TWIN — a caller-visible `del d[k]` that CLAIMS the deleted key
survives must NOT prove (verdict UNPROVEN).

Standalone param `del d["a"]` under `requires "a" in d`; the contract falsely asserts
`ensures "a" in d` (the key still present after its own deletion). The `writes {d}`
frame is genuinely CHECKED, so this is UNPROVABLE — the deletion is not vacuous. If this
ever proved, the `del`→`map_update_none` model would be UNSOUND."""
_ = 0
from typing import Dict
#@ requires "a" in d
#@ ensures "a" in d
def rm(d: Dict[str, int]) -> None:
    del d["a"]
