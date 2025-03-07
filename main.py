#!usr/bin/python3
import json
from liberty_sdk.tools.logger import setup_logger
from liberty_sdk.parser.liberty_parser import LibertyParser, LibertyJSONEncoder

# For building custom LIB
from liberty_sdk.builder.liberty_builder import LibBuilder, atomic
from liberty_sdk.parser.liberty_parser import LibertyGroup

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

"""Build custom LIB"""


# subclass LibBuilder to your own Liberty-syntax clause builder
class PinBuilder(LibBuilder):
    """
    Based on certain template.lib
    """

    def build(self):
        # Get necessary variables from database
        self.lib = LibertyGroup("pin", self.name)
        self.lib.set_params(
            direction="input",
            related_ground_pin=self.db.get("GND_PIN"),
            related_power_pin=self.db.get("POWER_PIN"),
            max_transition=self.db.get("MAX_TRAN"),
        )

        clause = atomic.TimingArc(
            timing_type="hold_rising",
            sdf_cond=self.db.get("SDF_COND"),
            when_cond=self.db.get("WHEN_COND")
        )

        self.lib.set_child(clause)


# Prepare value dictionary
db = {
    "POWER_PIN": "VSS",
    "GND_PIN": "VDD",
    "MAX_TRAN": 0.125,
    "SDF_COND": "ENCLK",
    "WHEN_COND": "!ENCLK"
}
indent_level = 0  # Use this to control sub-clause/indentation.

builder = PinBuilder(
    name="CLK",
    db=db,
    reference="some_template_clk.lib"
)

with open('tmp/generated_lib.lib', 'w') as f:
    f.write(builder.dump(level=indent_level))
