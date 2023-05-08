import modules.flex as lex
from dotenv import load_dotenv
import os

load_dotenv()

_inst = lex.LexFileGenerator(path=os.environ["EVOTING_PATH"], source_file_ext=".java")

for lf in _inst:
    for tok in lf.tokens:
        print(f"{type(tok[0])}, {type(tok[1])}: {tok}")
        # print(str(tok[0]))
    break
