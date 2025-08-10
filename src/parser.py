from __future__ import annotations

import string
import textwrap
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Literal


# tokenizer:
@dataclass
class Token:
    """A token produced by tokenization."""

    kind: TokenKind
    text: str
    start_pos: int
    end_pos: int
    errors: list[str] = field(default_factory=list)


class TokenKind(Enum):
    """What the token represents."""

    # keywords
    SELECT = auto()
    FROM = auto()
    WHERE = auto()

    # literals
    STRING = auto()
    IDENTIFIER = auto()
    STAR = auto()
    EQUALS = auto()

    # structure
    COMMA = auto()
    ERROR = auto()
    EOF = auto()  # this is a fake token only made and used in the parser


KEYWORDS = {
    "SELECT": TokenKind.SELECT,
    "FROM": TokenKind.FROM,
    "WHERE": TokenKind.WHERE,
}


@dataclass
class Cursor:
    """Helper class to allow peeking into a stream of characters."""

    contents: str
    index: int = 0

    def peek(self) -> str:
        """Look one character ahead in the stream."""
        return self.contents[self.index : self.index + 1]

    def next(self) -> str:
        """Get the next character in the stream."""
        c = self.peek()
        if c != "":
            self.index += 1
        return c


def tokenize(query: str) -> list[Token]:
    """Turn a query into a list of tokens."""
    result = []

    cursor = Cursor(query)
    while True:
        idx = cursor.index
        char = cursor.next()

        if char == "":
            break

        if char in string.ascii_letters:
            char = cursor.peek()

            while char in string.ascii_letters + ".":
                cursor.next()
                char = cursor.peek()
                if char == "":
                    break

            identifier = cursor.contents[idx : cursor.index]
            kind = KEYWORDS.get(identifier, TokenKind.IDENTIFIER)
            result.append(Token(kind, identifier, idx, cursor.index))

        elif char == ",":
            result.append(Token(TokenKind.COMMA, ",", idx, cursor.index))

        elif char == "*":
            result.append(Token(TokenKind.STAR, "*", idx, cursor.index))

        elif char == "'":
            # idk escaping rules in SQL lol
            char = cursor.peek()
            while char != "'":
                cursor.next()
                char = cursor.peek()
                if char == "":
                    break

            cursor.next()  # get the last '

            string_result = cursor.contents[idx : cursor.index]
            kind = TokenKind.STRING if string_result.endswith("'") and len(string_result) > 1 else TokenKind.ERROR
            result.append(Token(kind, string_result, idx, cursor.index))

        elif char == "=":
            result.append(Token(TokenKind.EQUALS, "=", idx, cursor.index))

    return result


# parser
# heavily inspired by https://matklad.github.io/2023/05/21/resilient-ll-parsing-tutorial.html
@dataclass
class Parser:
    """Helper class that provides useful parser functionality."""

    contents: list[Token]
    events: list[Event] = field(default_factory=list)
    index: int = 0
    unreported_errors: list[str] = field(default_factory=list)

    def eof(self) -> bool:
        """Check whether the token stream is done."""
        return self.index == len(self.contents)

    def peek(self) -> TokenKind:
        """Look at the next kind of token in the stream."""
        if self.eof():
            return TokenKind.EOF
        return self.contents[self.index].kind

    def advance(self) -> None:
        """Move to the next token in the stream."""
        self.index += 1
        self.events.append("ADVANCE")

    def advance_with_error(self, error: str) -> None:
        """Mark the current token as being wrong."""
        if self.eof():
            # this should probably be done better...
            self.unreported_errors.append(error)
        else:
            self.contents[self.index].errors.append(error)
            self.advance()

    def open(self) -> int:
        """Start nesting children."""
        result = len(self.events)
        self.events.append(("OPEN", ParentKind.ERROR_TREE))
        return result

    def open_before(self, index: int) -> int:
        """Start nesting children before a given point."""
        self.events.insert(index, ("OPEN", ParentKind.ERROR_TREE))
        return index

    def close(self, kind: ParentKind, where: int) -> int:
        """Stop nesting children and note the tree type."""
        self.events[where] = ("OPEN", kind)
        self.events.append("CLOSE")
        return where

    def expect(self, kind: TokenKind, error: str) -> None:
        """Ensure the next token is a specific kind and advance."""
        if self.at(kind):
            self.advance()
        else:
            self.advance_with_error(error)

    def at(self, kind: TokenKind) -> None:
        """Check if the next token is a specific kind."""
        return self.peek() == kind


