from pathlib import Path
from unittest import TestCase

from master_validator.csv_reader import read_csv
from master_validator.parser import Validator, Context


class TestPaser(TestCase):
    def test_parse(self):
        test_data_path = Path('fixtures/character/character_test.csv')
        master = read_csv(test_data_path)
        test_cases = [
            {'name': '引数0個',
             'args': {
                 "token": ['test_arg0_filter', '(', ')', '>', 'test_arg0_validation', '(', ')'],
                 "master": read_csv(test_data_path),
             },
             'expect': {
                 'parse': 'test_arg0_filter() > test_arg0_validation()',
                 'error_rows': [master.find_by_pk(1)],
                 'is_error': True
             },
             },
            {'name': '引数1個',
             'args': {
                 "token": ['test_arg1_filter', '(', '2', ')', '>', 'test_arg1_validation', '(', '6', ')'],
                 "master": read_csv(test_data_path),
             },
             'expect': {
                 'parse': 'test_arg1_filter(2) > test_arg1_validation(6)',
                 'error_rows': [],
                 'is_error': True
             },
             },
            {'name': '引数2個',
             'args': {
                 'token': ['test_arg2_filter', '(', '4', ',', '7', ')', '>', 'test_arg0_validation', '(', ')'],
                 "master": read_csv(test_data_path),
             },
             'expect': {
                 'parse': 'test_arg2_filter(4, 7) > test_arg0_validation()',
                 'error_rows': [master.find_by_pk(6)],
                 'is_error': True
             }
             },
        ]

        for tc in test_cases:
            with self.subTest(tc['name']):
                c = Context(tc['args']['master'], tc['args']['token'], 'test.command')
                validator = Validator()

                validator.parse(c)
                self.assertEqual(str(validator), tc['expect']['parse'])

                validator.execute(c)
                self.assertEqual(c.result_info.get_error_data(), tc['expect']['error_rows'])
                self.assertEqual(c.result_info.is_err, tc['expect']['is_error'])
