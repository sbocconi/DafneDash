from dash import Dash, html, dash_table, dependencies, dcc, callback, Output, Input # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore
import plotly.express as px # type: ignore
from datetime import datetime, timedelta
import glob
from pathlib import Path

from filedumps import FileDumps
from apidumps import APIDumps
from metricsdata import MetricsData

REG_TL_ID = "registrations_tl"
SLD_ID = "date-slider"

class Slider:

    def __init__(self):
        pass

    def as_html(self):
        return html.Div(
                [
                    html.H3("Time Range:"),
                    dcc.RangeSlider(
                        allowCross=False,
                        id=SLD_ID,
                        min=FileDumps.min_ts(),
                        max=FileDumps.max_ts(),
                        marks = self.get_marks(),
                        updatemode = 'drag',
                        step = None,
                        className = 'reg-slider'
                    )
                ],
            )

    def get_marks(self):
        """
        Returns:
            dict: format is {
                1270080000: '04-2010',
                1235865600: '03-2009',
                ...etc.
            }
        """
        # start_date = min_date()
        # end_date = max_date()
        # months = pd.date_range(start_date, end_date, freq='MS')
        months = pd.date_range(FileDumps.min_ts()*10**9, FileDumps.max_ts()*10**9, freq='MS')

        # breakpoint()
        timestamps = months.view('int64') // 10**9
        timestamps = [ int(timestamp) for timestamp in timestamps]
        months_str = months.strftime("%m-%Y")
        # {'label': '0°C', 'style': {'color': '#77b0b1'}},

        labels = [{'label': month_str} for month_str in months_str]
        # breakpoint()
        return dict(zip(timestamps, labels))
    

class RegistrationGraph:
    TOT_COL = 'black'
    UC1_COL = 'red'
    UC2_COL = 'green'
    UC3_COL = 'blue'

    def __init__(self, reg_data, evt_data, app):
        self.reg_data = reg_data
        self.evt_data = evt_data
        self.app = app
        self.app.callback(
            dependencies.Output(REG_TL_ID, "figure"),
            dependencies.Input(SLD_ID, "value")
            )(self.registrations_tl_updt)

    def registrations_tl_updt(self,tss):
        if tss == None:
            start = FileDumps.min_ts()
            end = FileDumps.max_ts()
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
        
        if start == FileDumps.min_ts() and end == FileDumps.max_ts():
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

def main(dir, event):
    # Initialize the app
    
    metr_data = MetricsData()

    FileDumps.init(dir, event, metr_data)
    APIDumps.init(metr_data)
    # breakpoint()

    app = Dash(__name__)
    reg_graph = RegistrationGraph(metr_data.get_data('user-registrations'), metr_data.get_data(event), app)
        
    # App layout
    slider = Slider()
    app.layout = html.Div(
        [
            html.H1(
                "Dashboard",
            ),
            slider.as_html(),
            reg_graph.as_html(),

        ]
    )
    
    metr_data.all_used()
    app.run(debug=True)

    

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '-d', '--dir',
        dest='dir',
        action='store',
        required=False,
        default='/Users/SB/Projects/Software/Dyne/Dafne/DataExports',
        help='specifies the directory where the db dumps are stored',
    )

    parser.add_argument(
        '-e','--event',
        dest='event',
        action='store',
        default='events',
        required=False,
        help='specifies the filename with Use-case event dates',
    )


    args, unknown = parser.parse_known_args()

    if len(unknown) > 0:
        print(f'Unknown options {unknown}')
        parser.print_help()
        exit(-1)


    main(dir=args.dir, event=args.event)

# TODO
# Save the graphs https://gist.github.com/exzhawk/33e5dcfc8859e3b6ff4e5269b1ba0ba4
# Other graphs https://dash-example-index.herokuapp.com/
