"""Test 0888 — route-R record monomorphization threads across a call boundary (B1, POSITIVE).

The value-model-wall benchmark B1 (value-model-wall-stand-alone.md §6): a statically-closed,
literal-keyed record built by one function and read by a SEPARATE function — proved value-level,
each function independently. A `@dataclass` (equivalently a `TypedDict`) monomorphizes to a native
WhyML record with FAITHFUL per-field types (string/int), so the producer's return type and the
consumer's parameter type are the SAME generated record (type identity across the boundary), the
construction `Entry(name, arity)` is a faithful record literal, and the projection `e.arity` is a
faithful field read.

No tags, no projection laws, no `pyval` embedding, zero SMT string/map cost — type-safety is
discharged by WhyML's type checker; the value contracts (`\result.arity == arity`, `\result == e.arity`)
prove directly. The record value shape is certified axiom-free (Phase2b_RecordVal.v / RecordVal.lean);
the 3-axiom ledger is untouched. If this regresses, the dataclass/TypedDict->record lowering, the
cross-method record-type identity, or the field-projection path broke.
"""
from dataclasses import dataclass


@dataclass
class Entry:
    name: str
    arity: int


#@ requires True
#@ ensures \result.arity == arity
#@ assigns \nothing
def mk_entry(name: str, arity: int) -> Entry:
    return Entry(name, arity)


#@ requires True
#@ ensures \result == e.arity
#@ assigns \nothing
def entry_arity(e: Entry) -> int:
    return e.arity
