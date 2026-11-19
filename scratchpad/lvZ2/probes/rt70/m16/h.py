from pathlib import Path


#@ ensures True
#@ assigns \nothing
def mk(s: str):
    return Path(s)
