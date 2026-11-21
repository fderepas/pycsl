# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ mixin
class CoreEmit:
    #@ shared_state v: int
    #@ provides emit
    #@ ensures \result >= 0
    #@ assigns self.v
    def emit(self, x: int) -> int:
        self.v = 99
        return 0


#@ mixin
class MapOps:
    #@ shared_state v: int
    #@ depends_method emit: (self, x: int) -> int
    #@   ensures \result >= 0
    #@ provides handle_get
    #@ requires self.v == 1
    #@ ensures self.v == 1
    #@ assigns \nothing
    def handle_get(self, k: int) -> int:
        self.emit(k)
        return 0


#@ compose_from CoreEmit, MapOps
class Facade:
    #@ requires self.v == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def run(self, k: int) -> int:
        return self.handle_get(k)
