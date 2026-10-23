# file-type-of-wall-response.md — Response to the `_field_type_of` wall report

*Response, 2026-07-10, to `file-type-of-wall.md`. Agrees with §3–§5 in full (the map-vs-enumerable
tension is real, correctly diagnosed, and a fair SOTA lens). Disagrees with §6's framing of the
available routes and their costs, on the strength of two facts about `_record_types` specifically that
the original report didn't have priced in. Net recommendation: lift both `\trusted` leaves at near-zero
cost via a **reverse index**, not by re-representing `_record_types` or maintaining a general
enumerable companion. Discipline as elsewhere in this campaign: spike first, measure, don't assert.*

---

## 1. Two facts that change the costing in §6

**Fact A — write-once, then frozen.** `_record_types` has exactly **one** mutation site,
`preamble.py:3160`, inside the single-pass preamble scan over the program's `record`-kind type
declarations. Every one of the 21 keyed-read sites across 7 methods, and both `.values()` sites, execute
strictly after that scan completes. There is no interleaved read/write, no per-emission mutation, and
therefore **no invariant to maintain** — only one to *state once*, at the single write site.

**Fact B — the search key is already sitting in the value, computed at the same write site.** The loop in
both `_field_type_of` and `_field_type_for` is not a generic fold; it is a linear search for the entry
whose `whyml_name` field equals `cls`:

```python
for info in self._record_types.values():
    if info["whyml_name"] == cls:
        return info["field_types"].get(field)
```

`whyml_name` is not derived from anywhere the loop can't already see — it is computed **at the write
site itself**: `type_name = whyml_ident(td["name"].lower())` immediately precedes
`self._record_types[td["name"]] = {"whyml_name": type_name, …}`. So the primary key (`td["name"]`) and
the secondary key the search actually wants (`type_name`) are both in hand, together, at population time.

**Consequence.** These two methods do not need enumeration at all. They need a **second keyed map**,
indexed by `whyml_name` instead of `td["name"]`, built by one extra insert at the same site. That
collapses §6's three-way choice for *this pair of methods* into something none of the three routes
describes: no re-representation (route 1), no dual structure with a fold-based reader (route 2), and no
accepted wall (route 3) — a plain second index, same representation family (`map string (option V)`) as
the object it mirrors.

---

## 2. Why this doesn't contradict §3–§5

§3–§5 stand exactly as written: Why3's `map` genuinely cannot be enumerated, that is a real syntax-level
limit, and it is the correct general lens (Why3/SMT arrays vs. Dafny/Viper finite domains vs. inductive
assoc-lists is accurate SOTA positioning). What changes is narrower: `_field_type_of`/`_field_type_for`
were mis-classified as needing the enumeration column of the table in §4, when what they need is a second
row of the *keyed* column. The general tension the report describes is real; it just isn't the tension
this particular method hits. This is worth stating plainly because it's a useful category to have on
record for the rest of the campaign: **"search by a field of the value" is not evidence of a need to
enumerate** — check for a missing index before reaching for `pydict`.

---

## 3. The fix

### 3.1 Population site (`preamble.py`, alongside line 3160)

```python
if td["kind"] == "record":
    type_name = whyml_ident(td["name"].lower())
    declared_types.add(type_name)
    record_info = {
        "whyml_name": type_name,
        "fields": [f["name"] for f in td["fields"]],
        "field_types": {f["name"]: f.get("type", "int") for f in td["fields"]},
        "field_value_types": {f["name"]: f["value_type"]
                              for f in td["fields"] if f.get("value_type")},
        "field_key_types": {f["name"]: f["key_type"]
                            for f in td["fields"] if f.get("key_type")},
        "defaults": td.get("field_defaults", {}),
        "init_params": td.get("init_params", []),
        # ... (unchanged fields elided)
    }
    self._record_types[td["name"]] = record_info
    # NEW: reverse index, same representation family, same write site.
    # whyml_name is already unique per record (it is the emitted WhyML type
    # name), so this is a total keyed map, not a multimap.
    self._record_types_by_whyml_name[type_name] = record_info
```

`self._record_types_by_whyml_name` is initialised as `{}` alongside `self._record_types` wherever that
is currently done. No new class of object, no new WhyML theory — it is a second instance of the *same*
`map string (option recordinfoview)` model already certified and already used for `_record_types` itself.
The two maps share the same `record_info` dict object per entry (not a copy), so there is nothing to keep
in sync beyond the two inserts happening together, which they now do by construction at one site.

### 3.2 The two methods, rewritten

```python
def _field_type_for(self, obj: str, field: str) -> Optional[str]:
    if obj != "self":
        return None
    cls = self._current_self_type
    if not cls:
        return None
    info = self._record_types_by_whyml_name.get(cls)
    return info.get("field_types", {}).get(field) if info else None

def _field_type_of(self, attr_ir: Dict[str, Any]) -> Optional[str]:
    ...                      # unchanged resolution of `cls` (identical to today)
    if not cls:
        return None
    info = self._record_types_by_whyml_name.get(cls)
    return info.get("field_types", {}).get(field_name) if info else None
```

