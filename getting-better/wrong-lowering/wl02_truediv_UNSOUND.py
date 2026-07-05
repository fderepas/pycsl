"""WL-02 UNSOUND — Python `/` is TRUE division (returns float); PyCSL lowers a body
`/` to integer Euclidean `pycsl_div`, dropping the fractional part.

CPython ground truth:  5 / 2 == 2.5   (a float; `2.5 == 2` is False)
PyCSL body lowering:   pycsl_div 5 2 == 2  (int Euclidean div)

Detector D3: PyCSL PROVES `\result == 2`, which is FALSE of Python -> UNSOUND.
(The faithful-typed variant `-> float` fail-closes with a real-vs-int TYPEERR;
the int-return path silently certifies the wrong value.)"""
_ = 0
#@ ensures \result == 2
def f() -> int:
    return 5 / 2

if __name__ == "__main__":
    assert f() == 2.5  # CPython -> the proved `==2` is false
