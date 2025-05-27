import pandas as pd # type: ignore
import numpy as np

import requests
from requests.exceptions import RequestException

from datadumps import DataDumps, read_yaml
from metricsdata import MetricsData
from globals import USER_TOOLS_KEY, USAGE_TOOLS_KEY, MARKETPLACE_KEY, GITHUB
from dafnekeycloak import DafneKeycloak

class APIDumps(DataDumps):

    user_map = {}

    def __init__(self):
        pass
        
    @classmethod
    def init(cls, metr_data):
        cls.set_metric_data(metr_data)
        cls.read_dafne_tools_data()
        cls.read_github_tools_data()
        # breakpoint()
        cls.token = DafneKeycloak().get_access_token()
        cls.read_nft_items()
        cls.read_marketplace_items()
        cls.read_ratings()
        cls.read_reports()

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
    def read_dafne_tools_data(cls):

        settings = read_yaml()['dafne_tools']
 
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
                        date = cls.convert_date_frmt(usage['timestamp'],MetricsData.SYNTL_DT_FRMT, MetricsData.CNT_DT_FRMT)
                        data.append([username,date])
                    cls.set_keyed_data(USER_TOOLS_KEY, tool_name, cls.get_user_tools_df(data))
                    # breakpoint()
                except Exception as e:
                    print(e)
                    continue
            else:
                raise Exception('Auth request not yet implemented')

    @classmethod
    def read_github_tools_data(cls):

        settings = read_yaml()['github_tools']
        
        base_url = settings['url']
        h = {"Accept": "application/vnd.github.v3+json"}
        data = []
        for tool in settings['tools']:
            # breakpoint()
            tool_name = next(iter(tool))
            tool_owner = tool[tool_name]['owner']
            tool_repo = tool[tool_name]['repo']
            
            try:
                response = cls.do_request(f"{base_url}/{tool_owner}/{tool_repo}/releases?per_page=100", headers=h)
                
                # breakpoint()
                for rel in response:
                    # breakpoint()
                    tag = rel['tag_name']
                    date = cls.convert_date_frmt(rel['published_at'],MetricsData.GITHUB_DT_FRMT, MetricsData.CNT_DT_FRMT)
                    download_cnt = 0
                    for asset in rel['assets']:
                        # breakpoint()
                        filename = asset['name'] 
                        download_cnt = download_cnt + asset['download_count']
                    
                    data.append([tool_name,tag,date,download_cnt])
                # breakpoint()
            except Exception as e:
                # breakpoint()
                print(f"Exception {e}")
                continue
        # breakpoint()
        cls.set_keyed_data(USAGE_TOOLS_KEY, GITHUB, cls.get_github_tools_df(data))
            
    
    @classmethod
    def get_header(cls, auth):
        if auth:
            return {
                'Accept': 'application/json',
                'Authorization': f'Bearer {cls.token}'
            }
        return {}
     
    @classmethod
    def read_nft_items(cls):
        settings = read_yaml()['marketplace']

        mp_api_url = settings['url']
        
        mp_api_name = 'nft_items'
        mp_api = settings[f"{mp_api_name}"]
        mp_api_endpoint = mp_api['endpoint']
        headers = cls.get_header(mp_api['auth'])
        # breakpoint()

        try:
            response = cls.do_request(f"{mp_api_url}/{mp_api_endpoint}", headers=headers)
            data = []
            for item in response:
                # breakpoint()
                id = item['id']
                item_name = item['name']
                creator = item['creator']
                if not item['creator_name']:
                    print(f"Warning: nft {id} has null creator name, creator {creator}")
                    creator_name = None
                else:    
                    creator_name = item['creator_name'] if mp_api['encoded_users'] else MetricsData.encode_user(item['creator_name'])
                price = item['price']
                royalty_value = item['royalty_value'] if item['royalty_value'] else np.nan
                token_id = item['token_id']
                chainid = item['chainid']

                data.append([id, item_name, creator, creator_name, price, royalty_value, token_id, chainid])
            cls.set_keyed_data(MARKETPLACE_KEY, mp_api_name, cls.get_mp_nfts_df(data))
            # breakpoint()
            
        except Exception as e:
            print(e)
            raise Exception(e)

    @classmethod
    def read_marketplace_items(cls):
        settings = read_yaml()['marketplace']
        
        mp_api_url = settings['url']
        
        mp_api_name = 'marketplace_items'
        mp_api = settings[f"{mp_api_name}"]
        mp_api_endpoint = mp_api['endpoint']

        headers = cls.get_header(mp_api['auth'])

        nfts = cls.get_keyed_data(MARKETPLACE_KEY, 'nft_items')
        # breakpoint()

        try:
            response = cls.do_request(f"{mp_api_url}/{mp_api_endpoint}", headers=headers)
            data = []
            for item in response:
                # breakpoint()
                id = item['id']
                item_name = item['name']
                type = item['type']
                owner = item['owner_name'] if mp_api['encoded_users'] else MetricsData.encode_user(item['owner_name'])
                if not f"{item['owner']}" in cls.user_map:
                    cls.user_map[f"{item['owner']}"] = owner

                created_date = cls.convert_date_frmt(item['created'],MetricsData.MP_DT_FRMT, MetricsData.CNT_DT_FRMT)
                modified_date = cls.convert_date_frmt(item['modified'],MetricsData.MP_DT_FRMT, MetricsData.CNT_DT_FRMT)
                nft = item['nft']
                if nft:
                    # breakpoint()
                    creator = nfts.loc[nfts.id == nft]['creator_name'].item()
                    if creator == None:
                        print(f"Warning: nft {nft} has null creator name, assuming creator is owner {owner}")
                        creator = owner
                        # breakpoint()
                else:
                    creator = owner
                version = item['version']
                version_parent = item['version_parent']
                license = item['license']
                overall_rating = item['overall_rating'] if item['overall_rating'] is not None else 0

                data.append([id, item_name, type, owner, creator, created_date, modified_date, nft, version, version_parent, license, overall_rating])
            cls.set_keyed_data(MARKETPLACE_KEY, mp_api_name, cls.get_mp_items_df(data))
            # breakpoint()
            
        except Exception as e:
            print(e)
            raise Exception(e)
    
    @classmethod
    def read_ratings(cls):
        settings = read_yaml()['marketplace']
        
        mp_api_url = settings['url']
        
        mp_api_name = 'ratings'
        mp_api = settings[f"{mp_api_name}"]
        mp_api_endpoint = mp_api['endpoint']

        headers = cls.get_header(mp_api['auth'])

        # breakpoint()

        try:
            response = cls.do_request(f"{mp_api_url}/{mp_api_endpoint}", headers=headers)
            data = []
            for item in response:
                # breakpoint()
                id = item['id']
                item_id = item['item']
                # user = item['user'] if mp_api['encoded_users'] else MetricsData.encode_user(item['user'])
                user = cls.user_map[f"{item['user']}"]
                rating = item['rating']
                rated_at = cls.convert_date_frmt(item['rated_at'],MetricsData.MP_DT_FRMT, MetricsData.CNT_DT_FRMT)

                data.append([id, item_id, user, rating, rated_at])
            cls.set_keyed_data(MARKETPLACE_KEY, mp_api_name, cls.get_mp_ratings_df(data))
            # breakpoint()
            
        except Exception as e:
            print(e)
            raise Exception(e)

    @classmethod
    def read_reports(cls):
        settings = read_yaml()['marketplace']
        
        mp_api_url = settings['url']
        
        mp_api_name = 'reports'
        mp_api = settings[f"{mp_api_name}"]
        mp_api_endpoint = mp_api['endpoint']

        headers = cls.get_header(mp_api['auth'])

        # breakpoint()

        try:
            response = cls.do_request(f"{mp_api_url}/{mp_api_endpoint}", headers=headers)
            data = []
            for item in response:
                # breakpoint()
                id = item['id']
                item_id = item['item']
                item_name = item['item_name']
                reason = item['reason']
                reporter = cls.user_map[f"{item['reporter']}"]
                action = item['action']
                report_received = cls.convert_date_frmt(item['report_received'],MetricsData.MP_DT_FRMT, MetricsData.CNT_DT_FRMT)
                # breakpoint()
                if item['warning_sent'] is not None:
                    warning_sent = cls.convert_date_frmt(item['warning_sent'],MetricsData.MP_DT_FRMT, MetricsData.CNT_DT_FRMT)
                else:
                    warning_sent = None

                data.append([id, item_id, item_name, reason, reporter, action, report_received, warning_sent])
            cls.set_keyed_data(MARKETPLACE_KEY, mp_api_name, cls.get_mp_reports_df(data))
            # breakpoint()
            
        except Exception as e:
            print(e)
            raise Exception(e)
