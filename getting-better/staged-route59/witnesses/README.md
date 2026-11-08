# ROUTE #59 WITNESSES — LANDED. THIS DIRECTORY IS EMPTY OF DRIVERS BY DESIGN.

All eight drivers (`1125`-`1132`) moved into `test-suite/corpus/pycsl-reference/` at the
commit that closed carriers 6 and 7, which is the order this file always specified: land
the repair, then the witnesses. Seven are `# pycsl-expected: FAIL` negatives that PROVED
at HEAD before the repairs and now refuse; `1131` is the POSITIVE list control that
proved before and must keep proving — it is what stops a future repair from satisfying
all seven negatives by simply refusing every collection binding.

Route #60's witnesses (`1133`-`1142`) were written straight into the corpus for the same
reason: their repair landed first.