Both are now a single keyed `Map.get` — the exact operation already proved sound and already used at the
21 other `_record_types` read sites. No new termination argument, no fold, no `pydict`.

### 3.3 Certificate / ledger impact

**None.** `map string (option recordinfoview)` is not a new value shape — it is the type already used for
`_record_types`; a second instance of it needs no additional Rocq/Lean certificate, and the ledger stays
at 3 without a new co-landing. This is cheaper than every route §6 costs, including its own "accept the
wall" route 3, once you count route 3's downstream cost (§3.4).

### 3.4 Downstream faithfulness residual, closed as a side effect

The report notes (§6, route 3) that two already-converted callers, `_rhs_yields_array` /
`_rhs_yields_map`, compare `_field_type_of`'s result via an opaque integer hash rather than by string,
specifically *because* `_field_type_of` was trusted and its result untyped for proof purposes. Once
`_field_type_of` is verified against the reverse index, its result is a proved `Optional[str]` from a
certified keyed lookup, and those two callers can be revisited to compare the string directly — closing
a residual the report correctly flagged as otherwise "permanent, bounded by the trusted leaf." This is a
second `\trusted`-adjacent win from the same change, not a separate cost.

---

## 4. Blast radius (measured claim, not asserted)

- **Touched:** 1 preamble site (2 lines: field init + one extra insert), 2 method bodies (the loop
  replaced by a `.get`), 1 new field initialisation.
- **Untouched:** all 21 existing `_record_types[...]` / `.get(...)` / `in` sites — they keep reading the
  original map exactly as before. No representation change ripples to them, unlike route 1 in the
  original report.
- **No new WhyML theory, no new termination obligation, no new certificate.**

This is narrower than any of the three routes §6 costed, which is expected — the report's routes were
sized for "make `_record_types` enumerable," and this fix never needs `_record_types` to be enumerable at
all.

---

## 5. Spike (measure before claiming "cleared")

Per the campaign's standing discipline (`value-model-wall-stand-alone-plan-2.md` §7's acceptance gate,
`09-2223-plan.md`'s spike-gating): this is a small change but "cleared" is asserted only after the run.

**S-reverse-index.** Add the field, the one extra insert, and the two rewritten bodies to the live mirror;
remove both `\trusted` markers; whole-file prove
(`python3 src/pycsl/pycsl.py <mirror-file> --import-path src/pycsl`); corpus byte-diff-0 on the reference
set (no emission-shape change is intended — the WhyML the emitter produces for user programs is
unaffected, only the emitter's own internal lookup path changes, so byte-diff-0 is expected, not
optimistic, but is still to be **run**, not assumed); ledger check
(`Print Assumptions` / `#print axioms` == 3, expected unchanged per §3.3's argument, to be confirmed by
the actual check, not the argument alone).

**Expected outcome, stated as hypothesis:** both methods clear; `Print Assumptions` is untouched because
no new theory was introduced; corpus is byte-identical because no emission path changed. If any of these
three fails, that is more informative than a clean pass and should be reported precisely (e.g., if
`whyml_name` turns out not to be unique in some edge case the static call-site count didn't surface, the
reverse index becomes a multimap and the fix needs a small revision — cheap to detect, cheap to fix,
still far short of route 1 or 2's blast radius).

---

## 6. What this does and does not settle

**Settled, if S-reverse-index passes:** `_field_type_of` and `_field_type_for` lift out of `\trusted`,
`file-type-of-wall.md`'s two leaves close, and the downstream int-hash residual in
`_rhs_yields_array`/`_rhs_yields_map` becomes fixable rather than permanent — all at a blast radius the
original report's §6 did not have on the table, because its three routes were framed around solving
enumeration in general rather than this pair's specific need.

**Not settled, and not claimed:** the general Why3-`map`-cannot-be-enumerated wall from §3–§5 is untouched
and remains real. If a **future** trusted method genuinely needs to walk every value of a write-once
table for a reason that isn't "search by a value field" (e.g., aggregate over all entries, or build a
report listing every record type), routes 1/2/3 as originally costed are still the live menu, and the
report's §6 trade-off table is the right reference for that case. The general "keep a `pydict`-style
companion for genuinely enumerable reads" route from that discussion remains the right fallback for such
a method, sized the same way S-reverse-index is here: write-once co-construction at the single population
site, spiked and measured before being claimed.

**One category worth carrying forward in the campaign's census discipline:** before classifying a
`for x in d.values(): if x.<field> == k: ...` shape as "needs enumeration" (and therefore as an instance
of the map-vs-array wall), check whether it is actually "needs a second index on `<field>`" — the latter
is not a wall at all, just a missing `map`, and is cheaper to fix than to trust.
