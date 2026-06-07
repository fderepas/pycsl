# pure_lib/syscfg — pure-Python sysconfig module
# Config dict: Modelled. String formatting (_subst_vars): Specified.

_CONFIG_VARS = {}


#@ ensures \result >= 0
def get_config_var(name) -> int:
    if name in _CONFIG_VARS:
        return _CONFIG_VARS[name]
    return 0


#@ ensures \result >= 0
def get_config_vars() -> int:
    return _CONFIG_VARS


#@ ensures \result >= 0
def get_default_scheme() -> int:
    return 0


#@ ensures \result >= 0
def get_path(name) -> int:
    return 0


#@ ensures \result >= 0
def get_paths(scheme) -> int:
    return 0


#@ ensures \result >= 0
def get_makefile_filename() -> int:
    return 0
