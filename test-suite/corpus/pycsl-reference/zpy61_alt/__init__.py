# u64 witnesses 10340 / 10343 (review rt74 V2D): makes ../zpy61_alt a REGULAR package so that every file
# of the witness tree loads by its own dotted name (bin/check-corpus-executes imports ./zpy61/__init__.py
# as `zpy61.__init__`, which CPython searches in the redirected `__path__`, i.e. here; u61's version had no
# such file and that plane failed "No module named 'zpy61.__init__'"). CPython never runs this file for
# `zpy61.b`: the witnesses' import loads ./zpy61_alt/b.py directly as `zpy61.b`.
