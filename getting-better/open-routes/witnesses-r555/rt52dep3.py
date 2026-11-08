from typing import Dict, List, Optional, Tuple

ZN = None
ZI: int = None
ZO: Optional[int] = None
ZL = [None]
ZLI: List[int] = [None]
ZD = {"a": None}
ZDI: Dict[str, int] = {"a": None}
ZT = (1, None)
ZTI: Tuple[int, int] = (1, None)
ZS: str = None
ZK = 5


#@ no_exception \all
def gz() -> int:
    return ZK


def gn() -> None:
    return None


#@ no_exception \all
def gnone() -> Optional[int]:
    return None


#@ no_exception \all
def gintnone() -> int:
    return ZI
