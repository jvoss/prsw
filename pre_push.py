#!/usr/bin/env python3
"""
Pre-push static analysis utility.

Running this script performs all tests and static analysis. This is useful
prior to pushing or submitting a PR.
"""

import sys
from subprocess import CalledProcessError, check_call


def run(program):
    """Runs a program."""

    print(f"Running {program}")
    try:
        check_call(program)
    except CalledProcessError:
        print(f"Failed to run {program}")
        return False
    except Exception as e:
        sys.stderr.write(f"{str(e)}\n")
        sys.exit(1)

    return True


def run_linters():
    """Runs all linters."""
    run("black --check .")
    run("flake8 --exclude docs rsaw")
    run("pydocstyle rsaw")


def run_unit_tests():
    """Runs all unit tests."""
    run("pytest")


def main():
    success = True

    try:
        run_unit_tests()
        run_linters()
    except KeyboardInterrupt:
        return int(not False)

    return int(not success)


if __name__ == "__main__":
    exit_code = main()
    print("\npre_push.py: Success!" if not exit_code else "\npre_push.py: Fail")
    sys.exit(exit_code)
