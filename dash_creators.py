from dash import Dash, html, dash_table, dependencies, dcc, callback, Output, Input # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore
import plotly.graph_objects as go


from globals import SLD_ID, CREATORS_GRAPH_ID, thumbs, get_mask
from metricsdata import MetricsData

class DashCreators:
    SCALING = 1
    CREATOR_THR = 2

    TOT_COL = 'black'
    CRT_COL = 'blue'


    def __init__(self, marketplace_data, min, max, app):
        self.marketplace_data = marketplace_data
        # breakpoint()
        self.daily_creators = self.get_daily_creators(min, max)
        # breakpoint()
        self.min = min
        self.max = max
        self.app = app
        self.app.callback(
            dependencies.Output(CREATORS_GRAPH_ID, "figure"),
            dependencies.Input(SLD_ID, "value")
            )(self.creators_tl_updt)
    
   
    def get_daily_creators(self, start, end):
        df = pd.DataFrame(columns=['date','nr_daily_creators', 'nr_creators'])
        start_date = pd.to_datetime(start, unit='s', utc=True)
        end_date = pd.to_datetime(end, unit='s', utc=True)
        pivot = start_date
        slice = MetricsData.get_subdata(self.marketplace_data, 'marketplace_items')
        unique_creators = []
        while pivot < end_date:
            mask = (pivot <= slice['created']) &  (slice['created'] < pivot + pd.Timedelta(days=1))
            unique_daily_creators = set(slice['creator'].loc[mask])
            for creator in unique_daily_creators:
                if creator not in unique_creators:
                    unique_creators.append(creator)
            df.loc[len(df)] = [pivot, len(unique_daily_creators)*self.SCALING, len(unique_creators)*self.SCALING*DashCreators.CREATOR_THR/100]
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

        mask = get_mask(self.daily_creators['date'], start, end)
        
        sel_daily_creators = self.daily_creators.loc[mask]
        
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=sel_daily_creators['date'], y=sel_daily_creators['nr_daily_creators'], mode='lines', name='Unique creators per day'))
        fig.add_trace(go.Scatter(x=sel_daily_creators['date'], y=sel_daily_creators['nr_creators'], mode='lines', name=f"{DashCreators.CREATOR_THR}% total creators"))

        fig.update_layout(
            # title='Multiple ECDFs with Custom Colors and Legend',
            xaxis_title='Time',
            yaxis_title='Nr Creators',
            # legend_title='Group',
        )
        
        # breakpoint()
        
        return fig

    def as_html(self):
        
        return html.Div(
                [
                    html.H2("Daily Creators"),
                    html.H3(f"KPI_9 Creators generating tokens daily > {DashCreators.CREATOR_THR}% - Some days {thumbs(True)}, most days {thumbs(False)}"),
                    dcc.Graph(id=CREATORS_GRAPH_ID)
                ],
            )

