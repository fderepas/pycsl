# OPEN ROUTE #335 — AN INHERITED CLASS INVARIANT ASSUMES THE BASE CONSTRUCTOR'S FIELD VALUES FOR A SUBCLASS THAT NEVER RAN IT
**Status: OPEN (gen #37, 2026-10-24), Severity 1.** Red-team round 22; driver-reproduced on main (rc=0; CPython violates).
Witnesses `witnesses-r335/`: a subclass inherits the base's `#@ class invariant`; the inherited goal `_check_class_inv_s` assumes the BASE
constructor's field values (`forall s_n. s_n = 0 -> ...`) — wrong when `S.__init__` never calls super: class attribute `n = -1` + `__init__: pass`
(i35, CPython -1), `__init__` sets only another field (i36; `no_exception \all` proves, CPython AttributeError), `__init__(k)` + class attribute
`n = 3` (i37), a subclass property `x` returning 7 (i33), `class S(M, B)` where MRO runs `M.__init__` first (i38). A parameter `b: B` may hold a
subclass (default since #277), so it receives an invariant no subclass instance established. Controls hold when the subclass constructor
assigns the field itself (with or without super) and for grandchildren. Likely a residual of route #226 (inheritance section).
Repair: the inherited-invariant establishment goal for a subclass must be built from the subclass's ACTUAL construction (its own __init__ per
Python MRO: explicit super() calls inlined, otherwise base __init__ NOT run; class-attribute / property shadowing of invariant fields
considered) — or refuse a subclass of an invariant-carrying class whose __init__ does not provably call the base __init__ (and whose
class attributes/properties shadow invariant fields).
