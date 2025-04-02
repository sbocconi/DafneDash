import yaml
from pathlib import Path

def read_yaml():
    SETTINGS_FILE = '.settings.yaml'
    full_file_path = Path(__file__).parent.joinpath(SETTINGS_FILE)
    with open(full_file_path) as settings:
        settings = yaml.load(settings, Loader=yaml.Loader)
    return settings


class DataDumps:
    API_DT_FRMT = "%Y-%m-%dT%H:%M:%S.%f"
    FILE_DT_FRMT = "%Y-%m-%dT%H:%M:%SZ"

    metric_data = None

    def __init__(self):
        pass
    
    @classmethod
    def set_metric_data(cls, metric_data):
        cls.metric_data = metric_data
    
    @classmethod
    def get_keyed_data(cls, key):
        return cls.metric_data.get_data(key)
    
    @classmethod
    def set_keyed_data(cls, key, data):
        cls.metric_data.set_data(key, data)
    