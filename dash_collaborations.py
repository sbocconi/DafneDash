from dash import Dash, html, dash_table, dependencies, dcc, callback, Output, Input # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore
import plotly.graph_objects as go

from globals import SLD_ID, CNTMGMT_KEY, MARKETPLACE_KEY, COLLABORATIONS_GRAPH_ID, thumbs, get_mask
from metricsdata import MetricsData

class DashCollaborations:
    SCALING = 10
    SHARING_THR = 2

    TOT_COL = 'black'
    COLLAB_COL = 'blue'
    VERSION_COL = 'red'
    FREE_COL = 'green'
    


    def __init__(self, metrics_data, min, max, app):
        self.added_contributors = metrics_data.get_data(CNTMGMT_KEY, 'contributors')
        versions = metrics_data.get_data(MARKETPLACE_KEY, 'marketplace_items')
        self.versions = versions.loc[versions['version'].notnull()]
    
        # breakpoint()
        self.nr_sharing = len(self.added_contributors) + len(self.versions)
        self.nr_creators = len(metrics_data.get_creators())
        # breakpoint()
        # breakpoint()
        self.min = min
        self.max = max
        self.app = app
        self.app.callback(
            dependencies.Output(COLLABORATIONS_GRAPH_ID, "figure"),
            dependencies.Input(SLD_ID, "value")
            )(self.collaborations_tl_updt)
    
    def collaborations_tl_updt(self,tss):
        if tss == None:
            start = self.min
            end = self.max
        else:
            start = tss[0]
            end = tss[1]
        # breakpoint()
        
        
        mask_contrib = get_mask(self.added_contributors.dateTime, start, end)
        mask_versions = get_mask(self.versions.created, start, end)
        # all_data = self.added_contributors[mask]
        # daily_token_creators = self.token_generating_creators(start, end)
        
        # breakpoint()
        collab_fig = px.ecdf(self.added_contributors[mask_contrib], x='dateTime', ecdfmode="standard", ecdfnorm=None, markers=True, color_discrete_sequence=[DashCollaborations.COLLAB_COL])
        
        version_fig = px.ecdf(self.versions[mask_versions], x='created', ecdfmode="standard", ecdfnorm=None, markers=True, color_discrete_sequence=[DashCollaborations.VERSION_COL])

        # Select and rename columns so they match
        collab_renamed = self.added_contributors[['dateTime']].rename(columns={'dateTime': 'time'})
        versions_renamed = self.versions[['created']].rename(columns={'created': 'time'})

        # Combine the data
        df_combined = pd.concat([collab_renamed, versions_renamed], ignore_index=True)

        # Sort by time
        df_combined = df_combined.sort_values('time').reset_index(drop=True)
        
        mask_all = get_mask(df_combined.time, start, end)
        # Generate ECDF
        tot_fig = px.ecdf(df_combined.loc[mask_all], x='time', ecdfmode="standard", ecdfnorm=None, markers=True, color_discrete_sequence=[DashCollaborations.TOT_COL])


        # breakpoint()
        fig = go.Figure()

        for trace in tot_fig.data:
            trace.name = 'Total'
            trace.line.color = DashCollaborations.TOT_COL
            trace.showlegend=True
            fig.add_trace(trace)

        for trace in collab_fig.data:
            trace.name = 'Collaborators'
            trace.line.color = DashCollaborations.COLLAB_COL
            trace.showlegend=True
            fig.add_trace(trace)
        for trace in version_fig.data:
            trace.name = 'Versions'
            trace.line.color = DashCollaborations.VERSION_COL
            trace.showlegend=True
            fig.add_trace(trace)
        
        # breakpoint()
        
        # if start == self.min and end == self.max:
        #     fig.add_hline(y=len(self.creators)/50*self.SCALING, line_dash="dashdot", line_width=0.5, line_color=self.TOT_COL,
        #         annotation_text="KPI_9 Creators generating tokens daily >2%", 
        #         annotation_position="top left",
        #         annotation_font_size=15,
        #         annotation_font_color=self.TOT_COL
        #         )
        fig.update_layout(
            # title='Multiple ECDFs with Custom Colors and Legend',
            xaxis_title='Time',
            yaxis_title='Nr Sharings',
            # legend_title='Group',
        )

        return fig


    def as_html(self):
        
        return html.Div(
                [
                    html.H2("Collaborations"),
                    html.H3(f"KPI_8 Number of re-use of community-shared items > {DashCollaborations.SHARING_THR} per creator {thumbs(self.nr_sharing/self.nr_creators>DashCollaborations.SHARING_THR)}"),
                    html.P(f"More info: Total creators: {self.nr_creators}, average sharing per creator: {self.nr_sharing/self.nr_creators}"),
                    dcc.Graph(id=COLLABORATIONS_GRAPH_ID)
                ],
            )

