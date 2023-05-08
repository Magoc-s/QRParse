from modules.fglob import create_file_loader, SourceLoadConfig, SourceFileLoader, SourceFile
import loguru
import pygments
from pygments import lexers
from typing import Iterable


class LexFile:
    source: SourceFile = None
    tokens: Iterable = None

    def __init__(self, source: SourceFile) -> None:
        # print(source)
        self.sn: str = source.name
        self.source: SourceFile = source
        _lexer = lexers.guess_lexer_for_filename(self.sn, source.contents)
        self.tokens = pygments.lex(source.contents, _lexer)
        loguru.logger.debug(f"Lexed file {self.sn}")


class LexFileGenerator:
    loader: SourceFileLoader = None

    def __init__(self, *, path: str, source_file_ext: str):
        SourceLoadConfig().set_source_file_extension(source_file_ext)
        self.loader = create_file_loader(path)
        loguru.logger.debug(f"Connected lex generator to source loader stream")

    def __iter__(self):
        return self

    def __next__(self) -> LexFile:
        return LexFile(self.loader.__next__())
