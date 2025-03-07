from .liberty_parser import ParseError
from logging import getLogger

logger = getLogger("main")


class LibertyLinter:
    """
    ast = LibertyParser().parse_file()
    linter = LibertyLinter(ast)
    linter.run_checks()

    print(linter.generator_report())

    sys.exit(1 if linter.errors else 0)
    """
    def __init__(self, parsed_ast):
        self.ast = parsed_ast  # Abstract Syntax Tree
        self.errors = []
        self.warnings = []

    def add_diagnostics(self, level, code, msg, loc):
        entry = {
            "level": level,
            "code": f"{code}",  # error code
            "message": msg,
            "location": {
                "start_line": loc.start_line,
                "end_line": loc.end_line,
                "column": loc.start_column
            }
        }

        if level == "error":
            self.errors.append(entry)
        else:
            self.warnings.append(entry)

    @staticmethod
    def check_indentation(self, file_path):
        indent_stack = [0]  # 记录缩进级别栈
        for node in self.ast.walk_with_raw():  # 带原始行信息的遍历
            curr_indent = node.raw.leading_spaces

            if node.type == "block_close":  # 遇到}时缩进回退
                indent_stack.pop()
                expected = indent_stack[-1]
            else:
                expected = indent_stack[-1] + 4  # 默认4空格缩进

            if curr_indent != expected:
                self.add_diagnostic(
                    level="warning",
                    code="W202",
                    msg=f"缩进应为{expected}空格，实际为{curr_indent}",
                    loc=node.loc
                )

            if node.type == "block_open":  # 遇到{时压入新缩进级别
                indent_stack.append(expected)

        return True

    @staticmethod
    def check_bracket(self, file_path):
        stack = []
        return None

    @staticmethod
    def check_unit_consistency():
        unit_mapping = {}
        return None