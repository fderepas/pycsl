import sys
import multi_file_lib.r326pkg

def _setup() -> None:
    sys.modules.update({"multi_file_lib.r326smod": sys.modules["multi_file_lib.r326pkg"]})
_setup()

#@ ensures \result == 0
#@ assigns \nothing
def noop() -> int:
    return 0
