from dash import Dash, html, dash_table, dependencies, dcc, callback, Output, Input # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore

from globals import SLD_ID, CREATORS_GRAPH_ID, thumbs

class DashCreators:
    SCALING = 1

    TOT_COL = 'black'
    CRT_COL = 'blue'


    def __init__(self, marketplace_data, min, max, app):
        # self.marketplace_data = DashMarketPlace.to_pd(marketplace_data)
        self.marketplace_data = marketplace_data
        # breakpoint()
        self.creators = set(self.marketplace_data['marketplace_items']['data']['creator'])
        # breakpoint()
        self.min = min
        self.max = max
        self.app = app
        self.app.callback(
            dependencies.Output(CREATORS_GRAPH_ID, "figure"),
            dependencies.Input(SLD_ID, "value")
            )(self.creators_tl_updt)
    
   
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
    
    def creators_tl_updt(self,tss):
        if tss == None:
            start = self.min
            end = self.max
        else:
            start = tss[0]
            end = tss[1]
        # breakpoint()
        daily_token_creators = self.token_generating_creators(start, end)
        
        # breakpoint()
        fig = px.line(daily_token_creators, x='date', y="nr_creators")
        
        # for trace in nft_graph.data:
        #     fig.add_trace(trace)
        # for trace in free_graph.data:
        #     fig.add_trace(trace)
        # for trace in creator_graph.data:
        #     fig.add_trace(trace)
        
        # breakpoint()
        
        if start == self.min and end == self.max:
            fig.add_hline(y=len(self.creators)/50*self.SCALING, line_dash="dashdot", line_width=0.5, line_color=self.TOT_COL,
                annotation_text="KPI_9 Creators generating tokens daily >2%", 
                annotation_position="top left",
                annotation_font_size=15,
                annotation_font_color=self.TOT_COL
                )
            
        return fig

    def as_html(self):
        
        return html.Div(
                [
                    html.H2("Daily Creators"),
                    html.H3(f"Some days {thumbs(True)}, most days {thumbs(False)} KPI_9 Creators generating tokens daily >2%"),
                    dcc.Graph(id=CREATORS_GRAPH_ID)
                ],
            )

