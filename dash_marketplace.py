from dash import Dash, html, dash_table, dependencies, dcc, callback, Output, Input # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore

from globals import SLD_ID, MARKETPLACE_GRAPH_ID, thumbs

class DashMarketPlace:
    SCALING = 10

    TOT_COL = 'black'
    NTF_COL = 'red'
    FREE_COL = 'green'
    CRT_COL = 'blue'


    def __init__(self, marketplace_data, min, max, app):
        # self.marketplace_data = DashMarketPlace.to_pd(marketplace_data)
        self.marketplace_data = marketplace_data
        # breakpoint()
        self.creators = set(self.marketplace_data['marketplace_items']['data']['creator'])
        self.items_per_creator()
        self.work_reposiory_items = len(self.marketplace_data['marketplace_items']['data'].loc[self.marketplace_data['marketplace_items']['data']['type']=='work_repository'])
        self.type_items = set(self.marketplace_data['marketplace_items']['data']['type'])
        # breakpoint()
        self.min = min
        self.max = max
        self.app = app
        self.app.callback(
            dependencies.Output(MARKETPLACE_GRAPH_ID, "figure"),
            dependencies.Input(SLD_ID, "value")
            )(self.marketplace_tl_updt)
    
    @classmethod
    def to_pd(cls, data):
        df = pd.DataFrame(columns=['id', 'name', 'type', 'owner','creator','created', 'modified', 'nft', 'chainid', 'version', 'version_parent', 'license', 'overall_rating'])
        # breakpoint()
        for key in data.keys():
            for arr in data[key]['data']:
                # breakpoint()
                df.loc[len(df)] = arr
        # breakpoint()
        return df
    
    def token_generating_creators(self, start, end):
        df = pd.DataFrame(columns=['date','nr_creators'])
        start_date = pd.to_datetime(start, unit='s', utc=True)
        end_date = pd.to_datetime(end, unit='s', utc=True)
        pivot = start_date
        while pivot < end_date:
            mask = (pivot <= self.marketplace_data['marketplace_items']['data']['created']) &  (self.marketplace_data['marketplace_items']['data']['created'] < pivot + pd.Timedelta(days=1))
            unique_creators = set(self.marketplace_data['marketplace_items']['data']['creator'].loc[mask])
            df.loc[len(df)] = [pivot, len(unique_creators)*self.SCALING]
            pivot = pivot + pd.Timedelta(days=1)

        return df
    
    def marketplace_tl_updt(self,tss):
        if tss == None:
            start = self.min
            end = self.max
        else:
            start = tss[0]
            end = tss[1]
        # breakpoint()
        dt_idx = pd.DatetimeIndex(self.marketplace_data['marketplace_items']['data'].created).view('int64') // 10**9
        mask = (dt_idx > start) & (dt_idx <= end)
        all_data = self.marketplace_data['marketplace_items']['data'].loc[mask]
        nft_data = self.marketplace_data['marketplace_items']['data'].loc[mask & (~self.marketplace_data['marketplace_items']['data']['nft'].isnull())]
        free_data = self.marketplace_data['marketplace_items']['data'].loc[mask & (self.marketplace_data['marketplace_items']['data']['nft'].isnull())]
        # daily_token_creators = self.token_generating_creators(start, end)
        
        # breakpoint()
        fig = px.ecdf(all_data, x='created', ecdfmode="standard", ecdfnorm=None, markers=True, color_discrete_sequence=[self.TOT_COL])
        # breakpoint()
        nft_graph = px.ecdf(nft_data, x='created', ecdfmode="standard", ecdfnorm=None, markers=True, color_discrete_sequence=[self.NTF_COL])
        free_graph = px.ecdf(free_data, x='created', ecdfmode="standard", ecdfnorm=None, markers=True, color_discrete_sequence=[self.FREE_COL])
        # creator_graph = px.line(daily_token_creators, x='date', y="nr_creators")
        
        for trace in nft_graph.data:
            fig.add_trace(trace)
        for trace in free_graph.data:
            fig.add_trace(trace)
        # for trace in creator_graph.data:
        #     fig.add_trace(trace)
        
        # breakpoint()
        
        # if start == self.min and end == self.max:
        #     fig.add_hline(y=len(self.creators)/50*self.SCALING, line_dash="dashdot", line_width=0.5, line_color=self.TOT_COL,
        #         annotation_text="KPI_9 Creators generating tokens daily >2%", 
        #         annotation_position="top left",
        #         annotation_font_size=15,
        #         annotation_font_color=self.TOT_COL
        #         )
            
        return fig

    def items_per_creator(self):
        tot = 0
        self.tot_users_zero = 0
        self.tot_users_one = 0
        self.tot_users_more = 0
        for creator in self.creators:
            items_per_creator = self.marketplace_data['marketplace_items']['data'].loc[self.marketplace_data['marketplace_items']['data']['creator'] == creator]
            if len(items_per_creator) == 0:
                self.tot_users_zero = self.tot_users_zero + 1
            else:
                if len(items_per_creator) == 1:
                    self.tot_users_one = self.tot_users_one + 1
                else:
                    self.tot_users_more = self.tot_users_more + 1
            tot = tot + len(items_per_creator)
        self.avg_item_per_creator = tot / len(self.creators)
        # breakpoint()
    
        
    
    def get_creators(self):
        return self.creators

    def as_html(self):
        
        return html.Div(
                [
                    html.H2("Marketplace Items"),
                    html.H3(f"{thumbs(self.tot_users_zero==0 and self.tot_users_one==0)} KPI_7 Number of items shared by creators > 1 per creator"),
                    html.H3(f"{thumbs(self.work_reposiory_items>5)} KPI_32 Short term: Number of artwork production setups (work repositories) published > 5"),
                    html.P(f"Total creators: {len(self.creators)}, average items per creator: {self.avg_item_per_creator}"),
                    html.P(f"Users with no items: {self.tot_users_zero}, one item: {self.tot_users_one}, more items: {self.tot_users_more}"),
                    html.P(f"Type of items published: {self.type_items}"),
                    dcc.Graph(id=MARKETPLACE_GRAPH_ID)
                ],
            )

