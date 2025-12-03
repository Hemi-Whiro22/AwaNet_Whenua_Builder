import sys


def ding():
    sys.stdout.write("\a")
    sys.stdout.flush()


def good():
    print("[OK] ✓\a")


def bad():
    print("[ERR] ✗\a")
