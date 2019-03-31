# pyjson5

A Python implementation of the JSON5 data format.

[JSON5](https://json5.org) extends the
[JSON](http://www.json.org) data interchange format to make it
slightly more usable as a configuration language:

* JavaScript-style comments (both single and multi-line) are legal.

* Object keys may be unquoted if they are legal ECMAScript identifiers

* Objects and arrays may end with trailing commas.

* Strings can be single-quoted, and multi-line string literals are allowed.

There are a few other more minor extensions to JSON; see the above page for
the full details.

This project implements a reader and writer implementation for Python;
where possible, it mirrors the
[standard Python JSON API](https://docs.python.org/library/json.html)
package for ease of use.

This is an early release. It has been reasonably well-tested, but it is
**SLOW**. It can be 1000-6000x slower than the C-optimized JSON module,
and is 200x slower (or more) than the pure Python JSON module.

## Known issues

* Did I mention that it is **SLOW**?

* The implementation follows Python3's `json` implementation where
  possible. This means that the `encoding` method to `dump()` is
  ignored, and unicode strings are always returned.

* The `cls` keyword argument that `json.load()`/`json.loads()` accepts
  to specify a custom subclass of ``JSONDecoder`` is not and will not be
  supported, because this implementation uses a completely different
  approach to parsing strings and doesn't have anything like the
  `JSONDecoder` class.

* The `cls` keyword argument that `json.dump()`/`json.dumps()` accepts
  is also not supported, for consistency with `json5.load()`. The `default`
  keyword *is* supported, though, and might be able to serve as a 
  workaround.
