from enum import Enum
from abc import ABC
from typing import Any, Callable, Self, Iterable

import loguru
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


class CommentMultiline(CommentToken):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour_type = "Multiline"


class CommentSingle(CommentToken):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour_type = "Single"


class NameToken(LexToken):
    flavour_type: str = None

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour = "Name"


class NameFunction(NameToken):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour_type = "Function"


class NameNamespace(NameToken):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour_type = "Namespace"


class NameClass(NameToken):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour_type = "Class"


class NameAttribute(NameToken):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour_type = "Attribute"


class NameDecorator(NameToken):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour_type = "Decorator"


class NameUnflavoured(NameToken):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)


class LiteralToken(LexToken):
    flavour_type: str = None

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour = "Literal"


class LiteralNumber(LiteralToken):
    flavour_subtype: str = None

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour_type = "Number"


class LiteralString(LiteralToken):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour_type = "String"


class LiteralInteger(LiteralNumber):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour_subtype = "Integer"


class LiteralFloat(LiteralNumber):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour_subtype = "Float"


class LiteralHex(LiteralNumber):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour_subtype = "Hex"


class LiteralBin(LiteralNumber):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour_subtype = "Bin"


class TextToken(LexToken):
    flavour_type: str = None

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour = "Text"


class TextUnflavoured(TextToken):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)


class TextWhitespace(TextToken):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour_type = "Whitespace"


class PunctuationToken(LexToken):
    flavour_type: str = None

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour = "Punctuation"


class PunctuationUnflavoured(PunctuationToken):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)


class OperatorToken(LexToken):
    flavour_type: str = None

    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour = "Operator"


class OperatorUnflavoured(OperatorToken):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)


class KeywordDeclaration(KeywordToken):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour_type = "Declaration"


class KeywordUnflavoured(KeywordToken):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)


class KeywordNamespace(KeywordToken):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour_type = "Namespace"


class KeywordType(KeywordToken):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour_type = "Type"


class KeywordConstant(KeywordToken):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position)
        self.flavour_type = "Constant"


class TokenFactory(metaclass=McSingleton):
    generated: list[LexToken] = None
    line_number: int = None
    char_number: int = None
    l1_lookup: dict = {
        "Keyword": {
            "Namespace": KeywordNamespace,
            "Declaration": KeywordDeclaration,
            "Type": KeywordType,
            "Constant": KeywordConstant,
            "%UNFLAVOURED%": KeywordUnflavoured,
        },
        "Name": {
            "Class": NameClass,
            "Function": NameFunction,
            "Namespace": NameNamespace,
            "Attribute": NameAttribute,
            "Decorator": NameDecorator,
            "%UNFLAVOURED%": NameUnflavoured,
        },
        "Comment": {
            "Multiline": CommentMultiline,
            "Single": CommentSingle,
        },
        "Text": {
            "Whitespace": TextWhitespace,
            "%UNFLAVOURED%": TextUnflavoured,
        },
        "Punctuation": {
            "%UNFLAVOURED%": PunctuationUnflavoured,
        },
        "Operator": {
            "%UNFLAVOURED%": OperatorUnflavoured
        },
        "Literal": {
            "Number": {
                "Integer": LiteralInteger,
                "Hex": LiteralHex,
                "Bin": LiteralBin,
                "Float": LiteralFloat,
            },
            "String": LiteralString
        },
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
                _lookup = _lookup[_token_type_descendents.pop(0)]
            except KeyError as e:
                loguru.logger.error(f"No lookup entry found for token {_token_type_name}"
                                    f"@L{self.line_number}:{self.char_number}")
                raise e
            except IndexError as e:
                if "%UNFLAVOURED%" in _lookup:
                    break
                else:
                    loguru.logger.error(f"No resolving callable for token classifier stream {_token_type_name}"
                                        f"@L{self.line_number}:{self.char_number}")
                    raise e

        if type(_lookup) is dict:
            if "%UNFLAVOURED%" in _lookup:
                _lookup = _lookup["%UNFLAVOURED%"]
            else:
                loguru.logger.error(f"Exhausted token classifier stream but didn't "
                                    f"resolve a callable: {_token_type_name}")

        # Create and set token object from lookup and misc properties
        _token_obj: LexToken = _lookup((self.line_number, self.char_number))
        _token_obj.set_token_type(token[0]).set_token_string(_token_str)
        # Keep track of position in the file
        _newlines = _token_str.count("\n")

        if _newlines > 0:
            self.line_number += _newlines
            self.char_number = 0
        else:
            self.char_number += len(_token_str)

        self.generated.append(_token_obj)
        return _token_obj


class TokenGroup(ABC):
    tokens: list[LexToken] = None


class TokenBlock(TokenGroup):
    def __init__(self, tokens: list[LexToken]):
        self.tokens = tokens
        self.opening_def = "{"
        self.closing_def = "}"


class TokenCollection(TokenGroup):
    def __init__(self, tokens: list[LexToken]):
        self.tokens = tokens
        self.opening_def = "("
        self.closing_def = ")"


class TokenLine(TokenGroup):
    def __init__(self, tokens: list[LexToken]):
        self.tokens = tokens
        self.opening_def = None
        self.closing_def = ";"


class ParseLexStream:
    def __init__(self, token_stream: Iterable) -> None:
        self._tok_stream = token_stream
        self.parsed_tokens = []
        _factory = TokenFactory()
        for tok in self._tok_stream:
            self.parsed_tokens.append(_factory.feed(tok))

        loguru.logger.info(f"Transposed lex stream into objects")
        # print(self.parsed_tokens)