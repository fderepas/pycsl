# OPEN ROUTE #280 — A MUTATOR CALLED ON A SUBSCRIPTED / CALL-RESULT RECEIVER IS DROPPED
**Status: OPEN (gen #37, 2026-10-19), Severity 1.** Red-team round 6; driver-reproduced at 78162575 (7 files rc=0; CPython AssertionError).
Witnesses `witnesses-r280/`: `d[k].append/pop/clear`, `d.get(0, []).append`, `t[0].append` emit body-less stubs
(`let _ = (append_1 1)`, `pop_0 ()`) that never touch the receiver, so frame/`\old`/alias claims prove falsely
(p228 `assigns \nothing`; p230/p237/p240 value claims; p223/p233/p251 aliased local). The "mutator with no certified
lowering" refusal only checks plain-name receivers; list-of-lists receivers already fail closed (p227/p234/p235).
Repair: refuse (or model) every receiver mutator whose receiver is not a plain name with a certified lowering —
census all mutator names (append/extend/insert/pop/remove/clear/sort/reverse/update/setdefault/add/discard/...).
