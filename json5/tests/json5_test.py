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

import math
import os
import sys
import unittest

is_python2 = sys.version_info[0] < 3
if is_python2:
    from StringIO import StringIO
else:
    from io import StringIO

import json5


class TestLoads(unittest.TestCase):
    maxDiff = None

    def check(self, s, obj):
        self.assertEqual(json5.loads(s), obj)

    def check_fail(self, s, err=None):
        try:
            json5.loads(s)
            self.fail()  # pragma: no cover
        except ValueError as e:
            if err:
                self.assertEqual(err, str(e))

    def test_arrays(self):
        self.check('[]', [])
        self.check('[0]', [0])
        self.check('[0,1]', [0, 1])
        self.check('[ 0 , 1 ]', [0, 1])

    def test_bools(self):
        self.check('true', True)
        self.check('false', False)

    def test_cls_is_not_supported(self):
        self.assertRaises(AssertionError, json5.loads, '1', cls=lambda x: x)

    def test_empty_strings_are_errors(self):
        self.check_fail('', 'Empty strings are not legal JSON5')

    def test_encoding(self):
        if is_python2:
          s = '"\xf6"'
        else:
          s = b'"\xf6"'
        self.assertEqual(json5.loads(s, encoding='iso-8859-1'),
                         u"\xf6")

    def test_numbers(self):
        # decimal literals
        self.check('1', 1)
        self.check('-1', -1)
        self.check('+1', 1)

        # hex literals
        self.check('0xf', 15)
        self.check('0xfe', 254)
        self.check('0xfff', 4095)
        self.check('0XABCD', 43981)
        self.check('0x123456', 1193046)

        # floats
        self.check('1.5', 1.5)
        self.check('1.5e3', 1500.0)
        self.check('-0.5e-2', -0.005)

        # names
        self.check('Infinity', float('inf'))
        self.check('-Infinity', float('-inf'))
        self.assertTrue(math.isnan(json5.loads('NaN')))
        self.assertTrue(math.isnan(json5.loads('-NaN')))

        # syntax errors
        self.check_fail('14d', '<string>:1 Unexpected "d" at column 3')

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
        self.check(u'{\xc3: 1}', {u'\xc3': 1})

    def test_null(self):
        self.check('null', None)

    def test_object_hook(self):
        hook = lambda d: [d]
        self.assertEqual(json5.loads('{foo: 1}', object_hook=hook),
                         [{"foo": 1}])

    def test_object_pairs_hook(self):
        hook = lambda pairs: pairs
        self.assertEqual(json5.loads('{foo: 1, bar: 2}',
                                     object_pairs_hook=hook),
                         [('foo', 1), ('bar', 2)])

    def test_objects(self):
        self.check('{}', {})
        self.check('{"foo": 0}', {"foo": 0})
        self.check('{"foo":0,"bar":1}', {"foo": 0, "bar": 1})
        self.check('{ "foo" : 0 , "bar" : 1 }', {"foo": 0, "bar": 1})

    def test_parse_constant(self):
        hook = lambda x: x
        self.assertEqual(json5.loads('-Infinity', parse_constant=hook),
                         '-Infinity')
        self.assertEqual(json5.loads('NaN', parse_constant=hook),
                         'NaN')

    def test_parse_float(self):
        hook = lambda x: x
        self.assertEqual(json5.loads('1.0', parse_float=hook), '1.0')

    def test_parse_int(self):
        hook = lambda x, base=10: x
        self.assertEqual(json5.loads('1', parse_int=hook), '1')

    def test_sample_file(self):
        path = os.path.join(os.path.dirname(__file__), '..', '..',
                            'sample.json5')
        with open(path) as fp:
            obj = json5.load(fp)
        self.assertEqual({
            u'oh': [
                u"we shouldn't forget",
                u"arrays can have",
                u"trailing commas too",
            ],
            u"this": u"is a multi-line string",
            u"delta": 10,
            u"hex": 3735928559,
            u"finally": "a trailing comma",
            u"here": "is another",
            u"to": float("inf"),
            u"while": True,
            u"half": 0.5,
            u"foo": u"bar"
            }, obj)

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

        # string literals w/ continuation markers at the end of the line.
        # These should not have spaces is the result.
        self.check('"foo\\\nbar"', 'foobar')
        self.check("'foo\\\nbar'", 'foobar')

        # unterminated string literals.
        self.check_fail('"\n')
        self.check_fail("'\n")

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

    def test_whitespace(self):
        self.check('\n1', 1)
        self.check('\r1', 1)
        self.check('\r\n1', 1)
        self.check('\t1', 1)
        self.check('\v1', 1)
        self.check(u'\uFEFF 1', 1)
        self.check(u'\u00A0 1', 1)
        self.check(u'\u2028 1', 1)
        self.check(u'\u2029 1', 1)


class TestDump(unittest.TestCase):
    def test_basic(self):
        sio = StringIO()
        json5.dump(True, sio)
        self.assertEqual('true', sio.getvalue())


