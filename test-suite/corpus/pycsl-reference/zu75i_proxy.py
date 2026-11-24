def _fwd(self, name):
    raise AttributeError(name)


class P:
    __getattr__ = _fwd


#@ ensures \result == 3
#@ assigns \nothing
def three() -> int:
    return 3
