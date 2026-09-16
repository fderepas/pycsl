# ROUTE #162 — a collection passed to an OPAQUE library function is assumed unchanged

**Status: REPAIR DRAFTED by gen #29 (worktree wtJ, with #161); battery I pending — a DENYLIST, the systemic question stays recorded.** Severity 1. Generator: hand (frame probes after #161).

## Measured at `87258ff7`

    #@ assigns \nothing
    def f(xs: List[int]) -> None:
        heapq.heapify(xs)
    # caller: requires xs == [5, 1]; f(xs); ensures \result == xs-before[0] == 5   PROVED   (CPython 1)

Routes #13/#14 refuse a mutating METHOD on a receiver (`xs.sort()`, `xs.reverse()`), keyed on the
method NAME in `_SELF_FIELD_MUTATORS`. A module-level function that mutates its ARGUMENT
(`heapq.heapify`, `heapq.heappush`, `random.shuffle`, `bisect.insort`, `struct.pack_into`, ...)
reaches the same abstract-op fallback in `_handle_dotted_call` with no receiver and no `writes`, and
its effect is deleted.

## Candidate repair (not landed — census first)

In the generic fallback: a collection-typed argument (list/dict/set/bytearray local, parameter or
field) passed to an abstract op with no `writes` clause is refused unless the callee is on a
whitelist of functions that never mutate their arguments. Census the corpus dotted calls with
collection arguments and predict the refused (GONE) set.

## Draft (wtJ)

A census of dotted calls with name/attribute arguments over the corpus and the mirrors (json.dumps,
os.path.*, IRScanner helpers, struct.pack/unpack, ...) shows a pure-callee WHITELIST would refuse the
mirror's own verified bodies, so the draft is a DENYLIST of standard-library functions documented to
mutate an argument in place: heapq.{heapify, heappush, heappop, heappushpop, heapreplace},
random.shuffle, bisect.{insort, insort_left, insort_right}, struct.pack_into,
operator.{setitem, delitem, iadd, iconcat}, refused when the op carries no `writes`. Witnesses
1556/1557. The general gap — an unknown argument mutator — remains OPEN as a WATCH.
