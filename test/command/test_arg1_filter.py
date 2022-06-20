from master_validator.master_data import MasterDataManipulator, ComparisonInt


def test_arg1_filter(master_data: MasterDataManipulator, min_id):
    """
    テスト用フィルター
    idがmin_id以上のレコードを残す
    :return:
    """
    master_data.remove_lt('id', ComparisonInt(min_id))
    return master_data
