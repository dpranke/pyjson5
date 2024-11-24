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

import enum
import math
import re
from typing import (
    Any,
    Callable,
    IO,
    Iterable,
    Mapping,
    Optional,
    Set,
    Tuple,
    Union,
)
import unicodedata

from .parser import Parser


# Used when encoding keys, below.
_reserved_word_re: Optional[re.Pattern] = None


class QuoteStyle(enum.Enum):
    """Controls how strings will be quoted during encoding.

    See description of the `quote_strings` keyword to dump/dumps/JSON5Encoder,
    below.
    """

    ALWAYS_DOUBLE = 1
    ALWAYS_SINGLE = 2
    PREFER_DOUBLE = 3
    PREFER_SINGLE = 4


class _QuotesSeen(enum.IntFlag):
    NONE = 0
    SINGLE = 1
    DOUBLE = 2
    BOTH = 3


def load(
    fp: IO,
    *,
    encoding: Optional[str] = None,
    cls: Any = None,
    object_hook: Optional[Callable[[Mapping[str, Any]], Any]] = None,
    parse_float: Optional[Callable[[str], Any]] = None,
    parse_int: Optional[Callable[[str], Any]] = None,
    parse_constant: Optional[Callable[[str], Any]] = None,
    strict: bool = True,
    object_pairs_hook: Optional[
        Callable[[Iterable[Tuple[str, Any]]], Any]
    ] = None,
    allow_duplicate_keys: bool = True,
) -> Any:
    """Deserialize ``fp`` (a ``.read()``-supporting file-like object
    containing a JSON document) to a Python object.

    Supports almost the same arguments as ``json.load()`` except that:
        - the `cls` keyword is ignored.
        - an extra `allow_duplicate_keys` parameter supports checking for
          duplicate keys in a object; by default, this is True for
          compatibility with ``json.load()``, but if set to False and
          the object contains duplicate keys, a ValueError will be raised.
    """

    s = fp.read()
    return loads(
        s,
        encoding=encoding,
        cls=cls,
        object_hook=object_hook,
        parse_float=parse_float,
        parse_int=parse_int,
        parse_constant=parse_constant,
        strict=strict,
        object_pairs_hook=object_pairs_hook,
        allow_duplicate_keys=allow_duplicate_keys,
    )


def loads(
    s: str,
    *,
    encoding: Optional[str] = None,
    cls: Any = None,
    object_hook: Optional[Callable[[Mapping[str, Any]], Any]] = None,
    parse_float: Optional[Callable[[str], Any]] = None,
    parse_int: Optional[Callable[[str], Any]] = None,
    parse_constant: Optional[Callable[[str], Any]] = None,
    strict: bool = True,
    object_pairs_hook: Optional[
        Callable[[Iterable[Tuple[str, Any]]], Any]
    ] = None,
    allow_duplicate_keys: bool = True,
):
    """Deserialize ``s`` (a string containing a JSON5 document) to a Python
    object.

    Supports the same arguments as ``json.load()`` except that:
        - the `cls` keyword is ignored.
        - an extra `allow_duplicate_keys` parameter supports checking for
          duplicate keys in a object; by default, this is True for
          compatibility with ``json.load()``, but if set to False and
          the object contains duplicate keys, a ValueError will be raised.
    """

    assert cls is None, 'Custom decoders are not supported'

    if isinstance(s, bytes):
        encoding = encoding or 'utf-8'
        s = s.decode(encoding)

    if not s:
        raise ValueError('Empty strings are not legal JSON5')
    parser = Parser(s, '<string>')
    ast, err, _ = parser.parse(global_vars={'_strict': strict})
    if err:
        raise ValueError(err)

    def _fp_constant_parser(s):
        return float(s.replace('Infinity', 'inf').replace('NaN', 'nan'))

    if object_pairs_hook:
        dictify = object_pairs_hook
    elif object_hook:

        def dictify(pairs):
            return object_hook(dict(pairs))
    else:
        dictify = dict

    if not allow_duplicate_keys:
        _orig_dictify = dictify

        def dictify(pairs):  # pylint: disable=function-redefined
            return _reject_duplicate_keys(pairs, _orig_dictify)

    parse_float = parse_float or float
    parse_int = parse_int or int
    parse_constant = parse_constant or _fp_constant_parser

    return _walk_ast(ast, dictify, parse_float, parse_int, parse_constant)


