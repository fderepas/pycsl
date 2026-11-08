# advice probe (route #440): 6650 with `path.rindex(".")` replaced by the row method `path.rfind(".")` -> VERIFIES
class Buffer:
    def rindex(self, v: int) -> int:
        return 0


#@ no_exception \all
def last_dot(path: str) -> int:
    return path.rfind(".")
