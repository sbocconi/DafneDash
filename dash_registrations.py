from dash import Dash, html, dash_table, dependencies, dcc, callback, Output, Input # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore

from globals import REG_TL_ID, SLD_ID

class DashRegistrations:
    TOT_COL = 'black'
    UC1_COL = 'red'
    UC2_COL = 'green'
    UC3_COL = 'blue'

    def __init__(self, reg_data, evt_data, min, max, app):
        self.reg_data = reg_data
        self.evt_data = evt_data
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
        dt_idx = pd.DatetimeIndex(self.reg_data.registrationTime).view('int64') // 10**9
        mask = (dt_idx > start) & (dt_idx <= end)
        mask_uc1 = self.reg_data.loc[mask & (self.reg_data['UC'] == 1)]
        mask_uc2 = self.reg_data.loc[mask & (self.reg_data['UC'] == 2)]
        mask_uc3 = self.reg_data.loc[mask & (self.reg_data['UC'] == 3)]
        # breakpoint()
        # https://plotly.com/python/ecdf-plots/
        fig = px.ecdf(self.reg_data.loc[mask], x='registrationTime', ecdfmode="standard", ecdfnorm=None, markers=True, color_discrete_sequence=[self.TOT_COL])
        # breakpoint()
        uc1 = px.ecdf(mask_uc1, x='registrationTime', ecdfmode="standard", ecdfnorm=None, markers=True, color_discrete_sequence=[self.UC1_COL])
        uc2 = px.ecdf(mask_uc2, x='registrationTime', ecdfmode="standard", ecdfnorm=None, markers=True, color_discrete_sequence=[self.UC2_COL])
        uc3 = px.ecdf(mask_uc3, x='registrationTime', ecdfmode="standard", ecdfnorm=None, markers=True, color_discrete_sequence=[self.UC3_COL])
        
        for trace in uc1.data:
            fig.add_trace(trace)
        for trace in uc2.data:
            fig.add_trace(trace)
        for trace in uc3.data:
            fig.add_trace(trace)
        
        for event in self.evt_data.itertuples():
            fig.add_vrect(x0=event.start, x1=event.end, 
              annotation_text=event.name, annotation_position="top left",
              fillcolor=self.UC1_COL if event.UC == 1 else self.UC2_COL if event.UC == 2 else self.UC3_COL, opacity=0.20, line_width=0)
        
        if start == self.min and end == self.max:
            fig.add_hline(y=200, line_dash="dashdot", line_width=0.5, line_color=self.TOT_COL,
                annotation_text="KPI 12: Total Nr. Users", 
                annotation_position="bottom left",
                annotation_font_size=15,
                annotation_font_color=self.TOT_COL
                )
            fig.add_hline(y=100, line_dash="dashdot", line_width=0.5, line_color=self.TOT_COL,
                annotation_text="KPI 15: UC1 Nr. Users",
                annotation_position="bottom left",
                annotation_font_size=15,
                annotation_font_color=self.UC1_COL
                )
            fig.add_hline(y=50, line_dash="dashdot", line_width=0.5, line_color=self.TOT_COL,
                annotation_text="KPI 16: UC2 Nr. Users",
                annotation_position="bottom left",
                annotation_font_size=15,
                annotation_font_color=self.UC2_COL
                )
            fig.add_hline(y=50, line_dash="dashdot", line_width=0.5, line_color=self.TOT_COL,
                annotation_text="KPI 17: UC3 Nr. Users",
                annotation_position="bottom right",
                annotation_font_size=15,
                annotation_font_color=self.UC3_COL
                )
            
        return fig

    def as_html(self):
        
        return html.Div(
                [
                    html.H2("User Registrations"),
                    dcc.Graph(id=REG_TL_ID)
                ],
            )
