import pytest  # noqkey: F401

from pathlib import Path
from xqute.path import SpecPath
from pipen_verbose import (
    _format_secs,
    _format_atomic_value,
    _shorten_value,
    _is_mounted_path,
    _format_value,
    _log_values,
    _pretty_format,
)


@pytest.mark.parametrize(
    "value,expected",
    [
        ("/abc/def/ghi/klmn/opq", "/.../klmn/opq"),
        ("123", "123"),
        ("abcdefghijklmnopqrstuvwxyz", "abcde ... vwxyz"),
        ("123/789/abcdefghijklmnopqrstuvwxyz/456", "123/.../456"),
        ("abcdefghijklmnopqrstuvwxyz/888", ".../888"),
        ("888/abcdefghijklmnopqrstuvwxyz", "888/...vwxyz"),
        # not a str
        (123, "123"),
        # MountedPath
        (SpecPath("/abc/def/ghi/klmn/opq").mounted, "/.../klmn/opq"),
        (
            SpecPath("/abc/def/ghi/klmn/opq", mounted="abc").mounted,
            "abc ← /.../klmn/opq",
        ),
    ],
)
def test_shorten_value(value, expected):
    assert _shorten_value(value) == expected


def test_is_mounted_path():
    assert _is_mounted_path(SpecPath("/abc/def/ghi/klmn/opq", mounted="abc").mounted)
    assert not _is_mounted_path(SpecPath("/abc/def/ghi/klmn/opq").mounted)
    assert not _is_mounted_path(SpecPath("/abc/def/ghi/klmn/opq"))
    assert not _is_mounted_path("/abc/def/ghi/klmn/opq")
    assert not _is_mounted_path(123)


@pytest.mark.parametrize(
    "secs,expected",
    [
        (0, "00:00:00.000"),
        (1, "00:00:01.000"),
        (60, "00:01:00.000"),
        (61, "00:01:01.000"),
        (3600, "01:00:00.000"),
        (3661, "01:01:01.000"),
        (3661.1, "01:01:01.100"),
        (3661.123, "01:01:01.123"),
    ],
)
def test_format_secs(secs, expected):
    assert _format_secs(secs) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        # Simple values
        ("abc", "abc"),
        (123, 123),
        (True, True),
        (None, None),
        # MountedPath
        (SpecPath("/abc/def").mounted, "/abc/def"),
        (SpecPath("/abc/def", mounted="abc").mounted, "abc ← /abc/def"),
        # List
        ([1, 2, 3], [1, 2, 3]),
        (
            ["abc", SpecPath("/abc/def", mounted="abc").mounted],
            ["abc", "abc ← /abc/def"],
        ),
        # Tuple
        ((1, 2, 3), (1, 2, 3)),
        (
            ("abc", SpecPath("/abc/def", mounted="abc").mounted),
            ("abc", "abc ← /abc/def"),
        ),
        # Set
        ({1, 2, 3}, {1, 2, 3}),
        # Can't reliably test sets with SpecPath due to ordering
        # Dict
        ({"a": 1, "b": 2}, {"a": 1, "b": 2}),
        (
            {
                "a": SpecPath("/abc/def", mounted="abc").mounted,
                "b": [1, SpecPath("/123", mounted="xyz").mounted],
            },
            {"a": "abc ← /abc/def", "b": [1, "xyz ← /123"]},
        ),
        # Nested
        (
            {"a": [1, {"b": SpecPath("/path", mounted="mount").mounted}]},
            {"a": [1, {"b": "mount ← /path"}]},
        ),
    ],
)
def test_format_atomic_value(value, expected):
    result = _format_atomic_value(value)
    assert result == expected


