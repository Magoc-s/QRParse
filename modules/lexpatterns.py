from enum import Enum
from abc import ABC
from pygments import token


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


class LexToken:
    token_type = None
    token_string = None

    def __init__(self, tok):
        self.token_type = tok[0]
        self.token_string = tok[1]


class LexStreamNode(ABC):
    pass


class SourceBlock(LexStreamNode):
    contents: list[LexStreamNode]
    declaration: LexStreamNode


class SourceLine(LexStreamNode):
    declaration: list[LexToken]


class DecanonicaliseLexStream:

    def __init__(self, token_stream):