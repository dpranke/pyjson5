pyjson5
=======

A Python implementation of the JSON5 data format.

`JSON5 <https://github.com/aseemk/json5>`_ extends the
`JSON <http://www.json.org>`_ data interchange format to make it
slightly more usable as a configuration language:

* JavaScript-style comments (both single and multi-line) are legal.

* Object keys may be unquoted if they are legal JavaScript field names.

* Objects and arrays may end with trailing commas.

* Strings can be single-quoted, and multi-line string literals are allowed.

There are a few other more minor extensions to JSON; see the above page for
the full details.

This project implements a reader and writer implementation for Python;
where possible, it mirrors the
`standard Python JSON API <https://docs.python.org/library/json.html>`_
for ease of use.

This is an early release. It is not well-tested, and has not been tuned
for performance.
