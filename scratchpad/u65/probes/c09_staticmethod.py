class C:
    #@ requires x > 0 and x < 0
    #@ ensures \result == 99
    @staticmethod
    def constant(x: int) -> int:
        return 1
