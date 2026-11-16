# lvU shutil.which: a PARAMETER named `shutil` shadows the module; the user method has an effect
# the law-free model drops. Caller catches the modelled OSError family.
import shutil
from typing import Optional


class W:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns self.n
    def which(self, c: str) -> Optional[str]:
        self.n = self.n + 1
        return None


#@ assigns \nothing
def where(shutil: W, cmd: str) -> Optional[str]:
    return shutil.which(cmd)


#@ ensures \result == 0
def caller() -> int:
    w = W()
    try:
        where(w, "sh")
    except OSError:
        return 0
    return w.n


if __name__ == "__main__":
    r = caller()
    print("VIOLATION contract" if r != 0 else "result", r)
