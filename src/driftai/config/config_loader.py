import os as __os
import driftai.utils as __drift_utils

# this private variable will hold the configs
# this is a global variable, so, it will load only once on first loading.
_config: dict = None


def load_config() -> None:
    global _config

    if _config is None:
        json_fp = __drift_utils.get_internal_path(
            'data/config.json', check_exist=True
        )
        _config = __drift_utils.read_json_file(json_fp)

        # add this extra key to the '_config' path
        _config['config_file_path'] = json_fp


def get_config() -> dict:
    global _config

    if _config is None:
        load_config()
    
    return _config


def get_config_data_subpath(
        keys: list[str],
        check_exist: bool = False
) -> str:
    
    fp = get_config()
    data_dir = fp['data_dir']

    for key in keys:
        fp = fp.get(key)

    complete_path = __os.path.join(
        __drift_utils.PACKAGE_DIR,
        fp.format(data_dir=data_dir)
    )

    if check_exist:
        assert __os.path.exists(complete_path), \
            f'Path: "{fp}" does not exist inside the "data" folder!'
    
    return complete_path

