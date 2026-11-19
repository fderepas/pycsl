class C:
    #@ \trusted reviewer: probe
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self) -> None:
        pass

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def go(self) -> None:
        self.b = 7

    #@ requires True
    #@ ensures \result == 0
    #@ assigns \nothing
    def run(self) -> int:
        self.b = 0
        self.go()
        return self.b