def _reject_duplicate_keys(pairs, dictify):
    keys = set()
    for key, _ in pairs:
        if key in keys:
            raise ValueError(f'Duplicate key "{key}" found in object')
        keys.add(key)
    return dictify(pairs)


def _walk_ast(
    el,
    dictify: Callable[[Iterable[Tuple[str, Any]]], Any],
    parse_float,
    parse_int,
    parse_constant,
):
    if el == 'None':
        return None
    if el == 'True':
        return True
    if el == 'False':
        return False
    ty, v = el
    if ty == 'number':
        if v.startswith('0x') or v.startswith('0X'):
            return parse_int(v, base=16)
        if '.' in v or 'e' in v or 'E' in v:
            return parse_float(v)
        if 'Infinity' in v or 'NaN' in v:
            return parse_constant(v)
        return parse_int(v)
    if ty == 'string':
        return v
    if ty == 'object':
        pairs = []
        for key, val_expr in v:
            val = _walk_ast(
                val_expr, dictify, parse_float, parse_int, parse_constant
            )
            pairs.append((key, val))
        return dictify(pairs)
    if ty == 'array':
        return [
            _walk_ast(el, dictify, parse_float, parse_int, parse_constant)
            for el in v
        ]
    raise ValueError('unknown el: ' + el)  # pragma: no cover


def dump(
    obj: Any,
    fp: IO,
    *,
    skipkeys: bool = False,
    ensure_ascii: bool = True,
    check_circular: bool = True,
    allow_nan: bool = True,
    cls: Optional['JSON5Encoder'] = None,
    indent: Optional[Union[int, str]] = None,
    separators: Optional[Tuple[str, str]] = None,
    default: Optional[Callable[[Any], Any]] = None,
    sort_keys: bool = False,
    quote_keys: bool = False,
    trailing_commas: bool = True,
    allow_duplicate_keys: bool = True,
    allow_custom_numbers: bool = True,
    quote_style: QuoteStyle = QuoteStyle.ALWAYS_DOUBLE,
    **kw,
):
    """Serialize ``obj`` to a JSON5-formatted stream to ``fp``,
    a ``.write()``-supporting file-like object.

    Supports the same arguments as ``dumps()``, below.

    Calling ``dump(obj, fp, quote_keys=True, trailing_commas=False, \
                   allow_duplicate_keys=True)``
    should produce exactly the same output as ``json.dump(obj, fp).``
    """

    fp.write(
        dumps(
            obj=obj,
            skipkeys=skipkeys,
            ensure_ascii=ensure_ascii,
            check_circular=check_circular,
            allow_nan=allow_nan,
            cls=cls,
            indent=indent,
            separators=separators,
            default=default,
            sort_keys=sort_keys,
            quote_keys=quote_keys,
            trailing_commas=trailing_commas,
            allow_duplicate_keys=allow_duplicate_keys,
            allow_custom_numbers=allow_custom_numbers,
            quote_style=quote_style,
            **kw,
        )
    )


