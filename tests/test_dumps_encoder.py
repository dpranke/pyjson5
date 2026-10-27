"""dumps()/JSON5Encoder coverage for gaps in upstream tests/lib_test.py.

Upstream covers the main encoder paths (indent, quote styles, sort
keys, circular refs, custom encoders) well. The cases below were chosen
by grepping that file first: sequence-like values that are not lists,
separator handling without indent, U+2028/U+2029 escaping, the
is_identifier/is_reserved_word helpers used directly, quote_style not
affecting keys, allow_nan=False for non-string keys, and round-trips
through the json-compatible option combination.

Every assertion below was confirmed against the cloned source with a
probe script before being written here.
"""

import io
import json as stdlib_json

import pytest

import json5
from json5 import QuoteStyle
from json5.lib import JSON5Encoder


# ------------------------------------------------------- sequence-like values

def test_tuple_dumps_as_array():
    assert json5.dumps((1, 2)) == '[1, 2]'


def test_empty_tuple_dumps_as_empty_array():
    assert json5.dumps(()) == '[]'


def test_range_dumps_as_array():
    assert json5.dumps(range(3)) == '[0, 1, 2]'


def test_bytes_dump_as_int_array():
    # bytes is sequence-like (__getitem__ + __iter__), so the encoder
    # treats it as an array of ints rather than as a string.
    assert json5.dumps(b'xy') == '[120, 121]'


def test_single_element_set_via_default_hook():
    assert json5.dumps({7}, default=list) == '[7]'


def test_dump_writes_to_a_file_object():
    stream = io.StringIO()
    assert json5.dump({'a': 1}, stream) is None
    assert stream.getvalue() == '{a: 1}'


# ------------------------------------------------------------ options / output

def test_separators_without_indent():
    assert json5.dumps({'a': 1}, separators=(',', ':')) == '{a:1}'


def test_sort_keys_applies_to_nested_objects_with_indent():
    assert json5.dumps([{'b': 2, 'a': 1}], indent=2, sort_keys=True) == (
        '[\n  {\n    a: 1,\n    b: 2,\n  },\n]'
    )


def test_negative_zero_float_round_trips_its_sign():
    assert json5.dumps(-0.0) == '-0.0'
    assert json5.dumps(0.0) == '0.0'


def test_large_int_and_exponent_float_spellings():
    assert json5.dumps(10**30) == '1000000000000000000000000000000'
    assert json5.dumps(1e20) == '1e+20'


def test_line_and_paragraph_separators_are_always_escaped():
    # Even with ensure_ascii=False, U+2028/U+2029 are escaped (lib.py
    # special-cases them), unlike other non-ASCII characters.
    assert json5.dumps('\u2028', ensure_ascii=False) == '"\\u2028"'
    assert json5.dumps('\u2029', ensure_ascii=False) == '"\\u2029"'
    assert json5.dumps({'a\u2028b': 1}) == '{"a\\u2028b": 1}'


def test_emoji_escaping_depends_on_ensure_ascii():
    assert json5.dumps('\U0001f600', ensure_ascii=False) == '"😀"'
    assert json5.dumps('\U0001f600', ensure_ascii=True) == '"\\ud83d\\ude00"'


def test_empty_and_blank_string_keys_are_quoted():
    assert json5.dumps({'': 1, ' ': 2}) == '{"": 1, " ": 2}'


def test_skipkeys_drops_only_the_bad_keys():
    assert json5.dumps({(1, 2): 'x', 'a': 1}, skipkeys=True) == '{a: 1}'


def test_tuple_key_error_message():
    # Note the stray literal 'f' in the message: lib.py raises
    # f'Invalid key f{obj}'. Pin the real text, not the intended text.
    with pytest.raises(TypeError, match='Invalid key f'):
        json5.dumps({(1, 2): 'x'})


