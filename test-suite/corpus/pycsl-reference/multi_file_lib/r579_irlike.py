"""Route #579 corpus dependency (9274 / 9277): a USER module whose classes are spelled like pycsl / `ast` IR node
classes (`Name`, `Call`) but are ordinary records carrying a `kind` field."""
from dataclasses import dataclass


@dataclass
class Call:
    func: str
    kind: str


@dataclass
class Name:
    id: str
    kind: str
