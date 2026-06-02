"""Linker — manifest writing and qualname-resolution helpers.

`manifest.write_manifest` emits `pycsl-bridge.manifest.toml`.
`manifest.check_manifest` re-computes the manifest and reports drift.
"""

from .manifest import write_manifest, check_manifest, Manifest

__all__ = ["write_manifest", "check_manifest", "Manifest"]
