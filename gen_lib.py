from liberty_sdk.tools.logger import setup_logger
from liberty_sdk.parser.template_parser import *
# from liberty_sdk.parser.liberty_parser import LibertyParser, LibertyJSONEncoder

logger = setup_logger(log_file="parser.log")

# Variables
slew_width = 7
inslew = ["0.1, 0.2, 0.3, 1, 2, 3, 4"]
bus_pin = "D"
cell_name = "BNDATD585WS"
bus_from = 177

# Specify bus
bus_lib = LibertyGroup("bus", bus_pin)
bus_lib.set_params(
    bus_type=f"bus_{cell_name}_{bus_pin}_{bus_from}_0",
    direction="input",
)

# Test with Pin Q
pin_lib = LibertyGroup("pin", "D[0]")
pin_lib.set_params(
    direction="input",
    related_groud_pin="VDD",
    related_power_pin="VSS",
    capacitance=10235.5832745)

hr_timing = TimingArc("hold_rising", "ENCLK_TEST1", "TEST1")
hr_timing.set_children(
    slew_width=slew_width,
    inslew=inslew,
    values_r=["-0.0054047, -0.0054069, -0.005419, -0.0054162, -0.0054093, -0.0054414, -0.005493"],
    values_f=["-0.0054047, -0.0054069, -0.005419, -0.0054162, -0.0054093, -0.0054414, -0.005493"]
)

bus_lib.set_child(pin_lib)
bus_lib.set_child(hr_timing)

# Output Bus PIN
bus_pin = "Q"
POWER_PIN = "VDD"
GND_PIN = "VSS"

bus_lib = LibertyGroup("bus", bus_pin)
bus_lib.set_params(
    bus_type=f"bus_{cell_name}_{bus_pin}_{bus_from}_0",
    direction="output"
)

pin = LibertyGroup("pin", "Q[0]")
pin.set_params(
    power_down_function=f"(!{POWER_PIN}) + ({GND_PIN})",
    related_ground_pin=GND_PIN,
    related_power_pin=POWER_PIN,
    max_capacitance=125135.1146
)


# REF_HEADER.LIB
# TODO: Block comments
main_lib = LibertyGroup(f"{cell_name}_tt_0p75v_25c_rcbest_CCbest")


with open("tmp/test_gen.lib", "w") as f:
    f.write(bus_lib.dump())