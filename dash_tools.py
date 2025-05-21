from dash import Dash, html, dash_table, dependencies, dcc, callback, Output, Input # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore

from globals import SLD_ID, USER_TOOLS_GRAPH_ID, USAGE_VIEWS_TOOLS_GRAPH_ID, USAGE_DOWNLOADS_TOOLS_GRAPH_ID, thumbs, get_mask, IRCAM, GITHUB
from metricsdata import MetricsData

class DashTools:
    TOT_COL = 'black'

    def __init__(self, user_tools_data, usage_tools_data, creators, min, max, app):
        self.user_tools_data = DashTools.flatten_pd(user_tools_data)
        self.pv_usage_data = MetricsData.get_subdata(usage_tools_data, IRCAM)
        self.dl_usage_data = DashTools.get_downloads(usage_tools_data)
        self.creators = creators
        self.usage_tools_per_creator()
        # breakpoint()
        self.min = min
        self.max = max
        self.app = app
        self.app.callback(
            dependencies.Output(USER_TOOLS_GRAPH_ID, "figure"),
            dependencies.Input(SLD_ID, "value")
            )(self.user_tools_tl_updt)
        self.app.callback(
            dependencies.Output(USAGE_VIEWS_TOOLS_GRAPH_ID, "figure"),
            dependencies.Input(SLD_ID, "value")
            )(self.usage_views_tools_tl_updt)
        self.app.callback(
            dependencies.Output(USAGE_DOWNLOADS_TOOLS_GRAPH_ID, "figure"),
            dependencies.Input(SLD_ID, "value")
            )(self.usage_downloads_tools_tl_updt)
        
    @classmethod
    def get_downloads(cls, data):
        # Gets downloads per year from GitHub data structure and merges
        # with the Data provided by IRCAM
        github_data = MetricsData.get_subdata(data, GITHUB).copy()
        github_data['Year'] = pd.to_datetime(github_data['date'].dt.year, utc=True, format=MetricsData.YEAR_DT_FRMT)
        result = github_data.groupby(['name', 'Year'], as_index=False)['download_cnt'].sum()
        result = result.rename(columns={
            'name': 'Projects',
            'download_cnt': 'Downloads'
        })
        result['Page Views'] = 0
        usage_data = pd.concat([MetricsData.get_subdata(data, IRCAM), result], ignore_index=True)
        # breakpoint()
        usage_data = usage_data.groupby(['Projects', 'Year'], as_index=False).sum()
        return usage_data

    @classmethod
    def flatten_pd(cls, data):
        df = pd.DataFrame(columns=["tool","user", "access_date"])
        for key in data.keys():
            for row in MetricsData.get_subdata(data, key).itertuples():
                # breakpoint()
                df.loc[len(df)] = [key,row.user,row.access_date]
        # breakpoint()
        return df
    
    
    def user_tools_tl_updt(self,tss):
        if tss == None:
            start = self.min
            end = self.max
        else:
            start = tss[0]
            end = tss[1]
        # breakpoint()
        mask = get_mask(self.user_tools_data.access_date, start, end)
        
        tools = set(self.user_tools_data['tool'].loc[mask])
        self.tools_df = pd.DataFrame(columns=["tool","total_usage", "unique_users"])
        for tool in tools:
            unique_users = len(set(self.user_tools_data.loc[mask & (self.user_tools_data['tool'] == tool)]['user']))
            total_usage = len(self.user_tools_data.loc[mask & (self.user_tools_data['tool'] == tool)])
            self.tools_df.loc[len(self.tools_df)] = [tool, total_usage, unique_users]
        # breakpoint()
        # fig = px.histogram(self.tools_data[mask], x="tool")
        fig = None
        try:
            fig = px.bar(self.tools_df, x="tool", y=["total_usage","unique_users"], barmode="group")
        except ValueError as e:
            # breakpoint()
            print(f"Error {e}")
            
        else:
            fig.update_layout(
                xaxis_title='Tool Name',
                yaxis_title='Usage / Users',
                legend_title_text=None
            )

        return fig

    def usage_tools_tl_updt(self,tss, field):
        if tss == None:
            start = self.min
            end = self.max
        else:
            start = tss[0]
            end = tss[1]

        if field == 'Page Views':
            usage_data = self.pv_usage_data
        else:
            usage_data = self.dl_usage_data
            # breakpoint()

        mask = get_mask(usage_data.Year, start, end, is_year=True)
        
        # Use a copy of the data since we are changing type for 'Year'
        usage_dt = usage_data.copy().loc[mask]
        # Get just the year as string
        usage_dt['Year'] = usage_dt['Year'].dt.year.astype(str)

        df_totals = usage_dt.groupby('Projects', as_index=False).agg({field: 'sum'})
        df_totals['Year'] = 'Total'
        df_long = pd.concat([usage_dt, df_totals], ignore_index=True)

        # Force order of bars
        df_long['Year'] = pd.Categorical(df_long['Year'], categories=['2023', '2024', '2025', 'Total'], ordered=True)

        # Plot
        fig = None
        try:
            fig = px.bar(df_long, x='Year', y=field, color='Projects', barmode='group')
        except ValueError as e:
            # breakpoint()
            print(f"Error {e}")
        else:
            fig.update_yaxes(type='log')

            fig.update_layout(
                xaxis_title='Year',
                yaxis_title='Usage (Log base 10)',
                legend_title_text=None
            )

        return fig
    
    def usage_views_tools_tl_updt(self,tss):
        
        return self.usage_tools_tl_updt(tss,'Page Views')

    def usage_downloads_tools_tl_updt(self,tss):
        
        return self.usage_tools_tl_updt(tss,'Downloads')


    def usage_tools_per_creator(self):
        tot = 0
        self.tot_users_zero = 0
        self.tot_users_one = 0
        self.tot_users_more = 0
        for creator in self.creators:
            tools_per_creator = self.user_tools_data.loc[self.user_tools_data['user'] == creator]
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
                    html.H2("Platform Tools Usage"),
                    html.H3(f"KPI_6 Usage of provided production components/ workflows > 1 per creator {thumbs(self.tot_users_zero==0 and self.tot_users_one==0)}"),
                    html.P(f"More info: Total creators: {len(self.creators)}, average tool usage per creator: {self.avg_usage_per_creator}"),
                    html.P(f"Users with no tool usage: {self.tot_users_zero}, one usage: {self.tot_users_one}, more usages: {self.tot_users_more}"),
                    dcc.Graph(id=USER_TOOLS_GRAPH_ID),
                    html.H2("IRCAM Tools Usage"),
                    html.H3(f"Page Views"),
                    dcc.Graph(id=USAGE_VIEWS_TOOLS_GRAPH_ID),
                    html.H3(f"Downloads"),
                    dcc.Graph(id=USAGE_DOWNLOADS_TOOLS_GRAPH_ID)
                ],
            )
