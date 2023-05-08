from enum import Enum
from abc import ABC
from typing import Any, Callable, Self

import loguru
from pygments import token
from modules.meta import McSingleton


class TokenEnum(Enum):
    pass

class TokenTypes(TokenEnum):
    KWDecl = "Token.Keyword.Declaration"
    MLComment = "Token.Comment.Multiline"
    SLComment = "Token.Comment.Single"
    Whitespace = "Token.Text.Whitespace"
    Punctuation = "Token.Punctuation"
    KWNamespace = "Token.Keyword.Namespace"
    NameNamespace = "Token.Name.Namespace"
    Name = "Token.Name"
    Operator = "Token.Operator"
    FunctionName = "Token.Name.Function"
    ClassName = "Token.Name.Class"
    LiteralInt = "Token.Literal.Number.Integer"


class TokenUStreams(TokenEnum):
    Private = (TokenTypes.KWDecl, "private")
    Public = (TokenTypes.KWDecl, "public")
    Final = (TokenTypes.KWDecl, "final")
    Static = (TokenTypes.KWDecl, "static")
    Semicolon = (TokenTypes.Punctuation, ";")
    OpCurlyBrace = (TokenTypes.Punctuation, "{")
    ClCurlyBrace = (TokenTypes.Punctuation, "}")
    OpParenthesis = (TokenTypes.Punctuation, "(")
    ClParenthesis = (TokenTypes.Punctuation, ")")
    Space = (TokenTypes.Whitespace, " ")
    Class = (TokenTypes.KWDecl, "class")


class LexToken(ABC):
    token_type: Any = None
    token_string: str = None
    position: tuple[int, int] = None
    flavour: str = None

    def __init__(self, position: tuple[int, int]):
        self.position = position

    def set_token_type(self, token_type: Any) -> Self:
        self.token_type = token_type
        return self

    def set_token_string(self, token_string: str) -> Self:
        self.token_string = token_string
        return self


class KeywordToken(LexToken):
    flavour_type: str = None

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour = "Keyword"


class CommentToken(LexToken):
    flavour_type: str = None

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour = "Comment"


class NameToken(LexToken):
    flavour_type: str = None

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour = "Name"


class LiteralToken(LexToken):
    flavour_type: str = None

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour = "Literal"


class TextToken(LexToken):
    flavour_type: str = None

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour = "Text"


class PunctuationToken(LexToken):
    flavour_type: str = None

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour = "Punctuation"


class OperatorToken(LexToken):
    flavour_type: str = None

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour = "Operator"


class KeywordDeclaration(KeywordToken):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour_type = "Declaration"


class KeywordNamespace(KeywordToken):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour_type = "Namespace"


class TokenFactory(metaclass=McSingleton):
    generated: list[LexToken] = None
    line_number: int = None
    char_number: int = None
    l1_lookup: dict = {
        "Keyword": {
            "Namespace": KeywordNamespace,
            "Declaration": KeywordDeclaration,
        },
        "Name": {},
        "Comment": {},
        "Test": {},
        "Punctuation": {},
        "Operator": {},
        "Literal": {},
    }

    def __init__(self) -> None:
        if self.generated is None:
            self.generated = []
        if self.line_number is None:
            self.line_number = 0
        if self.char_number is None:
            self.char_number = 0

    def feed(self, token: tuple) -> LexToken:
        """
        Feed me rawr
        Give me a big juicy tasty lexed token and I will make an uwu LexToken descendant (a class that inherits
        LexToken) that u can use for fun things
        """
        _token_type_name: str = str(token[0])
        _token_str: str = token[1]

        _token_type_descendents: list[str] = _token_type_name.split(".")
        assert _token_type_descendents.pop(0) == "Token"

        _lookup: dict | Callable = self.l1_lookup[_token_type_descendents.pop(0)]
        while type(_lookup) is dict:
            # Only breaks when lookup popping returns a callable
            try:
                _lookup = self.l1_lookup[_token_type_descendents.pop(0)]
            except KeyError as e:
                loguru.logger.error(f"No lookup entry found for token {_token_type_name}"
                                    f"@L{self.line_number}:{self.char_number}")
                raise e

        # Create and set token object from lookup and misc properties
        _token_obj: LexToken = _lookup((self.line_number, self.char_number))
        _token_obj.set_token_type(token[0]).set_token_string(_token_str)
        # Keep track of position in the file
        if _token_type_name == "Token.Text.Whitespace" and _token_str == "\n":
            self.line_number += 1
            self.char_number = 0
        else:
            self.char_number += len(_token_str)

        self.generated.append(_token_obj)
        return _token_obj


class LexStreamNode(ABC):
    pass


class SourceBlock(LexStreamNode):
    contents: list[LexStreamNode]
    declaration: LexStreamNode


class SourceLine(LexStreamNode):
    declaration: list[LexToken]


class DecanonicaliseLexStream:
    def __init__(self, token_stream):
        pass