""  # pycsl
#@ requires 1 == 1
#@ ensures \result >= 0
#@ assigns \nothing
def gcd(a: int, b: int) -> int:
    x = a
    y = b
    if x < 0:
        x = -x
    if y < 0:
        y = -y
    #@ loop invariant x >= 0
    #@ loop invariant y >= 0
    #@ loop variant y
    while y != 0:
        temp = x % y
        x = y
        y = temp
    return x


#@ requires n >= 0
#@ ensures 1 == 1
#@ assigns \nothing
def is_prime(n: int) -> int:
    is_p = 1
    if n < 2:
        is_p = 0
    else:
        divisor = 2
        #@ loop invariant 2 <= divisor and divisor <= n
        #@ loop variant n - divisor
        while divisor < n:
            if n % divisor == 0:
                is_p = 0
            divisor += 1
    return is_p


if __name__ == "__main__":
    print("gcd(48, 18):", gcd(48, 18))
    print("is_prime(97):", is_prime(97))