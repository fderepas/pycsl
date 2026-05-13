""  # pycsl
#@ requires n >= 1
#@ requires start >= 0
#@ requires end_node >= 0
#@ ensures \result >= -1
#@ assigns \nothing
def shortest_path_unweighted(n: int, start: int, end_node: int) -> int:
    if start > end_node:
        return -1
    else:
        dist = 0
        current = start
        #@ loop invariant current >= start
        #@ loop invariant dist >= 0
        #@ loop invariant dist == current - start
        #@ loop variant end_node - current
        while current < end_node:
            current += 1
            dist += 1
        return dist


if __name__ == "__main__":
    print("path length:", shortest_path_unweighted(6, 0, 3))