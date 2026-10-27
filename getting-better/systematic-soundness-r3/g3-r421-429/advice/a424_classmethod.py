class K:
    @classmethod
    def of(cls, item: int) -> int:
        return item


#@ no_exception \all
def f() -> int:
    s = {K.of(1)}
    return len(s)
