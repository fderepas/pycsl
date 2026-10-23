# OPEN ROUTE #309 — `getattr(o, name, <call/collection default>)` LOWERS TO ONE SHARED CONSTANT, EVEN WHEN THE ATTRIBUTE EXISTS
**Status: OPEN (gen #37, 2026-10-23), Severity 1.** Red-team round 14; driver-reproduced on main (l10, l15 rc=0; CPython violates).
Witnesses `witnesses-r309/`: l10 (default's call dropped: its writes vanish), l15 (`getattr(a,"n",z()) - getattr(b,"n",z()) == 0`
for different receivers), l16 (a read before and after `a.n = 9` agree). Mechanism: expressions.py (~14408) emits the constant
`pycsl_getattr_default_<hash of default IR>` — an arm meant for a statically-absent attribute is reached when the receiver is a
known record that HAS the attribute; receiver, attribute and the default's effects are all ignored. Distinct from #306 (dict.get)
and #213/#214 (unknown receivers).
Repair: for a known record receiver with a literal attribute name, lower `getattr(o, "f", d)` to: evaluate o, evaluate d (eager,
Python order), then the field read if `f` is a field of o's class (CLASS-EXACT applies), else d; refuse anything else (non-literal
name, unknown receiver, absent-attribute constant arm) — never a hashed constant.
