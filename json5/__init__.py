# Copyright 2014 Google Inc. All rights reserved.
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

"""A pure Python implementation of the JSON5 configuration language.

`JSON5 <https://www.json5.org>`_ extends the
`JSON <http://www.json.org>`_ data interchange format to make it more
usable as a configuration language:

* JavaScript-style comments (both single and multi-line) are legal.

* Object keys may be unquoted if they are legal ECMAScript identifiers

* Objects and arrays may end with trailing commas.

* Strings can be single-quoted, and multi-line string literals are allowed.

There are a few other more minor extensions to JSON; see the above pages
for the full details.

This project implements a reader and writer implementation for Python;
mirroring the
`standard JSON package <https://docs.python.org/library/json.html>`_'s
API.

Python values are mapped to JSON5 values as follows:

Python                  JSON5
------                  -----
None                    null
True                    true
False                   false
float('inf')            Infinity
float('nan')            NaN
float('-inf')           -Infinity
int/float               Number
list                    array
dict                    object

The ``tool`` module implements a command-line tool that can be used to
convert between and reformat JSON and JSON5.

    $ echo '{"foo": "bar"}' | python -m json5.tool
    {foo: "bar"}
    $ echo '{"foo": "bar"}' | python -m json5.tool --compact
    {foo:"bar"}
    $ echo '[1, 2]' | python -m json5.tool --indent=2 --trailing-commas
    [
      1,
      2,
    ]
    $ echo '{foo: "bar"}' | python -m json5.tool --json
    {"foo": "bar"}
    $

"""

from . import tool
from .lib import Decoder, Encoder, dump, dumps, load, loads, dump, dumps
from .version import VERSION


__all__ = [
    'VERSION',
    'Decoder',
    'Encoder',
    'dump',
    'dumps',
    'load',
    'loads',
    'tool',
]
