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

import re
import json

from builtins import str

from json5.parser import Parser


def load(fp, **kwargs):
    s = fp.read()
    return loads(s, **kwargs)


def loads(s, **kwargs):
    if not s:
        raise ValueError('Empty strings are not legal JSON5')
    parser = Parser(s, '<string>')
    ast, err = parser.parse()
    if not err:
        return _walk_ast(ast)
    raise ValueError(err)


def _walk_ast(el):
    if el == 'None':
        return None
    if el == 'True':
        return True
    if el == 'False':
        return False
    ty, v = el
    if ty == 'number':
        if v.startswith('0x') or v.startswith('0X'):
           return int(v, base=16)
        if '.' in v or 'e' in v or 'E' in v:
           return float(v)
        if 'Infinity' in v:
           return float(v.replace('Infinity', 'inf'))
        if 'NaN' in v:
           return float(v.replace('NaN', 'nan'))
        return int(v)
    if ty == 'string':
        return v
    if ty == 'object':
        o = {}
        for m in v:
            k = m[0]
            v = _walk_ast(m[1])
            o[k] = v
        return o
    if ty == 'array':
        return [_walk_ast(el) for el in v]
    raise Exception('unknown el: ' + el)  # pragma: no cover


_notletter = re.compile('\W')


def _dumpkey(k):
    if _notletter.search(k):
        return json.dumps(k)
    else:
        return str(k)


def dumps(data, compact=False, **kwargs):
    if not compact:
        return json.dumps(data, **kwargs)

    t = type(data)
    if data == True:
        return u'true'
    elif data == False:
        return u'false'
    elif data == None:
        return u'null'
    elif t == type('') or t == type(u''):
        single = "'" in data
        double = '"' in data
        if single and double:
            return json.dumps(data)
        elif single:
            return '"' + data + '"'
        else:
            return "'" + data + "'"
    elif t is float or t is int:
        return str(data)
    elif t is dict:
        return u'{' + u','.join([
            _dumpkey(k) + u':' + dumps(v) for k, v in data.items()
        ]) + '}'
    elif t is list:
        return u'[' + ','.join([dumps(v) for v in data]) + u']'
    else:  # pragma: no cover
        return u''


def dump(obj, fp, **kwargs):
    s = dumps(obj, **kwargs)
    fp.write(str(s))
