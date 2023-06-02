from datetime import datetime, timedelta, timezone
from matplotlib import dates as mdates

TZ = timezone(timedelta(hours=8))

DRUG = mdates.date2num(
    [
        datetime(1145, 1, 4, 19, 19, tzinfo=TZ),
        datetime(1145, 1, 4, 8, 10, tzinfo=TZ),
    ]
)
