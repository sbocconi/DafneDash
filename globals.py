import pandas as pd
from datetime import datetime, timezone

REG_TL_ID = "registrations-tl"
SLD_ID = "date-slider"
TOOLS_GRAPH_ID = "tools-graph"
MARKETPLACE_GRAPH_ID = "marketplace-graph"
CREATORS_GRAPH_ID = "creators-graph"
WEEK_ACTIONS_GRAPH_ID = "week-actions-graph"
MONTH_ACTIONS_GRAPH_ID = "month-actions-graph"
COLLABORATIONS_GRAPH_ID = "collaboration-graph"

DATAEXP_DIR = "../DataExports"
EVENT_FLNM = "events"
CNTMGMT_KEY = "cntmgmt"
TOOLS_KEY = "tools"
MARKETPLACE_KEY = "marketplace"

def thumbs(condition):
    return '✅' if condition else '❌'

def get_mask(date_column, start, end, strict_left:bool=False, strict_right:bool=False):
    # breakpoint()
    # print(f"Masking between {datetime.fromtimestamp(start,timezone.utc)} and {datetime.fromtimestamp(end,timezone.utc)}")
    dt_idx = pd.DatetimeIndex(date_column).view('int64') // 10**9
    if strict_left and strict_right:
        mask = (dt_idx > start) & (dt_idx < end)
    elif strict_left and not strict_right:
        mask = (dt_idx > start) & (dt_idx <= end)
    elif not strict_left and strict_right:
        mask = (dt_idx >= start) & (dt_idx < end)
    elif not strict_left and not strict_right:
        mask = (dt_idx >= start) & (dt_idx <= end)
    return mask