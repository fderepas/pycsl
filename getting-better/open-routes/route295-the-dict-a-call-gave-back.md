# OPEN ROUTE #295 — A dict RETURNED BY A CALL IS A COPY: STORES THROUGH IT DO NOT REACH THE ALIASED ORIGINAL
**Status: REPAIRED (gen #37, 2026-10-21; opened 2026-10-20), Severity 1.** Dict twin of #288 (found by the rB executor's census); driver-reproduced at 19461c40 (rc=0; CPython 2).
Witness `witnesses-r295/dict_alias.py`: `\trusted` identity callee `idd`; `d = {1: 1}; e = idd(d); e[1] = 2; return d[1]` proves
`\result == 1`. Emission `let e = ref (idd !d) in e := map_update_some !e 1 2` is a copy. #283/#288 cover lists only. Repair: extend
the returned-alias partner rule to dict/set (and every mutable collection) values bound from a may-alias call (imported / trusted /
early-return / returns-a-param), refusing stores/mutators/del through either name while the alias is live; census the collection kinds.

## REPAIR (2026-10-21, worktree pycsl-r295 off ea7f5bcb = rB 4b67e24d + this route file)
Root cause (located on the witness emission): `e = idd(d)` lowers to `let e = ref (idd !d) in` and `e[1] = 2` to
`e := map_update_some !e 1 2` — a store on a COPY. A dict/set is a map VALUE in the model (a parameter too), so
the copy happens for EVERY may-alias callee: `\trusted`, imported, and even a VERIFIED straight `return x` (unlike
the list case, where only an early return copies). #283/#288's partner rule (B) ran only for a LIST-valued target
and collected only list/array partners, so a map-valued alias was never fenced.

Probe table (`pycsl.py`, rc; CPython ground truth in each file's `__main__`; base = ea7f5bcb; census probes and
logs under the session scratchpad `r295/p`, `r295/{base,after}-{emit,prove}`):

| shape | base | after |
|---|---|---|
| route witness `e = idd(d); e[1] = 2; return d[1]`, `\trusted` idd (3450) | PROVED | REFUSED |
| annotated `e: Dict[int, int] = idd(d)` (3451) | PROVED | REFUSED |
| imported identity `iddh` (3452) | PROVED | REFUSED |
| VERIFIED callee `return x` (3453) | PROVED | REFUSED |
| REVERSE `e = idd(d); d[1] = 2; return e[1]`, verified `ensures \result == x` (3454) | PROVED | REFUSED |
| `del e[1]` (3455), `e[1] += 1` (3456), new key `e[5] = 5` (3461) | PROVED | REFUSED |
| writing callee `setk(e)` (`assigns x`) (3457) | PROVED | REFUSED |
| CONDITIONAL `e: Dict = d if c > 0 else {1: 5}` (3458) | PROVED | REFUSED |
| `idd(idd(d))` (3459), store in a loop (3460), rebind of a declared dict (3465) | PROVED | REFUSED |
| dict PARAMETER under `assigns d` (3462), `Dict[str, int]` (3463) | PROVED | REFUSED |
| `Set[int]` PARAMETER `t = ids(s); t.add(5); 5 in s` (3464) | PROVED | REFUSED |
| early-return verified callee, `e |= {..}`, `d or {..}`, local `Set[int]` add/discard/`|=`/reverse/member, `Set[str]` | ill-typed (fail-closed) | REFUSED (this rule) |
| `e.update/pop/clear/setdefault` | REFUSED (#162 mutator) | REFUSED (this rule first) |
| `h = e; h[1] = 2`, method callee `h.idm(d)` | REFUSED (#289 subscript_set gate) | REFUSED (this rule first) |
| unannotated callee `idu(d)`, unannotated `defaultdict`/`Counter` | REFUSED (#289 gate) | REFUSED (#289 gate) |
| annotated `DefaultDict`/`Counter`/`OrderedDict` store, `deque` append, `bytearray` store, tuple-unpacked dict, field getter, walrus | REFUSED (other gates) | REFUSED (unchanged) |
| `e = idd(self.m); e[1] = 2; return self.m[1]` (field argument) | — | FAIL (not proved; no partner: residual) |
| controls 3466: read-only alias via verified identity, fresh dict from `mk(1)`, `v = d.get(1, 0); d[1] = 2`, `n = d[1]; d[1] = 5`, `n = cnt(d); d[1] = 2` | PASS | PASS |

Rule (inline in `_handle_assign_stmt`, #283's block; mirror twin `\trusted` and already raising; no new def/
field; #283's code `PYCSL-M6-MUTATION-THROUGH-RETURNED-ALIAS` reused, message says "dict/set" for this arm):
(i) a target is MAP-valued when the RHS is not a name/literal/comprehension/slice, the target is not list-valued,
and its symbol-table type is `dict`/`set`/`frozenset`, or it is a `_dict_locals` name, or the RHS
`_rhs_yields_map`, or — only for a callee whose result type the module does not know or knows to be a map — the
rest of the body USES it as a collection (subscripted, stored/deleted through, a method receiver, the right of
`in`); (ii) its PARTNERS are the dict/set names (`_dict_locals` or dict/set-typed, parameters included) inside the
RHS outside a fresh constructor (`dict`/`set`/`frozenset`/`defaultdict`/`Counter`/`OrderedDict`/`deque`/`.copy`
join #283's list); a dict SUBSCRIPT read contributes only its key and a METHOD receiver (`d.get(k)`) contributes
nothing — neither yields the dict itself; (iii) #279/#283/#288's flow-sensitive walk then refuses every store,
augmented store, `del`, mutator method, augmented assignment, or hand-off to a may-write callee through any live
name. List targets are untouched (their partner arm is unchanged, byte for byte).
Census (collection kinds x binding shapes): dict (int/str keys), set (local/param) x {annotated, unannotated,
rebind} x {`\trusted`, imported, verified straight, verified early-return, nested call, method call, unannotated
callee, conditional, `or`, walrus, tuple unpack, field getter, two-step name alias} x {store, aug store, new key,
`del`, mutator, `|=`, writing callee, reverse} — 52 probes; every PROVED shape now REFUSED, every other shape was
and stays fail-closed. defaultdict/Counter/OrderedDict/deque/bytearray: no accepting shape exists at base
(annotated stores refused as non-list/dict, unannotated ones by #289's gate, deque by the seeded-deque/untracked-
append gates, bytearray by #289); the fresh-constructor list names them so a later model does not inherit a
coarse refusal.
