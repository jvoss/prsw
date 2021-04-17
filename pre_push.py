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

    print(f"Running: {' '.join(program)}")
    try:
        check_call(program, shell=False)
    except CalledProcessError:
        print(f"Failed to run {program}")
        return False
    except Exception as e:
        sys.stderr.write(f"{str(e)}\n")
        sys.exit(1)

    return True


def run_linters():
    """Runs all linters."""
    success = True
    success &= run(["black", "--check", "."])
    success &= run(["flake8", "--exclude", "docs", "prsw", "tests"])
    success &= run(["pydocstyle", "prsw"])
    return success


def run_unit_tests():
    """Runs all unit tests."""
    success = True
    success &= run(["pytest"])
    return success


def main():
    success = True

    try:
        success &= run_unit_tests()
        success &= run_linters()
    except KeyboardInterrupt:
        return int(not success)

    return int(not success)


if __name__ == "__main__":
    exit_code = main()
    print("\npre_push.py: Success!" if not exit_code else "\npre_push.py: Fail")
    sys.exit(exit_code)