def test_allow_nan_false_rejects_nan_and_inf_keys():
    with pytest.raises(ValueError, match='Illegal JSON5 value: nan'):
        json5.dumps({float('nan'): 1}, allow_nan=False)
    with pytest.raises(ValueError, match='Illegal JSON5 value: inf'):
        json5.dumps({float('inf'): 1}, allow_nan=False)


def test_circular_dict_is_rejected_but_shared_refs_are_fine():
    cyclic = {}
    cyclic['self'] = cyclic
    with pytest.raises(ValueError, match='Circular reference detected'):
        json5.dumps(cyclic)
    shared = [1]
    assert json5.dumps({'a': shared, 'b': shared}) == '{a: [1], b: [1]}'


# ------------------------------------------------------------- encoder helpers

@pytest.mark.parametrize(
    'key,expected',
    [
        ('foo', True),
        ('foo bar', False),
        ('', False),
        ('1abc', False),
        ('$x', True),
        ('_x', True),
        ('\u00e5', True),
        ('a-b', False),
    ],
)
def test_is_identifier(key, expected):
    assert JSON5Encoder().is_identifier(key) == expected


@pytest.mark.parametrize(
    'key,expected',
    [
        ('new', True),
        ('newbie', False),
        ('true', True),
        ('while', True),
        ('foo', False),
        ('class', True),
    ],
)
def test_is_reserved_word(key, expected):
    assert JSON5Encoder().is_reserved_word(key) == expected


def test_identifier_that_is_also_reserved_gets_quoted_on_dump():
    encoder = JSON5Encoder()
    assert encoder.is_identifier('new') is True
    assert encoder.is_reserved_word('new') is True
    assert json5.dumps({'new': 1}) == '{"new": 1}'
    assert json5.dumps({'newbie': 1}) == '{newbie: 1}'


@pytest.mark.parametrize(
    'value,expected',
    [
        ('foo', 'foo'),
        ('new', '"new"'),
        ('foo bar', '"foo bar"'),
        (42, '"42"'),
    ],
)
def test_encode_as_key(value, expected):
    assert JSON5Encoder().encode(value, set(), 0, as_key=True) == expected


# ---------------------------------------------------------------- quote styles

def test_quote_style_does_not_change_how_keys_are_quoted():
    assert json5.dumps({'a"b': 1}, quote_style=QuoteStyle.ALWAYS_SINGLE) == (
        "{'a\\"b': 1}"
    )


def test_prefer_styles_keep_the_tie_on_the_preferred_side():
    # Equal numbers of single and double quotes: no re-encode happens.
    assert json5.dumps("a'b\\"c", quote_style=QuoteStyle.PREFER_DOUBLE) == (
        '"a\\'b\\\\"c"'
    )
    assert json5.dumps("a'b\\"c", quote_style=QuoteStyle.PREFER_SINGLE) == (
        "'a\\\\'b\\"c'"
    )


# ------------------------------------------------------------------ round-trips

@pytest.mark.parametrize(
    'value',
    [
        {'a': [1, 2.5, 'x', True, None]},
        ['a', "b'c", 'd"e'],
        {'caf\u00e9': '\U0001f600'},
        {'a': {'b': {'c': [1]}}},
    ],
)
@pytest.mark.parametrize(
    'kwargs',
    [
        {},
        {'quote_keys': True, 'trailing_commas': False},
        {'indent': 2},
        {'quote_style': QuoteStyle.ALWAYS_SINGLE},
    ],
)
def test_round_trip_through_dumps_options(value, kwargs):
    assert json5.loads(json5.dumps(value, **kwargs)) == value


def test_json_compatible_options_match_stdlib_json():
    value = {'foo': 1}
    assert json5.dumps(value, quote_keys=True, trailing_commas=False) == (
        stdlib_json.dumps(value)
    )
    assert json5.dumps(
        {'foo': 'bar', 'n': [1, 2]}, quote_keys=True, trailing_commas=False
    ) == '{"foo": "bar", "n": [1, 2]}'
