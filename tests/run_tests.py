#!/usr/bin/env python3
from pathlib import Path
import itertools
import random
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PUSH_SWAP = ROOT / "push_swap"
CHECKER = ROOT / "checker"
VALID_MOVES = {"sa", "sb", "ss", "pa", "pb", "ra", "rb", "rr", "rra", "rrb", "rrr"}


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


def split_moves(output):
    if output == "":
        return []
    moves = output.splitlines()
    for move in moves:
        assert_ok(move in VALID_MOVES, f"unknown move emitted: {move!r}")
    return moves


def apply_moves(values, moves):
    a = list(values)
    b = []

    def swap(stack):
        if len(stack) > 1:
            stack[0], stack[1] = stack[1], stack[0]

    def push(dst, src):
        if src:
            dst.insert(0, src.pop(0))

    def rotate(stack):
        if len(stack) > 1:
            stack.append(stack.pop(0))

    def reverse_rotate(stack):
        if len(stack) > 1:
            stack.insert(0, stack.pop())

    for move in moves:
        if move == "sa":
            swap(a)
        elif move == "sb":
            swap(b)
        elif move == "ss":
            swap(a)
            swap(b)
        elif move == "pa":
            push(a, b)
        elif move == "pb":
            push(b, a)
        elif move == "ra":
            rotate(a)
        elif move == "rb":
            rotate(b)
        elif move == "rr":
            rotate(a)
            rotate(b)
        elif move == "rra":
            reverse_rotate(a)
        elif move == "rrb":
            reverse_rotate(b)
        elif move == "rrr":
            reverse_rotate(a)
            reverse_rotate(b)
    return a, b


def assert_sorted_by_program(values):
    args = [str(value) for value in values]
    result = run([PUSH_SWAP] + args)
    assert_equal(result.returncode, 0, f"push_swap sorts {values!r}")
    assert_equal(result.stderr, "", f"push_swap sort stderr for {values!r}")
    moves = split_moves(result.stdout)
    a, b = apply_moves(values, moves)
    assert_equal(a, sorted(values), f"move stream sorts stack {values!r}")
    assert_equal(b, [], f"move stream leaves stack b empty for {values!r}")
    checked = run([CHECKER] + args, result.stdout)
    assert_equal(checked.returncode, 0, f"checker validates stream for {values!r}")
    assert_equal(checked.stdout, "OK\n", f"checker OK for {values!r}")
    return moves


def test_sort_programs():
    sorted_case = run([PUSH_SWAP, "1", "2", "3", "4", "5"])
    assert_equal(sorted_case.returncode, 0, "already sorted input exits cleanly")
    assert_equal(sorted_case.stdout, "", "already sorted input emits no moves")
    assert_equal(sorted_case.stderr, "", "already sorted input has no stderr")

    fixed_cases = [
        [3, 2, 1],
        [5, -1, 4, 0, 2],
        [42, -2147483648, 0, 2147483647, -7, 9],
        [8, 3, 7, 1, 9, 0, 2, 6, 5, 4],
    ]
    for values in fixed_cases:
        assert_sorted_by_program(values)

    for size in range(2, 6):
        for values in itertools.permutations(range(size)):
            assert_sorted_by_program(list(values))


def test_move_counts():
    random.seed(4242)
    limits = [
        (100, 1500),
        (500, 8000),
    ]
    for size, limit in limits:
        values = random.sample(range(-10000, 10000), size)
        moves = assert_sorted_by_program(values)
        assert_ok(
            len(moves) <= limit,
            f"{size} value move count {len(moves)} exceeds {limit}",
        )


def main():
    test_parser_inputs()
    test_checker_operations()
    test_sort_programs()
    test_move_counts()
    print("tests passed")


if __name__ == "__main__":
    main()
