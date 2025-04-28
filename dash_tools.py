from dash import Dash, html, dash_table, dependencies, dcc, callback, Output, Input # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore

from globals import SLD_ID, TOOLS_GRAPH_ID, thumbs
from metricsdata import MetricsData

class DashTools:
    TOT_COL = 'black'

    def __init__(self, tools_data, creators, min, max, app):
        self.tools_data = DashTools.flatten_pd(tools_data)
        # breakpoint()
        self.creators = creators
        self.usage_tools_per_creator()
        # breakpoint()
        self.min = min
        self.max = max
        self.app = app
        self.app.callback(
            dependencies.Output(TOOLS_GRAPH_ID, "figure"),
            dependencies.Input(SLD_ID, "value")
            )(self.tools_tl_updt)
    
    @classmethod
    def flatten_pd(cls, data):
        df = pd.DataFrame(columns=["tool","user", "access_date"])
        for key in data.keys():
            for row in MetricsData.get_subdata(data, key).itertuples():
                # breakpoint()
                df.loc[len(df)] = [key,row.user,row.access_date]
        # breakpoint()
        return df
    
    
    def tools_tl_updt(self,tss):
        if tss == None:
            start = self.min
            end = self.max
        else:
            start = tss[0]
            end = tss[1]
        # breakpoint()
        dt_idx = pd.DatetimeIndex(self.tools_data.access_date).view('int64') // 10**9
        mask = (dt_idx > start) & (dt_idx <= end)
        
        tools = set(self.tools_data['tool'].loc[mask])
        self.tools_df = pd.DataFrame(columns=["tool","total_usage", "unique_users"])
        for tool in tools:
            unique_users = len(set(self.tools_data.loc[mask & (self.tools_data['tool'] == tool)]['user']))
            total_usage = len(self.tools_data.loc[mask & (self.tools_data['tool'] == tool)])
            self.tools_df.loc[len(self.tools_df)] = [tool, total_usage, unique_users]
        # breakpoint()
        # fig = px.histogram(self.tools_data[mask], x="tool")
        fig = px.bar(self.tools_df, x="tool", y=["total_usage","unique_users"], barmode="group")
        # breakpoint()
                    
        return fig

    def usage_tools_per_creator(self):
        tot = 0
        self.tot_users_zero = 0
        self.tot_users_one = 0
        self.tot_users_more = 0
        for creator in self.creators:
            tools_per_creator = self.tools_data.loc[self.tools_data['user'] == creator]
            if len(tools_per_creator) == 0:
                self.tot_users_zero = self.tot_users_zero + 1
            else:
                if len(tools_per_creator) == 1:
                    self.tot_users_one = self.tot_users_one + 1
                else:
                    self.tot_users_more = self.tot_users_more + 1
            tot = tot + len(tools_per_creator)
        self.avg_usage_per_creator = tot / len(self.creators)
        # breakpoint()



    def as_html(self):
        
        return html.Div(
                [
                    html.H2("Tools Usage"),
                    html.H3(f"KPI_6 Usage of provided production components/ workflows > 1 per creator {thumbs(self.tot_users_zero==0 and self.tot_users_one==0)}"),
                    html.P(f"More info: Total creators: {len(self.creators)}, average tool usage per creator: {self.avg_usage_per_creator}"),
                    html.P(f"Users with no tool usage: {self.tot_users_zero}, one usage: {self.tot_users_one}, more usages: {self.tot_users_more}"),
                    dcc.Graph(id=TOOLS_GRAPH_ID)
                ],
            )
