from pathlib import Path


#@ ensures True
#@ assigns \nothing
def mk(s: str) -> Path:
    return Path(s)
