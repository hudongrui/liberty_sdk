import json
import logging
import colorlog
from parser.liberty_parser import LibertyParser, LibertyJSONEncoder


def setup_logger(log_file, level=logging.DEBUG):
    stdout_handler = colorlog.StreamHandler()
    stdout_handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s [%(asctime)s] | %(levelname)s | %(message)s', "%Y-%m-%d %H:%M:%S"))
    # stdout_handler.setLevel(level)

    file_handler = logging.FileHandler(log_file, mode='w+')
    formatter = logging.Formatter('[%(asctime)s] | %(levelname)s | %(message)s', "%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(formatter)
    # file_handler.setLevel(level)

    logger = logging.getLogger("main")
    logger.handlers.clear()
    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)
    logger.setLevel(level)

    return logger


logger = setup_logger(log_file="parser.log")

test_lib = 'test/test_cell.lib'
parser = LibertyParser(test_lib)
logger.info(f"Using {test_lib}")
library = parser.parse()
logger.info(f"Parse success. <{type(library)}>")

output_json = 'test/test_cell.json'
with open(output_json, 'w') as f:
    json.dump(library, f, cls=LibertyJSONEncoder, indent=2)

assert library.name == "cells"