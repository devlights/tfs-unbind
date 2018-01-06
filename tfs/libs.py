"""
共通モジュール
共通関数などが定義されています。
"""

import contextlib as ctx
import io
import os
import sys
from datetime import datetime
from typing import Generator, Optional, IO, Tuple, TextIO, Union


@ctx.contextmanager
def open_inout(in_file: str,
               out_file: str,
               in_enc: str = 'utf-8',
               out_enc: str = 'utf-8') -> Generator[Tuple[IO[str], IO[str]], None, None]:
    """
    指定した２つのファイルを片方は読み込み用、もう片方は書込み用で開きます。

    :param in_file: 入力用ファイルパス
    :param out_file: 出力用ファイルパス
    :param in_enc: 入力用ファイルのエンコーディング
    :param out_enc: 出力用ファイルのエンコーディング
    :return: 入力用ファイル、出力用ファイルのタプル
    """
    if not in_file or not out_file:
        raise ValueError('parameters must be set. [in_file, out_file]')
    if not in_enc or not out_enc:
        raise ValueError('parameters must be set. [in_enc, out_enc]')

    in_fp = open(in_file, mode='r', encoding=in_enc)
    out_fp = open(out_file, mode='w', encoding=out_enc)
    try:
        yield (in_fp, out_fp)
    finally:
        if in_fp:
            in_fp.close()
        if out_fp:
            out_fp.close()


@ctx.contextmanager
def chdir(directory: str = None) -> Generator[str, None, None]:
    """
    指定したディレクトリを一時的にカレントディレクトリに変更するコンテキストマネージャです。

    :param directory: 一時的にカレントディレクトリにするディレクトリ
    :return: 現在のカレントディレクトリ (yield の結果)
    """
    if directory is None or not os.path.exists(directory):
        raise ValueError('parameter: directory must be directory-path.')

    _orig_dir = os.path.abspath(os.path.curdir)
    try:
        os.chdir(directory)
        yield os.path.abspath(directory)
    finally:
        os.chdir(_orig_dir)


@ctx.contextmanager
def timetracer(message: Optional[str] = None,
               file: Optional[Union[TextIO, io.StringIO]] = None) -> Generator[None, None, None]:
    """
    処理の経過時間を出力するコンテキストマネージャです。

    :param message: メッセージ (デフォルトは [timetracer])
    :param file: 出力先 (デフォルトは sys.stdout)
    :return: なし
    """
    _start = datetime.now()
    try:
        yield
    finally:
        _diff = datetime.now() - _start
        _io = sys.stdout if file is None else file
        _message = 'timetracer' if message is None else message
        _log = f'[{_message}] elapsed: {_diff.seconds}.{_diff.microseconds} seconds'

        print(_log, file=_io)
