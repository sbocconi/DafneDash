import pandas as pd # type: ignore
from datetime import datetime, timedelta
import requests
from requests.exceptions import RequestException

from datadumps import DataDumps, read_yaml
from metricsdata import MetricsData


class APIDumps(DataDumps):

    def __init__(self):
        pass
        
    @classmethod
    def init(cls, metr_data):
        cls.set_metric_data(metr_data)
        cls.read_tools_data()

    @classmethod
    def do_request(cls, url, headers={}, data={}):
        try:
            response = requests.request("GET", url, headers=headers, data=data)
            return response.json()
        except RequestException as e:
            print(e)
            # Handle exception, for the moment we raise
            raise Exception(e)

    @classmethod
    def read_tools_data(cls):

        settings = read_yaml()['tools']
 
        for tool in settings:
            # breakpoint()
            tool_name = next(iter(tool))
            tool_url = tool[f'{tool_name}']['url']
            tool_endpoint = tool[f'{tool_name}']['endpoint']
            if not tool[f'{tool_name}']['auth']:
                try:
                    response = cls.do_request(f"{tool_url}/{tool_endpoint}")
                    data = []
                    for usage in response['usages']:
                        username = usage['username'] if tool[f'{tool_name}']['encoded_users'] else MetricsData.encode_user(usage['username'])
                        date = cls.convert_date_frmt(usage['timestamp'])
                        data.append([username,date])
                    cls.set_keyed_data(tool_name, data)
                    # breakpoint()
                except Exception as e:
                    print(e)
                    continue
            else:
                raise Exception('Auth request not yet implemented')

    @classmethod
    def convert_date_frmt(cls, date_str):
        return datetime.strptime(date_str, DataDumps.API_DT_FRMT).strftime(DataDumps.FILE_DT_FRMT)
