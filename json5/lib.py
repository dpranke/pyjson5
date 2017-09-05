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

from .parser import Parser


def load(fp, **kwargs):
    """Deserialize ``fp`` (a ``.read()``-supporting file-like object
    containing a JSON document) to a Python object."""

    s = fp.read()
    return loads(s, **kwargs)


def loads(s, **kwargs):
    """Deserialize ``s`` (a ``str`` or ``unicode`` instance containing a
    JSON5 document) to a Python object."""

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


def dumps(obj, compact=False, as_json=False, **kwargs):
    """Serialize ``obj`` to a JSON5-formatted ``str``."""

    if as_json or not compact:
        return json.dumps(obj, **kwargs)

    t = type(obj)
    if obj == True:
        return u'true'
    elif obj == False:
        return u'false'
    elif obj == None:
        return u'null'
    elif t == type('') or t == type(u''):
        single = "'" in obj
        double = '"' in obj
        if single and double:
            return json.dumps(obj)
        elif single:
            return '"' + obj + '"'
        else:
            return "'" + obj + "'"
    elif t is float or t is int:
        return str(obj)
    elif t is dict:
        return u'{' + u','.join([
            _dumpkey(k) + u':' + dumps(v) for k, v in obj.items()
        ]) + '}'
    elif t is list:
        return u'[' + ','.join([dumps(el) for el in obj]) + u']'
    else:  # pragma: no cover
        return u''


def dump(obj, fp, **kwargs):
    """Serialize ``obj`` to a JSON5-formatted stream to ``fp`` (a ``.write()``-
    supporting file-like object)."""

    s = dumps(obj, **kwargs)
    fp.write(str(s))
