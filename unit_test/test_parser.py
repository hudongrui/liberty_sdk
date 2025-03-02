import os
import json
import unittest
from liberty_sdk.tools.logger import setup_logger
from liberty_sdk.parser.liberty_parser import LibertyParser, LibertyJSONEncoder, LibertyGroup

logger = setup_logger(log_file="unittest.log")

TEST_LIB = 'test/test_cell.lib'
TEST_DIR = 'tmp'


class ParserTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = LibertyParser(TEST_LIB)
        self.library = self.parser.parse()

    def test_readlib(self):
        assert isinstance(self.library, LibertyGroup)

    def test_dump_json(self):
        if not os.path.exists(TEST_DIR):
            os.makedirs(TEST_DIR)

        with open(f"{TEST_DIR}/parsed_lib.json", 'w') as f:
            json.dump(self.library, f, cls=LibertyJSONEncoder, indent=2)

    def test_dump_lib(self):
        if not os.path.exists(TEST_DIR):
            os.makedirs(TEST_DIR)

        with open(f"{TEST_DIR}/parsed_lib.lib", 'w') as f:
            f.write(self.library.dump(indent_value=True, indent_separator=' '))

    def test_parse_large_file(self):
        # TODO
        pass

    def test_get_values(self):
        # Test Simple Attribute
        attr = self.library.get('voltage_unit')
        assert attr == '"1V"'

        # Test Complex Attribute
        attr = self.library.get('voltage_map')
        logger.info(f"Test attribute: 'voltage_map': {attr}, type: {type(attr)}")
        assert str(attr) == "[['VDD', '0.75'], ['VSS', '0'], ['GND', '0']]"

        # Test nested complex attribute - 1
        pin = self.library.get(cell='DFF', pin='ADR[8]')
        logger.info(f"Test attribute: cell: 'DFF', pin: 'ADR[8]', retrived object: {type(pin)}")
        assert isinstance(pin, LibertyGroup)

        # Test nested complex attribute - 2
        template = self.library.get(lu_table_template='delay_temp_3x3')
        idx = template.get("index_1")
        assert idx == '1.0, 2.0, 3.0'

        # Test nested complex attribute - 3
        p = self.library.get(cell='AND2', pin='o', timing="", cell_rise="delay_temp_3x3")
        values = p.get("values")
        logger.info(values)
        assert values == ['0.1, 0.2, 0.3', '0.11, 0.21, 0.31', '0.12, 0.22, 0.32']

    # def test_set_values(self):
    #     # TODO
    #     comment_string = "This is a comment"
    #     self.library.set(comment=comment_string)
    #     assert self.library.get("comment") == comment_string
    #
    # def test_set_complex_attibutes(self):
    #     # TODO
    #     self.library.set(cell='AND2', pin='o', timing="", cell_rise="delay_temp_3x3", values="value set")


if __name__ == '__main__':
    unittest.main()