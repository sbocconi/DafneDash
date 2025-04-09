from dash import Dash, html, dash_table, dependencies, dcc, callback, Output, Input # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore

from globals import SLD_ID, MARKETPLACE_GRAPH_ID

class DashMarketPlace:
    TOT_COL = 'black'
    NTF_COL = 'red'
    FREE_COL = 'green'


    def __init__(self, marketplace_data, min, max, app):
        self.marketplace_data = DashMarketPlace.to_pd(marketplace_data)
        self.creators = set(self.marketplace_data['creator_name'])
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
        df = pd.DataFrame(columns=['id', 'name', 'type', 'owner_name','creator_name','created', 'modified', 'nft', 'chainid', 'version', 'version_parent', 'license', 'overall_rating'])
        # breakpoint()
        for key in data.keys():
            for arr in data[key]['data']:
                # breakpoint()
                df.loc[len(df)] = arr
        # breakpoint()
        return df
    
    
    def marketplace_tl_updt(self,tss):
        if tss == None:
            start = self.min
            end = self.max
        else:
            start = tss[0]
            end = tss[1]
        # breakpoint()
        dt_idx = pd.DatetimeIndex(self.marketplace_data.created).view('int64') // 10**9
        mask = (dt_idx > start) & (dt_idx <= end)
        nft_data = self.marketplace_data.loc[mask & (~self.marketplace_data['nft'].isnull())]
        free_data = self.marketplace_data.loc[mask & (self.marketplace_data['nft'].isnull())]
        
        # breakpoint()
        fig = px.ecdf(self.marketplace_data.loc[mask], x='created', ecdfmode="standard", ecdfnorm=None, markers=True, color_discrete_sequence=[self.TOT_COL])
        # breakpoint()
        nft_graph = px.ecdf(nft_data, x='created', ecdfmode="standard", ecdfnorm=None, markers=True, color_discrete_sequence=[self.NTF_COL])
        free_graph = px.ecdf(free_data, x='created', ecdfmode="standard", ecdfnorm=None, markers=True, color_discrete_sequence=[self.FREE_COL])
        
        for trace in nft_graph.data:
            fig.add_trace(trace)
        for trace in free_graph.data:
            fig.add_trace(trace)
        
        # breakpoint()
        
        # if start == self.min and end == self.max:
        #     fig.add_hline(y=2, line_dash="dashdot", line_width=0.5, line_color=self.TOT_COL,
        #         annotation_text="KPI 12: Total Nr. Users", 
        #         annotation_position="bottom left",
        #         annotation_font_size=15,
        #         annotation_font_color=self.TOT_COL
        #         )
            
        return fig

    def as_html(self):
        
        return html.Div(
                [
                    html.H2("Marketplace Items"),
                    dcc.Graph(id=MARKETPLACE_GRAPH_ID)
                ],
            )

    def get_creators(self):
        return self.creators
