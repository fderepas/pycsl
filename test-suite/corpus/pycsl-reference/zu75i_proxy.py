def _fwd(self: object, name: str) -> int:
    return 0


class P:
    __getattr__ = _fwd


#@ ensures \result == 3
#@ assigns \nothing
def three() -> int:
    return 3
