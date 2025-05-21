import pandas as pd
import os
import hashlib
import pickle
from pathlib import Path
from datetime import datetime, timedelta
import copy
from typing import Any, Optional, List, Dict, Union, Tuple

from globals import CNTMGMT_KEY, MARKETPLACE_KEY, CNTMGMT_KEY, MARKETPLACE_KEY, USER_TOOLS_KEY, USAGE_TOOLS_KEY, IRCAM, GITHUB

class MetricsData:
    MTRCS_FILE = 'metrics.pkl'
 
    SYNTL_DT_FRMT = "%Y-%m-%dT%H:%M:%S.%f"
    GITHUB_DT_FRMT = '%Y-%m-%dT%H:%M:%SZ'
    CNT_DT_FRMT = "%Y-%m-%dT%H:%M:%SZ"
    CERTL_DT_FRMT = "/%m/%d/%Y"
    MP_DT_FRMT = '%Y-%m-%dT%H:%M:%S.%fZ'
    YEAR_DT_FRMT = "%Y"


    MAPPING = {
                f'{CNTMGMT_KEY} - events' : {'userid' : None, 'date': ['start', 'end']},
                f'{CNTMGMT_KEY} - contents' : {'userid' :'creator', 'date': ['creationDate']},
                f'{CNTMGMT_KEY} - contributors' : {'userid' :'userAdding', 'date': ['creationDate']},
                f'{CNTMGMT_KEY} - organizations' : {'userid' :'owner', 'date': ['creationDate']},
                f'{CNTMGMT_KEY} - proposals': {'userid' :'proposerName', 'date': ['creationDate']},
                f'{CNTMGMT_KEY} - proposals-votes' : {'userid' :'user', 'date': ['creationDate']},
                f'{CNTMGMT_KEY} - teams' : {'userid' :'owner', 'date': ['creationDate']},
                f'{CNTMGMT_KEY} - user-registrations' : {'userid' :'username', 'date': ['registrationTime'], 'format': CNT_DT_FRMT},
                f'{USER_TOOLS_KEY} - ObjectReconstuctionTool' : {'userid' :'user', 'date': ['access_date']},
                f'{USER_TOOLS_KEY} - PoseEstimationTool' : {'userid' :'user', 'date': ['access_date']},
                f'{USER_TOOLS_KEY} - VirtualAvatarPersonalizationTool' : {'userid' :'user', 'date': ['access_date']},
                f'{USER_TOOLS_KEY} - style_transfer' : {'userid' :'user', 'date': ['access_date']},
                f'{MARKETPLACE_KEY} - nft_items' : {'userid' :'creator_name', 'date': []},
                f'{MARKETPLACE_KEY} - marketplace_items' : {'userid' :'creator', 'date': ['created', 'modified']},
                f'{MARKETPLACE_KEY} - ratings' : {'userid' :'user', 'date': ['rated_at']},
                f'{MARKETPLACE_KEY} - reports' : {'userid' :'reporter', 'date': ['report_received', 'warning_sent']},
                f'{USAGE_TOOLS_KEY} - {IRCAM}' : {'userid' : None, 'date': ['Year'], 'format': YEAR_DT_FRMT},
                f'{USAGE_TOOLS_KEY} - {GITHUB}' : {'userid' :None, 'date': ['date']},
                }


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
        date_fields, format = MetricsData.get_dates_field(category, key)
        for date_field in date_fields:
            if date_field not in self.data_container[category][key]['data']:
                raise Exception(f'Field {date_field} is not in {category}-{key}')
            if format is not None:
                self.data_container[category][key]['data'][date_field] = pd.to_datetime(self.data_container[category][key]['data'][date_field], utc=True, format=format)
            else:
                self.data_container[category][key]['data'][date_field] = pd.to_datetime(self.data_container[category][key]['data'][date_field], utc=True)
        if len(date_fields) > 0:
            self.data_container[category][key]['data'] = self.data_container[category][key]['data'].sort_values(by=[date_fields[0]],ascending = True).reset_index(drop=True, inplace=False)

    @classmethod
    def get_dates_field(cls, key1, key2):
        dates = cls.MAPPING[f'{key1} - {key2}']['date']
        if 'format' in cls.MAPPING[f'{key1} - {key2}']:
            format = cls.MAPPING[f'{key1} - {key2}']['format']
        else:
            format = None
        return dates, format

    @classmethod
    def get_user_field(cls, key1, key2):
        userid = cls.MAPPING[f'{key1} - {key2}']['userid']
        return userid

    @staticmethod
    def encode_user(username):
        hashed_username = hashlib.blake2b(username.encode(), digest_size=12).hexdigest()
        return hashed_username

    @classmethod
    def get_subdata(cls, data, key):
        if key is not None:
            if key in data:
                data[key]['used'] = True
                return data[key]['data']
            else:
                raise Exception(f'key {key} not in data: {data.keys()}')
        else:
            raise Exception(f'Key is None')

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
    
    def save_metrics(self):
        with open(MetricsData.MTRCS_FILE, 'wb') as f: 
            pickle.dump(self.data_container, f)

    @classmethod
    def read_metrics(cls, refresh):
        metrics_file = Path(cls.MTRCS_FILE)
        if metrics_file.is_file():
            if refresh:
                os.rename(cls.MTRCS_FILE, f"{cls.MTRCS_FILE}.bak")
                return None
            else:
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
    
    @classmethod
    def get_cumul_scaled(cls, data, scaling:int=1, weighted_masks:List[Dict[List[bool], int]] = None):
        
        cnt_data = copy.deepcopy(data)
        # breakpoint()
    
        if weighted_masks is None:
            cnt_data['cumsum'] = 1
        else:
            for weighted_mask in weighted_masks:
                cnt_data.loc[weighted_mask['mask'],'cumsum'] = weighted_mask['weight']
                # breakpoint()
        cnt_data['cumsum'] = cnt_data['cumsum'].cumsum()*scaling

        return cnt_data

    def get_creators(self):
        data = self.get_data(MARKETPLACE_KEY, 'marketplace_items')
        # breakpoint()
        creators = set(data['creator'])
        return creators
        
        
    
    