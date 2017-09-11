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
import unicodedata


_is_python2 = sys.version_info[0] < 3
if _is_python2:
    # pylint: disable=redefined-builtin
    str = unicode

from .parser import Parser


def load(fp, cls=None, encoding='utf-8', object_hook=None, parse_float=None,
         parse_int=None, parse_constant=None, object_pairs_hook=None):
    """Deserialize ``fp`` (a ``.read()``-supporting file-like object
    containing a JSON document) to a Python object.

    For help on the keyword args, see the docstring for json5.loads()."""

    return loads(fp.read(), cls=cls, encoding=encoding,
                 object_hook=object_hook, parse_float=parse_float,
                 parse_int=parse_int, parse_constant=parse_constant,
                 object_pairs_hook=object_pairs_hook)


def loads(s, cls=None, encoding='utf-8', object_hook=None, parse_float=None,
          parse_int=None, parse_constant=None, object_pairs_hook=None):
    """Deserialize ``s`` (a ``str`` or ``unicode`` instance containing a
    JSON5 document) to a Python object.

    If ``cls`` is specified, it will be used to encode the object instead
    of the standard Decoder class.

    In Python2, ``encoding`` determines the encoding used to used to
    interpret an object of type ``str``; if the object is a unicode
    string, the encoding is ignored. In Python3, the same applies if the
    object is a byte string and not a string.

    If ``object_hook`` is not none, it will be used to convert an dict
    into a custom Python value.

    If ``parse_float`` is not none, it will be used to convert the
    string representation of a floating-point number into a custom
    Python value.

    If ``parse_int`` is not none, it will be used to convert the string
    representation of an integer number into a custom Python value.

    If ``parse_constant`` is not none, it will be used to convert the
    string representation of a Nan, -Infinity, and Infinity JSON5
    values into Python values.

    If ``object_pairs_hook`` is not none, it will be used to convert an
    object into a custom Python value; it is passed a list of key-value
    pairs. If object_pairs_hook and object_hook are both passed,
    object_pairs_hook takes precedence.
    """
    cls = cls or Decoder
    return cls(encoding=encoding, object_hook=object_hook,
               parse_float=parse_float, parse_int=parse_int,
               parse_constant=parse_constant,
               object_pairs_hook=object_pairs_hook).decode(s)


class Decoder(object):
    """Simple JSON5 <http://json5.org> decoder."""

    def __init__(self, encoding='utf-8', object_hook=None, parse_float=None,
                 parse_int=None, parse_constant=None, object_pairs_hook=None):
        'For help on the keyword args, see the docstring for json5.loads().'

        self.encoding = encoding
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
        'Returns the string decoded into a Python object.'
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



def dump(obj, fp, cls=None, skipkeys=False, ensure_ascii=True,
         check_circular=True, allow_nan=True, indent=None, separators=None,
         encoding='utf-8', default=None, sort_keys=False,
         compact=False, as_json=False, trailing_commas=False):
    """Serialize ``obj`` to a JSON5-formatted stream to ``fp`` (a ``.write()``-
    supporting file-like object).

    For help on the keyword args, see the docstring for json5.dumps."""

    fp.write(dumps(obj, cls=cls, skipkeys=skipkeys, ensure_ascii=ensure_ascii,
                   check_circular=check_circular, allow_nan=allow_nan,
                   indent=indent, separators=separators, encoding=encoding,
                   default=default, sort_keys=sort_keys, compact=compact,
                   as_json=as_json, trailing_commas=trailing_commas))


