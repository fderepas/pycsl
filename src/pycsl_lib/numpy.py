"""PyCSL mock for numpy.

Provides trusted stubs for numerical computing with NumPy.
NdarrayObj models an ndarray with ndim and size invariants.
"""
_ = 0  # anchor

# ── NdarrayObj class ────────────────────────────────────────────────

""  # pycsl
#@ class invariant self._ndim >= 1
#@ class invariant self._size >= 0
class NdarrayObj:
    def __init__(self):
        self._ndim = 1
        self._size = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._ndim
    #@ assigns \nothing
    def ndim(self) -> int:
        return self._ndim

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._size
    #@ assigns \nothing
    def size(self) -> int:
        return self._size

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def shape(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def dtype(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def reshape(self, new_shape: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def transpose(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def flatten(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def ravel(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def copy(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def astype(self, dt: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == 0
    #@ assigns self._size
    def fill(self, value: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def item(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def tolist(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def sum_arr(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def mean_arr(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def std_arr(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def var_arr(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def min_arr(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def max_arr(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def argmin_arr(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def argmax_arr(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def dot(self, other: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def clip(self, a_min: int, a_max: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == 0
    #@ assigns self._size
    def sort(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def argsort(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def searchsorted(self, v: int) -> int:
        return 0

# ── Array creation ──────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def array(obj: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def zeros(shape: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def ones(shape: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def empty(shape: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def full(shape: int, fill_value: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def arange(start: int, stop: int, step: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def linspace(start: int, stop: int, num: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def eye(n: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def identity(n: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def zeros_like(a: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def ones_like(a: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def empty_like(a: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def copy_array(a: int) -> int:
    return 0

# ── Mathematical operations ─────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def dot_arrays(a: int, b: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def matmul(a: int, b: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def abs_val(x: int) -> int:
    return 0

#@ \trusted
def sqrt(x: int) -> int:
    return 0

#@ \trusted
def exp(x: int) -> int:
    return 0

#@ \trusted
def log(x: int) -> int:
    return 0

#@ \trusted
def log2(x: int) -> int:
    return 0

#@ \trusted
def log10(x: int) -> int:
    return 0

#@ \trusted
def sin(x: int) -> int:
    return 0

#@ \trusted
def cos(x: int) -> int:
    return 0

#@ \trusted
def tan(x: int) -> int:
    return 0

#@ \trusted
def power(x: int, y: int) -> int:
    return 0

#@ \trusted
def floor(x: int) -> int:
    return 0

#@ \trusted
def ceil(x: int) -> int:
    return 0

#@ \trusted
def round_(a: int, decimals: int) -> int:
    return 0

#@ \trusted
def clip_array(a: int, a_min: int, a_max: int) -> int:
    return 0

# ── Aggregation ─────────────────────────────────────────────────────

#@ \trusted
def sum_all(a: int) -> int:
    return 0

#@ \trusted
def prod(a: int) -> int:
    return 0

#@ \trusted
def mean_all(a: int) -> int:
    return 0

#@ \trusted
def std_all(a: int) -> int:
    return 0

#@ \trusted
def var_all(a: int) -> int:
    return 0

#@ \trusted
def min_all(a: int) -> int:
    return 0

#@ \trusted
def max_all(a: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def argmin(a: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def argmax(a: int) -> int:
    return 0

#@ \trusted
def cumsum(a: int) -> int:
    return 0

#@ \trusted
def cumprod(a: int) -> int:
    return 0

# ── Array manipulation ──────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def reshape_array(a: int, shape: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def transpose_array(a: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def flatten_array(a: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def ravel_array(a: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def concatenate(arrays: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def stack(arrays: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def vstack(tup: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def hstack(tup: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def split(ary: int, indices: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def squeeze(a: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def expand_dims(a: int, axis: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def sort_array(a: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def argsort_array(a: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def where(condition: int, x: int, y: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def unique(ar: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def searchsorted_array(a: int, v: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def append(arr: int, values: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def delete(arr: int, obj: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def insert(arr: int, obj: int, values: int) -> int:
    return 0

# ── Shape and type ──────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def ndim_of(a: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def size_of(a: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def shape_of(a: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def dtype_of(a: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def astype_array(a: int, dt: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def asarray(a: int) -> int:
    return 0

# ── Linear algebra ──────────────────────────────────────────────────

#@ \trusted
def linalg_norm(x: int) -> int:
    return 0

#@ \trusted
def linalg_det(a: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def linalg_inv(a: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def linalg_solve(a: int, b: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def linalg_eig(a: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def linalg_svd(a: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def linalg_matrix_rank(m: int) -> int:
    return 0

# ── Random ──────────────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def random_rand(d0: int) -> int:
    return 0

#@ \trusted
def random_randn(d0: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def random_randint(low: int, high: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def random_seed(seed: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def random_choice(a: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def random_shuffle(x: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def random_permutation(x: int) -> int:
    return 0

# ── I/O ─────────────────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def load(file: int) -> int:
    return 0

#@ \trusted
#@ ensures \result == 0
def save(file: int, arr: int) -> int:
    return 0

#@ \trusted
#@ ensures \result == 0
def savez(file: int, arr: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def loadtxt(fname: int) -> int:
    return 0

#@ \trusted
#@ ensures \result == 0
def savetxt(fname: int, x: int) -> int:
    return 0

# ── Constants ───────────────────────────────────────────────────────

pi = 0
e = 0
inf = 0
nan = 0
newaxis = 0
