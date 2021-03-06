import ast
import re
import os

import pycodestyle
import pytest

from flake8_import_order.flake8_linter import Linter

from tests.utils import extract_expected_errors


def load_test_cases():
    base_path = os.path.dirname(__file__)
    test_case_path = os.path.join(base_path, "test_cases")
    test_case_files = os.listdir(test_case_path)

    test_cases = []

    for fname in test_case_files:
        if not fname.endswith(".py"):
            continue

        fullpath = os.path.join(test_case_path, fname)
        data = open(fullpath).read()
        tree = ast.parse(data, fullpath)
        codes, messages = extract_expected_errors(data)

        test_cases.append((tree, fullpath, codes, messages))

    return test_cases


@pytest.mark.parametrize(
    "tree, filename, expected_codes, expected_messages",
    load_test_cases()
)
def test_expected_error(tree, filename, expected_codes, expected_messages):
    argv = [
        "--application-import-names=flake8_import_order,tests"
    ]

    for style in ['google', 'smarkets', 'pep8']:
        if style in filename:
            argv.append('--import-order-style=' + style)
            break

    parser = pycodestyle.get_parser('', '')
    Linter.add_options(parser)
    options, args = parser.parse_args(argv)
    Linter.parse_options(options)

    checker = Linter(tree, filename)
    codes = []
    messages = []
    for lineno, col_offset, msg, instance in checker.run():
        code, message = msg.split(" ", 1)
        codes.append(code)
        messages.append(message)
    assert codes == expected_codes
    assert set(messages) >= set(expected_messages)


def test_I101_default_style():
    base_path = os.path.dirname(__file__)
    test_case_path = os.path.join(base_path, "test_cases")
    fullpath = os.path.join(test_case_path, "bad_order.py")
    data = open(fullpath).read()
    tree = ast.parse(data, fullpath)

    argv = [
        "--application-import-names=flake8_import_order,tests",
#        "--import-order-style=google",
    ]

    parser = pycodestyle.get_parser('', '')
    Linter.add_options(parser)
    options, args = parser.parse_args(argv)
    Linter.parse_options(options)

    checker = Linter(tree, fullpath)
    codes = []
    messages = []
    for lineno, col_offset, msg, instance in checker.run():
        code, message = msg.split(" ", 1)
        codes.append(code)
        messages.append(message)
    assert codes == ["I101"]
    assert messages == [
        "Imported names are in the wrong order. Should be A, D, c"
    ]


def test_I101_google_style():
    base_path = os.path.dirname(__file__)
    test_case_path = os.path.join(base_path, "test_cases")
    fullpath = os.path.join(test_case_path, "bad_order_google.py")
    data = open(fullpath).read()
    tree = ast.parse(data, fullpath)

    argv = [
        "--application-import-names=flake8_import_order,tests",
        "--import-order-style=google",
    ]

    parser = pycodestyle.get_parser('', '')
    Linter.add_options(parser)
    options, args = parser.parse_args(argv)
    Linter.parse_options(options)

    checker = Linter(tree, fullpath)
    codes = []
    messages = []
    for lineno, col_offset, msg, instance in checker.run():
        code, message = msg.split(" ", 1)
        codes.append(code)
        messages.append(message)
    assert codes == ["I101"]
    assert messages == [
        "Imported names are in the wrong order. Should be A, c, D"
    ]
