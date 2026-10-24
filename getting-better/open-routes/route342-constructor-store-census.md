# OPEN ROUTE #342 — THE CONSTRUCTOR-INVARIANT GOAL READS ONLY PLAIN `self.f = e` STORES (for/tuple/with/del/setattr/alias/+=/loop/branch stores ignored; `__class__` reassignment)
**Status: OPEN (gen #37, 2026-10-24), Severity 1.** Red-team round 24; driver-reproduced on main (rc=0; CPython violates).
Witnesses `witnesses-r342/`: own class: `for self.x in ..` (i21), tuple target (i22), `del self.x` (i23), `with .. as self.x` (i24) give vacuous goals like
`goal _check_class_inv_b : forall x. x = 0 -> x = 0`; subclass after a leading `super().__init__()` (defeats #335): del (i10), setattr (i12), for (i17),
tuple (i18); #226's documented "computed / control-flow store: not covered" gap is a LIVE false proof: setattr (i20), `+=` (i25), setattr comprehension
(i26), alias `s = self; s.x = 5` (i35), while (i38), if (i39); `obj.__class__ = C` retypes an object (x03; #338's census does not count __class__ stores).
The same shapes in ordinary methods are refused (#301/with-binding), so __init__ takes a weaker path.
Repair: the constructor-invariant goal must be computed from the FULL constructor body semantics (every store form, control flow, aliases of
self) — or REFUSE any __init__ (of an invariant-carrying class or its subclasses) that stores an invariant field by any form other than
straight-line `self.f = e` (and any `self` alias/escape before the invariant is established); refuse `__class__` stores.
