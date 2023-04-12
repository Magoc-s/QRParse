import sys
# import logging
import loguru
import multiprocessing
from multiprocessing import Manager
# from queue import Queue
import os
import yaml
import pathlib
import argparse
import re
from typing import Generator, Iterable, Any
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()
# This is default because im the best and everyone uses F drive surely
EVOTING_PATH: pathlib.Path = pathlib.Path(os.environ["EVOTING_PATH"])
TARGET_SOURCE_EXTENSION: str = ".java" if "TARGET_SOURCE_EXTENSION" not in os.environ.keys() \
    else os.environ["TARGET_SOURCE_EXTENSION"]

parser = argparse.ArgumentParser(
    prog='QRParse.py',
    description='A Quick Rough Parse(r) for java files (or any source file really...) '
                'looking for specified regexes and patterns',
    epilog='ALPHA version 0.1.0a')

parser.add_argument('-p', '--path', type=str)
parser.add_argument('-t', '--type', type=str)
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
    An iterable object of Java files globbed from the given directory and all subdirectories based on file extension.
    By default, we look for '.java' file extensions, but this can be overriden with the `--type` command-line argument,
    or with the TARGET_SOURCE_EXTENSION environment variable (use a .env file)
    """

    def __init__(self, project_path: str) -> None:
        self.path = pathlib.Path(project_path)
        self.depleted: bool = False
        self.files: Generator = self.path.glob(f"**/*{TARGET_SOURCE_EXTENSION}")
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
        """
        We multiprocess the file globbing and parsing as complex regex's can be inefficient to compute, especially over
        large numbers of files (such as the e-voting source dir)
        """
        self.POOL = multiprocessing.Pool(processes=8)
        self.MATCHES = {}

        manager = Manager()
        result_queue = manager.Queue()
        for pat_ in DEFAULT_PATTERNS.keys():
            self.MATCHES[pat_] = []

        print("Spinning up globbing engine...")
        for jf in tqdm(jf_iterable, ncols=60, colour='blue', desc='Globbing and Matching...'):
            self.POOL.apply_async(func=mp_parse_file, args=(jf, result_queue,))

        # Pull from the multiprocessing result queue to extract the computed dicts of each process invocation,
        # merge dict lists into main matches dict.
        while not result_queue.empty():
            _res: dict[str, list[JavaFile]] = result_queue.get()
            for rkey in _res.keys():
                self.MATCHES[rkey].extend(_res[rkey])


def mp_parse_file(jf: JavaFile, _rq: Any) -> None:
    """
    This is the multiprocessing target that the multiprocessing pool points the workers at,
    _rq is a result queue (from Manager().Queue()) that the output is stored in upon completion
    """
    _matches = {}
    for p_key in DEFAULT_PATTERNS.keys():
        pattern = DEFAULT_PATTERNS[p_key]
        _test = re.search(pattern, jf.contents)
        if not _test:
            continue

        if p_key not in _matches.keys():
            _matches[p_key] = []

        _matches[p_key].append(jf)
    _rq.put(_matches)


class RelevantValuesCallExtractor:
    """
    Uses the regexes specified in SUB_PATTERNS to extract the relevant important values from the given JavaFile
    object based on the computed relevance_type of that file from the RelevantFiles output dict
    """

    def __init__(self, jf: JavaFile, relevance_type: str) -> None:
        self.file = jf
        self.relevance_type = relevance_type
        self.extractor_regexes: list[str] = SUB_PATTERNS[self.relevance_type]
        self.extracted: list[str] = []
        for reg in self.extractor_regexes:
            _result = re.findall(reg, self.file.contents)
            if _result:
                for res in _result:
                    self.extracted.append(str(res).strip().replace("\n", "").replace("\t", ""))
        # print(f"{self.file.name}: {self.relevance_type}")
        # print(self.extracted)


class ClassInstanceFieldsExtractor:
    def __init__(self, jf: JavaFile) -> None:
        self.file = jf
        self.is_record = False
        self.is_final = False
        self.is_abstract = False
        self.has_static_builder = False
        self.implements: None | str = None
        self.extends: None | str = None
        self.values: list[tuple] = []
        try:
            if "public class" in self.file.contents:
                _search_str = "public class"
                _class_def_start: int = self.file.contents.index(_search_str)
            elif "public final class" in self.file.contents:
                _search_str = "public final class"
                _class_def_start: int = self.file.contents.index(_search_str)
            elif "public abstract class" in self.file.contents:
                self.is_abstract = True
                _search_str = "public abstract class"
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

            if "extends" in self.file.contents:
                self.extends = self.file.contents.split("extends ")[1].strip().split()[0]

            if "public static class Builder" in self.file.contents:
                self.has_static_builder = True

            if self.is_record:
                _class_def_name = _class_def_name.split("(")[0]
                _class_def_end = self.file.contents.index(f"public {_class_def_name} {{")
            elif self.is_abstract:
                _class_def_name = _class_def_name.split()[0]
                _class_def_end = self.file.contents.index(f"public abstract")
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


class HashGeneratorCheckInstanceFieldUsage:
    USED: list[str] = None
    UNUSED: list[str] = None

    def __init__(self,
                 cife: ClassInstanceFieldsExtractor,
                 rvce: RelevantValuesCallExtractor,
                 ) -> None:
        self.USED = []
        self.UNUSED = []
        self._cife = cife

        for _cif in cife.values:

            _name = _cif[0 if len(_cif[0]) > len(_cif[1]) else 1].replace("final", "").strip()
            _name = _name.split()[-1]
            if _name == "signature":
                continue
            if any([_name in x for x in rvce.extracted]):
                self.USED.append(_name)
            else:
                self.UNUSED.append(_name)

    def log(self) -> None:
        loguru.logger.success(f"REPORT: {self._cife.file.name} results")
        if self.UNUSED:
            loguru.logger.warning(f"The following class instance fields were found to not be used in the Hash Generator:")
            for _un in self.UNUSED:
                loguru.logger.warning(f" - {_un}")
        else:
            loguru.logger.info(f"All class instance fields were found in the Hash Generator declaration.")


class ClassInstanceFieldUsageReport:

    REPORT: dict[JavaFile, dict]

    def __init__(self) -> None:
        self.REPORT = {}

    def report(self, jf: JavaFile, relevance_type: str) -> None:
        if jf in self.REPORT.keys():
            if relevance_type in self.REPORT[jf].keys():
                return

        _fields = ClassInstanceFieldsExtractor(jf)
        _matches = RelevantValuesCallExtractor(jf, relevance_type)
        _usages = HashGeneratorCheckInstanceFieldUsage(_fields, _matches)

        self.REPORT[jf][relevance_type] = {
            "used": _usages.USED,
            "unused": _usages.UNUSED
        }

args = parser.parse_args()

if __name__ == "__main__":
    if args.list:
        print(yaml.safe_dump(DEFAULT_PATTERNS))
        sys.exit(0)

    if args.path is None:
        print(f"<< No path provided with --path < path >, defaulting to EVOTING_PATH environment variable. >>")

    if args.patterns:
        print(f"<< Additional anonymous patterns provided with --patterns, temp inserting into defaults... >>")
        for idx, pat in enumerate(args.patterns):
            DEFAULT_PATTERNS[f"ANONYMOUS_{idx}"] = pat

    if args.type:
        TARGET_SOURCE_EXTENSION = args.type
        print(f"<< Target source type extension provided with --type, overriding TARGET_SOURCE_EXTENSION >>")

    if not TARGET_SOURCE_EXTENSION.startswith("."):
        print("!! Target source type override is likely not a file extension (doesn't start with \".\") !!")
        print("!! This may result in unusual and unexpected globbing behaviour, proceed with caution.   !!")

    _path = EVOTING_PATH if args.path is None else args.path
    _relevant = RelevantFiles(JavaFileLoader(_path))
    for hash_gen in _relevant.MATCHES["Hash Generators"]:
        # print(hash_gen.name)
        _cife = ClassInstanceFieldsExtractor(hash_gen)
        _rvce = RelevantValuesCallExtractor(hash_gen, "Hash Generators")
        HashGeneratorCheckInstanceFieldUsage(_cife, _rvce)
    for hash_gen in _relevant.MATCHES["Hashcode Generators"]:
        # print(hash_gen.name)
        _cife = ClassInstanceFieldsExtractor(hash_gen)
        _rvce = RelevantValuesCallExtractor(hash_gen, "Hashcode Generators")
        HashGeneratorCheckInstanceFieldUsage(_cife, _rvce).log()
    # print(_relevant.MATCHES)
