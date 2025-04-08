import pandas as pd # type: ignore
from datetime import datetime, timedelta
import glob
from pathlib import Path

from datadumps import DataDumps
from metricsdata import MetricsData
from globals import DATAEXP_DIR, CNTMGMT_KEY, TOOLS_KEY, EVENT_FLNM

class FileDumps(DataDumps):

    
    def __init__(self):
        pass
        
    @classmethod
    def init(cls, metr_data):
        cls.set_metric_data(metr_data)
        cls.read_cntmgmt()
        cls.read_events()
        cls.assign_UC()
        cls.read_certhtools()

    @classmethod
    def read_cntmgmt(cls):
        xlsxfiles = [file for file in glob.iglob(f'{DATAEXP_DIR}/{CNTMGMT_KEY}/*.xlsx', recursive=False)]
        for xlsxfile in xlsxfiles:
            key = Path(xlsxfile).stem
            cls.set_keyed_data(CNTMGMT_KEY, key, pd.read_excel(xlsxfile).dropna(axis=1, how='all'))
    
    @classmethod
    def read_certhtools(cls):
        xlsxfiles = [file for file in glob.iglob(f'{DATAEXP_DIR}/{TOOLS_KEY}/*.xlsx', recursive=False)]
        for xlsxfile in xlsxfiles:
            content = pd.read_excel(xlsxfile).dropna(axis=1, how='all')
            data = {}
            for row in content.itertuples():
                if row.Index == 0:
                    continue
                username = MetricsData.encode_user(row[1])
                key = row[2]
                use_date = cls.convert_date_frmt(row[3],DataDumps.CERTL_DT_FRMT, DataDumps.CNT_DT_FRMT)
                if not key in data:
                    data[f'{key}'] = []
                data[f'{key}'].append([username,use_date])
            
            for key in data.keys():
                cls.set_keyed_data(TOOLS_KEY, key, data[f'{key}'])
            # breakpoint()

    @classmethod
    def read_events(cls):
        
        cls.set_keyed_data(CNTMGMT_KEY, EVENT_FLNM, pd.read_csv(f'{DATAEXP_DIR}/{EVENT_FLNM}.csv', parse_dates=['start','end']))
        
        data = cls.get_keyed_data(CNTMGMT_KEY, EVENT_FLNM)
        # Check there are no overlapping periods
        len_df = data.shape[0]
        for idx1, row1 in data.iterrows():
            for idx2 in range(idx1+1, len_df):
                # breakpoint()
                row2 = data.iloc[idx2]
                if (row1.start <= row2.start <=row1.end) or \
                    (row1.start <= row2.end <=row1.end) or \
                    (row2.start <= row1.start <=row2.end) or \
                    (row2.start <= row1.start <=row2.end):
                    # breakpoint()
                    raise Exception(f'Ranges {row1.start} / {row1.end} and {row2.start} / {row2.end} overlap')
        # breakpoint()

    @classmethod
    def assign_UC(cls):
        data = cls.get_keyed_data(CNTMGMT_KEY, 'user-registrations')
        data['registrationTime'] = pd.to_datetime(data['registrationTime'], format=cls.CNT_DT_FRMT)
        ucs = []
        event_data = cls.get_keyed_data(CNTMGMT_KEY, EVENT_FLNM)
        for reg_row in data.itertuples():
            found = False
            # breakpoint()
            for uc_row in event_data.itertuples():
                if uc_row.start <= reg_row.registrationTime <= uc_row.end:
                    # breakpoint()
                    ucs.append(uc_row.UC)
                    found = True
                    break
            if not found:
                ucs.append(-1)
                
        data['UC'] = ucs
        # breakpoint()

    @classmethod
    def min_date(cls):
        data = cls.get_keyed_data(CNTMGMT_KEY, 'user-registrations')
        return data.registrationTime.min().replace(day=1,hour=0,minute=0,second=0)
    
    @classmethod
    def max_date(cls):
        data = cls.get_keyed_data(CNTMGMT_KEY, 'user-registrations')
        last_day = data.registrationTime.max().replace(day=pd.Timestamp(data.registrationTime.max()).days_in_month)
        first_day = last_day + timedelta(days=1)
        return first_day.replace(day=1,hour=0,minute=0,second=0)
        # return parse_date(data['user-registrations'].registrationTime.max()).replace(day=pd.Timestamp(data['user-registrations'].registrationTime.max()).days_in_month,hour=23,minute=59,second=59)

    @classmethod
    def min_ts(cls):
        return int(pd.Timestamp(cls.min_date()).timestamp())

    @classmethod
    def max_ts(cls):
        return int(pd.Timestamp(cls.max_date()).timestamp())
    
    @classmethod
    def parse_date(cls, date_str):
        return datetime.strptime(date_str, cls.CNT_DT_FRMT)


