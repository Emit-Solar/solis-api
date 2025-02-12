"""
Functions for parsing data received from API calls
"""

import api_requests
import math
import pytz
from datetime import datetime


def get_installation_date(id):
    """
    Returns installation date for given station
    Date is returned as a timestamp
    """
    station = api_requests.get_station_details(id)
    if station:
        timestamp = station["data"]["createDate"]
        dt = datetime.fromtimestamp(
            timestamp / 1000
        )  # convert timestamp to datetime obj
        tz = pytz.timezone("Asia/Kuala_Lumpur")  # convert to KL time
        dt = dt.astimezone(tz)
        date_str = dt.date().isoformat()
        time_str = dt.time().isoformat()

        return date_str, time_str

    return None


def get_inverter_total():
    inverter_list = api_requests.get_inverter_list()
    if inverter_list:
        return inverter_list["data"]["inverterStatusVo"]["all"]

    return None


def get_all_sns():
    """Returns list of all SNs or empty list on failure"""
    total_num = get_inverter_total()
    if total_num is None:
        return []

    total_pages = math.ceil(total_num / 100)
    sns = []

    for i in range(total_pages):
        inv_list = api_requests.get_inverter_list(i + 1, 100)
        if not inv_list or "data" not in inv_list or "page" not in inv_list["data"]:
            print(f"Skipping page {i+1} due to API error")
            continue

        for entry in inv_list["data"]["page"].get("records", []):
            sns.append(entry.get("sn", "Unknown"))

    return sns


def get_station_id(sn):
    inverter = api_requests.get_inverter_details(sn)

    if inverter:
        return inverter["data"]["stationId"]

    return None


def get_station_name(sn):
    inverter = api_requests.get_inverter_details(sn)

    if inverter:
        return inverter["data"]["stationName"]

    return None
