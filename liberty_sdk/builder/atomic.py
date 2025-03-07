from colorlog import getLogger

from ..parser.liberty_parser import LibertyGroup, LibertyAttribute, ComplexLibertyAttribute

logger = getLogger("main")


class ValueClause(LibertyGroup):
    def __init__(self, group_type, template, index_1=None, index_2=None, values=None):
        self.group_type = group_type
        self.name = template
        self.params = {}
        self.children = []  # List of Liberty Complex Attributes

        self.children.append(ComplexLibertyAttribute(name="index_1", params=index_1))
        if index_2:
            self.children.append(ComplexLibertyAttribute(name="index_2", params=index_1))

        self.children.append(ComplexLibertyAttribute(name="values", params=values))


class TimingArc(LibertyGroup):
    """
    An example Timing Simulation clause constructor.
    Create customized lib content following this style.
    """
    def __init__(self, timing_type, sdf_cond, when_cond):
        self.group_type = "timing"
        self.name = ""
        self.params = {
            "timing_type": timing_type,
            "sdf_cond": f"{sdf_cond}",
            "when": f'"{when_cond}"'
        }
        self.children = []

    def set_clause(self, template_name, inslew, values_rise, values_fall):
        # Rise constraint
        self.children.append(ValueClause(
            group_type="rise_constraint",
            template=template_name,
            index_1=inslew,
            values=values_rise
        ))

        # Fall constraint
        self.children.append(ValueClause(
            group_type="fall_constraint",
            template=template_name,
            index_1=inslew,
            values=values_fall
        ))
