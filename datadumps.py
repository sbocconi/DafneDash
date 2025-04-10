import yaml
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

def read_yaml():
    SETTINGS_FILE = '.settings.yaml'
    full_file_path = Path(__file__).parent.joinpath(SETTINGS_FILE)
    with open(full_file_path) as settings:
        settings = yaml.load(settings, Loader=yaml.Loader)
    return settings


class DataDumps:
    SYNTL_DT_FRMT = "%Y-%m-%dT%H:%M:%S.%f"
    CNT_DT_FRMT = "%Y-%m-%dT%H:%M:%SZ"
    CERTL_DT_FRMT = "/%m/%d/%Y"
    MP_DT_FRMT = '%Y-%m-%dT%H:%M:%S.%fZ'

    metric_data = None

    def __init__(self):
        pass
    
    @classmethod
    def set_metric_data(cls, metric_data):
        cls.metric_data = metric_data
    
    @classmethod
    def get_keyed_data(cls, category, key):
        return cls.metric_data.get_data(category, key)
    
    @classmethod
    def set_keyed_data(cls, category, key, data):
        cls.metric_data.set_data(category, key, data)
    
    @classmethod
    def convert_date_frmt(cls, date, frmt_in, frmt_out):
        # breakpoint()
        if type(date) == datetime:
            return date.strftime(frmt_out)    
        return datetime.strptime(date, frmt_in).strftime(frmt_out)
    
    @classmethod
    def get_tools_df(cls, data):
        df = pd.DataFrame(columns=["user", "access_date"])
        # df = df.astype({"access_date": "datetime64[ns]"})
        for tuple in data:
            df.loc[len(df)] = tuple
            breakpoint()
        
        df["access_date"] = pd.to_datetime(df["access_date"])
        # breakpoint()
        return df
    
    @classmethod
    def get_marketplace_df(cls, data):
        df = pd.DataFrame(columns=['id', 'name', 'type', 'owner','creator','created', 'modified', 'nft', 'chainid', 'version', 'version_parent', 'license', 'overall_rating'])
        # df = df.astype({"created": "datetime64[ns]", "modified": "datetime64[ns]"})
        for tuple in data:
            df.loc[len(df)] = tuple
            breakpoint()
        df["created"] = pd.to_datetime(df["created"])
        df["modified"] = pd.to_datetime(df["modified"])
        return df
    
    

    