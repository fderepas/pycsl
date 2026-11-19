# lvU shutil.which: a PARAMETER named `shutil` shadows the module; the claim (frame of the
# parameter object) is on the function itself.
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


#@ ensures shutil.n == \old(shutil.n)
def where(shutil: W, cmd: str) -> Optional[str]:
    return shutil.which(cmd)


if __name__ == "__main__":
    w = W()
    where(w, "sh")
    print("VIOLATION contract" if w.n != 0 else "result", w.n)
