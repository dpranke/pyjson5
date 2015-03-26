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

import json

from json5.parser import Parser

def load(fp, **kwargs):
    s = fp.read()
    return loads(s, **kwargs)


def loads(s, **kwargs):
    import pdb; pdb.set_trace()
    parser = Parser(s, '')
    obj, err = parser.parse()
    if not err:
        return obj
    raise Exception(err)


def dump(obj, fp, **kwargs):
    s = dumps(obj, **kwargs)
    fp.write(s)


def dumps(obj, **kwargs):
    return json.dumps(obj, **kwargs)
