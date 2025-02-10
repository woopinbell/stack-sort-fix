#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PUSH_SWAP = ROOT / "push_swap"
CHECKER = ROOT / "checker"


def run(args, input_text=None):
    return subprocess.run(
        [str(arg) for arg in args],
        input=input_text,
        text=True,
        capture_output=True,
        cwd=ROOT,
    )


def fail(message):
    print(message, file=sys.stderr)
    raise SystemExit(1)


def assert_equal(actual, expected, message):
    if actual != expected:
        fail(f"{message}: expected {expected!r}, got {actual!r}")


def assert_ok(condition, message):
    if not condition:
        fail(message)


def test_parser_inputs():
    no_args = run([PUSH_SWAP])
    assert_equal(no_args.returncode, 0, "push_swap without args exits cleanly")
    assert_equal(no_args.stdout, "", "push_swap without args has no stdout")
    assert_equal(no_args.stderr, "", "push_swap without args has no stderr")

    valid = run([PUSH_SWAP, "3 2", "1"])
    assert_equal(valid.returncode, 0, "quoted and split argv are accepted")
    checked = run([CHECKER, "3 2", "1"], valid.stdout)
    assert_equal(checked.returncode, 0, "checker accepts generated moves")
    assert_equal(checked.stdout, "OK\n", "generated moves sort quoted input")

    invalid_cases = [
        ["1", "2", "2"],
        ["2147483648"],
        ["-2147483649"],
        ["12a"],
        ["+"],
        [""],
        ["1", "2 1"],
    ]
    for case in invalid_cases:
        result = run([PUSH_SWAP] + case)
        assert_ok(result.returncode != 0, f"invalid input {case!r} fails")
        assert_equal(result.stdout, "", f"invalid input {case!r} has no stdout")
        assert_equal(result.stderr, "Error\n", f"invalid input {case!r} reports Error")


def checker_ok(args, program, label):
    result = run([CHECKER] + args, program)
    assert_equal(result.returncode, 0, f"{label} checker exit")
    assert_equal(result.stdout, "OK\n", f"{label} checker stdout")
    assert_equal(result.stderr, "", f"{label} checker stderr")


def test_checker_operations():
    cases = [
        ("sa", ["2", "1"], "sa\n"),
        ("sb", ["2", "1", "3"], "pb\npb\nsb\npa\npa\n"),
        ("ss", ["2", "1", "4", "3"], "pb\npb\nss\npa\npa\n"),
        ("pa-pb", ["1", "2"], "pb\npa\n"),
        ("ra", ["3", "1", "2"], "ra\n"),
        ("rb", ["2", "1", "3"], "pb\npb\nrb\npa\npa\n"),
        ("rr", ["2", "1", "4", "3"], "pb\npb\nrr\npa\npa\n"),
        ("rra", ["2", "3", "1"], "rra\n"),
        ("rrb", ["2", "1", "3"], "pb\npb\nrrb\npa\npa\n"),
        ("rrr", ["2", "1", "4", "3"], "pb\npb\nrrr\npa\npa\n"),
    ]
    for label, args, program in cases:
        checker_ok(args, program, label)

    ko = run([CHECKER, "2", "1"], "")
    assert_equal(ko.returncode, 0, "unsorted checker input exits cleanly")
    assert_equal(ko.stdout, "KO\n", "unsorted checker input reports KO")
    assert_equal(ko.stderr, "", "unsorted checker input has no stderr")

    invalid = run([CHECKER, "1", "2"], "ra\nwat\n")
    assert_ok(invalid.returncode != 0, "invalid checker command fails")
    assert_equal(invalid.stdout, "", "invalid checker command has no stdout")
    assert_equal(invalid.stderr, "Error\n", "invalid checker command reports Error")


def main():
    test_parser_inputs()
    test_checker_operations()
    print("tests passed")


if __name__ == "__main__":
    main()
