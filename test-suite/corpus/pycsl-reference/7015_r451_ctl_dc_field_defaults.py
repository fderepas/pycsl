r"""Test 7015 -- route #451 (expected PASS): CONTROL -- dataclass fields `name: str = ""`, `alt: Optional[str] = None`, `retries: int = 3`; PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Optional
from dataclasses import dataclass
@dataclass
class Config:
    path: str
    name: str = ""
    alt: Optional[str] = None
    retries: int = 3
#@ no_exception \all
def f(path: str) -> int:
    c = Config(path)
    return len(c.name.strip()) + c.retries
