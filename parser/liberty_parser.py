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

    @lru_cache(maxsize=1024)
    def asdict(self):
        data = {}

        # Group Type
        data[self.group_type] = self.name

        # Simple Attributes
        for k, v in self.params.items():
            data[k] = v

        # Complex Attributes
        for g in self.children:
            # data[g.name] = g.asdict()
            if isinstance(g, (LibertyAttribute, ComplexLibertyAttribute)):
                data[g.name] = g.asdict()
            elif isinstance(g, LibertyGroup):
                # using special separator as values
                instance_name = f"#&#{g.group_type}#&#{g.name}"
                data[instance_name] = g.asdict()
            else:
                raise ParseError(f"Unrecognized data type: {type(g)}")

        return data


class LibertyParser:
    TOKEN_REGEX = re.compile(r"""
        (?P<keyword>\b(?:library|cell|pin|direction|timing|related_pin|cell_rise|values)\b) |
        (?P<string>"[^"]*") |
        (?P<number>[-+]?\d+\.?\d*) |
        (?P<symbol>[(){},:;]) |
        (?P<identifier>\w+)
    """, re.VERBOSE)

    def __init__(self, file_path):
        self.file_path = file_path
        self.tokens: List[LibertyToken] = []
        self.current_token = 0
        # TODO: Handle  bus_naming_style : "%s[%d]";

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
        # logger.info(f"Line: {self._current().line} Peek: {self._peek().value}")

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
        else:
            self._advance()
            self._consume(')')
        # logger.debug(f"name: {name}")

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
                self._advance()
                self._consume(';')
                group.params[key] = value
                logger.debug(f"Assign attribute - {key}: {value}")
        self._advance()  # Skip }
        logger.debug(f'Parsed Group: {group}')
        return group

    def _consume(self, expected):
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
        移动到下一个Token
        :return:
        """
        self.current_token += 1

    def _peek(self) -> Optional[LibertyToken]:
        """
        预读下一个Token，不移动指针
        :return:
        """
        next_pos = self.current_token + 1
        return self.tokens[next_pos] if next_pos < len(self.tokens) else None
