import pandas as pd
from datetime import datetime, timezone

REG_TL_ID = "registrations-tl"
SLD_ID = "date-slider"
USER_TOOLS_GRAPH_ID = "user_tools-graph"
USAGE_VIEWS_TOOLS_GRAPH_ID = "usage_views_tools-graph"
USAGE_DOWNLOADS_TOOLS_GRAPH_ID = "usage_downloads_tools-graph"
MARKETPLACE_GRAPH_ID = "marketplace-graph"
CREATORS_GRAPH_ID = "creators-graph"
WEEK_ACTIONS_GRAPH_ID = "week-actions-graph"
MONTH_ACTIONS_GRAPH_ID = "month-actions-graph"
COLLABORATIONS_GRAPH_ID = "collaboration-graph"

DATAEXP_DIR = "../DataExports"
EVENT_FLNM = "events"
CNTMGMT_KEY = "cntmgmt"
USER_TOOLS_KEY = "user-tools"
USAGE_TOOLS_KEY = "usage-tools"
MARKETPLACE_KEY = "marketplace"
IRCAM = 'ircam'
GITHUB = 'github'

def thumbs(condition):
    return '✅' if condition else '❌'

def get_mask(date_column, start, end, is_year:bool=False, strict_left:bool=False, strict_right:bool=False):
    # breakpoint()
    # print(f"Masking between {datetime.fromtimestamp(start,timezone.utc)} and {datetime.fromtimestamp(end,timezone.utc)}")
    dt_idx = pd.DatetimeIndex(date_column).view('int64') // 10**9
    if is_year:
        # breakpoint()
        start_ts = pd.to_datetime(start, unit='s')
        end_ts = pd.to_datetime(end, unit='s')
        start = int(pd.Timestamp(year=start_ts.year, month=1, day=1, tz=start_ts.tz).timestamp())
        end = int(pd.Timestamp(year=end_ts.year, month=12, day=31, hour=23, minute=59, second=59, microsecond=999999, tz=start_ts.tz).timestamp())
        strict_left = False
        strict_right = False
        
    if strict_left and strict_right:
        mask = (dt_idx > start) & (dt_idx < end)
    elif strict_left and not strict_right:
        mask = (dt_idx > start) & (dt_idx <= end)
    elif not strict_left and strict_right:
        mask = (dt_idx >= start) & (dt_idx < end)
    elif not strict_left and not strict_right:
        mask = (dt_idx >= start) & (dt_idx <= end)
    return mask