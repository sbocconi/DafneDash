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
    def get_user_tools_df(cls, data):
        df = pd.DataFrame(columns=["user", "access_date"])
        # df = df.astype({"access_date": "datetime64[ns]"})
        for tuple in data:
            df.loc[len(df)] = tuple
            # breakpoint()
        
        # df["access_date"] = pd.to_datetime(df["access_date"])
        # breakpoint()
        return df
    
    @classmethod
    def get_github_tools_df(cls, data):
        df = pd.DataFrame(columns=["name","tag","date","download_cnt"])
        # df = df.astype({"access_date": "datetime64[ns]"})
        for tuple in data:
            df.loc[len(df)] = tuple
            # breakpoint()
        
        # df["access_date"] = pd.to_datetime(df["access_date"])
        # breakpoint()
        return df
    
    @classmethod
    def get_mp_items_df(cls, data):
        df = pd.DataFrame(columns=['id', 'name', 'type', 'owner','creator','created', 'modified', 'nft', 'version', 'version_parent', 'license', 'overall_rating'])
        # df = df.astype({"created": "datetime64[ns]", "modified": "datetime64[ns]"})
        # breakpoint()
        for tuple in data:
            df.loc[len(df)] = tuple
            # breakpoint()
        # df["created"] = pd.to_datetime(df["created"])
        # df["modified"] = pd.to_datetime(df["modified"])
        return df
    
    @classmethod
    def get_mp_nfts_df(cls, data):
        df = pd.DataFrame(columns=['id', 'name', 'type', 'creator', 'creator_name', 'price', 'royalty_value', 'token_id', 'chainid'])
        df = df.astype({"creator_name": "str"})
        for tuple in data:
            df.loc[len(df)] = tuple
            # breakpoint()
        return df
    
    @classmethod
    def get_mp_ratings_df(cls, data):
        df = pd.DataFrame(columns=['id', 'item_id', 'user', 'rating', 'rated_at'])
        # df = df.astype({"rated_at": "datetime64[ns]"})
        # breakpoint()
        for tuple in data:
            df.loc[len(df)] = tuple
            # breakpoint()
        # df["rated_at"] = pd.to_datetime(df["created"])
        return df
    
    @classmethod
    def get_mp_reports_df(cls, data):
        df = pd.DataFrame(columns=['id', 'item_id', 'item_name', 'reason', 'reporter', 'action', 'report_received', 'warning_sent'])
        # df = df.astype({"report_received": "datetime64[ns]", "warning_sent": "datetime64[ns]"})
        # breakpoint()
        for tuple in data:
            df.loc[len(df)] = tuple
            # breakpoint()
        # df["report_received"] = pd.to_datetime(df["report_received"])
        # df["warning_sent"] = pd.to_datetime(df["warning_sent"])
        return df
    