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
import sys

_is_python2 = sys.version_info[0] < 3
if _is_python2:
    # pylint: disable=redefined-builtin
    str = unicode

from .parser import Parser


def load(fp, **kwargs):
    """Deserialize ``fp`` (a ``.read()``-supporting file-like object
    containing a JSON document) to a Python object."""
    return loads(fp.read())


def loads(s, **kwargs):
    """Deserialize ``s`` (a ``str`` or ``unicode`` instance containing a
    JSON5 document) to a Python object."""
    cls = kwargs.pop('cls', Decoder)
    return cls(**kwargs).decode(s)


class Decoder(object):

    def __init__(self, encoding=None, object_hook=None, parse_float=None,
                 parse_int=None, parse_constant=None, object_pairs_hook=None):
        self.encoding = encoding or 'utf-8'
        self.parse_float = parse_float or float
        self.parse_int = parse_int or self._default_parse_int
        self.parse_constant = parse_constant or self._default_parse_constant
        self.object_pairs_hook = object_pairs_hook
        if object_pairs_hook:
            self.object_pairs_hook = object_pairs_hook
        elif object_hook:
            self.object_pairs_hook = lambda pairs: object_hook(dict(pairs))
        else:
            self.object_pairs_hook = dict

    def decode(self, s):
        if _is_python2:
            decodable_type = type('')
        else:
            decodable_type = type(b'')
        if isinstance(s, decodable_type):
            s = s.decode(self.encoding)

        parser = Parser(s, '<string>')
        ast, err = parser.parse()
        if err:
            raise ValueError(err)

        return self._walk(ast)

    def _default_parse_constant(self, s):
        return float(s.replace('Infinity', 'inf').replace('NaN', 'nan'))

    def _default_parse_int(self, node_val):
        if node_val.startswith('0x') or node_val.startswith('0X'):
            return int(node_val, base=16)
        else:
            return int(node_val)

    def _walk(self, ast_node):
        node_type, node_val = ast_node
        if node_type in ('null', 'true', 'false', 'string'):
            return node_val
        elif node_type == 'number':
            if node_val.startswith('0x') or node_val.startswith('0X'):
                return self.parse_int(node_val)
            elif '.' in node_val or 'e' in node_val or 'E' in node_val:
                return self.parse_float(node_val)
            elif 'Infinity' in node_val or 'NaN' in node_val:
                return self.parse_constant(node_val)
            else:
                return self.parse_int(node_val)
        elif node_type == 'object':
            pairs = [(key, self._walk(val)) for key, val in node_val]
            return self.object_pairs_hook(pairs)
        elif node_type == 'array':
            return [self._walk(el) for el in node_val]
        else:  # pragma: no cover
            raise Exception('unknown ast node: ' + repr(ast_node))


def dump(obj, fp, **kwargs):
    """Serialize ``obj`` to a JSON5-formatted stream to ``fp`` (a ``.write()``-
    supporting file-like object)."""
    fp.write(dumps(obj, **kwargs))


def dumps(obj, **kwargs):
    """Serialize ``obj`` to a JSON5-formatted string."""
    cls = kwargs.pop('cls', Encoder)
    return cls(**kwargs).encode(obj)


squote = "'"
dquote = '"'
bslash = '\\'


