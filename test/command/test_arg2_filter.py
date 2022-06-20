from master_validator.master_data import MasterDataManipulator, ComparisonInt


def test_arg2_filter(master_data: MasterDataManipulator, arg1, arg2):
    """
    テスト用フィルター
    idがarg1以上arg2未満のレコードを残す
    arg1 <= id < arg2
    :return:
    """
    if arg1 >= arg2:
        raise ValueError(f'引数arg2({arg2})はarg1({arg1})より大きい値を指定してください.')

    master_data.remove_lt('id', ComparisonInt(arg1))
    master_data.remove_ge('id', ComparisonInt(arg2))
    return master_data
