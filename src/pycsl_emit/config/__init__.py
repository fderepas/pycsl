"""config — shared TOML schema for rocq2pycsl, lean2pycsl, pycsl_bridge.

schema.py defines the dataclass shapes. load.py reads a TOML file and
returns a populated Config object. Converters extend the base schema
with their own [rocq]/[lean] sections.
"""

from .schema import Config, FunctionSpec, PycslSettings
from .load import load_config

__all__ = ["Config", "FunctionSpec", "PycslSettings", "load_config"]
