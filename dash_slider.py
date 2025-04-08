from dash import Dash, html, dash_table, dependencies, dcc, callback, Output, Input # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore


from globals import SLD_ID

class DashSlider:

    def __init__(self, min, max):
        self.min = min
        self.max = max

    def as_html(self):
        return html.Div(
                [
                    html.H3("Time Range:"),
                    dcc.RangeSlider(
                        allowCross=False,
                        id=SLD_ID,
                        min=self.min,
                        max=self.max,
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
        months = pd.date_range(self.min*10**9, self.max*10**9, freq='MS')

        # breakpoint()
        timestamps = months.view('int64') // 10**9
        timestamps = [ int(timestamp) for timestamp in timestamps]
        months_str = months.strftime("%m-%Y")
        # {'label': '0°C', 'style': {'color': '#77b0b1'}},

        labels = [{'label': month_str} for month_str in months_str]
        # breakpoint()
        return dict(zip(timestamps, labels))
    
