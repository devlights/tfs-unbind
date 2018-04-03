"""
TFSのプロジェクトバインディングを削除し、指定された場所に出力します。
元のプロジェクトに対しては変更は加えません。

使い方：
python unbinder.py 元フォルダ 先フォルダ

参考にした情報：
https://stackoverflow.com/questions/10028874/getting-unbound-solution-from-tfs
"""
import argparse
import logging
import os
import shutil
import stat
from typing import Tuple, List

from .libs import chdir, open_inout

# 不要なディレクトリの名前
unnecessary_dir_types = ('Debug', 'Release', 'StyleCop')
# 不要なファイルの拡張子
unnecessary_file_types = ('.vssscc', '.user', '.vspscc', '.pdb')


def unbind(orig_dir: str, dest_dir: str) -> None:
    """
    orig_dirをdest_dirにコピーした後、TFSのバインドを解除します。

    :param orig_dir: 元ディレクトリ
    :param dest_dir: 先ディレクトリ
    :return: なし
    """
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    logging.warning('開始')

    # 対象ディレクトリをコピー
    _copytree(orig_dir, dest_dir)

    with chdir(dest_dir) as current_dir:
        # 読み取り専用を解除
        _make_writeable(current_dir)

        # 処理対象となるディレクトリとファイルを収集
        del_dirs, del_files, sln_files, csproj_files = _collect(current_dir)

        # 不要なディレクトリとファイルを削除
        _delete(del_dirs, del_files)

        # ソリューションファイルからTFSのバインディングを除去
        _update_sln(sln_files)

        # csprojファイルからTFSのバインディングを除去
        _update_proj(csproj_files)

    logging.warning('完了')


def _copytree(orig_dir: str, dest_dir: str) -> None:
    """
    ディレクトリをコピーします。

    :param orig_dir: 元ディレクトリ
    :param dest_dir: 先ディレクトリ
    :return: なし
    """
    if not os.path.exists(dest_dir):
        logging.info('ファイルのコピーを開始します・・・・')
        shutil.copytree(orig_dir, dest_dir)


def _make_writeable(directory: str) -> None:
    """
    読み取り専用を解除します。

    :param directory: 対象ディレクトリ
    :return: なし
    """
    logging.info('読み取り専用を解除します・・・・')
    for dirpath, dirnames, filenames in os.walk(directory):
        for file_name in filenames:
            full_path = os.path.join(dirpath, file_name)
            if not os.access(full_path, os.W_OK):
                os.chmod(full_path, stat.S_IWRITE)


def _collect(directory: str) -> Tuple[List[str], List[str], List[str], List[str]]:
    """
    処理に必要な情報を収集します。

    :param directory: 対象ディレクトリ
    :return: タプル(削除対象ディレクトリリスト、削除対象ファイルリスト、ソリューションファイルリスト、プロジェクトファイルリスト)
    """
    logging.info('処理に必要な情報を収集します・・・・')

    del_dirs = []
    del_files = []
    sln_files = []
    proj_files = []

    for dirpath, dirnames, filenames in os.walk(directory):
        if dirpath.endswith(unnecessary_dir_types):
            del_dirs.append(dirpath)
        else:
            for fname in filenames:
                if fname.endswith(unnecessary_file_types):
                    del_files.append(os.path.join(dirpath, fname))

                if fname.endswith('.sln'):
                    sln_files.append(os.path.join(dirpath, fname))

                if fname.endswith('proj'):
                    proj_files.append(os.path.join(dirpath, fname))

    return del_dirs, del_files, sln_files, proj_files


def _delete(del_dirs: List[str], del_files: List[str]) -> None:
    """
    指定されたディレクトリとファイルを削除します。

    :param del_dirs: 削除対象ディレクトリリスト
    :param del_files: 削除対象ファイルリスト
    :return:
    """
    logging.info('不要ディレクトリとファイルを削除します・・・・')
    for del_dir in list(del_dirs):
        try:
            shutil.rmtree(del_dir)
        except FileNotFoundError as e:
            logging.warning(e)

    for file in list(del_files):
        try:
            os.unlink(file)
        except FileNotFoundError as e:
            logging.warning(e)


def _update_sln(sln_files: List[str]) -> None:
    """
    slnファイルを更新し、TFSとのバインディング部分を除去します。

    :param sln_files: ソリューションファイルリスト
    :return: なし
    """
    logging.info('slnファイルを更新します・・・・')
    for sln_file in sln_files:
        sln_file_new = f'{sln_file}.new'

        with open_inout(sln_file, sln_file_new) as (in_fp, out_fp):
            in_vcs_region = False
            for line in in_fp:
                stripped = line.strip()

                if stripped.startswith('GlobalSection') and 'VersionControl' in stripped:
                    in_vcs_region = True

                if not in_vcs_region:
                    out_fp.write(line)

                if in_vcs_region and 'EndGlobalSection' in stripped:
                    in_vcs_region = False

        shutil.copystat(sln_file, sln_file_new)
        shutil.move(sln_file_new, sln_file)


def _update_proj(proj_files: List[str]) -> None:
    """
    projファイルを更新し、TFSとのバインディング部分を除去します。

    :param proj_files: projファイルリスト
    :return: なし
    """
    logging.info('**projファイルを更新します・・・・')
    for proj_file in proj_files:
        proj_file_new = f'{proj_file}.new'

        with open_inout(proj_file, proj_file_new) as (in_fp, out_fp):
            for line in in_fp:
                stripped = line.strip()

                if not stripped.startswith('<Scc'):
                    out_fp.write(line)

        shutil.copystat(proj_file, proj_file_new)
        shutil.move(proj_file_new, proj_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('origdir', metavar='Orig', type=str, help='元ディレクトリ')
    parser.add_argument('destdir', metavar='Dest', type=str, help='先ディレクトリ')

    args = parser.parse_args()

    unbind(args.origdir, args.destdir)
