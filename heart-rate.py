# PATH = '/home/STUB/Downloads/apple_health_export/export.xml'
#
# import xml.etree.ElementTree as ET
#
# from itertools import islice
#
# with open(PATH, 'r') as f:
#    lines = list(islice(f, 1398848 - 1, None))
#
# data = '<FakeRoot>\n' + ''.join(lines[:-1]) + '</FakeRoot>'
#
# with open("./temp.txt", 'w') as f:
#    f.write(data)
#
# root = ET.fromstring(data)
# for elem in root:
#    assert elem.tag == "Record" and elem.attrib["type"] == "HKQuantityTypeIdentifierHeartRateVariabilitySDNN"
#    heart_rate_list = elem.findall("HeartRateVariabilityMetadataList")
#    assert len(heart_rate_list) == 1
#    for heart_rate in heart_rate_list[0]:
#        assert heart_rate.tag == "InstantaneousBeatsPerMinute"

PATH = "/home/sprite/Downloads/apple_health_export/export_cda.xml"

import xml.etree.ElementTree as ET
import matplotlib

from datetime import datetime, timedelta, timezone
from matplotlib import pyplot as plt, dates as mdates, ticker as mticker, font_manager

import shared

with open(PATH, "r") as f:
    data = f.read()

data = data.replace(
    'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:hl7-org:v3 ../../../CDA%20R2/'
    'cda-schemas-and-samples/infrastructure/cda/CDA.xsd" xmlns="urn:hl7-org:v3" xmlns:cda="urn:hl7-org:v3" '
    'xmlns:sdtc="urn:l7-org:sdtc" xmlns:fhir="http://hl7.org/fhir/v3"',
    "",
).replace("xsi:type", "xsi_type")

# with open('./temp.txt', 'w') as f:
#    f.write(data)

root = ET.fromstring(data)

types = {""}

i = 0
DT_FMT = "%Y%m%d%H%M%S%z"
begin_datetime = datetime(1145, 1, 4, 19, 19, tzinfo=shared.TZ)

heart_rate = []
respiratory_rate = []

for elem in root:
    if elem.tag != r"entry":
        continue
    for elem in elem:
        assert elem.tag == "organizer"
        for elem in elem:
            if elem.tag == "component":
                for elem in elem:
                    assert (
                        elem.tag == "observation"
                        and elem.attrib["classCode"] == "OBS"
                        and elem.attrib["moodCode"] == "EVN"
                    )
                    text = elem.find("text")
                    text_type = text.find("type")
                    types.add(text_type.text)
                    if (
                        text_type.text != "HKQuantityTypeIdentifierHeartRate"
                        and text_type.text != "HKQuantityTypeIdentifierRespiratoryRate"
                    ):
                        continue
                    time = elem.find("effectiveTime")
                    (time_low_str, time_high_str) = (
                        time.find("low").attrib["value"],
                        time.find("high").attrib["value"],
                    )
                    (time_low, time_high) = (
                        datetime.strptime(time_low_str, DT_FMT),
                        datetime.strptime(time_high_str, DT_FMT),
                    )
                    if time_low < begin_datetime:
                        continue
                    i += 1
                    value = text.find("value").text
                    assert elem.find("statusCode").attrib["code"] == "completed"

                    if text_type.text == "HKQuantityTypeIdentifierHeartRate":
                        print(time_low, time_high, float(value))
                        if time_low == time_high:
                            heart_rate.append((time_low, float(value)))
                        else:
                            heart_rate.append((time_low, float(value)))
                            heart_rate.append((time_high, float(value)))
                    elif text_type.text == "HKQuantityTypeIdentifierRespiratoryRate":
                        if time_low == time_high:
                            respiratory_rate.append((time_low, float(value)))
                        else:
                            respiratory_rate.append((time_low, float(value)))
                            respiratory_rate.append((time_high, float(value)))
                    else:
                        assert False

heart_rate = sorted(heart_rate, key=lambda x: x[0])
respiratory_rate = sorted(respiratory_rate, key=lambda x: x[0])

matplotlib.rcParams["timezone"] = "Asia/Shanghai"

# make data
hr_x = mdates.date2num([heart_rate[i][0] for i in range(len(heart_rate))])
hr_y = [heart_rate[i][1] for i in range(len(heart_rate))]
rr_x = mdates.date2num([respiratory_rate[i][0] for i in range(len(respiratory_rate))])
rr_y = [respiratory_rate[i][1] for i in range(len(respiratory_rate))]

# new_x = np.linspace(hr_x[0], hr_x[-1], int(len(hr_x) / 2))
# new_y = np.interp(new_x, hr_x, hr_y, period=len(hr_x))

# plot
fig, ax = plt.subplots(dpi=200)

fig.autofmt_xdate()

locator = mdates.HourLocator(interval=3)
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f BPM"))
ax.plot_date(hr_x, hr_y, label="Heart rate")
# ax.plot_date(rr_x, rr_y, label='Respiratory rate')
for drug in shared.DRUG:
    ax.axvline(drug, color="orange", linestyle="--", label="acetaminophen 500mg")

plt.grid(linestyle=":")
plt.title("Heart Rate Change")
plt.xlabel("Date Time")
plt.ylabel("Heart Rate")

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
