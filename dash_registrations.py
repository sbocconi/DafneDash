from dash import Dash, html, dash_table, dependencies, dcc, callback, Output, Input # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore
import plotly.graph_objects as go

from globals import REG_TL_ID, SLD_ID, thumbs, get_mask
from metricsdata import MetricsData

class DashRegistrations:
    TOT_COL = 'black'
    UC1_COL = 'red'
    UC2_COL = 'green'
    UC3_COL = 'blue'

    def __init__(self, reg_data, evt_data, min, max, app):
        self.reg_data = reg_data
        self.evt_data = evt_data
        self.total_reg_nr = len(self.reg_data)
        self.uc1_reg_nr = len(self.reg_data.loc[self.reg_data['UC'] == 1]) + len(self.reg_data.loc[self.reg_data['UC'] == -1])/3
        self.uc2_reg_nr = len(self.reg_data.loc[self.reg_data['UC'] == 2]) + len(self.reg_data.loc[self.reg_data['UC'] == -1])/3
        self.uc3_reg_nr = len(self.reg_data.loc[self.reg_data['UC'] == 3]) + len(self.reg_data.loc[self.reg_data['UC'] == -1])/3
        self.min = min
        self.max = max
        self.app = app
        self.app.callback(
            dependencies.Output(REG_TL_ID, "figure"),
            dependencies.Input(SLD_ID, "value")
            )(self.registrations_tl_updt)

    def registrations_tl_updt(self,tss):
        if tss == None:
            start = self.min
            end = self.max
        else:
            start = tss[0]
            end = tss[1]
        
        mask = get_mask(self.reg_data.registrationTime, start, end)
        
        comm_wght_mask = {
                'mask' : (self.reg_data['UC'] == -1),
                'weight': 1/3
        }
        uc1_wght_mask = {
                'mask' : (self.reg_data['UC'] == 1),
                'weight': 1
        }
        uc2_wght_mask = {
                'mask' : (self.reg_data['UC'] == 2),
                'weight': 1
        }
        
        uc3_wght_mask = {
                'mask' : (self.reg_data['UC'] == 3),
                'weight': 1
        }
        
        all_data = MetricsData.get_cumul_scaled(self.reg_data).loc[mask]

        uc1_data = MetricsData.get_cumul_scaled(self.reg_data, weighted_masks=[uc1_wght_mask,comm_wght_mask]).loc[mask & ( uc1_wght_mask['mask']| comm_wght_mask['mask'])]
        uc2_data = MetricsData.get_cumul_scaled(self.reg_data, weighted_masks=[uc2_wght_mask,comm_wght_mask]).loc[mask & ( uc2_wght_mask['mask']| comm_wght_mask['mask'])]
        uc3_data = MetricsData.get_cumul_scaled(self.reg_data, weighted_masks=[uc3_wght_mask,comm_wght_mask]).loc[mask & ( uc3_wght_mask['mask']| comm_wght_mask['mask'])]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=all_data['registrationTime'],
            y=all_data['cumsum'],
            mode='lines+markers',
            line_shape='hv',  # step ECDF
            name='All Use Cases',
            marker=dict(color=self.TOT_COL)
        ))

        fig.add_trace(go.Scatter(
            x=uc1_data['registrationTime'],
            y=uc1_data['cumsum'],
            mode='lines+markers',
            line_shape='hv',  # step ECDF
            name='Use Case 1',
            marker=dict(color=self.UC1_COL)
        ))

        fig.add_trace(go.Scatter(
            x=uc2_data['registrationTime'],
            y=uc2_data['cumsum'],
            mode='lines+markers',
            line_shape='hv',  # step ECDF
            name='Use Case 2',
            marker=dict(color=self.UC2_COL)
        ))

        fig.add_trace(go.Scatter(
            x=uc3_data['registrationTime'],
            y=uc3_data['cumsum'],
            mode='lines+markers',
            line_shape='hv',  # step ECDF
            name='Use Case 3',
            marker=dict(color=self.UC3_COL)
        ))

        # uc1_data = self.reg_data.loc[mask_all & ((self.reg_data['UC'] == 1) | (self.reg_data['UC'] == -1))]
        # uc2_data = self.reg_data.loc[mask_all & ((self.reg_data['UC'] == 2) | (self.reg_data['UC'] == -1))]
        # uc3_data = self.reg_data.loc[mask_all & ((self.reg_data['UC'] == 3) | (self.reg_data['UC'] == -1))]
        # # breakpoint()
        # https://plotly.com/python/ecdf-plots/
        # fig = px.ecdf(self.reg_data.loc[mask_all], x='registrationTime', ecdfmode="standard", ecdfnorm=None, markers=True, color_discrete_sequence=[self.TOT_COL])
        # # breakpoint()
        # uc1 = px.ecdf(uc1_data, x='registrationTime', y='counts', ecdfmode="standard", ecdfnorm=None, markers=True, color_discrete_sequence=[self.UC1_COL])
        # uc2 = px.ecdf(uc2_data, x='registrationTime', y='counts', ecdfmode="standard", ecdfnorm=None, markers=True, color_discrete_sequence=[self.UC2_COL])
        # uc3 = px.ecdf(uc3_data, x='registrationTime', y='counts', ecdfmode="standard", ecdfnorm=None, markers=True, color_discrete_sequence=[self.UC3_COL])
        
        # for trace in uc1.data:
        #     fig.add_trace(trace)
        # for trace in uc2.data:
        #     fig.add_trace(trace)
        # for trace in uc3.data:
        #     fig.add_trace(trace)
        
        mask_event = get_mask(self.evt_data.end, start, end)
        
        # positions = ["bottom left","top left"]
        positions = range(20,220,20)
        cnt = 0
        for event in self.evt_data.loc[mask_event].itertuples():
            fig.add_vrect(x0=event.start, x1=event.end, 
            #   annotation_text=event.name, annotation_position=positions[cnt],
              fillcolor=self.UC1_COL if event.UC == 1 else self.UC2_COL if event.UC == 2 else self.UC3_COL, opacity=0.20, line_width=0)
            fig.add_annotation(
                x=event.start,
                y=positions[cnt],
                text=event.name,
                showarrow=True
            )
            cnt = (cnt+1)%len(positions)
        
        # if start == self.min and end == self.max:
        #     fig.add_hline(y=200, line_dash="dashdot", line_width=0.5, line_color=self.TOT_COL,
        #         annotation_text="KPI 12: Total Nr. Users", 
        #         annotation_position="bottom left",
        #         annotation_font_size=15,
        #         annotation_font_color=self.TOT_COL
        #         )
        #     fig.add_hline(y=100, line_dash="dashdot", line_width=0.5, line_color=self.TOT_COL,
        #         annotation_text="KPI 15: UC1 Nr. Users",
        #         annotation_position="bottom left",
        #         annotation_font_size=15,
        #         annotation_font_color=self.UC1_COL
        #         )
        #     fig.add_hline(y=50, line_dash="dashdot", line_width=0.5, line_color=self.TOT_COL,
        #         annotation_text="KPI 16: UC2 Nr. Users",
        #         annotation_position="bottom left",
        #         annotation_font_size=15,
        #         annotation_font_color=self.UC2_COL
        #         )
        #     fig.add_hline(y=50, line_dash="dashdot", line_width=0.5, line_color=self.TOT_COL,
        #         annotation_text="KPI 17: UC3 Nr. Users",
        #         annotation_position="bottom right",
        #         annotation_font_size=15,
        #         annotation_font_color=self.UC3_COL
        #         )

        fig.update_layout(
            xaxis_title='Registration Time',
            yaxis_title='Nr Users',
            legend_title_text=None
        )
            
        return fig

    def as_html(self):
        
        return html.Div(
                [
                    html.H2("User Registrations"),
                    html.H3(f"KPI_12 At least 200 participants in the pilots {thumbs(self.total_reg_nr>=200)}"),
                    html.H3(f"KPI_15 Use Case 1: At least 100 registered users {thumbs(self.uc1_reg_nr>=100)}"),
                    html.H3(f"KPI_16 Use Case 2: At least 50 registered users {thumbs(self.uc2_reg_nr>=50)}"),
                    html.H3(f"KPI_17 Use Case 3: At least 50 registered users {thumbs(self.uc3_reg_nr>=50)}"),
                    dcc.Graph(id=REG_TL_ID)
                ],
            )
