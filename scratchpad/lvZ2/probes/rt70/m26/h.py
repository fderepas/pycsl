class Box:
    #@ ensures \result == x
    #@ assigns \nothing
    @staticmethod
    def keep(x: str) -> str:
        return x
