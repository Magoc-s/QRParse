import sys
import logging
import yaml
import pathlib
import argparse
import re
from typing import Generator, Iterable
from tqdm import tqdm

# This is default because im the best and everyone uses F drive surely
EVOTING_PATH: pathlib.Path = pathlib.Path("F:\\projects\\investigating-errors-project\\e-voting")

parser = argparse.ArgumentParser(
                    prog='QRParse.py',
                    description='A Quick Rough Parse(r) for java files (or any source file really...) '
                                'looking for specified regexes and patterns',
                    epilog='ALPHA version 0.1.0a')

parser.add_argument('-p', '--path', type=str)           # positional argument
parser.add_argument('-v', '--verbose',
                    action='store_true')  # on/off flag
parser.add_argument('-l', '--list',
                    action='store_true')
parser.add_argument('--patterns', metavar='R', type=str, nargs='+',
                    help='The regex patterns to look for, appended to default')

DEFAULT_PATTERNS: dict = {
    "Hash Generators": r"List<Hashable> toHashableForm\(\)",
    "Hash Usages": r"([a-zA-Z]+[a-zA-Z0-9]*).toHashableForm\(\)",
    "Hashable Type Usages": r"Hashable([A-Za-z]+).from\(([a-zA-Z]+[a-zA-Z0-9\.\_\(\)]*)\)",
    "Hashcode Generators": r"public int hashCode\(\)"
}

SUB_PATTERNS: dict = {
    "Hashcode Generators": [
        r"Objects.hash\(([a-zA-Z]+[a-zA-Z0-9\.,\_\(\)\s]*)\)",
        # matches the Objects.hash func call, and groups the meth. params
    ],
    "Hash Generators": [
        r"List.of\([\s]*([a-zA-Z]+[a-zA-Z0-9\.,\_\(\)\s]*)\)"
        # matches the List.of func call, and groups the params included in that call
    ]
}

INSTANCE_FIELD_MATCH = r"private(final | )? ([^;]+);"
RECORD_CONS_FIELD_MATCH = r"([\S]+ [a-zA-Z_]+)(,|$)"


class JavaFile:
    """
    An object representing a JavaFile, containing the file path, name and contents
    """

    def __init__(self, path: pathlib.Path):
        self.path = path
        self.name = path.name
        with open(self.path, 'r', encoding='utf-8') as f:
            self.contents = f.read()


class JavaFileLoader:
    """
    An iterable object of Java files globbed from the given directory and all subdirectories
    """

    def __init__(self, project_path: str) -> None:
        self.path = pathlib.Path(project_path)
        self.depleted: bool = False
        self.files: Generator = self.path.glob("**/*.java")
        self.current_idx: int = 0

    def __iter__(self):
        return self

    def __next__(self) -> JavaFile:
        return JavaFile(self.files.__next__())


class RelevantFiles:
    """
    An object containing an iterable of JavaFile's that contain the desired regex patterns
    """
    MATCHES: dict[str, list[JavaFile]] = None

    def __init__(self, jf_iterable: Iterable[JavaFile]) -> None:
        self.MATCHES = {}
        for pat_ in DEFAULT_PATTERNS.keys():
            self.MATCHES[pat_] = []

        print("Spinning up globbing engine...")
        for jf in tqdm(jf_iterable, ncols=60, colour='blue', desc='Globbing and Matching...'):
            for p_key in DEFAULT_PATTERNS.keys():
                pattern = DEFAULT_PATTERNS[p_key]
                _test = re.search(pattern, jf.contents)
                if not _test:
                    continue

                self.MATCHES[p_key].append(jf)


class RelevantValuesCallExtractor:
    def __init__(self, jf: JavaFile, relevance_type: str) -> None:
        self.file = jf
        self.relevance_type = relevance_type
        self.extractor_regexes: list[str] = SUB_PATTERNS[self.relevance_type]
        self.extracted: list[str] = []
        for reg in self.extractor_regexes:
            _result = re.findall(reg, self.file.contents)
            if _result:
                for res in _result:
                    self.extracted.append(str(res).strip().replace("\\n", "").replace("\\t", ""))
        print(f"{self.file.name}: {self.relevance_type}")
        print(self.extracted)


class ClassInstanceFieldsExtractor:
    def __init__(self, jf: JavaFile) -> None:
        self.file = jf
        self.is_record = False
        self.has_static_builder = False
        self.implements: None | str = None
        self.values: None | list[tuple] = None
        try:
            if "public class" in self.file.contents:
                _search_str = "public class"
                _class_def_start: int = self.file.contents.index(_search_str)
            elif "public record" in self.file.contents:
                self.is_record = True
                _search_str = "public record"
                _class_def_start: int = self.file.contents.index(_search_str)
            else:
                print(f"Cant find a class or record def in {self.file.name}.")
                raise ValueError(f"Cant find a class or record def in {self.file.name}.")

            _class_def_name: str = self.file.contents[_class_def_start + len(_search_str):]
            _class_def_name = _class_def_name.strip()

            if "implements" in self.file.contents:
                self.implements = self.file.contents.split("implements ")[1].split("{")[0].strip()

            if "public static class Builder" in self.file.contents:
                self.has_static_builder = True

            if self.is_record:
                _class_def_name = _class_def_name.split("(")[0]
                _class_def_end = self.file.contents.index(f"public {_class_def_name} {{")
            else:
                _class_def_name = _class_def_name.split()[0]
                if self.has_static_builder:
                    _class_def_end = self.file.contents.index(f"private {_class_def_name}(")
                else:
                    _class_def_end = self.file.contents.index(f"public {_class_def_name}(")

            # print(f"Class def starts at {_class_def_start}, ends at {_class_def_end} and has name {_class_def_name} ")
            if self.is_record:
                _sub_contents: str = self.file.contents[_class_def_start:_class_def_end].split("(")[1].split(")")[0]
                matches = re.findall(RECORD_CONS_FIELD_MATCH, _sub_contents)
                if matches:
                    self.values = matches
                    # print(matches)
            else:
                _sub_contents: str = self.file.contents[_class_def_start:_class_def_end]
                matches = re.findall(INSTANCE_FIELD_MATCH, _sub_contents)
                if matches:
                    self.values = matches
                    # print(matches)

        except ValueError as e:
            print(f"Could not string manipulate file...")
            print(e)


args = parser.parse_args()

if args.list:
    print(yaml.safe_dump(DEFAULT_PATTERNS))
    sys.exit(0)


if args.path is None:
    print(f"No path provided with --path < path >, using default path to evoting (hard coded in script!)")


if args.patterns:
    for idx, pat in enumerate(args.patterns):
        DEFAULT_PATTERNS[f"ANONYMOUS_{idx}"] = pat


if __name__ == "__main__":
    _path = EVOTING_PATH if args.path is None else args.path
    _relevant = RelevantFiles(JavaFileLoader(_path))
    for hash_gen in _relevant.MATCHES["Hash Generators"]:
        # print(hash_gen.name)
        ClassInstanceFieldsExtractor(hash_gen)
        RelevantValuesCallExtractor(hash_gen, "Hash Generators")
    # print(_relevant.MATCHES)
