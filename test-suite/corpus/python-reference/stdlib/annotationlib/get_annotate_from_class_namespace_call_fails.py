"""Test annotationlib.get_annotate_from_class_namespace L5 — negative: caller can't discharge requires.

Documents the soundness path: callers that don't establish the
function's precondition fail to verify under full proof. The
corpus runner uses `--no-proof` for fast iteration; the failure
mode is exercised manually with `--proof`.
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import annotationlib  # noqa: F401


#@ ensures True
def use_get_annotate_from_class_namespace_unsafe(x: int) -> int:
    return annotationlib.get_annotate_from_class_namespace(x)


if __name__ == "__main__":
    pass
