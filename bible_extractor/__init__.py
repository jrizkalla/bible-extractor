# Simple python >= 3.6 guard
try:
    eval('f""')
except SyntaxError:
    raise RuntimeError("This script needs Python 3.6 or higher to run")
