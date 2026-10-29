# Advice probe (route #453, module function): witness 6860 with the claim dropped.
import shutil


def f(path: str) -> int:
    shutil.copy(path, path + '.bak')
    return len(path)
