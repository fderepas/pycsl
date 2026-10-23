"""class-variant-impl.md (self-tcb-reduction driver-backlog item 3, §OUTCOME-CC):
the DISCRIMINATING TWIN of 0962 — the non-facade (mutation) lock.

Identical to 0962 EXCEPT the first presence-tested canon field is
`registry_canon` (not `rocq_canon`). The emitted body therefore reads
`match self.registry_canon with Some _ -> ...` where 0962 reads
`match self.rocq_canon with ...` — a BYTE-DIFFERENT emission for the
discriminated field. It PROVES (the carrier forces `ensures True`; there is
no oracle to collapse to), so the mutation test + emitted-vacuity are the
non-facade lock: the record field genuinely FLOWS into the `.mlw`.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


class Term:
    pass


@dataclass
class IRCrossCheckResult:
    registry_raw: str = ""
    rocq_canon: Optional[Term] = None
    lean_canon: Optional[Term] = None
    registry_canon: Optional[Term] = None

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def registry_skipped(self) -> bool:
        return (not self.registry_raw) and (
            self.registry_canon is not None or self.lean_canon is not None
        )
