# OPEN ROUTE #321 — Counter / OrderedDict / defaultdict MODEL: seed keyed on SOURCE TEXT, keyword seeds dropped, factory ignored, read does not insert
**Status: OPEN (gen #37, 2026-10-23), Severity 1.** Red-team round 18 (stdlib/builtin model); driver-reproduced on main 3b07a838 (rc=0; CPython violates).
Witnesses `witnesses-r321/`: (a) `pycsl_seeded_map_%d % stable_hash(repr(seed))` (expressions.py ~11825): `Counter(xs); xs = [2]; Counter(xs)` share
one constant -> `c1[1] != c2[1]` decided False (d09, d12; across a dict-param mutation d13) — the README's "seeded-map constant (L3-tc-closed)"
residual is NOT closed once annotated `c: Dict[int,int] = Counter(..)`; (b) keyword seeds dropped: `Counter(a=5)`, `OrderedDict(a=5)`,
`defaultdict(int, a=5)` -> empty map, `d["a"] == 0` proves (n03, n04, n06); (c) defaultdict factory ignored, missing-key default hard-wired 0:
`defaultdict(lambda: 7)[5] == 0` (j05), `defaultdict(str)[5] == 0` (j06), `d[1] = d[1] + 4; return d[1] - 4` proves 0 (j08); (d) a defaultdict read
does not insert the key: `x = d[5]; 5 in d` proves False (j03; SEV-2).
Repair: seeded maps must be keyed on the seed's VALUE (evaluate the seed; model Counter(xs) as a function of the seed's contents, or refuse a
non-literal seed); refuse keyword seeds (as plain dict(a=..) is); model only `defaultdict(int)` (factory 0) or refuse other factories; a
defaultdict subscript read must insert (or refuse reads of defaultdicts whose membership is later observed).
