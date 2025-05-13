import pandas as pd # type: ignore
from datetime import datetime, timedelta
import glob
from pathlib import Path

from datadumps import DataDumps
from metricsdata import MetricsData
from globals import DATAEXP_DIR, CNTMGMT_KEY, USER_TOOLS_KEY, USAGE_TOOLS_KEY, EVENT_FLNM, IRCAM

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
        cls.read_ircamtools()

    @classmethod
    def read_cntmgmt(cls):
        xlsxfiles = [file for file in glob.iglob(f'{DATAEXP_DIR}/{CNTMGMT_KEY}/*.xlsx', recursive=False)]
        for xlsxfile in xlsxfiles:
            key = Path(xlsxfile).stem
            cls.set_keyed_data(CNTMGMT_KEY, key, pd.read_excel(xlsxfile).dropna(axis=1, how='all'))
    
    @classmethod
    def read_certhtools(cls):
        xlsxfiles = [file for file in glob.iglob(f'{DATAEXP_DIR}/{USER_TOOLS_KEY}/*.xlsx', recursive=False)]
        for xlsxfile in xlsxfiles:
            if len(pd.ExcelFile(xlsxfile).sheet_names) != 1:
                raise Exception(f"Unexpected multile tabs in {xlsxfile}: {pd.ExcelFile(xlsxfile).sheet_names}")
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
                cls.set_keyed_data(USER_TOOLS_KEY, key, cls.get_user_tools_df(data[f'{key}']))
            # breakpoint()
    
    @classmethod
    def read_ircamtools(cls):
        xlsxfiles = [file for file in glob.iglob(f'{DATAEXP_DIR}/{USAGE_TOOLS_KEY}/*.xlsx', recursive=False)]
        for xlsxfile in xlsxfiles:
            if len(pd.ExcelFile(xlsxfile).sheet_names) != 2:
                raise Exception(f"Unexpected multile tabs in {xlsxfile}: {pd.ExcelFile(xlsxfile).sheet_names}")
            tabs = pd.read_excel(xlsxfile, sheet_name=None)
            first = True
            prfx = 'IRCAM Forum Software '
            for key in tabs.keys():
                # breakpoint()
                content = tabs[key].dropna(axis=1, how='all')
                value = key[len(prfx):]
                cnt_long = content.drop(columns=content.columns[-1]).melt(
                    id_vars=content.columns[0],
                    # value_vars=list(content.columns[1:-1]),
                    var_name='Year',
                    value_name=value
                )
                if first:
                    data = cnt_long
                    first = False
                else:
                    data = data.merge(cnt_long, how='outer')
            # breakpoint()
                
            
            cls.set_keyed_data(USAGE_TOOLS_KEY, IRCAM, data)
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
                    break
            if not found:
                ucs.append(-1)
                
        data['UC'] = ucs
        # breakpoint()
    
    @classmethod
    def parse_date(cls, date_str):
        return datetime.strptime(date_str, cls.CNT_DT_FRMT)


