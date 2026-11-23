# u66 witness 10380 (review rt76 r2, route #621): a package __init__ that first loads its submodule `b`
# (under another name) and then binds the NAME `b` to its sibling module `c`. CPython leaves the package
# attribute `zr80.b` bound to `c` while `zr80.b` is already in sys.modules.
from . import b as b0
from . import c as b
