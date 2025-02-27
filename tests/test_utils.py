import pytest  # noqkey: F401

from xqute.path import DualPath
from pipen_verbose import (
    _format_secs,
    _shorten_value,
    _is_mounted_path,
    _format_value,
    _log_values,
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
        (DualPath("/abc/def/ghi/klmn/opq").mounted, "/.../klmn/opq"),
        (DualPath("/abc/def/ghi/klmn/opq", mounted="abc").mounted, "/.../klmn/opq:abc"),
    ],
)
def test_shorten_value(value, expected):
    assert _shorten_value(value) == expected


def test_is_mounted_path():
    assert _is_mounted_path(DualPath("/abc/def/ghi/klmn/opq", mounted="abc").mounted)
    assert not _is_mounted_path(DualPath("/abc/def/ghi/klmn/opq").mounted)
    assert not _is_mounted_path(DualPath("/abc/def/ghi/klmn/opq"))
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
            DualPath("/abc/def/ghi/klmn/opq").mounted,
            "key",
            3,
            ["key: /abc/def/ghi/klmn/opq"],
        ),
        (
            DualPath("/abc/def/ghi/klmn/opq", mounted="abc").mounted,
            "key",
            9,
            ["key      : abc", "key.spec : /abc/def/ghi/klmn/opq"],
        ),
    ],
)
def test_format_value(value, key, key_len, expected):
    assert _format_value(value, key, key_len) == expected


def test_log_values(capsys):
    def log_fn(level, msg, logger):
        print(f"{level}: {msg}")

    values = {
        "a": "abc",
        "b": "def",
        "c": DualPath("/abc/def", mounted="/ghi/jkl").mounted,
    }
    _log_values(values, log_fn, prefix="x.")
    captured = capsys.readouterr().out
    assert "info: x.a     : abc" in captured
    assert "info: x.b     : def" in captured
    assert "info: x.c     : /ghi/jkl" in captured
    assert "info: x.c.spec: /abc/def" in captured
