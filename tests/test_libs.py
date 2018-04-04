"""
unittest for pytest
"""
import io
import os
import platform
import re
import tempfile
import time

from tfs.libs import chdir, open_inout, timetracer


def test_chdir():
    # arrange
    orig_dir = os.path.abspath('.')
    dest_dir = tempfile.gettempdir()

    if platform.mac_ver()[0]:
        dest_dir = f'/private{dest_dir}'

    os.chdir(orig_dir)
    assert orig_dir == os.path.abspath(os.curdir)

    # act
    with chdir(dest_dir) as current_dir:
        assert dest_dir == current_dir
        assert dest_dir == os.path.abspath(os.curdir)

    # assert
    assert orig_dir == os.path.abspath(os.curdir)


def test_timetracer():
    # arrange
    file = io.StringIO()

    # act
    with timetracer('test', file):
        time.sleep(0.3)

    # assert
    file.seek(io.SEEK_SET)
    result = str(file.read()).strip()

    assert result
    r = re.match(r'[test] elapsed: .* seconds', result)
    pass


def test_open_inout():
    # arrange
    in_file = './test_open_input.txt'
    out_file = './test_open_input2.txt'

    with open(in_file, 'w', encoding='utf-8') as fp:
        fp.writelines(str(x) for x in range(10))

    try:
        # act
        # assert
        with open_inout(in_file, out_file) as (in_fp, out_fp):
            assert in_fp
            assert out_fp
            assert in_file == in_fp.name
            assert out_file == out_fp.name
            assert in_fp.mode == 'r'
            assert out_fp.mode == 'w'
    finally:
        if os.path.exists(in_file):
            os.unlink(in_file)
        if os.path.exists(out_file):
            os.unlink(out_file)
