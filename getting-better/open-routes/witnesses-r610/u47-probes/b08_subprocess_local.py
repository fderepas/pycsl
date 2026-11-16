# u47: a LOCAL named `subprocess` shadows the module; `subprocess.run(..)` is the user method.
import subprocess
from typing import List


class S:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns self.n
    def run(self, a: List[str], capture_output: bool, text: bool) -> int:
        self.n = self.n + 1
        return 0


#@ ensures \result == 0
def f(s: S) -> int:
    subprocess = s
    try:
        r = subprocess.run(["true"], capture_output=True, text=True)
    except OSError:
        return 0
    except ValueError:
        return 0
    except UnicodeDecodeError:
        return 0
    return s.n


if __name__ == "__main__":
    r = f(S())
    print("VIOLATION contract" if r != 0 else "result", r)
