"""loads()/parse() coverage for JSON5 features the upstream unittest
suite does not exercise directly.

Upstream tests/lib_test.py covers the core grammar heavily (numbers,
strings, identifiers, hooks, strict newlines, sample file). The cases
below were chosen by grepping that file first and keeping only gaps:
comments (never asserted there), trailing commas on the loads side,
number spellings, reserved-word-like keys, unknown escapes, strict
handling of tab vs CR, bytes/encoding paths, hook argument details,
and parse() position/error reporting.

Every assertion below was confirmed against the cloned source with a
probe script before being written here; nothing is guessed from the
JSON5 spec or the docs.
"""

import io
import math

import pytest

import json5


# ---------------------------------------------------------------- comments

def test_line_comment_before_value():
    assert json5.loads('// hi\n42') == 42


def test_line_comment_after_value_without_newline():
    assert json5.loads('42 // trailing') == 42


def test_line_comments_inside_object():
    assert json5.loads('{\n// leading\nfoo: 1, // trailing\nbar: 2\n}') == {
        'foo': 1,
        'bar': 2,
    }


def test_block_comment_between_array_elements():
    assert json5.loads('[1, /* y */ 2]') == [1, 2]


def test_block_comment_spanning_lines():
    assert json5.loads('{\n/* a\nb */\nfoo: 1}') == {'foo': 1}


def test_comment_markers_inside_strings_are_not_comments():
    assert json5.loads('{"a": "//not a comment"}') == {'a': '//not a comment'}
    assert json5.loads('{"a": "/* not a comment */"}') == {
        'a': '/* not a comment */'
    }


def test_comment_only_document_fails():
    with pytest.raises(ValueError, match='Unexpected end of input'):
        json5.loads('// only')


def test_unterminated_block_comment_fails():
    with pytest.raises(ValueError, match='Unexpected end of input'):
        json5.loads('/* oops 42')


def test_comment_wrapped_config_document():
    # A realistic config-file shape: comments + hex + trailing commas.
    doc = (
        "{// cfg\n"
        " host: 'x', // c\n"
        " port: 0x50, /* multi\nline */ tags: ['a',],}"
    )
    assert json5.loads(doc) == {'host': 'x', 'port': 80, 'tags': ['a']}


# ----------------------------------------------------------- trailing commas

def test_object_trailing_comma_loads():
    assert json5.loads('{a: 1,}') == {'a': 1}


def test_array_trailing_comma_loads():
    assert json5.loads('[1, 2,]') == [1, 2]


def test_nested_trailing_commas_load():
    assert json5.loads('{a: [1,], b: {c: 2,},}') == {'a': [1], 'b': {'c': 2}}


def test_double_comma_still_fails():
    with pytest.raises(ValueError, match='Unexpected ","'):
        json5.loads('[1,,]')


def test_trailing_comma_in_empty_object_fails():
    with pytest.raises(ValueError, match='Unexpected "}"'):
        json5.loads('{,}')


def test_trailing_comma_in_empty_array_fails():
    with pytest.raises(ValueError, match='Unexpected ","'):
        json5.loads('[,]')


# ------------------------------------------------------------------ numbers

@pytest.mark.parametrize('text,expected', [('.5', 0.5), ('5.', 5.0), ('1.e3', 1000.0)])
def test_leading_and_trailing_dot_numbers(text, expected):
    assert json5.loads(text) == expected


@pytest.mark.parametrize(
    'text,expected',
    [('0x0', 0), ('0Xff', 255), ('0xABCDEF', 11259375), ('+0x10', 16), ('-0X10', -16)],
)
def test_hex_spellings(text, expected):
    assert json5.loads(text) == expected


@pytest.mark.parametrize(
    'text', ['01', '00', '0b101', '0o17', '1_000', '0x', '1e+']
)
def test_non_json5_number_spellings_rejected(text):
    with pytest.raises(ValueError):
        json5.loads(text)


def test_negative_zero_float_keeps_its_sign():
    value = json5.loads('-0.0')
    assert value == 0.0
    assert math.copysign(1, value) == -1.0


def test_plus_nan_is_accepted():
    assert math.isnan(json5.loads('+NaN'))


@pytest.mark.parametrize('text', ['infinity', '-infinity', 'nan'])
def test_lowercase_constant_names_rejected(text):
    with pytest.raises(ValueError):
        json5.loads(text)


# --------------------------------------------------------------------- keys

def test_reserved_word_like_keys_parse_as_strings():
    # Parsing accepts unquoted true/null as keys even though dumps()
    # quotes them back (see test_dumps_encoder.py).
    assert json5.loads('{true: 1}') == {'true': 1}
    assert json5.loads('{null: 1}') == {'null': 1}


def test_single_quoted_keys():
    assert json5.loads("{'foo': 1}") == {'foo': 1}


def test_digit_leading_key_fails():
    with pytest.raises(ValueError):
        json5.loads('{9lives: 1}')


def test_hyphenated_key_fails():
    with pytest.raises(ValueError):
        json5.loads('{foo-bar: 1}')


