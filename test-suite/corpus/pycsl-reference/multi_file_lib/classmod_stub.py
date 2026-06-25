"""multi_file_lib.classmod_stub — fixture for 10-2006-convergence-spec-2 Gap 2a.

`Tmpl` mirrors the real `strmod.Template` shape: a record class with a `str` instance field
(declared in `__init__`, as in the model). Constructing it in an importer needs a
TYPE-CORRECT record literal for the `str` field — the empty-string witness
`{ template = "" }`, not the ill-typed int `{ template = 0 }`. (Gap 2a fixes
`_call_record_constructor._field_default` so a `str`/`real` field defaults to `""`/`0.0`.)
"""
_ = 0  # anchor


class Tmpl:
    def __init__(self):
        self.template: str = ""

    #@ ensures self.template == t
    #@ assigns self.template
    def set_template(self, t: str) -> None:
        self.template = t
