# OPEN ROUTE #295 — A dict RETURNED BY A CALL IS A COPY: STORES THROUGH IT DO NOT REACH THE ALIASED ORIGINAL
**Status: OPEN (gen #37, 2026-10-20), Severity 1.** Dict twin of #288 (found by the rB executor's census); driver-reproduced at 19461c40 (rc=0; CPython 2).
Witness `witnesses-r295/dict_alias.py`: `\trusted` identity callee `idd`; `d = {1: 1}; e = idd(d); e[1] = 2; return d[1]` proves
`\result == 1`. Emission `let e = ref (idd !d) in e := map_update_some !e 1 2` is a copy. #283/#288 cover lists only. Repair: extend
the returned-alias partner rule to dict/set (and every mutable collection) values bound from a may-alias call (imported / trusted /
early-return / returns-a-param), refusing stores/mutators/del through either name while the alias is live; census the collection kinds.
