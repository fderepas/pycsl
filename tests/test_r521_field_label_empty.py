"""Routes #521-#526 (u18): the field-store lowering passed `None` to `_field_label`, whose
`record_lower` is annotated `str` (the record value-fence's escape obligation in the
self-annotate mirror of `statements.py`). It now passes `""`; `_field_label` only tests the
argument's truth, so the label is the same for every field, ambiguous or not."""
from __future__ import annotations


def test_field_label_none_and_empty_agree():
    from module6_whyml.expressions import ExpressionEmissionMixin

    class _E(ExpressionEmissionMixin):
        pass

    e = _E.__new__(_E)
    e._ambiguous_fields = {"count"}
    for field in ("count", "other", "type"):
        assert e._field_label(None, field) == e._field_label("", field)
    assert e._field_label("rec", "count") != e._field_label("", "count")
