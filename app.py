from dash import Dash, html, dash_table, dependencies, dcc, callback, Output, Input # type: ignore

from globals import EVENT_FLNM, CNTMGMT_KEY, TOOLS_KEY, MARKETPLACE_KEY
from filedumps import FileDumps
from apidumps import APIDumps
from metricsdata import MetricsData
from dash_slider import DashSlider
from dash_registrations import DashRegistrations
from dash_tools import DashTools
from dash_marketplace import DashMarketPlace

def main():
    # Initialize the app
    
    metr_data = MetricsData()

    FileDumps.init(metr_data)
    APIDumps.init(metr_data)
    

    app = Dash(__name__)
    reg_graph = DashRegistrations(metr_data.get_data(CNTMGMT_KEY,'user-registrations'), metr_data.get_data(CNTMGMT_KEY, EVENT_FLNM), FileDumps.min_ts(), FileDumps.now(), app)
    marketplace_graph = DashMarketPlace(metr_data.get_data(MARKETPLACE_KEY), FileDumps.min_ts(), FileDumps.now(), app)
    tools_graph = DashTools(metr_data.get_data(TOOLS_KEY), marketplace_graph.get_creators(), FileDumps.min_ts(), FileDumps.now(), app)
    
    
    # breakpoint()

    # App layout
    slider = DashSlider(FileDumps.min_ts(), FileDumps.now())
    app.layout = html.Div(
        [
            html.H1(
                "Dashboard",
            ),
            slider.as_html(),
            reg_graph.as_html(),
            tools_graph.as_html(),
            marketplace_graph.as_html(),

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

    # parser.add_argument(
    #     '-d', '--dir',
    #     dest='dir',
    #     action='store',
    #     required=False,
    #     default='/Users/SB/Projects/Software/Dyne/Dafne/DataExports',
    #     help='specifies the directory where the db dumps are stored',
    # )

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


    # main(dir=args.dir, event=args.event)
    main()

# TODO
# Save the graphs https://gist.github.com/exzhawk/33e5dcfc8859e3b6ff4e5269b1ba0ba4
# Other graphs https://dash-example-index.herokuapp.com/
