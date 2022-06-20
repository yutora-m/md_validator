"""
csvファイルからマスターデータを読み込むためのモジュール
"""
import csv
from logging import error
from pathlib import Path

from master_validator.master_data import MasterDataManipulator


def read_all(csv_path):
    """
    csv_path内のcsvファイルを全て読み込む
    :param csv_path:
    :return:
    """
    result = []
    try:
        # csvファイルが存在するか確認する
        Path(csv_path).glob('**/*.csv').__next__()
    except StopIteration as e:
        error('not found csv files.', exc_info=True, stack_info=True)
        raise e

    for path in Path(csv_path).glob('**/*.csv'):
        result.append(read_csv(path))
    return result


def read_csv(path: Path):
    """
    csvファイルを読み込む
    idカラムが存在する前提
    :param path:
    :return:
    """
    try:
        with open(path, newline='') as f:
            reader = csv.DictReader(f, quoting=csv.QUOTE_ALL)
            return MasterDataManipulator(reader, path.stem)
    except FileNotFoundError as e:
        error('file not found error.', exc_info=True, stack_info=True)
        raise e
