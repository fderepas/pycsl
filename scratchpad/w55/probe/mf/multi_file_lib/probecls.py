"""probecls — a contracted METHOD whose ensures is FALSE when its requires is violated."""
_ = 0  # anchor


class Helper:
    #@ requires x > 0
    #@ ensures \result > 0
    def pos_only(self, x: int) -> int:
        return x
