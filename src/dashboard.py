"""
Generates dashboards for all stations

1. Get all field names
2. Get all station names
3. For each station, generate a dashboard
4. Each dashboard will contain graph for all fields

"""

import json
import parse
import settings
import requests
from logger import logger

PANEL_H = 8
PANEL_W = 12


def generate_panel(sn, field):
    query = (
        f'from(bucket: "inverter_api_test")\r\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\r\n  |> filter(fn: (r) => r["_measurement"] == "solis")\r\n  |> filter(fn: (r) => r._field == "{field}")\r\n  |> filter(fn: (r) => r["sn"] == "{sn}")\r\n  |> yield(name: "mean")\r\n\r\n',
    )

    with open("panel_template.json", "r") as f:
        panel = json.load(f)
        panel["targets"][0]["query"] = query
        panel["title"] = field

        return panel


def generate_dashboard(sn, name):
    fields = parse.get_day_fields(sn)
    panels = []
    if fields:
        for field, i in enumerate(fields, start=1):
            panel = generate_panel(sn, field)
            x = 0 if i % 2 == 1 else PANEL_W
            y = (i // 2) * PANEL_H

            panel["gridPos"] = {"h": PANEL_H, "w": PANEL_W, "x": x, "y": y}

            panels.append(panel)

        with open("dashboard_template.json", "r") as f:
            dashboard = json.load(f)
            dashboard["panels"] = panels
            dashboard["title"] = name

            return dashboard

    return None


def write_dashboard(dashboard):
    url = f"{settings.GRAFANA_URL}/api/dashboards/db"
    headers = {
        "Authorization": f"Bearer {settings.GRAFANA_TOKEN}",
        "Content-Type": "application/json",
    }

    resp = requests.post(url, headers=headers, json=dashboard)

    if resp.status_code == 200:
        return None
    else:
        return (resp.status_code, resp.text)
