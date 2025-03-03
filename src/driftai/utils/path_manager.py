import os

PACKAGE_DIR = os.path.dirname(os.path.dirname(__file__))


def get_internal_path(fp: str, check_exist: bool = False) -> str:
    global PACKAGE_DIR
    
    complete_path = os.path.join(PACKAGE_DIR, fp)

    if check_exist:
        assert os.path.exists(complete_path), \
            f'Path: "{fp}" does not exist inside the project folder!'
    
    return complete_path
