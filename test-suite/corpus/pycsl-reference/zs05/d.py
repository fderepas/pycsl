# u69 witness 10405 (review rt78 t4): a SIBLING submodule loads `zs05.b`, then stores the sibling module c
# into the package attribute `zs05.b` at import time (an attribute store, not a Name binding of __init__).
from . import b as b0
from . import c as c0
import zs05
zs05.b = c0