# ------------------------------------------------------------ string escapes

def test_unknown_escapes_drop_the_backslash():
    assert json5.loads(r'"\a"') == 'a'
    assert json5.loads(r'"\z"') == 'z'


def test_nul_escape_followed_by_digit():
    assert json5.loads(r'"\0a"') == '\x00a'


def test_line_continuation_with_crlf_and_cr():
    assert json5.loads('"foo\\\r\nbar"') == 'foobar'
    assert json5.loads('"foo\\\rbar"') == 'foobar'


def test_line_continuation_keeps_following_text():
    assert json5.loads("'a\\\n b'") == 'a b'


def test_hex_and_unicode_escapes():
    assert json5.loads(r'"\x41"') == 'A'
    assert json5.loads(r'"\u0041"') == 'A'


# ------------------------------------------------------------------- strict

def test_raw_tab_inside_string_passes_even_when_strict():
    # Measured behaviour: strict mode rejects raw CR/LF but not raw tab.
    assert json5.loads('"a\tb"', strict=True) == 'a\tb'


def test_raw_cr_fails_when_strict_and_passes_when_not():
    with pytest.raises(ValueError, match='Unexpected'):
        json5.loads('"a\rb"', strict=True)
    assert json5.loads('"a\rb"', strict=False) == 'a\rb'


def test_raw_lf_inside_scalar_string_fails_when_strict():
    with pytest.raises(ValueError):
        json5.loads('"a\nb"', strict=True)
    assert json5.loads('"a\nb"', strict=False) == 'a\nb'


# ----------------------------------------------------------- bytes / encoding

def test_loads_bytes_as_utf8_by_default():
    assert json5.loads(b'{"a": 1}') == {'a': 1}


def test_loads_bad_utf8_bytes_raise_unicode_decode_error():
    with pytest.raises(UnicodeDecodeError):
        json5.loads(b'\xff')


def test_loads_bytes_with_explicit_encoding():
    assert json5.loads(b'"\xe9"', encoding='latin-1') == 'é'


def test_load_from_bytes_stream():
    assert json5.load(io.BytesIO(b'{a: 1}')) == {'a': 1}


# ---------------------------------------------------------- parse() / hooks

def test_parse_empty_string_raises_instead_of_returning_error():
    with pytest.raises(ValueError, match='Empty strings are not legal JSON5'):
        json5.parse('')


def test_parse_bytes_input():
    assert json5.parse(b'42') == (42, None, 2)


def test_parse_steps_through_multiple_values():
    value, err, pos = json5.parse('1 2', consume_trailing=False)
    assert (value, err, pos) == (1, None, 1)
    assert json5.parse('1 2', consume_trailing=False, start=pos) == (2, None, 3)


def test_parse_position_includes_trailing_whitespace():
    assert json5.parse('42  ') == (42, None, 4)


def test_parse_error_reports_second_line():
    _, err, _ = json5.parse('{\na: }')
    assert err == '<string>:2 Unexpected "}" at column 4'


def test_parse_int_hook_receives_base_16_for_hex():
    seen = []

    def hook(value, base=10):
        seen.append((value, base))
        return int(value, base)

    assert json5.loads('0x10', parse_int=hook) == 16
    assert seen == [('0x10', 16)]


def test_parse_float_hook_receives_the_raw_exponent_spelling():
    seen = []
    assert json5.loads('1.5e3', parse_float=lambda s: seen.append(s) or 0.0) == 0.0
    assert seen == ['1.5e3']


def test_parse_constant_hook_sees_signed_spellings():
    assert json5.loads('+Infinity', parse_constant=lambda s: 'C:' + s) == 'C:Infinity'
    assert json5.loads('-NaN', parse_constant=lambda s: 'C:' + s) == 'C:-NaN'


def test_object_pairs_hook_applies_to_nested_objects():
    assert json5.loads(
        '{a: 1, b: {c: 2}}', object_pairs_hook=lambda pairs: list(pairs)
    ) == [('a', 1), ('b', [('c', 2)])]


def test_object_hook_applies_bottom_up():
    assert json5.loads('{a: {b: 1}}', object_hook=lambda d: ('hooked', d)) == (
        'hooked',
        {'a': ('hooked', {'b': 1})},
    )


def test_duplicate_keys_rejected_in_nested_objects():
    with pytest.raises(ValueError, match='Duplicate key "b"'):
        json5.loads('{a: {b: 1, b: 2}}', allow_duplicate_keys=False)


def test_custom_decoder_cls_is_rejected_not_ignored():
    # The loads()/parse() docstrings say cls is ignored, but parse()
    # actually asserts it is None; pin the real behaviour.
    with pytest.raises(AssertionError, match='Custom decoders are not supported'):
        json5.loads('42', cls=object)
    with pytest.raises(AssertionError, match='Custom decoders are not supported'):
        json5.parse('42', cls=object)
    with pytest.raises(AssertionError, match='Custom decoders are not supported'):
        json5.load(io.StringIO('42'), cls=object)
