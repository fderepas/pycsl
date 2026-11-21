"""Helper for corpus 3452 (route #295): a callee that RETURNS its dict argument."""
from typing import Dict


#@ assigns \nothing
def iddh(x: Dict[int, int]) -> Dict[int, int]:
    return x
