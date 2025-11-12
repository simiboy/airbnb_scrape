import os
from datetime import datetime, timedelta

# Directories
projects = {
    "Booking.com": "booking.com/data",
    "Ingatlan.com": "ingatlan.com/data"
}

# Get all CSV files and map them by week (Monday as start of week)
def get_weekly_data(directory):
    weeks = {}
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            date_str = filename.replace(".csv", "")
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                continue
            # ISO week number
            year, week, _ = date.isocalendar()
            week_key = f"{year}-W{week:02d}"
            weeks[week_key] = True
    return weeks

# Collect all weeks across all projects
all_weeks = set()
project_weeks = {}

for project, path in projects.items():
    weeks = get_weekly_data(path)
    project_weeks[project] = weeks
    all_weeks.update(weeks.keys())

# Sort weeks newest first
all_weeks = sorted(all_weeks, reverse=True)

# Generate HTML
html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Scraping Tracker</title>
<style>
body { font-family: Arial, sans-serif; padding: 20px; }
table { border-collapse: collapse; width: 60%; margin: auto; }
th, td { border: 1px solid #aaa; padding: 8px 12px; text-align: center; }
th { background-color: #f4f4f4; }
.done { color: green; font-weight: bold; }
.not-done { color: red; font-weight: bold; }
</style>
</head>
<body>
<h1>Weekly Scraping Tracker</h1>
<table>
<thead>
<tr>
<th>Week</th>"""

for project in projects:
    html += f"<th>{project}</th>"
html += "</tr></thead>\n<tbody>\n"

for week in all_weeks:
    html += f"<tr><td>{week}</td>"
    for project in projects:
        done = "✓" if week in project_weeks[project] else "✗"
        cls = "done" if done == "✓" else "not-done"
        html += f"<td class='{cls}'>{done}</td>"
    html += "</tr>\n"

html += "</tbody>\n</table>\n</body>\n</html>"

# Save HTML file
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("index.html generated successfully.")
