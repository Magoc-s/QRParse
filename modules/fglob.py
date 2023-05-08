import pathlib
from typing import Generator
from modules.meta import McSingleton
import loguru


class SourceLoadConfig(metaclass=McSingleton):
    SourceFileExtension: str = None

    def __init__(self):
        if self.SourceFileExtension is None:
            self.SourceFileExtension = ""

    def set_source_file_extension(self, source_file_extension: str) -> None:
        loguru.logger.debug(f"Updated source load config to search for source "
                            f"files with extension: {source_file_extension}")
        self.SourceFileExtension = source_file_extension


class SourceFile:
    """
    An object representing a SourceFile, containing the file path, name and contents
    """
    def __init__(self, path: pathlib.Path):
        self.path = path
        self.name = path.name
        with open(self.path, 'r', encoding='utf-8') as f:
            self.contents = f.read()


class SourceFileLoader:
    """
    An iterable object of SourceFiles globbed from the given directory and all subdirectories based on file extension.
    By default, we look for '.java' file extensions, but this can be overriden with the `--type` command-line argument,
    or with the TARGET_SOURCE_EXTENSION environment variable (use a .env file)
    """

    def __init__(self, project_path: str) -> None:
        _config = SourceLoadConfig()
        assert _config.SourceFileExtension is not None and _config.SourceFileExtension != ""
        self.path = pathlib.Path(project_path)
        self.depleted: bool = False
        self.files: Generator = self.path.glob(f"**/*{_config.SourceFileExtension}")
        self.current_idx: int = 0

    def __iter__(self):
        return self

    def __next__(self) -> SourceFile:
        return SourceFile(self.files.__next__())


def create_file_loader(project_path: str) -> SourceFileLoader:
    _inst = SourceFileLoader(project_path=project_path)
    loguru.logger.debug(f"Instantiated a source file loader for directory {project_path}.")
    return _inst
