"""Test 0287 — Local left rotation kernel"""
_ = 0  # anchor


#@ requires \length(keys) == \length(left)
#@ requires \length(keys) == \length(right)
#@ requires \length(keys) >= 3
#@ requires right[0] == 1
#@ requires left[0] == -1
#@ requires left[1] == 2
#@ requires right[1] == -1
#@ requires keys[0] < keys[2]
#@ requires keys[2] < keys[1]
#@ ensures \result == \old(right[0])
#@ ensures left[\result] == 0
#@ ensures right[0] == \old(left[1])
#@ ensures keys[left[\result]] < keys[\result]
#@ ensures keys[0] < keys[right[0]]
#@ ensures keys[right[0]] < keys[\result]
#@ ensures \forall k; 0 <= k and k < \length(keys) ==> keys[k] == \old(keys[k])
#@ ensures \forall k; 0 <= k and k < \length(left) and k != \result ==> left[k] == \old(left[k])
#@ ensures \forall k; 0 <= k and k < \length(right) and k != 0 ==> right[k] == \old(right[k])
#@ assigns left[1..2], right[0..1]
def rotate_left_root(keys: list, left: list, right: list) -> int:
    y = right[0]
    beta = left[y]
    right[0] = beta
    left[y] = 0
    return y


if __name__ == "__main__":
    keys = [10, 30, 20, 99]
    left = [-1, 2, -1, -1]
    right = [1, -1, -1, -1]

    root = rotate_left_root(keys, left, right)

    assert root == 1
    assert keys == [10, 30, 20, 99]
    assert left == [-1, 0, -1, -1]
    assert right == [2, -1, -1, -1]
    print("PASS")
