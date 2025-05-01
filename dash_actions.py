from dash import Dash, html, dash_table, dependencies, dcc, callback, Output, Input # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore
import plotly.graph_objects as go

from globals import SLD_ID, WEEK_ACTIONS_GRAPH_ID, MONTH_ACTIONS_GRAPH_ID, CNTMGMT_KEY, thumbs, get_mask
from metricsdata import MetricsData


class DashActions:
    SCALING = 1
    WEEKLY_PERC_THR = 15
    MONTHLY_PERC_THR = 25

    TOT_COL = 'black'
    WEEK_COL = 'red'
    MONTH_COL = 'blue'

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
            dependencies.Output(WEEK_ACTIONS_GRAPH_ID, "figure"),
            dependencies.Input(SLD_ID, "value")
            )(self.week_actions_tl_updt)
        self.app.callback(
            dependencies.Output(MONTH_ACTIONS_GRAPH_ID, "figure"),
            dependencies.Input(SLD_ID, "value")
            )(self.month_actions_tl_updt)
    
   
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



    def week_actions_tl_updt(self,tss):
        if tss == None:
            start = self.min
            end = self.max
        else:
            start = tss[0]
            end = tss[1]
        # breakpoint()
        mask_week = get_mask(self.weekly_active_users['date'], start, end)
        
        users_scaled = MetricsData.get_cumul_scaled(self.metr_data.get_data(CNTMGMT_KEY, 'user-registrations'), scaling=DashActions.WEEKLY_PERC_THR/100)
        mask_reg = get_mask(users_scaled['registrationTime'], start, end)
        # breakpoint()
        
        aligned_weekly = self.weekly_active_users.loc[mask_week]
        bar = go.Bar(x=aligned_weekly['date'], y=aligned_weekly['nr_active_users'], name='Weekly Active Users', marker_color=DashActions.WEEK_COL, width=7*24*3600*1000)
        
        fig = go.Figure()
        fig.add_scatter(x=users_scaled.loc[mask_reg]['registrationTime'], y=users_scaled.loc[mask_reg]['cumsum'], mode='lines', name='Registered Users', line_color=DashActions.TOT_COL, line_width=2)
        
        mid_point = int(len(users_scaled.loc[mask_reg])/2)
        fig.add_annotation(
                x=users_scaled.loc[mask_reg]['registrationTime'].iloc[mid_point],
                y=users_scaled.loc[mask_reg]['cumsum'].iloc[mid_point],
                text=f"{DashActions.WEEKLY_PERC_THR}% of users",
                showarrow=False,
                font_size=15,
                xanchor="left",
                yanchor="top"
            )
        
        fig.add_trace(bar)

        fig.update_layout(
            # title='Combined Bar Charts',
            xaxis_title='Time',
            yaxis_title='Nr. Users',
            showlegend=True,
        )

        return fig

    def month_actions_tl_updt(self,tss):
        if tss == None:
            start = self.min
            end = self.max
        else:
            start = tss[0]
            end = tss[1]
        # breakpoint()
        mask_month = get_mask(self.monthly_active_users['date'],start, end, strict_right=True)
        
        users_scaled = MetricsData.get_cumul_scaled(self.metr_data.get_data(CNTMGMT_KEY,'user-registrations'), scaling=DashActions.MONTHLY_PERC_THR/100)
        mask_reg = get_mask(users_scaled['registrationTime'],start, end)
        
        # print(mask_month[mask_month].size)
        # if mask_month[mask_month].size == 1:
        #     breakpoint()
        aligned_monthly = self.monthly_active_users.loc[mask_month]
        month_width = 28*24*3600*1000
        aligned_monthly_centered = aligned_monthly['date'] + pd.Timedelta(milliseconds=month_width / 2)

        bar = go.Bar(
            x=aligned_monthly_centered,
            y=aligned_monthly['nr_active_users'], 
            name='Monthly Active Users',
            marker_color=DashActions.MONTH_COL,
            width=month_width,
            hovertemplate=
                        'Start: %{customdata|%Y-%m-%d}<br>' +
                        'Value: %{y}<extra></extra>',  # removes trace name box
            customdata=aligned_monthly['date']
            )
        
        
        fig = go.Figure()
        fig.add_scatter(x=users_scaled.loc[mask_reg]['registrationTime'], y=users_scaled.loc[mask_reg]['cumsum'], mode='lines', name='Registered Users', line_color=DashActions.TOT_COL, line_width=2)
        
        mid_point = int(len(users_scaled.loc[mask_reg])/2)
        fig.add_annotation(
            x=users_scaled.loc[mask_reg]['registrationTime'].iloc[mid_point],
            y=users_scaled.loc[mask_reg]['cumsum'].iloc[mid_point],
            text=f"{DashActions.MONTHLY_PERC_THR}% of users",
            showarrow=False,
            font_size=15,
            xanchor="left",
            yanchor="top"
        )
        
        fig.add_trace(bar)

        fig.update_layout(
            # title='Combined Bar Charts',
            xaxis_title='Time',
            yaxis_title='Nr. Users',
            showlegend=True,
        )

        # breakpoint()
            
        return fig

    def as_html(self):
        
        return html.Div(
                [
                    html.H2("Weekly Active Users"),
                    html.H3(f"KPI_10 Users that perform any action on the platform weekly > {DashActions.WEEKLY_PERC_THR}% - Some weeks {thumbs(True)}, most weeks {thumbs(False)}"),
                    dcc.Graph(id=WEEK_ACTIONS_GRAPH_ID),
                    html.H2("Monthly Active Users"),
                    html.H3(f"KPI_11 Users that perform any action on the platform monthly > {DashActions.MONTHLY_PERC_THR}% - Some months {thumbs(True)}, most months {thumbs(False)}"),
                    dcc.Graph(id=MONTH_ACTIONS_GRAPH_ID)
                ],
            )

