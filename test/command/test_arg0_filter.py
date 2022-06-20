from master_validator.master_data import MasterDataManipulator, ComparisonInt


def test_arg0_filter(master_data: MasterDataManipulator):
    """
    テスト用フィルター
    idが5より大きいレコードを消す
    """
    master_data.remove_gt('id', ComparisonInt('5'))
    return master_data
