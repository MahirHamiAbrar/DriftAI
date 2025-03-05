
def test_config_subpath() -> None:
    from driftai.config import get_config_data_subpath
    path = get_config_data_subpath(['audio', 'recorder', 'output_dir'])
    print(f'{path = }')
