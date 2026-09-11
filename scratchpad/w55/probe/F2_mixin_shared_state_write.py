# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ mixin
class CoreEmit:
    #@ shared_state program_ir: int
    #@ provides emit
    #@ ensures \result >= 0
    #@ assigns self.program_ir
    def emit(self, x: int) -> int:
        self.program_ir = 99
        return 0


#@ compose_from CoreEmit
class Facade:
    #@ requires self.program_ir == 1
    #@ ensures self.program_ir == 1
    #@ assigns \nothing
    def run(self, k: int) -> int:
        self.emit(k)
        return 0
