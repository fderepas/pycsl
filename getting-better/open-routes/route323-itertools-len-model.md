# OPEN ROUTE #323 — THE itertools LENGTH MODEL DROPS KEYWORDS, MATCHES BY SHORT NAME, AND COUNTS A STARRED ARG AS ONE OPERAND
**Status: OPEN (gen #37, 2026-10-23), Severity 1.** Red-team round 18 (stdlib/builtin model); driver-reproduced on main 3b07a838 (rc=0; CPython violates).
Witnesses `witnesses-r323/`: `_iter_len_expr` (expressions.py ~7168): `len(list(itertools.product(xs, repeat=2)))` modelled as `len(xs)` (k01;
keywords dropped on the dotted path); a user-defined `product`/`chain` returning [0] is modelled as itertools' (k02, k03; `fn.rsplit(".", 1)[-1]`
short-name match); `len(list(chain(*xss)))` -> `Array.length xss` (k06; product(*xss) k09).
Repair: resolve the callee to the real itertools binding (refuse when shadowed/unresolved); refuse any keyword or starred argument in the length
model; census other short-name oracles (#75/#305 class).
