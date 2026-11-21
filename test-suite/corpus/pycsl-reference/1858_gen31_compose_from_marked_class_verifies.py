r"""Test 1858 — gen #31 CONTROL for 1857 (expected PASS): the marker restored.

Byte-identical to 1857 except for the one line `#@ mixin` above `class CoreEmit:`. It
verifies, so the refusal in 1857 is about the MISSING MARKER and not about the
composition, the `#@ provides`, the `#@ depends_method` or the `#@ shared_state` — the
same control discipline 1841, 1843, 1848, 1851, 1853/1854 and 1856 pay for.

This is also 0549's shape, so if this file ever starts being REFUSED the repair has
become a ban on mixin composition rather than a rule about declaring one.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ mixin
class CoreEmit:
    #@ shared_state program_ir: int
    #@ provides emit
    #@ ensures \result >= 0
    #@ assigns \nothing
    def emit(self, x: int) -> int:
        return x if x >= 0 else 0


#@ mixin
class MapOps:
    #@ depends_method emit: (self, x: int) -> int
    #@   ensures \result >= 0
    #@ provides handle_get
    #@ ensures \result >= 0
    #@ assigns \nothing
    def handle_get(self, k: int) -> int:
        return self.emit(k)


#@ compose_from CoreEmit, MapOps
class Facade:
    #@ ensures \result >= 0
    #@ assigns \nothing
    def run(self, k: int) -> int:
        return self.handle_get(k)
