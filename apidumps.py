import pandas as pd # type: ignore
import requests
from requests.exceptions import RequestException

from datadumps import DataDumps, read_yaml
from metricsdata import MetricsData
from globals import TOOLS_KEY, MARKETPLACE_KEY
from dafnekeycloak import DafneKeycloak

class APIDumps(DataDumps):

    def __init__(self):
        pass
        
    @classmethod
    def init(cls, metr_data):
        cls.set_metric_data(metr_data)
        cls.read_tools_api_data()
        # breakpoint()
        cls.token = DafneKeycloak().get_access_token()
        cls.read_marketplace_data()

    @classmethod
    def do_request(cls, url, headers={}, data={}):
        try:
            response = requests.request("GET", url, headers=headers, data=data)
            # breakpoint()
            if response.status_code == requests.codes.ok:
                return response.json()
            else:
                raise Exception(f"Request {url} with headers {headers} returned {response.status_code}")
        except RequestException as e:
            print(f"Not handling yet Exception {e}")
            # Handle exception, for the moment we raise
            raise Exception(e)

    @classmethod
    def read_tools_api_data(cls):

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
                        date = cls.convert_date_frmt(usage['timestamp'],DataDumps.SYNTL_DT_FRMT, DataDumps.CNT_DT_FRMT)
                        data.append([username,date])
                    cls.set_keyed_data(TOOLS_KEY, tool_name, data)
                    # breakpoint()
                except Exception as e:
                    print(e)
                    continue
            else:
                raise Exception('Auth request not yet implemented')
            
    @classmethod
    def read_marketplace_data(cls):
        settings = read_yaml()['marketplace']
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {cls.token}'
        }
        mp_api_url = settings['url']
        for mp_api in settings['api']:
            mp_api_name = next(iter(mp_api))
            mp_api_endpoint = mp_api[f'{mp_api_name}']['endpoint']
            # breakpoint()

            try:
                response = cls.do_request(f"{mp_api_url}/{mp_api_endpoint}", headers=headers)
                data = []
                for item in response:
                    # breakpoint()
                    id = item['id']
                    item_name = item['name']
                    type = item['type']
                    owner = item['owner_name'] if mp_api[f'{mp_api_name}']['encoded_users'] else MetricsData.encode_user(item['owner_name'])
                    created_date = cls.convert_date_frmt(item['created'],DataDumps.MP_DT_FRMT, DataDumps.CNT_DT_FRMT)
                    modified_date = cls.convert_date_frmt(item['modified'],DataDumps.MP_DT_FRMT, DataDumps.CNT_DT_FRMT)
                    nft = item['nft']
                    if nft:
                        # breakpoint()
                        nft_response = cls.do_request(f"{mp_api_url}/nft/{nft}", headers=headers)
                        if not nft_response['creator_name']:
                            print(f"Warning: item {id} with nft {nft} has null creator name")
                            creator = owner
                        else:    
                            creator = nft_response['creator_name'] if mp_api[f'{mp_api_name}']['encoded_users'] else MetricsData.encode_user(nft_response['creator_name'])
                    else:
                        creator = owner
                    chainid = item['chainid']
                    version = item['version']
                    version_parent = item['version_parent']
                    license = item['license']
                    overall_rating = item['overall_rating'] if item['overall_rating'] is not None else 0

                    data.append([id, item_name, type, owner, creator, created_date, modified_date, nft, chainid, version, version_parent, license, overall_rating])
                cls.set_keyed_data(MARKETPLACE_KEY, mp_api_name, data)
                # breakpoint()
                
            except Exception as e:
                print(e)
                continue


