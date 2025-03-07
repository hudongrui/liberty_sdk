import re
from dataclasses import dataclass
from logging import getLogger

from .liberty_parser import LibertyGroup, LibertyAttribute, ComplexLibertyAttribute

logger = getLogger("main")


class Power(LibertyGroup):
    def __init__(self, group_type, template, index_1, values):
        self.group_type = group_type
        self.name = template,
        self.params = {}
        self.children = []

        self.children.append(ComplexLibertyAttribute(name="index_1", params=index_1))
        self.children.append(ComplexLibertyAttribute(name="values", params=values))


class Constraint(LibertyGroup):
    def __init__(self, group_type, template, index_1, index_2, values):
        self.group_type = group_type  # rise_constraint
        self.name = template
        self.params = {}
        self.children = []

        self.children.append(ComplexLibertyAttribute(name="index_1", params=index_1))
        self.children.append(ComplexLibertyAttribute(name="index_2", params=index_2))
        self.children.append(ComplexLibertyAttribute(name="values", params=values))


class TimingArc(LibertyGroup):
    def __init__(self, timing_type, sdf_cond, when_cond):
        self.group_type = "timing"
        self.name = ""
        self.params = {
            "related_pin": '"CLK"',
            "timing_type": timing_type,
            "sdf_cond": f"{sdf_cond}",
            "when_cond": f"{when_cond}"
        }
        self.children = []

    def set_children(self, slew_width, inslew, values_r, values_f):
        # This should be set at RUN-TIME
        # Pre-process values

        # Rise constraint
        self.children.append(Constraint(
            group_type="rise_constraint",
            template=f"constraint_template_{slew_width}x{slew_width}",
            index_1=inslew,
            index_2=inslew,
            values=values_r
        ))

        # Fall constraint
        self.children.append(Constraint(
            group_type="fall_constraint",
            template=f"constraint_template_{slew_width}x{slew_width}",
            index_1=inslew,
            index_2=inslew,
            values=values_f
        ))


class PowerArc(LibertyGroup):
    def __init__(self, related_pg_pin, when_cond):
        self.group_type = "internal_power"
        self.name = ""
        self.params = {
            "when": when_cond,
            "related_pg_pin": related_pg_pin
        }
        self.children = []

    def set_children(self, slew_width, inslew, values_r, values_f):
        # rise_power
        self.children.append(Power(
            group_type="rise_power",
            template=f"passive_power_template_{slew_width}x1",
            index_1=inslew,
            values=values_r
        ))

        # fall_power
        self.children.append(Power(
            group_type="fall_power",
            template=f"passive_power_template_{slew_width}x1",
            index_1=inslew,
            values=values_f
        ))
