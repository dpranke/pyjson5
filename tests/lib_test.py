# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import builtins
import decimal
import io
import json
import math
import os
import unittest
from collections import OrderedDict, namedtuple
from types import MappingProxyType

import json5


class RecordingHook(list):
    def __init__(self, transform=None):
        super().__init__()
        self.transform = transform

    def __call__(self, value):
        self.append(value)
        return self.transform(value) if self.transform is not None else value


class NoTruthHook(RecordingHook):
    def __bool__(self):
        raise AssertionError(
            'Callbacks must not be truth-tested'
        )  # pragma: no cover


class TestOptionalHooks(unittest.TestCase):
    def test_decoding_hooks(self):
        cases = (
            ('object_hook', '{"a": 1}'),
            ('object_pairs_hook', '{"a": 1}'),
            ('parse_int', '42'),
            ('parse_float', '1.5'),
            ('parse_constant', 'NaN'),
        )
        for name, text in cases:
            for hook_type in (RecordingHook, NoTruthHook):
                for method in ('load', 'loads', 'parse'):
                    with self.subTest(
                        name=name, hook=hook_type, method=method
                    ):
                        hook = hook_type()
                        expected = json.loads(
                            text, **{name: lambda value: value}
                        )
                        if method == 'load':
                            actual = json5.load(
                                io.StringIO(text), **{name: hook}
                            )
                        elif method == 'loads':
                            actual = json5.loads(text, **{name: hook})
                        else:
                            actual, error, position = json5.parse(
                                text, **{name: hook}
                            )
                            self.assertIsNone(error)
                            self.assertEqual(position, len(text))
                        self.assertEqual(actual, expected)
                        self.assertEqual(len(hook), 1)

    def test_object_pairs_hook_precedence(self):
        pairs = RecordingHook()
        objects = RecordingHook()
        self.assertEqual(
            json5.loads(
                '{a: 1}', object_pairs_hook=pairs, object_hook=objects
            ),
            [('a', 1)],
        )
        self.assertEqual(pairs, [[('a', 1)]])
        self.assertEqual(objects, [])

    def test_default_hook(self):
        for hook_type in (RecordingHook, NoTruthHook):
            for method in ('dump', 'dumps'):
                with self.subTest(hook=hook_type, method=method):
                    hook = hook_type(lambda _obj: 'custom')
                    value = object()
                    if method == 'dump':
                        output = io.StringIO()
                        json5.dump(value, output, default=hook)
                        actual = output.getvalue()
                    else:
                        actual = json5.dumps(value, default=hook)
                    self.assertEqual(actual, '"custom"')
                    self.assertEqual(hook, [value])


