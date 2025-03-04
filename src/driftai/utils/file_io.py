import json
from typing import Any


def read_file(fp: str) -> str:
    with open(fp, 'r') as _file:
        return _file.read()

def write_file(fp: str, content: str, filemode: str = 'w') -> None:
    with open(fp, filemode) as _file:
        _file.write(content)

def read_json_file(fp: str) -> Any:
    return json.loads(read_file(fp))

def write_json_file(fp: str, obj: Any, filemode: str = 'w', indent: int = 4) -> None:
    write_file(
        fp,
        json.dumps(obj, indent=indent),
        filemode
    )
