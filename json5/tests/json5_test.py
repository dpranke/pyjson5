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
import unittest

import json5


class Tests(unittest.TestCase):
    def check(self, s, obj):
        self.assertEqual(json5.loads(s), obj)

    def test_empty(self):
        self.assertRaises(ValueError, json5.loads, '')

    def test_hex_literals(self):
        self.check('0xf', 15)
        self.check('0xfe', 254)
        self.check('0xfff', 4095)
        self.check('0XABCD', 43981)
        self.check('0x123456', 1193046)

    def test_ints(self):
        self.check('1', 1)
        self.check('-1', -1)
        self.check('+1', 1)

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

    def test_sample_file(self):
        path = os.path.join(os.path.dirname(__file__), '..', '..',
                            'sample.json5')
        with open(path) as fp:
            obj = json5.load(fp)
        self.assertEqual({
            "oh": [
                "we shouldn't forget",
                "arrays can have",
                "trailing commas too",
            ],
            "this": "is a \nmulti-line string",
            "delta": 10,
            "hex": 3735928559,
            "finally": "a trailing comma",
            "here": "is another",
            "to": float("inf"),
            "while": True,
            "half": 0.5,
            "foo": "bar"
            }, obj)

    def test_strings(self):
        self.check('"foo"', 'foo')
        self.check("'foo'", 'foo')
        self.check("'\x66oo'", 'foo')
        self.check('"foo\\\nbar"', 'foo\nbar')
        self.check("'foo\\\nbar'", 'foo\nbar')
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