class TestDumps(unittest.TestCase):
    maxDiff = None

    def check(self, obj, exp, **kwargs):
        got = json5.dumps(obj, **kwargs)
        self.assertMultiLineEqual(exp, got)

    def test_array_with_multiple_elements(self):
        self.check([1, 2, 3], '[1, 2, 3]')

    def test_array_with_no_elements(self):
        self.check([], '[]')

    def test_array_with_one_element(self):
        self.check([1], '[1]')

    def test_as_json(self):
        self.check({'foo': 1, 'bar': 3, 'baz': 2},
                   '{"bar": 3, "baz": 2, "foo": 1}',
                   sort_keys=True, as_json=True)

    def test_bools(self):
        self.check(True, 'true')
        self.check(False, 'false')

    def test_compact(self):
        self.check({'foo': 1, 'bar': 3, 'baz': 2},
                   '{bar:3,baz:2,foo:1}',
                   sort_keys=True, compact=True)

    def test_circular_array(self):
        o = []
        o.append(o)
        self.assertRaises(ValueError, self.check, o, '',
                          check_circular=True)

    def test_circular_object(self):
        o = {}
        o['self'] = o
        self.assertRaises(ValueError, self.check, o, '',
                          check_circular=True)

    def test_default_is_provided(self):
        self.check({1}, "'Hi'", default=lambda obj: 'Hi')

    def test_default_raises(self):
        self.assertRaises(TypeError, self.check, {1}, '')

    def test_ensure_ascii_is_false(self):
        self.check(u'foobar', u"'foobar'", ensure_ascii=False)

    def test_ensure_ascii_is_true_by_default(self):
        self.check(u'\u00e9', "'\\u00e9'")

    def test_float(self):
        self.check(1.0, '1.0')

    def test_indented_array(self):
        self.check([1, 2],
                   '[\n  1,\n  2\n]', indent=2)

    def test_indented_object(self):
        self.check({'foo': 1, 'bar': 2},
                   '{\n  foo: 1,\n  bar: 2\n}', indent=2)

    def test_infinity(self):
        self.check(float('inf'), 'Infinity')

    def test_infinity_not_allowed(self):
        self.assertRaises(ValueError, self.check, float('inf'), '',
                          allow_nan=False)

    def test_int(self):
        self.check(15, '15')

    def test_key_is_ident(self):
        self.check({'foo': 1}, '{foo: 1}')

    def test_key_with_dquote(self):
        self.check({'foo"': 1}, "{'foo\"': 1}")

    def test_key_with_space(self):
        self.check({'foo ': 1}, "{'foo ': 1}")

    def test_key_with_squote(self):
        self.check({"foo'": 1}, '{"foo\'": 1}')

    def test_minus_infinity(self):
        self.check(float('-inf'), '-Infinity')

    def test_minus_infinity_not_allowed(self):
        self.assertRaises(ValueError, self.check, float('-inf'), '',
                          allow_nan=False)

    def test_nan(self):
        self.check(float('nan'), 'NaN')

    def test_nan_not_allowed(self):
        self.assertRaises(ValueError, self.check, float('nan'), '',
                          allow_nan=False)

    def test_null(self):
        self.check(None, 'null')

    def test_object_with_multiple_elements(self):
        self.check({'foo': 1}, '{foo: 1}')

    def test_object_with_no_elements(self):
        self.check({}, '{}')

    def test_object_with_one_element(self):
        self.check({'foo': 1}, '{foo: 1}')

    def test_separators(self):
        self.check({'foo': 1, 'bar': 3, 'baz': 2},
                   '{bar=3;baz=2;foo=1}',
                   sort_keys=True, separators=(';', "="))

    def test_skipkeys_is_false_by_default(self):
        self.assertRaises(TypeError, self.check, {(1, 2): True}, '')

    def test_skipkeys_is_true(self):
        self.check({(1, 2): True}, '{}', skipkeys=True)

    def test_sort_keys(self):
        self.check({'foo': 1, 'bar': 3, 'baz': 2},
                   "{bar: 3, baz: 2, foo: 1}", sort_keys=True)

    def test_string(self):
        self.check('hello, world', "'hello, world'")

    def test_string_containing_a_single_quote(self):
        self.check("single ' ", '"single \' "')

    def test_string_containing_a_single_quote_as_json(self):
        self.check("single ' ", '"single \' "')

    def test_string_containing_a_double_quote(self):
        self.check('double " ', "'double \" '")

    def test_string_containing_both_a_single_quote_and_a_double_quote(self):
        self.check("single ' and double \" ",
                   '"single \' and double \\" "')

    def test_trailing_commas_in_array(self):
        self.check([1, 2],
                   '[1, 2, ]', trailing_commas=True)

    def test_trailing_commas_in_array_with_indent(self):
        self.check([1, 2],
                   '[\n  1,\n  2,\n]',
                   trailing_commas=True, indent=2)

    def test_trailing_commas_in_object(self):
        self.check({'foo': 1, 'bar': 2},
                   '{foo: 1, bar: 2, }',
                   trailing_commas=True)

    def test_trailing_commas_in_object_with_indent(self):
        self.check({'foo': 1, 'bar': 2},
                   '{\n  foo: 1,\n  bar: 2,\n}',
                   trailing_commas=True, indent=2)
