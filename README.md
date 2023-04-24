# QRParse

QRParse is a python scripted designed to peform a **Q**uick **R**ough **Parse** on series of Java project directories,
globbing all `.java` files and looking for matches against a hardcoded series of regular expressions.

This script was created as a part of a larger project at the Australian National University (Thomas Haines et al. 2023).

We used this script to statically analyse the projects open sourced for the SwissPost Evoting system, found here:

https://gitlab.com/swisspost-evoting

In this current build, we are matching all `.java` files that contain a `toHashableForm()` class instance method,
and then we are cross-checking the fields entered into the method against what fields the class declares.

Any field that isn't called `signature` and isn't found being passed into the `toHashableForm()` method is noted.

## Setting Up Paths

This program uses a `.env` file and `python3-dotenv` to load path variables. 

To specify your project paths, create a `.env` file in the following format:

```dotenv
EVOTING_PATH="path/to/evoting/dir"
CPD_PATH="path/to/crypto-primitives-domain/dir"
CP_PATH="path/to/crypto-primitives/dir"
VERIFIER_PATH="path/to/verifier/dir"
```

As you will notice, this `.env` file is hardcoded for the project that this script was built for: analysing the SwissPost
E-voting system (Thomas Haines et al. 2023). You can easily change what environment variables the script looks for by
modifying the `QRParseWrapper.get_paths_from_env()"` method.

i.e.

The method is defined as such:
```py 
class QRParseWrapper:
    ...
    def get_paths_from_env(self) -> None:
        try:
            self.paths.append(pathlib.Path(os.environ["VERIFIER_PATH"]))
            self.paths.append(pathlib.Path(os.environ["EVOTING_PATH"]))
            self.paths.append(pathlib.Path(os.environ["CPD_PATH"]))
            self.paths.append(pathlib.Path(os.environ["CP_PATH"]))
        except KeyError as e:
            print("Environment variable for path to dir is missing.")
            raise e
    ...
```
where the keys to `os.environ` can be freely modified to search for different environment variables.


## Command Line Arguments

This program has some command line parameters, and some of them work a little better than others:

```
$ python3 main.py --help

usage: QRParse.py [-h] [-p PATH] [-t TYPE] [-n NUMBER_THREADS] [-o OUT] [-v]
                  [-l] [--patterns R [R ...]]

A Quick Rough Parse(r) for java files (or any source file really...) looking
for specified regexes and patterns

options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH
  -t TYPE, --type TYPE
  -n NUMBER_THREADS, --number-threads NUMBER_THREADS
  -o OUT, --out OUT
  -v, --verbose
  -l, --list
  --patterns R [R ...]  The regex patterns to look for, appended to default

ALPHA version 1.0.0rc1

Process finished with exit code 0

```

**NOTE:** To speedily parse arbitrarily large Java projects, this program by default uses multithreading, and if the
command line argument `-n`/`--number-threads` isn't specified, it will spawn an 8 thread pool to achieve this.

## Example Invocation/Usage
```
python3 main.py --verbose --out report.yml  
```
