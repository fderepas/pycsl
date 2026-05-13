#@ requires 1 == 1
#@ ensures \result >= 0
#@ assigns \nothing
def word_frequencies(words: list) -> int:
    n = len(words)
    total = 0
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant total >= 0
    #@ loop invariant total == i
    #@ loop variant n - i
    while i < n:
        total += 1
        i += 1
    return total


#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns \nothing
def unique_sorted_values(values: list) -> int:
    n = len(values)
    total = 0
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        total += values[i]
        i += 1
    return total


#@ requires row_id >= 0
#@ ensures \result == row_id
#@ assigns \nothing
def index_by_id(row_id: int) -> int:
    return row_id


if __name__ == "__main__":
    words = ["red", "blue", "red", "green", "blue", "red"]
    print("freq:", word_frequencies(words))
    print("unique:", unique_sorted_values([3, 3, 1, 2, 1]))
    print("index:", index_by_id(10))