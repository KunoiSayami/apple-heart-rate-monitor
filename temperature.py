import datetime
import numpy as np
import matplotlib

from datetime import datetime
from matplotlib import pyplot as plt, dates as mdates, ticker as mticker, font_manager

import shared

temperature = [
    (datetime(1145, 1, 4, 8, 10, tzinfo=shared.TZ), 1919.81),
    (datetime(1145, 1, 4, 19, 19, tzinfo=shared.TZ), 1145.14),
]

matplotlib.rcParams["timezone"] = "Asia/Shanghai"

# make data
x = mdates.date2num([temperature[i][0] for i in range(len(temperature))])
y = [temperature[i][1] for i in range(len(temperature))]

# plot
fig, ax = plt.subplots(dpi=200)

fig.autofmt_xdate()

locator = mdates.HourLocator(interval=3)
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f ℃"))
ax.axhline(37, color="red", linestyle="--", label="Normal body temperature")
ax.plot_date(x, y, linestyle="solid", label="Temperature")
for drug in shared.DRUG:
    ax.axvline(drug, color="orange", linestyle="--", label="acetaminophen 500mg")

plt.grid(linestyle=":")
plt.title("Temperature Change")
plt.xlabel("Date Time")
plt.ylabel("Temperature")

handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.legend(
    by_label.values(),
    by_label.keys(),
    prop=font_manager.FontProperties(
        fname="/usr/share/fonts/noto-cjk/NotoSerifCJK-Regular.ttc"
    ),
)

plt.show()
