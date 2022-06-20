from master_validator.master_data import MasterDataManipulator
from master_validator.parser import ValidationResult, RowsResult


def count_validation(master_data: MasterDataManipulator, min_count: str) -> ValidationResult:
    """
    最低でもmin_count件のレコードがあるなら真
    :return:
    """
    is_err = master_data.count() < int(min_count)
    result = RowsResult(is_err,
                        master_name=master_data.master_name,
                        validator_name=count_validation.__name__,
                        err_msg=f'{min_count}件以上のレコードがありません。{master_data.count()}件')

    return result
