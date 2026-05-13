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


#@ requires v >= 0
#@ ensures \result == v + 1
#@ assigns \nothing
def counter_increment(v: int) -> int:
    return v + 1


#@ requires v >= 0 and workers >= 0 and increments_per_worker >= 0
#@ ensures \result == v + workers * increments_per_worker
#@ assigns \nothing
def run_workers(v: int, workers: int, increments_per_worker: int) -> int:
    total = workers * increments_per_worker
    current = v
    i = 0
    #@ loop invariant 0 <= i and i <= total
    #@ loop invariant current == v + i
    #@ loop variant total - i
    while i < total:
        current += 1
        i += 1
    return current


if __name__ == "__main__":
    v = counter_init()
    v = run_workers(v, 4, 5000)
    print("counter:", counter_value(v))