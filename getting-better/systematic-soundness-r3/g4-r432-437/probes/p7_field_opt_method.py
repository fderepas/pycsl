from typing import Optional
class C:
    def __init__(self) -> None:
        self.s: Optional[str] = None
    #@ no_exception \all
    def m(self) -> int:
        return len(self.s.strip())
