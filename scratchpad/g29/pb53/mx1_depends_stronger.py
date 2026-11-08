# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ mixin
class CoreEmit:
    #@ provides emit
    #@ ensures \result == 0
    #@ assigns \nothing
    def emit(self, x: int) -> int:
        return 0


#@ mixin
class MapOps:
    #@ depends_method emit: (self, x: int) -> int
    #@   ensures \result == 7
    #@ provides handle_get
    #@ ensures \result == 7
    #@ assigns \nothing
    def handle_get(self, k: int) -> int:
        return self.emit(k)


#@ compose_from CoreEmit, MapOps
class Facade:
    #@ ensures \result == 7
    #@ assigns \nothing
    def run(self) -> int:
        return self.handle_get(1)
