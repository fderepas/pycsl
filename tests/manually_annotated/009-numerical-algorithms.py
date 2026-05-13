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


#@ requires 1 == 1
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def is_prime(n: int) -> int:
    is_p = 1
    if n < 2:
        is_p = 0
    else:
        if n == 2:
            is_p = 1
        else:
            if n % 2 == 0:
                is_p = 0
            else:
                divisor = 3
                flag = 1
                #@ loop invariant divisor <= n + 1
                #@ loop invariant divisor >= 3
                #@ loop invariant flag == 0 or flag == 1
                #@ loop invariant is_p == 0 or is_p == 1
                #@ loop variant (n - divisor + 1) + flag
                while flag == 1:
                    if divisor * divisor > n:
                        flag = 0
                    else:
                        if n % divisor == 0:
                            is_p = 0
                            flag = 0
                        else:
                            divisor += 2
    return is_p


if __name__ == "__main__":
    print("gcd(48, 18):", gcd(48, 18))
    print("is_prime(97):", is_prime(97))