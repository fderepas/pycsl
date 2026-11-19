"""class-variant-impl.md (self-tcb-reduction driver-backlog item 3, §OUTCOME-CC):
a POSITIVE witness for the crosscheck_ir.py self-state boolean-predicate carrier.

A `@property`-derived 0-arg self method over a record with `Optional[Term]`
canon fields (the `IRCrossCheckResult` shape) whose body is the presence /
string-empty boolean fragment:

    return (not self.registry_raw) and (
        self.rocq_canon is not None or self.lean_canon is not None)

It lowers onto a total `let ircrosscheckresult__registry_skipped
(self: ircrosscheckresult) : bool` reading the REAL record fields: the string
field via the abstract `val pystr_eq self.registry_raw ""` (result VC-free —
a `val`, NOT an axiom; ledger 3) and each `Optional[Term]` canon field via an
inline `match self.<f> with Some _ -> true | None -> false end` over an
INHABITABLE `option int` (the `Optional[Term]` payload is opaque here — the
method reads presence only, so NO `term` inductive and NO `term_eq` are
needed). Gated on the (class, field) allow-list + `_has_opaque_term_fields`
-> fires on 0 other programs (corpus + every other mirror byte-identical).
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


# opaque base "Term" marker: the `Optional[Term]` canon fields carry it as an
# inhabitable option with an OPAQUE payload (`option int`).
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
            self.rocq_canon is not None or self.lean_canon is not None
        )
