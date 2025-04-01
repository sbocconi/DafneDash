import pandas as pd # type: ignore
from datetime import datetime, timedelta
import glob
from pathlib import Path


def read_xls(xls_dir):
    data = {}
    xlsxfiles = [file for file in glob.iglob(f'{xls_dir}/*.xlsx', recursive=False)]
    for xlsxfile in xlsxfiles:
        key = Path(xlsxfile).stem
        data[key] = {
            'data' : pd.read_excel(xlsxfile).dropna(axis=1, how='all'),
            'used' : False
        }
    return data

class DataDumps:
    DT_FRMT = "%Y-%m-%dT%H:%M:%SZ"
    data = {}
    dir = ""
    event = ""
    
    def __init__(self):
        pass
        
    @classmethod
    def init(cls, dir, event):
        cls.dir = dir
        cls.event = event
        cls.read_data()
        cls.read_events()
        cls.assign_UC()

    @classmethod
    def read_data(cls):
        
        cls.data = read_xls(cls.dir)

    @classmethod
    def read_events(cls):
        cls.data[cls.event] = {}
        cls.data[cls.event]['data'] = pd.read_csv(f'{cls.dir}/{cls.event}.csv', parse_dates=['start','end'])
        df = cls.data[cls.event]['data']

        len_df = df.shape[0]
        for idx1, row1 in df.iterrows():
            for idx2 in range(idx1+1, len_df):
                # breakpoint()
                row2 = df.iloc[idx2]
                if (row1.start <= row2.start <=row1.end) or \
                    (row1.start <= row2.end <=row1.end) or \
                    (row2.start <= row1.start <=row2.end) or \
                    (row2.start <= row1.start <=row2.end):
                    # breakpoint()
                    raise Exception(f'Ranges {row1.start} / {row1.end} and {row2.start} / {row2.end} overlap')
        # breakpoint()

    @classmethod
    def assign_UC(cls):
        cls.data['user-registrations']['data']['registrationTime'] = pd.to_datetime(cls.data['user-registrations']['data']['registrationTime'], format=DataDumps.DT_FRMT)
        ucs = []
        for reg_row in cls.data['user-registrations']['data'].itertuples():
            found = False
            for uc_row in cls.data[cls.event]['data'].itertuples():
                if uc_row.start <= reg_row.registrationTime <= uc_row.end:
                    # breakpoint()
                    ucs.append(uc_row.UC)
                    found = True
                    break
            if not found:
                ucs.append(-1)
                
        cls.data['user-registrations']['data']['UC'] = ucs
        # breakpoint()

    @classmethod
    def get_data(cls, key):
        if key in cls.data:
            cls.data[key]['used'] = True
            return cls.data[key]['data']
        else:
            raise Exception(f'Key {key} not in data: {cls.data.keys()}')
    
    @classmethod
    def all_used(cls):
        are_all_used = True
        for key in cls.data:
            if 'used' in cls.data[key] and not cls.data[key]['used']:
                print(f'Key {key} not used')
                are_all_used = False
        return are_all_used

    @staticmethod  
    def parse_date(date_str):
        return datetime.strptime(date_str, DataDumps.DT_FRMT)
    
    @classmethod
    def min_date(cls):
        return cls.data['user-registrations']['data'].registrationTime.min().replace(day=1,hour=0,minute=0,second=0)
    
    @classmethod
    def max_date(cls):
        last_day = cls.data['user-registrations']['data'].registrationTime.max().replace(day=pd.Timestamp(cls.data['user-registrations']['data'].registrationTime.max()).days_in_month)
        first_day = last_day + timedelta(days=1)
        return first_day.replace(day=1,hour=0,minute=0,second=0)
        # return parse_date(data['user-registrations'].registrationTime.max()).replace(day=pd.Timestamp(data['user-registrations'].registrationTime.max()).days_in_month,hour=23,minute=59,second=59)

    @classmethod
    def min_ts(cls):
        return int(pd.Timestamp(cls.min_date()).timestamp())

    @classmethod
    def max_ts(cls):
        return int(pd.Timestamp(cls.max_date()).timestamp())

