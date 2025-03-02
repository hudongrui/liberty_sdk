#!usr/bin/python3
import json
from liberty_sdk.tools.logger import setup_logger
from liberty_sdk.parser.liberty_parser import LibertyParser, LibertyJSONEncoder


logger = setup_logger(log_file="parser.log")

"""Parse"""
test_lib = 'test/test_cell.lib'
parser = LibertyParser(test_lib)
logger.info(f"Using {test_lib}")
library = parser.parse()
logger.info(f"Parse success. <{type(library)}>")

"""Lib2Json"""
output_json = 'test/test_cell.json'
with open(output_json, 'w') as f:
    json.dump(library, f, cls=LibertyJSONEncoder, indent=2)

"""LibClass2File"""
output_lib = 'test/output_cell.lib'
with open(output_lib, 'w') as f:
    f.write(library.dump(indent_value=True, indent_separator='  '))

# Generate Test
assert library.name == "cells"

# Test Simple Attribute
attr = library.get('voltage_unit')
logger.info(f"Test attribute 'voltage_unit': {attr}")
assert attr == '"1V"'

# Test Complex Attribute
attr = library.get('voltage_map')
logger.info(f"Test attribute: 'voltage_map': {attr}, type: {type(attr)}")
assert str(attr) == "[['VDD', '0.75'], ['VSS', '0'], ['GND', '0']]"

# Test nested complex attribute
pin = library.get(cell='DFF', pin='ADR[8]')
logger.info(f"Type of Pin: {type(pin)}")
logger.info(pin)
logger.info(pin.dump())

# Test other cases
template = library.get(lu_table_template='delay_temp_3x3')
logger.info(template)
idx = template.get("index_1")
logger.info(f"Test for index_1: {idx}")
# logger.info(idx.dump())
assert idx == '1.0, 2.0, 3.0'

# Test nested complex attribute
p = library.get(cell='AND2', pin='o', timing="", cell_rise="delay_temp_3x3")
# measure = p.get(timing="", cell_rise="delay_temp_3x3")
values = p.get("values")
logger.info(values)

# Test SET
library.set(comment="This is a comment")

# Set nested complex attributes
library.set(cell='AND2', pin='o', timing="", cell_rise="delay_temp_3x3", values="value set")