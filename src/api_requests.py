import requests
import api_header
import settings
import math
import time


def _call_api(endpoint, body, max_retries=3):
    url = f"{settings.HOST_URL}/v1/api/{endpoint}"
    req_header = api_header.get_request_header(endpoint, body)

    retries = 0

    while retries < max_retries:
        resp = requests.post(url, headers=req_header, json=body)
        resp_json = resp.json()

        # Error handling
        if resp_json["code"] != "0":
            print(
                f"Error {resp_json['code']} on {endpoint}: {resp_json['msg']}, Retrying..."
            )
            retries += 1
        else:
            return resp_json

        time.sleep(2)

    return None


def _get_inverters_list(pageNo=1, pageSize=20):
    """Returns details of all inverters"""
    body = {"pageNo": pageNo, "pageSize": pageSize}

    return _call_api("inverterList", body)


def _get_inverter_num():
    """Returns the total number of inverters installed"""
    response = _get_inverters_list()
    if response:
        return response["data"]["inverterStatusVo"]["all"]

    return None


def get_all_sns():
    """Returns list of all SNs or empty list on failure"""
    total_num = _get_inverter_num()
    if total_num is None:
        return []

    total_pages = math.ceil(total_num / 100)
    sns = []

    for i in range(total_pages):
        inv_list = _get_inverters_list(i + 1, 100)
        if not inv_list or "data" not in inv_list or "page" not in inv_list["data"]:
            print(f"Skipping page {i+1} due to API error")
            continue

        for entry in inv_list["data"]["page"].get("records", []):
            sns.append(entry.get("sn", "Unknown"))

    return sns


def get_inverter_details(sn):
    """Returns details about single inverter"""
    body = {"sn": sn}

    return _call_api("inverterDetail", body)


def get_inverter_day(sn, date):
    """
    Returns daily data for given inverter

    Args:
        sn (str): Inverter SN
        date (str): Must be in YYYY-MM-DD

    """
    body = {"sn": sn, "time": date}

    return _call_api("inverterDay", body)


def get_station_details(id):
    body = {"id": id}

    return _call_api("stationDetail", body)
