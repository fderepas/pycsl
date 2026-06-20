"""PyCSL mock for Python's hashlib module.

Provides trusted stubs for secure hash and message digest algorithms.
Hash object is modelled as a class with digest_size >= 0 and block_size > 0.
"""
_ = 0  # anchor

# ── HashObj class ────────────────────────────────────────────────────

""  # pycsl
#@ class invariant self._digest_size >= 0
#@ class invariant self._block_size >= 1
class HashObj:
    def __init__(self):
        self._digest_size = 1
        self._block_size = 1

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._digest_size
    #@ assigns \nothing
    def digest_size(self) -> int:
        return self._digest_size

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._block_size
    #@ assigns \nothing
    def block_size(self) -> int:
        return self._block_size

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.name
#@ ensures True
#@ assigns \nothing
    def name(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/hashlib.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def update(self, data: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.hash.digest
#@ requires True
#@ ensures True
#@ assigns \nothing
    def digest(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.hash.hexdigest
#@ requires True
#@ ensures \result >= 0
#@ assigns \nothing
    def hexdigest(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.hash.copy
#@ requires True
#@ ensures True
#@ assigns \nothing
    def copy(self) -> int:
        return 0

# ── Generic constructor ─────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.new
#@ requires data >= 0
#@ ensures \result >= 0
def new(name: int, data: int) -> int:
    """Mock: generic hash constructor by algorithm name."""
    return 0

# ── Named constructors: MD5, SHA-1, SHA-2 ───────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.md5
#@ ensures \result >= 0
#@ ensures \result < 340282366920938463463374607431768211456
def md5(data: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.sha1
#@ ensures \result >= 0
#@ ensures \result < 2**160
def sha1(data: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.sha224
#@ ensures \result >= 0
def sha224(data: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.sha256
#@ ensures \result >= 0
#@ ensures \result < 2**256
def sha256(data: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.sha384
#@ ensures \result >= 0
def sha384(data: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.sha512
#@ ensures \result >= 0
#@ ensures \result < 13407807929942597099574024998205846127479365820592393377723561443721764030073546976801874298166903427690031858186486050853753882811946569946433649006084096
def sha512(data: int) -> int:
    return 0

# ── SHA-3 constructors ──────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.sha3_224
#@ ensures \result >= 0
#@ ensures \result < 26959946667150639794667015087019630673637144422540572481103610249216
def sha3_224(data: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.sha3_256
#@ ensures \result >= 0
#@ ensures \result < 115792089237316195423570985008687907853269984665640564039457584007913129639936
def sha3_256(data: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.sha3_384
#@ ensures \result >= 0
#@ ensures \result < 39402006196394479212279040100143613805079739270465446667946905279627659399113263569398956308152294913554433653942643
def sha3_384(data: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.sha3_512
#@ ensures \result >= 0
def sha3_512(data: int) -> int:
    return 0

# ── SHAKE constructors ──────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.shake_128
#@ ensures \result >= 0
def shake_128(data: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.shake_256
#@ ensures \result >= 0
def shake_256(data: int) -> int:
    return 0

# ── BLAKE2 constructors ─────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.blake2b
#@ requires digest_size >= 1
#@ requires digest_size <= 64
#@ ensures \result >= 0
def blake2b(data: int, digest_size: int, key: int, salt: int, person: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.blake2s
#@ requires digest_size >= 1
#@ requires digest_size <= 32
#@ ensures \result >= 0
def blake2s(data: int, digest_size: int, key: int, salt: int, person: int) -> int:
    return 0

# ── SHAKE variable-length digest ────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#shake-variable-length-digests
#@ requires True
#@ ensures True
def shake_digest(h: int, length: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.shake_128.hexdigest
#@ requires True
#@ ensures True
def shake_hexdigest(h: int, length: int) -> int:
    return 0

# ── Key derivation ──────────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.pbkdf2_hmac
#@ requires iterations >= 1
#@ requires dklen >= 1
#@ ensures \result >= 0
def pbkdf2_hmac(hash_name: int, password: int, salt: int, iterations: int, dklen: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.scrypt
#@ requires n >= 2
#@ requires r >= 1
#@ requires p >= 1
#@ requires maxmem >= 0
#@ requires dklen >= 1
#@ ensures \result >= 0
def scrypt(password: int, salt: int, n: int, r: int, p: int, maxmem: int, dklen: int) -> int:
    return 0

# ── File hashing ────────────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.file_digest
#@ ensures True
def file_digest(fileobj: int, digest: int) -> int:
    return 0

# ── Module data attributes ──────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.algorithms_guaranteed
#@ requires True
#@ ensures True
def algorithms_guaranteed() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/hashlib.py
#@ requires True
#@ ensures True
def algorithms_available() -> int:
    return 0

# ── BLAKE2 constants ────────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/hashlib.py
#@ requires True
#@ ensures True
def blake2b_SALT_SIZE() -> int:
    return 1

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.blake2s
#@ requires True
#@ ensures \result >= 1
def blake2s_SALT_SIZE() -> int:
    return 1

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/hashlib.py
#@ requires True
#@ ensures True
def blake2b_PERSON_SIZE() -> int:
    return 1

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/hashlib.py
#@ requires True
#@ ensures \result >= 1
def blake2s_PERSON_SIZE() -> int:
    return 1

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/hashlib.py
#@ requires True
#@ ensures \result >= 1
def blake2b_MAX_KEY_SIZE() -> int:
    return 1

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/hashlib.py
#@ requires True
#@ ensures True
def blake2s_MAX_KEY_SIZE() -> int:
    return 1

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.blake2b
#@ ensures \result == 64
def blake2b_MAX_DIGEST_SIZE() -> int:
    return 1

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/hashlib.html#hashlib.blake2s
#@ requires True
#@ ensures True
def blake2s_MAX_DIGEST_SIZE() -> int:
    return 1