@dataclass
class Parent:
    """Syntax tree element with children."""

    kind: ParentKind
    children: list[Tree]
    errors: list[str] = field(default_factory=list)


class ParentKind(Enum):
    """Kinds of syntax tree elements that have children."""

    SELECT_STMT = auto()
    ERROR_TREE = auto()
    FIELD_LIST = auto()
    FROM_CLAUSE = auto()
    WHERE_CLAUSE = auto()
    EXPR_NAME = auto()
    EXPR_STRING = auto()
    EXPR_BINARY = auto()
    FILE = auto()


Tree = Parent | Token
Event = Literal["ADVANCE", "CLOSE"] | tuple[Literal["OPEN"], ParentKind]


def turn_tokens_into_events(tokens: list[Token]) -> list[Event]:
    """Parse a token stream into a list of events."""
    parser = Parser(tokens, [])
    while not parser.eof():
        _parse_stmt(parser)
    return parser.events, parser.unreported_errors


def parse(tokens: list[Token]) -> Tree:
    """Parse a token stream into a syntax tree."""
    events, errors = turn_tokens_into_events(tokens)
    stack = [("OPEN", ParentKind.FILE)]
    events.append("CLOSE")

    i = 0
    for event in events:
        if event == "ADVANCE":
            stack.append(tokens[i])
            i += 1
        elif event == "CLOSE":
            inner = []
            while True:
                e = stack.pop()
                if isinstance(e, tuple) and e[0] == "OPEN":
                    inner.reverse()
                    stack.append(Parent(e[1], inner))
                    break
                inner.append(e)
        else:
            assert isinstance(event, tuple)
            assert event[0] == "OPEN"
            stack.append(event)

    assert i == len(tokens)
    assert len(stack) == 1
    result = stack[0]
    assert isinstance(result, Tree)
    assert result.kind == ParentKind.FILE
    result.errors.extend(errors)
    return result


# free parser functions
def _parse_stmt(parser: Parser) -> None:
    # <select_stmt>
    _parse_select_stmt(parser)


def _parse_select_stmt(parser: Parser) -> None:
    # 'SELECT' <field> [ ',' <field> ]* [ 'FROM' IDENTIFIER ] [ 'WHERE' <expr> ]
    start = parser.open()
    parser.expect(TokenKind.SELECT, "only SELECT is supported")

    fields_start = parser.open()
    _parse_field(parser)
    while parser.at(TokenKind.COMMA):
        parser.advance()
        _parse_field(parser)
    parser.close(ParentKind.FIELD_LIST, fields_start)

    if parser.at(TokenKind.FROM):
        # from clause
        from_start = parser.open()
        parser.advance()

        parser.expect(TokenKind.IDENTIFIER, "expected to select from a table")
        parser.close(ParentKind.FROM_CLAUSE, from_start)

    if parser.at(TokenKind.WHERE):
        # where clause
        where_start = parser.open()
        parser.advance()

        _parse_expr(parser)
        parser.close(ParentKind.WHERE_CLAUSE, where_start)

    parser.close(ParentKind.SELECT_STMT, start)


def _parse_field(parser: Parser) -> None:
    # '*' | <expr>
    if parser.at(TokenKind.STAR):
        parser.advance()
    else:
        _parse_expr(parser)


def _parse_expr(parser: Parser) -> None:
    # <small expr> | <small expr> = <small expr>
    _parse_expr_inner(parser, TokenKind.EOF)


def _parse_expr_inner(parser: Parser, left_op: TokenKind) -> None:
    left = _parse_small_expr(parser)

    while True:
        right_op = parser.peek()
        if right_goes_first(left_op, right_op):
            # if we have A <left_op> B <right_op> C ...,
            # then we need to parse (A <left_op> (B <right_op> C ...))
            outer = parser.open_before(left)
            parser.advance()
            _parse_expr_inner(parser, right_op)  # (B <right_op> C ...)
            parser.close(ParentKind.EXPR_BINARY, outer)
        else:
            # (A <left_op> B) <right_op> C will be handled
            # (if this were toplevel, right_goes_first will happen)
            break