@pytest.mark.parametrize(
    "value,key,key_len,expected",
    [
        ("/abc/def/ghi/klmn/opq", "key", 3, ["key: /abc/def/ghi/klmn/opq"]),
        ("123", "key", 3, ["key: 123"]),
        ("abcdefghijklmnopqrstuvwxyz", "key", 3, ["key: abcdefghijklmnopqrstuvwxyz"]),
        (
            "abcdefg\nhijklmnopqrstuvwxyz",
            "key",
            3,
            ["key: abcdefg", "     hijklmnopqrstuvwxyz"],
        ),
        # not a str
        (123, "key", 3, ["key: 123"]),
        # MountedPath
        (
            SpecPath("/abc/def/ghi/klmn/opq").mounted,
            "key",
            3,
            ["key: /abc/def/ghi/klmn/opq"],
        ),
        (
            SpecPath("/abc/def/ghi/klmn/opq", mounted="abc").mounted,
            "key",
            9,
            ["key      : abc ← /abc/def/ghi/klmn/opq"],
        ),
        (
            [SpecPath("/abc/def/ghi/klmn/opq", mounted="abc").mounted, 1],
            "key",
            9,
            ["key      : \\['abc ← /abc/def/ghi/klmn/opq', 1]"],
        ),
        (
            {
                "a": SpecPath("/abc/def/ghi/klmn/opq", mounted="abc").mounted,
                "b": 1,
                "c": SpecPath("/abc/def/ghi/klmn/opq").mounted,
                "def": Path("/rst/uvw/xyz"),
            },
            "key",
            9,
            [
                "key      : {'a': 'abc ← /abc/def/ghi/klmn/opq', 'b': 1, "
                "'c': '/abc/def/ghi/klmn/opq', 'def': '/rst/uvw/xyz'}"
            ],
        ),
    ],
)
def test_format_value(value, key, key_len, expected):
    assert _format_value(value, key, key_len, 0) == expected


def test_log_values(capsys):
    def log_fn(level, msg, logger):
        print(f"{level}: {msg}")

    values = {
        "a": "abc",
        "b": "def",
        "c": SpecPath("/abc/def", mounted="/ghi/jkl").mounted,
    }
    _log_values(values, log_fn, 0, prefix="x.")
    captured = capsys.readouterr().out
    assert "info: x.a: abc" in captured
    assert "info: x.b: def" in captured
    assert "info: x.c: /ghi/jkl ← /abc/def" in captured


def test_pretty_default():
    class ArbitraryObject:
        def __repr__(self):
            return "ArbitraryObject()"

    assert _pretty_format(ArbitraryObject()) == "ArbitraryObject()"


def test_pretty_dict_depth():
    test_dict = {
        "b": {
            "c": 2,
            "d": {
                "e": 3,
                "f": [4, 5, 6],
            },
        },
        "g": [7, 8, {"h": 9}],
        "a": 1,
    }
    result = _pretty_format(
        test_dict,
        _level=0,
        **{
            "depth": 1,
            "indent": 2,
            "width": 40,
            "compact": False,
            "sort_dicts": False,
            "underscore_numbers": False,
        },
    )
    expected = "{\n" "  'b': {...},\n" "  'g': [...],\n" "  'a': 1,\n" "}"
    assert result == expected

    result = _pretty_format(
        test_dict,
        _level=0,
        **{
            "depth": 1,
            "indent": 2,
            "width": 40,
            "compact": False,
            "sort_dicts": True,
            "underscore_numbers": False,
        },
    )
    expected = "{\n" "  'a': 1,\n" "  'b': {...},\n" "  'g': [...],\n" "}"
    assert result == expected


def test_pretty_nested_dict():
    test_dict = {
        "venn": {
            "enabled": "auto",
            "more_formats": [],
            "save_code": False,
            "devpars": {"res": 100},
        },
    }
    result = _pretty_format(
        test_dict,
        _level=0,
        **{
            "depth": None,
            "indent": 2,
            "width": 90,
            "compact": False,
            "sort_dicts": False,
            "underscore_numbers": False,
        },
    )
    expected = (
        "{\n"
        "  'venn': {\n"
        "    'enabled': 'auto',\n"
        "    'more_formats': [],\n"
        "    'save_code': False,\n"
        "    'devpars': {\n"
        "      'res': 100,\n"
        "    },\n"
        "  },\n"
        "}"
    )
    assert result == expected


def test_pretty_dict_compact():
    test_dict = {"x": {"a": 1, "b": 2, "c": 3}}
    result = _pretty_format(
        test_dict,
        indent=2,
        width=40,
        compact=True,
    )
    expected = "{'x': {'a': 1, 'b': 2, 'c': 3}}"
    assert result == expected

    result = _pretty_format(
        test_dict,
        indent=2,
        width=26,
        compact=True,
    )
    expected = "{\n" "  'x': {\n" "    'a': 1, 'b': 2, 'c': 3\n" "  },\n" "}"
    assert result == expected