class TestLoads(unittest.TestCase):
    maxDiff = None

    def check(self, s, obj, strict=True):
        self.assertEqual(obj, json5.loads(s, strict=strict))

    def check_fail(self, s, err=None):
        try:
            json5.loads(s)
            self.fail()  # pragma: no cover
        except ValueError as e:
            if err is not None:
                self.assertEqual(err, str(e))

    def test_arrays(self):
        self.check('[]', [])
        self.check('[0]', [0])
        self.check('[0,1]', [0, 1])
        self.check('[ 0 , 1 ]', [0, 1])

        try:
            json5.loads('[ ,]')
            self.fail()  # pragma: no cover
        except ValueError as e:
            self.assertIn('Unexpected "," at column 3', str(e))

    def test_bools(self):
        self.check('true', True)
        self.check('false', False)

    def test_duplicate_keys_should_be_allowed(self):
        self.assertEqual(
            json5.loads('{foo: 1, foo: 2}', allow_duplicate_keys=True),
            {'foo': 2},
        )

    def test_duplicate_keys_should_be_allowed_by_default(self):
        self.check('{foo: 1, foo: 2}', {'foo': 2})

    def test_duplicate_keys_should_not_be_allowed(self):
        self.assertRaises(
            ValueError,
            json5.loads,
            '{foo: 1, foo: 2}',
            allow_duplicate_keys=False,
        )

        # Also check to make sure we don't reject things incorrectly.
        self.assertEqual(
            json5.loads('{foo: 1, bar: 2}', allow_duplicate_keys=False),
            {'foo': 1, 'bar': 2},
        )

    def test_empty_strings_are_errors(self):
        self.check_fail('', 'Empty strings are not legal JSON5')

    def test_partial_strings_are_errors(self):
        self.check_fail("'", '<string>:1 Unexpected end of input at column 2')

    def test_encoding(self):
        self.assertEqual(json5.loads(b'"\xf6"', encoding='iso-8859-1'), '\xf6')
        with self.assertRaises(UnicodeDecodeError):
            json5.load(io.BytesIO(b'\xff'))

    def test_numbers(self):
        # decimal literals
        self.check('1', 1)
        self.check('-1', -1)
        self.check('+1', 1)
        self.check_fail('--6', '<string>:1 Unexpected "-" at column 2')
        self.check_fail('++6', '<string>:1 Unexpected "+" at column 2')
        self.check_fail('+-6', '<string>:1 Unexpected "-" at column 2')

        # hex literals
        self.check('0xf', 15)
        self.check('0xfe', 254)
        self.check('0xfff', 4095)
        self.check('0XABCD', 43981)
        self.check('0x123456', 1193046)
        self.check_fail('0x+', '<string>:1 Unexpected "+" at column 3')

        # signed hex literals
        self.check('+0xf', 15)
        self.check('-0xf', -15)
        self.check('-0XABCD', -43981)
        self.check('-0x0', 0)

        # floats
        self.check('1.5', 1.5)
        self.check('1.5e3', 1500.0)
        self.check('-0.5e-2', -0.005)
        self.check_fail('--6.0', '<string>:1 Unexpected "-" at column 2')
        self.check_fail('++6.0', '<string>:1 Unexpected "+" at column 2')
        self.check_fail('+-6.0', '<string>:1 Unexpected "-" at column 2')

        # names
        self.check('Infinity', float('inf'))
        self.check('+Infinity', float('inf'))
        self.check('-Infinity', float('-inf'))
        self.assertTrue(math.isnan(json5.loads('NaN')))
        self.assertTrue(math.isnan(json5.loads('-NaN')))

        # syntax errors
        self.check_fail('14d', '<string>:1 Unexpected "d" at column 3')
        self.check_fail('.', '<string>:1 Unexpected end of input at column 2')
        self.check_fail('.e5', '<string>:1 Unexpected "e" at column 2')
        self.check_fail('1e', '<string>:1 Unexpected end of input at column 3')
        self.check_fail(
            '1e+', '<string>:1 Unexpected end of input at column 4'
        )
        self.check_fail('[1e]', '<string>:1 Unexpected "]" at column 4')

        # malformed numbers are rejected by the parser, not by parse_float
        self.assertEqual(
            json5.parse('1e', parse_float=decimal.Decimal),
            (None, '<string>:1 Unexpected end of input at column 3', 2),
        )

    def test_identifiers(self):
        self.check('{a: 1}', {'a': 1})
        self.check('{$: 1}', {'$': 1})
        self.check('{_: 1}', {'_': 1})
        self.check('{a_b: 1}', {'a_b': 1})
        self.check('{a$: 1}', {'a$': 1})

        # This valid JavaScript but not valid JSON5; keys must be identifiers
        # or strings.
        self.check_fail('{1: 1}')

    def test_identifiers_unicode(self):
        # It would be silly to try and test all of the possible unicode
        # characters for correctness, but we can at least check each
        # legal Unicode category.

        # Latin Capital letter A with Tilde, category Lu (uppercase letter)
        self.check('{\xc3: 1}', {'\xc3': 1})

        # Latin small A with Ring above, category Ll (lowercase letter)
        self.check('{\u00e5: 1}', {'\u00e5': 1})

        # Modifier Letter small H, category Lm (modifier letter)
        self.check('{\u02b0: 1}', {'\u02b0': 1})

        # Latin Letter Two with Stroke, category Lo (other letter)
        self.check('{\u01bb: 1}', {'\u01bb': 1})

        # Latin Capital Letter L with Small Letter J
        # (category Lt, titlecase letter)
        self.check('{\u01c8: 1}', {'\u01c8': 1})

        # Roman Numeral One (category Nl, letter number)
        self.check('{\u2160: 1}', {'\u2160': 1})

        # Combining Diaresis (category Mn, non-spacing mark)
        self.check('{a\u0308o: 1}', {'a\u0308o': 1})

        # Rejang Virama (category Mc, spacing mark)
        self.check('{a\ua953o: 1}', {'a\ua953o': 1})

        # Arabic-Indic Digit Zero (category Nd, decimal number)
        self.check('{a\u0660: 1}', {'a\u0660': 1})

        # Undertie (category Pc, connector punctuation)
        self.check('{a\u203fb: 1}', {'a\u203fb': 1})

    def test_identifiers_escapes(self):
        self.check('{\\u0061: 1}', {'a': 1})
        self.check('{\\u0024\\u005f: 1}', {'$_': 1})
        self.check(
            '{\\u00c3\\u02b0\\u01bb\\u01c8\\u2160: 1}',
            {'\xc3\u02b0\u01bb\u01c8\u2160': 1},
        )
        self.check(
            '{a\\u0030\\u0308\\ua953\\u203f: 1}', {'a0\u0308\ua953\u203f': 1}
        )
        self.check('{a\\u200c\\u200D: 1}', {'a\u200c\u200d': 1})
        self.check('{\\ud835\\udc00: 1}', {'\U0001d400': 1})

        # An escape can't be used to put a character into an identifier
        # that wouldn't otherwise be legal there.
        self.check_fail('{\\u0031: 1}')
        self.check_fail('{\\u0022: 1}')
        self.check_fail('{a\\u0020b: 1}')
        self.check_fail('{a\\u003a: 1}')
        self.check_fail('{a\\u0000: 1}')

    def test_null(self):
        self.check('null', None)

    def test_object_hook(self):
        def hook(d):
            return [d]

        self.assertEqual(
            json5.loads('{foo: 1}', object_hook=hook), [{'foo': 1}]
        )

    def test_object_pairs_hook(self):
        def hook(pairs):
            return pairs

        self.assertEqual(
            json5.loads('{foo: 1, bar: 2}', object_pairs_hook=hook),
            [('foo', 1), ('bar', 2)],
        )

    def test_objects(self):
        self.check('{}', {})
        self.check('{"foo": 0}', {'foo': 0})
        self.check('{"foo":0,"bar":1}', {'foo': 0, 'bar': 1})
        self.check('{ "foo" : 0 , "bar" : 1 }', {'foo': 0, 'bar': 1})

    def test_parse_constant(self):
        def hook(x):
            return x

        self.assertEqual(
            json5.loads('-Infinity', parse_constant=hook), '-Infinity'
        )
        self.assertEqual(json5.loads('NaN', parse_constant=hook), 'NaN')

    def test_parse_float(self):
        def hook(x):
            return x

        self.assertEqual(json5.loads('1.0', parse_float=hook), '1.0')
        for text in ('1E5', '1E+5', '2.5E-3', '1e5', '1e-5'):
            with self.subTest(text=text):
                self.assertEqual(json5.loads(text, parse_float=hook), text)

    def test_parse_int(self):
        def hook(x):
            return x

        self.assertEqual(json5.loads('1', parse_int=hook), '1')
        self.assertEqual(json5.loads('0x10', parse_int=hook), '0x10')
        self.assertEqual(json5.loads('-0xff', parse_int=hook), '-0xff')
        self.assertEqual(json5.loads('0x10'), 16)
        self.assertEqual(json5.loads('-0xff'), -255)
        self.assertEqual(json5.loads('0X2a'), 42)

    def test_sample_file(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'sample.json5')
        with open(path, encoding='utf-8') as fp:
            obj = json5.load(fp)
        self.assertEqual(
            {
                'oh': [
                    "we shouldn't forget",
                    'arrays can have',
                    'trailing commas too',
                ],
                'this': 'is a multi-line string',
                'delta': 10,
                'hex': 3735928559,
                'finally': 'a trailing comma',
                'here': 'is another',
                'to': float('inf'),
                'while': True,
                'half': 0.5,
                'foo': 'bar',
            },
            obj,
        )

    def test_load_fails(self):
        s = io.StringIO('x')
        with self.assertRaises(ValueError):
            json5.load(s)

    def test_load_start_is_absolute(self):
        for stream_type in (io.StringIO, io.BytesIO):
            for prefix in ('', 'ignored\n', '\u00e9\u4e2d\n'):
                text = prefix + '{answer: 42}'
                data = (
                    text.encode('utf-8') if stream_type is io.BytesIO else text
                )
                for position in (0, 1, len(data)):
                    with self.subTest(
                        stream=stream_type, prefix=prefix, position=position
                    ):
                        fp = stream_type(data)
                        fp.seek(position)
                        self.assertEqual(
                            {'answer': 42}, json5.load(fp, start=len(prefix))
                        )

    def test_load_without_start_uses_current_position(self):
        for stream_type in (io.StringIO, io.BytesIO):
            text = 'ignored\n{answer: 42}'
            data = text.encode('utf-8') if stream_type is io.BytesIO else text
            fp = stream_type(data)
            fp.read(len('ignored\n'))
            self.assertEqual({'answer': 42}, json5.load(fp))

    def test_load_start_does_not_change_numbers(self):
        for text, position, start in (('123', 1, 0), ('x 123', 2, 2)):
            with self.subTest(text=text, position=position, start=start):
                fp = io.StringIO(text)
                fp.seek(position)
                self.assertEqual(123, json5.load(fp, start=start))

    def test_load_without_start_does_not_seek(self):
        class NonSeekable(io.StringIO):
            def seek(self, offset, whence=0):
                del offset, whence
                raise io.UnsupportedOperation('not seekable')

        self.assertEqual(
            {'answer': 42}, json5.load(NonSeekable('{answer: 42}'))
        )
        with self.assertRaises(io.UnsupportedOperation):
            json5.load(NonSeekable('{answer: 42}'), start=0)

    def test_strict(self):
        # From [GitHub issue #82](https://github.com/dpranke/pyjson5/issues/82)
        d = '{\n"key": "value\nover two lines",\n}'
        self.check_fail(d, '<string>:2 Unexpected "\n" at column 14')
        self.check(d, {'key': 'value\nover two lines'}, strict=False)

        # Test w/ single quotes to get coverage.
        d = "{\n'key': 'value\nover two lines',\n}"
        self.check_fail(d, '<string>:2 Unexpected "\n" at column 14')
        self.check(d, {'key': 'value\nover two lines'}, strict=False)

    def test_strings(self):
        self.check('"foo"', 'foo')
        self.check("'foo'", 'foo')

        # escape chars
        self.check("'\\b\\t\\f\\n\\r\\v\\\\'", '\b\t\f\n\r\v\\')
        self.check("'\\''", "'")
        self.check('"\\""', '"')

        # hex literals
        self.check('"\\x66oo"', 'foo')

        # unicode literals
        self.check('"\\u0066oo"', 'foo')

        # surrogate pairs decode to the astral code point they represent,
        # matching the json module.
        self.check('"\\ud800\\udc00"', chr(0x10000))
        self.check('"\\ud83d\\ude00"', '\U0001f600')
        self.check('{"\\ud83d\\ude00": 1}', {'\U0001f600': 1})
        # a lone surrogate is left as-is.
        self.check('"\\ud800"', '\ud800')

        # string literals w/ continuation markers at the end of the line.
        # These should not have spaces is the result.
        self.check('"foo\\\nbar"', 'foobar')
        self.check("'foo\\\nbar'", 'foobar')

        # U+2028 and U+2029 are allowed unescaped, as in JSON.
        self.check('"foo\u2028bar\u2029"', 'foo\u2028bar\u2029')
        self.check("'foo\u2028bar\u2029'", 'foo\u2028bar\u2029')
        self.check('"foo\\\u2028bar"', 'foobar')

        # unterminated string literals.
        self.check_fail('"\n')
        self.check_fail("'\n")
        self.check_fail('"\r"')

        # bad hex literals
        self.check_fail("'\\x0'")
        self.check_fail("'\\xj'")
        self.check_fail("'\\x0j'")

        # bad unicode literals
        self.check_fail("'\\u0'")
        self.check_fail("'\\u00'")
        self.check_fail("'\\u000'")
        self.check_fail("'\\u000j'")
        self.check_fail("'\\u00j0'")
        self.check_fail("'\\u0j00'")
        self.check_fail("'\\uj000'")

    def test_unrecognized_escape_char(self):
        self.check(r'"\/"', '/')

    def test_nul(self):
        self.check(r'"\0"', '\x00')

    def test_whitespace(self):
        # Whitespace should be allowed before and after a value.
        self.check('\n1', 1)
        self.check('\r1', 1)
        self.check('\r\n1', 1)
        self.check('\t1', 1)
        self.check('\v1', 1)
        self.check('\ufeff 1', 1)
        self.check('\u00a0 1', 1)
        self.check('\u2028 1', 1)  # line separator
        self.check('\u2029 1', 1)  # paragraph separator
        self.check('\u2000 1', 1)  # En quad, unicode category Zs

        self.check('1\n', 1)

    def test_error_reporting(self):
        self.check_fail('[ ,]', err='<string>:1 Unexpected "," at column 3')

        self.check_fail(
            '{\n'
            '    version: "1.0",\n'
            '    author: "John Smith",\n'
            '    people : [\n'
            '        "Monty",\n'
            '        "Python"foo\n'
            '    ]\n'
            '}\n',
            err='<string>:6 Unexpected "f" at column 17',
        )

    def test_no_extra_characters_in_value(self):
        self.check_fail('0 1', '<string>:1 Unexpected "1" at column 3')
        self.check_fail('0 a', '<string>:1 Unexpected "a" at column 3')


