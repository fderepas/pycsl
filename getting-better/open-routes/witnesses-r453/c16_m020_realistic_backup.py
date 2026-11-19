from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

import shutil



#@ no_exception \all
def f(path: str) -> int:
    shutil.copy(path, path + '.bak')
    return len(path)


if __name__ == "__main__":
    try:
        r = f('/nonexistent/rt36.cfg')
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
