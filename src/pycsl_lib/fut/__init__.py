# pycsl_lib/fut — pure-Python __future__ module
# Modelled: _Feature class and annotations constant.


class _Feature:
    def __init__(self, compiler_flag, mandatory):
        self.compiler_flag = compiler_flag
        self.mandatory = mandatory


# CO_FUTURE_ANNOTATIONS = 0x100000 (1048576)
annotations = _Feature(1048576, 0)
