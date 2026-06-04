"""Test 0501 — collections: deque via the growable-list model (partial).

`deque()` lowers to the list/append model: `append` writes at the high end and bumps the length
counter, so `len(dq)` and `dq[i]` carry real content. Here two appends give `dq[0] == 5`.
Out of scope (documented): left-end ops `appendleft`/`popleft` and `pop` — only right-end
`append`, indexed read `dq[i]`, and `len` are modelled."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
from collections import deque


#@ ensures \result == 5
def front() -> int:
    dq = deque()
    dq.append(5)
    dq.append(9)
    return dq[0]
