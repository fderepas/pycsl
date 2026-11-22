# u66 control 10381 (route #621): the package __init__ binds the submodule `b` itself (`from . import b`)
# and an alias of it under a name that is no submodule, so the attribute `zr81.b` is the submodule.
from . import b
from . import b as b1
