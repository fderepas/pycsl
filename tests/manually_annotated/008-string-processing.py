""  # pycsl
#@ requires 1 == 1
#@ ensures \result >= 0
#@ assigns \nothing
def normalize(chars: list) -> int:
    n = len(chars)
    count = 0
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant n == \length(chars)
    #@ loop invariant count >= 0
    #@ loop invariant count <= i
    #@ loop variant n - i
    while i < n:
        if chars[i] >= 0:
            count += 1
        i += 1
    return count


#@ requires 1 == 1
#@ ensures \result >= 0
#@ assigns \nothing
def is_palindrome(cleaned: list) -> int:
    n = len(cleaned)
    left = 0
    right = n - 1
    result_val = 1
    #@ loop invariant 0 <= left
    #@ loop invariant right >= -1
    #@ loop invariant right < n
    #@ loop invariant n == \length(cleaned)
    #@ loop invariant result_val >= 0
    #@ loop variant right - left + 1
    while left < right:
        if cleaned[left] != cleaned[right]:
            result_val = 0
            left = right
        else:
            left += 1
            right -= 1
    return result_val


#@ requires 1 == 1
#@ ensures \result >= 0
#@ assigns \nothing
def word_count(tokens: list) -> int:
    n = len(tokens)
    return n


if __name__ == "__main__":
    cleaned = [ord(c) for c in "amanaplanacanalpanama"]
    print("palindrome:", is_palindrome(cleaned))
    print("word_count:", word_count([1, 2, 3]))