"""tool.py / host.py coverage for gaps in upstream tests/tool_test.py
and tests/host_test.py.

Upstream tool tests cover --help, -c, --indent, --as-json, quote-keys
flags, trailing-comma flags, stdin/file input, unknown switches and
--version. They do not cover --quote-style values, --strict /
--no-strict with a genuinely raw newline, --indent with a string of
spaces, or invalid --quote-style choices. Upstream host tests cover
only one directory/file round-trip and print(); the helpers below add
join, custom end, unicode round-trips, mkdtemp and rmtree-of-missing.

Tool tests reuse upstream's FakeHost (tests.host_fake) exactly as
tool_test.py does, so when these files are copied into the upstream
tests/ directory the import keeps working from the repository root.
All assertions were confirmed against the cloned source with a probe
script first.
"""

import io
import os

import pytest

import json5
from json5.host import Host
from json5.tool import main
from tests.host_fake import FakeHost


def run_tool(args, stdin=None, files=None):
    """Run tool.main against a FakeHost; return (code, stdout, stderr).

    Raises (not SystemExit) when the input document itself is invalid:
    tool.main does not catch ValueError from loads().
    """
    host = FakeHost()
    if stdin is not None:
        host.stdin.write(stdin)
        host.stdin.seek(0)
    if files:
        for path, contents in files.items():
            host.write_text_file(path, contents)
    code = main(args, host)
    return code, host.stdout.getvalue(), host.stderr.getvalue()


# ---------------------------------------------------------------------- tool

def test_tool_quote_style_always_single():
    _, out, _ = run_tool(['--quote-style', 'always_single', '-c', '{foo: "bar"}'])
    assert out == "{\n    foo: 'bar',\n}\n"


def test_tool_quote_style_prefer_double_flips_when_double_quotes_dominate():
    _, out, _ = run_tool(
        ['--quote-style', 'prefer_double', '-c', '{foo: "a\\"b"}']
    )
    assert out == "{\n    foo: 'a\"b',\n}\n"


def test_tool_strict_rejects_raw_newline_and_no_strict_allows_it():
    with pytest.raises(ValueError, match='Unexpected'):
        run_tool(['-c', '"a\nb"'])
    with pytest.raises(ValueError, match='Unexpected'):
        run_tool(['--strict', '-c', '"a\nb"'])
    code, out, _ = run_tool(['--no-strict', '-c', '"a\nb"'])
    assert code == 0
    assert out == '"a\\nb"\n'


def test_tool_indent_accepts_a_tab_string():
    _, out, _ = run_tool(['--indent', '\t', '-c', '[1,2]'])
    assert out == '[\n\t1,\n\t2,\n]\n'


def test_tool_indent_zero():
    _, out, _ = run_tool(['--indent', '0', '-c', '[1]'])
    assert out == '[\n1,\n]\n'


def test_tool_version_short_flag_matches_library_version():
    _, out, _ = run_tool(['-V'])
    assert out == json5.__version__ + '\n'


def test_tool_version_constants_agree():
    assert json5.VERSION == json5.__version__
    assert isinstance(json5.__version__, str)


def test_tool_as_json_on_nested_document():
    _, out, _ = run_tool(['--as-json', '-c', '{foo: 1, bar: [1,2]}'])
    assert out == '{\n    "foo": 1,\n    "bar": [\n        1,\n        2\n    ]\n}\n'


def test_tool_reads_commented_document_from_stdin():
    _, out, _ = run_tool([], stdin='{a: 1 /* c */}')
    assert out == '{\n    a: 1,\n}\n'


def test_tool_invalid_document_raises_instead_of_exiting():
    with pytest.raises(ValueError, match='Unexpected end of input'):
        run_tool(['-c', '{'])


def test_tool_invalid_quote_style_choice_exits_2():
    host = FakeHost()
    with pytest.raises(SystemExit) as exc_info:
        main(['--quote-style', 'bogus', '-c', '1'], host)
    assert exc_info.value.code == 2
    assert 'invalid choice' in host.stderr.getvalue()


# ---------------------------------------------------------------------- host

def test_host_join_and_absolute_join():
    host = Host()
    assert host.join('a', 'b', 'c') == 'a/b/c'
    assert host.join('/tmp', 'x') == '/tmp/x'


def test_host_getcwd_matches_os_getcwd():
    assert Host().getcwd() == os.getcwd()


def test_host_print_custom_end_and_empty_message():
    stream = io.StringIO()
    Host().print('hi', end='!', file=stream)
    assert stream.getvalue() == 'hi!'
    stream = io.StringIO()
    Host().print(file=stream)
    assert stream.getvalue() == '\n'


def test_host_unicode_file_round_trip(tmp_path):
    host = Host()
    path = str(tmp_path / 'unicode.txt')
    host.write_text_file(path, 'caf\u00e9')
    assert host.read_text_file(path) == 'caf\u00e9'


def test_host_mkdtemp_creates_a_real_directory():
    host = Host()
    path = host.mkdtemp()
    try:
        assert os.path.isdir(path)
    finally:
        host.rmtree(path)
    assert not os.path.exists(path)


def test_host_rmtree_of_missing_path_does_not_raise():
    Host().rmtree('/tmp/does-not-exist-pyjson5-xyz')