def test_pretty_dict_wraps_even_compact():
    test_dict = {"x": {"a": 1, "b": 2, "c": 3}}
    result = _pretty_format(
        test_dict,
        indent=2,
        width=25,
        compact=True,
    )
    expected = (
        "{\n" "  'x': {\n" "    'a': 1,\n" "    'b': 2,\n" "    'c': 3,\n" "  },\n" "}"
    )
    assert result == expected


def test_pretty_list_compact():
    test_list = [1, 2, 3000]
    result = _pretty_format(
        test_list,
        _level=0,
        **{
            "depth": 1,
            "indent": 2,
            "width": 20,
            "compact": True,
            "sort_dicts": False,
            "underscore_numbers": True,
        },
    )
    expected = "[1, 2, 3_000]"
    assert result == expected


def test_pretty_list_wraps_even_compact():
    test_list = [1, 2, 3000]
    result = _pretty_format(
        test_list,
        _level=0,
        **{
            "depth": 1,
            "indent": 2,
            "width": 12,
            "compact": True,
            "sort_dicts": False,
            "underscore_numbers": True,
        },
    )
    expected = "[\n" "  1,\n" "  2,\n" "  3_000,\n" "]"
    assert result == expected


def test_pretty_list_compact_with_enough_width():
    test_list = [1, 2, 3000]
    result = _pretty_format(
        test_list,
        _level=0,
        **{
            "depth": 1,
            "indent": 2,
            "width": 13,
            "compact": True,
            "sort_dicts": False,
            "underscore_numbers": True,
        },
    )
    expected = "[1, 2, 3_000]"
    assert result == expected


def test_pretty_list_compact_but_wraps_as_one_line():
    test_list = {"x": [1, 2, 3000]}
    result = _pretty_format(
        test_list,
        _level=0,
        **{
            "indent": 2,
            "width": 15,
            "compact": True,
            "sort_dicts": False,
            "underscore_numbers": True,
        },
    )
    expected = "{\n" "  'x': [\n" "    1, 2, 3_000\n" "  ],\n" "}"
    assert result == expected


def test_pretty_list_non_compact():
    test_list = [1, 2, 3000]
    result = _pretty_format(
        test_list,
        _level=0,
        **{
            "depth": 1,
            "indent": 2,
            "width": 40,
            "compact": False,
            "sort_dicts": False,
            "underscore_numbers": True,
        },
    )
    expected = "[\n  1,\n  2,\n  3_000,\n]"
    assert result == expected


def test_pretty_empty_dict():
    test_dict = {}
    result = _pretty_format(
        test_dict,
        _level=0,
        **{
            "depth": 1,
            "indent": 2,
            "width": 40,
            "compact": False,
            "sort_dicts": False,
            "underscore_numbers": False,
        },
    )
    expected = "{}"
    assert result == expected


def test_pretty_empty_list():

    test_list = []
    result = _pretty_format(
        test_list,
        _level=0,
        **{
            "depth": 1,
            "indent": 2,
            "width": 40,
            "compact": False,
            "sort_dicts": False,
            "underscore_numbers": False,
        },
    )
    expected = "[]"
    assert result == expected


def test_pretty_real_case():
    test_dict = {
        "another_key": {
            "nested_list_key": [
                {"key1": "value1", "key2": "value2"},
                {
                    "key3": "value3",
                    "key4": "value4",
                    "key5": "value5",
                },
            ],
        },
    }
    result = _pretty_format(
        test_dict,
        _level=0,
        **{
            "depth": None,
            "indent": 2,
            "width": 79,
            "compact": True,
            "sort_dicts": False,
            "underscore_numbers": False,
        },
    )
    expected = (
        "{\n"
        "  'another_key': {\n"
        "    'nested_list_key': [\n"
        "      {'key1': 'value1', 'key2': 'value2'},\n"
        "      {'key3': 'value3', 'key4': 'value4', 'key5': 'value5'},\n"
        "    ],\n"
        "  },\n"
        "}"
    )
    assert result == expected
