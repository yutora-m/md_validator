import logging
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from master_validator.validator import validate_all


def main():
    CSV_DIR_PATH = './../master_data'
    result_list = validate_all(CSV_DIR_PATH)
    [logging.info(r.message()) for r in result_list if r.is_err]
    return


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    try:
        main()
    except Exception as e:
        logging.error(e)
        exit(1)
