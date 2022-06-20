from shlex import shlex

from typing import List


def lexer(cmd: str) -> List[str]:
    """
    cmdを有効なトークンに分割する
    """
    result = analyze(cmd)
    if invalid_tokens(result):
        raise ValueError('ERROR: invalid tokens.')
        pass
    return result


def analyze(cmd: str) -> List[str]:
    """
    cmdを字句解析する
    """
    if cmd.isspace() or not cmd:
        raise ValueError('ERROR: cmd is empty.')

    sh_lexer = shlex(cmd, posix=True, punctuation_chars=False)
    sh_lexer.wordchars += '.'
    result = []
    while (token := sh_lexer.get_token()) != sh_lexer.eof:
        result.append(token)
    return result


def invalid_tokens(tokens: List[str]) -> List[str]:
    """
    TODO: 有効なトークンか確認する
    無効なトークンのリストを返す
    """
    # 記号のチェック 許可されている記号 ()>.,
    # 識別子を正規表現でチェック
    return []
