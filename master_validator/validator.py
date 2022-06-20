import logging
from pathlib import Path
from typing import List

from master_validator.csv_reader import read_all
from master_validator.lexer import lexer
from master_validator.master_data import MasterDataManipulator
from master_validator.parser import Context, Validator, ValidationResult


def read_validator_file(name):
    """
    バリデータの内容をファイルから読み込む
    :param name: validatorフォルダ内の拡張子なしファイル名を指定
    :return: ファイルの中身の文字列
    """
    try:
        path = Path('./validator')
        path = path.joinpath(name)
        path = path.with_suffix('.txt')
        with open(path, newline='') as f:
            result = f.readlines()
    except Exception as e:
        logging.error(f'error [{e}]', exc_info=True, stack_info=True)
        raise e

    return result


def exec_validator(master_data: MasterDataManipulator, validator_str) -> ValidationResult:
    """
    validator_strに含まれるコマンドを順次実行する。
    コマンドはcommandモジュールフォルダ内のものが実行される。
    :param master_data: マスターデータ
    :param validator_str: コマンド列の文字列
    :return:
    """
    logging.debug(master_data.all())

    token_list = lexer(validator_str)
    c = Context(master_data, token_list, 'master_validator.command')
    validator = Validator()
    validator.parse(c)
    validator.execute(c)

    logging.debug(f'{c.master_data.all()}')

    return c.result_info


def validate(master_data: MasterDataManipulator) -> List[ValidationResult]:
    """
    マスタに対応するバリデータを実行する。
    :param master_data:
    :return:
    """
    result_list = []
    validator_str_list = read_validator_file(master_data.master_name)
    for validator_str in validator_str_list:
        result = exec_validator(master_data, validator_str)
        result_list.append(result)
    return result_list


def validate_all(csv_dir_path) -> List[ValidationResult]:
    """
    全てのバリデータを実行する。
    csv_dir_pathディレクトリにあるcsvフォーマットのマスターデータを読み込み、validatorディレクトリ内のバリデータファイルを実行する。
    csvファイル名と同じバリデータファイルが実行される。
    :param csv_dir_path:
    :return:
    """
    result_list: List[ValidationResult] = []
    for master_data in read_all(csv_dir_path):
        logging.debug('csv file = ' + master_data.master_name)
        # CSVファイル名 == マスター名としている
        result_list += validate(master_data)

    return result_list
