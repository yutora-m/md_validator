from master_validator.master_data import MasterDataManipulator, ComparisonInt


def equal_filter(master_data: MasterDataManipulator, column: str, value: str):
    """
    同値フィルター
    :param master_data: フィリター対象のマスタデータ
    :param column: 比較するカラム名
    :param value: 比較する値
    :return:
    """
    master_data.remove_not_eq(column, ComparisonInt(value))
    return master_data