def dumps(
    obj: Any,
    *,
    skipkeys: bool = False,
    ensure_ascii: bool = True,
    check_circular: bool = True,
    allow_nan: bool = True,
    cls: Optional['JSON5Encoder'] = None,
    indent: Optional[Union[int, str]] = None,
    separators: Optional[Tuple[str, str]] = None,
    default: Optional[Callable[[Any], Any]] = None,
    sort_keys: bool = False,
    quote_keys: bool = False,
    trailing_commas: bool = True,
    allow_duplicate_keys: bool = True,
    allow_custom_numbers: bool = False,
    quote_style: QuoteStyle = QuoteStyle.ALWAYS_DOUBLE,
    **kw,
):
    """Serialize ``obj`` to a JSON5-formatted string.

    Supports the same arguments as ``json.dumps()``, except that:

    - The ``encoding`` keyword is ignored; Unicode strings are always written.
    - By default, object keys that are legal identifiers are not quoted; if you
      pass ``quote_keys=True``, they will be.
    - By default, if lists and objects span multiple lines of output (i.e.,
      when ``indent`` >=0), the last item will have a trailing comma after it.
      If you pass ``trailing_commas=False``, it will not.
    - If you use a number, a boolean, or ``None`` as a key value in a dict, it
      will be converted to the corresponding JSON string value, e.g.  "1",
      "true", or "null". By default, ``dump()`` will match the `json` modules
      behavior and produce malformed JSON if you mix keys of different types
      that have the same converted value; e.g., ``{1: "foo", "1": "bar"}``
      produces '{"1": "foo", "1": "bar"}', an object with duplicated keys. If
      you pass ``allow_duplicate_keys=False``, an exception will be raised
      instead.
    - If `quote_keys` is true, then keys of objects will be enclosed in quotes,
      as in regular JSON. Otheriwse, keys will not be enclosed in quotes unless
      they contain whitespace.
    - If `trailing_commas` is false, then commas will not be inserted after the
      final elements of objects and arrays, as in regular JSON.  Otherwise,
      such commas will be inserted.
    - If `allow_duplicate_keys` is false, then only the last entry with a given
      key will be written. Otherwise, all entries with the same key will be
      written.
    - The standard `json` module will call intentionally call `int.__repr__`
      and `float.__repr__` to encode subclasses of ints and floats, even if the
      subclass had customized the __repr__. This kinda makes sense for JSON
      since there can more-or-less only be one representation of those kinds of
      numbers. JSON5 can support multiple versions (notably hexadecimal), and
      so it would be nice if it didn't. if `allow_custom_numbers` is true (it
      is false by default), the encoder will call obj.__repr__ instead of
      int.__repr__ or float.__repr__.  If you really want more fine-grained
      control over the conversion, you'll need to subclass the JSON5Encoder
      class. *`allow_custom_numbers` was added in version 0.10.0*.
    - `quote_style` controls how strings will be encoded. By default, for
      compatibility with the `json` module and older versions of `json5`,
      strings will always be double-quoted, and any double quotes in the string
      will be escaped. This is `QuoteStyle.ALWAYS_DOUBLE`.  If you pass
      `QuoteStyle.ALWAYS_SINGLE`, then strings will always be single-quoted,
      and any single quotes in the string will be escaped.  If you pass
      `QuoteStyle.PREFER_DOUBLE`, then the behavior is the same as
      ALWAYS_DOUBLE and strings will be double-quoted *unless*g the string
      contains double quotes (and not single quotes), in which case the string
      will be single-quoted.  If the string contains both single and double
      quotes, then the string will be double-quoted and the double quotes will
      be escaped.  If you pass `QuoteStyle.PREFER_SINGLE`, then the behavior is
      the same as ALWAYS_SINGLE and strings will be single-quoted *unless* the
      string contains double quotes (and not single quotes), in which case the
      string will be double-quoted. If the string contains both single and
      double quotes, the string will be single-quoted and single quotes in the
      string will be escaped. Strings that are being used as keys and that can
      pass as identifiers are not affected by this parameter. 
      *`quote_style` was added in version 0.10.0*.

    Other keyword arguments are allowed and will be passed to the
    encoder so custom encoders can get them, but otherwise they will
    be ignored in an attempt to provide some amount of forward-compatibility.

    Calling ``dumps(obj, quote_keys=True, trailing_commas=False, \
                    allow_duplicate_keys=True)``
    should produce exactly the same output as ``json.dumps(obj).``
    """

    cls = cls or JSON5Encoder
    enc = cls(
        skipkeys=skipkeys,
        ensure_ascii=ensure_ascii,
        check_circular=check_circular,
        allow_nan=allow_nan,
        indent=indent,
        separators=separators,
        default=default,
        sort_keys=sort_keys,
        quote_keys=quote_keys,
        trailing_commas=trailing_commas,
        allow_duplicate_keys=allow_duplicate_keys,
        allow_custom_numbers=allow_custom_numbers,
        quote_style=quote_style,
        **kw,
    )
    return enc.encode(obj)


