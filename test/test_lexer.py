import os
from unittest import TestCase

from master_validator.lexer import analyze


class TestLexerMethods(TestCase):
    def test_analyze_lexical(self):
        test_cases = [
            {'name': 'valid case 01',
             'arg': 'test_arg0_filter() > test_arg1_filter()',
             'expect': ['test_arg0_filter', '(', ')', '>', 'test_arg1_filter', '(', ')']
             },
            {'name': 'valid case 02',
             'arg': 'test_arg0_filter()>test_arg1_filter()',
             'expect': ['test_arg0_filter', '(', ')', '>', 'test_arg1_filter', '(', ')']
             },
            {'name': 'valid case 03',
             'arg': 'test_arg0_filter()   >test_arg1_filter()',
             'expect': ['test_arg0_filter', '(', ')', '>', 'test_arg1_filter', '(', ')']
             },
            {'name': 'valid case 04',
             'arg': 'test_arg0_filter() > ValidateA(aaa, 123.4)',
             'expect': ['test_arg0_filter', '(', ')', '>', 'ValidateA', '(', 'aaa', ',', '123.4', ')']
             },
            {'name': 'valid case 05',
             'arg': f'{os.linesep}test_arg0_filter(){os.linesep}',
             'expect': ['test_arg0_filter', '(', ')']
             },
        ]
        for tc in test_cases:
            with self.subTest(tc['name']):
                self.assertEqual(tc['expect'], analyze(tc['arg']))

        exception_test_cases = [
            {'name': 'error case 01',
             'arg': '',
             'expect': ValueError
             },
            {'name': 'error case 02',
             'arg': ' ',
             'expect': ValueError
             },
            {'name': 'error case 03',
             'arg': f"{os.linesep}{os.linesep}",
             'expect': ValueError
             },
        ]
        for tc in exception_test_cases:
            with self.subTest(tc['name']):
                with self.assertRaises(tc['expect']):
                    analyze(tc['arg'])
