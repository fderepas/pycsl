# Pure model for graphlib — topological sort
# Models TopologicalSorter as node-count tracker.

""" # pycsl"""


#@ class invariant self._nodes >= 0
#@ class invariant self._ready >= 0
#@ class invariant self._ready <= self._nodes
class TopologicalSorter:
    """Abstract topological sorter tracking node count."""

    #@ ensures self._nodes == 0
    #@ ensures self._ready == 0
    #@ ensures self._prepared == 0
    def __init__(self) -> None:
        self._nodes: int = 0
        self._ready: int = 0
        self._prepared: int = 0

    #@ requires self._prepared == 0
    #@ ensures self._nodes == \old(self._nodes) + 1
    #@ assigns self._nodes
    def add(self, node: int) -> None:
        """Add a node to the graph."""
        self._nodes = self._nodes + 1

    #@ requires self._prepared == 0
    #@ ensures self._prepared == 1
    #@ ensures self._ready <= self._nodes
    #@ assigns self._prepared, self._ready
    def prepare(self) -> None:
        """Mark graph as ready for iteration."""
        self._prepared = 1
        self._ready = self._nodes

    #@ requires self._prepared == 1
    #@ ensures \result >= 0
    #@ ensures \result <= self._nodes
    def is_active(self) -> int:
        """Return 1 if nodes remain, else 0."""
        if self._nodes > 0:
            return 1
        return 0

    #@ requires self._prepared == 1
    #@ requires self._ready > 0
    #@ ensures \result >= 0
    #@ ensures \result <= \old(self._ready)
    def get_ready(self) -> int:
        """Return count of ready nodes."""
        return self._ready

    #@ requires self._prepared == 1
    #@ requires self._nodes > 0
    #@ ensures self._nodes == \old(self._nodes) - 1
    #@ assigns self._nodes, self._ready
    def done(self, node: int) -> None:
        """Mark node as processed."""
        self._nodes = self._nodes - 1
        if self._ready > 0:
            self._ready = self._ready - 1