def _parse_small_expr(parser: Parser) -> int:
    # IDENTIFIER
    start = parser.open()
    if parser.at(TokenKind.IDENTIFIER):
        parser.advance()
        return parser.close(ParentKind.EXPR_NAME, start)
    if parser.at(TokenKind.STRING):
        parser.advance()
        return parser.close(ParentKind.EXPR_STRING, start)
    parser.advance_with_error("expected expression")
    return parser.close(ParentKind.ERROR_TREE, start)


TABLE = [[TokenKind.EQUALS]]


def right_goes_first(left: TokenKind, right: TokenKind) -> bool:
    """Understand which token type binds tighter.

    We say that A <left> B <right> C is equivalent to:
     - A <left> (B <right> C) if we return True
     - (A <left> B) <right> C if we return False
    """
    left_idx = next((i for i, r in enumerate(TABLE) if left in r), None)
    right_idx = next((i for i, r in enumerate(TABLE) if right in r), None)

    if right_idx is None:
        # evaluate left-to-right
        return False
    if left_idx is None:
        # well, maybe left doesn't exist?
        assert left == TokenKind.EOF
        return True

    return right_idx > left_idx


##### tests: (this should be moved to a proper tests folder)


def check_tok(before: str, after: TokenKind) -> None:
    """Test helper which checks a string tokenizes to a single given token kind."""
    assert [tok.kind for tok in tokenize(before)] == [after]


def stringify_tokens(query: str) -> str:
    """Test helper which turns a query into a repr of the tokens.

    Used for manual snapshot testing.
    """
    tokens = tokenize(query)
    result = ""
    for i, c in enumerate(query):
        for tok in tokens:
            if tok.end_pos == i:
                result += "<"

        for tok in tokens:
            if tok.start_pos == i:
                result += ">"

        result += c

    i += 1
    for tok in tokens:
        if tok.end_pos == i:
            result += "<"

    return result


def _stringify_tree(tree: Tree) -> list[str]:
    result = []
    if isinstance(tree, Parent):
        result.append(f"{tree.kind.name}")
        result.extend("    " + line for child in tree.children for line in _stringify_tree(child))
    else:
        repr = f'{tree.kind.name} ("{tree.text}")'
        if tree.errors:
            repr += " -- "
            repr += " / ".join(tree.errors)
        result.append(repr)

    return result


def stringify_tree(tree: Tree) -> str:
    """Test helper that turns a syntax tree into a representation of it.

    Used for manual snapshot testing
    """
    assert not tree.errors
    return "\n".join(_stringify_tree(tree))


def test_simple_tokens() -> None:
    """Tests that various things tokenize correct in minimal cases."""
    assert [tok.kind for tok in tokenize("")] == []
    check_tok("SELECT", TokenKind.SELECT)
    check_tok("FROM", TokenKind.FROM)
    check_tok("'hello :)'", TokenKind.STRING)
    check_tok(",", TokenKind.COMMA)
    check_tok("*", TokenKind.STAR)
    check_tok("username", TokenKind.IDENTIFIER)


def test_tokenize_simple_select() -> None:
    """Tests that tokenization works in more general cases."""
    assert stringify_tokens("SELECT * FROM posts") == ">SELECT< >*< >FROM< >posts<"


def test_parse_simple() -> None:
    """Tests that parsing works in some specific cases."""
    assert (
        stringify_tree(parse(tokenize("SELECT * FROM posts")))
        == textwrap.dedent("""
        FILE
            SELECT_STMT
                SELECT ("SELECT")
                FIELD_LIST
                    STAR ("*")
                FROM_CLAUSE
                    FROM ("FROM")
                    IDENTIFIER ("posts")
    """).strip()
    )

    assert (
        stringify_tree(parse(tokenize("SELECT * WHERE actor = 'aaa'")))
        == textwrap.dedent("""
        FILE
            SELECT_STMT
                SELECT ("SELECT")
                FIELD_LIST
                    STAR ("*")
                WHERE_CLAUSE
                    WHERE ("WHERE")
                    EXPR_BINARY
                        EXPR_NAME
                            IDENTIFIER ("actor")
                        EQUALS ("=")
                        EXPR_STRING
                            STRING ("'aaa'")
    """).strip()
    )


if __name__ == "__main__":
    query = input("query> ")
    print(stringify_tokens(query))

    print()
    print(stringify_tree(parse(tokenize(query))))
