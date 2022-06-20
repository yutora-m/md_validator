from abc import ABCMeta, abstractmethod
from importlib import import_module
from logging import error
from re import match
from typing import List

from master_validator.master_data import MasterDataManipulator


class ValidationResult(metaclass=ABCMeta):
    """
    バリデーションの結果を表示するための抽象基底クラス
    """

    def __init__(self, is_err=False, master_name='', validator_name='', err_msg=''):
        # エラーになったバリデータ名
        self._validator_name = validator_name
        # エラーメッセージ
        self._err_msg = err_msg
        self._master_name = master_name

        # バリデータの結果がエラーか。エラーならTrue
        self.is_err = is_err

    def message(self):
        """
        additional_msg()をオーバーライドして結果のメッセージを返すメソッドを実装する
        エラーではない場合は空文字を返す
        :return:
        """
        if not self.is_err:
            return ''

        return \
            f'master=<{self._master_name}> ' \
            f'validation=<{self._validator_name}> ' \
            f'error_message=<{self._err_msg}> ' \
            f'{self.additional_msg()}'

    @abstractmethod
    def additional_msg(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_error_data(self):
        raise NotImplementedError


class RowsResult(ValidationResult):
    """
    バリデーションの結果をマスターデータの行について表示するためのクラス
    """

    def __init__(self, is_err=False, master_name='', validator_name='', err_msg='', err_rows=None):
        super().__init__(is_err, master_name, validator_name, err_msg)

        # バリデータでエラーになったレコードを格納する
        if err_rows is None:
            err_rows = []
        self.err_rows = err_rows

    def additional_msg(self):
        """
        追加のエラー表示用の文字列を返す
        :return:
        """
        return f'error_master_data=<{self.err_rows}>'

    def get_error_data(self):
        return self.err_rows


class Context:
    """
    構文解析の状態を管理するクラス
    """

    def __init__(self, master_data: MasterDataManipulator, token_list: List[str], mod_path: str):
        """
        コンストラクタ
        :param master_data:
        :param token_list: トークンリスト
        :param mod_path: コマンドを読み込むモジュールパス
        """
        self._token_list = token_list
        self._it = iter(self._token_list)
        self._mod_path = mod_path

        # 初期値を先頭のトークンに進めておく
        self.current = next(self._it)
        self.master_data = master_data
        self.master_name = master_data.master_name
        self.result_info: ValidationResult = self.create_result()

    def nextToken(self):
        """
        次のトークンに進めてからその値を返す
        次のトークンが無い場合はNoneを返す
        :return:
        """
        self.current = next(self._it, None)
        return self.current

    def skipToken(self, token: str):
        """
        tokenと同値かチェックして同値なら次のトークンに進む
        :param token:
        :return:
        """
        if self.current != token:
            raise ValueError(f'current token = {self.current}, expect token = {token}')
        return self.nextToken()

    def isParsable(self):
        """
        現在値がまだ構文解析できるならTrue
        :return:
        """
        return self.current is not None

    def create_command(self, command_name: str):
        """
        command_nameに対応する関数を返す
        :param command_name:
        :return:
        """
        return get_cmd(self._mod_path, command_name)

    def create_result(self) -> ValidationResult:
        """
        マスターに対応するValidationResultの具象クラスのインスタンスを返す
        :return:
        """
        # INFO: 現在はRowsResultのみ対応
        return RowsResult()


class Node(metaclass=ABCMeta):
    """
    構文木のノードの抽象クラス
    このクラスを継承した各ノードクラスで解析と実行処理を実装する
    """

    @abstractmethod
    def parse(self, context: Context):
        """
        各ノードに対応した解析処理をオーバーライドする
        """
        raise NotImplementedError

    @abstractmethod
    def execute(self, c: Context):
        """
        構文木の各ノードを実行する
        :return:
        """
        raise NotImplementedError


class Validation(Node):
    """
    Validation ::= (Character | Number)+ "validation" Args
    Character ::= a | ... | z | A | ... | Z
    Number :== 0 | ... | 9
    """

    def __init__(self):
        self._validation_name = ''
        self._argNode = None
        self._command = None

    def parse(self, c: Context):
        if not match(r'[\S|\d]+validation', c.current):
            raise ValueError(c.current)
        self._validation_name = c.current
        self._command = c.create_command(self._validation_name)

        c.nextToken()
        self._argNode = Args()
        self._argNode.parse(c)

    def execute(self, c: Context):
        try:
            args = self._argNode.execute(c)
            c.result_info = self._command(c.master_data, *args)
        except Exception as e:
            error(f'call {self._command.__name__} error. args=[{args}]', exc_info=True, stack_info=True)
            raise e

    def __str__(self):
        return self._validation_name + str(self._argNode)


class ArgValue(Node):
    """
    ArgValue ::= (Character | Number)+
    Character ::= a | ... | z | A | ... | Z
    Number :== 0 | ... | 9
    """

    def __init__(self):
        self._value = None

    def parse(self, c: Context):
        if not match(r'[\S|\d]+', c.current):
            raise ValueError(c.current)

        self._value = c.current
        c.nextToken()

    def execute(self, c: Context):
        return self._value

    def __str__(self):
        return str(self._value)


class Args(Node):
    """
    Args ::= "(" ArgValue? | (ArgValue ("," ArgValue)*) ")"
    """

    def __init__(self):
        self._arg_value_list: List[Node] = []

    def parse(self, c: Context):
        c.skipToken('(')

        if c.current == ')':
            # 引数なしの場合
            c.nextToken()
            return

        while True:
            argValueNode = ArgValue()
            argValueNode.parse(c)
            self._arg_value_list.append(argValueNode)

            if c.current == ',':
                c.nextToken()
            elif c.current == ')':
                # 引数終わり
                c.nextToken()
                return
            else:
                raise ValueError(c.current)

    def execute(self, c: Context):
        return [value.execute(c) for value in self._arg_value_list]

    def __str__(self):
        return f'({", ".join(str(x) for x in self._arg_value_list)})'


class Filter(Node):
    """
    Filter ::= (Character | Number)+ "filter" Args
    Character ::= a | ... | z | A | ... | Z
    Number :== 0 | ... | 9
    """

    def __init__(self):
        self._fileterName = ''
        self._argNode = None
        self._command = None

    def parse(self, c: Context):
        if not match(r'[\S|\d]+filter', c.current):
            raise ValueError(c.current)
        self._fileterName = c.current
        self._command = c.create_command(self._fileterName)
        c.nextToken()

        self._argNode = Args()
        self._argNode.parse(c)

    def execute(self, c: Context):
        args = None
        try:
            args = self._argNode.execute(c)
            c.master_data = self._command(c.master_data, *args)
        except Exception as e:
            error(f'call {self._command.__name__} error. args=[{args}]', exc_info=True, stack_info=True)
            raise e

    def __str__(self):
        return self._fileterName + str(self._argNode)


class Validator(Node):
    """
    フィルターとバリデーションを合わせたものをバリデータと呼ぶ
    Validator ::= (Filter ">")+ Validation
    """

    def __init__(self):
        self._filterListNode: List[Node] = []
        self._validation = None

    def parse(self, c: Context):
        if not c.isParsable():
            raise Exception('current context is invalid error.')

        while match(r'[\S|\d]+filter', c.current):
            filterNode = Filter()
            filterNode.parse(c)
            self._filterListNode.append(filterNode)
            c.skipToken('>')

        self._validation = Validation()
        self._validation.parse(c)

        if c.isParsable():
            # 最後まできてもまだ解析可能な場合はエラー
            raise ValueError(f'Current token is {c.current}.')

    def execute(self, c: Context):
        """
        ノードに対応する処理を実行する
        :param c:
        :return:
        """
        for node in self._filterListNode:
            node.execute(c)
        self._validation.execute(c)

    def __str__(self):
        return f'{" > ".join(str(x) for x in self._filterListNode)} > {self._validation}'


def get_cmd(mod_name, command_name):
    """
    mod_nameモジュールからcommand_nameオブジェクトを取り出す
    """
    mod_path = f'{mod_name}.{command_name}'
    mod = _get_module(mod_path)
    try:
        callable_obj = getattr(mod, command_name)
        if not callable(callable_obj):
            error(f'[{callable_obj}] is not callable.', exc_info=True, stack_info=True)
            raise TypeError()
        return callable_obj
    except AttributeError as e:
        error(f'no callable object name [{command_name}].', exc_info=True, stack_info=True)
        raise e


def _get_module(mod_name):
    try:
        return import_module(f'{mod_name}')
    except ModuleNotFoundError as e:
        error(f'not found module. module=[{mod_name}]', exc_info=True, stack_info=True)
        raise e
