"""pycsl_emit — shared backend for rocq2pycsl, lean2pycsl, and pycsl_bridge.

Provides:
  - ir:        language-agnostic first-order IR for PyCSL contracts
  - translator: IR → PyCSL surface-syntax strings
  - emitter:   libcst-based annotation insertion onto Python source
  - checker:   subprocess wrapper around the pycsl CLI + verdict parser
  - config:    shared TOML schema and loader
"""

__version__ = "0.1.0"
