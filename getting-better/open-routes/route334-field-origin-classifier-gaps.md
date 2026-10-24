# OPEN ROUTE #334 — #330/#331 FIELD-ORIGIN GAPS: non-int field initialisers through locals/walrus/negative pow, tuple-target __init__, integral floats, unknown dict values
**Status: OPEN (gen #37, 2026-10-24), Severity 1.** Red-team round 21; driver-reproduced on main ec549509 (rc=0; CPython violates).
Witnesses `witnesses-r334/`: the field-initialiser classifier only recognises literal / `/` / some calls / non-int-annotated params / globals; these lower to
`{ r = (any int) }` without tainting the label: `x = 2.5; self.r = x` (f02), walrus (f20), `2 ** -1` (f06), `10 ** -1` with `c.r * 10 == 1` False (f22; the
#259 py_pow obligation is also lost), str via a local (f18), None via a local under no_exception (f24), str via local `c.s - c.s` (f25);
tuple-target `self.r, self.s = 2.5, 1` escapes #315 (class opaque, `get_r`) and `c.r % 1 == 0` proves (o03); integral float `self.r = 3.0` carried as int:
`c.r*10**17 + 1 != c.r*10**17` proves (p01), `len("ab" * c.r)` with r=2.0 under no_exception (CPython TypeError) (p10); dict values of unknown
type: field `{"a": 0.5}` then `c.d["a"] % 1 == 0` (k04), bare `d: dict` param `map string (option int)` proves the same even with
--strict-bare-containers (k01; BARE-CONTAINER-INT lists only list/List/Sequence/tuple).
Repair: classify a field origin by the TYPE of the initialiser expression (type inference over locals/walrus/pow/calls), not by syntactic shape —
any initialiser not provably int taints the label; integral float literals are floats (taint, or keep int only where #148/#236 controls need it
and prove those uses are float-safe); dict values of unknown/bare type are origins (extend BARE-CONTAINER-INT docs or taint); tuple-target
field initialisation must be either modelled like single targets or refused by #315.
