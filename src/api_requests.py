import requests
import api_header
import settings
import math


def _call_api(endpoint, body):
    req_header = api_header.get_request_header(endpoint, body)

    url = f"{settings.HOST_URL}/v1/api/{endpoint}"

    r = requests.post(url, headers=req_header, json=body)

    return r.json()


def _get_inverters_list(pageNo=1, pageSize=20):
    """Returns details of all inverters"""
    body = {"pageNo": pageNo, "pageSize": pageSize}

    response = _call_api("inverterList", body)

    return response


def _get_inverter_num():
    """Returns the total number of inverters installed"""
    return _get_inverters_list()["data"]["inverterStatusVo"]["all"]


def _get_all_sns():
    """Returns list of all SNs"""
    total_num = _get_inverter_num()
    total_pages = math.ceil(total_num / 100)

    sns = []
    for i in range(total_pages):
        inv_list = _get_inverters_list(i + 1, 100)["data"]["page"]["records"]
        for entry in inv_list:
            sns.append(entry["sn"])

    return sns
