from dash import Dash, html, dash_table, dependencies, dcc, callback, Output, Input # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore

from globals import SLD_ID, TOOLS_ID

class DashTools:
    TOT_COL = 'black'

    def __init__(self, tools_data, min, max, app):
        self.tools_data = DashTools.to_pd(tools_data)
        # breakpoint()
        self.min = min
        self.max = max
        self.app = app
        self.app.callback(
            dependencies.Output(TOOLS_ID, "figure"),
            dependencies.Input(SLD_ID, "value")
            )(self.tools_tl_updt)
    
    @classmethod
    def to_pd(cls, data):
        df = pd.DataFrame(columns=["tool","user", "access_date"])
        for key in data.keys():
            for arr in data[key]['data']:
                df.loc[len(df)] = [key, arr[0], arr[1]]
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
        
        # breakpoint()
        fig = px.histogram(self.tools_data[mask], x="tool")
        # breakpoint()
        
        if start == self.min and end == self.max:
            fig.add_hline(y=2, line_dash="dashdot", line_width=0.5, line_color=self.TOT_COL,
                annotation_text="KPI 12: Total Nr. Users", 
                annotation_position="bottom left",
                annotation_font_size=15,
                annotation_font_color=self.TOT_COL
                )
            
        return fig

    def as_html(self):
        
        return html.Div(
                [
                    html.H2("Tools Usage"),
                    dcc.Graph(id=TOOLS_ID)
                ],
            )