class TestParse(unittest.TestCase):
    maxDiff = None

    def check(self, s, obj, err, pos, consume_trailing=True, start=0):
        actual_obj, actual_err, actual_pos = json5.parse(
            s, consume_trailing=consume_trailing, start=start
        )
        self.assertEqual(obj, actual_obj)
        self.assertEqual(err, actual_err)
        self.assertEqual(pos, actual_pos)

    def test_parse_empty_input(self):
        for source in ('', b''):
            with self.subTest(source=source):
                self.assertEqual(
                    json5.parse(source),
                    (None, 'Empty strings are not legal JSON5', 0),
                )

    def test_parse(self):
        self.check('4', 4, err=None, pos=1)
        self.check('4 ', 4, err=None, pos=2)
        self.check('4 ', 4, err=None, pos=1, consume_trailing=False)
        self.check(
            'x', None, err='<string>:1 Unexpected "x" at column 1', pos=0
        )
        self.check(
            '4 x', None, err='<string>:1 Unexpected "x" at column 3', pos=2
        )
        self.check('4 x', 4, err=None, pos=1, consume_trailing=False)
        self.check('x 4', 4, err=None, pos=3, start=1)
        self.check(
            'x y',
            None,
            err='<string>:1 Unexpected "y" at column 3',
            pos=2,
            start=1,
        )

        val, err, pos = json5.parse('[][]', consume_trailing=False)
        self.assertEqual(val, [])
        self.assertEqual(err, None)
        self.assertEqual(pos, 2)
        val, err, pos = json5.parse('[][]', consume_trailing=False, start=pos)
        self.assertEqual(val, [])
        self.assertEqual(err, None)
        self.assertEqual(pos, 4)


