from dash import Dash, html, dash_table, dependencies, dcc, callback, Output, Input # type: ignore
import plotly.graph_objects as go

from globals import EVENT_FLNM, CNTMGMT_KEY, USER_TOOLS_KEY, USAGE_TOOLS_KEY, MARKETPLACE_KEY, IRCAM
from filedumps import FileDumps
from apidumps import APIDumps
from metricsdata import MetricsData
from dash_slider import DashSlider
from dash_registrations import DashRegistrations
from dash_tools import DashTools
from dash_marketplace import DashMarketPlace
from dash_creators import DashCreators
from dash_actions import DashActions
from dash_collaborations import DashCollaborations

def main(refresh:bool):
    # Initialize the app
    
    metr_data = MetricsData.read_metrics(refresh=refresh)
    # breakpoint()
    if metr_data is None:
        metr_data = MetricsData()

        FileDumps.init(metr_data)
        APIDumps.init(metr_data)
        metr_data.save_metrics()
    
    # Fix random plotly errors
    # see this: https://github.com/plotly/plotly.py/issues/3441
    go.Figure(layout=dict(template='plotly'))

    app = Dash(__name__)
    # breakpoint()
    reg_graph = DashRegistrations(metr_data.get_data(CNTMGMT_KEY,'user-registrations'), metr_data.get_data(CNTMGMT_KEY, EVENT_FLNM), metr_data.min_ts(), metr_data.now(), app)
    marketplace_graph = DashMarketPlace(metr_data, metr_data.min_ts(), metr_data.now(), app)    
    creators_graph = DashCreators(metr_data.get_data(MARKETPLACE_KEY), metr_data.min_ts(), metr_data.now(), app)
    actions_graph = DashActions(metr_data, metr_data.min_ts(), metr_data.now(), app)
    sharing_graph = DashCollaborations(metr_data, metr_data.min_ts(), metr_data.now(), app)
    tools_graph = DashTools(metr_data.get_data(USER_TOOLS_KEY), metr_data.get_data(USAGE_TOOLS_KEY, IRCAM), metr_data.get_creators(), metr_data.min_ts(), metr_data.now(), app)
    
    # breakpoint()
    

    # App layout
    slider = DashSlider(metr_data.min_ts(), metr_data.now())
    app.layout = html.Div(
        [
            html.H1(
                "Dashboard",
            ),
            slider.as_html(),
            reg_graph.as_html(),
            marketplace_graph.as_html(),
            creators_graph.as_html(),
            actions_graph.as_html(),
            sharing_graph.as_html(),
            tools_graph.as_html(),
        ]
    )
    
    # breakpoint()
    app.run(debug=True)
    metr_data.all_used()

    

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '-r', '--refresh',
        dest='refresh',
        action='store_true',
        required=False,
        default=False,
        help='specifies whether to fetch new data from the API',
    )

    # parser.add_argument(
    #     '-e','--event',
    #     dest='event',
    #     action='store',
    #     default='events',
    #     required=False,
    #     help='specifies the filename with Use-case event dates',
    # )


    args, unknown = parser.parse_known_args()

    if len(unknown) > 0:
        print(f'Unknown options {unknown}')
        parser.print_help()
        exit(-1)


    main(refresh=args.refresh)

# TODO
# Save the graphs https://gist.github.com/exzhawk/33e5dcfc8859e3b6ff4e5269b1ba0ba4
# Other graphs https://dash-example-index.herokuapp.com/
