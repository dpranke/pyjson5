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

import unittest

import json5

class LoadTest(unittest.TestCase):
    def test_hex_literals(self):
        self.assertEqual(json5.loads("0xf"), 15)
        self.assertEqual(json5.loads("0xfe"), 254)
        self.assertEqual(json5.loads("0xfff"), 4095)
        self.assertEqual(json5.loads("0XABCD"), 43981)
        self.assertEqual(json5.loads("0x123456"), 1193046)
