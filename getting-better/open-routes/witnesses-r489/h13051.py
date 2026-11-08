class C:
    def __init__(self) -> None:
        self.v = 0

    #@ assigns self.v
    def __eq__(self, x: object) -> bool:
        self.v = 7
        return True