def dumps(obj, cls=None, skipkeys=False, ensure_ascii=True,
         check_circular=True, allow_nan=True, indent=None, separators=None,
         encoding='utf-8', default=None, sort_keys=False,
         compact=False, as_json=False, trailing_commas=False):
    """Returns ``obj`` serialized as a JSON5-formatted string.

    If ``cls`` is specified, it will be used to encode the object instead
    of the standard Encoder class.

    ``skipkeys``, if true, will tell the encoder to skip any keys in a
    dict that are not of type str, int, float, or None; if false (the
    default), a TypeError will be raised instead.

    If ``ensure_ascii`` is true (the default), all non-ASCII characters
    in the output are encoded as \\uXXXX sequences instead; if false, the
    string will be rendered into unicode instead.

    If ``check_circular`` is true (the default), if the encoder tries to
    encode an object that contains circular references, a ValueError will
    be raised; if it is false, the encoder will be slightly faster, but
    unpredictable things will happen if an object contains cycles.

    If ``allow_nan`` is true (the default), floating point values of NaN,
    -Infinity, and +Infinity are allowed, otherwise a ValueError is
    raised.

    If ``indent`` is None (the default), the encoding will contain no
    newlines or indentation; if indent is zero, the encoding will contain
    newlines but not be indented and if indent is greater than zero, each
    line will be indented by that many spaces as appropriate.

    If ``separators`` is non-None, it must be a tuple of two strings, the
    first of which is used to separate items in objects and lists, and the
    second of which is used to separate a key from its value in an object.
    If it is None, the default value of (', ', ': ') will be used (unless
    compact=True is passed, see below).

    In Python2, ``encoding`` determines the encoding used to used to
    interpret an object of type ``str``; if the object is a unicode string,
    the encoding is ignored. In Python3, the same applies if the object is
    a byte string instead of a string.

    If ``default`` is non-None, it will be invoked whenever the object is
    of a non-standard type; it must return an equivalent standard
    representation.

    If ``sort_keys`` is true; an object will be encoded with its keys and
    values in lexicographic order; if false, the keys may show up in an
    arbitrary order.

    If ``compact`` is true, the object will be rendered in the most
    compact way possible; this is the same as passing
    separators=(',',':'), indent=None, as_json=False, and
    trailing_commas=False. However, if any of those arguments are also
    passed, they will override the compact value. This field is an
    extension to the standard JSON API.

    If ``as_json`` is true, the object will be encoded as JSON, not
    JSON5. This is an extension to the standard JSON API.

    If ``trailing_commas`` is true, then objects and lists will be
    encoded with a comma on the end. For example, you'd get [1,2,]
    instead of [1,2]. This is an extension to the standard JSON API.
    """

    cls = cls or Encoder
    return cls(skipkeys=skipkeys, ensure_ascii=ensure_ascii,
               check_circular=check_circular, allow_nan=allow_nan,
               indent=indent, separators=separators, encoding=encoding,
               default=default, sort_keys=sort_keys, compact=compact,
               as_json=as_json, trailing_commas=trailing_commas).encode(obj)


squote = "'"
dquote = '"'
bslash = '\\'


class Encoder(object):
    """Simple JSON5 <http://json5.org> encoder."""

    def __init__(self, skipkeys=False, ensure_ascii=True,
                 check_circular=True, allow_nan=True,
                 indent=None, separators=None,
                 encoding='utf-8', default=None,
                 sort_keys=False, compact=False, as_json=False,
                 trailing_commas=False):
        'For help on the keyword args, see the docstring for json5.dumps().'

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
        """Return the obj serialized into a string."""

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

        needs_quotes = not self._is_id_start(k)
        has_squote = k[0] == squote
        for i, ch in enumerate(k[1:], 1):
            needs_quotes = needs_quotes or not self._is_id_cont(k[i:])
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

    _id_start_cats = ('Ll', 'Lm', 'Lo', 'Lt', 'Lu', 'Nl')

    _id_cont_cats = _id_start_cats + ('Mn', 'Mc', 'Nd', 'Pc')

    def _indent(self):
        if self.indent is not None:
            return '\n' + ' ' * self.indent * self._indent_level
        else:
            return ''

    def _is_any_cat(self, ch, cats):
        return unicodedata.category(str(ch)) in cats

    def _is_ascii_start(self, ch):
        return ch.isalpha() or ch == '_' or ch == '$'

    def _is_hex(self, ch):
        return ('0' <= ch <= '9') or ('a' <= ch <= 'f') or ('A' <= ch <= 'F')

    def _is_id_cont(self, s):
        ch = s[0]
        return (self._is_ascii_start(ch) or ch.isdigit() or
                self._is_any_cat(ch, self._id_cont_cats) or
                ch == u'\u200C' or ch == u'\u200D' or self._is_uni_esc(s))

    def _is_id_start(self, s):
        ch = s[0]
        return (self._is_ascii_start(ch) or
                self._is_any_cat(ch, self._id_start_cats) or
                self._is_uni_esc(s))

    def _is_uni_esc(self, s):
        return (len(s) >= 6 and s[0] == '\\' and s[1] == 'u' and
                self._is_hex(s[2]) and self._is_hex(s[3]) and
                self._is_hex(s[4]) and self._is_hex(s[5]))

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
