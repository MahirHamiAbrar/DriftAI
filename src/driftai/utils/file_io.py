import json
from typing import Any


def read_json(fp: str) -> Any:
    with open(fp, 'r') as _json_file:
        return json.load(_json_file)


def write_json(fp: str, obj: Any, indent: int = 4) -> None:
    with open(fp, 'w') as _json_file:
        json.dump(obj, fp, indent=indent)