class TestDump(unittest.TestCase):
    def test_basic(self):
        sio = io.StringIO()
        json5.dump(True, sio)
        self.assertEqual('true', sio.getvalue())

    def test_use_duck_typing(self):
        output = io.StringIO()
        json5.dump(bytearray(b'hi'), output, use_duck_typing=True)
        self.assertEqual('[104, 105]', output.getvalue())


class TestDumps(unittest.TestCase):
    maxDiff = None

    def check(self, obj, s, **kwargs):
        self.assertEqual(s, json5.dumps(obj, **kwargs))

    def test_skipkeys_with_indent_and_no_valid_keys(self):
        obj = {(): 1}
        for indent in (0, 2, '\t'):
            for trailing_commas in (True, False):
                with self.subTest(
                    indent=indent, trailing_commas=trailing_commas
                ):
                    kwargs = {
                        'skipkeys': True,
                        'indent': indent,
                        'trailing_commas': trailing_commas,
                    }
                    self.assertEqual(json5.dumps(obj, **kwargs), '{}')
                    self.assertEqual(
                        json5.loads(json5.dumps([obj], **kwargs)), [{}]
                    )

    def test_allow_duplicate_keys(self):
        self.assertIn(
            json5.dumps({1: 'foo', '1': 'bar'}),
            {'{"1": "foo", "1": "bar"}', '{"1": "bar", "1": "foo"}'},
        )

        self.assertRaises(
            ValueError,
            json5.dumps,
            {1: 'foo', '1': 'bar'},
            allow_duplicate_keys=False,
        )

    def test_allow_duplicate_keys_differently_encoded(self):
        # These keys encode differently but decode to the same string.
        for obj, kwargs in (
            ({float('inf'): 'foo', 'Infinity': 'bar'}, {}),
            ({float('nan'): 'foo', 'NaN': 'bar'}, {}),
            (
                {1: 'foo', '1': 'bar'},
                {'quote_style': json5.QuoteStyle.ALWAYS_SINGLE},
            ),
            (
                {True: 'foo', 'true': 'bar'},
                {'quote_style': json5.QuoteStyle.PREFER_SINGLE},
            ),
            (
                {None: 'foo', 'null': 'bar'},
                {'quote_style': json5.QuoteStyle.ALWAYS_SINGLE},
            ),
        ):
            with self.subTest(obj=obj, kwargs=kwargs):
                self.assertRaises(
                    ValueError,
                    json5.dumps,
                    obj,
                    allow_duplicate_keys=False,
                    **kwargs,
                )

    def test_arrays(self):
        self.check([], '[]')
        self.check([1, 2, 3], '[1, 2, 3]')
        self.check(
            [{'foo': 'bar'}, {'baz': 'quux'}], '[{foo: "bar"}, {baz: "quux"}]'
        )

    def test_bools(self):
        self.check(True, 'true')
        self.check(False, 'false')

    def test_check_circular(self):
        # This tests that a non-cyclic object works w/ either flag value.
        obj = [1, 2, 3]
        self.check(obj, '[1, 2, 3]')  # testing the default
        self.check(obj, '[1, 2, 3]', check_circular=True)
        self.check(obj, '[1, 2, 3]', check_circular=False)

        # This tests a trivial cycle.
        obj = [1, 2, 3]
        obj[2] = obj
        self.assertRaises(ValueError, json5.dumps, obj)

        # This checks that json5 doesn't raise an error with
        # check_circular=false and a cycle. However,
        # the underlying Python implementation likely will.
        try:
            json5.dumps(obj, check_circular=False)
            self.fail()  # pragma: no cover
        except RecursionError:
            pass

        # This checks that repeated but non-circular references
        # are okay.
        x = [1, 2]
        y = {'foo': x, 'bar': x}
        self.check(y, '{foo: [1, 2], bar: [1, 2]}')

        # This tests a more complicated cycle.
        x = {}
        y = {}
        z = {}
        z['x'] = x
        z['y'] = y
        z['x']['y'] = y
        z['y']['x'] = x
        self.assertRaises(ValueError, json5.dumps, z)

    def test_custom_arrays(self):
        # With duck typing, a sequence-like object can be dumped by either
        # iterating over it using __iter__, or manually iterating
        # over it using __len__ and __getitem__. As long as one or
        # the other is implemented, this test will pass. The implementation
        # is perhaps more lenient than it should be, as we don't ensure
        # that all three methods are implemented correctly.
        class MyArray:
            def __iter__(self):
                yield 0
                yield 1
                yield 1

            def __getitem__(self, i):
                return 0 if i == 0 else 1  # pragma: no cover

            def __len__(self):
                return 3  # pragma: no cover

        value = MyArray()
        self.assertRaises(TypeError, json5.dumps, value)
        self.assertEqual(json5.dumps(value, default=list), '[0, 1, 1]')
        self.assertEqual(json5.dumps(value, use_duck_typing=True), '[0, 1, 1]')

        class GetItemOnly:
            def __getitem__(self, index):
                return (0, 1)[index]  # pragma: no cover

        self.assertRaises(
            TypeError,
            json5.dumps,
            GetItemOnly(),
            use_duck_typing=True,
        )

    def test_custom_arrays_without_truth_value(self):
        class Array:
            def __init__(self, values):
                self.values = values

            def __iter__(self):
                return iter(self.values)

            def __getitem__(self, index):
                return self.values[index]  # pragma: no cover

            def __bool__(self):  # pragma: no cover
                raise ValueError('The truth value of an array is ambiguous')

        for values in ([], [0.0], [1.0, 2.0]):
            for indent in (None, 0, 2, ''):
                for trailing_commas in (True, False):
                    with self.subTest(
                        values=values,
                        indent=indent,
                        trailing_commas=trailing_commas,
                    ):
                        result = json5.dumps(
                            Array(values),
                            use_duck_typing=True,
                            indent=indent,
                            trailing_commas=trailing_commas,
                        )
                        self.assertEqual(json5.loads(result), values)

    def test_duck_mapping_without_truth_value(self):
        class Mapping:
            def __init__(self, values):
                self.values = values

            def keys(self):
                return iter(self.values)

            def __getitem__(self, key):
                return self.values[key]

            def __bool__(self):
                raise ValueError(
                    'The truth value is undefined'
                )  # pragma: no cover

        for values in ({}, {'b': 0, 'a': [1, 2]}):
            for indent in (None, 0, 2, '\t'):
                for trailing_commas in (False, True):
                    for sort_keys in (False, True):
                        with self.subTest(
                            values=values,
                            indent=indent,
                            trailing_commas=trailing_commas,
                            sort_keys=sort_keys,
                        ):
                            options = {
                                'indent': indent,
                                'trailing_commas': trailing_commas,
                                'sort_keys': sort_keys,
                            }
                            self.assertEqual(
                                json5.dumps(
                                    Mapping(values),
                                    use_duck_typing=True,
                                    **options,
                                ),
                                json5.dumps(values, **options),
                            )

    def test_false_valued_duck_mapping(self):
        class Mapping:
            def keys(self):
                return ['answer']

            def __getitem__(self, key):
                return {'answer': 42}[key]

            def __bool__(self):
                return False  # pragma: no cover

        self.assertEqual(
            json5.dumps(Mapping(), use_duck_typing=True), '{answer: 42}'
        )

    def test_invalid_collection(self):
        # Check that something that isn't actually an array or a dict doesn't
        # work.
        self.assertRaises(TypeError, json5.dumps, {1, 2, 3})

    def test_custom_numbers(self):
        # See https://github.com/dpranke/pyjson5/issues/57: we
        # need to ensure that we use the bare int.__repr__ and
        # float.__repr__ in order to get legal JSON values when
        # people have custom subclasses with customer __repr__ methods.
        # (This is what JSON does and we want to match it).
        # pylint: disable=no-self-argument, invalid-repr-returned
        class MyInt(int):
            def __repr__(other):  # pragma: no cover
                del other
                self.fail()

        self.assertEqual(json5.dumps(MyInt(5)), '5')

        class MyFloat(float):
            def __repr__(other):  # pragma: no cover
                del other
                self.fail()

        self.assertEqual(json5.dumps(MyFloat(0.5)), '0.5')

    def test_custom_objects(self):
        class MyDict:
            def __iter__(self):  # pragma: no cover
                yield ('a', 1)
                yield ('b', 2)

            def keys(self):
                return ['a', 'b']

            def __getitem__(self, k):
                return {'a': 1, 'b': 2}[k]

        value = MyDict()
        self.assertRaises(TypeError, json5.dumps, value)
        self.assertEqual(
            json5.dumps(
                value,
                default=lambda obj: {'a': obj['a'], 'b': obj['b']},
            ),
            '{a: 1, b: 2}',
        )
        self.assertEqual(
            json5.dumps(value, use_duck_typing=True), '{a: 1, b: 2}'
        )

    def test_concrete_collections(self):
        point_type = namedtuple('Point', ('x', 'y'))
        cases = (
            ([], '[]'),
            ([1], '[1]'),
            ((), '[]'),
            ((1,), '[1]'),
            (point_type(1, 2), '[1, 2]'),
            ({}, '{}'),
            ({'a': 1}, '{a: 1}'),
            (OrderedDict([('a', 1)]), '{a: 1}'),
        )
        for value, expected in cases:
            with self.subTest(value=value, expected=expected):
                self.assertEqual(json5.dumps(value), expected)
                self.assertEqual(
                    json5.dumps(value, use_duck_typing=True), expected
                )

        encoder = json5.JSON5Encoder(use_duck_typing=True)
        self.assertEqual(
            encoder.encode(point_type(1, 2), set(), 0, as_key=False),
            '[1, 2]',
        )

        proxy = MappingProxyType({'a': 1})
        self.assertRaises(TypeError, json5.dumps, proxy)
        self.assertEqual(json5.dumps(proxy, use_duck_typing=True), '{a: 1}')

        frozendict_type = getattr(builtins, 'frozendict', None)
        if frozendict_type is not None:  # pragma: no cover - Python 3.15+
            self.assertEqual(json5.dumps(frozendict_type({'a': 1})), '{a: 1}')

    def test_custom_encoder(self):
        class Test:
            pass

        class Encoder(json5.JSON5Encoder):
            def default(self, obj):
                assert isinstance(obj, Test)
                return {'foo': 'bar'}

        # This tests that the custom value is indented at the same level
        # that a regular object would be. This is also testing that
        # Encoder.default is only being called when we don't otherwise know
        # how to encode something.
        self.assertEqual(
            '{\n    baz: {\n        foo: "bar",\n    },\n    quux: 4,\n}',
            json5.dumps({'baz': Test(), 'quux': 4}, indent=4, cls=Encoder),
        )

    def test_custom_strings(self):
        class MyStr(str):
            pass

        self.assertEqual(json5.dumps({'foo': MyStr('bar')}), '{foo: "bar"}')

    def test_default(self):
        def _custom_serializer(obj):
            del obj
            return 'something'

        self.assertRaises(TypeError, json5.dumps, set())
        self.assertEqual(
            json5.dumps(set(), default=_custom_serializer), '"something"'
        )

        # Bytes-like objects are binary data, not arrays of numbers, even
        # though they can be indexed and iterated over.
        for value in (b'hi', bytearray(b'hi'), memoryview(b'hi')):
            with self.subTest(value=value):
                self.assertRaises(TypeError, json5.dumps, value)
                self.assertEqual(
                    json5.dumps(
                        {'a': value}, default=lambda o: bytes(o).hex()
                    ),
                    '{a: "6869"}',
                )
                was_duck_array = hasattr(value, '__getitem__') and hasattr(
                    value, '__iter__'
                )
                if was_duck_array:
                    self.assertEqual(
                        json5.dumps(value, use_duck_typing=True), '[104, 105]'
                    )
                else:  # pragma: no cover - memoryview varies by Python
                    self.assertRaises(
                        TypeError, json5.dumps, value, use_duck_typing=True
                    )

    def test_ensure_ascii(self):
        self.check('\u00fc', '"\\u00fc"')
        self.assertEqual(json5.dumps('\u00fc', ensure_ascii=False), '"\u00fc"')

    def test_ensure_ascii_del(self):
        for obj in ('\x7f', {'\x7f': 1}):
            for ensure_ascii in (False, True):
                with self.subTest(obj=obj, ensure_ascii=ensure_ascii):
                    encoded = json5.dumps(
                        obj,
                        quote_keys=True,
                        trailing_commas=False,
                        ensure_ascii=ensure_ascii,
                    )
                    self.assertEqual(
                        encoded, json.dumps(obj, ensure_ascii=ensure_ascii)
                    )
                    self.assertEqual(json5.loads(encoded), obj)

    def test_ensure_ascii_unquoted_keys(self):
        # Identifier keys are emitted unquoted, but must still honour
        # ensure_ascii; the non-ascii characters are \\u-escaped in place
        # (which the parser accepts in identifiers, so this round-trips).
        self.check({'\u00e5': 1}, '{\\u00e5: 1}')
        self.assertEqual(
            json5.dumps({'\u00e5': 1}, ensure_ascii=False), '{\u00e5: 1}'
        )
        self.assertEqual(
            json5.loads(json5.dumps({'\u00e5': 1})), {'\u00e5': 1}
        )

    def test_ensure_ascii_astral_keys(self):
        # JSON5 uses ES5.1 IdentifierName: surrogate escapes are not allowed.
        self.check({'\U0001d49c': 1}, '{"\\ud835\\udc9c": 1}')
        self.check({'a\U0001d49cb': 1}, '{"a\\ud835\\udc9cb": 1}')
        self.check({'\U00010000': 1}, '{"\\ud800\\udc00": 1}')
        self.assertEqual(
            json5.dumps({'\U0001d49c': 1}, ensure_ascii=False),
            '{\U0001d49c: 1}',
        )
        self.assertEqual(
            json5.loads(json5.dumps({'\U0001d49c': 1})), {'\U0001d49c': 1}
        )

    def test_indent(self):
        self.assertEqual(json5.dumps([1, 2, 3], indent=None), '[1, 2, 3]')
        self.assertEqual(json5.dumps([1, 2, 3], indent=-1), '[\n1,\n2,\n3,\n]')
        self.assertEqual(json5.dumps([1, 2, 3], indent=0), '[\n1,\n2,\n3,\n]')
        self.assertEqual(json5.dumps([], indent=2), '[]')
        self.assertEqual(
            json5.dumps([1, 2, 3], indent=2), '[\n  1,\n  2,\n  3,\n]'
        )
        self.assertEqual(
            json5.dumps([1, 2, 3], indent=' '), '[\n 1,\n 2,\n 3,\n]'
        )
        self.assertEqual(
            json5.dumps([1, 2, 3], indent='++'), '[\n++1,\n++2,\n++3,\n]'
        )
        self.assertEqual(
            json5.dumps([[1, 2, 3]], indent=2),
            '[\n  [\n    1,\n    2,\n    3,\n  ],\n]',
        )

        self.assertEqual(json5.dumps({}, indent=2), '{}')
        self.assertEqual(
            json5.dumps({'foo': 'bar', 'baz': 'quux'}, indent=2),
            '{\n  foo: "bar",\n  baz: "quux",\n}',
        )

    def test_numbers(self):
        self.check(15, '15')
        self.check(1.0, '1.0')
        self.check(float('inf'), 'Infinity')
        self.check(float('-inf'), '-Infinity')
        self.check(float('nan'), 'NaN')

        for v in (float('inf'), float('-inf'), float('nan')):
            with self.assertRaises(ValueError) as ctx:
                json5.dumps(v, allow_nan=False)
            self.assertIn(str(v), str(ctx.exception))

    def test_null(self):
        self.check(None, 'null')

    def test_separators(self):
        # Check that custom separators work; these separators add an
        # extra space.
        self.check(
            [{'foo': 1}, 2], '[{foo:  1},  2]', separators=(',  ', ':  ')
        )

    def test_objects(self):
        self.check({'foo': 1}, '{foo: 1}')
        self.check({'foo bar': 1}, '{"foo bar": 1}')
        self.check({'1': 1}, '{"1": 1}')

    def test_reserved_words_in_object_keys_are_quoted(self):
        self.check({'new': 1}, '{"new": 1}')

    def test_identifiers_starting_with_reserved_words(self):
        # `newbie` should not be quoted.
        self.check({'newbie': 1}, '{newbie: 1}')

    def test_non_string_keys(self):
        self.assertEqual(
            json5.dumps({False: 'a', 1: 'b', 2.0: 'c', None: 'd'}),
            '{"false": "a", "1": "b", "2.0": "c", "null": "d"}',
        )

    def test_quote_keys(self):
        self.assertEqual(
            json5.dumps({'foo': 1}, quote_keys=True), '{"foo": 1}'
        )

    def test_strings_containing_backslashes_and_quotes(self):
        # Understanding how things are escaped in test of JSON5 strings
        # can be tricky.

        # Normal Python escaping means that the following asserts are true:
        # pylint: disable=redundant-unittest-assert
        self.assertEqual('\\z', '\\z')
        self.assertEqual('\\z', r'\z')
        self.assertEqual('\\z', r'\z')

        # But, in Python, escaping quotes in a raw string is tricky, because
        # the escape is left in the output. The results of this are:

        # (1) You cannot use a raw string to match a value ending in a
        # an odd number of backslashes: the first N-1 backslashes would
        # be matched by the same number of backslashes in the raw string,
        # leaving a single backslash followed by a quote. The quote
        # would then be considered escaped, leaving the string unterminated.
        # Ending in an even number of backslashes is fine:
        self.assertEqual(len(r'\\'), 2)
        self.assertEqual(r'\\', '\\\\')

        # (2) You cannot use a raw string to represent a value that contains
        # the same kind of quote you're using to enclose the string, unless the
        # value actually contains an odd number of backslashes immediately
        # preceding the quote:
        self.assertEqual(len(r'\''), 2)
        self.assertEqual(r'\'', "\\'")
        self.assertEqual(r'\'', "\\'")
        self.assertEqual(r'\'', r'\'')

        # Now, in JSON5, if the value doesn't contain backslashes, you can
        # use normal quoting as you would in Python, but you can't use
        # raw strings, since the raw strings would require the values to
        # have backslashes in them:
        self.check("'single'", '"\'single\'"')
        self.check("'single'", '"\'single\'"')

        # In order to represent a backslash in the value you also need to
        # escape it in the JSON string: a string containing a single backslash
        # is represented by "\\". So, in order to match that single backslash
        # via non-raw strings in Python source code, you need to (3) double the
        # backslashes (for JSON5) and then double them again, for python source
        # code. I.e., you need *4* backslashes in the source code. In many
        # cases you can also use single-quoted raw strings (where you have
        # to (4) double the number of quotes in the output), but in this
        # particular example, you cannot use single-quoted raw strings,
        # due to (1).
        self.check('\\', '"\\\\"')
        self.check('\\', '"\\\\"')

        # You cannot use a double-quoted raw string to represent
        # double-quoted JSON5 strings, since the output needs to start with a
        # double quote, and you can't represent that in a raw double-quoted
        # string due to (2).

        # Here you see the doubling of backslashes in single-quoted
        # raw output strings, and the quadrupling in a non-raw string.
        self.check(r'\z', r'"\\z"')
        self.check(r'\\z', r'"\\\\z"')
        self.check(r'\\\z', r'"\\\\\\z"')
        self.check(r'\z', '"\\\\z"')

        self.check('"', '"\\""')
        self.check('"', '"\\""')

        # Here it's okay to use a raw string for output since the output
        # needs to have a single backslash and doesn't end in a single quote.
        self.check('"', r'"\""')

        # Here you cannot use raw strings for the output as the output
        # would need to have only two backslashes in it.
        self.check(r'\'', '"\\\\\'"')
        self.check(r'\'', '"\\\\\'"')

    def test_string_escape_sequences(self):
        # self.check(r'\'', '"\\\\\'"')
        self.check("'\\'", '"\'\\\\\'"')
        self.check(
            '\u2028\u2029\b\t\f\n\r\v\\\0',
            r'"\u2028\u2029\b\t\f\n\r\u000b\\\u0000"',
        )

    def test_control_char_escapes_are_valid_json(self):
        # JSON has no `\0` or `\v` escape sequences (they are JSON5-only),
        # so NUL and VT have to be written as `\u0000` and `\u000b` for
        # the json-compatible settings to produce output that the json
        # module can read back.
        for ch in ('\0', '\v'):
            for s in (ch, ch + '1', 'a' + ch + 'b'):
                with self.subTest(s=s):
                    encoded = json5.dumps(
                        s, quote_keys=True, trailing_commas=False
                    )
                    self.assertEqual(encoded, json.dumps(s))
                    self.assertEqual(json.loads(encoded), s)

    def test_null_escape_before_digits(self):
        for digit in '0123456789':
            for quote_style in json5.QuoteStyle:
                for ensure_ascii in (False, True):
                    with self.subTest(
                        digit=digit,
                        quote_style=quote_style,
                        ensure_ascii=ensure_ascii,
                    ):
                        value = '\0' + digit
                        encoded = json5.dumps(
                            value,
                            quote_style=quote_style,
                            ensure_ascii=ensure_ascii,
                        )
                        self.assertEqual(json5.loads(encoded), value)

    def test_string_quote_styles(self):
        def checkp(**kwargs):
            return lambda obj, s: self.assertEqual(
                s, json5.dumps(obj, **kwargs)
            )

        sq = "'"
        dq = '"'

        neither = 'a b c'
        single_neither = sq + neither + sq
        double_neither = dq + neither + dq

        single = "a 'b' c"
        single_single = sq + r'a \'b\' c' + sq
        double_single = dq + single + dq

        double = 'a "b" c'
        single_double = sq + double + sq
        double_double = dq + r'a \"b\" c' + dq

        both = 'a \'b\' "c" d'
        single_both = sq + r'a \'b\' "c" d' + sq
        double_both = dq + r"a 'b' \"c\" d" + dq

        reverse = 'a "b" \'c\' d'
        single_reverse = sq + r'a "b" \'c\' d' + sq
        double_reverse = dq + r"a \"b\" 'c' d" + dq

        more_single = "a 'b' 'c' \"d\" e"
        single_more_single = sq + r'a \'b\' \'c\' "d" e' + sq
        double_more_single = dq + r"a 'b' 'c' \"d\" e" + dq

        more_double = 'a "b" "c" \'d\' e'
        single_more_double = sq + r'a "b" "c" \'d\' e' + sq
        double_more_double = dq + r"a \"b\" \"c\" 'd' e" + dq

        more_single_double_first = "a \"b\" 'c' 'd' e"
        single_more_single_double_first = sq + r'a "b" \'c\' \'d\' e' + sq
        double_more_single_double_first = dq + r"a \"b\" 'c' 'd' e" + dq

        more_double_single_first = 'a \'b\' "c" "d" e'
        single_more_double_single_first = sq + r'a \'b\' "c" "d" e' + sq
        double_more_double_single_first = dq + r"a 'b' \"c\" \"d\" e" + dq

        # Default settings (should be ALWAYS_DOUBLE)
        c = checkp()
        c(neither, double_neither)
        c(single, double_single)
        c(double, double_double)
        c(both, double_both)
        c(reverse, double_reverse)
        c(more_single, double_more_single)
        c(more_double, double_more_double)
        c(more_single_double_first, double_more_single_double_first)
        c(more_double_single_first, double_more_double_single_first)

        c = checkp(quote_style=json5.QuoteStyle.ALWAYS_DOUBLE)
        c(neither, double_neither)
        c(single, double_single)
        c(double, double_double)
        c(both, double_both)
        c(reverse, double_reverse)
        c(more_single, double_more_single)
        c(more_double, double_more_double)
        c(more_single_double_first, double_more_single_double_first)
        c(more_double_single_first, double_more_double_single_first)

        c = checkp(quote_style=json5.QuoteStyle.ALWAYS_SINGLE)
        c(neither, single_neither)
        c(single, single_single)
        c(double, single_double)
        c(both, single_both)
        c(reverse, single_reverse)
        c(more_single, single_more_single)
        c(more_double, single_more_double)
        c(more_single_double_first, single_more_single_double_first)
        c(more_double_single_first, single_more_double_single_first)

        c = checkp(quote_style=json5.QuoteStyle.PREFER_DOUBLE)
        c(neither, double_neither)
        c(single, double_single)
        c(double, single_double)
        c(both, double_both)
        c(reverse, double_reverse)
        c(more_single, double_more_single)
        c(more_double, single_more_double)
        c(more_single_double_first, double_more_single_double_first)
        c(more_double_single_first, single_more_double_single_first)

        c = checkp(quote_style=json5.QuoteStyle.PREFER_SINGLE)
        c(neither, single_neither)
        c(single, double_single)
        c(double, single_double)
        c(both, single_both)
        c(reverse, single_reverse)
        c(more_single, double_more_single)
        c(more_double, single_more_double)
        c(more_single_double_first, double_more_single_double_first)
        c(more_double_single_first, single_more_double_single_first)

    def test_invalid_quote_styles(self):
        with self.assertRaises(TypeError):
            json5.dumps("it's", quote_style='always_double')
        with self.assertRaises(TypeError):
            json5.dumps('foo', quote_style=1)

    def test_skip_keys(self):
        od = OrderedDict()
        od[(1, 2)] = 2
        self.assertRaises(TypeError, json5.dumps, od)
        self.assertEqual(json5.dumps(od, skipkeys=True), '{}')

        od['foo'] = 1
        self.assertEqual(json5.dumps(od, skipkeys=True), '{foo: 1}')

        # Also test that having an invalid key as the last element
        # doesn't incorrectly add a trailing comma (see
        # https://github.com/dpranke/pyjson5/issues/33).
        od = OrderedDict()
        od['foo'] = 1
        od[(1, 2)] = 2
        self.assertEqual(json5.dumps(od, skipkeys=True), '{foo: 1}')

    def test_sort_keys(self):
        od = OrderedDict()
        od['foo'] = 1
        od['bar'] = 2
        self.assertEqual(json5.dumps(od, sort_keys=True), '{bar: 2, foo: 1}')

    def test_trailing_commas(self):
        # By default, multi-line dicts and lists should have trailing
        # commas after their last items.
        self.assertEqual(json5.dumps({'foo': 1}, indent=2), '{\n  foo: 1,\n}')
        self.assertEqual(json5.dumps([1], indent=2), '[\n  1,\n]')

        self.assertEqual(
            json5.dumps({'foo': 1}, indent=2, trailing_commas=False),
            '{\n  foo: 1\n}',
        )
        self.assertEqual(
            json5.dumps([1], indent=2, trailing_commas=False), '[\n  1\n]'
        )

    def test_supplemental_unicode(self):
        self.check(chr(0x10000), '"\\ud800\\udc00"')

    def test_empty_key(self):
        self.assertEqual(json5.dumps({'': 'value'}), '{"": "value"}')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
