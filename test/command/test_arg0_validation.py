from sys import _getframe

from master_validator.master_data import MasterDataManipulator
from master_validator.parser import ValidationResult, RowsResult


def test_arg0_validation(master_data: MasterDataManipulator) -> ValidationResult:
    """
    テスト用バリデーション
    :return:
    """
    invalid_rows = []
    for row in master_data.all():
        dt = row.get_column_datetime('start_data')
        if dt.second != 0:
            invalid_rows.append(row)

    is_err = len(invalid_rows) >= 1
    result = RowsResult(is_err,
                        master_data.master_name,
                        _getframe().f_code.co_name,
                        'start_dataの秒が0秒になっていません。',
                        invalid_rows)
    return result
