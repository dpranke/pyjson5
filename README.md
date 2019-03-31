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

## Version History / Release Notes

* v0.7 (2019-03-31)
    * Changes dump()/dumps() to not quote object keys by default if they are
      legal identifiers. Passing `quote_keys=True` will turn that off
      and always quote object keys.
    * Changes dump()/dumps() to insert trailing commas after the last item
      in an array or an object if the object is printed across multiple lines
      (i.e., if `indent` is not None). Passing `trailing_commas=False` will
      turn that off.
    * The `json5.tool` command line tool now supports the `--indent`,
      `--[no-]quote-keys`, and `--[no-]trailing-commas` flags to allow
      for more control over the output, in addition to the existing
      `--as-json` flag.
    * The `json5.tool` command line tool no longer supports reading from
      multiple files, you can now only read from a single file or
      from standard input.
    * The implementation no longer relies on the standard `json` module
      for anything. The output should still match the json module (except
      as noted above) and discrepancies should be reported as bugs.

* v0.6.2 (2019-03-08)
    * Fix [GitHub issue #23](https://github.com/dpranke/pyjson5/issues/23) and
      pass through unrecognized escape sequences.

* v0.6.1 (2018-05-22)
    * Cleaned up a couple minor nits in the package.

* v0.6.0 (2017-11-28)
    * First implementation that attempted to implement 100% of the spec.

* v0.5.0 (2017-09-04)
    * First implementation that supported the full set of kwargs that
      the `json` module supports.
