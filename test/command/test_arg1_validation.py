from master_validator.master_data import MasterDataManipulator
from master_validator.parser import ValidationResult, RowsResult


def test_arg1_validation(master_data: MasterDataManipulator, min_count) -> ValidationResult:
    """
    テスト用バリデーション
    最低でもmin_count件のレコードがあるなら真
    :return:
    """
    is_err = master_data.count() < int(min_count)
    result = RowsResult(is_err=is_err, master_name=master_data.master_name)
    return result
