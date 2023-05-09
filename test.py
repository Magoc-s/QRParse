import loguru

import modules.flex as lex
import modules.lexpatterns as lp
from dotenv import load_dotenv
import os

load_dotenv()

_inst = lex.LexFileGenerator(path=os.environ["EVOTING_PATH"], source_file_ext=".java")

for lf in _inst:
    tok_parser = lp.ParseLexStream(lf.tokens)
    loguru.logger.info(f"Parsed {len(tok_parser.parsed_tokens)} tokens from file {lf.source.name}.")
    # _last_ln = 0
    # for parsed_obj in tok_parser.parsed_tokens:
    #     print(f"{parsed_obj.token_string}@L{parsed_obj.position[0]}:{parsed_obj.position[1]}",
    #           end="\n" if parsed_obj.position[0] != _last_ln else "")
    #     _last_ln = parsed_obj.position[0]
    # break
