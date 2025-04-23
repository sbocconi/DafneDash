from dash import Dash, html, dash_table, dependencies, dcc, callback, Output, Input # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore
import plotly.graph_objects as go

from globals import SLD_ID, ACTIONS_GRAPH_ID, CNTMGMT_KEY, thumbs
from metricsdata import MetricsData


class DashActions:
    SCALING = 1

    TOT_COL = 'black'
    USR_COL = 'blue'
    

    def __init__(self, metr_data, min, max, app):
        self.metr_data = metr_data
        # breakpoint()
        self.weekly_active_users = self.period_active_users(min, max, period='week')
        self.monthly_active_users = self.period_active_users(min, max, period='month')
        # breakpoint()
        self.min = min
        self.max = max
        self.app = app
        self.app.callback(
            dependencies.Output(ACTIONS_GRAPH_ID, "figure"),
            dependencies.Input(SLD_ID, "value")
            )(self.actions_tl_updt)
    
   
    def period_active_users(self, start, end, period):
        """
            Look in the whole dataset for users that did any action in a week or month
            and produces a Dataframe (date - unique users id)
        """
        df = pd.DataFrame(columns=['date','active_users'])
        start_date = pd.to_datetime(start, unit='s', utc=True)
        end_date = pd.to_datetime(end, unit='s', utc=True)
        if period == 'week':
            offset = pd.Timedelta(days=7)
        elif period == 'month':
            offset = pd.DateOffset(months=1)
        else:
            raise Exception(f'Unkwnow period: {period}')

        for key1 in self.metr_data.data_container.keys():
            for key2 in self.metr_data.data_container[key1].keys():
                # print(f'{key1} - {key2}')
                # breakpoint()
                userid = MetricsData.get_user_field(key1, key2)
                dates, _ = MetricsData.get_dates_field(key1, key2)
                if userid is None or dates == []:
                    continue
                # breakpoint()
                users_slice = self.metr_data.get_data(key1, key2)[userid]
                for date in dates:
                    date_slice = self.metr_data.get_data(key1, key2)[date]
                    # breakpoint()
                    pivot = start_date
                    while pivot < end_date:
                        mask = (pivot <= date_slice) &  (date_slice < pivot + offset)
                        un_active_users = set(users_slice.loc[mask])
                        if len(un_active_users) > 0:
                            # breakpoint()
                            if not df['date'].eq(pivot).any():
                                df.loc[len(df)] = [pivot, un_active_users]
                            else:
                                # print(df.loc[df['date'] == pivot, 'active_users'])
                                # print(un_active_users)
                                # breakpoint()
                                row_index = df.index[df['date'] == pivot][0]
                                df.at[row_index, 'active_users'] = df.at[row_index, 'active_users'].union(un_active_users)
                                # df.loc[df['date'] == pivot, 'active_users'] = df.loc[df['date'] == pivot, 'active_users'].iloc[0].union(un_active_users)

                        pivot = pivot + offset

        
        df['nr_active_users'] = [len(item) for item in df['active_users']]
        # breakpoint()
        return df.sort_values(by=["date",],ascending = True).reset_index(drop=True, inplace=False)



    def actions_tl_updt(self,tss):
        if tss == None:
            start = self.min
            end = self.max
        else:
            start = tss[0]
            end = tss[1]
        # breakpoint()
        dt_idx = pd.DatetimeIndex(self.weekly_active_users['date']).view('int64') // 10**9
        mask_week = (dt_idx > start) & (dt_idx <= end)
        dt_idx = pd.DatetimeIndex(self.monthly_active_users['date']).view('int64') // 10**9
        mask_month = (dt_idx > start) & (dt_idx <= end)
        dt_idx = pd.DatetimeIndex(self.metr_data.get_data(CNTMGMT_KEY,'user-registrations')['registrationTime']).view('int64') // 10**9
        mask_reg = (dt_idx > start) & (dt_idx <= end)
        users_scaled = self.metr_data.get_cumul_scaled(CNTMGMT_KEY, 'user-registrations', .15)
        # breakpoint()
        
        aligned_weekly = self.weekly_active_users.loc[mask_week]
        week_bar = go.Bar(x=aligned_weekly['date'], y=aligned_weekly['nr_active_users'], name='Weekly', width=7*24*3600*1000)
        
        aligned_monthly = self.monthly_active_users.loc[mask_month]
        month_bar = go.Bar(x=aligned_monthly['date'], y=aligned_monthly['nr_active_users'], name='Monthly', width=28*24*3600*1000)
        fig = go.Figure(data=[month_bar,week_bar])
        
        # fig.update_traces(line_color=DashActions.USR_COL, line_width=2)
        reg_graph = px.line(users_scaled.loc[mask_reg], x='registrationTime', y='cumsum')
        reg_graph.update_traces(line_color=DashActions.TOT_COL, line_width=2)
        
        for trace in reg_graph.data:
            fig.add_trace(trace)

        fig.update_layout(
            # title='Combined Bar Charts',
            xaxis_title='Time',
            yaxis_title='Active Users',
            barmode='overlay'
        )

        # breakpoint()

        
        # if start == self.min and end == self.max:
        #     fig.add_hline(y=len(self.creators)/50*self.SCALING, line_dash="dashdot", line_width=0.5, line_color=self.TOT_COL,
        #         annotation_text="KPI_9 Creators generating tokens daily >2%", 
        #         annotation_position="top left",
        #         annotation_font_size=15,
        #         annotation_font_color=self.TOT_COL
        #         )
            
        return fig

    def as_html(self):
        
        return html.Div(
                [
                    html.H2("Active Users"),
                    html.H3(f"Some days {thumbs(True)}, most days {thumbs(False)} KPI_9 Creators generating tokens daily >2%"),
                    dcc.Graph(id=ACTIONS_GRAPH_ID)
                ],
            )

