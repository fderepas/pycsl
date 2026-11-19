"""Helper for corpus 8681-8689 (route #555): results of a program module's functions."""
from typing import Optional

ZI: int = None
ZK = 5


def gn() -> None:
    return None


#@ no_exception \all
def gnone() -> Optional[int]:
    return None


#@ no_exception \all
def gopt(k: int) -> Optional[int]:
    if k > 0:
        return None
    return k


#@ no_exception \all
def gpipe(k: int) -> int | None:
    return None


#@ no_exception \all
def gintnone() -> int:
    return ZI


#@ no_exception \all
def gz() -> int:
    return ZK
