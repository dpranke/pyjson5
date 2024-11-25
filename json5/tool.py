# Copyright 2014 Google Inc. All rights reserved.
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

"""A tool to parse and pretty-print JSON5.

Usage:

    $ echo '{foo:"bar"}' | python -m json5.tool
    {
        foo: 'bar',
    }
    $ echo '{foo:"bar"}' | python -m json5.tool --as-json
    {
        "foo": "bar"
    }
"""

import argparse
import sys

from . import lib
from .host import Host
from .version import __version__


def main(argv=None, host=None):
    host = host or Host()

    usage = 'json5 [options] [FILE]\n'

    class CustomArgumentParser(argparse.ArgumentParser):
        def exit(self, status=0, message=None):
            if message:
                self._print_message(message, host.stderr)
            sys.exit(status)

        def error(self, message):
            host.print(f'usage: {usage}', end='', file=host.stderr)
            host.print('    -h/--help for help\n', file=host.stderr)
            self.exit(2, f'error: {message}\n')

        def print_help(self, file=None):
            host.print(self.format_help(), file=file)

    parser = CustomArgumentParser(
        prog='json5',
        usage=usage,
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '-V',
        '--version',
        action='store_true',
        help=f'show JSON5 library version ({__version__})',
    )
    parser.add_argument(
        '-c',
        metavar='STR',
        dest='cmd',
        help='inline json5 string to read instead of reading from a file',
    )
    parser.add_argument(
        '--as-json',
        dest='as_json',
        action='store_const',
        const=True,
        default=False,
        help='output as JSON (same as --quote-keys --no-trailing-commas)',
    )
    parser.add_argument(
        '--indent',
        dest='indent',
        default=4,
        help='amount to indent each line (default is 4 spaces)',
    )
    parser.add_argument(
        '--quote-keys',
        action='store_true',
        default=False,
        help='quote all object keys',
    )
    parser.add_argument(
        '--no-quote-keys',
        action='store_false',
        dest='quote_keys',
        help="don't quote object keys that are identifiers"
        ' (this is the default)',
    )
    parser.add_argument(
        '--trailing-commas',
        action='store_true',
        default=True,
        help='add commas after the last item in multi-line '
        'objects and arrays (this is the default)',
    )
    parser.add_argument(
        '--no-trailing-commas',
        dest='trailing_commas',
        action='store_false',
        help='do not add commas after the last item in '
        'multi-line lists and objects',
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        default=True,
        help='Do not allow control characters (\\x00-\\x1f) in strings '
        '(default)',
    )
    parser.add_argument(
        '--no-strict',
        dest='strict',
        action='store_false',
        help='Allow control characters (\\x00-\\x1f) in strings',
    )
    parser.add_argument(
        'file',
        metavar='FILE',
        nargs='?',
        default='-',
        help='optional file to read JSON5 document from; if '
        'not specified or "-", will read from stdin '
        'instead',
    )
    args = parser.parse_args(argv)

    if args.version:
        host.print(__version__)
        return 0

    if args.cmd:
        inp = args.cmd
    elif args.file == '-':
        inp = host.stdin.read()
    else:
        inp = host.read_text_file(args.file)

    if args.indent == 'None':
        args.indent = None
    else:
        try:
            args.indent = int(args.indent)
        except ValueError:
            pass

    if args.as_json:
        args.quote_keys = True
        args.trailing_commas = False

    obj = lib.loads(inp, strict=args.strict)
    s = lib.dumps(
        obj,
        indent=args.indent,
        quote_keys=args.quote_keys,
        trailing_commas=args.trailing_commas,
    )
    host.print(s)
    return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
