from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
@dataclass
class Report:
    passes: List[str] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)
    #@ requires True
    #@ ensures \length(self.passes) == \old(\length(self.passes)) + len(other.passes)
    #@ assigns self.passes, self.failures
    def extend(self, other: Report) -> None:
        self.passes.extend(other.passes)
        self.failures.extend(other.failures)
