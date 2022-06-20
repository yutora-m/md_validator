from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Protocol


@dataclass(frozen=True)
class MasterRow:
    """
    マスタデータの1行を表すクラス。
    カラムの値の参照を扱う。
    idカラムは必須。
    """
    # INFO: マスターデータのレコードの方を変更したい場合はこの属性の型を変える。
    row: Dict

    def __post_init__(self):
        if 'id' not in self.row:
            raise KeyError('not exist id column error.')

    def get_pk(self):
        """
        INFO: 現在、主キーはidだけに対応している。
        :return:
        """
        try:
            return int(self.row['id'])
        except ValueError as e:
            raise e

    def get_column_int(self, column: str) -> int:
        try:
            return int(self.row[column])
        except ValueError as e:
            raise e

    def get_column_float(self, column: str) -> float:
        try:
            return float(self.row[column])
        except ValueError as e:
            raise e

    def get_column_datetime(self, column: str) -> datetime:
        try:
            return datetime.strptime(self.row[column], '%Y-%m-%d %X')
        except ValueError as e:
            raise e


class ValueComparisonProto(Protocol):
    """
    値の比較操作を扱うインターフェース
    """

    def eq(self, row: MasterRow, column: str) -> bool:
        """
        ==
        :param row:
        :param column:
        :return:
        """
        pass

    def gt(self, row: MasterRow, column: str) -> bool:
        """
        >
        :param row:
        :param column:
        :return:
        """
        pass

    def lt(self, row: MasterRow, column: str) -> bool:
        """
        <
        :param row:
        :param column:
        :return:
        """
        pass


class ComparisonInt:
    def __init__(self, value):
        self.value = int(value)

    def eq(self, row: MasterRow, column: str) -> bool:
        return row.get_column_int(column) == self.value

    def gt(self, row: MasterRow, column: str) -> bool:
        return self.value > row.get_column_int(column)

    def lt(self, row: MasterRow, column: str) -> bool:
        return self.value < row.get_column_int(column)


class ComparisonFloat:
    def __init__(self, value):
        self.value = float(value)


class MasterDataManipulator:
    """
    マスタをレコード単位で操作する責務を持つ
    """

    def __init__(self, master_data, master_name):
        self.master_name = master_name

        self._rows: Dict[int, MasterRow] = {}
        for row in master_data:
            master_row = MasterRow(row)
            self._rows[master_row.get_pk()] = master_row

    def all(self):
        """
        呼び出し元で変更出来ないようにvalues()の戻り値を返す
        :return:
        """
        return self._rows.values()

    def count(self):
        return len(self._rows)

    def find_by_pk(self, pk):
        return self._rows[pk]

    def remove_by_pk(self, pk):
        try:
            del self._rows[pk]
        except KeyError as e:
            raise e

    def remove_eq(self, column: str, value: ValueComparisonProto):
        """
        columnカラムの値 == value のレコードを削除
        :param column: 比較対象のカラム名
        :param value: 比較対象の値
        :return:
        """
        remove_row_pks = []
        for row in self._rows.values():
            if value.eq(row, column):
                remove_row_pks.append(row.get_pk())
        for pk in remove_row_pks:
            self.remove_by_pk(pk)

    def remove_not_eq(self, column: str, value: ValueComparisonProto):
        """
        columnカラムの値 != value のレコードを削除
        :param column: 比較対象のカラム名
        :param value: 比較対象の値
        :return:
        """
        remove_row_pks = []
        for row in self._rows.values():
            if not value.eq(row, column):
                remove_row_pks.append(row.get_pk())
        for pk in remove_row_pks:
            self.remove_by_pk(pk)

    def remove_gt(self, column: str, value: ValueComparisonProto):
        """
        columnカラムの値 > value のレコードを削除
        :param column:
        :param value:
        :return:
        """
        remove_row_pks = []
        for row in self._rows.values():
            if value.lt(row, column):
                remove_row_pks.append(row.get_pk())

        for pk in remove_row_pks:
            self.remove_by_pk(pk)

    def remove_lt(self, column: str, value: ValueComparisonProto):
        """
        columnカラムの値 < value のレコードを削除
        :param column:
        :param value:
        :return:
        """
        remove_row_pks = []
        for row in self._rows.values():
            if value.gt(row, column):
                remove_row_pks.append(row.get_pk())

        for pk in remove_row_pks:
            self.remove_by_pk(pk)

    def remove_ge(self, column: str, value: ValueComparisonProto):
        """
        columnカラムの値 >= value のレコードを削除
        :param column:
        :param value:
        :return:
        """
        self.remove_eq(column, value)
        self.remove_gt(column, value)

    def remove_le(self, column: str, value: ValueComparisonProto):
        """
        columnカラムの値 <= value のレコードを削除
        :param column:
        :param value:
        :return:
        """
        self.remove_eq(column, value)
        self.remove_lt(column, value)
