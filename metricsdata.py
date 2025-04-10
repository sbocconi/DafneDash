import pandas as pd
import hashlib
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from globals import CNTMGMT_KEY, MARKETPLACE_KEY

class MetricsData:
    MTRCS_FILE = 'metrics.pkl'

    def __init__(self, data=None):
        if data is None:
            self.data_container = {}
        else:
            self.data_container = data

    def create_keyed_data(self, category, key, data_to_set=None):
        if category not in self.data_container:
            self.data_container[category] = {}
        self.data_container[category][key] = {
                'data' : data_to_set if data_to_set is not None else {},
                'used' : False
            }


    @staticmethod
    def encode_user(username):
        hashed_username = hashlib.blake2b(username.encode(), digest_size=12).hexdigest()
        return hashed_username


    def get_data(self, category, key=None):
        
        if category in self.data_container:
            if key is not None:
                if key in self.data_container[category]:
                    self.data_container[category][key]['used'] = True
                    return self.data_container[category][key]['data']
                else:
                    raise Exception(f'key {key} not in data: {self.data_container[category].keys()}')
            else:
                return self.data_container[category]
        else:
            raise Exception(f'Category {category} not in data: {self.data_container.keys()}')

        

    def set_data(self, category, key, data):
        if not (category in self.data_container and key in self.data_container[category]):
            self.create_keyed_data(category, key, data)
        else:
            self.data_container[category][key]['data'] = data

    def all_used(self):
        are_all_used = True
        for category in self.data_container:
            for key in self.data_container[category]:
                if 'used' in self.data_container[category][key] and not self.data_container[category][key]['used']:
                    print(f'Key {key} in category {category} not used')
                    are_all_used = False
        return are_all_used
    
    def save_data(self):
        with open(self.MTRCS_FILE, 'wb') as f: 
            pickle.dump(self.data_container, f)

    @classmethod
    def get_metrics(cls):
        metrics_file = Path(cls.MTRCS_FILE)
        if metrics_file.is_file():
            with open(cls.MTRCS_FILE, 'rb') as f: 
                data = pickle.load(f)
            # breakpoint()
            return MetricsData(data)
        return None

    @classmethod
    def start_following_month(cls, date):
        last_day = date.replace(day=pd.Timestamp(date).days_in_month)
        first_day = last_day + timedelta(days=1)
        return first_day.replace(day=1,hour=0,minute=0,second=0)

    @classmethod
    def now(cls):
        return int(cls.start_following_month(pd.Timestamp.now()).timestamp())

    def min_date(self):
        data = self.get_data(CNTMGMT_KEY, 'user-registrations')
        return data.registrationTime.min().replace(day=1,hour=0,minute=0,second=0)
    
    def max_date(self):
        data = self.get_data(MARKETPLACE_KEY, 'marketplace_items')
        # breakpoint()
        return self.start_following_month(data.modified.max())
        # return parse_date(data['user-registrations'].registrationTime.max()).replace(day=pd.Timestamp(data['user-registrations'].registrationTime.max()).days_in_month,hour=23,minute=59,second=59)

    def min_ts(self):
        return int(pd.Timestamp(self.min_date()).timestamp())

    def max_ts(self):
        return int(pd.Timestamp(self.max_date()).timestamp())
    
    