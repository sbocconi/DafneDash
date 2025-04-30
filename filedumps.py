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
                tool = row[2]
                use_date = cls.convert_date_frmt(row[3],MetricsData.CERTL_DT_FRMT, MetricsData.CNT_DT_FRMT)
                if not tool in data:
                    data[f'{tool}'] = []
                data[f'{tool}'].append([username,use_date])
                # data.append([key,username,use_date])
            for key in data.keys():
                cls.set_keyed_data(TOOLS_KEY, key, cls.get_tools_df(data[f'{key}']))
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
                if (row1.start >= row1.end) or \
                    (row1.start <= row2.start <=row1.end) or \
                    (row1.start <= row2.end <=row1.end) or \
                    (row2.start <= row1.start <=row2.end) or \
                    (row2.start <= row1.start <=row2.end):
                    # breakpoint()
                    raise Exception(f'Ranges {row1.start} / {row1.end} and {row2.start} / {row2.end} overlap')
        # breakpoint()

    @classmethod
    def assign_UC(cls):
        data = cls.get_keyed_data(CNTMGMT_KEY, 'user-registrations')
        # data['registrationTime'] = pd.to_datetime(data['registrationTime'], format=cls.CNT_DT_FRMT)
        # breakpoint()
        ucs = []
        counts = []
        event_data = cls.get_keyed_data(CNTMGMT_KEY, EVENT_FLNM)
        for reg_row in data.itertuples():
            found = False
            # breakpoint()
            for uc_row in event_data.itertuples():
                # breakpoint()
                if uc_row.start <= reg_row.registrationTime <= uc_row.end:
                    # breakpoint()
                    ucs.append(uc_row.UC)
                    found = True
                    counts.append(1)
                    break
            if not found:
                ucs.append(-1)
                counts.append(1/3)
                
        data['UC'] = ucs
        data['counts'] = counts
        # breakpoint()
    
    @classmethod
    def parse_date(cls, date_str):
        return datetime.strptime(date_str, cls.CNT_DT_FRMT)