class Encoder(object):

    def __init__(self, skipkeys=False, ensure_ascii=True,
                 check_circular=True, allow_nan=True,
                 indent=None, separators=None,
                 encoding='utf-8', default=None,
                 sort_keys=False, compact=False, as_json=False,
                 trailing_commas=False):
        self.skipkeys = skipkeys
        self.ensure_ascii = ensure_ascii
        self.check_circular = check_circular
        self.allow_nan = allow_nan
        self.indent = indent
        self.encoding = encoding
        self.default = default or self._default
        self.sort_keys = sort_keys
        self.trailing_commas = trailing_commas
        self.as_json = as_json

        if separators:
            item_sep, key_sep = separators
        else:
            item_sep, key_sep = (None, None)
        if item_sep is None:
            self.item_separator = ',' if compact else ', '
        else:
            self.item_separator = item_sep
        if key_sep is None:
            self.key_separator = ':' if compact else ': '
        else:
            self.key_separator = key_sep
        if self.indent:
            self.item_separator = self.item_separator.strip()

        self._seen_objs = set()
        self._valid_key_types = [str, int, float, bool, type(None)]
        if _is_python2:
            self._valid_key_types.extend([long, type('')])
        self._indent_level = 0

    def encode(self, obj):
        t = type(obj)
        if obj is True:
            return 'true'
        elif obj is False:
            return 'false'
        elif obj is None:
            return 'null'
        elif t == type('') or t == type(u''):
            return self._encode_str(obj)
        elif t == float:
            return self._encode_float(obj)
        elif t is int:
            return str(obj)
        elif t is dict:
            return self._encode_dict(obj)
        elif t is list:
            return self._encode_list(obj)
        else:
            return self.encode(self.default(obj))

    def _default(self, obj):
        raise TypeError(obj)

    def _encode_dict(self, obj):
        keys = obj.keys()
        if not keys:
            return '{}'

        if self.sort_keys:
            keys = sorted(keys)
        num_keys = len(keys) - 1

        if self.check_circular:
            if id(obj) in self._seen_objs:
                raise ValueError(obj)
            self._seen_objs.add(id(obj))

        s = '{'
        self._indent_level += 1
        for i, k in enumerate(keys):
            if type(k) not in self._valid_key_types:
                if self.skipkeys:
                    continue
                raise TypeError(k)
            s += self._indent() + self._esc_key(k) + self.key_separator
            s += self.encode(obj[k]) + self._sep(i, num_keys)
        self._indent_level -= 1
        s += self._indent() + '}'
        return s

    def _encode_float(self, obj):
        if not math.isnan(obj) and not math.isinf(obj):
            return str(obj)
        elif not self.allow_nan:
            raise ValueError(obj)
        elif math.isnan(obj):
            return 'NaN'
        elif obj == float('inf'):
            return 'Infinity'
        else:
            return '-Infinity'

    def _encode_list(self, obj):
        if self.check_circular:
            if id(obj) in self._seen_objs:
                raise ValueError(obj)
            self._seen_objs.add(id(obj))
        num_els = len(obj) - 1

        if not obj:
            return '[]'

        s = '['
        self._indent_level += 1
        for i, el in enumerate(obj):
            s += self._indent() + self.encode(el) + self._sep(i, num_els)
        self._indent_level -= 1
        s += self._indent() + ']'
        return s

    def _encode_str(self, obj):
        has_single_quote = "'" in obj
        if not has_single_quote:
            return squote + self._esc_str(obj, esc_dquote=False) + squote
        else:
            return dquote + self._esc_str(obj, esc_dquote=True) + dquote

    def _esc_char(self, ch, esc_dquote):
        o = ord(ch)
        if ch == dquote and esc_dquote:
            return bslash + dquote
        elif 32 <= o < 128:
            return ch
        else:
            return '\\u%04x' % o

    def _esc_key(self, k):
        if self.as_json:
            return dquote + self._esc_str(k, esc_dquote=True) + dquote

        ch = k[0]
        needs_quotes = not self._is_id_start(ch)
        has_squote = ch == squote
        for ch in k[1:]:
            needs_quotes = needs_quotes or not self._is_id_continue(ch)
            has_squote = has_squote or ch == squote
        if needs_quotes:
            if not has_squote:
                return squote + self._esc_str(k, esc_dquote=False) + squote
            else:
                return dquote + self._esc_str(k, esc_dquote=True) + dquote
        else:
            return k

    def _esc_str(self, s, esc_dquote=True):
        if not self.ensure_ascii:
            return s
        chars = []
        for ch in s:
            chars.append(self._esc_char(ch, esc_dquote))
        return ''.join(chars)

    def _indent(self):
        if self.indent is not None:
            return '\n' + ' ' * self.indent * self._indent_level
        else:
            return ''

    def _is_id_start(self, ch):
        return ch.isalpha() or ch == '_'

    def _is_id_continue(self, ch):
        return ch.isalnum() or ch == '_'

    def _sep(self, i, n):
        if i < n:
            return self.item_separator
        elif self.trailing_commas:
            if self.indent is None:
                return self.item_separator
            else:
                return self.item_separator.strip()
        else:
            return ''
