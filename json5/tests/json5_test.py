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

import StringIO
import math
import os
import unittest

import json5


class TestLoads(unittest.TestCase):
    maxDiff = None

    def check(self, s, obj):
        self.assertEqual(json5.loads(s), obj)

    def test_bools(self):
        self.check('true', True)
        self.check('false', False)

    def test_empty(self):
        self.assertRaises(ValueError, json5.loads, '')

    def test_hex_literals(self):
        self.check('0xf', 15)
        self.check('0xfe', 254)
        self.check('0xfff', 4095)
        self.check('0XABCD', 43981)
        self.check('0x123456', 1193046)

    def test_floats(self):
        self.check('1.5', 1.5)
        self.check('1.5e3', 1500.0)
        self.check('-0.5e-2', -0.005)
        self.check('Infinity', float('inf'))
        self.check('-Infinity', float('-inf'))
        self.assertTrue(math.isnan(json5.loads('NaN')))
        self.assertTrue(math.isnan(json5.loads('-NaN')))

    def test_identifiers(self):
        self.check('{a: 1}', {'a': 1})
        self.check('{$: 1}', {'$': 1})
        self.check('{_: 1}', {'_': 1})
        self.check('{a_b: 1}', {'a_b': 1})
        self.check('{a$: 1}', {'a$': 1})

        self.assertRaises(Exception, self.check, '{1: 1}', None)

    def test_ints(self):
        self.check('1', 1)
        self.check('-1', -1)
        self.check('+1', 1)

    def test_null(self):
        self.check('null', None)

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
        self.check("'\x66oo'", 'foo')
        self.check('"foo\\\nbar"', 'foobar')
        self.check("'foo\\\nbar'", 'foobar')
        self.assertRaises(Exception, self.check, '"\n', None)
        self.assertRaises(Exception, self.check, "'\n", None)

    def test_syntax_errors(self):
        try:
            json5.loads('')
        except ValueError as e:
            self.assertEqual('Empty strings are not legal JSON5',
                             e.message)

        try:
            json5.loads('''\
{"foo":
    14d}''')
        except ValueError as e:
            self.assertEqual('<string>:2 Unexpected "d" at column 7',
                             e.message)


class TestDump(unittest.TestCase):
    def test_basic(self):
        sio = StringIO.StringIO()
        json5.dump(True, sio)
        self.assertEqual('true', sio.getvalue())


class TestDumps(unittest.TestCase):
    maxDiff = None

    def check(self, obj, s):
        self.assertEqual(json5.dumps(obj, compact=True), s)

    def test_arrays(self):
        self.check([], '[]')
        self.check([1, 2, 3], '[1,2,3]')

    def test_bools(self):
        self.check(True, 'true')
        self.check(False, 'false')

    def test_numbers(self):
        self.check(15, '15')

    def test_null(self):
        self.check(None, 'null')

    def test_objects(self):
        self.check({'foo': 1}, '{foo:1}')
        self.check({'foo bar': 1}, '{"foo bar":1}')

    def test_strings(self):
        self.check("'single'", '"\'single\'"')
        self.check('"double"', "'\"double\"'")
        self.check("'single \\' and double \"'", '"\'single \\\\\' and double \\"\'"')
