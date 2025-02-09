# Generates request header required for all API calls

import settings
import hashlib
import hmac
import base64
import time
import json


def getGMTDate():
    return time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())


def getContentMD5(body):
    # Ensure body is properly converted to a JSON string if it's a dictionary
    body_str = json.dumps(body) if isinstance(body, dict) else str(body)
    md5_value = hashlib.md5(body_str.encode("utf-8"))

    return base64.b64encode(md5_value.digest()).decode("utf-8").strip("\n")


# Generates sign needed for authorization
def getSign(content_md5, gmt_date, canonicalized_resource):
    raw_str = f"{settings.VERB}\n{content_md5}\n{settings.CONTENT_TYPE}\n{gmt_date}\n{canonicalized_resource}"

    hashed = hmac.new(
        settings.API_KEYSECRET.encode("utf-8"),  # type: ignore
        raw_str.encode("utf-8"),
        hashlib.sha1,
    )

    return base64.b64encode(hashed.digest()).decode("utf-8").strip("\n")


def getAuth(sign):
    return f"API {settings.API_KEYID}:{sign}"


def getRequestHeader(endpoint, body):
    canonicalized_resource = f"/v1/api/{endpoint}"
    content_md5 = getContentMD5(body)
    gmt_date = getGMTDate()

    sign = getSign(content_md5, gmt_date, canonicalized_resource)
    auth = getAuth(sign)

    header = {
        "Content-MD5": content_md5,
        "Content-Type": settings.CONTENT_TYPE,
        "Date": gmt_date,
        "Authorization": auth,
    }

    return header
