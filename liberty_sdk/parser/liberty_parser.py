import dataclasses
import json
import re
from enum import Enum
from logging import getLogger
from functools import lru_cache
from typing import Dict, List, Optional
from dataclasses import dataclass, field

logger = getLogger("main")


class LibertyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if not isinstance(o, (LibertyGroup, LibertyAttribute, ComplexLibertyAttribute)):
            raise AssertionError('Unsupported Liberty Class Format')
        else:
            return o.asdict()
            # return dataclasses.asdict(o)   # Ordinary Class
        return super().default(o)


class ParseError(Exception):
    def __init__(self, msg, line=None):
        super().__init__(f"Line {line}: {msg}" if line else msg)


def indent(level=0, separator='  '):
    indentation = ''
    for _ in range(level):
        indentation += separator
    return indentation


def list2dict(l):
    """
    Convert a list of kv-pairs to dict. Such as:
    [{"cell": "AND2"}, {"pin": "o"}] -> {{"cell": "AND2"}, {"pin": "o"}}
    """
    d = {}
    for kv_pair in l:
        d.update(kv_pair)

    return d


def dict2list(d):
    """
    Convert dict (kwargs) to a list of kv-pairs
    """
    kv_pairs = []
    for k, v in d.items():
        kv_pairs.append({k: v})

    return kv_pairs


class TokenType(Enum):
    IDENTIFIER = 1
    STRING = 2
    NUMBER = 3
    SYMBOL = 4
    KEYWORD = 5


@dataclass
class LibertyToken:
    type: TokenType
    value: str
    line: int


@dataclass
class LibertyAttribute:
    """Simple Attribute"""
    name: str
    value: str

    def __hash__(self):
        return hash(repr(self))

    def get(self):
        return self.value

    def match(self, k):
        return self.name == k

    def dump(self, level=0, indent_value=True, indent_separator='  '):
        data = f"{indent(level=level, separator=indent_separator)}{self.name}: ("
        if self.name == "values" and indent_value:  # For certain attributes, indent
            data += f" \\\n{indent(level=level+1, separator=indent_separator)}\"{self.value}\" \\\n{indent(level=level, separator=indent_separator)});\n"
        else:
            data += f"\"{self.value}\");\n"

        return data

    @lru_cache(maxsize=1024)
    def asdict(self):
        return self.value


@dataclass
class ComplexLibertyAttribute:
    """Complex Attribute"""
    name: str
    params: List[str] = field(default_factory=list)

    def set_values(self, values):
        self.params = values

    def __hash__(self):
        return hash(repr(self))

    def __repr__(self):
        return f"{self.name}: ({', '.join(self.params)})"

    def get(self):
        return self.params

    def match(self, k, v=None):
        return self.name == k

    def dump(self, level=0, indent_value=True, indent_separator='  '):
        data = f"{indent(level=level, separator=indent_separator)}{self.name} ("

        # Value section
        if self.name == 'values' and indent_value is True:
            data += f" \\\n{indent(level=level+1, separator=indent_separator)}"
            params = list(map(lambda x: f'"{x}"', self.params))
            data += f", \\\n{indent(level=level+1, separator=indent_separator)}".join(params)
            data += f"\\\n{indent(level=level, separator=indent_separator)}"
        else:
            data += ", ".join(self.params)
        data += ");\n"

        return data

    @lru_cache(maxsize=1024)
    def asdict(self):
        return self.params


