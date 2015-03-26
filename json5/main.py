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

import fileinput
import json
import os
import sys

from json5 import lib
from json5.host import Host
from json5.arg_parser import ArgumentParser
from json5.version import VERSION


def main(argv=None, host=None, **defaults):
    host = Host()
    parser = ArgumentParser(host)
    args = parser.parse_args(argv)
    if parser.exit_status is not None:
        return parser.exit_status

    if args.version:
        host.print_(VERSION)

    if args.cmd:
        inp = args.cmd
    else:
        inp = '\n'.join(fileinput.input(args.files))
    host.print_(lib.dumps(lib.loads(inp)))
    return 0


if __name__ == '__main__':  # pragma: no cover
    sys.modules['__main__'].__file__ = path_to_file
    sys.exit(main(sys.argv[1:])[0])
