# u69 witness 10406 (review rt78 t8): a SUB-PACKAGE __init__ stores the sibling module c into its parent
# package's attribute `zs06.b` through an alias, at import time.
from .. import c as c0
import zs06 as _p
_p.b = c0