@dataclass
class LibertyGroup:
    group_type: str
    name: str
    params: Dict[str, str] = field(default_factory=dict)  # Simple Attribute
    children: List['LibertyGroup'] = field(default_factory=list)  # LibertyGroup or Complex Attribute

    def __hash__(self):
        return hash(repr(self))

    def dump(self, level=0, indent_value=True, indent_separator='  '):
        data = f"{indent(level=level, separator=indent_separator)}{self.group_type} ({self.name}) {{\n"
        for k, v in self.params.items():
            data += f"{indent(level=level + 1, separator=indent_separator)}{k}: {v};\n"

        for child in self.children:
            data += child.dump(
                level=level + 1,
                indent_value=indent_value,
                indent_separator=indent_separator)

        data += f"{indent(level=level, separator=indent_separator)}}}\n"
        return data

    def match(self, k, v=None):
        if v:
            return self.group_type == k and self.name == v
        else:
            return self.group_type == k

    @lru_cache(maxsize=1024)
    def get(self, *args, **kwargs):
        if args:
            # TODO: Support arg list later.
            # if len(args) > 1:
            #     value_list = []
            #     for k in args:
            #         # self.params - Simple Attribute
            #         value_list.append(self.params.get(k))
            #     return value_list
            # else:
            key = args[0]
            if not self.params.get(key):
                # Liberty Group
                value_list = []
                for child in self.children:
                    if child.match(key):
                        value_list.append(child.get())
                return value_list[0] if len(value_list) == 1 else value_list
            else:
                # Simple Liberty attribute
                return self.params.get(args[0])
        if kwargs:
            # logger.info(kwargs)
            for child in self.children:
                k0 = dict2list(kwargs)[0]
                for k, v in k0.items():
                    if child.match(k, v):
                        # logger.debug(f"Found item with current key: {k0}")
                        k1 = dict2list(kwargs)[1:]
                        # logger.debug(f"Using rest of key: {list2dict(k1)}")
                        return child.get(**list2dict(k1))

        return self

    @lru_cache(maxsize=1024)
    def asdict(self):
        data = {}

        # Group Type
        data['type'] = self.group_type
        data['name'] = self.name
        # data[self.group_type] = self.name

        # Simple Attributes
        for k, v in self.params.items():
            data[k] = v

        # Complex Attributes
        for g in self.children:
            if isinstance(g, (LibertyAttribute, ComplexLibertyAttribute)):
                data[g.name] = g.asdict()
            elif isinstance(g, LibertyGroup):
                # using special separator as values
                if 'group' not in data.keys():
                    data['group'] = []
                data['group'].append(g.asdict())
                # instance_name = f"#&#{g.group_type}#&#{g.name}"  # Use unique name as key
                # data[instance_name] = g.asdict()
            else:
                raise ParseError(f"Unrecognized data type: {type(g)}")

        return data


