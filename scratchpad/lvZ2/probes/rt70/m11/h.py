from pathlib import Path
from g import Fp


#@ ensures True
#@ assigns \nothing
def mk(s: str) -> Fp:
    return Path(s)
