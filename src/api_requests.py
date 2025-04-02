"""
Function for calling needed API endpoints
"""

import requests
import api_header
import settings
import time
from logger import logger
from requests.exceptions import ConnectTimeout


def _call_api(endpoint, body):
    url = f"{settings.HOST_URL}/v1/api/{endpoint}"
    req_header = api_header.get_request_header(endpoint, body)

    retries = 0

    while True:
        try:
            resp = requests.post(url, headers=req_header, json=body)
            resp_json = resp.json()

            # Error handling
            if resp_json["code"] != "0":
                logger.error(
                    f"Error {resp_json['code']} on {endpoint}: {resp_json['msg']}, Retrying..."
                )
                retries += 1
            else:
                return resp_json
        except ConnectTimeout:
            retries += 1
            delay = 2 ** (retries - 1)
            logger.error(
                f"Connection timeout on {endpoint}, Retrying in {delay} seconds..."
            )
            time.sleep(delay)


def get_inverter_detail_list(pageNo=1, pageSize=20):
    """Returns list of all inverter details"""
    body = {"pageNo": pageNo, "pageSize": pageSize}

    return _call_api("inverterDetailList", body)


def get_inverter_list(pageNo=1, pageSize=20):
    body = {"pageNo": pageNo, "pageSize": pageSize}

    return _call_api("inverterList", body)


def get_inverter_details(sn):
    """
    Returns details about single inverter
    """
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