class LibertyParser:
    TOKEN_REGEX = re.compile(r"""
        (?P<keyword>\b(?:library|cell|pin|direction|timing|related_pin|cell_rise|values)\b) |
        (?P<string>"[^"]*") |
        (?P<number>[-+]?\d+\.?\d*) |
        (?P<symbol>[(){},:;\[\]]) |
        (?P<identifier>\w+)
    """, re.VERBOSE)

    def __init__(self, file_path):
        """
        Liberty File parser
        Args:
            file_path:
        """
        self.file_path = file_path
        self.tokens: List[LibertyToken] = []
        self.current_token = 0

    def parse(self) -> LibertyGroup:
        """
        Main Parsing Function
        :return: <class 'LibertyGroup'>
        """
        self._tokenize()
        return self._parse_group()

    def _tokenize(self):
        is_comment = False
        with open(self.file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.split('//')[0].strip()  # Skip inline comments

                # SKIP block comment
                if is_comment:
                    continue

                if line.strip().startswith('/*'):
                    is_comment = True
                    if line.strip().endswith('*/'):
                        is_comment = False
                    continue

                if line.strip().startswith('*/'):
                    is_comment = False
                    continue

                for match in self.TOKEN_REGEX.finditer(line):
                    groups = match.groupdict()
                    if groups['keyword']:
                        self.tokens.append(LibertyToken(TokenType.KEYWORD, groups['keyword'], line_num))
                    elif groups['string']:
                        self.tokens.append(LibertyToken(TokenType.STRING, groups['string'][1:-1], line_num))
                    elif groups['number']:
                        self.tokens.append(LibertyToken(TokenType.NUMBER, groups['number'], line_num))
                    elif groups['symbol']:
                        self.tokens.append(LibertyToken(TokenType.SYMBOL, groups['symbol'], line_num))
                    elif groups['identifier']:
                        self.tokens.append(LibertyToken(TokenType.IDENTIFIER, groups['identifier'], line_num))

    def _parse_value(self, value=[]) -> list:
        """
        Parse Complex Attibute values with the following format:
            attribute_name (param1, [param2, param3 ...] );
        :param value:
        :return:
        """
        self._advance()
        self._advance()  # Skip Line break "\"

        if self._peek().value == ')':
            value.append(self._current().value)
            self._advance()
            self._consume(')')
            self._consume(';')
            return value

        elif self._peek().value == ',':  # Value list continues
            value.append(self._current().value)
            return self._parse_value(value)

    def _parse_group(self) -> LibertyGroup:
        group_type = self._current().value  # Such as "cell"

        self._advance()
        self._consume('(')

        # LibertyGroup clause w/ name
        name = self._current().value  # Such as "AND2X1"

        if name == ')':  # Such as timing(), which name is EMPTY
            name = ""
            self._advance()
        elif self._peek().value == ',':  # Begin to parse value list
            attr = ComplexLibertyAttribute(group_type)
            attr.set_values(self._parse_value([self._current().value]))
            logger.debug(f"Parsed ComplexAttribute: {attr}")
            return attr
        elif self._peek().value == '[':  # Begin to parse pin, such as ADR[8]
            self._advance()
            name += self._current().value  # Add '['
            # logger.info(f"{self._current().value}, Next: {self._peek().value}, Peek: {self._peek()}")
            while self._peek().value != ']':
                self._advance()
                name += self._current().value
            self._advance()
            name += self._current().value  # Add ']'
            # Done parsing PIN name, procede as normal
            self._advance()
            self._consume(')')
        else:
            self._advance()
            self._consume(')')

        try:
            self._consume('{')
        except ParseError:
            self._consume(';')
            attr = LibertyAttribute(group_type, name)
            logger.debug(f"Parsed attribute: {attr}")
            return attr

        group = LibertyGroup(group_type, name)
        while self._current().value != '}':
            if self._peek().value == '(':
                # Group statements OR complex attributes
                group.children.append(self._parse_group())
            else:
                key = self._current().value
                self._advance()
                self._consume(':')
                value = self._current().value

                # Differentiate STRING | IDENTIFIER TOKEN
                if self._current().type == TokenType.STRING:
                    value = f'"{value}"'

                self._advance()
                self._consume(';')
                group.params[key] = value
                # logger.debug(f"Assign attribute - {key}: {value}")

        self._advance()  # Skip }
        logger.debug(f'Parsed Group: {group}')
        return group

    def _consume(self, expected):
        """
        Expect and consume the next token.
        If not expected, raise exception.
        """
        if self._current().value != expected:
            raise ParseError(
                f"Expected '{expected}', got '{self._current().value}'",
                self._current().line
            )
        self._advance()

    def _current(self) -> LibertyToken:
        if self.current_token < len(self.tokens):
            return self.tokens[self.current_token]

        raise ParseError("Unexpected EOF", line=None)

    def _advance(self) -> None:
        """
        Advance to the next token
        :return:
        """
        self.current_token += 1

    def _prev(self) -> Optional[LibertyToken]:
        prev_pos = self.current_token - 1
        return self.tokens[prev_pos] if prev_pos >= 0 else None

    def _peek(self) -> Optional[LibertyToken]:
        """
        Peek at the next token, without moving cursor
        :return:
        """
        next_pos = self.current_token + 1
        return self.tokens[next_pos] if next_pos < len(self.tokens) else None
