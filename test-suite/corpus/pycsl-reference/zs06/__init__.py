# u69 witness 10406 (review rt78 t8, route #621 extended): the package loads its submodule b, then its
# sub-package `sub`, whose __init__ rebinds the attribute.
from . import b as b0
from . import sub as s0
