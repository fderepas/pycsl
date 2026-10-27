# OPEN ROUTE #428 — THE §7.63 "SAFE MODULE" LIST COVERS THE MODULE'S CLASSES' METHODS: A STDLIB __init__ CALLED ON self STORES ATTRIBUTES
**Status: OPEN, Severity 1.** Red-team round 33 (2026-10-27, convergence measurement after the run #3 allow-list repairs; 653 screened / 385 fully proved / 116 confirmed); driver-reproduced on main (see `scratchpad/rt33/driver-repro.txt`).
Witnesses `witnesses-r428/` (19): `i01_logger_init.py`, `i02_filter_init.py`, `i04_formatter_init.py`, `i05_userlist_init.py`, `i06_textwrapper_init.py`, `i07_jsonenc_init.py`, `i08_suppress_init.py`, `i09_warnings_cw_init.py`, `i11_future_init.py`, `i13_jsondec_init.py`, `i14_logadapter_init.py`, `i15_dataclasses_field.py`, `i16_pprint_init.py`, `i18_shlex_init.py`, `i19_codecs_init.py`, `i20_logrecord_init.py`, `i21_string_template.py`, `t01_userlist_field_hash.py`, `t04_logger_field_hash.py`.

```
#428 THE §7.63 "SAFE MODULE" LIST COVERS THE MODULE'S CLASSES' METHODS: A STDLIB __init__ CALLED ON self STORES ATTRIBUTES  [slips past §7.63 / route #406]  (19)
  i01  R.__init__: logging.Logger.__init__(self, "n"); getattr(r, "level", 7) == 7 PROVED           CPython 0
  i02 logging.Filter  i04 logging.Formatter  i14 logging.LoggerAdapter  i20 logging.LogRecord  i05 collections.UserList
  i06 textwrap.TextWrapper  i07 json.JSONEncoder  i13 json.JSONDecoder  i08 contextlib.suppress  i09 warnings.catch_warnings
  i11 concurrent.futures.Future  i15 dataclasses.Field  i16 pprint.PrettyPrinter  i18 shlex.shlex  i19 codecs.IncrementalDecoder
  i21 string.Template     (each `<mod>.<Class>.__init__(self, ..)`; CPython returns the stored attribute)
  t01  field `data: int` then collections.UserList.__init__(self, [1]); {r.data} PROVED            CPython TypeError
  t04  field `handlers` then logging.Logger.__init__(self, "n"); {r.handlers}                       CPython TypeError
  (super().__setattr__, type(self).__setattr__, R.__setattr__, methodcaller / reduce(setattr) / __dict__.update: refused.
  t02 / t03 -- the same call in a method under a class invariant / an ensures -- fail.)
  REPAIR: the allow-list of `_sm406` modules applies to module-level FUNCTIONS only; a callee reached through a CLASS of the
  module (`mod.Cls.meth(x, ..)`, any `mod.Cls(..)` taking x) is treated as an unread callee (the file is DYNAMIC) unless the
  (class, method) pair is itself listed.
```
