# pure_lib/dc — pure-Python dataclasses module
# field/fields: Modelled. @dataclass decorator: Stubbed (uses exec/type).


class Field:
    def __init__(self, default, default_factory, init, repr_f, compare, kw_only):
        self.name = 0
        self.default = default
        self.default_factory = default_factory
        self.init = init
        self.repr_f = repr_f
        self.compare = compare
        self.kw_only = kw_only


#@ ensures \result._init == 1
def field(default=0, default_factory=0, init=1, repr_f=1, compare=1, kw_only=0) -> Field:
    return Field(default, default_factory, init, repr_f, compare, kw_only)


#@ ensures \result >= 0
def fields(class_or_instance) -> int:
    return 0


#@ ensures \result >= 0
def dataclass(cls) -> int:
    return cls


#@ ensures \result >= 0
def is_dataclass(obj) -> int:
    return 0
