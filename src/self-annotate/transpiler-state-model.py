"""transpiler-state-model.py — A3.2/A3.4 (a3-plan.md): the transpiler state as a
@mutable_state record with CHECKED assigns frames.

Models the emitter's mutable state (a3-plan.md §0 census) as a @mutable_state
@dataclass and proves: (A3.4) `_add_abstract_op` — the dominant mutator (19 sites)
— carries a CHECKED `writes { self.abstract_ops }`; a composed handler mutating
several fields proves the UNION frame; and a caller INHERITS a callee's frame.
Built entirely on the landed mutable-self feature (M.2-M.7) — no new emitter code.

Run: PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/self-annotate/transpiler-state-model.py
"""
from dataclasses import dataclass
from typing import Set


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class TranspilerState:
    # set-of-name fields (a3-plan §0): each mutated via `.add` → a real map write.
    abstract_ops: Set[str]        # via _add_abstract_op (19 sites — the dominant one)
    dict_locals: Set[str]
    array_locals: Set[str]
    ghost_string_vars: Set[str]
    # scalar state
    havoc_counter: int            # += 1
    in_spec: bool                 # = True/False

    # A3.4: the dominant mutator, framed. Its `writes { self.abstract_ops }` is
    # CHECKED against the body (a `\nothing` here FAILS — non-vacuity).
    #@ assigns self.abstract_ops
    def add_abstract_op(self, op: str) -> None:
        self.abstract_ops.add(op)

    #@ assigns self.havoc_counter
    def next_havoc(self) -> None:
        self.havoc_counter = self.havoc_counter + 1

    #@ assigns self.in_spec
    def enter_spec(self) -> None:
        self.in_spec = True

    #@ assigns self.in_spec
    def leave_spec(self) -> None:
        self.in_spec = False

    # A composed handler: mutates a set field directly, CALLS the framed mutator
    # (inheriting its write), and bumps a counter — the UNION frame is checked.
    #@ assigns self.dict_locals, self.abstract_ops, self.havoc_counter
    def handle_like(self, name: str) -> None:
        self.dict_locals.add(name)
        self.add_abstract_op("val getattr_x (x: int) : int")
        self.havoc_counter = self.havoc_counter + 1


# --- NON-VACUITY (expected FAIL, out of this pass-file) ---
#   handle_like with `#@ assigns \nothing` (or omitting a mutated field) FAILS:
#   "unlisted write effect". A caller that under-declares its frame is rejected
#   (validated in scratchpad). The a3-plan.md §9 hole is CLOSED for the state model.
#
# RESIDUAL (a3-plan §10): a `Dict[str,int]` record field (known_collection_sizes)
# is emitted int-keyed, so `self.sizes[name]=1` str-key mismatches — a record-dict-
# field key-type concern (no-more-int), not the frame mechanism. Omitted here.