class JSON5Encoder:
    def __init__(
        self,
        *,
        skipkeys: bool = False,
        ensure_ascii: bool = True,
        check_circular: bool = True,
        allow_nan: bool = True,
        indent: Optional[Union[int, str]] = None,
        separators: Optional[Tuple[str, str]] = None,
        default: Optional[Callable[[Any], Any]] = None,
        sort_keys: bool = False,
        quote_keys: bool = False,
        trailing_commas: bool = True,
        allow_duplicate_keys: bool = True,
        allow_custom_numbers: bool = False,
        quote_style: QuoteStyle = QuoteStyle.ALWAYS_DOUBLE,
        **kw,
    ):
        """Provides a class that may be overridden to customize the behavior
        of `dumps()`. The keyword args are the same as for that function."""
        # Ignore unrecognized keyword arguments in the hope of providing
        # some level of backwards- and forwards-compatibility.
        del kw

        self.skipkeys = skipkeys
        self.ensure_ascii = ensure_ascii
        self.check_circular = check_circular
        self.allow_nan = allow_nan
        self.indent = indent
        self.separators = separators
        if separators is None:
            if indent is None:
                self.item_separator, self.kv_separator = (', ', ': ')
            else:
                self.item_separator, self.kv_separator = (',', ': ')
        self.default_fn = default or _raise_type_error
        self.sort_keys = sort_keys
        self.quote_keys = quote_keys
        self.trailing_commas = trailing_commas
        self.allow_duplicate_keys = allow_duplicate_keys
        self.allow_custom_numbers = allow_custom_numbers
        self.quote_style = quote_style

    def default(self, obj: Any) -> Any:
        """Provides a last-ditch option to encode a value that the encoder
        doesn't otherwise recognize, by converting `obj` to a value that
        *can* (and will) be serialized by the other methods in the class.

        Note: this must not return a serialized value (i.e., string)
        directly, as that'll result in a doubly-encoded value."""
        return self.default_fn(obj)

    def encode(
        self,
        obj: Any,
        seen: Optional[Set] = None,
        level: int = 0,
        *,
        as_key: bool = False,
    ) -> str:
        """Returns an JSON5-encoded version of an arbitrary object. This can
        be used to provide customized serialization of objects. Overridden
        methods of this class should handle their custom objects and then
        fall back to super.encode() if they've been passed a normal object.

        `seen` is used for duplicate object tracking when `check_circular`
        is True. If `set` is None, it should be initialized to an empty
        set that is then passed to any recursive invocations of `encode`.

        `level` represents the current indentation level, which increases
        by one for each recursive invocation of encode (i.e., whenever
        we're encoding the values of a dict or a list).

        May raise `TypeError` if the object is the wrong type to be
        encoded (i.e., your custom routine can't handle it either), and
        `ValueError` if there's something wrong with the value, e.g.
        a float value of NaN when `allow_nan` is false.

        If `as_key` is true, the return value should be a double-quoted string
        representation of the object, unless obj is a string that can be an
        identifier (and quote_keys is false and obj isn't a reserved word).  If
        the object should not be used as a key (and you don't want to raise a
        TypeError), the method should return None, which will then allow the
        base implementation to implement `skipkeys` properly.
        """
        seen = seen or set()
        r = self._encode_basic_type(obj, as_key=as_key)
        if r is not None:
            return r
        if as_key:
            # Complex types can't be used as keys by default; a subclass
            # would have to override `encode(..., as_key=True)` to handle
            # them.
            return None
        return self._encode_non_basic_type(obj, seen, level)

    def _encode_basic_type(self, obj: Any, *, as_key: bool) -> str:
        if isinstance(obj, str):
            return self._encode_str(
                obj, as_key=as_key, quote_style=self.quote_style
            )

        # Check for True/False before ints because True and False are
        # also considered ints and so would be represented as 1 and 0
        # if we did ints first.
        if obj is True:
            return '"true"' if as_key else 'true'
        if obj is False:
            return '"false"' if as_key else 'false'
        if obj is None:
            return '"null"' if as_key else 'null'

        if isinstance(obj, int):
            s = repr(obj) if self.allow_custom_numbers else int.__repr__(obj)
            return f'"{s}"' if as_key else s

        if isinstance(obj, float):
            return self._encode_float(obj, as_key=as_key)
        return None

    def _encode_float(self, obj: float, *, as_key: bool) -> str:
        if obj == float('inf'):
            allowed = self.allow_nan
            s = 'Infinity'
        elif obj == float('-inf'):
            allowed = self.allow_nan
            s = '-Infinity'
        elif math.isnan(obj):
            allowed = self.allow_nan
            s = 'NaN'
        else:
            allowed = True
            s = repr(obj) if self.allow_custom_numbers else float.__repr__(obj)
        if not allowed:
            raise ValueError()
        return f'"{s}"' if as_key else s

    def _encode_str(
        self, obj: str, *, as_key: bool, quote_style: QuoteStyle
    ) -> str:
        if (
            as_key
            and self.is_identifier(obj)
            and not self.quote_keys
            and not self.is_reserved_word(obj)
        ):
            return obj

        quotes_seen = _QuotesSeen.NONE
        if quote_style in (QuoteStyle.ALWAYS_SINGLE, QuoteStyle.ALWAYS_DOUBLE):
            ret = []
            for ch in obj:
                encoded_ch, quotes_seen = self._encode_ch(
                    ch, quote_style, quotes_seen
                )
                ret.append(encoded_ch)
            if quote_style == QuoteStyle.ALWAYS_SINGLE:
                return "'" + ''.join(ret) + "'"
            else:
                return '"' + ''.join(ret) + '"'

        ret = []
        for ch in obj:
            encoded_ch, quotes_seen = self._encode_ch(
                ch, quote_style, quotes_seen
            )
            if quotes_seen == _QuotesSeen.BOTH:
                # If we get here, at least one of the characters wasn't
                # encoded correctly. To fix this, it's perhaps
                # easiest to just start over and force the needed style.
                if quote_style == QuoteStyle.PREFER_SINGLE:
                    return self._encode_str(
                        obj,
                        as_key=as_key,
                        quote_style=QuoteStyle.ALWAYS_SINGLE,
                    )
                else:
                    return self._encode_str(
                        obj,
                        as_key=as_key,
                        quote_style=QuoteStyle.ALWAYS_DOUBLE,
                    )
            ret.append(encoded_ch)
        if self._use_double_quotes(quotes_seen):
            return '"' + ''.join(ret) + '"'
        else:
            return "'" + ''.join(ret) + "'"

    def _encode_ch(
        self, ch: str, quote_style: QuoteStyle, quotes_seen: _QuotesSeen
    ) -> (str, _QuotesSeen):
        """Returns a tuple of a string and what kinds of quotes we've seen
        so far. The string is the `ch` if it doesn't need to be escaped,
        or the escaped version if it does."""
        if ch == '"':
            return self._encode_double_quote(quote_style, quotes_seen)
        if ch == "'":
            return self._encode_single_quote(quote_style, quotes_seen)

        o = ord(ch)
        if 32 <= o < 128 and ch != '\\':
            return ch, quotes_seen
        if o < 32:
            return self._escape_ch(ch), quotes_seen
        if ch == '\\':
            return self._escape_ch(ch), quotes_seen
        if not self.ensure_ascii and not (ch in ('\u2028', '\u2029')):
            return ch, quotes_seen
        return self._escape_ch(ch), quotes_seen

    def _encode_double_quote(
        self, quote_style: QuoteStyle, quotes_seen: _QuotesSeen
    ) -> str:
        quotes_seen |= _QuotesSeen.DOUBLE
        if (quote_style == QuoteStyle.ALWAYS_DOUBLE) or (
            quote_style == QuoteStyle.PREFER_DOUBLE
            and quotes_seen == _QuotesSeen.BOTH
        ):
            return self._escape_ch('"'), quotes_seen
        return '"', quotes_seen

    def _encode_single_quote(
        self, quote_style: QuoteStyle, quotes_seen: _QuotesSeen
    ) -> str:
        quotes_seen |= _QuotesSeen.SINGLE
        if (quote_style == QuoteStyle.ALWAYS_SINGLE) or (
            quote_style == QuoteStyle.PREFER_SINGLE
            and quotes_seen == _QuotesSeen.BOTH
        ):
            return self._escape_ch("'"), quotes_seen
        return "'", quotes_seen

    def _escape_ch(self, ch: str) -> str:
        """Returns the backslash-escaped representation of the char."""
        if ch == '\\':
            return '\\\\'
        if ch == "'":
            return r'\''
        if ch == '"':
            return r'\"'
        if ch == '\n':
            return r'\n'
        if ch == '\r':
            return r'\r'
        if ch == '\t':
            return r'\t'
        if ch == '\b':
            return r'\b'
        if ch == '\f':
            return r'\f'
        if ch == '\v':
            return r'\v'
        if ch == '\0':
            return r'\0'

        o = ord(ch)
        if o < 65536:
            return rf'\u{o:04x}'

        val = o - 0x10000
        high = 0xD800 + (val >> 10)
        low = 0xDC00 + (val & 0x3FF)
        return rf'\u{high:04x}\u{low:04x}'

    def _use_double_quotes(self, quotes_seen):
        if (
            self.quote_style == QuoteStyle.ALWAYS_DOUBLE
            or (
                self.quote_style == QuoteStyle.PREFER_DOUBLE
                and quotes_seen != _QuotesSeen.DOUBLE
            )
            or (
                self.quote_style == QuoteStyle.PREFER_SINGLE
                and quotes_seen == _QuotesSeen.SINGLE
            )
        ):
            return True
        return False

    def _encode_non_basic_type(self, obj, seen: Set, level: int) -> str:
        # Basic types can't be recursive so we only check for circularity
        # on non-basic types. If for some reason the caller was using a
        # subclass of a basic type and wanted to check circularity on it,
        # it'd have to do so directly in a subclass of JSON5Encoder.
        if self.check_circular:
            i = id(obj)
            if i in seen:
                raise ValueError('Circular reference detected.')
            seen.add(i)

        # Ideally we'd use collections.abc.Mapping and collections.abc.Sequence
        # here, but for backwards-compatibility with potential old callers,
        # we only check for the two attributes we need in each case.
        s = None
        if hasattr(obj, 'keys') and hasattr(obj, '__getitem__'):
            s = self._encode_dict(obj, seen, level + 1)
        elif hasattr(obj, '__getitem__') and hasattr(obj, '__iter__'):
            s = self._encode_array(obj, seen, level + 1)
        else:
            s = self.encode(self.default(obj), seen, level + 1, as_key=False)

        if self.check_circular:
            seen.remove(i)
        return s

    def _encode_dict(self, obj: Any, seen: set, level: int) -> str:
        if not obj:
            return '{}'

        indent_str, end_str = self._spacers(level)
        item_sep = self.item_separator + indent_str
        kv_sep = self.kv_separator

        if self.sort_keys:
            keys = sorted(obj.keys())
        else:
            keys = obj.keys()

        s = '{' + indent_str

        first_key = True
        new_keys = set()
        for key in keys:
            key_str = self.encode(key, seen, level, as_key=True)
            if key_str is None:
                if self.skipkeys:
                    continue
                raise TypeError(f'invalid key {repr(obj)}')

            if not self.allow_duplicate_keys:
                if key_str in new_keys:
                    raise ValueError(f'duplicate key {repr(key)}')
                new_keys.add(key_str)

            if first_key:
                first_key = False
            else:
                s += item_sep

            s += key_str + kv_sep + self.encode(obj[key], seen, level)

        s += end_str + '}'
        return s

    def _encode_array(self, obj: Any, seen: Set, level: int) -> str:
        if not obj:
            return '[]'

        indent_str, end_str = self._spacers(level)
        item_sep = self.item_separator + indent_str
        return (
            '['
            + indent_str
            + item_sep.join(self.encode(el, seen, level) for el in obj)
            + end_str
            + ']'
        )

    def _spacers(self, level: int) -> (str, str):
        if self.indent is not None:
            end_str = ''
            if self.trailing_commas:
                end_str = ','
            if isinstance(self.indent, int):
                if self.indent > 0:
                    indent_str = '\n' + ' ' * self.indent * level
                    end_str += '\n' + ' ' * self.indent * (level - 1)
                else:
                    indent_str = '\n'
                    end_str += '\n'
            else:
                indent_str = '\n' + self.indent * level
                end_str += '\n' + self.indent * (level - 1)
        else:
            indent_str = ''
            end_str = ''
        return indent_str, end_str

    def is_identifier(self, key: Optional[str]) -> bool:
        """Returns whether the string could be used as a legal
        EcmaScript/JavaScript identifier.

        There should normally be no reason to override this, unless
        the definition of identifiers change in later versions of the
        JSON5 spec and this implementation hasn't been updated to handle
        the changes yet."""
        if (
            not key
            or not self._is_id_start(key[0])
            and key[0] not in ('$', '_')
        ):
            return False
        for ch in key[1:]:
            if not self._is_id_continue(ch) and ch not in ('$', '_'):
                return False
        return True

    def _is_id_start(self, ch: str) -> bool:
        return unicodedata.category(ch) in (
            'Lu',
            'Ll',
            'Li',
            'Lt',
            'Lm',
            'Lo',
            'Nl',
        )

    def _is_id_continue(self, ch: str) -> bool:
        return unicodedata.category(ch) in (
            'Lu',
            'Ll',
            'Li',
            'Lt',
            'Lm',
            'Lo',
            'Nl',
            'Nd',
            'Mn',
            'Mc',
            'Pc',
        )

    def is_reserved_word(self, key: str) -> bool:
        """Returns whether the key is a reserved word.

        There should normally be no need to override this, unless there
        have been reserved words added in later versions of the JSON5
        spec and this implementation has not yet been updated to handle
        the changes yet."""
        global _reserved_word_re
        if _reserved_word_re is None:
            # List taken from section 7.6.1 of ECMA-262, version 5.1.
            # https://262.ecma-international.org/5.1/#sec-7.6.1.
            # This includes currently reserved words, words reserved
            # for future use (both as of 5.1), null, true, and false.
            _reserved_word_re = re.compile(
                '('
                + '|'.join(
                    [
                        'break',
                        'case',
                        'catch',
                        'class',
                        'const',
                        'continue',
                        'debugger',
                        'default',
                        'delete',
                        'do',
                        'else',
                        'enum',
                        'export',
                        'extends',
                        'false',
                        'finally',
                        'for',
                        'function',
                        'if',
                        'import',
                        'in',
                        'instanceof',
                        'new',
                        'null',
                        'return',
                        'super',
                        'switch',
                        'this',
                        'throw',
                        'true',
                        'try',
                        'typeof',
                        'var',
                        'void',
                        'while',
                        'with',
                    ]
                )
                + ')$'
            )
        return _reserved_word_re.match(key) is not None


def _raise_type_error(obj) -> Any:
    raise TypeError(f'{repr(obj)} is not JSON5 serializable')
