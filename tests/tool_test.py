# Copyright 2017 Google Inc. All rights reserved.
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

import subprocess
import sys
import unittest

from json5 import __version__, VERSION
from json5.host import Host
from json5.tool import main

from tests.host_fake import FakeHost


class ToolTest(unittest.TestCase):
    maxDiff = None

    def _write_files(self, host, files):
        for path, contents in list(files.items()):
            host.write_text_file(path, contents)

    def check(
        self, args, stdin=None, files=None, returncode=0, out=None, err=None
    ):
        # We can run the tests two ways: as a full out-of-process integration
        # test (launching a subprocess and checking stdin/out/err) and as
        # a mocked-out in-process pseudo-integration test.
        #
        # The code coverage between the two is identical (excluding the
        # coverage in this file, of course). The full integration tests
        # are slower, and running `python -m coverage` won't account for
        # the coverage in the subprocess.
        #
        # For greatest coverage, by default we run the tests both ways.
        # TODO: If there was some convention for how to pass arguments from
        # a caller of the unittest module to this code, it would be nice
        # if we had command line args to toggle the two modes off and on.
        # Or, we could also figure out how to get the coverage in the
        # subprocess correctly accounted for.
        in_proc = True
        out_of_proc = True
        assert (
            in_proc or out_of_proc
        ), 'At least one of in_proc or out_of_proc must be true'

        if in_proc:
            fake_host = FakeHost()
            orig_wd = fake_host.getcwd()
            tmpdir = fake_host.mkdtemp()
            fake_host.chdir(tmpdir)

            fake_host.write_text_file('/tmp/foo', '')

            if stdin:
                fake_host.stdin.write(stdin)
                fake_host.stdin.seek(0)
            if files:
                self._write_files(fake_host, files)

            try:
                mock_ret = main(args, fake_host)
            except SystemExit as e:
                mock_ret = e.code

            fake_host.rmtree(tmpdir)
            fake_host.chdir(orig_wd)

            mock_out = fake_host.stdout.getvalue()
            mock_err = fake_host.stderr.getvalue()

            if returncode is not None:
                self.assertEqual(returncode, mock_ret)
            if out is not None:
                self.assertMultiLineEqual(out, mock_out)
            if err is not None:
                self.assertMultiLineEqual(err, mock_err)
        else:  # pragma: no cover
            pass

        if out_of_proc:
            host = Host()
            orig_wd = host.getcwd()
            tmpdir = host.mkdtemp()
            try:
                host.chdir(tmpdir)
                if files:
                    self._write_files(host, files)

                args = [sys.executable, '-m', 'json5'] + args
                with subprocess.Popen(
                    args,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding='utf-8',
                ) as proc:
                    actual_out, actual_err = proc.communicate(input=stdin)
                    actual_ret = proc.returncode
                if returncode is not None:
                    self.assertEqual(returncode, actual_ret)
                if out is not None:
                    self.assertMultiLineEqual(out, actual_out)
                if err is not None:
                    self.assertMultiLineEqual(err, actual_err)

            finally:
                host.rmtree(tmpdir)
                host.chdir(orig_wd)
        else:  # pragma: no cover
            pass

        if in_proc:
            return mock_ret, mock_out, mock_err

        return actual_ret, actual_out, actual_err  # pragma: no cover

    def test_help(self):
        self.check(['--help'])

        # Run again and ignore the error code just to get coverage of
        # the test code branches in check().
        self.check(['--help'], returncode=None)

    def test_inline_expression(self):
        self.check(['-c', '{foo: 1}'], out='{\n    foo: 1,\n}\n')

    def test_indent(self):
        self.check(['--indent=None', '-c', '[1]'], out='[1]\n')
        self.check(['--indent=2', '-c', '[1]'], out='[\n  1,\n]\n')
        self.check(['--indent=  ', '-c', '[1]'], out='[\n  1,\n]\n')

    def test_as_json(self):
        self.check(
            ['--as-json', '-c', '{foo: 1}'],
            out='{\n    "foo": 1\n}\n',
        )

    def test_quote_keys(self):
        self.check(
            ['--quote-keys', '-c', '{foo: 1}'],
            out='{\n    "foo": 1,\n}\n',
        )

    def test_no_quote_keys(self):
        self.check(
            ['--no-quote-keys', '-c', '{foo: 1}'],
            out='{\n    foo: 1,\n}\n',
        )

    def test_keys_are_quoted_by_default(self):
        self.check(['-c', '{foo: 1}'], out='{\n    foo: 1,\n}\n')

    def test_read_command(self):
        self.check(['-c', '"foo"'], out='"foo"\n')

    def test_read_from_stdin(self):
        self.check([], stdin='"foo"\n', out='"foo"\n')

    def test_read_from_a_file(self):
        files = {
            'foo.json5': '"foo"\n',
        }
        self.check(['foo.json5'], files=files, out='"foo"\n')

    def test_trailing_commas(self):
        self.check(
            ['--trailing-commas', '-c', '{foo: 1}'],
            out='{\n    foo: 1,\n}\n',
        )

    def test_no_trailing_commas(self):
        self.check(
            ['--no-trailing-commas', '-c', '{foo: 1}'],
            out='{\n    foo: 1\n}\n',
        )

    def test_trailing_commas_are_there_by_default(self):
        self.check(['-c', '{foo: 1}'], out='{\n    foo: 1,\n}\n')

    def test_unknown_switch(self):
        self.check(
            ['--unknown-switch'],
            returncode=2,
            err=(
                'usage: json5 [options] [FILE]\n'
                '    -h/--help for help\n'
                '\n'
                'error: unrecognized arguments: --unknown-switch\n'
            ),
        )

    def test_version(self):
        self.check(['--version'], out=str(VERSION) + '\n')
        self.check(['--version'], out=str(__version__) + '\n')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
