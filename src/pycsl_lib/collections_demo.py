"""Formal driver for the `collections` module — REAL verifiable models (collections-plan).

`defaultdict(int)`/`Counter`/`OrderedDict` reduce to the dict model (`map int (option int)`,
missing key -> 0), `deque` to the growable-list model (append/index/len), and `namedtuple` to a
record — so every Tier-1/2 demo below carries real CONTENT and verifies with NO `\trusted`.
`ChainMap` and the User* wrappers remain opaque handles (Tier 3 — composition / subclass hooks are
out of scope). Verified end-to-end via `pycsl src/pycsl_lib/collections_demo.py`."""
from collections import defaultdict, Counter, OrderedDict, deque, namedtuple, ChainMap

Point = namedtuple('Point', ['x', 'y'])


#@ ensures \result == 7
def demo_defaultdict() -> int:
    """defaultdict(int): a missing key reads as 0, so d[3] becomes 7."""
    d = defaultdict(int)
    d[3] = d[3] + 7
    return d[3]


#@ ensures \result == 2
def demo_counter() -> int:
    """Counter: two `+= 1` increments from empty give a count of 2."""
    c = Counter()
    c[1] += 1
    c[1] += 1
    return c[1]


#@ ensures \result == 42
def demo_ordereddict() -> int:
    """OrderedDict: plain dict content (order not modelled)."""
    od = OrderedDict()
    od[1] = 42
    return od[1]


#@ ensures \result == 5
def demo_deque() -> int:
    """deque: right-end append + indexed read (left-end ops out of scope)."""
    dq = deque()
    dq.append(5)
    dq.append(9)
    return dq[0]


#@ requires a >= 0
#@ ensures \result == a
def demo_namedtuple(a: int, b: int) -> int:
    """namedtuple: Point(a, b).x == a via the record construction."""
    p = Point(a, b)
    return p.x


#@ ensures \result == 0
def demo_chainmap_opaque() -> int:
    """Tier 3: ChainMap is an opaque handle — no content reasoning."""
    cm = ChainMap()  # noqa: F841
    return 0
