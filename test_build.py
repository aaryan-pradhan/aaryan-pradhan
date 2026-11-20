import datetime
import xml.etree.ElementTree as ET

import build

counts = [0, 2, 3, 0, 1, 1, 1, 1, 0] + [0] * 362
weeks = [{"contributionDays": [
    {"contributionCount": c, "contributionLevel": "FIRST_QUARTILE" if c else "NONE", "weekday": i % 7}
    for i, c in list(enumerate(counts))[w * 7:w * 7 + 7]]} for w in range(53)]
days = [d for w in weeks for d in w["contributionDays"]]

assert build.longest_streak(days) == 4
svg = build.render({"totalContributions": sum(counts), "weeks": weeks}, datetime.date(2026, 11, 20))
ET.fromstring(svg)  # valid XML
assert "prefers-color-scheme:dark" in svg
print("ok")
