""  # pycsl
#@ requires 1 == 1
#@ ensures \result == 0
#@ assigns \nothing
def counter_init() -> int:
    return 0


#@ requires v >= 0
#@ ensures \result == v
#@ assigns \nothing
def counter_value(v: int) -> int:
    return v


#@ requires v >= 0 and amount >= 0
#@ ensures \result == v + amount
#@ assigns \nothing
def counter_increment(v: int, amount: int) -> int:
    return v + amount


#@ requires 1 == 1
#@ ensures \result == 0
#@ assigns \nothing
def counter_reset() -> int:
    return 0


if __name__ == "__main__":
    v = counter_init()
    v = counter_increment(v, 1)
    v = counter_increment(v, 4)
    print("value:", counter_value(v))
    v = counter_reset()
    print("after reset:", counter_value(v))