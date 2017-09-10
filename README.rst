pyjson5
=======

A Python implementation of the JSON5 data format.

`JSON5 <https://www.json5.org>`_ extends the `JSON <http://www.json.org>`_
data interchange format to make it more usable as a configuration language:

* JavaScript-style comments (both single and multi-line) are legal.

* Object keys may be unquoted if they are legal ECMAScript identifiers

* Objects and arrays may end with trailing commas.

* Strings can be single-quoted, and multi-line string literals are allowed.

There are a few other more minor extensions to JSON; see the above pages for
the full details.

This project implements a reader and writer implementation for Python;
mirroring the
`standard JSON package <https://docs.python.org/library/json.html>`_'s API.

Known issues
============

This is an early release. It has been well-tested and is feature-complete
(it implements the full JSON spec including proper handling of Unicode
identifiers, unlike even the reference JavaScript implementation), but it is
*SLOW*. It can be 1000-6000x slower than the C-optimized JSON module,
and is 200x slower (or more) than the pure Python JSON module.
